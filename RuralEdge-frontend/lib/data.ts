// Centralized mock-data + deterministic financial calculations for the RuralEdge demo.
// All monetary values are illustrative demo figures unless a real calculation is noted.

export type BusinessType =
  | 'dairy'
  | 'poultry'
  | 'farming'
  | 'retail'
  | 'textiles'
  | 'food'
  | 'handicrafts'
  | 'services'
  | 'other'

export type BusinessGoal =
  | 'new'
  | 'expand'
  | 'equipment'
  | 'production'
  | 'outlet'
  | 'distribution'

export interface BusinessProfile {
  ownerName: string
  type: BusinessType
  typeLabel: string
  village: string
  block: string
  district: string
  state: string
  margin: number
  goal: BusinessGoal
  goalLabel: string
}

export const DEFAULT_PROFILE: BusinessProfile = {
  ownerName: 'Ravi Kumar',
  type: 'dairy',
  typeLabel: 'Dairy Enterprise',
  village: 'Hosahalli',
  block: 'Channapatna',
  district: 'Ramanagara',
  state: 'Karnataka',
  margin: 100000,
  goal: 'new',
  goalLabel: 'Start a new business',
}

export const BUSINESS_TYPES: {
  id: BusinessType
  label: string
  hint: string
}[] = [
  { id: 'dairy', label: 'Dairy', hint: 'Milk & dairy products' },
  { id: 'poultry', label: 'Poultry', hint: 'Eggs & poultry farming' },
  { id: 'farming', label: 'Farming', hint: 'Crops & agriculture' },
  { id: 'retail', label: 'Retail', hint: 'Kirana & general store' },
  { id: 'textiles', label: 'Textiles', hint: 'Weaving & fabric work' },
  { id: 'food', label: 'Food Processing', hint: 'Packaged & processed food' },
  { id: 'handicrafts', label: 'Handicrafts', hint: 'Artisan & craft work' },
  { id: 'services', label: 'Services', hint: 'Local service business' },
  { id: 'other', label: 'Other', hint: 'Something else' },
]

export const BUSINESS_GOALS: { id: BusinessGoal; label: string }[] = [
  { id: 'new', label: 'Start a new business' },
  { id: 'expand', label: 'Expand an existing business' },
  { id: 'equipment', label: 'Buy equipment' },
  { id: 'production', label: 'Increase production' },
  { id: 'outlet', label: 'Open a new outlet' },
  { id: 'distribution', label: 'Improve distribution' },
]

export const LANGUAGES = [
  { code: 'en', label: 'English', native: 'English' },
  { code: 'hi', label: 'Hindi', native: 'हिंदी' },
  { code: 'kn', label: 'Kannada', native: 'ಕನ್ನಡ' },
  { code: 'ta', label: 'Tamil', native: 'தமிழ்' },
  { code: 'te', label: 'Telugu', native: 'తెలుగు' },
  { code: 'mr', label: 'Marathi', native: 'मराठी' },
  { code: 'bn', label: 'Bengali', native: 'বাংলা' },
]

// ---------- Currency / number formatting (Indian system) ----------

const inr = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 0,
})

export function formatINR(value: number): string {
  return inr.format(Math.round(value))
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-IN').format(Math.round(value))
}

/** Compact Indian phrasing e.g. ₹9.00 L, ₹1.4 Cr */
export function formatCompactINR(value: number): string {
  if (value >= 10000000) return `₹${(value / 10000000).toFixed(2)} Cr`
  if (value >= 100000) return `₹${(value / 100000).toFixed(2)} L`
  return formatINR(value)
}

// ---------- Financing schemes (challenge rules) ----------

export interface Scheme {
  id: 'micro' | 'term'
  name: string
  tagline: string
  minCost: number
  maxCost: number
  fundingPct: number
  maxLoan: number
  interest: number
  tenureYears: number
  moratoriumMonths: number
  audience: string
}

