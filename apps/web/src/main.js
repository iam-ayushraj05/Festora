/**
 * Festora — GenAI-Powered Celebration & Event Planner
 * Interactive Application Engine & Performance Architecture
 * 
 * Features:
 * - O(N log N) sweep-line interval conflict detection
 * - Reactive memoized computation cache for budget & guest metrics
 * - Non-blocking debounced persistence with requestIdleCallback
 * - Fine-grained DOM reconciliation avoiding layout thrashing
 * - Delegated high-throughput event dispatchers
 */

import {
  detectScheduleConflicts,
  calculateBudgetSummary,
  calculateGuestMetrics,
  formatCurrencyFast,
  autoResolveConflict,
  debounce,
  updateInnerHTMLIfChanged,
  updateTextIfChanged
} from './algorithms.js';

// Initial Seed Events Database
const initialEvents = {
  'event-1': {
    id: 'event-1',
    name: "Anya's 30th Birthday Soirée",
    type: 'birthday',
    typeDisplay: '🎂 Milestone Birthday',
    venue: 'The Sky Lounge at Hudson Yards',
    date: '2026-11-18',
    budget: 8500.00,
    currency: 'USD',
    currencySymbol: '$',
    status: 'confirmed',
    theme: {
      title: 'Neon Starlight Glow & Cocktail Soirée',
      decor: 'Custom neon acrylic signage, interactive LED polaroid photo station, floating geometric floral centerpieces with warm micro-lights, and metallic ambient accents.',
      palette: [
        { name: 'Electric Indigo', hex: '#6366f1' },
        { name: 'Neon Coral', hex: '#fb7185' },
        { name: 'Luminous Gold', hex: '#fbbf24' },
        { name: 'Obsidian Velvet', hex: '#0f172a' }
      ],
      cocktails: 'Electric Sunset Punch & Smoky Mezcal Paloma with torched rosemary.',
      costTip: 'Opt for an artisan grazing table and gourmet passed sliders instead of formal plated courses to save ~25% on food staffing.',
      inviteCopy: "Together under midnight skies, come celebrate 30 years of laughter, triumphs, and unforgettable memories! Let's raise a glass to the golden decade ahead at The Sky Lounge."
    },
    expenses: [
      { id: 'exp-1', category: 'Venue & Lounge Rental', desc: 'Terrace rental deposit', amount: 1500.00, paid: true },
      { id: 'exp-2', category: 'Catering & Bar', desc: 'Craft cocktail bar and passed hors d’oeuvres deposit', amount: 1200.00, paid: true },
      { id: 'exp-3', category: 'Music, DJ & Audio', desc: 'DJ retainer and sound setup', amount: 600.00, paid: true }
    ],
    timeline: [
      { id: 'sch-1', title: 'Vendor & Bartender Setup', location: 'Sky Lounge Bar', start: '16:00', end: '17:30' },
      { id: 'sch-2', title: 'VIP Golden Hour Photos', location: 'Terrace Lookout', start: '17:30', end: '18:15' },
      { id: 'sch-3', title: 'Guest Arrival & Welcome Prosecco', location: 'Main Foyer', start: '18:15', end: '19:00' },
      { id: 'sch-4', title: 'Artisan Grazing Buffet & Cocktail Hour', location: 'Dining Pavilion', start: '19:00', end: '20:30' },
      { id: 'sch-5', title: 'Birthday Toast & Champagne Fountain', location: 'Main Stage', start: '20:30', end: '21:00' },
      { id: 'sch-6', title: 'Dance Floor & Late Night Tacos', location: 'Ballroom & Terrace', start: '21:00', end: '23:30' }
    ],
    guests: [
      { id: 'g-1', name: 'Maya Lin', email: 'maya@example.com', plusOnes: 1, dietary: 'Vegetarian', status: 'attending', token: 'tok_8f92a1e4' },
      { id: 'g-2', name: 'Liam Gallagher', email: 'liam@example.com', plusOnes: 0, dietary: 'Gluten-Free', status: 'attending', token: 'tok_5b31c9d2' },
      { id: 'g-3', name: 'Sophia Rodriguez', email: 'sophia@example.com', plusOnes: 1, dietary: 'None', status: 'attending', token: 'tok_7a44f8e0' },
      { id: 'g-4', name: 'David Kim', email: 'david@example.com', plusOnes: 0, dietary: 'No Shellfish', status: 'declined', token: 'tok_1c88d2b3' },
      { id: 'g-5', name: 'Zara Patel', email: 'zara@example.com', plusOnes: 2, dietary: 'Vegan', status: 'attending', token: 'tok_9e22b7f1' },
      { id: 'g-6', name: 'Ethan Brooks', email: 'ethan@example.com', plusOnes: 0, dietary: 'None', status: 'tentative', token: 'tok_3f66a0d4' },
      { id: 'g-7', name: 'Chloe Dubois', email: 'chloe@example.com', plusOnes: 1, dietary: 'Nut Allergy', status: 'attending', token: 'tok_4d77e1c8' },
      { id: 'g-8', name: 'Marcus Sterling', email: 'marcus@example.com', plusOnes: 0, dietary: 'None', status: 'attending', token: 'tok_2e99c3a5' }
    ],
    vendors: [
      { id: 'v-1', name: 'The Sky Lounge at Hudson Yards', category: 'venue', rating: '4.95', price: '$$$', booked: true, cost: 3000.00, deposit: 1500.00, notes: 'Panoramic skyline views, private terrace.' },
      { id: 'v-2', name: 'Golden Saffron & Silk Artisan Catering', category: 'catering', rating: '4.90', price: '$$$', booked: true, cost: 2800.00, deposit: 1200.00, notes: 'Farm-to-table gourmet sliders & grazing.' },
      { id: 'v-3', name: 'Lumina Aperture Cinematography', category: 'photography', rating: '4.88', price: '$$', booked: false, cost: 1800.00, deposit: 0, notes: 'Editorial documentary party coverage.' },
      { id: 'v-4', name: 'Rhythm & Pulse Sound Collective', category: 'music_dj', rating: '4.92', price: '$$', booked: true, cost: 1200.00, deposit: 600.00, notes: 'Live hybrid percussion + modern funk DJ.' }
    ]
  },

  'event-2': {
    id: 'event-2',
    name: "Marcus & Elena's Royal Wedding",
    type: 'wedding',
    typeDisplay: '💒 Royal Wedding',
    venue: 'The Grand Celestial Ballroom & Gardens',
    date: '2027-01-26',
    budget: 42000.00,
    currency: 'USD',
    currencySymbol: '$',
    status: 'planning',
    theme: {
      title: 'Ethereal Garden Bloom & Candlelit Opulence',
      decor: 'Cascading eucalyptus arches, crystal candelabras, warm floating orb candles, gold-rimmed glassware, and ivory velvet drapery.',
      palette: [
        { name: 'Champagne Gold', hex: '#f59e0b' },
        { name: 'Sage Green', hex: '#84cc16' },
        { name: 'Dusty Rose', hex: '#f43f5e' },
        { name: 'Ivory White', hex: '#f8fafc' }
      ],
      cocktails: 'Blushing Bride Bellini & Saffron Elderflower Gin Spritz.',
      costTip: 'Repurpose the ceremony floral urns as reception head table centerpieces to save ~$1,500.',
      inviteCopy: "Together with their families, Marcus & Elena invite you to celebrate a lifetime of love and joyful revelry under starlit glass pavilions at The Grand Celestial Ballroom."
    },
    expenses: [
      { id: 'exp-w1', category: 'Venue & Lounge Rental', desc: 'Grand Ballroom deposit', amount: 8000.00, paid: true },
      { id: 'exp-w2', category: 'Photography & Video', desc: 'Full wedding day cinematography retainer', amount: 3500.00, paid: true },
      { id: 'exp-w3', category: 'Catering & Bar', desc: 'Multi-course banquet tasting deposit', amount: 5000.00, paid: true }
    ],
    timeline: [
      { id: 'sch-w1', title: 'Bridal Party & Groom Hair & Makeup', location: 'Bridal Suite', start: '09:00', end: '11:30' },
      { id: 'sch-w2', title: 'First Look & Couple Portraits', location: 'Courtyard Garden', start: '11:30', end: '12:30' },
      { id: 'sch-w3', title: 'Vendor Arrival & Floral / Audio Setup', location: 'Main Ballroom', start: '12:30', end: '14:00' },
      { id: 'sch-w4', title: 'Guest Arrival & Welcome Mocktails', location: 'Foyer & Terrace', start: '14:30', end: '15:00' },
      { id: 'sch-w5', title: 'Ceremony & Exchange of Vows', location: 'Grand Pavilion', start: '15:00', end: '15:45' },
      { id: 'sch-w6', title: 'Cocktail Hour & Passed Hors d’Oeuvres', location: 'Garden Terrace', start: '15:45', end: '17:00' },
      { id: 'sch-w7', title: 'Grand Entrance & Welcome Toasts', location: 'Main Ballroom', start: '17:15', end: '17:30' },
      { id: 'sch-w8', title: 'Dinner Service & Speeches', location: 'Main Ballroom', start: '17:30', end: '19:00' },
      { id: 'sch-w9', title: 'First Dance & Open Dance Floor', location: 'Dance Floor', start: '19:00', end: '23:00' }
    ],
    guests: [
      { id: 'gw-1', name: 'Lord Henry Vance', email: 'henry@vance.com', plusOnes: 1, dietary: 'None', status: 'attending', token: 'tok_w111' },
      { id: 'gw-2', name: 'Lady Caroline Vance', email: 'caroline@vance.com', plusOnes: 0, dietary: 'Gluten-Free', status: 'attending', token: 'tok_w222' },
      { id: 'gw-3', name: 'Julian Hayes', email: 'julian@hayes.org', plusOnes: 1, dietary: 'Vegetarian', status: 'attending', token: 'tok_w333' },
      { id: 'gw-4', name: 'Amelia Warner', email: 'amelia@warner.com', plusOnes: 0, dietary: 'None', status: 'tentative', token: 'tok_w444' }
    ],
    vendors: [
      { id: 'vw-1', name: 'The Grand Celestial Ballroom & Gardens', category: 'venue', rating: '4.98', price: '$$$$', booked: true, cost: 16000.00, deposit: 8000.00, notes: 'Exclusive estate rental.' },
      { id: 'vw-2', name: 'Golden Saffron & Silk Artisan Catering', category: 'catering', rating: '4.95', price: '$$$', booked: true, cost: 12000.00, deposit: 5000.00, notes: '5-course plated banquet.' },
      { id: 'vw-3', name: 'Lumina Aperture Cinematography', category: 'photography', rating: '4.92', price: '$$$', booked: true, cost: 5500.00, deposit: 3500.00, notes: '4K cinema drone + 2 shooters.' },
      { id: 'vw-4', name: 'Velvet Petals & Gilded Light Floral Co.', category: 'decor_floral', rating: '4.89', price: '$$$', booked: false, cost: 4500.00, deposit: 0, notes: 'Floral arches and suspended chandeliers.' }
    ]
  },

  'event-3': {
    id: 'event-3',
    name: 'Austin Tech Community Festival',
    type: 'community',
    typeDisplay: '🎪 Community Festival',
    venue: 'Zilker Metropolitan Park, Austin',
    date: '2026-12-05',
    budget: 18000.00,
    currency: 'USD',
    currencySymbol: '$',
    status: 'confirmed',
    theme: {
      title: 'Unity Horizon: Innovation & Cultural Harvest Fair',
      decor: 'Artisan wooden market booths, solar-powered fairy canopies, interactive community mural wall, and weatherproof cable ramps for stage sound.',
      palette: [
        { name: 'Vibrant Marigold', hex: '#f59e0b' },
        { name: 'Teal Blue', hex: '#06b6d4' },
        { name: 'Emerald Green', hex: '#10b981' },
        { name: 'Warm Terracotta', hex: '#ea580c' }
      ],
      cocktails: 'Artisan Local Spiced Cider & Hill Country Mint Cooler.',
      costTip: 'Partner with local neighborhood artisan stalls for co-sponsored equipment rentals and volunteer support.',
      inviteCopy: "Bringing builders, designers, and innovators together! Come for the tech showcases, stay for the live bands, and celebrate community spirit under the Austin sunshine."
    },
    expenses: [
      { id: 'exp-c1', category: 'Permits & Venue Security', desc: 'City park permit and EMS dispatch reserve', amount: 3200.00, paid: true },
      { id: 'exp-c2', category: 'Sound, Stage & Lighting', desc: 'Main stage rigging, speakers and generator', amount: 4500.00, paid: true },
      { id: 'exp-c3', category: 'Food Stalls & Refreshments', desc: 'Water refill stations and volunteer meal vouchers', amount: 2000.00, paid: true }
    ],
    timeline: [
      { id: 'sch-c1', title: 'Vendor Stall Setup & Stage Rigging', location: 'Festival Grounds', start: '07:00', end: '09:00' },
      { id: 'sch-c2', title: 'Safety Inspection & Audio Check', location: 'Main Stage', start: '09:00', end: '09:30' },
      { id: 'sch-c3', title: 'Gates Open & Community Welcome', location: 'Main Gate', start: '09:30', end: '10:00' },
      { id: 'sch-c4', title: 'Morning Demos & Open-Source Showcase', location: 'Pavilion Stage', start: '10:00', end: '13:00' },
      { id: 'sch-c5', title: 'Community Lunch & Food Truck Fair', location: 'Food Boulevard', start: '13:00', end: '14:30' },
      { id: 'sch-c6', title: 'Live Music & Hackathon Awards Ceremony', location: 'Main Stage', start: '14:30', end: '17:30' }
    ],
    guests: [
      { id: 'gc-1', name: 'Austin Civic League', email: 'civic@austin.gov', plusOnes: 10, dietary: 'Assorted', status: 'attending', token: 'tok_c1' },
      { id: 'gc-2', name: 'DevRelay Community Team', email: 'team@devrelay.com', plusOnes: 4, dietary: 'Vegetarian', status: 'attending', token: 'tok_c2' }
    ],
    vendors: [
      { id: 'vc-1', name: 'Zilker Park Events Office', category: 'venue', rating: '4.80', price: '$$', booked: true, cost: 4000.00, deposit: 3200.00, notes: 'Municipal permit approved.' },
      { id: 'vc-2', name: 'Austin Stage & Sound Production', category: 'music_dj', rating: '4.91', price: '$$$', booked: true, cost: 4500.00, deposit: 4500.00, notes: 'Generators and dual stage PA.' }
    ]
  }
};

