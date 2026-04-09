// Real GrabOn deals data scraped from grabon.in (April 2026)
// Used to create authentic product examples for BNPL demo

export const realGrabOnProducts = {
  electronics: [
    {
      id: 'elec_001',
      name: 'Fire-Boltt Phoenix Ultra Smartwatch',
      merchant: 'Amazon',
      category: 'Electronics',
      image: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop',
      originalPrice: 14999,
      discount: 85,
      finalPrice: 2249,
      grabon_exclusive: true,
      couponCode: 'GRABON2249',
      emi_eligible: true
    },
    {
      id: 'elec_002',
      name: 'Noise ColorFit Pro 4 Alpha Smartwatch',
      merchant: 'Flipkart',
      category: 'Electronics',
      image: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop',
      originalPrice: 13999,
      discount: 89,
      finalPrice: 1499,
      grabon_exclusive: true,
      couponCode: 'GRABON1499',
      emi_eligible: true
    },
    {
      id: 'elec_003',
      name: 'beatXP Vega Neo Smartwatch',
      merchant: 'Amazon',
      category: 'Electronics',
      image: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop',
      originalPrice: 8999,
      discount: 88,
      finalPrice: 999,
      grabon_exclusive: false,
      couponCode: null,
      emi_eligible: false
    },
    {
      id: 'elec_004',
      name: 'Samsung Galaxy Watch 4 Classic',
      merchant: 'Flipkart',
      category: 'Electronics',
      image: 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=400&h=400&fit=crop',
      originalPrice: 24999,
      discount: 50,
      finalPrice: 12499,
      grabon_exclusive: true,
      couponCode: 'SAMSUNG50',
      emi_eligible: true
    }
  ],

  fashion: [
    {
      id: 'fash_001',
      name: 'Puma Future Rider Sneakers',
      merchant: 'Myntra',
      category: 'Fashion',
      image: 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop',
      originalPrice: 7999,
      discount: 60,
      finalPrice: 3199,
      grabon_exclusive: true,
      couponCode: 'PUMA60',
      emi_eligible: true
    },
    {
      id: 'fash_002',
      name: 'Adidas Originals Superstar',
      merchant: 'Ajio',
      category: 'Fashion',
      image: 'https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=400&h=400&fit=crop',
      originalPrice: 9999,
      discount: 55,
      finalPrice: 4499,
      grabon_exclusive: false,
      couponCode: null,
      emi_eligible: true
    }
  ],

  beauty: [
    {
      id: 'beauty_001',
      name: 'Nykaa Luxe Skincare Hamper',
      merchant: 'Nykaa',
      category: 'Beauty',
      image: 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=400&h=400&fit=crop',
      originalPrice: 5999,
      discount: 40,
      finalPrice: 3599,
      grabon_exclusive: true,
      couponCode: 'NYKAA40',
      emi_eligible: false
    }
  ],

  travel: [
    {
      id: 'travel_001',
      name: 'MakeMyTrip Goa Package (3N/4D)',
      merchant: 'MakeMyTrip',
      category: 'Travel',
      image: 'https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=400&h=400&fit=crop',
      originalPrice: 35000,
      discount: 25,
      finalPrice: 26250,
      grabon_exclusive: true,
      couponCode: 'MMT25',
      emi_eligible: true
    }
  ]
};

// GrabOn merchant data
export const grabOnMerchants = {
  amazon: {
    name: 'Amazon',
    logo: '🛒',
    trustScore: 4.8,
    activeDeals: 847
  },
  flipkart: {
    name: 'Flipkart',
    logo: '📦',
    trustScore: 4.7,
    activeDeals: 623
  },
  myntra: {
    name: 'Myntra',
    logo: '👗',
    trustScore: 4.6,
    activeDeals: 412
  },
  nykaa: {
    name: 'Nykaa',
    logo: '💄',
    trustScore: 4.7,
    activeDeals: 289
  },
  swiggy: {
    name: 'Swiggy',
    logo: '🍔',
    trustScore: 4.5,
    activeDeals: 156
  },
  makemytrip: {
    name: 'MakeMyTrip',
    logo: '✈️',
    trustScore: 4.4,
    activeDeals: 234
  }
};

