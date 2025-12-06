import { useState } from 'react';
import { motion } from 'motion/react';
import { Plus, TrendingUp, Shield, Plane, Smartphone, Gamepad2, Home, BookOpen, X, DollarSign, Car, GraduationCap, ShoppingBag, Heart, Music, Dumbbell, Palmtree, Edit2, Trash2 } from 'lucide-react';
import { useWallet } from '../../App';

// Icon mapping
const iconMap: { [key: string]: any } = {
  Shield,
  Plane,
  Smartphone,
  Gamepad2,
  Home,
  BookOpen,
  DollarSign,
  Car,
  GraduationCap,
  ShoppingBag,
  Heart,
  Music,
  Dumbbell,
  Palmtree,
};

// Available icons for new goals
const availableIcons = ['DollarSign', 'Car', 'Home', 'Plane', 'GraduationCap', 'Smartphone', 'Gamepad2', 'ShoppingBag', 'Heart', 'Music', 'Dumbbell', 'Palmtree'];

// Available colors for new goals
const availableColors = [
  { name: 'Pink', value: 'bg-[#FF44EC]' },
  { name: 'Blue', value: 'bg-[#2820FF]' },
  { name: 'Green', value: 'bg-[#10B981]' },
  { name: 'Orange', value: 'bg-[#F97316]' },
  { name: 'Purple', value: 'bg-[#A855F7]' },
  { name: 'Yellow', value: 'bg-[#FEFF09]' },
];

