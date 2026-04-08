import { motion } from 'framer-motion';

const LoadingSkeleton = ({ variant = 'default' }) => {
  if (variant === 'persona') {
    return (
      <div className="space-y-3 animate-pulse">
        <div className="h-16 bg-gray-200 rounded-lg"></div>
        <div className="h-16 bg-gray-200 rounded-lg"></div>
        <div className="h-16 bg-gray-200 rounded-lg"></div>
      </div>
    );
  }

  if (variant === 'bnpl') {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="p-6 bg-white rounded-lg border border-gray-200"
      >
        <div className="space-y-4 animate-pulse">
          {/* Header */}
          <div>
            <div className="h-8 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          </div>

          {/* Trust badges */}
          <div className="flex gap-4">
            <div className="h-5 bg-gray-200 rounded w-32"></div>
            <div className="h-5 bg-gray-200 rounded w-24"></div>
          </div>

          {/* EMI options title */}
          <div className="h-5 bg-gray-200 rounded w-40 mt-6"></div>

          {/* EMI cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="p-4 bg-gray-100 rounded-lg">
                <div className="h-6 bg-gray-200 rounded w-24 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-full mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              </div>
            ))}
          </div>

          {/* Why you qualify button */}
          <div className="h-12 bg-gray-200 rounded mt-4"></div>
        </div>
      </motion.div>
    );
  }

  // Default skeleton
  return (
    <div className="space-y-4 animate-pulse">
      <div className="h-6 bg-gray-200 rounded w-3/4"></div>
      <div className="h-4 bg-gray-200 rounded w-1/2"></div>
    </div>
  );
};

export default LoadingSkeleton;
