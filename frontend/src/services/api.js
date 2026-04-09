/**
 * GrabOn BNPL API Client
 * Connects React frontend to FastAPI backend.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Check BNPL eligibility for a user.
 *
 * @param {string} userId - User ID (e.g., "USR_SNEHA")
 * @param {string} productId - Product ID
 * @param {number} amount - Purchase amount
 * @returns {Promise<Object>} Eligibility response
 */
export async function checkEligibility(userId, productId, amount) {
  // Create AbortController for 30 second timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000);

  try {
    const response = await fetch(`${API_BASE_URL}/api/checkout/eligibility`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        product_id: productId,
        amount: amount
      }),
      signal: controller.signal  // Add timeout signal
    });

    clearTimeout(timeoutId);  // Clear timeout on success

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    // Transform API response to match frontend persona structure
    return {
      name: userId.replace('USR_', '').replace('_', ' '),  // "USR_SNEHA" -> "SNEHA"
      type: mapStatusToType(data.status),
      status: data.status,
      creditLimit: data.credit_limit,
      reason: data.reason,
      transactionHistory: {
        totalPurchases: data.transaction_history.total_purchases,
        avgOrderValue: data.transaction_history.avg_order_value,
        returnRate: data.transaction_history.return_rate,
        memberSince: data.transaction_history.member_since
      },
      emiOptions: data.emi_options || null
    };

  } catch (error) {
    clearTimeout(timeoutId);  // Clear timeout on error

    if (error.name === 'AbortError') {
      const timeoutError = new Error('Request timeout: Backend took longer than 30 seconds to respond');
      timeoutError.isTimeout = true;
      console.error('Eligibility check timeout:', timeoutError);
      throw timeoutError;
    }

    console.error('Eligibility check failed:', error);
    throw error;
  }
}

/**
 * Map API status to frontend persona type.
 */
function mapStatusToType(status) {
  const statusMap = {
    'new_user': 'New User',
    'not_eligible': 'Risky User',
    'approved': 'Regular User'  // Will be refined by credit_limit
  };
  return statusMap[status] || 'Unknown';
}

/**
 * Health check endpoint.
 *
 * @returns {Promise<Object>} Health status
 */
export async function checkHealth() {
  // Create AbortController for 5 second timeout (shorter for health checks)
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 5000);

  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);

    if (error.name === 'AbortError') {
      console.error('Health check timeout after 5 seconds');
      throw new Error('Health check timeout');
    }

    console.error('Health check failed:', error);
    throw error;
  }
}

/**
 * Test API connectivity.
 * Call this on app startup to verify backend is reachable.
 */
export async function testConnection() {
  try {
    const health = await checkHealth();
    console.log('✅ Backend connected:', health);
    return true;
  } catch (error) {
    console.error('❌ Backend not reachable:', error);
    return false;
  }
}
