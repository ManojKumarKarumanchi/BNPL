import { motion } from 'framer-motion';

const GrabOnBranding = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
      className="mb-6 text-center"
    >
      {/* GrabOn Logo/Badge */}
      <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-orange-500 to-pink-500 rounded-full shadow-lg mb-3">
        <span className="text-2xl">🎁</span>
        <span className="text-white font-bold text-lg">GrabOn</span>
        <span className="text-white text-xs bg-white/20 px-2 py-0.5 rounded-full">Exclusive Deal</span>
      </div>

      {/* Trust Stats */}
      <div className="flex items-center justify-center gap-4 text-xs text-gray-600">
        <div className="flex items-center gap-1">
          <span>⭐</span>
          <span className="font-medium">40M+ Users</span>
        </div>
        <div className="w-1 h-1 bg-gray-300 rounded-full"></div>
        <div className="flex items-center gap-1">
          <span>🛡️</span>
          <span className="font-medium">Verified Deals</span>
        </div>
        <div className="w-1 h-1 bg-gray-300 rounded-full"></div>
        <div className="flex items-center gap-1">
          <span>🏪</span>
          <span className="font-medium">600+ Merchants</span>
        </div>
      </div>
    </motion.div>
  );
};

export default GrabOnBranding;
