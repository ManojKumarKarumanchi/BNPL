import { useState, useCallback, useEffect } from 'react';
import { checkEligibility } from '../services/api';

/**
 * Custom hook for real-time BNPL eligibility checking
 * Handles loading states, caching, and error recovery
 */
export const useEligibilityCheck = (productId, amount) => {
  const [eligibilityData, setEligibilityData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [cache, setCache] = useState(new Map());

  // Check eligibility with caching and deduplication
  const checkUserEligibility = useCallback(async (userId) => {
    // Return cached result if available
    const cacheKey = `${userId}-${productId}-${amount}`;
    if (cache.has(cacheKey)) {
      const cached = cache.get(cacheKey);
      setEligibilityData(cached);
      return cached;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await checkEligibility(userId, productId, amount);

      // Cache the result
      setCache(prev => new Map(prev).set(cacheKey, result));
      setEligibilityData(result);

      return result;
    } catch (err) {
      setError(err.message || 'Failed to check eligibility');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [productId, amount, cache]);

  // Clear cache when amount changes
  useEffect(() => {
    setCache(new Map());
  }, [amount]);

  // Clear error after 5 seconds
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  return {
    eligibilityData,
    isLoading,
    error,
    checkUserEligibility,
    clearCache: () => setCache(new Map())
  };
};