export const SCHEMES: Scheme[] = [
  {
    id: 'micro',
    name: 'Micro Finance Scheme',
    tagline: 'Designed for small, first-step business projects',
    minCost: 0,
    maxCost: 140000,
    fundingPct: 0.9,
    maxLoan: 125000,
    interest: 6.5,
    tenureYears: 3,
    moratoriumMonths: 3,
    audience: 'New and very small micro-enterprises',
  },
  {
    id: 'term',
    name: 'Term Loan Scheme',
    tagline: 'Designed for larger business projects',
    minCost: 140000,
    maxCost: 5000000,
    fundingPct: 0.9,
    maxLoan: 4500000,
    interest: 8,
    tenureYears: 7,
    moratoriumMonths: 6,
    audience: 'Growing enterprises with larger capital needs',
  },
]

export interface DetailedScheme {
  id: string
  name: string
  code: string
  matchPct: number
  tagline: string
  maxFinancing: number
  contributionPct: number
  interestRate: number
  tenureYears: number
  status: 'Highly suitable' | 'Suitable' | 'Moderate match'
  eligibilityRationale: string
  keyBenefits: string[]
  requiredDocs: string[]
}

export const DETAILED_SCHEMES: DetailedScheme[] = [
  {
    id: 'pmegp',
    name: 'PMEGP (Prime Minister Employment Generation)',
    code: 'PMEGP-RURAL',
    matchPct: 94,
    tagline: 'Govt credit-linked subsidy scheme for rural micro-enterprises',
    maxFinancing: 2500000,
    contributionPct: 10,
    interestRate: 8.5,
    tenureYears: 7,
    status: 'Highly suitable',
    eligibilityRationale:
      'You match this scheme because your proposed business falls within the supported rural category and your estimated project cost fits the financing range.',
    keyBenefits: [
      'Up to 35% margin money subsidy for rural applicants',
      'No collateral required for loans up to ₹10 Lakhs',
      'Dedicated mentoring support via KVIC / DIC',
    ],
    requiredDocs: ['Aadhaar Card', 'Project Report', 'EDP Training Certificate', 'Caste/Category Cert (if applicable)'],
  },
  {
    id: 'term-loan',
    name: 'RuralEdge Term Loan Scheme',
    code: 'GTL-SERIES-A',
    matchPct: 91,
    tagline: 'Long-term business capital funding with 6-month moratorium',
    maxFinancing: 4500000,
    contributionPct: 10,
    interestRate: 8.0,
    tenureYears: 7,
    status: 'Highly suitable',
    eligibilityRationale:
      'Ideal for your ₹8.5L dairy project. Gives you 6 months grace period before principal repayment begins.',
    keyBenefits: [
      '90% project cost coverage',
      '6-month moratorium on principal repayment',
      'Flexible monthly or quarterly repayment plans',
    ],
    requiredDocs: ['Aadhaar Card', '6-Month Bank Statement', 'RuralEdge Business Viability Assessment'],
  },
  {
    id: 'mudra-kishore',
    name: 'MUDRA Kishore Loan',
    code: 'PMMY-KISHORE',
    matchPct: 86,
    tagline: 'Collateral-free loan for establishing rural ventures',
    maxFinancing: 500000,
    contributionPct: 15,
    interestRate: 8.5,
    tenureYears: 5,
    status: 'Suitable',
    eligibilityRationale:
      'Fits micro-ventures needing quick capital with minimal documentation under Pradhan Mantri MUDRA Yojana.',
    keyBenefits: [
      'Zero collateral needed',
      'Fast-track approval within 7 working days',
      'Includes MUDRA card for working capital withdrawals',
    ],
    requiredDocs: ['Aadhaar Card', 'Address Proof', 'Business Quotation / Invoice'],
  },
  {
    id: 'micro-finance',
    name: 'RuralEdge Micro Finance Scheme',
    code: 'GMF-STARTER',
    matchPct: 89,
    tagline: 'Low-interest starter capital for small village enterprises',
    maxFinancing: 125000,
    contributionPct: 10,
    interestRate: 6.5,
    tenureYears: 3,
    status: 'Highly suitable',
    eligibilityRationale:
      'Provides quick low-interest seed capital for equipment purchases and preliminary operational expenses.',
    keyBenefits: [
      'Low 6.5% interest rate',
      'Simple 3-step verification process',
      '3-month grace period before repayment',
    ],
    requiredDocs: ['Aadhaar Card', 'Village Resident Verification Letter'],
  },
]

export interface RecommendationProfile {
  title: string
  category: string
  matchScore: number
  description: string
  demandScore: number
  demandLabel: string
  investmentAmount: number
  fundingAmount: number
  competitionLevel: string
  whyWeRecommend: string[]
  keyHighlights: { label: string; value: string }[]
}

