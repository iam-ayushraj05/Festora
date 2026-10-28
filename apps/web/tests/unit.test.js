import test from 'node:test';
import assert from 'node:assert';

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
    { id: '2', start: '11:00', end: '13:00' }, // Overlaps with 1
    { id: '3', start: '14:00', end: '15:00' }  // No overlap
  ];

  const conflicts = detectConflicts(items);
  assert.strictEqual(conflicts.length, 1);
  assert.strictEqual(conflicts[0].a.id, '1');
  assert.strictEqual(conflicts[0].b.id, '2');
});

test('budget calculations maintain exact precision', () => {
  const budget = 8500.00;
  const expenses = [
    { amount: 1500.00 },
    { amount: 1200.00 },
    { amount: 600.00 }
  ];

  const totalSpent = expenses.reduce((sum, e) => sum + e.amount, 0);
  const remaining = budget - totalSpent;
  const pct = (totalSpent / budget) * 100;

  assert.strictEqual(totalSpent, 3300.00);
  assert.strictEqual(remaining, 5200.00);
  assert.strictEqual(pct.toFixed(1), '38.8');
});

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
