/**
 * Festora — High-Performance Computational & Algorithmic Engine
 * 
 * Provides memoized, O(N log N) interval overlap detection, fixed-precision financial
 * calculators, guest RSVP aggregators, debounced persistence, and DOM reconcilers.
 * Fully typed via JSDoc for strict static type checking without runtime overhead.
 */

/**
 * @typedef {Object} TimelineItem
 * @property {string} id
 * @property {string} title
 * @property {string} [location]
 * @property {string} start - HH:MM format
 * @property {string} end - HH:MM format
 */

/**
 * @typedef {Object} TimelineConflict
 * @property {TimelineItem} itemA
 * @property {TimelineItem} itemB
 */

/**
 * @typedef {Object} Expense
 * @property {string} id
 * @property {string} [category]
 * @property {string} [desc]
 * @property {number} amount
 * @property {boolean} [paid]
 */

/**
 * @typedef {Object} BudgetSummary
 * @property {number} totalBudget
 * @property {number} totalSpent
 * @property {number} remainingBudget
 * @property {number} utilizationPct
 * @property {boolean} isOverBudget
 * @property {boolean} isNearLimit
 */

/**
 * @typedef {Object} Guest
 * @property {string} id
 * @property {string} name
 * @property {string} [email]
 * @property {number} [plusOnes]
 * @property {string} [dietary]
 * @property {string} status - 'attending' | 'declined' | 'tentative'
 * @property {string} [token]
 */

/**
 * @typedef {Object} GuestMetrics
 * @property {number} totalInvited
 * @property {number} confirmedCount
 * @property {number} declinedCount
 * @property {number} tentativeCount
 * @property {number} totalHeads - Confirmed plus confirmed plusOnes
 * @property {number} costPerGuest
 * @property {number} dietaryRequirementsCount
 */

/**
 * Converts HH:MM string to integer minutes from midnight.
 * Fast O(1) integer arithmetic for schedule comparisons.
 * @param {string} timeStr - "HH:MM"
 * @returns {number}
 */
export function timeToMinutes(timeStr) {
  if (!timeStr || typeof timeStr !== 'string') return 0;
  const colonIdx = timeStr.indexOf(':');
  if (colonIdx === -1) return 0;
  const hours = parseInt(timeStr.slice(0, colonIdx), 10) || 0;
  const mins = parseInt(timeStr.slice(colonIdx + 1), 10) || 0;
  return hours * 60 + mins;
}

/**
 * Formats minutes from midnight back into "HH:MM".
 * @param {number} minutes
 * @returns {string}
 */
export function minutesToTime(minutes) {
  const bounded = Math.max(0, Math.min(24 * 60 - 1, Math.round(minutes)));
  const h = Math.floor(bounded / 60);
  const m = bounded % 60;
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
}

/**
 * LRU / Simple Key-Value Memoization Helper
 * @template T
 * @param {(...args: any[]) => T} fn
 * @param {(...args: any[]) => string} [keyResolver]
 * @param {number} [maxEntries=100]
 * @returns {(...args: any[]) => T}
 */
export function createMemoizedFunction(fn, keyResolver, maxEntries = 100) {
  /** @type {Map<string, T>} */
  const cache = new Map();
  return function memoized(...args) {
    const key = keyResolver ? keyResolver(...args) : JSON.stringify(args);
    if (cache.has(key)) {
      return /** @type {T} */ (cache.get(key));
    }
    const result = fn(...args);
    if (cache.size >= maxEntries) {
      const oldestKey = cache.keys().next().value;
      if (oldestKey !== undefined) cache.delete(oldestKey);
    }
    cache.set(key, result);
    return result;
  };
}

/**
 * Detects schedule conflicts between timeline items using an optimal O(N log N)
 * sweep-line interval algorithm with early-termination.
 * Avoids quadratic O(N^2) loops by breaking the inner scan as soon as next.start >= current.end.
 * 
 * @param {TimelineItem[]} timelineItems
 * @returns {TimelineConflict[]}
 */