export const MAIN_RECOMMENDATION: RecommendationProfile = {
  title: 'Dairy Farming & Milk Collection Enterprise',
  category: 'Livestock & Agriculture',
  matchScore: 87,
  description:
    'Based on your location, available resources, starting capital and local market conditions.',
  demandScore: 92,
  demandLabel: 'High local demand',
  investmentAmount: 850000,
  fundingAmount: 765000,
  competitionLevel: 'Moderate',
  whyWeRecommend: [
    'Strong local demand (3,240 households & local institution buyers nearby)',
    'Suitable local resources (existing land parcel and fresh water access)',
    'Fits your available capital (₹85,000 contribution unlocks ₹7.65L loan)',
    'Financing options available (94% eligibility for PMEGP & Term Loan)',
    'Moderate competition with high margin potential on processed curd/paneer',
  ],
  keyHighlights: [
    { label: 'Monthly Net Profit', value: '₹24,500' },
    { label: 'Break-even Period', value: '11 months' },
    { label: 'Market Reach', value: '3,240 Households' },
    { label: 'Loan Scheme', value: 'PMEGP / Term Loan' },
  ],
}

export const ALTERNATIVE_RECOMMENDATIONS: RecommendationProfile[] = [
  {
    title: 'Poultry Farming (Layer & Broiler)',
    category: 'Livestock',
    matchScore: 81,
    description: 'High egg demand in local weekly markets with quick 6-week harvest cycles.',
    demandScore: 88,
    demandLabel: 'Very high demand',
    investmentAmount: 450000,
    fundingAmount: 405000,
    competitionLevel: 'Low to Moderate',
    whyWeRecommend: [
      'Short cash turnover cycle (6 weeks)',
      'Stable demand from local eateries & weekly santhe',
      'Low initial land requirement',
    ],
    keyHighlights: [
      { label: 'Monthly Net Profit', value: '₹18,200' },
      { label: 'Break-even Period', value: '8 months' },
      { label: 'Market Reach', value: '84 Local Shops' },
      { label: 'Loan Scheme', value: 'MUDRA Kishore' },
    ],
  },
  {
    title: 'Flour Mill & Food Processing Hub',
    category: 'Food Processing',
    matchScore: 76,
    description: 'Processing grain, spices, and pulses for nearby village clusters.',
    demandScore: 84,
    demandLabel: 'Consistent demand',
    investmentAmount: 320000,
    fundingAmount: 288000,
    competitionLevel: 'Moderate',
    whyWeRecommend: [
      'Year-round essential service',
      'High profit margin on custom spice grinding',
      'Requires minimal specialized labor',
    ],
    keyHighlights: [
      { label: 'Monthly Net Profit', value: '₹15,000' },
      { label: 'Break-even Period', value: '9 months' },
      { label: 'Market Reach', value: '5 Villages' },
      { label: 'Loan Scheme', value: 'Micro Finance Scheme' },
    ],
  },
  {
    title: 'Organic Fertilizer & Bio-Compost Unit',
    category: 'Agri-Services',
    matchScore: 72,
    description: 'Converting farm waste into premium organic bio-fertilizer for local farmers.',
    demandScore: 78,
    demandLabel: 'Growing demand',
    investmentAmount: 200000,
    fundingAmount: 180000,
    competitionLevel: 'Low',
    whyWeRecommend: [
      'Low raw material input cost',
      'Government incentives for eco-friendly farming',
      'Scalable model to neighboring blocks',
    ],
    keyHighlights: [
      { label: 'Monthly Net Profit', value: '₹12,500' },
      { label: 'Break-even Period', value: '6 months' },
      { label: 'Market Reach', value: '120 Farmers' },
      { label: 'Loan Scheme', value: 'PMEGP Subsidy' },
    ],
  },
]

export interface DocumentItem {
  id: string
  title: string
  description: string
  requiredFor: string
  isDone: boolean
}

