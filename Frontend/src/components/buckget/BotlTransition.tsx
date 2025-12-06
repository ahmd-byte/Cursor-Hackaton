import { motion } from 'motion/react';
import imgBotl from 'assets/IMG_6293 1.png';

export function BotlTransition() {
  return (
    <motion.div
      className="fixed inset-0 z-50 overflow-hidden"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Animated Gradient Background - Bottom to Top */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-b from-[#83d6e2] to-[#2820ff]"
        initial={{ y: '100%' }}
        animate={{ y: '0%' }}
        transition={{ duration: 0.6, ease: 'easeIn' }}
      />

      {/* Content */}
      <motion.div
        className="absolute inset-0 flex flex-col items-center justify-center"
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.3, type: 'spring', stiffness: 200 }}
      >
        {/* Botl Image */}
        <motion.div
          className="w-[179.27px] h-[190.41px] mb-8"
          animate={{
            y: [0, -10, 0],
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        >
          <img
            alt="Botl the robot mascot"
            className="w-full h-full object-cover"
            src={imgBotl}
          />
        </motion.div>

        {/* Success Text */}
        <p
          className="text-white text-center leading-[29.67px] text-[19.78px] max-w-[278px]"
          style={{ fontFamily: '"Momo Trust Display", sans-serif', fontWeight: 400 }}
        >
          Bottl is now happily
          <br />
          filling up your buckets!
        </p>
      </motion.div>
    </motion.div>
  );
}