export function detectScheduleConflicts(timelineItems) {
  if (!Array.isArray(timelineItems) || timelineItems.length < 2) {
    return [];
  }

  // Pre-map to items with cached numeric minute timestamps for O(1) interval math
  const itemsWithMinutes = timelineItems.map(item => ({
    raw: item,
    startMin: timeToMinutes(item.start),
    endMin: timeToMinutes(item.end)
  }));

  // Sort by start minute with secondary end minute tie-breaker for strict determinism: O(N log N)
  itemsWithMinutes.sort((a, b) => (a.startMin - b.startMin) || (a.endMin - b.endMin));

  /** @type {TimelineConflict[]} */
  const conflicts = [];
  const n = itemsWithMinutes.length;

  // Sweep line with immediate boundary termination
  for (let i = 0; i < n; i++) {
    const current = itemsWithMinutes[i];

    for (let j = i + 1; j < n; j++) {
      const next = itemsWithMinutes[j];

      // Since items are sorted by startMin:
      // If next.startMin >= current.endMin, then EVERY subsequent item k > j
      // will also have startMin >= current.endMin and CANNOT overlap current.
      // Early break drops best/average case to O(N log N).
      if (next.startMin >= current.endMin) {
        break;
      }

      // Check genuine open interval overlap
      if (next.startMin < current.endMin && current.startMin < next.endMin) {
        conflicts.push({
          itemA: current.raw,
          itemB: next.raw
        });
      }
    }
  }

  return conflicts;
}

/**
 * Computes complete budget financial metrics with fixed precision.
 * @param {number} totalBudget
 * @param {Expense[]} expenses
 * @returns {BudgetSummary}
 */
export function calculateBudgetSummary(totalBudget, expenses) {
  const safeBudget = typeof totalBudget === 'number' && !isNaN(totalBudget) ? totalBudget : 0;
  
  let totalSpent = 0;
  if (Array.isArray(expenses)) {
    for (let i = 0; i < expenses.length; i++) {
      const amt = expenses[i]?.amount;
      if (typeof amt === 'number' && !isNaN(amt)) {
        totalSpent += amt;
      }
    }
  }

  // Round to 2 decimal places to avoid standard IEEE-754 floating-point drift
  totalSpent = Math.round(totalSpent * 100) / 100;
  const remainingBudget = Math.round((safeBudget - totalSpent) * 100) / 100;
  const utilizationPct = safeBudget > 0 
    ? Math.round((totalSpent / safeBudget) * 1000) / 10 
    : 0;

  return {
    totalBudget: safeBudget,
    totalSpent,
    remainingBudget,
    utilizationPct,
    isOverBudget: totalSpent > safeBudget,
    isNearLimit: utilizationPct >= 90 && utilizationPct <= 100
  };
}

/**
 * Computes guest counts, attendance statistics, and cost-per-guest metrics.
 * Single O(N) pass for high performance on large guest lists.
 * 
 * @param {Guest[]} guests
 * @param {number} totalSpent
 * @returns {GuestMetrics}
 */
export function calculateGuestMetrics(guests, totalSpent) {
  if (!Array.isArray(guests) || guests.length === 0) {
    return {
      totalInvited: 0,
      confirmedCount: 0,
      declinedCount: 0,
      tentativeCount: 0,
      totalHeads: 0,
      costPerGuest: 0,
      dietaryRequirementsCount: 0
    };
  }

  let confirmed = 0;
  let declined = 0;
  let tentative = 0;
  let totalHeads = 0;
  let dietaryCount = 0;

  for (let i = 0; i < guests.length; i++) {
    const g = guests[i];
    const status = g.status?.toLowerCase();

    if (status === 'attending') {
      confirmed++;
      totalHeads += 1 + (Number(g.plusOnes) || 0);
    } else if (status === 'declined') {
      declined++;
    } else {
      tentative++;
    }

    if (g.dietary && g.dietary.trim().length > 0 && g.dietary.toLowerCase() !== 'none') {
      dietaryCount++;
    }
  }

  const safeSpent = typeof totalSpent === 'number' && !isNaN(totalSpent) ? totalSpent : 0;
  const costPerGuest = confirmed > 0 
    ? Math.round((safeSpent / confirmed) * 100) / 100 
    : 0;

  return {
    totalInvited: guests.length,
    confirmedCount: confirmed,
    declinedCount: declined,
    tentativeCount: tentative,
    totalHeads,
    costPerGuest,
    dietaryRequirementsCount: dietaryCount
  };
}

