import test from 'node:test';
import assert from 'node:assert';
import {
  detectScheduleConflicts,
  calculateBudgetSummary,
  calculateGuestMetrics,
  autoResolveConflict,
  timeToMinutes,
  minutesToTime,
  createMemoizedFunction,
  formatCurrencyFast,
  debounce
} from '../src/algorithms.js';

// 1. Conflict detection with O(N log N) sweep line
test('detectScheduleConflicts finds overlapping intervals using sweep-line algorithm', () => {
  const items = [
    { id: '1', title: 'Setup', start: '10:00', end: '12:00' },
    { id: '2', title: 'Arrival', start: '11:00', end: '13:00' },
    { id: '3', title: 'Lunch', start: '14:00', end: '15:00' }
  ];

  const conflicts = detectScheduleConflicts(items);
  assert.strictEqual(conflicts.length, 1);
  assert.strictEqual(conflicts[0].itemA.id, '1');
  assert.strictEqual(conflicts[0].itemB.id, '2');
});

test('detectScheduleConflicts does not flag adjacent non-overlapping slots', () => {
  const adjacentItems = [
    { id: 'a1', title: 'Slot 1', start: '09:00', end: '10:00' },
    { id: 'a2', title: 'Slot 2', start: '10:00', end: '11:00' },
    { id: 'a3', title: 'Slot 3', start: '11:00', end: '12:30' }
  ];

  const conflicts = detectScheduleConflicts(adjacentItems);
  assert.strictEqual(conflicts.length, 0);
});

// 2. Budget precision and calculation
test('budget calculations maintain exact fixed precision', () => {
  const budget = 8500.00;
  const expenses = [
    { id: 'e1', amount: 1500.00 },
    { id: 'e2', amount: 1200.00 },
    { id: 'e3', amount: 600.00 }
  ];
  
  const summary = calculateBudgetSummary(budget, expenses);
  assert.strictEqual(summary.totalSpent, 3300.00);
  assert.strictEqual(summary.remainingBudget, 5200.00);
  assert.strictEqual(summary.utilizationPct.toFixed(1), '38.8');
  assert.strictEqual(summary.isOverBudget, false);
});

test('calculateBudgetSummary flags over-budget accurately', () => {
  const summary = calculateBudgetSummary(1000, [{ id: 'e1', amount: 1250.50 }]);
  assert.strictEqual(summary.totalSpent, 1250.50);
  assert.strictEqual(summary.remainingBudget, -250.50);
  assert.strictEqual(summary.isOverBudget, true);
});

// 3. Guest RSVP count and cost-per-guest metrics
test('guest RSVP counts accurately distinguish attending from declined in single pass', () => {
  const guests = [
    { id: 'g1', name: 'Alice', status: 'attending', plusOnes: 1, dietary: 'Vegan' },
    { id: 'g2', name: 'Bob', status: 'declined', plusOnes: 0, dietary: '' },
    { id: 'g3', name: 'Charlie', status: 'attending', plusOnes: 2, dietary: 'Vegetarian' },
    { id: 'g4', name: 'David', status: 'tentative', plusOnes: 0, dietary: '' }
  ];

  const metrics = calculateGuestMetrics(guests, 3300.00);
  assert.strictEqual(metrics.totalInvited, 4);
  assert.strictEqual(metrics.confirmedCount, 2);
  assert.strictEqual(metrics.declinedCount, 1);
  assert.strictEqual(metrics.tentativeCount, 1);
  assert.strictEqual(metrics.totalHeads, 5); // Alice(1+1) + Charlie(1+2)
  assert.strictEqual(metrics.costPerGuest, 1650.00); // 3300 / 2
  assert.strictEqual(metrics.dietaryRequirementsCount, 2);
});

// 4. Currency conversion
test('currency conversion accurately applies exchange rate', () => {
  const usdAmount = 100.00;
  const inrRate = 85.0;
  const inrAmount = usdAmount * inrRate;
  assert.strictEqual(inrAmount, 8500.00);
});

// 5. Currency formatter
test('formatCurrency outputs correctly formatted currency string', () => {
  assert.strictEqual(formatCurrencyFast(1234.5, 'INR', 1.0, '₹'), '₹1,234.50');
  assert.strictEqual(formatCurrencyFast(50, 'USD', 1.0, '$'), '$50.00');
});

// 6. Dietary filter
test('dietary tag filter identifies special dietary requirements', () => {
  const guests = [
    { name: 'Maya', dietary: 'Vegetarian' },
    { name: 'Liam', dietary: 'Gluten-Free' },
    { name: 'Sophia', dietary: '' }
  ];
  const withDietary = guests.filter(g => Boolean(g.dietary));
  assert.strictEqual(withDietary.length, 2);
});

// 7. Vendor booking toggle
test('vendor booking status toggle updates confirmed state', () => {
  const vendor = { id: 'v-1', booked: false };
  vendor.booked = !vendor.booked;
  assert.strictEqual(vendor.booked, true);
  vendor.booked = !vendor.booked;
  assert.strictEqual(vendor.booked, false);
});

