'use client'

import { useRouter } from 'next/navigation'
import { AnimatePresence, motion } from 'framer-motion'
import {
  ArrowLeft,
  ArrowRight,
  Check,
  MapPin,
  Sparkles,
  Wallet,
  Building2,
  HelpCircle,
  Coins,
  CheckCircle2,
} from 'lucide-react'
import { useMemo, useState } from 'react'
import { useBusiness } from '@/components/business-context'
import {
  ONBOARDING_RESOURCES,
  ONBOARDING_INTERESTS,
  computeFinance,
  formatINR,
  formatCompactINR,
} from '@/lib/data'
import { cn } from '@/lib/utils'
import { AnalysisSequence } from '@/components/assessment/analysis-sequence'
import { RecommendationView } from '@/components/assessment/recommendation-view'

const STEPS = [
  'Location',
  'Budget',
  'Resources',
  'Interests',
  'Review',
] as const

const BUDGET_PRESETS = [50000, 100000, 200000, 500000, 1000000]

export function AssessmentFlow() {
  const router = useRouter()
  const { onboarding, updateOnboarding, setHasCompletedAssessment } = useBusiness()
  const [step, setStep] = useState(0)
  const [viewState, setViewState] = useState<'onboarding' | 'analyzing' | 'recommendation'>('onboarding')

  // Calculated finance preview
  const financePreview = useMemo(() => {
    return computeFinance(onboarding.budget / 2)
  }, [onboarding.budget])

  const toggleResource = (id: string) => {
    const current = onboarding.selectedResources
    const next = current.includes(id)
      ? current.filter((r) => r !== id)
      : [...current, id]
    updateOnboarding({ selectedResources: next })
  }

  const toggleInterest = (id: string) => {
    const current = onboarding.selectedInterests
    const next = current.includes(id)
      ? current.filter((i) => i !== id)
      : [...current, id]
    updateOnboarding({ selectedInterests: next, isAiDecide: false })
  }

  const handleAiDecide = () => {
    updateOnboarding({
      isAiDecide: true,
      selectedInterests: ['farming', 'dairy', 'poultry', 'food', 'retail'],
    })
  }

  const canNext = useMemo(() => {
    if (step === 0) return onboarding.village.trim() !== '' && onboarding.district.trim() !== ''
    if (step === 1) return onboarding.budget > 0
    if (step === 2) return onboarding.selectedResources.length > 0
    if (step === 3) return onboarding.selectedInterests.length > 0 || onboarding.isAiDecide
    return true
  }, [step, onboarding])

  const startAnalysis = () => {
    setViewState('analyzing')
  }

  if (viewState === 'analyzing') {
    return (
      <AnalysisSequence
        onDone={() => {
          setHasCompletedAssessment(true)
          setViewState('recommendation')
        }}
      />
    )
  }

  if (viewState === 'recommendation') {
    return (
      <RecommendationView
        onComplete={() => {
          router.push('/dashboard')
        }}
      />
    )
  }

  return (
    <div className="mx-auto w-full max-w-2xl px-4 py-8 sm:px-6">
      {/* Top Progress Bar */}
      <div className="mb-8 flex items-center justify-between gap-2">
        {STEPS.map((label, i) => (
          <div key={label} className="flex flex-1 items-center gap-2">
            <div
              className={cn(
                'flex h-8 items-center gap-1.5 rounded-full px-3 text-xs font-bold transition-all',
                i < step
                  ? 'bg-primary text-white'
                  : i === step
                    ? 'bg-primary/15 text-primary border border-primary/30 ring-2 ring-primary/20'
                    : 'bg-muted text-muted-foreground',
              )}
            >
              {i < step ? <Check className="size-3.5" /> : <span>0{i + 1}</span>}
              <span className="hidden sm:inline">{label}</span>
            </div>
            {i < STEPS.length - 1 && (
              <div
                className={cn(
                  'h-0.5 flex-1 rounded-full transition-colors',
                  i < step ? 'bg-primary' : 'bg-border',
                )}
              />
            )}
          </div>
        ))}
      </div>

      {/* Main Interactive Form Card */}
      <div className="rounded-3xl border border-border bg-card p-6 shadow-soft sm:p-8">
        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial={{ opacity: 0, x: 15 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -15 }}
            transition={{ duration: 0.25 }}
          >
            {/* STEP 1: LOCATION */}
            {step === 0 && (
              <StepHeader
                badge="STEP 1 — LOCATION"
                icon={MapPin}
                title="Where do you want to start your business?"
                subtitle="Select your state, district and village or locality to analyze local demand."
              >
                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">
                      State
                    </label>
                    <select
                      value={onboarding.state}
                      onChange={(e) => updateOnboarding({ state: e.target.value })}
                      className="w-full rounded-2xl border border-input bg-background px-4 py-3.5 text-base font-semibold text-foreground outline-none focus:ring-2 focus:ring-ring"
                    >
                      <option value="Karnataka">Karnataka</option>
                      <option value="Maharashtra">Maharashtra</option>
                      <option value="Rajasthan">Rajasthan</option>
                      <option value="Uttar Pradesh">Uttar Pradesh</option>
                      <option value="Madhya Pradesh">Madhya Pradesh</option>
                      <option value="Tamil Nadu">Tamil Nadu</option>
                      <option value="Telangana">Telangana</option>
                      <option value="Bihar">Bihar</option>
                      <option value="Gujarat">Gujarat</option>
                    </select>
                  </div>

                  <div className="grid gap-4 sm:grid-cols-2">
                    <div>
                      <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">
                        District
                      </label>
                      <input
                        value={onboarding.district}
                        onChange={(e) => updateOnboarding({ district: e.target.value })}
                        placeholder="e.g. Ramanagara"
                        className="w-full rounded-2xl border border-input bg-background px-4 py-3.5 text-base font-semibold outline-none focus:ring-2 focus:ring-ring"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">
                        Village / Locality
                      </label>
                      <input
                        value={onboarding.village}
                        onChange={(e) => updateOnboarding({ village: e.target.value })}
                        placeholder="e.g. Hosahalli"
                        className="w-full rounded-2xl border border-input bg-background px-4 py-3.5 text-base font-semibold outline-none focus:ring-2 focus:ring-ring"
                      />
                    </div>
                  </div>
                </div>
              </StepHeader>
            )}

            {/* STEP 2: BUDGET */}
            {step === 1 && (
              <StepHeader
                badge="STEP 2 — BUDGET"
                icon={Coins}
                title="What’s your starting budget?"
                subtitle="Specify how much initial money you can contribute towards your venture."
              >
                <div className="rounded-2xl border border-border bg-background p-6 text-center">
                  <p className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                    YOUR STARTING CAPITAL
                  </p>
                  <div className="mt-2 font-display text-4xl sm:text-5xl font-black text-primary tracking-tight">
                    {formatINR(onboarding.budget)}
                  </div>

                  {/* Interactive Slider */}
                  <div className="mt-6 px-2">
                    <input
                      type="range"
                      min={25000}
                      max={1000000}
                      step={25000}
                      value={onboarding.budget}
                      onChange={(e) => updateOnboarding({ budget: Number(e.target.value) })}
                      className="w-full accent-[#C96A45] cursor-pointer h-2.5 bg-muted rounded-lg"
                    />
                    <div className="mt-2 flex items-center justify-between text-xs font-bold text-muted-foreground">
                      <span>₹25,000</span>
                      <span>₹5,000,000</span>
                      <span>₹10,00,000</span>
                    </div>
                  </div>

                  {/* Presets */}
                  <div className="mt-6 flex flex-wrap items-center justify-center gap-2">
                    {BUDGET_PRESETS.map((val) => (
                      <button
                        key={val}
                        type="button"
                        onClick={() => updateOnboarding({ budget: val })}
                        className={cn(
                          'rounded-full px-4 py-2 text-xs font-bold border transition-all',
                          onboarding.budget === val
                            ? 'bg-primary text-white border-primary shadow-soft'
                            : 'bg-card text-foreground border-border hover:border-primary/40',
                        )}
                      >
                        {formatCompactINR(val)}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Derived financial stats */}
                <div className="mt-4 grid grid-cols-2 gap-3">
                  <div className="rounded-2xl border border-border bg-card p-4">
                    <p className="text-xs font-bold text-muted-foreground uppercase">
                      Unlocks Project Size
                    </p>
                    <p className="mt-1 text-xl font-extrabold text-foreground">
                      {formatCompactINR(financePreview.projectCost)}
                    </p>
                  </div>
                  <div className="rounded-2xl border border-border bg-card p-4">
                    <p className="text-xs font-bold text-muted-foreground uppercase">
                      Potential Scheme Loan
                    </p>
                    <p className="mt-1 text-xl font-extrabold text-primary">
                      {formatCompactINR(financePreview.loan)}
                    </p>
                  </div>
                </div>
              </StepHeader>
            )}

            {/* STEP 3: RESOURCES */}
            {step === 2 && (
              <StepHeader
                badge="STEP 3 — RESOURCES"
                icon={Building2}
                title="What resources do you have?"
                subtitle="Select all assets or facilities available to you (select all that apply)."
              >
                <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
                  {ONBOARDING_RESOURCES.map((res) => {
                    const selected = onboarding.selectedResources.includes(res.id)
                    return (
                      <button
                        key={res.id}
                        type="button"
                        onClick={() => toggleResource(res.id)}
                        className={cn(
                          'flex flex-col items-start rounded-2xl border p-4 text-left transition-all relative',
                          selected
                            ? 'border-primary bg-primary/10 ring-2 ring-primary/30'
                            : 'border-border bg-background hover:border-primary/40',
                        )}
                      >
                        {selected && (
                          <CheckCircle2 className="size-4 text-primary absolute top-3 right-3" />
                        )}
                        <span className="text-3xl">{res.icon}</span>
                        <span className="mt-3 font-bold text-sm text-foreground">
                          {res.label}
                        </span>
                        <span className="mt-0.5 text-xs text-muted-foreground">
                          {res.description}
                        </span>
                      </button>
                    )
                  })}
                </div>
              </StepHeader>
            )}

            {/* STEP 4: INTERESTS */}
            {step === 3 && (
              <StepHeader
                badge="STEP 4 — INTERESTS"
                icon={Sparkles}
                title="What kind of business interests you?"
                subtitle="Pick your preferred sectors or let AI choose the best match."
              >
                {/* Prominent AI Option */}
                <div
                  onClick={handleAiDecide}
                  className={cn(
                    'mb-5 cursor-pointer rounded-2xl border p-4 flex items-center justify-between transition-all shadow-soft',
                    onboarding.isAiDecide
                      ? 'bg-primary text-white border-primary ring-2 ring-sand ring-offset-2'
                      : 'bg-primary/10 border-primary/30 text-primary hover:bg-primary/15',
                  )}
                >
                  <div className="flex items-center gap-3">
                    <div className="grid size-10 place-items-center rounded-xl bg-charcoal text-white">
                      <Sparkles className="size-5" />
                    </div>
                    <div>
                      <h4 className="font-extrabold text-base">Not sure? Let AI decide →</h4>
                      <p className="text-xs opacity-90">
                        Our algorithm will rank all sectors based on local market profitability.
                      </p>
                    </div>
                  </div>
                  {onboarding.isAiDecide && <Check className="size-5 text-white" />}
                </div>

                <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                  {ONBOARDING_INTERESTS.map((item) => {
                    const selected = onboarding.selectedInterests.includes(item.id) && !onboarding.isAiDecide
                    return (
                      <button
                        key={item.id}
                        type="button"
                        onClick={() => toggleInterest(item.id)}
                        className={cn(
                          'flex flex-col items-start rounded-2xl border p-3.5 text-left transition-all relative',
                          selected
                            ? 'border-primary bg-primary/10 ring-2 ring-primary/30'
                            : 'border-border bg-background hover:border-primary/40',
                        )}
                      >
                        {selected && (
                          <CheckCircle2 className="size-4 text-primary absolute top-3 right-3" />
                        )}
                        <span className="text-2xl">{item.icon}</span>
                        <span className="mt-2 font-bold text-xs text-foreground">
                          {item.label}
                        </span>
                      </button>
                    )
                  })}
                </div>
              </StepHeader>
            )}

            {/* STEP 5: REVIEW */}
            {step === 4 && (
              <StepHeader
                badge="STEP 5 — REVIEW"
                icon={Check}
                title="Review your profile"
                subtitle="Double-check your inputs before we run our market intelligence analysis."
              >
                <div className="divide-y divide-border/80 rounded-2xl border border-border bg-background">
                  <SummaryRow label="Location" value={`${onboarding.village}, ${onboarding.district}, ${onboarding.state}`} />
                  <SummaryRow label="Starting Budget" value={formatINR(onboarding.budget)} />
                  <SummaryRow
                    label="Available Resources"
                    value={onboarding.selectedResources.map((r) => r.toUpperCase()).join(', ')}
                  />
                  <SummaryRow
                    label="Business Mode"
                    value={
                      onboarding.isAiDecide
                        ? '✨ AI Automatic Recommendation'
                        : onboarding.selectedInterests.map((i) => i.toUpperCase()).join(', ')
                    }
                  />
                  <SummaryRow label="Est. Project Size" value={formatCompactINR(financePreview.projectCost)} />
                  <SummaryRow label="Matched Loan" value={formatCompactINR(financePreview.loan)} />
                </div>
              </StepHeader>
            )}
          </motion.div>
        </AnimatePresence>

        {/* Navigation buttons */}
        <div className="mt-8 flex items-center justify-between gap-3 border-t border-border/80 pt-6">
          <button
            type="button"
            onClick={() => setStep((s) => Math.max(0, s - 1))}
            disabled={step === 0}
            className="inline-flex items-center gap-2 rounded-full border border-border px-5 py-2.5 text-sm font-bold text-foreground transition-colors hover:bg-muted disabled:opacity-0"
          >
            <ArrowLeft className="size-4" />
            Back
          </button>

          {step < STEPS.length - 1 ? (
            <button
              type="button"
              onClick={() => setStep((s) => s + 1)}
              disabled={!canNext}
              className="inline-flex items-center gap-2 rounded-full bg-primary px-7 py-3 text-sm font-bold text-white shadow-soft transition-transform enabled:hover:scale-105 hover:bg-primary-hover disabled:opacity-50"
            >
              Continue
              <ArrowRight className="size-4" />
            </button>
          ) : (
            <button
              type="button"
              onClick={startAnalysis}
              className="inline-flex items-center gap-2 rounded-full bg-primary px-8 py-3.5 text-base font-extrabold text-white shadow-lift transition-transform hover:scale-105 hover:bg-primary-hover"
            >
              Analyze My Opportunity →
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

function StepHeader({
  badge,
  icon: Icon,
  title,
  subtitle,
  children,
}: {
  badge: string
  icon: React.ElementType
  title: string
  subtitle: string
  children: React.ReactNode
}) {
  return (
    <div>
      <span className="inline-flex items-center gap-1.5 text-xs font-extrabold tracking-wider text-primary uppercase">
        <Icon className="size-3.5" />
        {badge}
      </span>
      <h2 className="mt-2 font-display text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
        {title}
      </h2>
      <p className="mt-1.5 text-sm text-muted-foreground">{subtitle}</p>
      <div className="mt-6">{children}</div>
    </div>
  )
}

function SummaryRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-4 px-4 py-3.5">
      <span className="text-xs font-bold text-muted-foreground uppercase">{label}</span>
      <span className="text-sm font-bold text-foreground text-right">{value}</span>
    </div>
  )
}
