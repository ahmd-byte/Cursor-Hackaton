import { motion } from 'motion/react';
import { ArrowRight, TrendingUp, Zap, Crown, Shield, Rocket, Send } from 'lucide-react';
import { useWallet } from '../../App';
import Slider from 'react-slick';
import { useState } from 'react';

interface HomePageProps {
  onNavigate: (page: 'transfer' | 'buckets' | 'ai') => void;
}

export function HomePage({ onNavigate }: HomePageProps) {
  const { user, wallet } = useWallet();

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 18) return 'Good Afternoon';
    return 'Good Evening';
  };

  const tierCards = [
    {
      id: 1,
      name: 'Buck Up, Power Save',
      tagline: 'Limit your spending to supercharge a 20% save.',
      savePercent: 20,
      color: 'bg-white',
      icon: Rocket,
      textColor: 'text-[#0F172A]',
    },
    {
      id: 2,
      name: 'Buck Up, Steady Flow',
      tagline: 'Secure your spending with a moderate 10% save.',
      savePercent: 10,
      color: 'bg-[#FF44EC]',
      icon: Shield,
      textColor: 'text-white',
    },
    {
      id: 3,
      name: 'Buck Up, Total Freedom',
      tagline: 'Enjoy your full spending power with a light 5% save.',
      savePercent: 5,
      color: 'bg-[#FEFF09]',
      icon: Crown,
      textColor: 'text-[#0F172A]',
    },
  ];

  const sliderSettings = {
    dots: true,
    infinite: true,
    speed: 500,
    slidesToShow: 1,
    slidesToScroll: 1,
    arrows: false,
    autoplay: false,
    centerMode: false,
    centerPadding: '0px',
  };

  const [aiMessage, setAiMessage] = useState('');

  return (
    <div className="min-h-screen p-6 text-white">
      {/* Header */}
      <motion.div
        className="mb-8"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="mb-1" style={{ fontFamily: '"Momo Trust Display", sans-serif', fontWeight: 800, fontSize: '48px', textTransform: 'uppercase', lineHeight: 1 }}>
              {getGreeting()}
            </h1>
            <p className="text-white/70" style={{ fontFamily: 'Inter, sans-serif' }}>
              {user.name}
            </p>
          </div>
        </div>
      </motion.div>

      {/* Ask Botl AI Chatbox */}
      <motion.div
        className="mb-6"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05 }}
      >
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-[2.5rem] p-4">
          <div className="flex items-center gap-3">
            <input
              type="text"
              value={aiMessage}
              onChange={(e) => setAiMessage(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && aiMessage.trim()) {
                  onNavigate('ai');
                }
              }}
              placeholder="Ask Botl AI anything..."
              className="flex-1 bg-transparent text-white placeholder-white/50 outline-none"
              style={{ fontFamily: 'Inter, sans-serif' }}
            />
            <motion.button
              onClick={() => {
                if (aiMessage.trim()) {
                  onNavigate('ai');
                }
              }}
              className="bg-[#FEFF09] text-[#0F172A] p-3 rounded-full"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
            >
              <Send className="w-5 h-5" />
            </motion.button>
          </div>
        </div>
      </motion.div>

      {/* Hero Card - Available Wages */}
      <motion.div
        className="bg-white rounded-[2.5rem] p-6 mb-6"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.1 }}
      >
        <div className="flex items-center gap-2 mb-2">
          <TrendingUp className="w-5 h-5 text-[#2820FF]" />
          <p className="text-[#0F172A]/70 text-sm" style={{ fontFamily: 'Inter, sans-serif' }}>
            Available Wages
          </p>
        </div>
        <p
          className="text-6xl mb-2 text-[#0F172A]"
          style={{ fontFamily: '"Momo Trust Display", sans-serif', fontWeight: 800 }}
        >
          ${wallet.currentAvailable.toFixed(2)}
        </p>
        <p className="text-[#0F172A]/50 text-sm" style={{ fontFamily: 'Inter, sans-serif' }}>
          Earned from {(wallet.currentAvailable / user.hourlyRate).toFixed(1)} hours @ ${user.hourlyRate}/hr
        </p>
      </motion.div>

      {/* The Golden Hour Card */}
      <motion.div
        className="bg-[#FEFF09] rounded-[2.5rem] p-8 mb-6 relative overflow-hidden"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        whileHover={{ scale: 1.02 }}
      >
        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-3">
            <Zap className="w-6 h-6 text-[#0F172A]" />
            <span className="text-[#0F172A]/70 text-sm" style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600 }}>
              INSTANT ACCESS
            </span>
          </div>
          <h2
            className="text-4xl text-[#0F172A] mb-4"
            style={{ fontFamily: '"Momo Trust Display", sans-serif', fontWeight: 800 }}
          >
            Unlock your wages
          </h2>
          <p className="text-[#0F172A]/70 mb-6" style={{ fontFamily: 'Inter, sans-serif' }}>
            Access your earned wages instantly. No waiting for payday.
          </p>
          <motion.button
            onClick={() => onNavigate('transfer')}
            className="bg-[#0F172A] text-[#FEFF09] px-8 py-4 rounded-full flex items-center gap-2"
            style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Unlock Now
            <ArrowRight className="w-5 h-5" />
          </motion.button>
        </div>

        {/* Background Pattern */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-[#0F172A]/5 rounded-full -translate-y-1/2 translate-x-1/2"></div>
      </motion.div>

      {/* Stats Grid */}
      <motion.div
        className="grid grid-cols-2 gap-4 mb-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        <div className="bg-white rounded-3xl p-5 break-words">
          <p className="text-[#0F172A]/70 text-sm mb-2 break-words" style={{ fontFamily: 'Inter, sans-serif' }}>
            Total Saved
          </p>
          <p
            className="text-3xl text-[#0F172A] break-words"
            style={{ fontFamily: 'JetBrains Mono, monospace', fontWeight: 700 }}
          >
            ${wallet.totalSaved.toFixed(2)}
          </p>
        </div>
        <div className="bg-white rounded-3xl p-5">
          <p className="text-[#0F172A]/70 text-sm mb-2" style={{ fontFamily: 'Inter, sans-serif' }}>
            Active Goals
          </p>
          <p
            className="text-3xl text-[#0F172A]"
            style={{ fontFamily: 'JetBrains Mono, monospace', fontWeight: 700 }}
          >
            6
          </p>
        </div>
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        className="space-y-3"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
      >
        <motion.button
          onClick={() => onNavigate('buckets')}
          className="w-full bg-white rounded-2xl p-4 text-left hover:bg-white/90 transition-colors"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="mb-1 text-[#0F172A]" style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600 }}>
                View Buckets
              </p>
              <p className="text-[#0F172A]/60 text-sm">Manage your savings goals</p>
            </div>
            <ArrowRight className="w-5 h-5 text-[#0F172A]" />
          </div>
        </motion.button>
      </motion.div>

      {/* Tier Cards Carousel */}
      <motion.div
        className="mt-8 mb-24"
      >
        <h3 className="text-sm text-white/70 mb-4 px-1" style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600 }}>
          CHOOSE YOUR TIER
        </h3>
        <Slider {...sliderSettings}>
          {tierCards.map((tier) => {
            const IconComponent = tier.icon;
            return (
              <div key={tier.id} className="px-4">
                <motion.div
                  className={`${tier.color} ${tier.textColor} rounded-[2.5rem] p-6`}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <IconComponent className={`w-8 h-8 ${tier.textColor}`} />
                      <span
                        className={`text-sm ${tier.textColor === 'text-white' ? 'text-white/80' : 'text-[#0F172A]/70'}`}
                        style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600 }}
                      >
                        TIER {tier.id}
                      </span>
                    </div>
                    <div
                      className={`px-4 py-2 rounded-full ${tier.textColor === 'text-white' ? 'bg-white/20' : 'bg-[#0F172A]/10'}`}
                    >
                      <span
                        className={`${tier.textColor}`}
                        style={{ fontFamily: 'JetBrains Mono, monospace', fontWeight: 700 }}
                      >
                        {tier.savePercent}% Save
                      </span>
                    </div>
                  </div>
                  <h3
                    className={`text-2xl mb-3 ${tier.textColor}`}
                    style={{ fontFamily: '"Momo Trust Display", sans-serif', fontWeight: 800 }}
                  >
                    {tier.name}
                  </h3>
                  <p
                    className={`${tier.textColor === 'text-white' ? 'text-white/80' : 'text-[#0F172A]/70'}`}
                    style={{ fontFamily: 'Inter, sans-serif' }}
                  >
                    {tier.tagline}
                  </p>
                </motion.div>
              </div>
            );
          })}
        </Slider>
      </motion.div>
    </div>
  );
}