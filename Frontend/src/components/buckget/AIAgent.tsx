import { useState, useRef, useEffect } from 'react';
import { motion } from 'motion/react';
import { Send } from 'lucide-react';
import { useWallet } from '../../App';
import imgBotl from 'assets/chatbot ai.png';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  action?: {
    type: 'split';
    get: number;
    save: number;
  };
}

export function AIAgent() {
  const { wallet, buckets } = useWallet();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: `Hi! I'm Botl, your AI financial advisor 🤖 \n\nYou have $${wallet.currentAvailable.toFixed(2)} available. Would you like me to suggest an optimal split?`,
      sender: 'ai',
    },
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const didMountRef = useRef(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    // Skip initial render - only scroll on new messages
    if (!didMountRef.current) {
      didMountRef.current = true;
      return;
    }
    scrollToBottom();
  }, [messages]);

  const getAIResponse = (userMessage: string): Message => {
    const lowerMessage = userMessage.toLowerCase();

    if (lowerMessage.includes('split') || lowerMessage.includes('suggest')) {
      const emergencyBucket = buckets.find(b => b.name === 'Emergency Fund');
      const needAmount = emergencyBucket ? emergencyBucket.target - emergencyBucket.current : 0;
      const suggestedSave = Math.min(needAmount, wallet.currentAvailable * 0.3);
      const suggestedGet = wallet.currentAvailable - suggestedSave;

      return {
        id: Date.now().toString(),
        text: `Based on your goals, I recommend:\n\n💰 Get: $${suggestedGet.toFixed(2)}\n🐷 Save: $${suggestedSave.toFixed(2)}\n\nThis will help you reach your Emergency Fund goal faster!`,
        sender: 'ai',
        action: {
          type: 'split',
          get: suggestedGet,
          save: suggestedSave,
        },
      };
    }

    if (lowerMessage.includes('bucket') || lowerMessage.includes('goal')) {
      const topBucket = buckets[0];
      return {
        id: Date.now().toString(),
        text: `Your top priority is "${topBucket.name}" 🎯\n\nYou've saved $${topBucket.current} out of $${topBucket.target}. Keep it up!`,
        sender: 'ai',
      };
    }

    if (lowerMessage.includes('spend') || lowerMessage.includes('budget')) {
      return {
        id: Date.now().toString(),
        text: `Here's a smart budgeting tip: Follow the 50/30/20 rule!\n\n• 50% for needs\n• 30% for wants\n• 20% for savings\n\nYou're doing great! 🎯`,
        sender: 'ai',
      };
    }

    return {
      id: Date.now().toString(),
      text: `I can help you with:\n\n✨ Optimal wage splits\n💰 Savings strategies\n📊 Budget planning\n🎯 Goal tracking\n\nWhat would you like to know?`,
      sender: 'ai',
    };
  };

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: input,
      sender: 'user',
    };

    setMessages([...messages, userMessage]);
    setInput('');
    setIsTyping(true);

    setTimeout(() => {
      const aiResponse = getAIResponse(input);
      setMessages((prev) => [...prev, aiResponse]);
      setIsTyping(false);
    }, 1000);
  };

  const quickActions = ['Suggest a split', 'Show my goals', 'Budget tips'];

  return (
    <div className="absolute inset-0 flex flex-col text-white overflow-hidden">
      {/* Header - Fixed at top */}
      <div className="flex-shrink-0 px-6 py-4 pt-2">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full overflow-hidden bg-white flex items-center justify-center">
            <img src={imgBotl} alt="Botl" className="w-full h-full object-cover" />
          </div>
          <div>
            <h1 className="text-xl font-bold" style={{ fontFamily: '"Momo Trust Display", sans-serif' }}>
              Botl AI
            </h1>
            <p className="text-white/60 text-xs">Your financial copilot</p>
          </div>
        </div>
      </div>

      {/* Messages - Scrollable middle */}
      <div className="flex-1 overflow-y-auto px-6 min-h-0">
        <div className="space-y-3 pb-4">
          {messages.map((message) => (
            <motion.div
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div
                className={`max-w-[85%] p-3 ${message.sender === 'user'
                  ? 'bg-[#FEFF09] text-[#0F172A] rounded-2xl rounded-br-sm'
                  : 'bg-white/10 backdrop-blur border border-white/20 text-white rounded-2xl rounded-bl-sm'
                  }`}
              >
                <p className="whitespace-pre-line text-sm">{message.text}</p>
                {message.action && (
                  <motion.button
                    className="w-full bg-[#0F172A] text-[#FEFF09] mt-2 py-2 rounded-full text-xs font-semibold"
                    whileTap={{ scale: 0.98 }}
                  >
                    Apply This Split
                  </motion.button>
                )}
              </div>
            </motion.div>
          ))}

          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-white/10 border border-white/20 rounded-2xl rounded-bl-sm p-3">
                <div className="flex gap-1">
                  {[0, 1, 2].map((i) => (
                    <motion.div
                      key={i}
                      className="w-2 h-2 bg-white rounded-full"
                      animate={{ y: [0, -6, 0] }}
                      transition={{ duration: 0.5, repeat: Infinity, delay: i * 0.15 }}
                    />
                  ))}
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area - Fixed at bottom, above navigation */}
      <div className="flex-shrink-0 px-6 pb-32">
        {/* Quick Actions */}
        <div className="flex gap-3 justify-center pb-2 mb-4">
          {quickActions.map((action, i) => (
            <button
              key={i}
              onClick={() => setInput(action)}
              className="px-4 py-2.5 bg-white/20 backdrop-blur-md border border-white/30 text-white text-sm rounded-full shadow-lg hover:bg-white/30 transition-all active:scale-95"
              style={{ fontFamily: 'Inter, sans-serif', fontWeight: 500 }}
            >
              {action}
            </button>
          ))}
        </div>

        {/* Input */}
        <div className="bg-white/25 backdrop-blur-lg border border-white/40 rounded-full p-2 flex gap-2 shadow-xl">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask Botl anything..."
            className="flex-1 px-4 py-2 bg-transparent text-white placeholder-white/60 focus:outline-none text-sm"
            style={{ fontFamily: 'Inter, sans-serif' }}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim()}
            className="w-10 h-10 bg-[#FEFF09] text-[#0F172A] rounded-full flex items-center justify-center disabled:opacity-50 shadow-md hover:scale-105 transition-transform active:scale-95"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}