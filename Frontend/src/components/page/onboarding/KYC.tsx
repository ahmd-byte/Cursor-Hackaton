import { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, ArrowRight, User, CreditCard, Phone, Mail } from 'lucide-react';

interface KYCProps {
  onNext: (data: { name: string; ic: string }) => void;
  onBack: () => void;
}

export function KYC({ onNext, onBack }: KYCProps) {
  const [formData, setFormData] = useState({
    fullName: '',
    ic: '',
    email: '',
    phone: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.fullName.trim()) {
      newErrors.fullName = 'Full name is required';
    }

    if (!formData.ic.trim()) {
      newErrors.ic = 'IC number is required';
    } else if (!/^\d{12}$/.test(formData.ic.replace(/-/g, ''))) {
      newErrors.ic = 'Invalid IC format';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }

    if (!formData.phone.trim()) {
      newErrors.phone = 'Phone number is required';
    } else if (!/^(\+?6?01)[0-9]{8,9}$/.test(formData.phone.replace(/[\s-]/g, ''))) {
      newErrors.phone = 'Invalid phone format';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      onNext({
        name: formData.fullName,
        ic: formData.ic,
      });
    }
  };

  return (
    <div className="min-h-screen bg-[#2820FF]">
      <div className="max-w-md mx-auto p-6">
        <motion.button
          onClick={onBack}
          className="flex items-center gap-2 text-white/70 hover:text-white mb-6"
          style={{ fontFamily: 'Inter, sans-serif' }}
          whileHover={{ x: -4 }}
          whileTap={{ scale: 0.95 }}
        >
          <ArrowLeft className="w-5 h-5" />
          Back
        </motion.button>

        <motion.div
          className="mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1
            className="text-5xl text-white mb-3"
            style={{ fontFamily: '"Momo Trust Display", sans-serif', fontWeight: 800 }}
          >
            VERIFY IDENTITY
          </h1>
          <p className="text-white/70" style={{ fontFamily: 'Inter, sans-serif' }}>
            We need to verify your identity to comply with regulations
          </p>
        </motion.div>

        {/* Progress Bar */}
        <div className="flex gap-2 mb-8">
          <div className="flex-1 h-1 bg-[#FEFF09] rounded-full"></div>
          <div className="flex-1 h-1 bg-white/20 rounded-full"></div>
        </div>

        <motion.form
          onSubmit={handleSubmit}
          className="space-y-5"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
        >
          <div>
            <label
              className="block text-sm text-white/70 mb-2"
              style={{ fontFamily: 'Inter, sans-serif' }}
            >
              Full Name (as per IC)
            </label>
            <div className="relative">
              <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#2820FF]/50" />
              <input
                type="text"
                value={formData.fullName}
                onChange={(e) =>
                  setFormData({ ...formData, fullName: e.target.value })
                }
                className="w-full pl-12 pr-4 py-4 bg-white border-2 border-transparent rounded-[2.5rem] focus:outline-none focus:border-[#FEFF09] text-[#0F172A]"
                style={{ fontFamily: 'Inter, sans-serif' }}
                placeholder="John Doe"
              />
            </div>
            {errors.fullName && (
              <p className="text-[#FF44EC] text-sm mt-1" style={{ fontFamily: 'Inter, sans-serif' }}>{errors.fullName}</p>
            )}
          </div>

          <div>
            <label
              className="block text-sm text-white/70 mb-2"
              style={{ fontFamily: 'Inter, sans-serif' }}
            >
              IC Number
            </label>
            <div className="relative">
              <CreditCard className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#2820FF]/50" />
              <input
                type="text"
                value={formData.ic}
                onChange={(e) =>
                  setFormData({ ...formData, ic: e.target.value })
                }
                className="w-full pl-12 pr-4 py-4 bg-white border-2 border-transparent rounded-[2.5rem] focus:outline-none focus:border-[#FEFF09] text-[#0F172A]"
                style={{ fontFamily: 'Inter, sans-serif' }}
                placeholder="990101-01-1234"
              />
            </div>
            {errors.ic && (
              <p className="text-[#FF44EC] text-sm mt-1" style={{ fontFamily: 'Inter, sans-serif' }}>{errors.ic}</p>
            )}
          </div>

          <div>
            <label
              className="block text-sm text-white/70 mb-2"
              style={{ fontFamily: 'Inter, sans-serif' }}
            >
              Email Address
            </label>
            <div className="relative">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#2820FF]/50" />
              <input
                type="email"
                value={formData.email}
                onChange={(e) =>
                  setFormData({ ...formData, email: e.target.value })
                }
                className="w-full pl-12 pr-4 py-4 bg-white border-2 border-transparent rounded-[2.5rem] focus:outline-none focus:border-[#FEFF09] text-[#0F172A]"
                style={{ fontFamily: 'Inter, sans-serif' }}
                placeholder="john@example.com"
              />
            </div>
            {errors.email && (
              <p className="text-[#FF44EC] text-sm mt-1" style={{ fontFamily: 'Inter, sans-serif' }}>{errors.email}</p>
            )}
          </div>

          <div>
            <label
              className="block text-sm text-white/70 mb-2"
              style={{ fontFamily: 'Inter, sans-serif' }}
            >
              Phone Number
            </label>
            <div className="relative">
              <Phone className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#2820FF]/50" />
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) =>
                  setFormData({ ...formData, phone: e.target.value })
                }
                className="w-full pl-12 pr-4 py-4 bg-white border-2 border-transparent rounded-[2.5rem] focus:outline-none focus:border-[#FEFF09] text-[#0F172A]"
                style={{ fontFamily: 'Inter, sans-serif' }}
                placeholder="+60123456789"
              />
            </div>
            {errors.phone && (
              <p className="text-[#FF44EC] text-sm mt-1" style={{ fontFamily: 'Inter, sans-serif' }}>{errors.phone}</p>
            )}
          </div>

          <motion.button
            type="submit"
            className="w-full bg-[#FEFF09] text-[#0F172A] py-5 rounded-full flex items-center justify-center gap-2 mt-8"
            style={{ fontFamily: '"Momo Trust Display", sans-serif', fontWeight: 800 }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            CONTINUE
            <ArrowRight className="w-5 h-5" />
          </motion.button>
        </motion.form>
      </div>
    </div>
  );
}