// Global App State
let appData = {
  events: initialEvents,
  currentEventId: 'event-1',
  currency: 'USD',
  currencyRate: 1.0,
  currencySymbol: '$'
};

// Load saved data if present
try {
  const saved = localStorage.getItem('festora_app_data');
  if (saved) {
    const parsed = JSON.parse(saved);
    if (parsed.events) {
      appData = parsed;
    }
  }
} catch (e) {
  console.warn("Storage access restricted, using in-memory state.");
}

/**
 * Non-blocking, debounced persistence layer.
 * Defers serialization to requestIdleCallback, preventing UI thread blocking.
 */
const persistAppDataDebounced = debounce(() => {
  try {
    localStorage.setItem('festora_app_data', JSON.stringify(appData));
  } catch (e) {}
}, 250);

function saveAppData() {
  persistAppDataDebounced();
}

function getCurrentEvent() {
  return appData.events[appData.currentEventId] || appData.events['event-1'];
}

// Currency Exchange rates for preview
const currencySymbols = {
  USD: '$',
  INR: '₹',
  EUR: '€',
  GBP: '£',
  CAD: '$',
  AUD: '$'
};
const currencyRates = {
  USD: 1.0,
  INR: 85.0,
  EUR: 0.92,
  GBP: 0.79,
  CAD: 1.38,
  AUD: 1.52
};