export function BucketsPage() {
  const { buckets, wallet, addBucket, deleteBucket, updateBucketDetails } = useWallet();
  const [selectedBucket, setSelectedBucket] = useState<string | null>(null);
  const [showNewGoalModal, setShowNewGoalModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [newGoalName, setNewGoalName] = useState('');
  const [newGoalTarget, setNewGoalTarget] = useState('');
  const [selectedIcon, setSelectedIcon] = useState('DollarSign');
  const [selectedColor, setSelectedColor] = useState('bg-[#FF44EC]');
  
  // Edit states
  const [editName, setEditName] = useState('');
  const [editCurrent, setEditCurrent] = useState('');
  const [editTarget, setEditTarget] = useState('');
  const [editIcon, setEditIcon] = useState('DollarSign');
  const [editColor, setEditColor] = useState('bg-[#FF44EC]');

  const selectedBucketData = buckets.find(b => b.id === selectedBucket);

  const handleCreateGoal = () => {
    if (!newGoalName || !newGoalTarget) return;
    
    addBucket({
      name: newGoalName,
      target: parseFloat(newGoalTarget),
      current: 0,
      icon: selectedIcon,
      color: selectedColor,
    });
    
    // Reset form and close modal
    setNewGoalName('');
    setNewGoalTarget('');
    setSelectedIcon('DollarSign');
    setSelectedColor('bg-[#FF44EC]');
    setShowNewGoalModal(false);
  };

  const handleEditGoal = () => {
    if (!editName || !editTarget) return;
    
    updateBucketDetails(selectedBucket as string, {
      name: editName,
      target: parseFloat(editTarget),
      current: parseFloat(editCurrent),
      icon: editIcon,
      color: editColor,
    });
    
    // Reset form and close modal
    setEditName('');
    setEditCurrent('');
    setEditTarget('');
    setEditIcon('DollarSign');
    setEditColor('bg-[#FF44EC]');
    setShowEditModal(false);
  };

  return (
    <div className="min-h-screen p-6 text-white">
      {/* Header */}
      <motion.div
        className="mb-8"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1
          className="text-5xl mb-2"
          style={{ fontFamily: '"Momo Trust Display", sans-serif', fontWeight: 800 }}
        >
          Buckets
        </h1>
        <p className="text-white/70" style={{ fontFamily: 'Inter, sans-serif' }}>
          Your savings goals in one place
        </p>
      </motion.div>

      {/* Total Saved Card */}
      <motion.div
        className="bg-[#FEFF09] rounded-[2.5rem] p-6 mb-6"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.1 }}
      >
        <div className="flex items-center gap-2 mb-2">
          <TrendingUp className="w-5 h-5 text-[#0F172A]" />
          <p className="text-[#0F172A]/70 text-sm" style={{ fontFamily: 'Inter, sans-serif' }}>
            TOTAL SAVED
          </p>
        </div>
        <p
          className="text-5xl text-[#0F172A]"
          style={{ fontFamily: 'JetBrains Mono, monospace', fontWeight: 700 }}
        >
          ${wallet.totalSaved.toFixed(2)}
        </p>
        <p className="text-[#0F172A]/60 text-sm mt-1" style={{ fontFamily: 'Inter, sans-serif' }}>
          Across {buckets.length} active goals
        </p>
      </motion.div>

      {/* Bento Grid */}
      <motion.div
        className="grid grid-cols-2 gap-4 mb-20"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        {buckets.map((bucket, index) => {
          const progress = (bucket.current / bucket.target) * 100;
          const isHighPriority = bucket.color === 'bg-[#FF44EC]';
          const IconComponent = iconMap[bucket.icon];
          
          // Determine background color
          let bgColorClass = 'bg-white';
          let textColorClass = 'text-[#0F172A]';
          let iconColorClass = 'text-[#2820FF]';
          
          if (isHighPriority) {
            bgColorClass = 'bg-[#FF44EC]';
            textColorClass = 'text-white';
            iconColorClass = 'text-white';
          } else if (bucket.color !== 'bg-white/10') {
            // Use the selected color from the new goal modal
            bgColorClass = bucket.color;
            textColorClass = 'text-white';
            iconColorClass = 'text-white';
          }

          return (
            <motion.button
              key={bucket.id}
              onClick={() => setSelectedBucket(bucket.id)}
              className={`${bgColorClass} ${textColorClass} rounded-3xl p-5 text-left hover:scale-105 transition-all ${
                index === 0 ? 'col-span-2' : ''
              }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <div className="mb-3">
                {IconComponent && <IconComponent className={`w-10 h-10 ${iconColorClass}`} />}
              </div>
              <h3 className="mb-2" style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600 }}>
                {bucket.name}
              </h3>
              <p
                className="text-2xl mb-3"
                style={{ fontFamily: 'JetBrains Mono, monospace', fontWeight: 700 }}
              >
                ${bucket.current}
              </p>
              <div className="mb-2">
                <div className={`h-2 ${isHighPriority || bucket.color !== 'bg-white/10' ? 'bg-white/30' : 'bg-[#0F172A]/20'} rounded-full overflow-hidden`}>
                  <motion.div
                    className={isHighPriority || bucket.color !== 'bg-white/10' ? 'bg-white h-full' : 'bg-[#FEFF09] h-full'}
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.min(progress, 100)}%` }}
                    transition={{ duration: 0.8, delay: 0.3 + index * 0.1 }}
                  />
                </div>
              </div>
              <p className={`${isHighPriority || bucket.color !== 'bg-white/10' ? 'text-white/80' : 'text-[#0F172A]/60'} text-sm`} style={{ fontFamily: 'Inter, sans-serif' }}>
                {Math.round(progress)}% of ${bucket.target}
              </p>
            </motion.button>
          );
        })}

        {/* Add New Bucket */}
        <motion.button
          className="bg-white text-[#0F172A] rounded-3xl p-5 flex flex-col items-center justify-center hover:bg-white/90 transition-all"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setShowNewGoalModal(true)}
        >
          <Plus className="w-10 h-10 mb-2" />
          <p style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600 }}>
            New Goal
          </p>
        </motion.button>
      </motion.div>

      {/* Bucket Detail Modal */}
      {selectedBucket && selectedBucketData && (() => {
        const ModalIcon = iconMap[selectedBucketData.icon];
        return (
        <motion.div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-end justify-center z-[60]"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          onClick={() => setSelectedBucket(null)}
        >
          <motion.div
            className="bg-[#2820FF] border-t-4 border-[#FEFF09] rounded-t-[2.5rem] w-full max-w-md p-6"
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 30 }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="w-12 h-1 bg-white/30 rounded-full mx-auto mb-6"></div>
            
            <div className="text-center mb-6">
              <div className="flex items-center justify-center mb-4">
                {ModalIcon && <ModalIcon className="w-20 h-20 text-[#FEFF09]" />}
              </div>
              <h2
                className="text-3xl mb-2"
                style={{ fontFamily: '"Momo Trust Display", sans-serif', fontWeight: 800 }}
              >
                {selectedBucketData.name}
              </h2>
              <p className="text-white/70" style={{ fontFamily: 'Inter, sans-serif' }}>
                Track your progress
              </p>
            </div>

            <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-3xl p-6 mb-6">
              <div className="flex justify-between mb-4">
                <div>
                  <p className="text-white/70 text-sm mb-1">Current</p>
                  <p
                    className="text-3xl"
                    style={{ fontFamily: 'JetBrains Mono, monospace', fontWeight: 700 }}
                  >
                    ${selectedBucketData.current}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-white/70 text-sm mb-1">Target</p>
                  <p
                    className="text-3xl"
                    style={{ fontFamily: 'JetBrains Mono, monospace', fontWeight: 700 }}
                  >
                    ${selectedBucketData.target}
                  </p>
                </div>
              </div>
              <div className="h-3 bg-white/20 rounded-full overflow-hidden">
                <div
                  className="bg-[#FEFF09] h-full"
                  style={{ width: `${Math.min((selectedBucketData.current / selectedBucketData.target) * 100, 100)}%` }}
                />
              </div>
              <p className="text-center text-white/60 text-sm mt-2">
                ${selectedBucketData.target - selectedBucketData.current} to go
              </p>
            </div>

            <motion.button
              className="w-full bg-[#FEFF09] text-[#0F172A] py-4 rounded-full mb-3"
              style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600 }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              Add Money
            </motion.button>
            <div className="grid grid-cols-2 gap-3 mb-3">
              <motion.button
                onClick={() => {
                  setEditName(selectedBucketData.name);
                  setEditCurrent(selectedBucketData.current.toString());
                  setEditTarget(selectedBucketData.target.toString());
                  setEditIcon(selectedBucketData.icon);
                  setEditColor(selectedBucketData.color);
                  setShowEditModal(true);
                }}
                className="flex items-center justify-center gap-2 bg-[#FF44EC] text-white py-4 rounded-full"
                style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Edit2 className="w-5 h-5" />
                Edit
              </motion.button>
              <motion.button
                onClick={() => {
                  if (confirm(`Delete ${selectedBucketData.name}?`)) {
                    deleteBucket(selectedBucket as string);
                    setSelectedBucket(null);
                  }
                }}
                className="flex items-center justify-center gap-2 bg-white/10 text-white py-4 rounded-full hover:bg-red-500/80 transition-colors"
                style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Trash2 className="w-5 h-5" />
                Delete
              </motion.button>
            </div>
            <button
              onClick={() => setSelectedBucket(null)}
              className="w-full bg-white/10 text-white py-4 rounded-full"
              style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600 }}
            >
              Close
            </button>
          </motion.div>
        </motion.div>
        );
      })()}

      {/* New Goal Modal */}
      {showNewGoalModal && (
        <motion.div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-end justify-center z-[60]"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          onClick={() => setShowNewGoalModal(false)}
        >
          <motion.div
            className="bg-white rounded-t-[2.5rem] w-full max-w-md p-6 pb-8"
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 30 }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <h2
                className="text-2xl text-[#0F172A]"
                style={{ fontFamily: '"Momo Trust Display", sans-serif', fontWeight: 800 }}
              >
                Create New Goal
              </h2>
              <button
                onClick={() => setShowNewGoalModal(false)}
                className="w-8 h-8 flex items-center justify-center bg-[#0F172A]/5 rounded-full hover:bg-[#0F172A]/10"
              >
                <X className="w-5 h-5 text-[#0F172A]" />
              </button>
            </div>

            {/* Goal Name */}
            <div className="mb-4">
              <label
                className="text-sm text-[#0F172A]/70 mb-2 block"
                style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600 }}
              >
                Goal Name
              </label>
              <input
                type="text"
                placeholder="e.g., Vacation Fund"
                value={newGoalName}
                onChange={(e) => setNewGoalName(e.target.value)}
                className="w-full bg-[#F1F5F9] text-[#0F172A] rounded-2xl px-4 py-3 outline-none focus:ring-2 focus:ring-[#2820FF]"
                style={{ fontFamily: 'Inter, sans-serif' }}
              />
            </div>

            {/* Target Amount */}
            <div className="mb-6">
              <label
                className="text-sm text-[#0F172A]/70 mb-2 block"
                style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600 }}
              >
                Target Amount
              </label>
              <input
                type="number"
                placeholder="5000"
                value={newGoalTarget}
                onChange={(e) => setNewGoalTarget(e.target.value)}
                className="w-full bg-[#F1F5F9] text-[#0F172A] rounded-2xl px-4 py-3 outline-none focus:ring-2 focus:ring-[#2820FF]"
                style={{ fontFamily: 'Inter, sans-serif' }}
              />
            </div>

            {/* Choose Icon */}
            <div className="mb-6">
              <label
                className="text-sm text-[#0F172A]/70 mb-3 block"
                style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600 }}
              >
                Choose Icon
              </label>
              <div className="grid grid-cols-6 gap-3">
                {availableIcons.map((iconName) => {
                  const IconComponent = iconMap[iconName];
                  return (
                    <button
                      key={iconName}
                      onClick={() => setSelectedIcon(iconName)}
                      className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-all ${
                        selectedIcon === iconName
                          ? 'bg-[#FF44EC] text-white scale-110'
                          : 'bg-[#F1F5F9] text-[#0F172A]/60 hover:bg-[#E2E8F0]'
                      }`}
                    >
                      {IconComponent && <IconComponent className="w-6 h-6" />}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Choose Color */}
            <div className="mb-6">
              <label
                className="text-sm text-[#0F172A]/70 mb-3 block"
                style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600 }}
              >
                Choose Color
              </label>
              <div className="flex gap-3">
                {availableColors.map((color) => (
                  <button
                    key={color.value}
                    onClick={() => setSelectedColor(color.value)}
                    className={`w-12 h-12 rounded-2xl transition-all ${color.value} ${
                      selectedColor === color.value
                        ? 'ring-4 ring-[#0F172A]/20 scale-110'
                        : 'hover:scale-105'
                    }`}
                  />
                ))}
              </div>
            </div>

            {/* Create Button */}
            <motion.button
              className="w-full bg-[#0F172A] text-white py-4 rounded-full"
              style={{ fontFamily: '"Momo Trust Display", sans-serif', fontWeight: 800 }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleCreateGoal}
            >
              Create Goal
            </motion.button>
          </motion.div>
        </motion.div>
      )}

      {/* Edit Goal Modal */}
      {showEditModal && selectedBucketData && (
        <motion.div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-end justify-center z-[60]"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          onClick={() => setShowEditModal(false)}
        >
          <motion.div
            className="bg-white rounded-t-[2.5rem] w-full max-w-md p-6 pb-8"
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 30 }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <h2
                className="text-2xl text-[#0F172A]"
                style={{ fontFamily: '"Momo Trust Display", sans-serif', fontWeight: 800 }}
              >
                Edit Goal
              </h2>
              <button
                onClick={() => setShowEditModal(false)}
                className="w-8 h-8 flex items-center justify-center bg-[#0F172A]/5 rounded-full hover:bg-[#0F172A]/10"
              >
                <X className="w-5 h-5 text-[#0F172A]" />
              </button>
            </div>

            {/* Goal Name */}
            <div className="mb-4">
              <label
                className="text-sm text-[#0F172A]/70 mb-2 block"
                style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600 }}
              >
                Goal Name
              </label>
              <input
                type="text"
                placeholder="e.g., Vacation Fund"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                className="w-full bg-[#F1F5F9] text-[#0F172A] rounded-2xl px-4 py-3 outline-none focus:ring-2 focus:ring-[#2820FF]"
                style={{ fontFamily: 'Inter, sans-serif' }}
              />
            </div>

            {/* Current Amount */}
            <div className="mb-4">
              <label
                className="text-sm text-[#0F172A]/70 mb-2 block"
                style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600 }}
              >
                Current Amount
              </label>
              <input
                type="number"
                placeholder="5000"
                value={editCurrent}
                onChange={(e) => setEditCurrent(e.target.value)}
                className="w-full bg-[#F1F5F9] text-[#0F172A] rounded-2xl px-4 py-3 outline-none focus:ring-2 focus:ring-[#2820FF]"
                style={{ fontFamily: 'Inter, sans-serif' }}
              />
            </div>

            {/* Target Amount */}
            <div className="mb-6">
              <label
                className="text-sm text-[#0F172A]/70 mb-2 block"
                style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600 }}
              >
                Target Amount
              </label>
              <input
                type="number"
                placeholder="5000"
                value={editTarget}
                onChange={(e) => setEditTarget(e.target.value)}
                className="w-full bg-[#F1F5F9] text-[#0F172A] rounded-2xl px-4 py-3 outline-none focus:ring-2 focus:ring-[#2820FF]"
                style={{ fontFamily: 'Inter, sans-serif' }}
              />
            </div>

            {/* Choose Icon */}
            <div className="mb-6">
              <label
                className="text-sm text-[#0F172A]/70 mb-3 block"
                style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600 }}
              >
                Choose Icon
              </label>
              <div className="grid grid-cols-6 gap-3">
                {availableIcons.map((iconName) => {
                  const IconComponent = iconMap[iconName];
                  return (
                    <button
                      key={iconName}
                      onClick={() => setEditIcon(iconName)}
                      className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-all ${
                        editIcon === iconName
                          ? 'bg-[#FF44EC] text-white scale-110'
                          : 'bg-[#F1F5F9] text-[#0F172A]/60 hover:bg-[#E2E8F0]'
                      }`}
                    >
                      {IconComponent && <IconComponent className="w-6 h-6" />}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Choose Color */}
            <div className="mb-6">
              <label
                className="text-sm text-[#0F172A]/70 mb-3 block"
                style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600 }}
              >
                Choose Color
              </label>
              <div className="flex gap-3">
                {availableColors.map((color) => (
                  <button
                    key={color.value}
                    onClick={() => setEditColor(color.value)}
                    className={`w-12 h-12 rounded-2xl transition-all ${color.value} ${
                      editColor === color.value
                        ? 'ring-4 ring-[#0F172A]/20 scale-110'
                        : 'hover:scale-105'
                    }`}
                  />
                ))}
              </div>
            </div>

            {/* Update Button */}
            <motion.button
              className="w-full bg-[#0F172A] text-white py-4 rounded-full"
              style={{ fontFamily: '"Momo Trust Display", sans-serif', fontWeight: 800 }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleEditGoal}
            >
              Update Goal
            </motion.button>
          </motion.div>
        </motion.div>
      )}
    </div>
  );
}