export const DOCUMENT_CHECKLIST: DocumentItem[] = [
  {
    id: 'doc-aadhaar',
    title: 'Aadhaar Card / National ID',
    description: 'Identity verification & address match for loan sanction',
    requiredFor: 'All Schemes',
    isDone: true,
  },
  {
    id: 'doc-address',
    title: 'Address Proof / Ration Card',
    description: 'Proof of residence in target village / rural block',
    requiredFor: 'PMEGP & Term Loan',
    isDone: true,
  },
  {
    id: 'doc-bank',
    title: 'Bank Account Statement (6 Months)',
    description: 'Savings or current account statement showing transaction history',
    requiredFor: 'Bank Loan Disbursement',
    isDone: false,
  },
  {
    id: 'doc-plan',
    title: 'RuralEdge Detailed Business Plan Report',
    description: 'AI-generated financial report with viability index & revenue model',
    requiredFor: 'Scheme Matching & Approval',
    isDone: false,
  },
  {
    id: 'doc-land',
    title: 'Land Record / Lease Agreement / NOC',
    description: 'Property ownership (7/12 extract) or 3-year lease agreement for unit',
    requiredFor: 'Dairy & Agri Infrastructure',
    isDone: false,
  },
]

export interface JourneyStep {
  id: number
  title: string
  subtitle: string
  status: 'completed' | 'current' | 'upcoming'
}

export const JOURNEY_STEPS: JourneyStep[] = [
  { id: 1, title: 'Choose Business', subtitle: 'Dairy Farming (87% Match)', status: 'completed' },
  { id: 2, title: 'Find Financing', subtitle: '₹7.65L Loan Planned', status: 'completed' },
  { id: 3, title: 'Match Government Scheme', subtitle: 'PMEGP & Term Loan Eligible', status: 'completed' },
  { id: 4, title: 'Prepare Documents', subtitle: '2 of 5 documents ready', status: 'current' },
  { id: 5, title: 'Apply for Financing', subtitle: 'Submit to DIC / Bank Officer', status: 'upcoming' },
  { id: 6, title: 'Start Business', subtitle: 'Procure livestock & setup space', status: 'upcoming' },
]

export const ONBOARDING_RESOURCES = [
  { id: 'land', label: 'Land', icon: '🌾', description: 'Agricultural or commercial plot' },
  { id: 'livestock', label: 'Livestock', icon: '🐄', description: 'Cattle, poultry, or shed space' },
  { id: 'water', label: 'Water Access', icon: '💧', description: 'Borewell, river, or water source' },
  { id: 'workers', label: 'Workers', icon: '👷', description: 'Family or hired local labor' },
  { id: 'shop', label: 'Shop / Workspace', icon: '🏪', description: 'Roadside counter or shed' },
  { id: 'equipment', label: 'Equipment', icon: '🚜', description: 'Tractor, machinery, or tools' },
]

export const ONBOARDING_INTERESTS = [
  { id: 'farming', label: 'Agriculture', icon: '🌱', description: 'Crops, horticulture, organic' },
  { id: 'dairy', label: 'Dairy', icon: '🐄', description: 'Milk collection, curd, paneer' },
  { id: 'poultry', label: 'Poultry', icon: '🐔', description: 'Eggs & broiler farming' },
  { id: 'food', label: 'Food Processing', icon: '🍯', description: 'Flour mill, pickles, spices' },
  { id: 'retail', label: 'Retail Store', icon: '🏪', description: 'Kirana, general store' },
  { id: 'manufacturing', label: 'Manufacturing', icon: '🛠️', description: 'Eco-bricks, craft, textiles' },
  { id: 'digital', label: 'Digital Services', icon: '💻', description: 'CSC center, cyber cafe, xerox' },
  { id: 'recycling', label: 'Recycling & Bio', icon: '♻️', description: 'Compost, plastic collection' },
]

export interface FinancePlan {
  margin: number
  projectCost: number
  loan: number
  scheme: Scheme
  capApplied: boolean
  aboveMax: boolean
  emi: number
  totalInterest: number
  totalPayable: number
  monthlyDuringMoratorium: number
  appliedMoratoriumMonths: number
  interestTreatment: 'accrue' | 'pay_separately'
}

// EMI for an amortising loan
function emiFor(principal: number, annualRate: number, months: number): number {
  const r = annualRate / 12 / 100
  if (r === 0) return principal / months
  const f = Math.pow(1 + r, months)
  return (principal * r * f) / (f - 1)
}

/**
 * Deterministic financing calculation from available margin money.
 * Project Cost = margin / 10%, Loan = 90% of project cost, subject to scheme caps.
 */
