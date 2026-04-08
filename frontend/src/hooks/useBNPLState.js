import { useState, useMemo, useEffect } from 'react';
import { orderData } from '../data/mockData';

export const useBNPLState = (initialEligibility = 'approved', emiOptions = null) => {
  const [selectedPayment, setSelectedPayment] = useState('grabcredit');
  const [selectedEMI, setSelectedEMI] = useState(null);
  const [showQualificationReason, setShowQualificationReason] = useState(false);
  const [eligibilityStatus, setEligibilityStatus] = useState(initialEligibility);

  // Auto-select first EMI option (shortest tenure, 0% interest) when BNPL is approved
  useEffect(() => {
    if (eligibilityStatus === 'approved' && selectedPayment === 'grabcredit' && emiOptions && emiOptions.length > 0 && !selectedEMI) {
      // Auto-select the first option (shortest tenure, typically 3-month @ 0%)
      setSelectedEMI(emiOptions[0].id);
    }
  }, [eligibilityStatus, selectedPayment, emiOptions, selectedEMI]);

  // Computed values
  const isGrabCreditSelected = selectedPayment === 'grabcredit';

  const canProceed = useMemo(() => {
    if (eligibilityStatus === 'not_eligible') return false;
    if (eligibilityStatus === 'new_user') return false;
    if (eligibilityStatus === 'loading') return false;
    if (eligibilityStatus === 'amount_exceeds_limit') return false;
    // For BNPL, allow proceeding if approved (default EMI will be auto-selected)
    // User can still manually change EMI before checkout
    if (isGrabCreditSelected && eligibilityStatus === 'approved') return true;
    return true;
  }, [eligibilityStatus, isGrabCreditSelected]);

  const finalAmount = useMemo(() => {
    if (isGrabCreditSelected && selectedEMI && emiOptions) {
      const emiPlan = emiOptions.find(opt => opt.id === selectedEMI);
      return emiPlan ? emiPlan.monthlyPayment : orderData.pricing.total;
    }
    return orderData.pricing.total;
  }, [isGrabCreditSelected, selectedEMI, emiOptions]);

  const ctaText = useMemo(() => {
    if (eligibilityStatus === 'not_eligible') {
      return 'Choose another payment method';
    }
    if (eligibilityStatus === 'amount_exceeds_limit') {
      return 'Amount exceeds limit';
    }
    if (eligibilityStatus === 'new_user') {
      return `Pay ₹${orderData.pricing.total.toLocaleString('en-IN')}`;
    }
    if (eligibilityStatus === 'loading') {
      return 'Please wait...';
    }
    if (isGrabCreditSelected && eligibilityStatus === 'approved') {
      return 'Continue with Pay Later';
    }
    return `Pay ₹${orderData.pricing.total.toLocaleString('en-IN')}`;
  }, [eligibilityStatus, isGrabCreditSelected]);

  const handlePaymentSelect = (paymentId) => {
    setSelectedPayment(paymentId);
    if (paymentId !== 'grabcredit') {
      setSelectedEMI(null);
    }
  };

  return {
    selectedPayment,
    setSelectedPayment: handlePaymentSelect,
    selectedEMI,
    setSelectedEMI,
    eligibilityStatus,
    setEligibilityStatus,
    showQualificationReason,
    setShowQualificationReason,
    isGrabCreditSelected,
    canProceed,
    finalAmount,
    ctaText
  };
};
