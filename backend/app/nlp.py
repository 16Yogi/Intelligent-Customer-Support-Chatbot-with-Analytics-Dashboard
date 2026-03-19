from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class NlpResult:
    intent: str
    entities: Dict[str, Any]
    confidence: float


FAQ_RESPONSES = {
    "greeting": "Hello! How can I help you today?",
    "order_status": "You can check your order status in the Orders section. If you share your order ID, I can help further.",
    "refund_policy": "Our refund policy allows returns within 30 days of purchase. Would you like more details?",
    "goodbye": "Thanks for chatting with us. Have a great day!",
    "fallback": "I'm not sure I understood that. Could you please rephrase your question?",
}


def simple_intent_classifier(text: str) -> NlpResult:
    lower = text.lower()

    if any(word in lower for word in ["hi", "hello", "hey"]):
        intent = "greeting"
    elif "order" in lower and any(w in lower for w in ["status", "track", "tracking"]):
        intent = "order_status"
    elif any(word in lower for word in ["refund", "return", "money back"]):
        intent = "refund_policy"
    elif any(word in lower for word in ["bye", "goodbye", "see you"]):
        intent = "goodbye"
    else:
        intent = "fallback"

    return NlpResult(intent=intent, entities={}, confidence=0.8)


def generate_response(nlp_result: NlpResult) -> str:
    return FAQ_RESPONSES.get(nlp_result.intent, FAQ_RESPONSES["fallback"])