function formatCurrency(amount) {
  const symbol = currencySymbols[appData.currency] || '$';
  const rate = currencyRates[appData.currency] || 1.0;
  return formatCurrencyFast(amount, appData.currency, rate, symbol);
}

// Toast notification helper with micro-animations and DOM node throttling
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  if (!container) return;
  // Prevent DOM tree bloat by capping active toasts to 3
  while (container.children.length >= 3) {
    container.firstElementChild?.remove();
  }
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${type === 'success' ? '✅' : type === 'warning' ? '⚠️' : '✨'}</span> <span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(20px)';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

/**
 * Active tab tracking and dirty-flag view cache.
 * Avoids reconstructing HTML and traversing DOM for hidden tabs.
 */
let currentActiveTab = 'tab-ai';
const dirtyTabs = new Set(['tab-ai', 'tab-budget', 'tab-timeline', 'tab-vendors', 'tab-guests']);

function markTabsDirty(...tabs) {
  if (tabs.length === 0) {
    ['tab-ai', 'tab-budget', 'tab-timeline', 'tab-vendors', 'tab-guests'].forEach(t => dirtyTabs.add(t));
  } else {
    tabs.forEach(t => dirtyTabs.add(t));
  }
}

/**
 * Reactive computation cache.
 * Avoids recalculating budget totals, cost-per-guest metrics,
 * timeline conflicts, and vendor comparisons when inputs have not changed.
 */
const memoCache = {
  eventId: '',
  expensesHash: '',
  budgetSummary: null,
  timelineHash: '',
  conflicts: null,
  guestsHash: '',
  guestMetrics: null,
  vendorsHash: '',
  bookedVendorsCount: 0
};

