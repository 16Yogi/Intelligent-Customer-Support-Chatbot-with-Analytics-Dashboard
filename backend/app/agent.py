"""
Dataset-backed agent with multilingual (e.g. Hindi + English) understanding.
Uses keyword matching for intent so "question - what in hindi" or "क्या है" are understood.
Returns real responses per intent instead of the generic dataset placeholder.
"""
import csv
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DATASET_FILENAME = "Agentic_AI_Customer_Support_Dataset_v1.csv"

# Multilingual keywords: intent -> list of patterns (English + Hindi, etc.)
# User can ask "what is X", "क्या है", "question" etc. and get a proper answer.
INTENT_KEYWORDS = {
    "greeting": [
        "hi", "hello", "hey", "namaste", "namaskar", "good morning", "good evening",
        "नमस्ते", "हाय", "हेलो", "कैसे हो",
    ],
    "goodbye": [
        "bye", "goodbye", "thanks", "thank you", "धन्यवाद", "अलविदा", "ठीक है",
    ],
    "refund": [
        "refund", "return", "money back", "cancel order", "वापसी", "रिफंड", "पैसे वापस",
        "ऑर्डर कैंसिल", "रिटर्न",
    ],
    "order_status": [
        "order", "track", "tracking", "delivery", "status", "कहाँ है", "ऑर्डर", "डिलीवरी",
        "स्टेटस", "ट्रैक",
    ],
    "payment": [
        "payment", "pay", "failed", "deducted", "payment failure", "पेमेंट", "भुगतान",
        "फेल", "कट गया",
    ],
    "login": [
        "login", "password", "account", "access", "लॉगिन", "पासवर्ड", "अकाउंट",
        "एक्सेस", "खुल नहीं रहा",
    ],
    "complaint": [
        "complaint", "problem", "issue", "wrong", "complaint", "शिकायत", "समस्या",
        "प्रॉब्लम", "गलत",
    ],
    "general_inquiry": [
        "what", "how", "when", "where", "question", "tell me", "बताओ", "क्या", "कैसे",
        "कब", "कहाँ", "सवाल", "जानकारी", "in hindi", "hindi", "हिंदी",
    ],
    "get_help": [
        "help", "support", "need help", "मदद", "सहायता", "हेल्प",
    ],
    "cancel_service": [
        "cancel", "stop", "रद्द", "कैंसिल", "बंद",
    ],
    "request_info": [
        "info", "information", "details", "process", "जानकारी", "डिटेल्स", "प्रोसेस",
    ],
}

# Human-readable responses per intent (so we don't return "AI provided a helpful response.")
INTENT_RESPONSES = {
    "greeting": "Hello! How can I help you today? You can ask about orders, refunds, payments, login issues, or any question in English or Hindi.",
    "goodbye": "Thank you for contacting us. Have a great day!",
    "refund": "We process refunds within 5–7 business days. Refunds are allowed within 30 days of purchase. Please share your order ID if you need status on a specific refund.",
    "order_status": "You can check your order status in the Orders section or share your order ID and I can help you track it.",
    "payment": "If your payment failed but amount was deducted, it is usually reversed in 7–10 days. For immediate help, please share your transaction ID or contact our billing team.",
    "login": "For login or password issues: use 'Forgot password' on the login page, or clear cache and try again. If it still fails, we can escalate to the technical team.",
    "complaint": "We’re sorry for the trouble. Please describe the issue briefly and we’ll escalate it to the right team for a quick resolution.",
    "general_inquiry": "I’m here to help. You can ask me about: order status, refunds, payments, login issues, or any support question—in English or Hindi (e.g. क्या है, कैसे करें). What do you need?",
    "get_help": "I can help with orders, refunds, payments, account/login issues, and general questions. Tell me what you need in English or Hindi.",
    "cancel_service": "To cancel a service or order, please share your order/reference number. We’ll process the cancellation and confirm via email.",
    "request_info": "Sure. Please tell me what information you need—e.g. refund policy, delivery timeline, or account process—and I’ll share the details.",
}

FALLBACK_RESPONSE = (
    "I’m not sure I understood. You can ask in English or Hindi (e.g. क्या है, रिफंड कैसे मिलेगा). "
    "I can help with: order status, refunds, payments, login issues, and general questions."
)


def _normalize(text: str) -> str:
    """Lowercase and normalize spaces for matching."""
    if not text or not isinstance(text, str):
        return ""
    return " ".join(re.split(r"\s+", text.lower().strip()))


def _detect_intent_multilingual(user_text: str) -> Optional[str]:
    """Detect intent from user message using multilingual keywords. Returns intent key or None."""
    normalized = _normalize(user_text)
    if not normalized:
        return None
    # Check each intent's keywords (as whole words or substrings where appropriate)
    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw and kw in normalized:
                return intent
    return None


class DatasetAgent:
    def __init__(self, csv_path: Path) -> None:
        self.csv_path = csv_path
        self.queries: List[str] = []
        self.responses: List[str] = []
        self.intents: List[str] = []
        self.categories: List[str] = []
        self.subcategories: List[str] = []
        self.vectorizer = TfidfVectorizer(max_features=5000, analyzer="char_wb", ngram_range=(2, 5))
        self.matrix = None
        self._load_and_train()

    def _load_and_train(self) -> None:
        with self.csv_path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                query_text = row.get("Customer_Query_Text") or ""
                response_text = row.get("AI_Response_Text") or ""
                intent = row.get("Intent_Detected") or "unknown"
                category = row.get("Query_Category") or ""
                subcategory = row.get("Query_Subcategory") or ""

                if not query_text:
                    continue

                self.queries.append(query_text)
                self.responses.append(response_text)
                self.intents.append(intent)
                self.categories.append(category)
                self.subcategories.append(subcategory)

        if not self.queries:
            raise RuntimeError("No usable rows found in customer support dataset.")

        self.matrix = self.vectorizer.fit_transform(self.queries)

    def reply(self, user_text: str, top_k: int = 1) -> Tuple[str, str]:
        # 1) Prefer multilingual intent from keywords (works for "question - what in hindi", Hindi, etc.)
        detected = _detect_intent_multilingual(user_text)
        if detected and detected in INTENT_RESPONSES:
            return INTENT_RESPONSES[detected], detected

        # 2) Fallback: TF-IDF similarity (character n-grams work for any script)
        if self.matrix is not None and user_text.strip():
            try:
                query_vec = self.vectorizer.transform([user_text])
                sims = cosine_similarity(query_vec, self.matrix)[0]
                best_idx = int(sims.argmax())
                # If dataset has generic response, replace with intent-based response when possible
                response = self.responses[best_idx]
                intent = self.intents[best_idx] if best_idx < len(self.intents) else "unknown"
                # Map dataset intent to our response if it's the generic placeholder
                if "AI provided a helpful response" in (response or ""):
                    intent_lower = (intent or "").lower().replace(" ", "_")
                    for key, resp in INTENT_RESPONSES.items():
                        if key in intent_lower or intent_lower in key:
                            return resp, intent
                    return FALLBACK_RESPONSE, intent
                return response, intent
            except Exception:
                pass

        return FALLBACK_RESPONSE, "general_inquiry"


@lru_cache(maxsize=1)
def get_agent() -> DatasetAgent:
    base_dir = Path(os.path.dirname(__file__)).parent
    dataset_path = base_dir / "dataset" / DATASET_FILENAME
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset file not found at {dataset_path}")
    return DatasetAgent(dataset_path)