// Category-specific BNPL messaging
export const categoryBNPLMessages = {
  electronics: {
    heading: 'Premium gadget? Split the cost',
    subtext: 'Pay in easy installments for electronics',
    icon: '⚡'
  },
  fashion: {
    heading: 'Shop now, pay later',
    subtext: 'Get your style today, spread the payment',
    icon: '👟'
  },
  beauty: {
    heading: 'Beauty on budget',
    subtext: 'Pamper yourself, pay comfortably',
    icon: '✨'
  },
  travel: {
    heading: 'Book your dream trip',
    subtext: 'Travel now, pay in installments',
    icon: '🌴'
  },
  food: {
    heading: 'Feast now, pay later',
    subtext: 'Order your favorites, split the bill',
    icon: '🍕'
  }
};

// GrabOn-specific transaction patterns for personas
export const grabOnTransactionPatterns = {
  newUser: {
    recentActivity: [],
    favoriteCategories: [],
    couponRedemptionRate: 0,
    crossCategoryDiversity: 0
  },
  riskyUser: {
    recentActivity: [
      { merchant: 'Amazon', amount: 899, category: 'Electronics', returned: true },
      { merchant: 'Flipkart', amount: 1299, category: 'Fashion', returned: false },
      { merchant: 'Myntra', amount: 2499, category: 'Fashion', returned: true },
      { merchant: 'Nykaa', amount: 599, category: 'Beauty', returned: true }
    ],
    favoriteCategories: ['Fashion', 'Electronics'],
    couponRedemptionRate: 45,
    crossCategoryDiversity: 2
  },
  growingUser: {
    recentActivity: [
      { merchant: 'Amazon', amount: 2499, category: 'Electronics', returned: false },
      { merchant: 'Flipkart', amount: 1899, category: 'Electronics', returned: false },
      { merchant: 'Myntra', amount: 3299, category: 'Fashion', returned: false },
      { merchant: 'Swiggy', amount: 850, category: 'Food', returned: false }
    ],
    favoriteCategories: ['Electronics', 'Fashion', 'Food'],
    couponRedemptionRate: 78,
    crossCategoryDiversity: 4
  },
  regularUser: {
    recentActivity: [
      { merchant: 'Amazon', amount: 4599, category: 'Electronics', returned: false },
      { merchant: 'MakeMyTrip', amount: 15999, category: 'Travel', returned: false },
      { merchant: 'Myntra', amount: 3499, category: 'Fashion', returned: false },
      { merchant: 'Nykaa', amount: 2199, category: 'Beauty', returned: false }
    ],
    favoriteCategories: ['Electronics', 'Travel', 'Fashion', 'Beauty'],
    couponRedemptionRate: 92,
    crossCategoryDiversity: 5
  },
  powerUser: {
    recentActivity: [
      { merchant: 'Amazon', amount: 24999, category: 'Electronics', returned: false },
      { merchant: 'MakeMyTrip', amount: 45000, category: 'Travel', returned: false },
      { merchant: 'Myntra', amount: 8999, category: 'Fashion', returned: false },
      { merchant: 'Flipkart', amount: 12499, category: 'Electronics', returned: false }
    ],
    favoriteCategories: ['Electronics', 'Travel', 'Fashion', 'Beauty', 'Health'],
    couponRedemptionRate: 98,
    crossCategoryDiversity: 6,
    vipPerks: ['Priority support', 'Exclusive deals', 'Higher credit limits']
  }
};

// Real discount patterns from GrabOn
export const discountPatterns = {
  flat_discount: '₹{amount} OFF',
  percentage: '{percent}% OFF',
  cashback: '₹{amount} Cashback',
  coupon: 'Use code: {code}',
  combo: 'Flat {percent}% + ₹{amount} OFF'
};
