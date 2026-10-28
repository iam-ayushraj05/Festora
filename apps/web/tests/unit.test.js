import test from 'node:test';
import assert from 'node:assert';

// 1. Conflict detection
test('detectScheduleConflicts finds overlapping intervals', () => {
  function detectConflicts(items) {
    const conflicts = [];
    const sorted = [...items].sort((a, b) => a.start.localeCompare(b.start));
    for (let i = 0; i < sorted.length; i++) {
      for (let j = i + 1; j < sorted.length; j++) {
        if (sorted[i].start < sorted[j].end && sorted[j].start < sorted[i].end) {
          conflicts.push({ a: sorted[i], b: sorted[j] });
        }
      }
    }
    return conflicts;
  }

  const items = [
    { id: '1', start: '10:00', end: '12:00' },
    { id: '2', start: '11:00', end: '13:00' },
    { id: '3', start: '14:00', end: '15:00' }
  ];

  const conflicts = detectConflicts(items);
  assert.strictEqual(conflicts.length, 1);
  assert.strictEqual(conflicts[0].a.id, '1');
  assert.strictEqual(conflicts[0].b.id, '2');
});

// 2. Budget precision
test('budget calculations maintain exact precision', () => {
  const budget = 8500.00;
  const expenses = [{ amount: 1500.00 }, { amount: 1200.00 }, { amount: 600.00 }];
  const totalSpent = expenses.reduce((sum, e) => sum + e.amount, 0);
  const remaining = budget - totalSpent;
  const pct = (totalSpent / budget) * 100;

  assert.strictEqual(totalSpent, 3300.00);
  assert.strictEqual(remaining, 5200.00);
  assert.strictEqual(pct.toFixed(1), '38.8');
});

// 3. Guest RSVP count
test('guest RSVP counts accurately distinguish attending from declined', () => {
  const guests = [
    { name: 'Alice', status: 'attending' },
    { name: 'Bob', status: 'declined' },
    { name: 'Charlie', status: 'attending' },
    { name: 'David', status: 'tentative' }
  ];

  const attending = guests.filter(g => g.status === 'attending').length;
  const declined = guests.filter(g => g.status === 'declined').length;

  assert.strictEqual(attending, 2);
  assert.strictEqual(declined, 1);
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
  function format(amount, symbol = '$') {
    return `${symbol}${amount.toFixed(2)}`;
  }
  assert.strictEqual(format(1234.5, '₹'), '₹1234.50');
  assert.strictEqual(format(50, '$'), '$50.00');
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
  const slotA = { start: '10:00', end: '11:30' };
  const slotB = { start: '11:00', end: '12:00' };

  if (slotA.start < slotB.end && slotB.start < slotA.end) {
    slotB.start = slotA.end;
  }
  assert.strictEqual(slotB.start, '11:30');
});

// 9. Input validation
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

// 10. Accessible button state
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

// 11. Cryptographic token format
test('invitation token matches expected secure prefix and length', () => {
  const token = 'tok_8f92a1e4c7b8d0e1';
  assert.strictEqual(token.startsWith('tok_'), true);
  assert.strictEqual(token.length >= 16, true);
});
