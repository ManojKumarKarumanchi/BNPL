# User Personas Guide

This document describes the 5 sample user personas included in the GrabCredit BNPL checkout demo.

## How to Use

Click on any persona in the **User Personas** panel (top-right) to see how the checkout experience adapts based on their transaction history and eligibility.

---

## 👤 Persona 1: New User (Rajesh Kumar)

**Status:** `new_user` ⚠️

**Profile:**
- **Transactions:** 0
- **Member Since:** Apr 2026 (6 days ago)
- **Return Rate:** 0%
- **Average Order Value:** ₹0

**BNPL Eligibility:** ❌ Not Available

**UI Behavior:**
- Shows "Complete purchases to unlock Pay Later" message
- EMI options are visible but disabled (grayed out)
- Footer CTA shows full price payment only
- Guidance message encourages building purchase history

**Credit Reason:**
> "You're new to GrabOn! Complete 3-5 purchases over the next few weeks to unlock Pay Later benefits and build your credit profile with us."

---

## ⚠️ Persona 2: Risky User (Priya Sharma)

**Status:** `not_eligible` ❌

**Profile:**
- **Transactions:** 8
- **Member Since:** Dec 2025 (118 days ago)
- **Return Rate:** 18% (High)
- **Average Order Value:** ₹950

**BNPL Eligibility:** ❌ Not Available

**UI Behavior:**
- Shows "Pay Later not available" message
- No EMI options displayed
- Footer CTA shows alternative payment methods
- Clear explanation for rejection

**Credit Reason:**
> "Our system detected irregular purchase patterns and a high return rate (18%). We need to see more consistent activity before enabling Pay Later for your account."

**Risk Signals:**
- High return rate (18% vs typical 2-4%)
- Low average order value
- Irregular purchasing pattern

---

## 📈 Persona 3: Growing User (Amit Patel)

**Status:** `approved` ✅ (Limited)

**Profile:**
- **Transactions:** 25
- **Member Since:** Dec 2025 (127 days ago)
- **Return Rate:** 4%
- **Average Order Value:** ₹1,850

**BNPL Eligibility:** ✅ **₹15,000 credit limit**

**UI Behavior:**
- Shows pre-approval message with ₹15,000 limit
- **2 EMI options** available (3 & 6 months)
- Trust badges displayed
- AI reasoning accordion available

**Credit Reason:**
> "Based on your 25 purchases over the past 4 months and low return rate of 4%, you qualify for Pay Later. Your average order value of ₹1,850 and consistent monthly activity show responsible buying behavior."

**EMI Options:**
1. **3 months** - ₹4,200/mo (No Cost EMI)
2. **6 months** - ₹2,150/mo

---

## ✅ Persona 4: Regular User (Sneha Reddy)

**Status:** `approved` ✅

**Profile:**
- **Transactions:** 48
- **Member Since:** Aug 2024 (235 days ago)
- **Return Rate:** 2%
- **Average Order Value:** ₹2,850

**BNPL Eligibility:** ✅ **₹25,000 credit limit**

**UI Behavior:**
- Shows pre-approval message with ₹25,000 limit
- **3 EMI options** available (3, 6, 9 months)
- Full feature access
- Trust badges and security messaging

**Credit Reason:**
> "Based on your frequent purchases, low return rate of 2%, and consistent spending over the past 6 months, you've been pre-approved for instant credit. Your track record of 48 completed orders demonstrates reliability."

**EMI Options:**
1. **3 months** - ₹4,200/mo (No Cost EMI)
2. **6 months** - ₹2,150/mo (Best Value)
3. **9 months** - ₹1,500/mo

---

## ⭐ Persona 5: Power User (Vikram Malhotra)

**Status:** `approved` ✅ (VIP)

**Profile:**
- **Transactions:** 237
- **Member Since:** Oct 2024 (539 days ago)
- **Return Rate:** 0% (Perfect!)
- **Average Order Value:** ₹4,200
- **VIP Status:** Yes

**BNPL Eligibility:** ✅ **₹50,000 credit limit** (Highest tier)

