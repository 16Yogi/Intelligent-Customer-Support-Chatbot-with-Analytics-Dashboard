import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Star } from 'lucide-react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { API_BASE } from '../config';

interface Message {
  role: 'user' | 'bot';
  content: string;
}

interface ChatResponse {
  conversation_id: number;
  reply: string;
  intent: string;
  created_at: string;
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showRating, setShowRating] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const text = input.trim();
    const userMessage: Message = { role: 'user', content: text };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const { data } = await axios.post<ChatResponse>(`${API_BASE}/api/chat`, {
        user_id: 1,
        text,
        conversation_id: conversationId,
      });

      setConversationId(data.conversation_id);

      const botMessage: Message = { role: 'bot', content: data.reply };
      setMessages(prev => [...prev, botMessage]);

      if (messages.length === 1) setShowRating(true);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, { role: 'bot', content: "Something went wrong talking to the server." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleRate = async (score: number) => {
    // Rating UI kept for now; you can wire this to a backend feedback endpoint if desired.
    console.log('User rating:', score);
    setShowRating(false);
  };

  return (
    <div className="flex flex-col h-full w-full bg-zinc-900 overflow-hidden transition-colors">
      {/* Messages */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-6 space-y-6 bg-zinc-950/50"
      >
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-zinc-500 space-y-4">
            <Bot className="w-12 h-12 opacity-20" />
            <p className="text-sm font-medium">Start a conversation with your AI assistant</p>
          </div>
        )}
        
        <AnimatePresence>
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`flex gap-3 max-w-[80%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                  msg.role === 'user' ? 'bg-zinc-800' : 'bg-emerald-900/30'
                }`}>
                  {msg.role === 'user' ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-emerald-400" />}
                </div>
                <div className={`p-4 rounded-2xl text-sm leading-relaxed shadow-sm ${
                  msg.role === 'user' 
                    ? 'bg-zinc-800 text-white rounded-tr-none' 
                    : 'bg-zinc-800 text-zinc-200 border border-zinc-700 rounded-tl-none'
                }`}>
                  {msg.content}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {loading && (
          <div className="flex justify-start">
            <div className="bg-zinc-800 border border-zinc-700 p-4 rounded-2xl rounded-tl-none shadow-sm flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-emerald-500" />
              <span className="text-xs text-zinc-400 font-medium">Thinking...</span>
            </div>
          </div>
        )}
      </div>

      {/* Rating Prompt */}
      <AnimatePresence>
        {showRating && (
          <motion.div 
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="bg-emerald-900/20 border-t border-emerald-900/30 p-3 flex items-center justify-between"
          >
            <span className="text-xs font-medium text-emerald-400">How's the response?</span>
            <div className="flex gap-1">
              {[1, 2, 3, 4, 5].map(star => (
                <button
                  key={star}
                  onClick={() => handleRate(star)}
                  className="p-1 hover:scale-110 transition-transform text-emerald-400"
                >
                  <Star className="w-4 h-4 fill-current" />
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Input */}
      <div className="p-4 bg-zinc-900 border-t border-zinc-800">
        <div className="relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type your message..."
            className="w-full bg-zinc-800 border-none rounded-xl py-3 pl-4 pr-12 text-sm text-white focus:ring-2 focus:ring-emerald-500 transition-all"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || loading}
            className="absolute right-2 p-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <p className="text-[10px] text-center text-zinc-500 mt-3">
          Real-time Analytics Enabled
        </p>
      </div>
    </div>
  );
}