export function computeFinance(
  margin: number,
  customMoratorium: number | null = null,
  interestTreatment: 'accrue' | 'pay_separately' = 'pay_separately'
): FinancePlan {
  const safeMargin = Math.max(0, margin || 0)
  const rawProjectCost = safeMargin / 0.1
  const aboveMax = rawProjectCost > 5000000

  const scheme =
    rawProjectCost <= 140000 ? SCHEMES[0] : SCHEMES[1]

  const projectCost = Math.min(rawProjectCost, scheme.maxCost)
  const rawLoan = projectCost * scheme.fundingPct
  const loan = Math.min(rawLoan, scheme.maxLoan)
  const capApplied = rawLoan > scheme.maxLoan || rawProjectCost > scheme.maxCost

  const appliedMoratoriumMonths = customMoratorium !== null ? customMoratorium : scheme.moratoriumMonths
  const repaymentMonths = scheme.tenureYears * 12 - appliedMoratoriumMonths

  let emi = 0
  let totalPayable = 0
  let totalInterest = 0
  let monthlyDuringMoratorium = 0

  const monthlyRate = scheme.interest / 12 / 100

  if (interestTreatment === 'accrue') {
    let accruedBalance = loan
    for (let i = 0; i < appliedMoratoriumMonths; i++) {
      accruedBalance += accruedBalance * monthlyRate
    }
    
    emi = repaymentMonths > 0 ? emiFor(accruedBalance, scheme.interest, repaymentMonths) : 0
    totalPayable = emi * repaymentMonths
    totalInterest = totalPayable - loan
    monthlyDuringMoratorium = 0
  } else {
    emi = repaymentMonths > 0 ? emiFor(loan, scheme.interest, repaymentMonths) : 0
    monthlyDuringMoratorium = loan * monthlyRate
    const moratoriumInterest = monthlyDuringMoratorium * appliedMoratoriumMonths
    totalPayable = emi * repaymentMonths + moratoriumInterest
    totalInterest = totalPayable - loan
  }

  return {
    margin: safeMargin,
    projectCost,
    loan,
    scheme,
    capApplied,
    aboveMax,
    emi,
    totalInterest,
    totalPayable,
    monthlyDuringMoratorium,
    appliedMoratoriumMonths,
    interestTreatment
  }
}

export interface RepaymentRow {
  period: number
  label: string
  principal: number
  interest: number
  balance: number
  isMoratorium: boolean
}

export function buildRepaymentSchedule(
  plan: FinancePlan,
  mode: 'monthly' | 'quarterly',
): RepaymentRow[] {
  const { loan, scheme, emi, appliedMoratoriumMonths, interestTreatment } = plan
  const monthlyRate = scheme.interest / 12 / 100
  const rows: RepaymentRow[] = []
  let balance = loan
  const totalMonths = scheme.tenureYears * 12

  for (let m = 1; m <= totalMonths; m++) {
    const isMoratorium = m <= appliedMoratoriumMonths
    const interest = balance * monthlyRate
    let principal = 0
    
    if (isMoratorium) {
      principal = 0
      if (interestTreatment === 'accrue') {
        balance += interest
      }
    } else {
      principal = Math.min(emi - interest, balance)
      balance = Math.max(0, balance - principal)
    }
    rows.push({
      period: m,
      label: `M${m}`,
      principal,
      interest,
      balance,
      isMoratorium,
    })
  }

  if (mode === 'monthly') return rows.filter((_, i) => i % 3 === 0 || i === rows.length - 1)

  // quarterly aggregation
  const quarterly: RepaymentRow[] = []
  for (let i = 0; i < rows.length; i += 3) {
    const chunk = rows.slice(i, i + 3)
    const last = chunk[chunk.length - 1]
    quarterly.push({
      period: Math.floor(i / 3) + 1,
      label: `Q${Math.floor(i / 3) + 1}`,
      principal: chunk.reduce((s, r) => s + r.principal, 0),
      interest: chunk.reduce((s, r) => s + r.interest, 0),
      balance: last.balance,
      isMoratorium: chunk.some((r) => r.isMoratorium),
    })
  }
  return quarterly
}

// ---------- Dashboard / operating mock data ----------

