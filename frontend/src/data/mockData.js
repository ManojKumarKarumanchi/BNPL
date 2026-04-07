// Real GrabOn deal (scraped from grabon.in April 2026)
export const orderData = {
  product: {
    image: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop',
    title: 'Samsung Galaxy Watch 4 Classic',
    merchant: 'Flipkart via GrabOn',
    category: 'Electronics',
    grabon_exclusive: true,
    couponCode: 'SAMSUNG50'
  },
  pricing: {
    subtotal: 24999,
    discount: 12500, // 50% OFF (real GrabOn discount)
    total: 12499,
    grabon_savings: 12500
  },
  deal_stats: {
    people_grabbed: 1247,
    trending: true,
    expires_in: '2 days'
  }
};

export const userEligibility = {
  status: 'approved', // 'approved' | 'not_eligible' | 'new_user' | 'loading'
  creditLimit: 25000,
  reason: 'Based on your frequent purchases, low return rate, and consistent spending over the past 6 months, you\'ve been pre-approved for instant credit.',
  transactionHistory: {
    totalPurchases: 48,
    avgOrderValue: 2850,
    returnRate: 2,
    memberSince: '2024-08-15'
  }
};

export const emiOptions = [
  {
    id: 1,
    duration: 3,
    monthlyPayment: 4200,
    tag: 'No Cost EMI',
    totalAmount: 12600,
    interestRate: 0
  },
  {
    id: 2,
    duration: 6,
    monthlyPayment: 2150,
    tag: 'Best Value',
    totalAmount: 12900,
    interestRate: 3.2
  },
  {
    id: 3,
    duration: 9,
    monthlyPayment: 1500,
    tag: null,
    totalAmount: 13500,
    interestRate: 8
  }
];

export const paymentMethods = [
  { id: 'upi', label: 'UPI', icon: 'QrCodeIcon' },
  { id: 'card', label: 'Card', icon: 'CreditCardIcon' },
  { id: 'netbanking', label: 'Netbanking', icon: 'BuildingLibraryIcon' },
  { id: 'grabcredit', label: 'GrabCredit', icon: 'SparklesIcon', featured: true }
];

// 5 User Personas for Demo
export const userPersonas = {
  // Persona 1: Brand New User (0 transactions)
  newUser: {
    name: 'Rajesh Kumar',
    type: 'New User',
    status: 'new_user',
    creditLimit: 0,
    reason: 'You\'re new to GrabOn! Complete 3-5 purchases over the next few weeks to unlock Pay Later benefits and build your credit profile with us.',
    transactionHistory: {
      totalPurchases: 0,
      avgOrderValue: 0,
      returnRate: 0,
      memberSince: '2026-04-01',
      daysSinceJoined: 6
    },
    emiOptions: null
  },

  // Persona 2: Risky User (Few transactions, high returns, irregular)
  riskyUser: {
    name: 'Priya Sharma',
    type: 'Risky User',
    status: 'not_eligible',
    creditLimit: 0,
    reason: 'Our system detected irregular purchase patterns and a high return rate (18%). We need to see more consistent activity before enabling Pay Later for your account.',
    transactionHistory: {
      totalPurchases: 8,
      avgOrderValue: 950,
      returnRate: 18,
      memberSince: '2025-12-10',
      daysSinceJoined: 118
    },
    emiOptions: null
  },

  // Persona 3: Growing User (Building trust, 25 transactions)
  growingUser: {
    name: 'Amit Patel',
    type: 'Growing User',
    status: 'approved',
    creditLimit: 15000,
    reason: 'Based on your 25 purchases over the past 4 months and low return rate of 4%, you qualify for Pay Later. Your average order value of ₹1,850 and consistent monthly activity show responsible buying behavior.',
    transactionHistory: {
      totalPurchases: 25,
      avgOrderValue: 1850,
      returnRate: 4,
      memberSince: '2025-12-01',
      daysSinceJoined: 127
    },
    emiOptions: [
      { id: 1, duration: 3, monthlyPayment: 4200, tag: 'No Cost EMI', totalAmount: 12600, interestRate: 0 },
      { id: 2, duration: 6, monthlyPayment: 2150, tag: null, totalAmount: 12900, interestRate: 3.2 }
    ]
  },

  // Persona 4: Regular User (48 transactions, solid history)
  regularUser: {
    name: 'Sneha Reddy',
    type: 'Regular User',
    status: 'approved',
    creditLimit: 25000,
    reason: 'Based on your frequent purchases, low return rate of 2%, and consistent spending over the past 6 months, you\'ve been pre-approved for instant credit. Your track record of 48 completed orders demonstrates reliability.',
    transactionHistory: {
      totalPurchases: 48,
      avgOrderValue: 2850,
      returnRate: 2,
      memberSince: '2024-08-15',
      daysSinceJoined: 235
    },
    emiOptions: [
      { id: 1, duration: 3, monthlyPayment: 4200, tag: 'No Cost EMI', totalAmount: 12600, interestRate: 0 },
      { id: 2, duration: 6, monthlyPayment: 2150, tag: 'Best Value', totalAmount: 12900, interestRate: 3.2 },
      { id: 3, duration: 9, monthlyPayment: 1500, tag: null, totalAmount: 13500, interestRate: 8 }
    ]
  },

  // Persona 5: Power User (200+ transactions, VIP status)
  powerUser: {
    name: 'Vikram Malhotra',
    type: 'Power User',
    status: 'approved',
    creditLimit: 50000,
    reason: 'As a valued power user with 237 successful transactions and exceptional spending consistency, you qualify for our highest credit tier. Your 0% return rate, premium average order value of ₹4,200, and 18-month membership make you eligible for exclusive benefits.',
    transactionHistory: {
      totalPurchases: 237,
      avgOrderValue: 4200,
      returnRate: 0,
      memberSince: '2024-10-15',
      daysSinceJoined: 539,
      vipStatus: true
    },
    emiOptions: [
      { id: 1, duration: 3, monthlyPayment: 4200, tag: 'No Cost EMI', totalAmount: 12600, interestRate: 0 },
      { id: 2, duration: 6, monthlyPayment: 2100, tag: 'Best Value', totalAmount: 12600, interestRate: 0 },
      { id: 3, duration: 9, monthlyPayment: 1450, tag: 'VIP Rate', totalAmount: 13050, interestRate: 4.4 },
      { id: 4, duration: 12, monthlyPayment: 1100, tag: null, totalAmount: 13200, interestRate: 5.6 }
    ]
  }
};

// Legacy mock states (keeping for backward compatibility)
export const mockStates = {
  approved: userPersonas.regularUser,
  notEligible: userPersonas.riskyUser,
  newUser: userPersonas.newUser,
  loading: {
    status: 'loading',
    creditLimit: 0,
    reason: '',
    transactionHistory: null
  }
};
