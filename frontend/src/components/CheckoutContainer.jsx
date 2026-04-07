import { motion } from 'framer-motion';
import GrabOnBranding from './GrabOnBranding';

const CheckoutContainer = ({ children }) => {
  return (
    <div className="min-h-screen py-8 px-4 md:py-12">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="max-w-2xl mx-auto"
      >
        {/* GrabOn Branding */}
        <GrabOnBranding />

        {/* Header */}
        <div className="text-center mb-8">
          <motion.h1
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-3xl md:text-4xl font-display font-bold text-gray-900 mb-2"
          >
            Secure Checkout
          </motion.h1>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="text-gray-600"
          >
            Pay now or split with <span className="font-semibold text-grabcredit-600">GrabCredit BNPL</span>
          </motion.p>
        </div>

        {/* Main Card */}
        <div className="bg-white rounded-2xl shadow-soft-lg border border-gray-100 p-6 md:p-8 space-y-6">
          {children}
        </div>

        {/* Security Badge */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="mt-6 text-center"
        >
          <div className="flex items-center justify-center gap-2 text-sm text-gray-500">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
            </svg>
            <span>Secured by 256-bit SSL encryption</span>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default CheckoutContainer;
