import { motion } from 'motion/react';
import { User, Mail, Phone, CreditCard, Bell, Lock, HelpCircle, LogOut, ChevronRight, Crown } from 'lucide-react';
import { useWallet } from '../../App';

export function ProfilePage() {
  const { user } = useWallet();

  const menuSections = [
    {
      title: 'ACCOUNT',
      items: [
        { icon: User, label: 'Personal Information', value: user.name },
        { icon: Mail, label: 'Email', value: 'tao@buckget.com' },
        { icon: Phone, label: 'Phone Number', value: '+60 12-345 6789' },
        { icon: CreditCard, label: 'Payment Methods', value: '2 cards' },
      ],
    },
    {
      title: 'APP',
      items: [
        { icon: Bell, label: 'Notifications', value: 'Enabled' },
        { icon: Lock, label: 'Security & Privacy', value: '' },
        { icon: Crown, label: 'Upgrade to Premium', value: '' },
      ],
    },
    {
      title: 'SUPPORT',
      items: [
        { icon: HelpCircle, label: 'Help Center', value: '' },
      ],
    },
  ];

  return (
    <div className="min-h-screen text-white">
      {/* Header Card */}
      <motion.div
        className="bg-[#FEFF09] rounded-b-[2.5rem] p-6 pb-12 mb-6"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1
          className="text-4xl text-[#0F172A] mb-6"
          style={{ fontFamily: '"Momo Trust Display", sans-serif', fontWeight: 800 }}
        >
          Profile
        </h1>
        
        <div className="flex items-center gap-4">
          <div className="w-20 h-20 bg-[#0F172A] rounded-full flex items-center justify-center text-3xl">
            👤
          </div>
          <div>
            <h2
              className="text-2xl text-[#0F172A] mb-1"
              style={{ fontFamily: '"Momo Trust Display", sans-serif', fontWeight: 800 }}
            >
              {user.name}
            </h2>
            <p className="text-[#0F172A]/70" style={{ fontFamily: 'Inter, sans-serif' }}>
              Basic Member
            </p>
          </div>
        </div>
      </motion.div>

      <div className="px-6">
        {/* Stats Card */}
        <motion.div
          className="bg-white rounded-3xl p-6 mb-6"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
        >
          <div className="grid grid-cols-2 gap-6">
            <div>
              <p className="text-[#0F172A]/70 text-sm mb-1" style={{ fontFamily: 'Inter, sans-serif' }}>
                Hourly Rate
              </p>
              <p
                className="text-3xl text-[#0F172A]"
                style={{ fontFamily: 'JetBrains Mono, monospace', fontWeight: 700 }}
              >
                ${user.hourlyRate}
              </p>
            </div>
            <div>
              <p className="text-[#0F172A]/70 text-sm mb-1" style={{ fontFamily: 'Inter, sans-serif' }}>
                Member Since
              </p>
              <p
                className="text-3xl text-[#0F172A]"
                style={{ fontFamily: 'JetBrains Mono, monospace', fontWeight: 700 }}
              >
                Dec 2024
              </p>
            </div>
          </div>
        </motion.div>

        {/* Menu Sections */}
        {menuSections.map((section, sectionIndex) => (
          <motion.div
            key={section.title}
            className="mb-6"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 + sectionIndex * 0.1 }}
          >
            <h3
              className="text-white/50 text-xs mb-3 px-2"
              style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600 }}
            >
              {section.title}
            </h3>
            <div className="bg-white rounded-3xl overflow-hidden">
              {section.items.map((item, itemIndex) => {
                const Icon = item.icon;
                const isUpgrade = item.label === 'Upgrade to Premium';
                
                return (
                  <motion.button
                    key={itemIndex}
                    className={`w-full flex items-center gap-4 p-4 hover:bg-[#0F172A]/5 transition-colors border-b border-[#0F172A]/10 last:border-b-0 ${
                      isUpgrade ? 'bg-[#FF44EC]/20' : ''
                    }`}
                    whileHover={{ scale: 1.01 }}
                    whileTap={{ scale: 0.99 }}
                  >
                    <Icon className={`w-5 h-5 ${isUpgrade ? 'text-[#FF44EC]' : 'text-[#0F172A]'}`} />
                    <div className="flex-1 text-left">
                      <p className="text-[#0F172A]" style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600 }}>
                        {item.label}
                      </p>
                      {item.value && (
                        <p className="text-sm text-[#0F172A]/60" style={{ fontFamily: 'Inter, sans-serif' }}>
                          {item.value}
                        </p>
                      )}
                    </div>
                    <ChevronRight className="w-5 h-5 text-[#0F172A]/50" />
                  </motion.button>
                );
              })}
            </div>
          </motion.div>
        ))}

        {/* Logout Button */}
        <motion.button
          className="w-full bg-white rounded-3xl p-4 flex items-center justify-center gap-2 text-red-500 hover:bg-red-50 transition-colors mb-20"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <LogOut className="w-5 h-5" />
          <span style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600 }}>
            Log Out
          </span>
        </motion.button>

        {/* Footer */}
        <div className="text-center text-white/50 text-sm mb-20" style={{ fontFamily: 'Inter, sans-serif' }}>
          <p>BuckGet v1.0.0</p>
          <p className="mt-1">© 2024 BuckGet. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
}