// UI Rendering Engine with fine-grained element reconciliation
function renderApp() {
  const ev = getCurrentEvent();
  if (!ev) return;

  // 1. Hero & Badges
  updateTextIfChanged(document.getElementById('heroTypeBadge'), ev.typeDisplay);
  updateTextIfChanged(document.getElementById('heroTitle'), ev.name);
  updateTextIfChanged(document.getElementById('heroVenue'), ev.venue);
  updateTextIfChanged(
    document.getElementById('heroDate'),
    new Date(ev.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
  );

  // Calculate days remaining
  const eventDate = new Date(ev.date);
  const now = new Date();
  const daysDiff = Math.ceil((eventDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
  updateTextIfChanged(
    document.getElementById('heroCountdown'),
    daysDiff > 0 ? `${daysDiff} days remaining` : (daysDiff === 0 ? 'Today!' : 'Completed')
  );

  const statusBadge = document.getElementById('heroStatusBadge');
  if (statusBadge) {
    statusBadge.className = `badge badge-${ev.status}`;
    updateTextIfChanged(statusBadge, ev.status.charAt(0).toUpperCase() + ev.status.slice(1));
  }

  // 2. Budget Calculations with Cache Check
  const expensesHash = `${ev.budget}-${ev.expenses.length}-${ev.expenses.map(e => `${e.id}:${e.amount}`).join('|')}`;
  if (memoCache.eventId !== ev.id || memoCache.expensesHash !== expensesHash) {
    memoCache.budgetSummary = calculateBudgetSummary(ev.budget, ev.expenses);
    memoCache.expensesHash = expensesHash;
  }
  const budgetSum = memoCache.budgetSummary;

  updateTextIfChanged(
    document.getElementById('kpiBudgetSpent'),
    `${formatCurrency(budgetSum.totalSpent)} / ${formatCurrency(budgetSum.totalBudget)}`
  );
  updateTextIfChanged(document.getElementById('budgetSpentDisplay'), formatCurrency(budgetSum.totalSpent));
  updateTextIfChanged(document.getElementById('budgetTotalDisplay'), formatCurrency(budgetSum.totalBudget));
  updateTextIfChanged(document.getElementById('budgetRemainingDisplay'), formatCurrency(budgetSum.remainingBudget));
  updateTextIfChanged(document.getElementById('budgetPctDisplay'), `${budgetSum.utilizationPct}% Utilized`);

  const progressBar = document.getElementById('budgetProgressBar');
  if (progressBar) {
    progressBar.style.width = `${Math.min(budgetSum.utilizationPct, 100)}%`;
    if (budgetSum.utilizationPct > 90) {
      progressBar.classList.add('danger');
    } else {
      progressBar.classList.remove('danger');
    }
  }

  // 3. Guests & RSVPs Calculations with Cache Check
  const guestsHash = `${ev.guests.length}-${ev.guests.map(g => `${g.id}:${g.status}:${g.plusOnes}`).join('|')}-${budgetSum.totalSpent}`;
  if (memoCache.eventId !== ev.id || memoCache.guestsHash !== guestsHash) {
    memoCache.guestMetrics = calculateGuestMetrics(ev.guests, budgetSum.totalSpent);
    memoCache.guestsHash = guestsHash;
  }
  const guestMet = memoCache.guestMetrics;

  updateTextIfChanged(document.getElementById('kpiGuests'), `${guestMet.confirmedCount} Confirmed`);
  updateTextIfChanged(document.getElementById('costPerGuestDisplay'), formatCurrency(guestMet.costPerGuest));

  // 4. Timeline & Conflict Detection with Sweep-Line Algorithm & Cache Check
  const timelineHash = `${ev.timeline.length}-${ev.timeline.map(t => `${t.id}:${t.start}-${t.end}`).join('|')}`;
  if (memoCache.eventId !== ev.id || memoCache.timelineHash !== timelineHash) {
    memoCache.conflicts = detectScheduleConflicts(ev.timeline);
    memoCache.timelineHash = timelineHash;
  }
  const conflicts = memoCache.conflicts;

  updateTextIfChanged(document.getElementById('kpiTimeline'), `${ev.timeline.length} Slots`);
  const conflictStatus = document.getElementById('kpiConflictStatus');
  const conflictBanner = document.getElementById('scheduleConflictBanner');

  if (conflicts.length > 0) {
    if (conflictStatus) {
      conflictStatus.textContent = `⚠️ ${conflicts.length} Overlap Conflict!`;
      conflictStatus.style.color = 'var(--accent-rose)';
    }
    if (conflictBanner) conflictBanner.style.display = 'flex';
    updateTextIfChanged(
      document.getElementById('scheduleConflictMessage'),
      `Conflict between "${conflicts[0].itemA.title}" (${conflicts[0].itemA.start}-${conflicts[0].itemA.end}) and "${conflicts[0].itemB.title}" (${conflicts[0].itemB.start}-${conflicts[0].itemB.end}).`
    );
  } else {
    if (conflictStatus) {
      conflictStatus.textContent = '0 Schedule Conflicts';
      conflictStatus.style.color = 'var(--text-secondary)';
    }
    if (conflictBanner) conflictBanner.style.display = 'none';
  }

  // 5. Vendors KPI with Cache Check
  const vendorsHash = `${ev.vendors.length}-${ev.vendors.map(v => `${v.id}:${v.booked}`).join('|')}`;
  if (memoCache.eventId !== ev.id || memoCache.vendorsHash !== vendorsHash) {
    memoCache.bookedVendorsCount = ev.vendors.filter(v => v.booked).length;
    memoCache.vendorsHash = vendorsHash;
  }
  updateTextIfChanged(document.getElementById('kpiVendors'), `${memoCache.bookedVendorsCount} Booked`);

  memoCache.eventId = ev.id;

  // 6. Active Tab Sub-view Rendering with Lazy Dirty Checking
  renderSubView(currentActiveTab, ev, conflicts);
}

/**
 * Lazily renders a specific sub-view only when required.
 * @param {string} tabId
 * @param {any} [ev]
 * @param {any[]} [conflicts]
 */
function renderSubView(tabId, ev, conflicts) {
  if (!ev) ev = getCurrentEvent();
  if (!conflicts) conflicts = memoCache.conflicts || [];

  switch (tabId) {
    case 'tab-ai':
      renderAIStudio(ev);
      break;
    case 'tab-budget':
      renderExpenses(ev);
      break;
    case 'tab-timeline':
      renderTimeline(ev, conflicts);
      break;
    case 'tab-vendors':
      renderVendors(ev);
      break;
    case 'tab-guests':
      renderGuests(ev);
      break;
  }
  dirtyTabs.delete(tabId);
}

// Render GenAI Studio
function renderAIStudio(ev) {
  const theme = ev.theme;
  updateTextIfChanged(document.getElementById('aiThemeTitle'), theme.title);
  updateTextIfChanged(document.getElementById('aiThemeDecor'), theme.decor);
  updateTextIfChanged(document.getElementById('aiCocktails'), theme.cocktails);
  updateTextIfChanged(document.getElementById('aiCostTip'), theme.costTip);
  updateTextIfChanged(document.getElementById('aiInviteCopy'), `"${theme.inviteCopy}"`);
  updateTextIfChanged(document.getElementById('aiBudgetTypeName'), ev.typeDisplay);

  // Render Palette
  const palContainer = document.getElementById('aiPaletteContainer');
  const paletteHTML = theme.palette.map(p => `
    <div class="color-swatch-item">
      <div class="swatch-circle" style="background-color: ${p.hex};"></div>
      <span>${p.name}</span>
    </div>
  `).join('');
  updateInnerHTMLIfChanged(palContainer, paletteHTML);

  // Render Budget Breakdown
  const budgetList = document.getElementById('aiBudgetBreakdownList');
  const total = ev.budget;
  const splits = ev.type === 'wedding'
    ? [
        { name: 'Venue & Hall', pct: 30 },
        { name: 'Catering & Signature Cocktails', pct: 30 },
        { name: 'Photography & Cinematography', pct: 15 },
        { name: 'Floral, Decor & Ambience', pct: 10 },
        { name: 'Music, Sound & DJ', pct: 8 },
        { name: 'Contingency & Favors', pct: 7 }
      ]
    : [
        { name: 'Venue & Rentals', pct: 25 },
        { name: 'Food, Drinks & Bar', pct: 35 },
        { name: 'Decor & Theme Accents', pct: 15 },
        { name: 'DJ & Sound System', pct: 15 },
        { name: 'Emergency Contingency', pct: 10 }
      ];

  const splitsHTML = splits.map(s => {
    const amt = (total * (s.pct / 100));
    return `
      <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.03); padding: 0.5rem 0.85rem; border-radius: 6px;">
        <span>${s.name} <strong style="color: var(--text-gold);">(${s.pct}%)</strong></span>
        <span>${formatCurrency(amt)}</span>
      </div>
    `;
  }).join('');
  updateInnerHTMLIfChanged(budgetList, splitsHTML);

  // Render AI Checkpoints
  const checkList = document.getElementById('aiChecklistItems');
  const checkpoints = [
    'Confirm noise curfew and alcohol licensing with the venue team.',
    'Schedule final dietary requirement count with executive chef 7 days prior.',
    'Deliver specialized "Must-Play" and "Do-Not-Play" song lists to the sound DJ.',
    'Test microphone acoustics and ambient lighting levels at golden hour.',
    'Prepare designated sparkler / confetti departure kits with safety buckets.'
  ];
  const checkpointsHTML = checkpoints.map(c => `
    <li style="display: flex; align-items: flex-start; gap: 0.5rem;">
      <span style="color: var(--accent-emerald);">✔</span> <span>${c}</span>
    </li>
  `).join('');
  updateInnerHTMLIfChanged(checkList, checkpointsHTML);
}

// Render Expenses Table with delegated data attributes
function renderExpenses(ev) {
  const tbody = document.getElementById('expensesTableBody');
  const html = ev.expenses.map(exp => `
    <tr>
      <td><strong>${exp.category}</strong></td>
      <td>${exp.desc}</td>
      <td style="font-weight: 700; color: #fff;">${formatCurrency(exp.amount)}</td>
      <td>
        <span class="badge ${exp.paid ? 'badge-confirmed' : 'badge-planning'}">
          ${exp.paid ? 'Paid' : 'Pending'}
        </span>
      </td>
      <td>
        <button class="btn btn-secondary btn-sm" data-action="delete-expense" data-id="${exp.id}">Delete</button>
      </td>
    </tr>
  `).join('');
  updateInnerHTMLIfChanged(tbody, html);
}

// Render Timeline with delegated data attributes
function renderTimeline(ev, conflicts) {
  const container = document.getElementById('timelineItemsContainer');
  const conflictIds = new Set();
  conflicts.forEach(c => {
    conflictIds.add(c.itemA.id);
    conflictIds.add(c.itemB.id);
  });

  const sorted = [...ev.timeline].sort((a, b) => a.start.localeCompare(b.start));

  const html = sorted.map(item => {
    const isConflict = conflictIds.has(item.id);
    return `
      <div class="timeline-item-card ${isConflict ? 'has-conflict' : ''}">
        <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
          <span class="timeline-time-badge">${item.start} - ${item.end}</span>
          <div>
            <div style="font-weight: 700; font-size: 1.05rem;">${item.title}</div>
            <div style="color: var(--text-secondary); font-size: 0.85rem;">📍 ${item.location}</div>
          </div>
        </div>
        <div style="display: flex; align-items: center; gap: 0.75rem;">
          ${isConflict ? '<span class="badge badge-conflict">Overlap Alert!</span>' : ''}
          <button class="btn btn-secondary btn-sm" data-action="delete-schedule" data-id="${item.id}">Remove</button>
        </div>
      </div>
    `;
  }).join('');
  updateInnerHTMLIfChanged(container, html);
}

// Render Vendors with delegated data attributes
function renderVendors(ev) {
  const grid = document.getElementById('vendorGrid');
  const html = ev.vendors.map(v => `
    <div class="ai-card">
      <span class="ai-card-badge" style="${v.booked ? 'background: rgba(16,185,129,0.18); color: #10b981;' : ''}">
        ${v.booked ? 'Booked & Confirmed' : 'Quote Requested'}
      </span>
      <h3 class="ai-card-title">${v.name}</h3>
      <p style="color: var(--text-secondary); font-size: 0.88rem; margin-bottom: 0.75rem;">
        Category: <strong>${v.category.toUpperCase()}</strong> | Price Range: <strong>${v.price}</strong> | Rating: ⭐ <strong>${v.rating}</strong>
      </p>
      <p style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 1rem;">${v.notes}</p>
      <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border-subtle); padding-top: 0.75rem;">
        <span style="font-weight: 700; color: #fff;">Est: ${formatCurrency(v.cost)}</span>
        <button class="btn ${v.booked ? 'btn-secondary' : 'btn-primary'} btn-sm" data-action="toggle-vendor" data-id="${v.id}">
          ${v.booked ? 'Cancel Booking' : 'Confirm Booking'}
        </button>
      </div>
    </div>
  `).join('');
  updateInnerHTMLIfChanged(grid, html);
}

// Render Guests
function renderGuests(ev) {
  const tbody = document.getElementById('guestsTableBody');
  const html = ev.guests.map(g => {
    let badgeClass = 'badge-planning';
    if (g.status === 'attending') badgeClass = 'badge-confirmed';
    if (g.status === 'declined') badgeClass = 'badge-conflict';

    return `
      <tr>
        <td><strong>${g.name}</strong></td>
        <td>${g.email || '—'}</td>
        <td>${g.plusOnes > 0 ? `+${g.plusOnes} guest(s)` : 'None'}</td>
        <td>
          ${g.dietary ? `<span style="background: rgba(139,92,246,0.15); color: #c4b5fd; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem;">${g.dietary}</span>` : '<span style="color: var(--text-muted);">None specified</span>'}
        </td>
        <td>
          <span class="badge ${badgeClass}">${g.status.toUpperCase()}</span>
        </td>
        <td>
          <code style="background: rgba(0,0,0,0.4); padding: 2px 6px; border-radius: 4px; font-size: 0.76rem; color: var(--accent-gold);">${g.token}</code>
        </td>
      </tr>
    `;
  }).join('');
  updateInnerHTMLIfChanged(tbody, html);

  // Populate guest dropdown for the simulation modal
  const select = /** @type {HTMLSelectElement|null} */ (document.getElementById('rsvpGuestSelect'));
  if (select) {
    const opts = ev.guests.map(g => `
      <option value="${g.id}">${g.name} (${g.status.toUpperCase()})</option>
    `).join('');
    updateInnerHTMLIfChanged(select, opts);
  }
}

// High-performance Event Delegation Listeners (Avoids inline onclick thrashing)
document.getElementById('expensesTableBody')?.addEventListener('click', (e) => {
  const target = /** @type {HTMLElement|null} */ (e.target);
  const btn = target?.closest('[data-action="delete-expense"]');
  if (btn) {
    const id = btn.getAttribute('data-id');
    if (id) deleteExpenseById(id);
  }
});

document.getElementById('timelineItemsContainer')?.addEventListener('click', (e) => {
  const target = /** @type {HTMLElement|null} */ (e.target);
  const btn = target?.closest('[data-action="delete-schedule"]');
  if (btn) {
    const id = btn.getAttribute('data-id');
    if (id) deleteScheduleItemById(id);
  }
});

document.getElementById('vendorGrid')?.addEventListener('click', (e) => {
  const target = /** @type {HTMLElement|null} */ (e.target);
  const btn = target?.closest('[data-action="toggle-vendor"]');
  if (btn) {
    const id = btn.getAttribute('data-id');
    if (id) toggleVendorBookingById(id);
  }
});

function deleteExpenseById(id) {
  const ev = getCurrentEvent();
  ev.expenses = ev.expenses.filter(e => e.id !== id);
  markTabsDirty('tab-budget');
  saveAppData();
  renderApp();
  showToast("Expense removed successfully.", "info");
}

function deleteScheduleItemById(id) {
  const ev = getCurrentEvent();
  ev.timeline = ev.timeline.filter(t => t.id !== id);
  markTabsDirty('tab-timeline');
  saveAppData();
  renderApp();
  showToast("Schedule slot removed.", "info");
}

function toggleVendorBookingById(id) {
  const ev = getCurrentEvent();
  const v = ev.vendors.find(item => item.id === id);
  if (v) {
    v.booked = !v.booked;
    markTabsDirty('tab-vendors');
    saveAppData();
    renderApp();
    showToast(v.booked ? `Booking confirmed for ${v.name}!` : `Booking cancelled for ${v.name}.`, v.booked ? "success" : "info");
  }
}

// Backward compatibility window exposures
/** @type {any} */ (window).deleteExpense = deleteExpenseById;
/** @type {any} */ (window).deleteScheduleItem = deleteScheduleItemById;
/** @type {any} */ (window).toggleVendorBooking = toggleVendorBookingById;

// Auto-resolve overlap handler with algorithms.js resolver
document.getElementById('btnAutoResolveConflict')?.addEventListener('click', () => {
  const ev = getCurrentEvent();
  const conflicts = detectScheduleConflicts(ev.timeline);
  if (conflicts.length > 0) {
    const conflict = conflicts[0];
    const resolved = autoResolveConflict(conflict);
    conflict.itemB.start = resolved.newStart;
    conflict.itemB.end = resolved.newEnd;
    markTabsDirty('tab-timeline');
    saveAppData();
    renderApp();
    showToast(`Schedule overlap auto-resolved! Shifted to ${resolved.newStart}-${resolved.newEnd}`, "success");
  }
});

// Event Switcher Listener
document.getElementById('eventSelect')?.addEventListener('change', (e) => {
  const target = /** @type {HTMLSelectElement} */ (e.target);
  appData.currentEventId = target.value;
  markTabsDirty();
  saveAppData();
  renderApp();
  showToast(`Switched active event to: ${getCurrentEvent().name}`, 'info');
});

// Currency Switcher
document.getElementById('currencySelector')?.addEventListener('change', (e) => {
  const target = /** @type {HTMLSelectElement} */ (e.target);
  appData.currency = target.value;
  markTabsDirty('tab-ai', 'tab-budget', 'tab-vendors');
  renderApp();
  showToast(`Currency changed to ${appData.currency}`, 'info');
});

// Tab Navigation Listener with lazy rendering
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => {
      b.classList.remove('active');
      b.setAttribute('aria-selected', 'false');
    });
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));

    btn.classList.add('active');
    btn.setAttribute('aria-selected', 'true');
    const tabName = btn.getAttribute('data-tab');
    if (tabName) {
      currentActiveTab = tabName;
      const target = document.getElementById(tabName);
      if (target) target.classList.add('active');

      // Lazily render view if dirty
      if (dirtyTabs.has(tabName)) {
        renderSubView(tabName);
      }
    }
  });
});

