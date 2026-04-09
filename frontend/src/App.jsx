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
import { testConnection, pollBackendConnection } from './services/api';

function App() {
  // Backend connection state
  const [backendConnected, setBackendConnected] = useState(false);

  // Persona management (user IDs for API calls)
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

  // Active persona - ONLY from real-time API (no mock fallback)
  const activePersona = eligibilityData;

  // State management - Only works when we have real API data
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
  } = useBNPLState(
    eligibilityData?.status || 'loading',
    eligibilityData?.emiOptions || []
  );

  // Feature flag for persona switcher (for demo/testing only)
  const SHOW_PERSONA_SWITCHER = import.meta.env.VITE_SHOW_PERSONA_SWITCHER === 'true';
  const [showPersonaSwitcher, setShowPersonaSwitcher] = useState(SHOW_PERSONA_SWITCHER);

  // Check backend connectivity on mount with retry and start polling
  useEffect(() => {
    const checkBackend = async () => {
      // Try to connect with 3 retries, 2 seconds between each
      const connected = await testConnection(3, 2000);
      setBackendConnected(connected);

      if (connected) {
        setToast({
          type: 'success',
          message: 'Backend connected successfully'
        });
        // Always fetch eligibility data for default persona
        const userId = userIdMap[currentPersona];
        if (userId) {
          await checkUserEligibility(userId);
        }
      } else {
        setToast({
          type: 'error',
          message: 'Backend not reachable. Waiting for connection... (retrying every 10s)'
        });
      }
    };

    // Initial connection check
    checkBackend();

    // Start polling for backend connection (checks every 10 seconds)
    const stopPolling = pollBackendConnection(
      // onConnect callback
      async () => {
        setBackendConnected(true);
        setToast({
          type: 'success',
          message: 'Backend reconnected! Fetching data...'
        });

        // Always auto-fetch data when backend comes online
        const userId = userIdMap[currentPersona];
        if (userId) {
          await checkUserEligibility(userId);
        }
      },
      // onDisconnect callback
      () => {
        setBackendConnected(false);
        setToast({
          type: 'error',
          message: 'Backend connection lost. Please check backend server...'
        });
      },
      10000 // Poll every 10 seconds
    );

    // Cleanup: stop polling when component unmounts
    return () => {
      stopPolling();
    };
  }, []); // Empty deps - only run on mount

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

  // Handle persona change - Always fetch from API if connected
  const handlePersonaChange = async (personaKey) => {
    setCurrentPersona(personaKey);
    setSelectedEMI(null);

    if (backendConnected) {
      try {
        await checkUserEligibility(userIdMap[personaKey]);
        setToast({
          type: 'success',
          message: `Loaded eligibility for user ${userIdMap[personaKey]}`
        });
      } catch (error) {
        console.error('Failed to fetch eligibility:', error);
        setToast({
          type: 'error',
          message: 'Failed to load user data. Please try again.'
        });
      }
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
                {backendConnected ? '[LIVE] Real-time Data' : '[OFFLINE] Waiting for backend...'}
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

          {/* Backend Status Indicator */}
          <div className="mb-3">
            {backendConnected ? (
              <div className="p-2 bg-green-50 border border-green-200 rounded-lg text-xs">
                <div className="flex items-center gap-2 text-green-800">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span className="font-semibold">Backend Connected</span>
                  <span className="text-green-600 text-xs">(Real-time API)</span>
                </div>
              </div>
            ) : (
              <div className="p-2 bg-red-50 border border-red-200 rounded-lg text-xs">
                <div className="flex items-center gap-2 text-red-800 mb-1">
                  <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span className="font-semibold">Connecting to backend...</span>
                </div>
                <p className="text-red-700 ml-6">
                  Start backend: <code className="bg-red-100 px-1 py-0.5 rounded text-xs font-mono">python backend/run.py</code>
                </p>
                <p className="text-red-600 ml-6 mt-1">
                  Auto-retrying every 10 seconds...
                </p>
              </div>
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
              // Show real API data only if available for current persona
              const displayData = (currentPersona === key && eligibilityData)
                ? eligibilityData
                : null; // No fallback to mock data

              const isCurrentPersona = currentPersona === key;
              const hasData = !!displayData;

              return (
                <button
                  key={key}
                  onClick={() => handlePersonaChange(key)}
                  disabled={isLoading || !backendConnected}
                  className={`w-full p-3 text-left rounded-lg border-2 transition-all ${getPersonaButtonClass(key)} ${
                    (isLoading || !backendConnected) ? 'opacity-50 cursor-not-allowed' : ''
                  }`}
                >
                  <div className="flex items-start gap-2">
                    <span className="text-xs font-mono font-bold">
                      {hasData ? getPersonaIcon(displayData.status) : '[?]'}
                    </span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-semibold truncate">{persona.name}</span>
                        {isCurrentPersona && (
                          <svg className="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                          </svg>
                        )}
                      </div>
                      <div className="text-xs opacity-75 mt-0.5">{persona.type}</div>
                      <div className="text-xs opacity-60 mt-1">
                        {hasData ? (
                          <>
                            {(displayData.transactionHistory?.total_purchases || displayData.transactionHistory?.totalPurchases || 0)} purchases
                            {displayData.status === 'approved' && ` | Limit: Rs.${(displayData.creditLimit || displayData.credit_limit || 0).toLocaleString('en-IN')}`}
                          </>
                        ) : (
                          <span className="text-gray-400 italic">Click to load data from API</span>
                        )}
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
        ) : !backendConnected ? (
          isGrabCreditSelected && (
            <div className="p-6 bg-amber-50 border border-amber-200 rounded-lg text-center">
              <svg className="w-12 h-12 mx-auto text-amber-500 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <h3 className="text-lg font-semibold text-amber-900 mb-2">Backend Not Connected</h3>
              <p className="text-amber-700 text-sm mb-3">
                Pay Later requires connection to the backend server to check eligibility.
              </p>
              <code className="block bg-amber-100 p-2 rounded text-sm text-amber-900 mb-3">
                python backend/run.py
              </code>
              <p className="text-amber-600 text-xs">
                The page will auto-connect when backend is ready.
              </p>
            </div>
          )
        ) : activePersona ? (
          <BNPLWidget
            isExpanded={isGrabCreditSelected}
            selectedEMI={selectedEMI}
            onEMISelect={setSelectedEMI}
            userPersona={activePersona}
            showQualificationReason={showQualificationReason}
            onToggleQualification={() => setShowQualificationReason(!showQualificationReason)}
          />
        ) : (
          isGrabCreditSelected && (
            <div className="p-6 bg-blue-50 border border-blue-200 rounded-lg text-center">
              <svg className="animate-spin w-8 h-8 mx-auto text-blue-500 mb-3" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <p className="text-blue-700 text-sm">Loading eligibility data from API...</p>
              <p className="text-blue-600 text-xs mt-2">Click a user persona above to load their data</p>
            </div>
          )
        )}

        {/* Footer Bar - Always show but adjust state based on data availability */}
        <FooterBar
          selectedEMI={selectedEMI}
          ctaText={activePersona ? ctaText : 'Connect to backend first'}
          canProceed={activePersona && backendConnected && canProceed && !isLoading}
          isGrabCreditSelected={isGrabCreditSelected}
          emiOptions={activePersona?.emiOptions || []}
          isLoading={isLoading || !backendConnected}
        />
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
