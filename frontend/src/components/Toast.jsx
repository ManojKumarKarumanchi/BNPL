import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircleIcon, XCircleIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';

const Toast = ({ type = 'info', message, onClose, duration = 4000 }) => {
  const icons = {
    success: <CheckCircleIcon className="w-5 h-5 text-success-600" />,
    error: <XCircleIcon className="w-5 h-5 text-red-600" />,
    warning: <ExclamationTriangleIcon className="w-5 h-5 text-amber-600" />
  };

  const bgColors = {
    success: 'bg-success-50 border-success-200',
    error: 'bg-red-50 border-red-200',
    warning: 'bg-amber-50 border-amber-200'
  };

  // Auto-close after duration
  if (duration > 0) {
    setTimeout(onClose, duration);
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className={`fixed top-4 right-4 z-50 max-w-md p-4 rounded-lg border shadow-lg ${bgColors[type]}`}
      >
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0 mt-0.5">
            {icons[type]}
          </div>
          <div className="flex-1">
            <p className="text-sm text-gray-800">{message}</p>
          </div>
          <button
            onClick={onClose}
            className="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <XCircleIcon className="w-5 h-5" />
          </button>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

export default Toast;