// Modal Open / Close Helpers
function openModal(id) {
  const m = document.getElementById(id);
  if (m) m.classList.add('open');
}

function closeModal(id) {
  const m = document.getElementById(id);
  if (m) m.classList.remove('open');
}

document.querySelectorAll('[data-close]').forEach(btn => {
  btn.addEventListener('click', () => {
    const modalId = btn.getAttribute('data-close');
    if (modalId) closeModal(modalId);
  });
});

// Trigger Buttons for Modals
document.getElementById('btnNewEvent')?.addEventListener('click', () => openModal('modalNewEvent'));
document.getElementById('btnAddExpense')?.addEventListener('click', () => openModal('modalAddExpense'));
document.getElementById('btnAddScheduleItem')?.addEventListener('click', () => openModal('modalAddSchedule'));
document.getElementById('btnSimulateRSVP')?.addEventListener('click', () => openModal('modalSimulateRSVP'));

// Modal Form Submissions
// 1. New Event
document.getElementById('btnSubmitNewEvent')?.addEventListener('click', (e) => {
  e.preventDefault();
  const nameInput = /** @type {HTMLInputElement} */ (document.getElementById('newEvName'));
  const typeInput = /** @type {HTMLSelectElement} */ (document.getElementById('newEvType'));
  const venueInput = /** @type {HTMLInputElement} */ (document.getElementById('newEvVenue'));
  const dateInput = /** @type {HTMLInputElement} */ (document.getElementById('newEvDate'));
  const budgetInput = /** @type {HTMLInputElement} */ (document.getElementById('newEvBudget'));

  const name = nameInput?.value.trim();
  const type = typeInput?.value;
  const venue = venueInput?.value.trim();
  const date = dateInput?.value;
  const budget = parseFloat(budgetInput?.value) || 10000;

  if (!name || !venue || !date) {
    showToast("Please fill in all event fields.", "warning");
    return;
  }

  const id = `event-${Date.now()}`;
  /** @type {Record<string, string>} */
  const typeMap = {
    wedding: '💒 Wedding Ceremony',
    birthday: '🎂 Milestone Birthday',
    community: '🎪 Community Festival',
    corporate: '🏢 Corporate Celebration'
  };

  appData.events[id] = {
    id,
    name,
    type,
    typeDisplay: typeMap[type] || '🎉 Celebration',
    venue,
    date,
    budget,
    currency: 'USD',
    currencySymbol: '$',
    status: 'planning',
    theme: {
      title: `${name} — Bespoke Vibe`,
      decor: 'Curated atmospheric lighting, ambient botanicals, customized entrance statement, and signature lounge seating.',
      palette: [
        { name: 'Royal Gold', hex: '#f59e0b' },
        { name: 'Deep Amethyst', hex: '#8b5cf6' },
        { name: 'Rose Petal', hex: '#f43f5e' },
        { name: 'Midnight', hex: '#0f172a' }
      ],
      cocktails: 'Celebration Starlight Spritz & Artisanal Blackberry Mocktail',
      costTip: 'Book off-peak vendor time slots for photography and acoustics to enjoy bundled discounts.',
      inviteCopy: `We are thrilled to welcome you to ${name} at ${venue} on ${date}. Let's make this day unforgettable!`
    },
    expenses: [
      { id: `exp-${Date.now()}`, category: 'Venue & Lounge Rental', desc: 'Initial holding deposit', amount: budget * 0.2, paid: true }
    ],
    timeline: [
      { id: `sch-${Date.now()}-1`, title: 'Setup & Vendor Arrival', location: venue, start: '15:00', end: '16:30' },
      { id: `sch-${Date.now()}-2`, title: 'Guest Arrival & Welcome', location: venue, start: '16:30', end: '17:30' },
      { id: `sch-${Date.now()}-3`, title: 'Main Celebration Program', location: venue, start: '17:30', end: '20:30' }
    ],
    guests: [
      { id: `g-${Date.now()}`, name: 'VIP Guest', email: 'guest@festora.test', plusOnes: 1, dietary: 'None', status: 'attending', token: 'tok_vip123' }
    ],
    vendors: [
      { id: `v-${Date.now()}`, name: venue, category: 'venue', rating: '4.90', price: '$$$', booked: true, cost: budget * 0.35, deposit: budget * 0.2, notes: 'Primary celebration venue.' }
    ]
  };

  appData.currentEventId = id;
  markTabsDirty();
  saveAppData();

  // Update selector
  const select = document.getElementById('eventSelect');
  if (select) {
    const opt = document.createElement('option');
    opt.value = id;
    opt.textContent = `${name} (${type.toUpperCase()})`;
    opt.selected = true;
    select.appendChild(opt);
  }

  closeModal('modalNewEvent');
  renderApp();
  showToast(`Celebration "${name}" created!`, "success");
});

