import { useState } from 'react';
import CheckoutContainer from './components/CheckoutContainer';
import OrderSummary from './components/OrderSummary';
import PaymentMethods from './components/PaymentMethods';
import BNPLWidget from './components/BNPLWidget';
import FooterBar from './components/FooterBar';
import { useBNPLState } from './hooks/useBNPLState';
import { userPersonas } from './data/mockData';

function App() {
  // Persona management
  const [currentPersona, setCurrentPersona] = useState('regularUser');
  const activePersona = userPersonas[currentPersona];

  // State management
  const {
    selectedPayment,
    setSelectedPayment,
    selectedEMI,
    setSelectedEMI,
    showQualificationReason,
    setShowQualificationReason,
    isGrabCreditSelected,
    canProceed,
    finalAmount,
    ctaText,
  } = useBNPLState(activePersona.status, activePersona.emiOptions);

  // Demo: Persona switcher for testing (remove in production)
  const [showPersonaSwitcher, setShowPersonaSwitcher] = useState(true);

  // Handle persona change
  const handlePersonaChange = (personaKey) => {
    setCurrentPersona(personaKey);
    setSelectedEMI(null); // Reset EMI selection when switching personas
  };

  // Persona icons based on status
  const getPersonaIcon = (status) => {
    switch (status) {
      case 'approved':
        return '✅';
      case 'not_eligible':
        return '❌';
      case 'new_user':
        return '👤';
      default:
        return '⭐';
    }
  };

  // Persona button styling
  const getPersonaButtonClass = (personaKey) => {
    const isActive = currentPersona === personaKey;
    const persona = userPersonas[personaKey];

    if (isActive) {
      if (persona.status === 'approved') return 'bg-success-100 text-success-800 border-success-300';
      if (persona.status === 'not_eligible') return 'bg-red-100 text-red-800 border-red-300';
      if (persona.status === 'new_user') return 'bg-amber-100 text-amber-800 border-amber-300';
    }

    return 'bg-gray-50 hover:bg-gray-100 text-gray-700 border-gray-200';
  };

  return (
    <>
      {/* Persona Switcher - For Demo Only */}
      {showPersonaSwitcher && (
        <div className="fixed top-4 right-4 z-50 bg-white rounded-lg shadow-xl border border-gray-200 p-4 max-w-sm">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h3 className="text-sm font-bold text-gray-900">User Personas</h3>
              <p className="text-xs text-gray-500">Switch between demo users</p>
            </div>
            <button
              onClick={() => setShowPersonaSwitcher(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="space-y-2">
            {Object.entries(userPersonas).map(([key, persona]) => (
              <button
                key={key}
                onClick={() => handlePersonaChange(key)}
                className={`w-full p-3 text-left rounded-lg border-2 transition-all ${getPersonaButtonClass(key)}`}
              >
                <div className="flex items-start gap-2">
                  <span className="text-lg">{getPersonaIcon(persona.status)}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-semibold truncate">{persona.name}</span>
                      {currentPersona === key && (
                        <svg className="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                      )}
                    </div>
                    <div className="text-xs opacity-75 mt-0.5">{persona.type}</div>
                    <div className="text-xs opacity-60 mt-1">
                      {persona.transactionHistory.totalPurchases} purchases
                      {persona.status === 'approved' && ` • ₹${persona.creditLimit.toLocaleString('en-IN')} limit`}
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>

          {/* Current Persona Info */}
          <div className="mt-3 pt-3 border-t border-gray-200">
            <div className="text-xs text-gray-500 space-y-1">
              <div className="flex justify-between">
                <span>Status:</span>
                <span className="font-medium text-gray-700 capitalize">{activePersona.status.replace('_', ' ')}</span>
              </div>
              {activePersona.status === 'approved' && (
                <>
                  <div className="flex justify-between">
                    <span>Credit Limit:</span>
                    <span className="font-medium text-gray-700">₹{activePersona.creditLimit.toLocaleString('en-IN')}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>EMI Options:</span>
                    <span className="font-medium text-gray-700">{activePersona.emiOptions?.length || 0}</span>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Main Checkout UI */}
      <CheckoutContainer>
        {/* Order Summary */}
        <OrderSummary />

        {/* Payment Methods */}
        <PaymentMethods
          selectedPayment={selectedPayment}
          onPaymentSelect={setSelectedPayment}
        />

        {/* BNPL Widget */}
        <BNPLWidget
          isExpanded={isGrabCreditSelected}
          selectedEMI={selectedEMI}
          onEMISelect={setSelectedEMI}
          userPersona={activePersona}
          showQualificationReason={showQualificationReason}
          onToggleQualification={() => setShowQualificationReason(!showQualificationReason)}
        />

        {/* Footer Bar */}
        <FooterBar
          selectedEMI={selectedEMI}
          ctaText={ctaText}
          canProceed={canProceed}
          isGrabCreditSelected={isGrabCreditSelected}
          emiOptions={activePersona.emiOptions}
        />
      </CheckoutContainer>

      {/* Toggle Demo Controls Button (when hidden) */}
      {!showPersonaSwitcher && (
        <button
          onClick={() => setShowPersonaSwitcher(true)}
          className="fixed bottom-4 right-4 z-50 bg-gray-900 text-white px-4 py-2 rounded-full shadow-lg hover:bg-gray-800 transition-colors text-sm font-medium"
        >
          Show Personas
        </button>
      )}
    </>
  );
}

export default App;