export const OPERATING = {
  monthlyRevenue: 95000,
  monthlyCost: 70500,
  get monthlyProfit() {
    return this.monthlyRevenue - this.monthlyCost
  },
  get profitMargin() {
    return (this.monthlyProfit / this.monthlyRevenue) * 100
  },
  businessHealth: 82,
  marketOpportunity: 78,
  initialInvestment: 1000000,
  breakEvenMonths: 11,
}

export const REVENUE_TREND = [
  { month: 'Apr', revenue: 72000, expenses: 60000, profit: 12000 },
  { month: 'May', revenue: 78000, expenses: 62000, profit: 16000 },
  { month: 'Jun', revenue: 83000, expenses: 64500, profit: 18500 },
  { month: 'Jul', revenue: 88000, expenses: 67000, profit: 21000 },
  { month: 'Aug', revenue: 92000, expenses: 69000, profit: 23000 },
  { month: 'Sep', revenue: 95000, expenses: 70500, profit: 24500 },
]

export function buildBreakEven(
  investment: number,
  monthlyRevenue: number,
  monthlyCost: number,
): { month: number; cumulative: number; investment: number }[] {
  const net = monthlyRevenue - monthlyCost
  const rows = []
  for (let m = 0; m <= 18; m++) {
    rows.push({
      month: m,
      cumulative: net * m,
      investment,
    })
  }
  return rows
}

export const COST_BREAKDOWN = [
  { name: 'Feed & inputs', value: 34000 },
  { name: 'Labour', value: 15000 },
  { name: 'Transport', value: 9500 },
  { name: 'Utilities', value: 6000 },
  { name: 'Maintenance', value: 6000 },
]

// ---------- Market intelligence mock data ----------

export interface MarketMarker {
  id: string
  name: string
  category: 'competitor' | 'supplier' | 'market' | 'customer'
  label: string
  x: number // percentage within map
  y: number
  distanceKm: number
}

export const MARKET_MARKERS: MarketMarker[] = [
  { id: 'm1', name: 'Ganga Dairy', category: 'competitor', label: 'Dairy', x: 38, y: 42, distanceKm: 2.1 },
  { id: 'm2', name: 'Sri Milk Point', category: 'competitor', label: 'Dairy', x: 62, y: 55, distanceKm: 3.4 },
  { id: 'm3', name: 'Amrit Dairy', category: 'competitor', label: 'Dairy', x: 70, y: 30, distanceKm: 4.8 },
  { id: 'm4', name: 'Village Retail Hub', category: 'competitor', label: 'Dairy corner', x: 48, y: 66, distanceKm: 5.2 },
  { id: 'm5', name: 'Channapatna Dairy', category: 'competitor', label: 'Dairy', x: 30, y: 70, distanceKm: 6.7 },
  { id: 's1', name: 'GreenFeed Supplies', category: 'supplier', label: 'Feed supplier', x: 20, y: 30, distanceKm: 3.0 },
  { id: 's2', name: 'AgriVet Center', category: 'supplier', label: 'Veterinary', x: 80, y: 62, distanceKm: 4.1 },
  { id: 'k1', name: 'Weekly Santhe Market', category: 'market', label: 'Weekly market', x: 55, y: 22, distanceKm: 3.9 },
  { id: 'k2', name: 'Block Collection Point', category: 'market', label: 'Collection', x: 44, y: 34, distanceKm: 1.8 },
  { id: 'c1', name: 'Hosahalli Households', category: 'customer', label: 'Households', x: 50, y: 50, distanceKm: 0.5 },
  { id: 'c2', name: 'Govt. School Hostel', category: 'customer', label: 'Institution', x: 60, y: 44, distanceKm: 2.6 },
  { id: 'c3', name: 'Rural Cafe Cluster', category: 'customer', label: 'Local shops', x: 36, y: 56, distanceKm: 2.9 },
]

export const MARKET_REACH = {
  households: 3240,
  localShops: 84,
  institutionalBuyers: 12,
  distribution: [
    'Direct doorstep delivery',
    'Local retailers',
    'Weekly market (Santhe)',
    'Local collection point',
  ],
}

export const OPPORTUNITY_RADAR = [
  { category: 'Demand', level: 'HIGH', score: 82 },
  { category: 'Competition', level: 'MEDIUM', score: 58 },
  { category: 'Pricing', level: 'HIGH', score: 76 },
  { category: 'Distribution', level: 'MEDIUM', score: 60 },
  { category: 'Seasonality', level: 'MEDIUM', score: 55 },
  { category: 'Supply', level: 'MEDIUM', score: 62 },
]