/**
 * High-performance Currency Formatter with pre-warmed Intl.NumberFormat instances.
 * @type {Map<string, Intl.NumberFormat>}
 */
const formatterCache = new Map();

// Pre-warm formatters for instant zero-allocation execution
['USD', 'INR', 'EUR', 'GBP', 'CAD', 'AUD'].forEach(curr => {
  try {
    formatterCache.set(curr, new Intl.NumberFormat(undefined, {
      style: 'currency',
      currency: curr,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }));
  } catch (_) {}
});

/**
 * @param {number} amount
 * @param {string} [currency='USD']
 * @param {number} [rate=1.0]
 * @param {string} [customSymbol]
 * @returns {string}
 */
export function formatCurrencyFast(amount, currency = 'USD', rate = 1.0, customSymbol) {
  const numericAmount = (Number(amount) || 0) * (rate || 1.0);

  if (customSymbol) {
    return `${customSymbol}${numericAmount.toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })}`;
  }

  let formatter = formatterCache.get(currency);
  if (!formatter) {
    try {
      formatter = new Intl.NumberFormat(undefined, {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      });
      formatterCache.set(currency, formatter);
    } catch {
      return `$${numericAmount.toFixed(2)}`;
    }
  }

  return formatter.format(numericAmount);
}

/**
 * Auto-resolves a schedule conflict by shifting the later event forward
 * past the conflicting time slot and extending its end time safely.
 * 
 * @param {TimelineConflict} conflict
 * @returns {{ newStart: string, newEnd: string }}
 */
export function autoResolveConflict(conflict) {
  const itemA = conflict.itemA;
  const itemB = conflict.itemB;

  const aEnd = timeToMinutes(itemA.end);
  const bStart = timeToMinutes(itemB.start);
  const bEnd = timeToMinutes(itemB.end);

  const durationB = Math.max(30, bEnd - bStart);
  
  // Shift item B's start to item A's end
  const resolvedStartMin = aEnd;
  const resolvedEndMin = Math.min(23 * 60 + 59, resolvedStartMin + durationB);

  return {
    newStart: minutesToTime(resolvedStartMin),
    newEnd: minutesToTime(resolvedEndMin)
  };
}

/**
 * Creates a high-performance debounced function.
 * Utilizes requestIdleCallback when available for storage I/O, preventing
 * frame drops and main thread jank.
 * 
 * @param {(...args: any[]) => any} fn
 * @param {number} delayMs
 * @returns {(...args: any[]) => void}
 */
export function debounce(fn, delayMs = 200) {
  /** @type {ReturnType<typeof setTimeout> | null} */
  let timeoutId = null;
  return function debounced(...args) {
    if (timeoutId !== null) {
      clearTimeout(timeoutId);
    }
    timeoutId = setTimeout(() => {
      timeoutId = null;
      if (typeof window !== 'undefined' && 'requestIdleCallback' in window) {
        // @ts-ignore
        window.requestIdleCallback(() => fn(...args));
      } else {
        fn(...args);
      }
    }, delayMs);
  };
}

/**
 * Reconciles element innerHTML only when the markup has actually changed.
 * Avoids expensive browser layout thrashing, DOM reconstruction, and repaints.
 * 
 * @param {HTMLElement|null} element
 * @param {string} newHTML
 * @returns {boolean} True if DOM was updated, false if skipped
 */
export function updateInnerHTMLIfChanged(element, newHTML) {
  if (!element) return false;
  if (element.innerHTML !== newHTML) {
    element.innerHTML = newHTML;
    return true;
  }
  return false;
}

/**
 * Reconciles element textContent only when the text has changed.
 * @param {HTMLElement|null} element
 * @param {string|number} newText
 * @returns {boolean}
 */
export function updateTextIfChanged(element, newText) {
  if (!element) return false;
  const str = String(newText);
  if (element.textContent !== str) {
    element.textContent = str;
    return true;
  }
  return false;
}
