// Dedicated chatbot knowledge base & response engine for RuralEdge

export interface StructuredCard {
  title: string
  code?: string
  subsidyBadge?: string
  eligibility: string
  support: string
  documents: string[]
  nextSteps: string[]
  linkHref?: string
  linkText?: string
}

export interface ChatbotResponse {
  explanation: string
  headings?: string[]
  bulletPoints?: string[]
  numbers?: { label: string; value: string }[]
  steps?: string[]
  card?: StructuredCard
  isUnverified?: boolean
}

export const SUGGESTED_ACTIONS = [
  { label: 'Find a government scheme', query: 'Find a government scheme for my business' },
  { label: 'Business guidance', query: 'Give me basic business guidance for starting a rural venture' },
  { label: 'Loan & financing', query: 'What loan and financing options are available?' },
  { label: 'Subsidy information', query: 'What subsidy options can I get?' },
  { label: 'Eligibility help', query: 'How do I know if I am eligible for schemes?' },
]

export const QUICK_QUESTIONS = [
  'What schemes are available for dairy farming?',
  'Can I get a loan to start a small business?',
  'What subsidy options are available?',
  'What documents do I need?',
  'How do I know if I am eligible?',
]

export function processChatbotQuery(query: string): ChatbotResponse {
  const q = query.toLowerCase().trim()

  // 1. Dairy Farming / Specific Agri Scheme
  if (q.includes('dairy') || q.includes('dairy farming')) {
    return {
      explanation:
        'Dairy farming is one of the most reliable rural micro-enterprises in India. Here are verified schemes and guidance tailored for rural dairy ventures.',
      bulletPoints: [
        'High local demand for milk, curd, and fresh dairy products.',
        'Requires minimum 0.5 acre plot for shed and fodder storage.',
        'Supports automated milking equipment and stainless steel cooling units.',
      ],
      numbers: [
        { label: 'Expected Setup Cost', value: '₹5.0L – ₹10.0L' },
        { label: 'Max Subsidy (PMEGP)', value: 'Up to 35%' },
        { label: 'Loan Grace Period', value: '3 to 6 Months' },
      ],
      steps: [
        'Identify land & water source in your village.',
        'Prepare project report for cattle shed & livestock procurement.',
        'Apply for PMEGP or RuralEdge Term Loan with Bank Statement.',
      ],
      card: {
        title: 'PMEGP — Dairy Micro-Enterprise Support',
        code: 'PMEGP-RURAL-DAIRY',
        subsidyBadge: '35% Margin Money Subsidy',
        eligibility:
          'Rural entrepreneurs starting new manufacturing, processing, or agri-dairy ventures above 18 years of age.',
        support: 'Bank loan covering up to 90% of total project cost with 15% - 35% government subsidy.',
        documents: [
          'Aadhaar Card & Address Proof',
          'Project Report for Dairy Shed & Livestock',
          'EDP Training Certificate (or KVIC online orientation)',
          'Bank Account Details & Category Certificate (if applicable)',
        ],
        nextSteps: [
          'Register on jan-samarth / KVIC portal.',
          'Submit project report to District Industries Centre (DIC).',
          'Sanction letter issued for bank loan disbursement.',
        ],
        linkHref: '/schemes',
        linkText: 'Learn More in Schemes Engine',
      },
    }
  }

  // 2. Government Schemes Inquiry
  if (q.includes('scheme') || q.includes('find a government scheme') || q.includes('pmegp') || q.includes('mudra')) {
    return {
      explanation:
        'RuralEdge verifies key central and state government schemes designed to fund rural entrepreneurs.',
      bulletPoints: [
        'PMEGP: Credit-linked subsidy up to 35% for rural projects up to ₹25 Lakhs.',
        'MUDRA Kishore: Collateral-free loans up to ₹5 Lakhs for working capital.',
        'RuralEdge Micro Finance: Low 6.5% interest rate for starter micro-projects.',
      ],
      numbers: [
        { label: 'Max PMEGP Support', value: '₹25,00,000' },
        { label: 'MUDRA Cap', value: '₹5,00,000' },
        { label: 'Micro Interest', value: '6.5% p.a.' },
      ],
      card: {
        title: 'Prime Minister Employment Generation Programme (PMEGP)',
        code: 'PMEGP-RURAL',
        subsidyBadge: 'Government Credit Subsidy',
        eligibility: 'Individuals above 18 years, SHGs, and Co-operative societies starting rural projects.',
        support: '15% to 35% subsidy on project capital depending on applicant category and location.',
        documents: [
          'Aadhaar Card & PAN Card',
          'Detailed Business Project Report (DPR)',
          'Educational Qualification Certificate (Class 8th pass for projects above ₹10L)',
          'Category / Special Status Certificate',
        ],
        nextSteps: [
          'Prepare your detailed project report using RuralEdge templates.',
          'Apply online at KVIC Official Portal.',
          'District Task Force Committee (DTFC) reviews application.',
        ],
        linkHref: '/schemes',
        linkText: 'View All Schemes',
      },
    }
  }

  // 3. Loans & Financing
  if (q.includes('loan') || q.includes('financing') || q.includes('borrow') || q.includes('capital') || q.includes('term loan')) {
    return {
      explanation:
        'Getting loan approval for a rural business depends on project cost, margin contribution, and repayment capacity.',
      bulletPoints: [
        'Micro Finance: Ideal for initial capital up to ₹1.4L with 6.5% interest rate.',
        'Term Loans: Suitable for larger setups (₹1.4L – ₹50L) with up to 7-year repayment tenure.',
        'Moratorium Period: Grace period of 3 to 6 months before principal repayment starts.',
      ],
      numbers: [
        { label: 'Margin Required', value: '10% – 15%' },
        { label: 'Term Loan Rate', value: '8.0% – 8.5%' },
        { label: 'Repayment Tenure', value: '3 to 7 Years' },
      ],
      steps: [
        'Calculate total project cost and your personal margin money contribution.',
        'Check loan repayment EMI using RuralEdge Loan Calculator.',
        'Submit Bank Statement & Aadhaar to your local bank branch or JanSamarth portal.',
      ],
      card: {
        title: 'RuralEdge Business Term Loan',
        code: 'RURAL-TERM-80',
        subsidyBadge: '6-Month Moratorium Included',
        eligibility: 'Rural micro-entrepreneurs with verified business viability plan.',
        support: '90% project cost coverage with flexible monthly or quarterly repayment schedule.',
        documents: [
          'Aadhaar & Address Verification',
          '6-Month Savings / Bank Account Statement',
          'RuralEdge Viability & Cashflow Report',
        ],
        nextSteps: [
          'Use RuralEdge Loan Calculator to adjust tenure.',
          'Generate project report.',
          'Visit nearest partner bank branch.',
        ],
        linkHref: '/finance',
        linkText: 'Calculate Loan Repayment',
      },
    }
  }

  // 4. Subsidy Information
  if (q.includes('subsidy') || q.includes('subsidies') || q.includes('margin money')) {
    return {
      explanation:
        'Subsidies reduce the net amount you have to repay to the bank. Under government schemes, subsidies are credited as "Margin Money".',
      bulletPoints: [
        'Rural General Category: 25% subsidy of total project cost.',
        'Rural Special Category (SC/ST/OBC/Women/Ex-Servicemen): 35% subsidy.',
        'Subsidy is kept in a locked bank account for 3 years before adjustment.',
      ],
      numbers: [
        { label: 'General Rural Subsidy', value: '25%' },
        { label: 'Special Rural Subsidy', value: '35%' },
        { label: 'Lock-in Period', value: '3 Years' },
      ],
      steps: [
        'Determine your applicant category and location classification.',
        'Apply for credit-linked subsidy scheme through KVIC / DIC.',
        'Bank disburses loan; government releases subsidy to bank.',
      ],
      card: {
        title: 'PMEGP Margin Money Subsidy Structure',
        code: 'SUBSIDY-KVIC',
        subsidyBadge: 'Up to 35% Non-refundable Subsidy',
        eligibility: 'New rural micro-enterprises with maximum project cost of ₹50 Lakhs (Manufacturing) or ₹20 Lakhs (Service).',
        support: 'Government pays 25%-35% of project cost directly to loan account.',
        documents: [
          'Identity & Category Proof',
          'Rural Area Verification Certificate',
          'Detailed Project Report',
        ],
        nextSteps: [
          'Verify category documents.',
          'Submit online application.',
          'Attend short EDP training post-sanction.',
        ],
        linkHref: '/schemes',
        linkText: 'Check Subsidy Details',
      },
    }
  }

  // 5. Documents Required
  if (q.includes('document') || q.includes('paperwork') || q.includes('proof')) {
    return {
      explanation:
        'Having complete documentation speeds up loan approval from weeks to days. Here is the standard checklist required for rural loans and government schemes.',
      bulletPoints: [
        'Identity Proof: Aadhaar Card & PAN Card.',
        'Address & Residence: Voter ID, Ration Card, or Village Sarpanch Letter.',
        'Financial Record: 6-month Bank Passbook / Bank Statement.',
        'Project Plan: Detailed Business Project Report (DPR).',
      ],
      numbers: [
        { label: 'Core Documents', value: '4 Essential Files' },
        { label: 'Approval Speed', value: '7 – 15 Days' },
      ],
      steps: [
        'Gather Aadhaar, PAN, and Bank Statement.',
        'Obtain land lease or ownership proof for business location.',
        'Generate project report using RuralEdge tool.',
      ],
      card: {
        title: 'Standard Rural Loan Document Checklist',
        code: 'DOC-CHECKLIST-v1',
        subsidyBadge: 'Verified Checklist',
        eligibility: 'Applicable for all PMEGP, MUDRA, and Bank Term Loan applications.',
        support: 'Ensures fast-track processing without application rejections.',
        documents: [
          'Aadhaar Card & Passport Size Photographs',
          'PAN Card / Form 60',
          'Proof of Rural Business Premises (Rent Agreement / Land Document)',
          'Bank Account Passbook (last 6 months transaction history)',
          'Business Viability / Project Cost Estimate',
        ],
        nextSteps: [
          'Verify all document names match Aadhaar exactly.',
          'Keep self-attested photocopies ready.',
          'Upload digital copies on JanSamarth or present to bank manager.',
        ],
        linkHref: '/dashboard',
        linkText: 'Manage Document Checklist',
      },
    }
  }

  // 6. Eligibility Help
  if (q.includes('eligible') || q.includes('eligibility')) {
    return {
      explanation:
        'Scheme eligibility is determined by applicant age, project location, category, and proposed business activity.',
      bulletPoints: [
        'Age: Must be 18 years or older.',
        'Location: Must be situated within designated rural/village boundaries.',
        'Education: 8th Pass required only for manufacturing projects above ₹10L or service above ₹5L.',
        'New Enterprise: Subsidy applies primarily to new business startups.',
      ],
      numbers: [
        { label: 'Min Age', value: '18 Years' },
        { label: 'Location Requirement', value: 'Rural / Village' },
        { label: 'Owner Contribution', value: '5% – 10%' },
      ],
      steps: [
        'Verify your age and residence status in village.',
        'Choose eligible sector (Dairy, Poultry, Food Processing, Retail, Services).',
        'Check project cost against scheme ceiling.',
      ],
    }
  }

  // 7. General Business Guidance
  if (q.includes('business') || q.includes('start') || q.includes('grow') || q.includes('guidance')) {
    return {
      explanation:
        'Starting a successful rural enterprise requires understanding your local 5 km market, managing cash flow, and choosing low-risk business models.',
      bulletPoints: [
        'Focus on daily necessity goods/services (Milk, Kirana, Poultry, Grain Milling).',
        'Keep initial fixed overheads low by utilizing local resources.',
        'Maintain a cash margin cushion of at least 2 months of operational costs.',
      ],
      numbers: [
        { label: 'Target Customer Radius', value: '5 km Village Radius' },
        { label: 'Recommended Margin Cushion', value: '₹15,000 – ₹25,000' },
      ],
      steps: [
        'Identify top demand product in your village.',
        'Estimate total setup capital and monthly operating expense.',
        'Secure government scheme subsidy or micro-loan funding.',
      ],
    }
  }

  // 8. UNVERIFIED / UNKNOWN QUERY FALLBACK
  return {
    explanation:
      "I'm not able to verify that information right now. Try asking me about government schemes, loans, subsidies, eligibility or rural business guidance.",
    isUnverified: true,
  }
}