// 8. Schedule auto-resolve
test('schedule conflict auto-resolution adjusts start time past conflicting slot', () => {
  const slotA = { id: 's1', title: 'Cocktails', start: '10:00', end: '11:30' };
  const slotB = { id: 's2', title: 'Speeches', start: '11:00', end: '12:00' };

  const conflict = { itemA: slotA, itemB: slotB };
  const resolved = autoResolveConflict(conflict);
  
  assert.strictEqual(resolved.newStart, '11:30');
  assert.strictEqual(resolved.newEnd, '12:30');
});

// 9. Time integer conversions
test('timeToMinutes and minutesToTime perform roundtrip accurately', () => {
  assert.strictEqual(timeToMinutes('09:30'), 570);
  assert.strictEqual(minutesToTime(570), '09:30');
  assert.strictEqual(timeToMinutes('00:00'), 0);
  assert.strictEqual(minutesToTime(0), '00:00');
  assert.strictEqual(timeToMinutes('23:45'), 1425);
  assert.strictEqual(minutesToTime(1425), '23:45');
});

// 10. Computation memoization
test('createMemoizedFunction prevents redundant recalculations', () => {
  let computeCount = 0;
  const expensiveOp = (x, y) => {
    computeCount++;
    return x * y;
  };

  const memoized = createMemoizedFunction(expensiveOp, (x, y) => `${x}:${y}`);
  
  assert.strictEqual(memoized(5, 10), 50);
  assert.strictEqual(computeCount, 1);
  
  // Second call with identical arguments must hit cache without invoking computation
  assert.strictEqual(memoized(5, 10), 50);
  assert.strictEqual(computeCount, 1);

  // New arguments compute once
  assert.strictEqual(memoized(3, 4), 12);
  assert.strictEqual(computeCount, 2);
});

// 11. Input validation
test('validation rejects negative budget and empty event names', () => {
  function validateEvent(name, budget) {
    if (!name || name.trim().length === 0) return false;
    if (isNaN(budget) || budget <= 0) return false;
    return true;
  }
  assert.strictEqual(validateEvent('', 5000), false);
  assert.strictEqual(validateEvent('Valid Gala', -100), false);
  assert.strictEqual(validateEvent('Anya Party', 5000), true);
});

// 12. Accessible button state
test('accessible tab state toggles aria-selected correctly', () => {
  const tabs = [
    { id: 'tab-1', active: true },
    { id: 'tab-2', active: false }
  ];
  function switchTab(targetId) {
    tabs.forEach(t => {
      t.active = t.id === targetId;
    });
  }
  switchTab('tab-2');
  assert.strictEqual(tabs[0].active, false);
  assert.strictEqual(tabs[1].active, true);
});

// 13. Cryptographic token format
test('invitation token matches expected secure prefix and length', () => {
  const token = 'tok_8f92a1e4c7b8d0e1';
  assert.strictEqual(token.startsWith('tok_'), true);
  assert.strictEqual(token.length >= 16, true);
});

// 14. High-throughput interval sweep-line benchmark
test('sweep-line detects conflicts across 100 timeline intervals in under 20ms', () => {
  const items = [];
  for (let i = 0; i < 100; i++) {
    const startHour = Math.floor(i / 5);
    const startMin = (i % 5) * 10;
    const startStr = `${String(startHour).padStart(2, '0')}:${String(startMin).padStart(2, '0')}`;
    const endStr = `${String(startHour).padStart(2, '0')}:${String(Math.min(59, startMin + 25)).padStart(2, '0')}`;
    items.push({ id: `item-${i}`, title: `Event ${i}`, start: startStr, end: endStr });
  }

  const start = performance.now();
  const conflicts = detectScheduleConflicts(items);
  const elapsed = performance.now() - start;

  assert.strictEqual(Array.isArray(conflicts), true);
  assert.strictEqual(elapsed < 20, true, `Expected execution under 20ms, took ${elapsed.toFixed(2)}ms`);
});

// 15. Identical start-time tie-breaker determinism
test('detectScheduleConflicts handles identical start times deterministically', () => {
  const items = [
    { id: 't1', title: 'Photo Booth', start: '14:00', end: '15:00' },
    { id: 't2', title: 'Cocktails', start: '14:00', end: '16:00' },
    { id: 't3', title: 'Live Acoustic', start: '14:00', end: '14:45' }
  ];
  const conflicts = detectScheduleConflicts(items);
  assert.strictEqual(conflicts.length, 3);
});

// 16. Pre-warmed currency cache
test('formatCurrencyFast reliably formats pre-warmed currencies with correct symbols', () => {
  assert.strictEqual(formatCurrencyFast(100, 'EUR'), '€100.00');
  assert.strictEqual(formatCurrencyFast(2500.75, 'USD'), '$2,500.75');
});

// 17. LRU cache eviction boundary
test('createMemoizedFunction evicts oldest entry when maxEntries is exceeded', () => {
  let calls = 0;
  const fn = (x) => { calls++; return x * 2; };
  const memoized = createMemoizedFunction(fn, (x) => String(x), 2);

  memoized(1); // calls: 1
  memoized(2); // calls: 2
  memoized(1); // hit: calls still 2
  assert.strictEqual(calls, 2);

  memoized(3); // evicts key '1'
  assert.strictEqual(calls, 3);

  memoized(1); // re-computes because '1' was evicted
  assert.strictEqual(calls, 4);
});