// 2. Add Expense
document.getElementById('btnSubmitExpense')?.addEventListener('click', (e) => {
  e.preventDefault();
  const catInput = /** @type {HTMLSelectElement} */ (document.getElementById('expCategory'));
  const descInput = /** @type {HTMLInputElement} */ (document.getElementById('expDesc'));
  const amtInput = /** @type {HTMLInputElement} */ (document.getElementById('expAmount'));
  const paidInput = /** @type {HTMLInputElement} */ (document.getElementById('expPaid'));

  const category = catInput?.value;
  const desc = descInput?.value.trim();
  const amount = parseFloat(amtInput?.value);
  const paid = Boolean(paidInput?.checked);

  if (!desc || isNaN(amount) || amount <= 0) {
    showToast("Please provide a valid description and positive amount.", "warning");
    return;
  }

  const ev = getCurrentEvent();
  ev.expenses.push({
    id: `exp-${Date.now()}`,
    category,
    desc,
    amount,
    paid
  });

  markTabsDirty('tab-budget');
  saveAppData();
  closeModal('modalAddExpense');
  const form = /** @type {HTMLFormElement|null} */ (document.getElementById('formAddExpense'));
  if (form) form.reset();
  renderApp();
  showToast(`Recorded expense: ${desc} (${formatCurrency(amount)})`, "success");
});

