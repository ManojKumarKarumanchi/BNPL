import { useState, useMemo } from 'react';
import { orderData } from '../data/mockData';

export const useBNPLState = (initialEligibility = 'approved', emiOptions = null) => {
  const [selectedPayment, setSelectedPayment] = useState('grabcredit');
  const [selectedEMI, setSelectedEMI] = useState(null);
  const [showQualificationReason, setShowQualificationReason] = useState(false);
  const [eligibilityStatus, setEligibilityStatus] = useState(initialEligibility);

  // Computed values
  const isGrabCreditSelected = selectedPayment === 'grabcredit';

  const canProceed = useMemo(() => {
    if (eligibilityStatus === 'not_eligible') return false;
    if (eligibilityStatus === 'new_user') return false;
    if (eligibilityStatus === 'loading') return false;
    if (isGrabCreditSelected && !selectedEMI) return false;
    return true;
  }, [eligibilityStatus, isGrabCreditSelected, selectedEMI]);

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
    if (eligibilityStatus === 'new_user') {
      return `Pay ₹${orderData.pricing.total.toLocaleString('en-IN')}`;
    }
    if (eligibilityStatus === 'loading') {
      return 'Please wait...';
    }
    if (isGrabCreditSelected && selectedEMI) {
      return 'Continue with EMI';
    }
    return `Pay ₹${orderData.pricing.total.toLocaleString('en-IN')}`;
  }, [eligibilityStatus, isGrabCreditSelected, selectedEMI]);

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
