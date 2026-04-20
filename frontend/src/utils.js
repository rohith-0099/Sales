/**
 * Frontend utilities for common operations and optimizations
 */

const REQUEST_TIMEOUT = 30000; // 30 seconds

/**
 * Fetch with timeout support
 */
export async function fetchWithTimeout(url, options = {}, timeoutMs = REQUEST_TIMEOUT) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * Safely parse error messages from API responses
 */
export function getAPIErrorMessage(error, defaultMessage = "An error occurred") {
  if (error?.response?.data?.error) {
    return error.response.data.error;
  }
  if (error?.message) {
    return error.message;
  }
  if (typeof error === "string") {
    return error;
  }
  return defaultMessage;
}

/**
 * Debounce function calls
 */
export function debounce(func, delayMs = 250) {
  let timeoutId;
  return function debounced(...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delayMs);
  };
}

/**
 * Memoize function results based on arguments
 */
export function memoize(func) {
  const cache = new Map();

  return function memoized(...args) {
    const key = JSON.stringify(args);
    if (cache.has(key)) {
      return cache.get(key);
    }

    const result = func(...args);
    cache.set(key, result);
    return result;
  };
}

/**
 * Format large numbers with abbreviations
 */
export function formatNumberShort(value) {
  const num = Number(value ?? 0);
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`;
  }
  if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`;
  }
  return num.toFixed(0);
}

/**
 * Create cancelled promise for cleanup
 */
export function createCancellablePromise() {
  let resolve, reject;
  let cancelled = false;

  const promise = new Promise((res, rej) => {
    resolve = res;
    reject = rej;
  });

  return {
    promise,
    cancel: () => {
      cancelled = true;
      reject(new Error("Operation cancelled"));
    },
    isCancelled: () => cancelled,
    resolve,
    reject,
  };
}