// 3. Add Schedule Slot
document.getElementById('btnSubmitSchedule')?.addEventListener('click', (e) => {
  e.preventDefault();
  const titleInput = /** @type {HTMLInputElement} */ (document.getElementById('schedTitle'));
  const locInput = /** @type {HTMLInputElement} */ (document.getElementById('schedLocation'));
  const startInput = /** @type {HTMLInputElement} */ (document.getElementById('schedStart'));
  const endInput = /** @type {HTMLInputElement} */ (document.getElementById('schedEnd'));

  const title = titleInput?.value.trim();
  const location = locInput?.value.trim();
  const start = startInput?.value;
  const end = endInput?.value;

  if (!title || !location || !start || !end) {
    showToast("Please complete all schedule fields.", "warning");
    return;
  }

  if (start >= end) {
    showToast("End time must be after start time.", "warning");
    return;
  }

  const ev = getCurrentEvent();
  ev.timeline.push({
    id: `sch-${Date.now()}`,
    title,
    location,
    start,
    end
  });

  markTabsDirty('tab-timeline');
  saveAppData();
  closeModal('modalAddSchedule');
  const form = /** @type {HTMLFormElement|null} */ (document.getElementById('formAddSchedule'));
  if (form) form.reset();
  renderApp();
  showToast(`Added schedule slot: ${title}`, "success");
});

// 4. Submit Guest RSVP Simulation
document.getElementById('btnSubmitRSVP')?.addEventListener('click', (e) => {
  e.preventDefault();
  const guestSelect = /** @type {HTMLSelectElement} */ (document.getElementById('rsvpGuestSelect'));
  const checkedChoice = /** @type {HTMLInputElement|null} */ (document.querySelector('input[name="rsvpStatusChoice"]:checked'));
  const plusInput = /** @type {HTMLInputElement} */ (document.getElementById('rsvpPlusOnes'));
  const dietaryInput = /** @type {HTMLInputElement} */ (document.getElementById('rsvpDietary'));

  const guestId = guestSelect?.value;
  const statusChoice = checkedChoice ? checkedChoice.value : 'attending';
  const plusOnes = parseInt(plusInput?.value) || 0;
  const dietary = dietaryInput?.value.trim();

  const ev = getCurrentEvent();
  const guest = ev.guests.find(g => g.id === guestId);
  if (guest) {
    guest.status = statusChoice;
    guest.plusOnes = plusOnes;
    if (dietary) guest.dietary = dietary;

    markTabsDirty('tab-guests');
    saveAppData();
    closeModal('modalSimulateRSVP');
    renderApp();
    showToast(`RSVP recorded for ${guest.name}: ${statusChoice.toUpperCase()}`, "success");
  }
});