**UI Behavior:**
- Shows pre-approval with highest ₹50,000 limit
- **4 EMI options** including exclusive 12-month plan
- VIP-specific tags and benefits
- Premium user experience

**Credit Reason:**
> "As a valued power user with 237 successful transactions and exceptional spending consistency, you qualify for our highest credit tier. Your 0% return rate, premium average order value of ₹4,200, and 18-month membership make you eligible for exclusive benefits."

**EMI Options:**
1. **3 months** - ₹4,200/mo (No Cost EMI)
2. **6 months** - ₹2,100/mo (Best Value - No Cost!)
3. **9 months** - ₹1,450/mo (VIP Rate - lower interest)
4. **12 months** - ₹1,100/mo (VIP exclusive)

---

## Key Differentiators

| Persona | Transactions | Credit Limit | EMI Options | Return Rate | Status |
|---------|--------------|--------------|-------------|-------------|---------|
| Rajesh (New) | 0 | ₹0 | 0 | 0% | ⚠️ New User |
| Priya (Risky) | 8 | ₹0 | 0 | 18% | ❌ Not Eligible |
| Amit (Growing) | 25 | ₹15,000 | 2 | 4% | ✅ Approved |
| Sneha (Regular) | 48 | ₹25,000 | 3 | 2% | ✅ Approved |
| Vikram (Power) | 237 | ₹50,000 | 4 | 0% | ⭐ VIP |

---

## Testing Scenarios

### Scenario 1: First-Time User Journey
**Start with:** Rajesh Kumar (New User)
- Observe the encouraging message to build history
- Notice disabled EMI options
- See how UI guides user to start transacting

### Scenario 2: Risk Detection
**Start with:** Priya Sharma (Risky User)
- See how high return rate affects eligibility
- Notice the clear rejection messaging
- Understand the trust-building requirements

### Scenario 3: Credit Growth Path
**Compare:** Amit → Sneha → Vikram
- Watch credit limit increase (₹15K → ₹25K → ₹50K)
- See more EMI options unlock
- Notice better rates for power users

### Scenario 4: EMI Selection Flow
**Best persona:** Sneha Reddy or Vikram Malhotra
- Select GrabCredit payment method
- Choose different EMI plans
- Observe footer updates with monthly amount
- Expand "Why you qualify" to see reasoning

---

## AI Reasoning Quality

Each persona has a **unique, data-backed explanation** that references:

✅ Specific transaction count  
✅ Return rate percentage  
✅ Average order value  
✅ Time-based patterns  
✅ Membership duration  

**No generic boilerplate** - every reason is personalized and actionable.

---

## Technical Implementation

### Data Location
`frontend/src/data/mockData.js` → `userPersonas` object

### Switching Personas
```javascript
// In App.jsx
const [currentPersona, setCurrentPersona] = useState('regularUser');
const activePersona = userPersonas[currentPersona];
```

### Persona Structure
```javascript
{
  name: string,
  type: string,
  status: 'approved' | 'not_eligible' | 'new_user',
  creditLimit: number,
  reason: string,
  transactionHistory: {
    totalPurchases: number,
    avgOrderValue: number,
    returnRate: number,
    memberSince: string,
    daysSinceJoined: number
  },
  emiOptions: Array<EMIOption> | null
}
```

---

## Demo Tips

1. **Show progression:** Start with Rajesh → Amit → Sneha → Vikram to demonstrate the credit journey
2. **Highlight differentiation:** Switch between personas to show adaptive UI
3. **Test all states:** Use each persona to validate different code paths
4. **Explain reasoning:** Open the "Why you qualify" section to show AI transparency
5. **Compare EMI options:** Notice how power users get better rates and more options

---

## Production Integration

To connect to a real backend:

1. Replace `userPersonas` with API call
2. Fetch user data from MCP server
3. Run credit scoring engine
4. Return persona-like structure
5. UI adapts automatically - no changes needed!

The frontend is **backend-agnostic** - it just needs a data structure matching the persona format.
