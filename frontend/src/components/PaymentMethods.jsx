import { motion } from 'framer-motion';
import {
  QrCodeIcon,
  CreditCardIcon,
  BuildingLibraryIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';
import { paymentMethods } from '../data/mockData';

const iconMap = {
  QrCodeIcon,
  CreditCardIcon,
  BuildingLibraryIcon,
  SparklesIcon,
};

const PaymentMethods = ({ selectedPayment, onPaymentSelect, eligibilityStatus }) => {
  // Determine if GrabCredit should be disabled
  const isGrabCreditDisabled = eligibilityStatus &&
    (eligibilityStatus === 'not_eligible' ||
     eligibilityStatus === 'new_user' ||
     eligibilityStatus === 'amount_exceeds_limit');

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.1 }}
      className="space-y-3"
    >
      <h3 className="text-sm font-semibold text-gray-900 mb-3">Payment Method</h3>

      <div className="space-y-2">
        {paymentMethods.map((method) => {
          const Icon = iconMap[method.icon];
          const isSelected = selectedPayment === method.id;
          const isFeatured = method.featured;
          const isDisabled = isFeatured && isGrabCreditDisabled;

          return (
            <motion.button
              key={method.id}
              onClick={() => !isDisabled && onPaymentSelect(method.id)}
              whileHover={!isDisabled ? { scale: 1.01 } : {}}
              whileTap={!isDisabled ? { scale: 0.99 } : {}}
              disabled={isDisabled}
              className={`
                w-full flex items-center gap-3 p-4 rounded-lg border-2 transition-all duration-200
                ${isDisabled
                  ? 'border-gray-200 bg-gray-50 opacity-60 cursor-not-allowed'
                  : isSelected
                    ? 'border-grabcredit-600 bg-grabcredit-50/50 shadow-md'
                    : 'border-gray-200 bg-white hover:border-gray-300'
                }
                ${isFeatured && !isSelected && !isDisabled ? 'ring-1 ring-grabcredit-200' : ''}
              `}
            >
              {/* Radio Button */}
              <div className={`
                flex-shrink-0 w-5 h-5 rounded-full border-2 flex items-center justify-center
                ${isSelected ? 'border-grabcredit-600' : 'border-gray-300'}
              `}>
                {isSelected && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="w-3 h-3 rounded-full bg-grabcredit-600"
                  />
                )}
              </div>

              {/* Icon */}
              <div className={`
                flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center
                ${isDisabled ? 'bg-gray-100' : isSelected ? 'bg-grabcredit-100' : 'bg-gray-100'}
              `}>
                <Icon className={`w-6 h-6 ${isDisabled ? 'text-gray-400' : isSelected ? 'text-grabcredit-600' : 'text-gray-600'}`} />
              </div>

              {/* Label */}
              <div className="flex-1 text-left">
                <span className={`
                  text-base font-medium
                  ${isDisabled ? 'text-gray-500' : isSelected ? 'text-gray-900' : 'text-gray-700'}
                `}>
                  {method.label}
                </span>
                {isFeatured && !isDisabled && (
                  <div className="flex items-center gap-1 mt-0.5">
                    <SparklesIcon className="w-3 h-3 text-grabcredit-600" />
                    <span className="text-xs text-grabcredit-600 font-medium">Instant EMI</span>
                  </div>
                )}
                {isFeatured && isDisabled && (
                  <div className="flex items-center gap-1 mt-0.5">
                    <svg className="w-3 h-3 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="text-xs text-gray-500 font-medium">Not available</span>
                  </div>
                )}
              </div>

              {/* Arrow for featured */}
              {isFeatured && isSelected && (
                <svg
                  className="w-5 h-5 text-grabcredit-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              )}
            </motion.button>
          );
        })}
      </div>
    </motion.div>
  );
};

export default PaymentMethods;
