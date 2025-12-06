import { useState } from 'react';
import { motion } from 'motion/react';
import { ArrowLeft, Wallet, PiggyBank, Sparkles, Bot, Zap, Check } from 'lucide-react';
import { useWallet } from '../../App';
import { BotlTransition } from './BotlTransition';

interface TransferPageProps {
  onBack: () => void;
}

export function TransferPage({ onBack }: TransferPageProps) {
  const { wallet, updateWallet, addTransaction, buckets, updateBucket } = useWallet();
  const [splitPercentage, setSplitPercentage] = useState(70); // 70% Get, 30% Save
  const [showSuccess, setShowSuccess] = useState(false);
  const [showBotlTransition, setShowBotlTransition] = useState(false);

  const getAmount = Math.round((wallet.currentAvailable * splitPercentage) / 100);
  const saveAmount = wallet.currentAvailable - getAmount;

  const handleSecureFunds = () => {
    // Update wallet
    updateWallet(0, wallet.totalSaved + saveAmount);
    
    // Add to first bucket (Emergency Fund)
    if (buckets.length > 0) {
      updateBucket(buckets[0].id, saveAmount);
    }
    
    // Add transactions
    addTransaction({
      type: 'unlock',
      amount: getAmount,
      date: new Date(),
      description: 'Wage unlock',
    });
    
    if (saveAmount > 0) {
      addTransaction({
        type: 'stash',
        amount: saveAmount,
        date: new Date(),
        description: 'Auto save',
      });
    }

    // Show first success screen for 500ms
    setShowSuccess(true);
    setTimeout(() => {
      setShowSuccess(false);
      // Then show Botl transition for 2000ms
      setShowBotlTransition(true);
      setTimeout(() => {
        setShowBotlTransition(false);
        onBack();
      }, 2000);
    }, 500);
  };

  return (
    <div className="min-h-screen p-6 text-white relative">
      {/* Header */}
      <motion.div
        className="mb-8"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-white/70 hover:text-white mb-6"
          style={{ fontFamily: 'Inter, sans-serif' }}
        >
          <ArrowLeft className="w-5 h-5" />
          Back
        </button>
        <h1
          className="text-5xl"
          style={{ fontFamily: '"Momo Trust Display", sans-serif', fontWeight: 800 }}
        >
          BUCK & SAVE
        </h1>
        <p className="text-white/70 mt-2" style={{ fontFamily: 'Inter, sans-serif' }}>
          Split your ${wallet.currentAvailable.toFixed(2)} between cash and savings
        </p>
      </motion.div>

      {/* The Splitter UI */}
      <motion.div
        className="mb-8"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.1 }}
      >
        {/* Display Container */}
        <div className="bg-white rounded-[2.5rem] p-8 mb-6">
          <div className="grid grid-cols-2 gap-8 mb-8">
            {/* Get Side */}
            <div className="text-center">
              <div
                className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-3 transition-all ${
                  splitPercentage > 50
                    ? 'bg-[#FEFF09]'
                    : 'bg-[#0F172A]/10'
                }`}
              >
                <Wallet className={`w-8 h-8 ${splitPercentage > 50 ? 'text-[#0F172A]' : 'text-[#0F172A]/50'}`} />
              </div>
              <p className="text-[#0F172A]/70 text-sm mb-2" style={{ fontFamily: 'Inter, sans-serif' }}>
                GET
              </p>
              <p
                className="text-4xl text-[#0F172A]"
                style={{ fontFamily: 'JetBrains Mono, monospace', fontWeight: 700 }}
              >
                ${getAmount}
              </p>
            </div>

            {/* Save Side */}
            <div className="text-center">
              <div
                className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-3 transition-all ${
                  splitPercentage < 50
                    ? 'bg-[#FF44EC]'
                    : 'bg-[#0F172A]/10'
                }`}
              >
                <PiggyBank className={`w-8 h-8 ${splitPercentage < 50 ? 'text-white' : 'text-[#0F172A]/50'}`} />
              </div>
              <p className="text-[#0F172A]/70 text-sm mb-2" style={{ fontFamily: 'Inter, sans-serif' }}>
                SAVE
              </p>
              <p
                className="text-4xl text-[#0F172A]"
                style={{ fontFamily: 'JetBrains Mono, monospace', fontWeight: 700 }}
              >
                ${saveAmount}
              </p>
            </div>
          </div>

          {/* Custom Slider */}
          <div className="relative">
            <div className="h-16 bg-[#0F172A]/10 rounded-full relative overflow-hidden">
              {/* Glow Effect */}
              <motion.div
                className="absolute inset-0 rounded-full"
                style={{
                  background: splitPercentage > 50
                    ? `linear-gradient(to right, #FEFF09 0%, #FEFF09 ${splitPercentage}%, transparent ${splitPercentage}%)`
                    : `linear-gradient(to right, transparent 0%, transparent ${splitPercentage}%, #FF44EC ${splitPercentage}%, #FF44EC 100%)`,
                  opacity: 0.3,
                }}
                animate={{ opacity: [0.3, 0.5, 0.3] }}
                transition={{ duration: 2, repeat: Infinity }}
              />

              {/* Slider Track */}
              <input
                type="range"
                min="0"
                max="100"
                value={splitPercentage}
                onChange={(e) => setSplitPercentage(Number(e.target.value))}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
              />

              {/* Slider Thumb */}
              <motion.div
                className="absolute top-1/2 -translate-y-1/2 w-12 h-12 bg-[#0F172A] rounded-full shadow-lg flex items-center justify-center pointer-events-none"
                style={{ left: `calc(${splitPercentage}% - 24px)` }}
                whileHover={{ scale: 1.1 }}
              >
                <div className="w-6 h-6 bg-[#FEFF09] rounded-full"></div>
              </motion.div>
            </div>

            {/* Percentage Labels */}
            <div className="flex justify-between mt-3 text-sm text-[#0F172A]/50">
              <span style={{ fontFamily: 'JetBrains Mono, monospace' }}>$0</span>
              <span style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                ${splitPercentage > 50 ? getAmount.toFixed(2) : saveAmount.toFixed(2)}
              </span>
              <span style={{ fontFamily: 'JetBrains Mono, monospace' }}>${wallet.currentAvailable.toFixed(2)}</span>
            </div>
          </div>
        </div>

        {/* AI Suggestion Card */}
        <motion.div
          className="bg-[#FF44EC]/20 backdrop-blur-md border border-[#FF44EC]/30 rounded-3xl p-5 mb-6"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 bg-[#FF44EC] rounded-full flex items-center justify-center flex-shrink-0">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div className="flex-1">
              <p className="text-sm text-white/70 mb-1" style={{ fontFamily: 'Inter, sans-serif' }}>
                Axel suggests:
              </p>
              <p className="text-white" style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600 }}>
                Save {100 - splitPercentage}% for your Emergency Fund goal
              </p>
            </div>
            <Sparkles className="w-5 h-5 text-[#FF44EC]" />
          </div>
        </motion.div>

        {/* CTA Button */}
        <motion.button
          onClick={handleSecureFunds}
          className="w-full bg-[#FEFF09] text-[#0F172A] py-6 rounded-full text-xl flex items-center justify-center gap-2"
          style={{ fontFamily: '"Momo Trust Display", sans-serif', fontWeight: 800 }}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          {showSuccess ? (
            <>
              <Check className="w-6 h-6" />
              FUNDS SECURED!
            </>
          ) : (
            'BUCK UP'
          )}
        </motion.button>
      </motion.div>

      {/* Success Animation */}
      {showSuccess && (
        <motion.div
          className="fixed inset-0 bg-[#2820FF]/95 backdrop-blur-lg flex items-center justify-center z-50"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 200 }}
            className="text-center"
          >
            <motion.div
              className="mb-4 flex items-center justify-center"
              animate={{ rotate: [0, 10, -10, 0] }}
              transition={{ duration: 0.5, repeat: 3 }}
            >
              <Zap className="w-32 h-32 text-[#FEFF09]" />
            </motion.div>
            <h2
              className="text-4xl text-white"
              style={{ fontFamily: '"Momo Trust Display", sans-serif', fontWeight: 800 }}
            >
              Success!
            </h2>
          </motion.div>
        </motion.div>
      )}

      {/* Botl Transition Animation */}
      {showBotlTransition && <BotlTransition />}
    </div>
  );
}