// AI Copilot Execution
function executeCopilot(promptText) {
  if (!promptText) return;
  const ev = getCurrentEvent();
  const lower = promptText.toLowerCase();
  let reply = "";

  if (lower.includes("budget") || lower.includes("save") || lower.includes("cost")) {
    reply = `Festora Cost-Saving Recommendations for ${ev.name}:\n\n` +
      `1. Floral Repurposing: Transition your ceremonial floral arches to the reception head table (saves ~$1,200).\n` +
      `2. Curated Bar Menu: Select 2 signature cocktails plus local craft beer and regional wines rather than open multi-brand spirits.\n` +
      `3. Digital-First Invites: Use Festora's 128-bit cryptographic invite links for instant RSVPs, cutting stationery printing and postage costs completely.`;
  } else if (lower.includes("rain") || lower.includes("weather") || lower.includes("backup")) {
    reply = `Weather Contingency Protocol for ${ev.venue}:\n\n` +
      `1. Pre-book an on-call glass conservatory or marquee 72h prior.\n` +
      `2. Supply 30 transparent dome umbrellas for cinematic, editorial photography portraits.\n` +
      `3. Ensure vendor audio cables are elevated with weatherproof heavy-duty ramps.`;
  } else if (lower.includes("rsvp") || lower.includes("reminder") || lower.includes("template")) {
    reply = `Polite RSVP Reminder Copy:\n\n` +
      `"Hi [Name]! We are putting the final touches on our seating plan and gourmet menu for ${ev.name}. ` +
      `We'd love to have you with us—please confirm your attendance by this Friday using your personalized invitation link!"`;
  } else if (lower.includes("speech") || lower.includes("toast")) {
    reply = `Master Celebration Speech Outline (3-4 mins):\n\n` +
      `1. Opening Hook: A humorous or heartfelt memory that captures the host's character.\n` +
      `2. The Journey: A meaningful milestone, obstacle overcome, or bond forged.\n` +
      `3. Gratitude: Thanking the guests, family, and organizers who traveled to be here.\n` +
      `4. The Climax Toast: Raising a glass with a high-energy blessing for the years ahead!`;
  } else {
    reply = `Festora Event Intelligence Response:\n\n` +
      `For your ${ev.typeDisplay} at ${ev.venue}, I recommend synchronizing the arrival times of Catering and Lighting 90 minutes before doors open. ` +
      `With a budget of ${formatCurrency(ev.budget)}, allocating 30% to venue and 35% to food/cocktails provides the most memorable guest experience.`;
  }

  const box = document.getElementById('aiCopilotResponseBox');
  const textElem = document.getElementById('aiCopilotResponseText');
  if (box) box.style.display = 'block';
  updateTextIfChanged(textElem, reply);
  showToast("Festora AI generated advice.", "info");
}

document.getElementById('btnSendCopilot')?.addEventListener('click', () => {
  const input = /** @type {HTMLInputElement|null} */ (document.getElementById('aiCopilotInput'));
  const text = input?.value.trim();
  if (text) {
    executeCopilot(text);
    if (input) input.value = '';
  }
});

document.getElementById('aiCopilotInput')?.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    document.getElementById('btnSendCopilot')?.click();
  }
});

// Quick Prompt Chips
document.querySelectorAll('.ai-chip').forEach(chip => {
  chip.addEventListener('click', () => {
    const prompt = chip.getAttribute('data-prompt');
    if (prompt) executeCopilot(prompt);
  });
});

// AI Re-synthesize
document.getElementById('btnRegenerateAI')?.addEventListener('click', () => {
  showToast("Re-synthesizing personalized celebration concepts...", "info");
  setTimeout(() => {
    const ev = getCurrentEvent();
    ev.theme.title = ev.type === 'wedding' ? 'Velvet Moon & Golden Radiance' : 'Electric Sunset & Gilded Disco';
    markTabsDirty('tab-ai');
    saveAppData();
    renderApp();
    showToast("New personalized theme & concepts generated!", "success");
  }, 600);
});

// Copy Invite Copy to Clipboard
document.getElementById('btnCopyInvite')?.addEventListener('click', () => {
  const elem = document.getElementById('aiInviteCopy');
  const text = elem ? elem.innerText : '';
  navigator.clipboard.writeText(text).then(() => {
    showToast("Invitation wording copied to clipboard!", "success");
  });
});

// Export / Print Plan
document.getElementById('btnPrintPlan')?.addEventListener('click', () => {
  const ev = getCurrentEvent();
  const summary = calculateBudgetSummary(ev.budget, ev.expenses);

  const preview = document.getElementById('printPlanContent');
  const previewHTML = `
    <div style="border-bottom: 2px solid var(--accent-gold); padding-bottom: 1rem; margin-bottom: 1.25rem;">
      <h2 style="font-size: 1.6rem; color: #fff;">${ev.name}</h2>
      <div style="color: var(--text-secondary);">Venue: <strong>${ev.venue}</strong> | Date: <strong>${ev.date}</strong> | Status: <strong>${ev.status.toUpperCase()}</strong></div>
    </div>

    <h3 style="color: var(--text-gold); font-size: 1.1rem; margin-bottom: 0.5rem;">✨ Theme & Vision</h3>
    <p style="margin-bottom: 1.25rem;">${ev.theme.title} — ${ev.theme.decor}</p>

    <h3 style="color: var(--text-gold); font-size: 1.1rem; margin-bottom: 0.5rem;">💵 Budget Summary</h3>
    <p style="margin-bottom: 1.25rem;">Total Budget: <strong>${formatCurrency(ev.budget)}</strong> | Allocated Expenses: <strong>${formatCurrency(summary.totalSpent)}</strong> | Remaining: <strong>${formatCurrency(summary.remainingBudget)}</strong></p>

    <h3 style="color: var(--text-gold); font-size: 1.1rem; margin-bottom: 0.5rem;">⏱️ Run-of-Show Day Timeline</h3>
    <ul style="margin-bottom: 1.25rem; padding-left: 1.2rem;">
      ${ev.timeline.map(t => `<li><strong>${t.start} - ${t.end}</strong>: ${t.title} (<em>${t.location}</em>)</li>`).join('')}
    </ul>

    <h3 style="color: var(--text-gold); font-size: 1.1rem; margin-bottom: 0.5rem;">👥 Guest List (${ev.guests.length} Invited)</h3>
    <p>Confirmed Attendees: <strong>${ev.guests.filter(g => g.status === 'attending').length}</strong></p>
  `;
  updateInnerHTMLIfChanged(preview, previewHTML);
  openModal('modalPrintPlan');
});

document.getElementById('btnDoPrint')?.addEventListener('click', () => {
  window.print();
});

// Export CSV
document.getElementById('btnExportGuestsCSV')?.addEventListener('click', () => {
  const ev = getCurrentEvent();
  let csv = "Name,Email,PlusOnes,Dietary,Status,Token\n";
  ev.guests.forEach(g => {
    csv += `"${g.name}","${g.email || ''}",${g.plusOnes},"${g.dietary || ''}","${g.status}","${g.token}"\n`;
  });
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${ev.name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_guests.csv`;
  a.click();
  showToast("Guest list exported to CSV.", "success");
});

// Initialize on DOM load
window.addEventListener('DOMContentLoaded', () => {
  renderApp();
  console.log("Festora GenAI Planning Assistant initialized successfully with optimized reactive engine.");
});
