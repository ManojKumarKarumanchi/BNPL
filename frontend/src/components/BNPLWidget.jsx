import { motion, AnimatePresence } from 'framer-motion';
import { useState } from 'react';
import {
  ShieldCheckIcon,
  CheckBadgeIcon,
  ChevronDownIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline';
import EMIOptionCard from './EMIOptionCard';
import { emiOptions as defaultEmiOptions } from '../data/mockData';

const BNPLWidget = ({
  isExpanded,
  selectedEMI,
  onEMISelect,
  userPersona,
  showQualificationReason,
  onToggleQualification
}) => {
  // Extract persona data with proper null handling
  const eligibilityStatus = userPersona?.status || 'loading';
  const creditLimit = (userPersona?.creditLimit !== undefined && userPersona?.creditLimit !== null)
    ? userPersona.creditLimit
    : 0;
  const reason = userPersona?.reason || '';
  const transactionHistory = userPersona?.transactionHistory || {};
  const emiOptions = userPersona?.emiOptions || defaultEmiOptions;
  // Loading skeleton component
  const LoadingSkeleton = () => (
    <div className="space-y-4 animate-pulse">
      <div className="h-6 bg-gray-200 rounded w-3/4"></div>
      <div className="h-4 bg-gray-200 rounded w-1/2"></div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
        ))}
      </div>
    </div>
  );

  // Collapsed state (when payment method not selected)
  if (!isExpanded) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="p-4 bg-gradient-to-r from-grabcredit-50 to-blue-50 rounded-lg border border-grabcredit-200"
      >
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <h4 className="text-base font-semibold text-gray-900">Pay Later with GrabCredit</h4>
              <span className="px-2 py-0.5 bg-success-500 text-white text-xs font-semibold rounded-full">
                Pre-approved
              </span>
            </div>
            <p className="text-sm text-gray-600">Instant EMI options</p>
          </div>
          <ChevronRightIcon className="w-5 h-5 text-gray-400" />
        </div>
      </motion.div>
    );
  }

  // Loading state
  if (eligibilityStatus === 'loading') {
    return (
      <motion.div
        initial={{ opacity: 0, height: 0 }}
        animate={{ opacity: 1, height: 'auto' }}
        exit={{ opacity: 0, height: 0 }}
        className="p-6 bg-white rounded-lg border border-gray-200"
      >
        <LoadingSkeleton />
      </motion.div>
    );
  }

  // Not eligible state (with AI-generated reason and alternative payments)
  if (eligibilityStatus === 'not_eligible' || eligibilityStatus === 'amount_exceeds_limit') {
    return (
      <motion.div
        initial={{ opacity: 0, height: 0 }}
        animate={{ opacity: 1, height: 'auto' }}
        exit={{ opacity: 0, height: 0 }}
        className="p-6 bg-red-50/50 rounded-lg border border-red-200"
      >
        <div className="mb-6">
          <div className="flex items-start gap-3 mb-3">
            <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0">
              <svg className="w-6 h-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <div className="flex-1">
              <h4 className="text-base font-semibold text-gray-900 mb-2">
                Pay Later not available
              </h4>
              <p className="text-sm text-gray-700 leading-relaxed">
                {reason || "This option is not available for this purchase. Please choose another payment method."}
              </p>
            </div>
          </div>

          {/* Alternative Payment Suggestions */}
          <div className="mt-4 pt-4 border-t border-red-200">
            <p className="text-xs font-semibold text-gray-700 mb-2">Try these instead:</p>
            <div className="flex flex-wrap gap-2">
              <div className="flex items-center gap-1.5 px-3 py-1.5 bg-white rounded-lg border border-gray-200 text-xs">
                <svg className="w-4 h-4 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M12 20h4.01M6 8h2a2 2 0 002-2V4a2 2 0 00-2-2H6a2 2 0 00-2 2v2a2 2 0 002 2zm0 0v2a2 2 0 002 2h2a2 2 0 002-2V8a2 2 0 00-2-2h-2a2 2 0 00-2 2v2zm0 0H4m16 4v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2a2 2 0 012-2h2a2 2 0 012 2z" />
                </svg>
                <span className="font-medium text-gray-700">UPI</span>
              </div>
              <div className="flex items-center gap-1.5 px-3 py-1.5 bg-white rounded-lg border border-gray-200 text-xs">
                <svg className="w-4 h-4 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                </svg>
                <span className="font-medium text-gray-700">Card</span>
              </div>
              <div className="flex items-center gap-1.5 px-3 py-1.5 bg-white rounded-lg border border-gray-200 text-xs">
                <svg className="w-4 h-4 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z" />
                </svg>
                <span className="font-medium text-gray-700">Netbanking</span>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    );
  }

  // New user / Risk state
  if (eligibilityStatus === 'new_user') {
    return (
      <motion.div
        initial={{ opacity: 0, height: 0 }}
        animate={{ opacity: 1, height: 'auto' }}
        exit={{ opacity: 0, height: 0 }}
        className="p-6 bg-gradient-to-br from-amber-50 to-orange-50 rounded-lg border border-amber-200"
      >
        <div className="mb-6">
          <div className="flex items-start gap-3 mb-3">
            <div className="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center flex-shrink-0">
              <svg className="w-6 h-6 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div>
              <h4 className="text-base font-semibold text-gray-900 mb-1">
                Complete purchases to unlock Pay Later
              </h4>
              <p className="text-sm text-gray-600">
                Build your purchase history with us to access instant credit options.
              </p>
            </div>
          </div>
        </div>

        {/* Disabled EMI Options */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {emiOptions.map((option) => (
            <EMIOptionCard
              key={option.id}
              option={option}
              isSelected={false}
              onSelect={() => {}}
              isDisabled={true}
            />
          ))}
        </div>
      </motion.div>
    );
  }

  // Approved state (default)
  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      exit={{ opacity: 0, height: 0 }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      className="p-6 bg-gradient-to-br from-white via-grabcredit-50/30 to-white rounded-lg border border-grabcredit-200 shadow-soft"
    >
      {/* Header Section */}
      <div className="mb-6">
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <h3 className="text-xl md:text-2xl font-bold text-gray-900 mb-2">
            You're pre-approved for ₹{creditLimit.toLocaleString('en-IN')}
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            Powered by <span className="font-semibold text-grabcredit-700">Poonawalla Fincorp</span>
          </p>

          {/* Trust Badges */}
          <div className="flex flex-wrap gap-4">
            <div className="flex items-center gap-1.5 text-sm text-gray-700">
              <ShieldCheckIcon className="w-5 h-5 text-success-600" />
              <span>No hidden charges</span>
            </div>
            <div className="flex items-center gap-1.5 text-sm text-gray-700">
              <CheckBadgeIcon className="w-5 h-5 text-grabcredit-600" />
              <span>Secure</span>
            </div>
          </div>
        </motion.div>
      </div>

      {/* EMI Options Section */}
      <div className="mb-5">
        <h4 className="text-sm font-semibold text-gray-900 mb-3">Choose your plan</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {emiOptions.map((option, index) => (
            <motion.div
              key={option.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 + index * 0.05 }}
            >
              <EMIOptionCard
                option={option}
                isSelected={selectedEMI === option.id}
                onSelect={onEMISelect}
              />
            </motion.div>
          ))}
        </div>
      </div>

      {/* AI Explanation Section */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        <button
          onClick={onToggleQualification}
          aria-expanded={showQualificationReason}
          aria-label="Why you qualify for this credit offer"
          className="w-full flex items-center justify-between p-4 bg-blue-50/50 hover:bg-blue-50 rounded-lg border border-blue-100 transition-colors duration-200"
        >
          <span className="text-sm font-medium text-grabcredit-700">
            Why you qualify
          </span>
          <ChevronDownIcon
            className={`w-5 h-5 text-grabcredit-700 transition-transform duration-250 ${
              showQualificationReason ? 'rotate-180' : ''
            }`}
          />
        </button>

        <AnimatePresence>
          {showQualificationReason && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.25 }}
              className="overflow-hidden"
            >
              <div className="mt-3 p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border border-blue-100">
                <p className="text-sm text-gray-700 leading-relaxed">
                  {reason}
                </p>
                {transactionHistory && (
                  <div className="mt-3 pt-3 border-t border-blue-200/50">
                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div>
                        <span className="text-gray-500">Total Purchases</span>
                        <p className="font-semibold text-gray-900">
                          {transactionHistory.totalPurchases}
                        </p>
                      </div>
                      <div>
                        <span className="text-gray-500">Avg Order Value</span>
                        <p className="font-semibold text-gray-900">
                          ₹{transactionHistory.avgOrderValue?.toLocaleString('en-IN') || 0}
                        </p>
                      </div>
                      <div>
                        <span className="text-gray-500">Return Rate</span>
                        <p className="font-semibold text-gray-900">
                          {transactionHistory.returnRate}%
                        </p>
                      </div>
                      <div>
                        <span className="text-gray-500">Member Since</span>
                        <p className="font-semibold text-gray-900">
                          {transactionHistory.memberSince ? new Date(transactionHistory.memberSince).toLocaleDateString('en-IN', { month: 'short', year: 'numeric' }) : 'N/A'}
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </motion.div>
  );
};

export default BNPLWidget;
