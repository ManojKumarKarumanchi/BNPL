import { useState, useMemo, useEffect } from 'react';
import { orderData } from '../data/mockData';

export const useBNPLState = (initialEligibility = 'approved', emiOptions = null) => {
  const [selectedPayment, setSelectedPayment] = useState('grabcredit');
  const [selectedEMI, setSelectedEMI] = useState(null);
  const [showQualificationReason, setShowQualificationReason] = useState(false);
  const [eligibilityStatus, setEligibilityStatus] = useState(initialEligibility);

  // Update eligibility status when user switches personas
  useEffect(() => {
    setEligibilityStatus(initialEligibility);
  }, [initialEligibility]);

  // No auto-switch away from GrabCredit for ineligible users
  // Let them click and see the rejection reason
  // The "Continue with Pay Later" button will be disabled instead

  // Auto-select first EMI option (15-day BNPL) when Pay Later is approved
  useEffect(() => {
    if (eligibilityStatus === 'approved' && selectedPayment === 'grabcredit' && emiOptions && emiOptions.length > 0 && !selectedEMI) {
      // Auto-select the first option (15-day BNPL @ 0%)
      setSelectedEMI(emiOptions[0].id);
    }
  }, [eligibilityStatus, selectedPayment, emiOptions, selectedEMI]);

  // Computed values
  const isGrabCreditSelected = selectedPayment === 'grabcredit';

  const canProceed = useMemo(() => {
    // Block checkout during loading
    if (eligibilityStatus === 'loading') return false;

    // Allow proceeding for all non-Pay Later payment methods (UPI, Card, Netbanking, etc.)
    if (!isGrabCreditSelected) return true;

    // For Pay Later: Only allow if approved
    if (isGrabCreditSelected) {
      // Block if ineligible
      if (
        eligibilityStatus === 'not_eligible' ||
        eligibilityStatus === 'new_user' ||
        eligibilityStatus === 'amount_exceeds_limit'
      ) {
        return false;
      }

      // Allow if approved
      if (eligibilityStatus === 'approved') {
        return true;
      }

      // Block for any other status
      return false;
    }

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
    if (eligibilityStatus === 'loading') {
      return 'Please wait...';
    }

    // If Pay Later is selected but user is ineligible
    if (isGrabCreditSelected && (
      eligibilityStatus === 'not_eligible' ||
      eligibilityStatus === 'new_user' ||
      eligibilityStatus === 'amount_exceeds_limit'
    )) {
      return 'Not eligible - Choose another method';
    }

    // If Pay Later is selected and user is approved
    if (isGrabCreditSelected && eligibilityStatus === 'approved') {
      return 'Continue with Pay Later';
    }

    // For all other payment methods
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