export const SWOT = {
  strengths: [
    'Strong local customer relationships',
    'Existing agricultural knowledge',
    'Short distribution distance',
  ],
  weaknesses: ['Limited working capital', 'Small production capacity'],
  opportunities: [
    'Growing nearby household demand',
    'Doorstep delivery model',
    'Institutional buyers nearby',
  ],
  threats: [
    'Seasonal demand changes',
    'Feed price fluctuations',
    'Local competition',
  ],
}

export interface RiskItem {
  id: string
  title: string
  level: 'Low' | 'Medium' | 'High'
  why: string
  action: string
}

export const RISKS: RiskItem[] = [
  {
    id: 'r1',
    title: 'Supply Risk',
    level: 'Medium',
    why: 'Feed and inputs depend on suppliers outside the village.',
    action: 'Keep at least two reliable suppliers to avoid shortages.',
  },
  {
    id: 'r2',
    title: 'Seasonal Demand',
    level: 'Medium',
    why: 'Milk demand can dip during certain months of the year.',
    action: 'Build a few institutional buyers for steady off-season sales.',
  },
  {
    id: 'r3',
    title: 'Price Risk',
    level: 'Low',
    why: 'Feed prices can rise, reducing your monthly profit.',
    action: 'Buy feed in planned batches when prices are lower.',
  },
]

export const PRICING = {
  estimatedPrice: 58,
  min: 50,
  max: 68,
  recommendedMin: 55,
  recommendedMax: 62,
  cost: 44,
  purchasingPower: 'Medium',
  competition: 'Moderate',
  strategy:
    'Start slightly below established premium sellers, then increase pricing after building repeat customers.',
  baseVolume: 1600, // litres per month at recommended price
}

// ---------- AI advisor scripted responses ----------

export const ADVISOR_SUGGESTIONS = [
  'Can I afford this loan?',
  'Should I expand now?',
  'Who are my main competitors?',
  'What should I sell?',
  'How can I improve my profit?',
  'Which support schemes should I check?',
]

export const ADVISOR_ANSWERS: { match: string; answer: string }[] = [
  {
    match: 'afford',
    answer:
      'Based on your current monthly surplus of about ₹24,500, your projected cash flow appears sufficient to handle the estimated repayment of your ₹9,00,000 term loan. You have a reasonable safety cushion, but keep at least two months of expenses in reserve before committing.',
  },
  {
    match: 'expand',
    answer:
      'Your business health is strong at 82/100, but before expanding I would first stabilise monthly sales and widen your customer reach. Growing repeat households in your 5 km radius will make an expansion loan much safer to repay.',
  },
  {
    match: 'competitor',
    answer:
      'There are about 5 similar dairy businesses within 7 km. Competition is Moderate. Your advantage is the shortest distance to nearby households, so doorstep delivery is your strongest differentiator against them.',
  },
  {
    match: 'sell',
    answer:
      'Beyond loose milk, consider curd, paneer and buttermilk. These processed products carry higher margins and reduce your dependence on daily fresh-milk demand. Start with curd, which sells well to nearby households.',
  },
  {
    match: 'profit',
    answer:
      'You currently keep about ₹26 of every ₹100 in revenue. To improve profit, lower feed cost by batch-buying, add one higher-margin product like curd, and reduce transport by grouping deliveries. Even a 5% cost reduction adds roughly ₹3,500 monthly profit.',
  },
  {
    match: 'scheme',
    answer:
      'Given your project size of ₹10,00,000 and ₹1,00,000 margin, the Term Loan Scheme (8% p.a., 7 years, 6-month moratorium) is your most relevant financing route. Check the Government Support page for the full conditions.',
  },
]

export function advisorReply(question: string): string {
  const q = question.toLowerCase()
  const found = ADVISOR_ANSWERS.find((a) => q.includes(a.match))
  if (found) return found.answer
  return "I've reviewed your dairy business profile, local market and current financing assumptions. Your monthly profit of about ₹24,500 gives you a stable base. Tell me whether you want to focus on financing, growing sales, or reducing risk, and I'll give you a practical next step."
}
