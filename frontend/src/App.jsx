import { useState, useEffect } from 'react';
import CheckoutContainer from './components/CheckoutContainer';
import OrderSummary from './components/OrderSummary';
import PaymentMethods from './components/PaymentMethods';
import BNPLWidget from './components/BNPLWidget';
import FooterBar from './components/FooterBar';
import Toast from './components/Toast';
import LoadingSkeleton from './components/LoadingSkeleton';
import { useBNPLState } from './hooks/useBNPLState';
import { useEligibilityCheck } from './hooks/useEligibilityCheck';
import { userPersonas, orderData } from './data/mockData';
import { testConnection } from './services/api';

function App() {
  // API mode toggle - Default to Real API mode for production
  const [useRealAPI, setUseRealAPI] = useState(true);
  const [backendConnected, setBackendConnected] = useState(false);

  // Persona management
  const [currentPersona, setCurrentPersona] = useState('regularUser');

  // Toast notifications
  const [toast, setToast] = useState(null);

  // Use eligibility check hook
  const {
    eligibilityData,
    isLoading,
    error: apiError,
    checkUserEligibility
  } = useEligibilityCheck(orderData.product.title, orderData.pricing.total);

  // Active persona (from API or mock) - Always fallback to mock data to prevent crashes
  const activePersona = (useRealAPI && eligibilityData)
    ? eligibilityData
    : userPersonas[currentPersona] || userPersonas.regularUser;

  // State management - Add safety checks
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
  } = useBNPLState(activePersona?.status || 'approved', activePersona?.emiOptions || []);

  // Feature flag for persona switcher (for demo/testing only)
  const SHOW_PERSONA_SWITCHER = import.meta.env.VITE_SHOW_PERSONA_SWITCHER === 'true';
  const [showPersonaSwitcher, setShowPersonaSwitcher] = useState(SHOW_PERSONA_SWITCHER);

  // Check backend connectivity on mount and fetch initial eligibility
  useEffect(() => {
    const checkBackend = async () => {
      const connected = await testConnection();
      setBackendConnected(connected);
      if (connected) {
        setToast({
          type: 'success',
          message: 'Backend connected successfully'
        });
        // Fetch eligibility for default persona if Real API is enabled
        if (useRealAPI) {
          const userId = userIdMap[currentPersona];
          if (userId) {
            await checkUserEligibility(userId);
          }
        }
      }
    };
    checkBackend();
  }, []);

  // Handle API error changes
  useEffect(() => {
    if (apiError) {
      setToast({
        type: 'error',
        message: `API Error: ${apiError}`
      });
    }
  }, [apiError]);

  // User ID mapping
  const userIdMap = {
    'newUser': 'USR_RAJESH',
    'riskyUser': 'USR_PRIYA',
    'growingUser': 'USR_AMIT',
    'regularUser': 'USR_SNEHA',
    'powerUser': 'USR_VIKRAM'
  };

  // Handle persona change
  const handlePersonaChange = async (personaKey) => {
    setCurrentPersona(personaKey);
    setSelectedEMI(null);

    if (useRealAPI && backendConnected) {
      try {
        await checkUserEligibility(userIdMap[personaKey]);
        setToast({
          type: 'success',
          message: `Loaded eligibility for ${userPersonas[personaKey].name}`
        });
      } catch (error) {
        console.error('Failed to fetch eligibility:', error);
      }
    }
  };

  // Toggle API mode
  const handleToggleAPIMode = async () => {
    const newMode = !useRealAPI;

    if (newMode && backendConnected) {
      // Switch mode immediately to show loading state
      setUseRealAPI(newMode);
      setToast({
        type: 'success',
        message: 'Switched to Real API Mode - Loading data...'
      });
      // Fetch current persona data
      try {
        await checkUserEligibility(userIdMap[currentPersona]);
        setToast({
          type: 'success',
          message: 'Real API data loaded successfully'
        });
      } catch (error) {
        console.error('Failed to fetch eligibility:', error);
        setToast({
          type: 'error',
          message: 'Failed to load API data. Please try again.'
        });
        // Switch back to mock mode on error
        setUseRealAPI(false);
      }
    } else {
      // Switching to mock mode - safe to do immediately
      setUseRealAPI(newMode);
      setToast({
        type: 'success',
        message: 'Switched to Mock Data Mode'
      });
    }
  };

  // Persona status indicators based on status
  const getPersonaIcon = (status) => {
    switch (status) {
      case 'approved':
        return '[APPROVED]';
      case 'not_eligible':
        return '[REJECTED]';
      case 'new_user':
        return '[NEW]';
      default:
        return '[VIP]';
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
      {/* Toast Notifications */}
      {toast && (
        <Toast
          type={toast.type}
          message={toast.message}
          onClose={() => setToast(null)}
        />
      )}

      {/* Persona Switcher - For Demo Only */}
      {SHOW_PERSONA_SWITCHER && showPersonaSwitcher && (
        <div className="fixed top-4 right-4 z-50 bg-white rounded-lg shadow-xl border border-gray-200 p-4 max-w-sm max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h3 className="text-sm font-bold text-gray-900">User Personas</h3>
              <p className="text-xs text-gray-500">
                {useRealAPI ? '[LIVE] Real API Mode' : '[DEMO] Mock Data Mode'}
              </p>
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

          {/* API Mode Toggle */}
          <div className="mb-3 p-2 bg-gray-50 rounded-lg">
            <label className="flex items-center justify-between">
              <span className="text-xs font-medium text-gray-700">
                Use Real API {backendConnected ? '[ON]' : '[OFF]'}
              </span>
              <button
                onClick={handleToggleAPIMode}
                disabled={!backendConnected}
                className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
                  useRealAPI ? 'bg-grabcredit-600' : 'bg-gray-300'
                } ${!backendConnected ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <span
                  className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${
                    useRealAPI ? 'translate-x-5' : 'translate-x-1'
                  }`}
                />
              </button>
            </label>
            {!backendConnected && (
              <p className="text-xs text-red-600 mt-1">
                [WARNING] Backend not running. Start: python backend/run.py
              </p>
            )}
          </div>

          {/* Loading State */}
          {isLoading && (
            <div className="mb-3 p-2 bg-blue-50 border border-blue-200 rounded text-xs text-blue-700 text-center">
              <div className="animate-pulse">Loading eligibility...</div>
            </div>
          )}

          {/* Persona Buttons */}
          <div className="space-y-2">
            {Object.entries(userPersonas).map(([key, persona]) => {
              // Show real API data if available and in API mode, otherwise show mock data
              const displayData = (useRealAPI && currentPersona === key && eligibilityData)
                ? eligibilityData
                : persona;

              return (
                <button
                  key={key}
                  onClick={() => handlePersonaChange(key)}
                  disabled={isLoading}
                  className={`w-full p-3 text-left rounded-lg border-2 transition-all ${getPersonaButtonClass(key)} ${
                    isLoading ? 'opacity-50 cursor-not-allowed' : ''
                  }`}
                >
                  <div className="flex items-start gap-2">
                    <span className="text-xs font-mono font-bold">{getPersonaIcon(displayData.status)}</span>
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
                        {(displayData.transactionHistory?.total_purchases || displayData.transactionHistory?.totalPurchases || 0)} purchases
                        {displayData.status === 'approved' && ` | Limit: Rs.${(displayData.creditLimit || displayData.credit_limit || 0).toLocaleString('en-IN')}`}
                      </div>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>

          {/* Current Persona Info */}
          {activePersona && (
            <div className="mt-3 pt-3 border-t border-gray-200">
              <div className="text-xs text-gray-500 space-y-1">
                <div className="flex justify-between">
                  <span>Status:</span>
                  <span className="font-medium text-gray-700 capitalize">
                    {(activePersona.status || 'unknown').replace('_', ' ')}
                  </span>
                </div>
                {activePersona.status === 'approved' && (
                  <>
                    <div className="flex justify-between">
                      <span>Credit Limit:</span>
                      <span className="font-medium text-gray-700">
                        ₹{(activePersona.creditLimit || 0).toLocaleString('en-IN')}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>EMI Options:</span>
                      <span className="font-medium text-gray-700">{activePersona.emiOptions?.length || 0}</span>
                    </div>
                  </>
                )}
              </div>
            </div>
          )}
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
          eligibilityStatus={activePersona?.status}
        />

        {/* BNPL Widget with Loading State */}
        {isLoading && isGrabCreditSelected ? (
          <LoadingSkeleton variant="bnpl" />
        ) : activePersona ? (
          <BNPLWidget
            isExpanded={isGrabCreditSelected}
            selectedEMI={selectedEMI}
            onEMISelect={setSelectedEMI}
            userPersona={activePersona}
            showQualificationReason={showQualificationReason}
            onToggleQualification={() => setShowQualificationReason(!showQualificationReason)}
          />
        ) : null}

        {/* Footer Bar */}
        {activePersona && (
          <FooterBar
            selectedEMI={selectedEMI}
            ctaText={ctaText}
            canProceed={canProceed && !isLoading}
            isGrabCreditSelected={isGrabCreditSelected}
            emiOptions={activePersona.emiOptions || []}
            isLoading={isLoading}
          />
        )}
      </CheckoutContainer>

      {/* Toggle Demo Controls Button (when hidden) */}
      {SHOW_PERSONA_SWITCHER && !showPersonaSwitcher && (
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
