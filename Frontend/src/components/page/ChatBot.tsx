import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles } from 'lucide-react';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

export function ChatBot() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hi! I'm your AI financial advisor. I can help you with budgeting, savings goals, and financial literacy. How can I assist you today?",
      sender: 'bot',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const getBotResponse = (userMessage: string): string => {
    const lowerMessage = userMessage.toLowerCase();

    if (lowerMessage.includes('bucket') || lowerMessage.includes('save')) {
      return "I can help you create a savings bucket! What's your goal? For example, you could save for:\n• Emergency fund (3-6 months expenses)\n• Vacation\n• New gadget\n• Education\n\nTell me your goal and target amount, and I'll help you set it up!";
    }

    if (lowerMessage.includes('spending') || lowerMessage.includes('expense')) {
      return "Based on your recent activity, you've been doing great! Here are some insights:\n• Daily average: RM 35\n• Top category: Food & Dining (40%)\n• Suggested budget: RM 1,200/month\n\nWould you like me to create a detailed spending report?";
    }

    if (lowerMessage.includes('goal') || lowerMessage.includes('target')) {
      return "Let's set up a financial goal! Popular goals include:\n• Building emergency fund (RM 5,000)\n• Saving for vacation (RM 3,000)\n• New phone fund (RM 2,500)\n\nWhich goal interests you?";
    }

    if (lowerMessage.includes('tip') || lowerMessage.includes('advice')) {
      return "Here's a financial tip: Try the 50/30/20 rule!\n• 50% for needs (rent, food, bills)\n• 30% for wants (entertainment, hobbies)\n• 20% for savings and debt\n\nWith your RM 2,400 salary, that's RM 480 for savings each month!";
    }

    if (lowerMessage.includes('hello') || lowerMessage.includes('hi')) {
      return "Hello! How can I help you achieve your financial goals today?";
    }

    return "I understand you're asking about '" + userMessage + "'. I can help you with:\n• Creating savings buckets\n• Analyzing your spending\n• Setting financial goals\n• Providing budgeting tips\n\nWhat would you like to explore?";
  };

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: input,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages([...messages, userMessage]);
    setInput('');
    setIsTyping(true);

    setTimeout(() => {
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: getBotResponse(input),
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botMessage]);
      setIsTyping(false);
    }, 1000);
  };

  const quickActions = [
    'Create a savings bucket',
    'Show my spending',
    'Budget tips',
    'Set a financial goal',
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-indigo-600 to-indigo-800 flex flex-col">
      <div className="bg-white/10 backdrop-blur-sm border-b border-white/20 p-6 text-white">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
            <Sparkles className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl">AI Financial Advisor</h1>
            <p className="text-sm text-indigo-200">Always here to help</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6 pb-48 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${
              message.sender === 'user' ? 'flex-row-reverse' : 'flex-row'
            }`}
          >
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                message.sender === 'user'
                  ? 'bg-indigo-500'
                  : 'bg-white/20'
              }`}
            >
              {message.sender === 'user' ? (
                <User className="w-5 h-5 text-white" />
              ) : (
                <Bot className="w-5 h-5 text-white" />
              )}
            </div>
            <div
              className={`max-w-[75%] p-4 rounded-2xl ${
                message.sender === 'user'
                  ? 'bg-indigo-500 text-white'
                  : 'bg-white/20 text-white'
              }`}
            >
              <p className="whitespace-pre-line">{message.text}</p>
              <p className="text-xs opacity-70 mt-2">
                {message.timestamp.toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </p>
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex gap-3">
            <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div className="bg-white/20 text-white p-4 rounded-2xl">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-white rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="fixed bottom-20 left-0 right-0 max-w-md mx-auto px-6">
        <div className="flex gap-2 mb-3 overflow-x-auto pb-2 scrollbar-hide">
          {quickActions.map((action, index) => (
            <button
              key={index}
              onClick={() => {
                setInput(action);
                setTimeout(() => handleSend(), 100);
              }}
              className="flex-shrink-0 px-4 py-2 bg-white/20 backdrop-blur-sm text-white text-sm rounded-full border border-white/30 hover:bg-white/30 transition-colors"
            >
              {action}
            </button>
          ))}
        </div>

        <div className="bg-white rounded-full p-2 flex gap-2 shadow-lg">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask me anything..."
            className="flex-1 px-4 py-2 bg-transparent focus:outline-none"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim()}
            className="w-10 h-10 bg-indigo-600 text-white rounded-full flex items-center justify-center hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
