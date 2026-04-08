import { motion } from 'framer-motion';

const EMIOptionCard = ({ option, isSelected, onSelect, isDisabled = false }) => {
  // Handle both camelCase (frontend) and snake_case (API) property names
  const {
    id,
    duration,
    monthlyPayment,
    monthly_payment,
    tag,
    totalAmount,
    total_amount,
    is_one_time_payment,
    isOneTimePayment,
    due_date,
    dueDate
  } = option || {};

  // Use camelCase first, fallback to snake_case, then to 0
  const displayMonthlyPayment = monthlyPayment || monthly_payment || 0;
  const displayTotalAmount = totalAmount || total_amount || 0;
  const isOnetime = isOneTimePayment || is_one_time_payment || false;
  const paymentDueDate = dueDate || due_date;

  return (
    <motion.button
      onClick={() => !isDisabled && onSelect(id)}
      disabled={isDisabled}
      whileHover={!isDisabled ? { scale: 1.02 } : {}}
      whileTap={!isDisabled ? { scale: 0.98 } : {}}
      aria-label={`Select ${duration} month EMI plan, ${displayMonthlyPayment.toLocaleString('en-IN')} rupees per month`}
      aria-pressed={isSelected}
      className={`
        relative p-4 rounded-lg border-2 transition-all duration-200 text-left w-full
        ${isSelected
          ? 'border-grabcredit-600 bg-grabcredit-50 shadow-lg shadow-grabcredit-200/50'
          : 'border-gray-200 bg-white hover:border-grabcredit-300'
        }
        ${isDisabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
      `}
    >
      {/* Tag */}
      {tag && (
        <div className="absolute -top-2 left-4">
          <span className={`
            inline-block px-2 py-0.5 text-xs font-semibold rounded-full
            ${tag === 'No Cost EMI'
              ? 'bg-success-500 text-white'
              : 'bg-amber-500 text-white'
            }
          `}>
            {tag}
          </span>
        </div>
      )}

      {/* Duration / Payment Info */}
      {isOnetime ? (
        <>
          {/* 15-day One-time Payment (PayU LazyPay Primary) */}
          <div className="mb-2">
            <span className="text-sm font-semibold text-grabcredit-600">
              Pay in 15 days
            </span>
          </div>

          {/* Full Amount */}
          <div className="mb-1">
            <span className="text-2xl font-bold text-gray-900">
              ₹{displayMonthlyPayment.toLocaleString('en-IN')}
            </span>
            <span className="text-sm text-gray-500 ml-1">full amount</span>
          </div>

          {/* Due Date */}
          {paymentDueDate && (
            <div className="text-xs text-gray-500">
              Due by: {new Date(paymentDueDate).toLocaleDateString('en-IN', {
                day: 'numeric',
                month: 'short',
                year: 'numeric'
              })}
            </div>
          )}

          {/* Zero Interest Badge */}
          <div className="mt-2 text-xs font-medium text-success-600">
            ✓ Zero interest · No processing fees
          </div>
        </>
      ) : (
        <>
          {/* EMI Duration */}
          <div className="mb-2">
            <span className="text-sm font-medium text-gray-600">
              {duration} months
            </span>
          </div>

          {/* Monthly Payment */}
          <div className="mb-1">
            <span className="text-2xl font-bold text-gray-900">
              ₹{displayMonthlyPayment.toLocaleString('en-IN')}
            </span>
            <span className="text-sm text-gray-500">/mo</span>
          </div>

          {/* Total Amount */}
          <div className="text-xs text-gray-500">
            Total: ₹{displayTotalAmount.toLocaleString('en-IN')}
          </div>
        </>
      )}

      {/* Selection Indicator */}
      {isSelected && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="absolute top-4 right-4"
        >
          <div className="w-6 h-6 bg-grabcredit-600 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        </motion.div>
      )}
    </motion.button>
  );
};

export default EMIOptionCard;
