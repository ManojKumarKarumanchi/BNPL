import { motion } from 'framer-motion';
import { orderData } from '../data/mockData';
import { SparklesIcon } from '@heroicons/react/24/solid';

const OrderSummary = () => {
  const { product, pricing, deal_stats } = orderData;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="pb-6 border-b border-gray-200"
    >
      {/* Product Info */}
      <div className="flex gap-4 mb-4">
        <div className="flex-shrink-0 relative">
          <img
            src={product.image}
            alt={product.title}
            className="w-20 h-20 rounded-lg object-cover shadow-sm"
          />
          {product.grabon_exclusive && (
            <div className="absolute -top-1 -right-1 bg-gradient-to-br from-orange-500 to-pink-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full shadow-md">
              GrabOn
            </div>
          )}
        </div>
        <div className="flex-1">
          <h2 className="text-base font-semibold text-gray-900 mb-1 leading-tight">
            {product.title}
          </h2>
          <p className="text-sm text-gray-500 mb-1">{product.merchant}</p>
          {product.couponCode && (
            <div className="inline-flex items-center gap-1 px-2 py-0.5 bg-green-50 border border-green-200 rounded text-xs font-mono text-green-700">
              <SparklesIcon className="w-3 h-3" />
              {product.couponCode}
            </div>
          )}
        </div>
      </div>

      {/* Deal Stats */}
      {deal_stats && (
        <div className="flex items-center gap-3 mb-4 text-xs text-gray-600">
          {deal_stats.trending && (
            <span className="flex items-center gap-1">
              <span className="text-orange-500">🔥</span>
              <span className="font-medium">Trending</span>
            </span>
          )}
          <span className="flex items-center gap-1">
            <span>👥</span>
            <span>{deal_stats.people_grabbed.toLocaleString()} grabbed</span>
          </span>
          {deal_stats.expires_in && (
            <span className="flex items-center gap-1 text-red-600">
              <span>⏰</span>
              <span>Ends in {deal_stats.expires_in}</span>
            </span>
          )}
        </div>
      )}

      {/* Pricing Breakdown */}
      <div className="space-y-2">
        {/* Subtotal */}
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Subtotal</span>
          <span className="text-gray-900">₹{pricing.subtotal.toLocaleString('en-IN')}</span>
        </div>

        {/* Discount */}
        <div className="flex justify-between text-sm">
          <div className="flex items-center gap-1">
            <span className="text-success-600 font-medium">GrabOn Savings</span>
            <span className="text-xs bg-success-100 text-success-700 px-1.5 py-0.5 rounded font-semibold">
              {Math.round((pricing.discount / pricing.subtotal) * 100)}% OFF
            </span>
          </div>
          <span className="text-success-600 font-medium">
            -₹{pricing.discount.toLocaleString('en-IN')}
          </span>
        </div>

        {/* Total */}
        <div className="flex justify-between pt-2 border-t border-gray-100">
          <span className="text-base font-semibold text-gray-900">Total</span>
          <span className="text-2xl font-bold text-gray-900">
            ₹{pricing.total.toLocaleString('en-IN')}
          </span>
        </div>
      </div>
    </motion.div>
  );
};

export default OrderSummary;
