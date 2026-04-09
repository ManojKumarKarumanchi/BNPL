import { useState, useEffect } from 'react';
import CheckoutContainer from './components/CheckoutContainer';
import OrderSummary from './components/OrderSummary';
import PaymentMethods from './components/PaymentMethods';
import BNPLWidget from './components/BNPLWidget';
import FooterBar from './components/FooterBar';
import { useBNPLState } from './hooks/useBNPLState';
import { userPersonas, orderData } from './data/mockData';
import { checkEligibility, testConnection } from './services/api';

function App() {
  // Persona management
  const [currentPersona, setCurrentPersona] = useState('regularUser');
  const [useRealAPI, setUseRealAPI] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState(null);
  const [backendConnected, setBackendConnected] = useState(false);

  // Active persona (either from mock data or API response)
  const [activePersona, setActivePersona] = useState(userPersonas[currentPersona]);

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

  // Demo: Persona switcher for testing
  const [showPersonaSwitcher, setShowPersonaSwitcher] = useState(true);
  const [lastFetchedUserId, setLastFetchedUserId] = useState(null);

  // Check backend connectivity on mount
  useEffect(() => {
    testConnection()
      .then(connected => setBackendConnected(connected))
      .catch(() => setBackendConnected(false));
  }, []);

  // Handle persona change (mock data mode)
  const handlePersonaChange = (personaKey) => {
    setCurrentPersona(personaKey);
    setActivePersona(userPersonas[personaKey]);
    setSelectedEMI(null);
    setApiError(null);
  };

  // Fetch real data from API
  const handleFetchFromAPI = async (userId) => {
    // Prevent duplicate requests
    if (isLoading || lastFetchedUserId === userId) {
      return;
    }

    setIsLoading(true);
    setApiError(null);
    setLastFetchedUserId(userId);

    try {
      const result = await checkEligibility(
        userId,
        orderData.product.title,
        orderData.pricing.total
      );

      // Update active persona with API data
      setActivePersona(result);
      setCurrentPersona(userId);
      setSelectedEMI(null);

      console.log('✅ API Response:', result);

    } catch (error) {
      setApiError(error.message);
      console.error('❌ API Error:', error);
      // Fallback to mock data on error if not using API mode
      if (!useRealAPI) {
        setActivePersona(userPersonas[currentPersona]);
      }
    } finally {
      setIsLoading(false);
    }
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
              <p className="text-xs text-gray-500">
                {useRealAPI ? 'Real API Mode' : 'Mock Data Mode'}
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
                Use Real API {backendConnected ? '🟢' : '🔴'}
              </span>
              <button
                onClick={() => setUseRealAPI(!useRealAPI)}
                className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
                  useRealAPI ? 'bg-grabcredit-600' : 'bg-gray-300'
                }`}
              >
                <span
                  className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${
                    useRealAPI ? 'translate-x-5' : 'translate-x-1'
                  }`}
                />
              </button>
            </label>
            {!backendConnected && useRealAPI && (
              <p className="text-xs text-red-600 mt-1">
                ⚠️ Backend not running. Start: python backend/api/main.py
              </p>
            )}
          </div>

          {/* API Error Display */}
          {apiError && (
            <div className="mb-3 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
              Error: {apiError}
            </div>
          )}

          {/* Persona Buttons */}
          <div className="space-y-2">
            {Object.entries(userPersonas).map(([key, persona]) => (
              <button
                key={key}
                onClick={() => {
                  if (useRealAPI) {
                    // Map persona keys to user IDs
                    const userIdMap = {
                      'newUser': 'USR_RAJESH',
                      'riskyUser': 'USR_PRIYA',
                      'growingUser': 'USR_AMIT',
                      'regularUser': 'USR_SNEHA',
                      'powerUser': 'USR_VIKRAM'
                    };
                    handleFetchFromAPI(userIdMap[key]);
                  } else {
                    handlePersonaChange(key);
                  }
                }}
                disabled={isLoading || (useRealAPI && !backendConnected)}
                className={`w-full px-3 py-2 text-left text-xs rounded-lg border transition-colors ${getPersonaButtonClass(key)} ${
                  isLoading ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span>{getPersonaIcon(persona.status)}</span>
                    <div>
                      <div className="font-semibold">{persona.name}</div>
                      <div className="text-gray-500">{persona.type}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold">₹{persona.creditLimit.toLocaleString()}</div>
                    <div className="text-gray-500">{persona.transactionHistory.totalPurchases} txns</div>
                  </div>
                </div>
              </button>
            ))}
          </div>

          {isLoading && (
            <div className="mt-3 text-center text-xs text-gray-600">
              <div className="animate-pulse">Loading from API...</div>
            </div>
          )}
        </div>
      )}

      {/* Toggle Persona Switcher */}
      {!showPersonaSwitcher && (
        <button
          onClick={() => setShowPersonaSwitcher(true)}
          className="fixed top-4 right-4 z-50 bg-grabcredit-600 text-white px-4 py-2 rounded-lg shadow-lg hover:bg-grabcredit-700 transition-colors text-sm font-medium"
        >
          Show Personas
        </button>
      )}

      {/* Main Checkout UI */}
      <CheckoutContainer>
        <OrderSummary />

        <PaymentMethods
          selectedPayment={selectedPayment}
          onPaymentChange={setSelectedPayment}
        />

        {isGrabCreditSelected && (
          <BNPLWidget
            userPersona={activePersona}
            selectedEMI={selectedEMI}
            onEMISelect={setSelectedEMI}
            showQualificationReason={showQualificationReason}
            onToggleQualification={() => setShowQualificationReason(!showQualificationReason)}
          />
        )}

        <FooterBar
          isGrabCreditSelected={isGrabCreditSelected}
          canProceed={canProceed}
          finalAmount={finalAmount}
          ctaText={ctaText}
        />
      </CheckoutContainer>
    </>
  );
}

export default App;
