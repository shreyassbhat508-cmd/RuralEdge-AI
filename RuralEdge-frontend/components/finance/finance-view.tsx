'use client'

import { AlertTriangle, CheckCircle2, IndianRupee, Info, Calculator, Clock, ArrowRight } from 'lucide-react'
import { useMemo, useState } from 'react'
import { useBusiness } from '@/components/business-context'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { RepaymentChart } from '@/components/charts/repayment-chart'
import {
  SCHEMES,
  buildRepaymentSchedule,
  computeFinance,
  formatCompactINR,
  formatINR,
} from '@/lib/data'
import { cn } from '@/lib/utils'

export function FinanceView() {
  const { profile, updateProfile, onboarding, businessAnalysis } = useBusiness()
  const [mode, setMode] = useState<'monthly' | 'quarterly'>('quarterly')
  
  const [moratoriumSelection, setMoratoriumSelection] = useState<string>('default')
  const [customMoratorium, setCustomMoratorium] = useState<number>(6)
  const [interestTreatment, setInterestTreatment] = useState<'pay_separately' | 'accrue'>('pay_separately')

  // Dynamic loan override option
  const margin = profile.margin
  
  const activeMoratorium = useMemo(() => {
    if (moratoriumSelection === 'default') return null
    if (moratoriumSelection === 'custom') return customMoratorium
    return parseInt(moratoriumSelection, 10)
  }, [moratoriumSelection, customMoratorium])

  const plan = useMemo(() => computeFinance(margin, activeMoratorium, interestTreatment), [margin, activeMoratorium, interestTreatment])
  const schedule = useMemo(
    () => buildRepaymentSchedule(plan, mode),
    [plan, mode],
  )
  const interestShare = plan.totalPayable
    ? (plan.totalInterest / plan.totalPayable) * 100
    : 0

  const timelineDate = (monthsOffset: number) => {
    const d = new Date()
    d.setMonth(d.getMonth() + monthsOffset)
    return d.toLocaleDateString('en-IN', { month: 'short', year: 'numeric' })
  }

  const emiStartDate = timelineDate(plan.appliedMoratoriumMonths)
  const finalRepaymentDate = timelineDate(plan.scheme.tenureYears * 12)
  const todayDate = timelineDate(0)

  // Primary authoritative values from backend when available
  const displayProjectCost = businessAnalysis?.finance?.project_cost ?? plan.projectCost
  const displayMargin = businessAnalysis?.finance?.own_contribution ?? plan.margin
  const displayLoan = businessAnalysis?.finance?.loan_amount ?? plan.loan
  const displayEmi = businessAnalysis?.finance?.emi ?? plan.emi
  const displayTenureYears = businessAnalysis?.finance?.payback_months
    ? Math.round(businessAnalysis.finance.payback_months / 12)
    : plan.scheme.tenureYears

  const calculationNote = businessAnalysis?.finance?.calculation_note ||
    "Estimated calculation for planning purposes. Actual loan terms, interest calculation, EMI, subsidy, moratorium and repayment schedule depend on the applicable government scheme and lending institution."

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      {/* Top Section Header */}
      <div className="mb-8">
        <span className="inline-flex items-center gap-1.5 rounded-full border border-primary/30 bg-primary/10 px-3.5 py-1.5 text-xs font-bold text-primary">
          <Calculator className="size-4 text-primary" />
          Fintech Loan & EMI Engine
        </span>
        <h1 className="mt-3 font-display text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
          Your financing plan
        </h1>
        <p className="mt-1 text-base text-muted-foreground">
          Authoritative credit & repayment calculations generated for your business in {onboarding.village || 'Hosahalli'}.
        </p>
      </div>

      {/* Large Metric Header Cards */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-5 mb-8">
        <div className="rounded-2xl border border-border bg-card/95 backdrop-blur-md p-5 shadow-soft">
          <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
            PROJECT COST
          </p>
          <p className="mt-2 font-display text-2xl sm:text-3xl font-black text-foreground">
            {formatINR(displayProjectCost)}
          </p>
          <p className="mt-1 text-[11px] text-muted-foreground">Total capital requirement</p>
        </div>

        <div className="rounded-2xl border border-border bg-card/95 backdrop-blur-md p-5 shadow-soft">
          <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
            YOUR CONTRIBUTION
          </p>
          <p className="mt-2 font-display text-2xl sm:text-3xl font-black text-primary">
            {formatINR(displayMargin)}
          </p>
          <p className="mt-1 text-[11px] text-muted-foreground">Own equity margin</p>
        </div>

        <div className="relative rounded-2xl border border-primary/40 bg-card/95 backdrop-blur-md p-5 shadow-soft overflow-hidden">
          <div className="absolute inset-0 bg-primary/10 pointer-events-none" />
          <div className="relative z-10">
            <p className="text-xs font-bold text-primary uppercase tracking-wider">
              POTENTIAL LOAN
            </p>
            <p className="mt-2 font-display text-2xl sm:text-3xl font-black text-primary">
              {formatINR(displayLoan)}
            </p>
            <p className="mt-1 text-[11px] text-primary/80 font-medium">Scheme loan principal</p>
          </div>
        </div>

        <div className="rounded-2xl border border-border bg-card/95 backdrop-blur-md p-5 shadow-soft">
          <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
            ESTIMATED EMI
          </p>
          <p className="mt-2 font-display text-2xl sm:text-3xl font-black text-foreground">
            {formatINR(displayEmi)}
            <span className="text-xs font-normal text-muted-foreground">/mo</span>
          </p>
          <p className="mt-1 text-[11px] text-muted-foreground">
            Monthly reducing payment
          </p>
        </div>

        <div className="col-span-2 lg:col-span-1 rounded-2xl border border-border bg-card/95 backdrop-blur-md p-5 shadow-soft">
          <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
            TENURE
          </p>
          <p className="mt-2 font-display text-2xl sm:text-3xl font-black text-foreground">
            {displayTenureYears} Years
          </p>
          <p className="mt-1 text-[11px] text-muted-foreground">
            {plan.appliedMoratoriumMonths}m grace period
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_1.4fr] items-start">
        {/* Calculator Controls */}
        <div className="flex flex-col gap-4 min-w-0">
          <Card className="rounded-3xl border-border shadow-soft">
            <CardHeader>
              <CardTitle className="text-xl">Interactive Loan & Margin Slider</CardTitle>
              <p className="text-sm text-muted-foreground">
                Adjust your contribution to recalculate loan eligibility and monthly EMI in real-time.
              </p>
            </CardHeader>
            <CardContent>
              <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-2">
                Your Contribution (Margin Money)
              </label>
              <div className="flex items-center gap-2 rounded-2xl border border-input bg-background px-4 py-3.5">
                <IndianRupee className="size-5 text-primary" />
                <input
                  inputMode="numeric"
                  value={margin ? margin.toLocaleString('en-IN') : ''}
                  onChange={(e) => {
                    const n = Number(e.target.value.replace(/[^0-9]/g, ''))
                    updateProfile({ margin: Number.isFinite(n) ? n : 0 })
                  }}
                  className="w-full bg-transparent text-xl font-bold outline-none"
                  placeholder="1,00,000"
                />
              </div>

              {/* Interactive Loan Slider */}
              <div className="mt-6">
                <div className="flex justify-between text-xs font-bold text-muted-foreground mb-2">
                  <span>₹25,000</span>
                  <span className="text-primary">₹5,00,000 loan slider</span>
                  <span>₹10,00,000</span>
                </div>
                <input
                  type="range"
                  min={10000}
                  max={500000}
                  step={5000}
                  value={Math.min(margin, 500000)}
                  onChange={(e) => updateProfile({ margin: Number(e.target.value) })}
                  className="w-full accent-[#C96A45] cursor-pointer h-2.5 bg-muted rounded-lg"
                  aria-label="Margin money slider"
                />
              </div>
            </CardContent>
          </Card>

          <Card className="rounded-3xl border-border shadow-soft">
            <CardHeader>
              <CardTitle className="text-xl">Repayment Settings</CardTitle>
              <p className="text-sm text-muted-foreground">
                Customize when you start paying your EMI and how interest is treated.
              </p>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-2">
                  Repayment Starts After (Moratorium)
                </label>
                <div className="flex flex-wrap gap-2">
                  {['default', '0', '3', '6', '9', '12', 'custom'].map(opt => (
                    <button
                      key={opt}
                      type="button"
                      onClick={() => setMoratoriumSelection(opt)}
                      className={cn(
                        "px-3 py-1.5 rounded-full border text-xs font-semibold transition-colors",
                        moratoriumSelection === opt ? "bg-primary text-white border-primary" : "bg-background border-border text-muted-foreground hover:bg-muted"
                      )}
                    >
                      {opt === 'default' ? `Default (${plan.scheme.moratoriumMonths}m)` : opt === 'custom' ? 'Custom' : `${opt} Months`}
                    </button>
                  ))}
                </div>
                {moratoriumSelection === 'custom' && (
                  <div className="mt-3 flex items-center gap-2">
                    <input
                      type="number"
                      min="0"
                      max="120"
                      value={customMoratorium}
                      onChange={(e) => setCustomMoratorium(Number(e.target.value))}
                      className="w-20 rounded-lg border border-input bg-background px-3 py-1.5 text-sm"
                    />
                    <span className="text-sm text-muted-foreground">months</span>
                  </div>
                )}
              </div>

              {plan.appliedMoratoriumMonths > 0 && (
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-2">
                    Interest Treatment During Moratorium
                  </label>
                  <div className="flex flex-col sm:flex-row gap-2">
                    <button
                      type="button"
                      onClick={() => setInterestTreatment('pay_separately')}
                      className={cn(
                        "flex-1 px-3 py-2 rounded-xl border text-left text-xs transition-colors",
                        interestTreatment === 'pay_separately' ? "border-primary bg-primary/5" : "border-border bg-background"
                      )}
                    >
                      <span className="block font-bold text-foreground">Pay Separately</span>
                      <span className="text-muted-foreground mt-0.5 block">Pay interest monthly during grace period</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setInterestTreatment('accrue')}
                      className={cn(
                        "flex-1 px-3 py-2 rounded-xl border text-left text-xs transition-colors",
                        interestTreatment === 'accrue' ? "border-primary bg-primary/5" : "border-border bg-background"
                      )}
                    >
                      <span className="block font-bold text-foreground">Accrue to Loan</span>
                      <span className="text-muted-foreground mt-0.5 block">Add interest to principal (No payment until EMI)</span>
                    </button>
                  </div>
                </div>
              )}

              {/* Timeline UI */}
              <div className="pt-6 border-t border-border">
                <h4 className="text-xs font-bold text-foreground mb-4 uppercase tracking-wider">Repayment Timeline</h4>
                <div className="relative flex justify-between text-center text-xs">
                  <div className="absolute left-4 right-4 top-2.5 h-0.5 bg-border -z-10" />
                  
                  <div className="flex w-16 flex-col items-center gap-1.5 bg-card/95 backdrop-blur-md z-10">
                    <div className="flex size-5 items-center justify-center rounded-full bg-primary text-white">
                      <CheckCircle2 className="size-3" />
                    </div>
                    <div className="font-semibold text-foreground leading-tight">Disbursed</div>
                    <div className="text-[10px] text-muted-foreground">{todayDate}</div>
                  </div>

                  {plan.appliedMoratoriumMonths > 0 && (
                    <div className="flex w-16 flex-col items-center gap-1.5 bg-card/95 backdrop-blur-md z-10">
                      <div className="flex size-5 items-center justify-center rounded-full border-2 border-primary bg-background text-primary">
                        <Clock className="size-3" />
                      </div>
                      <div className="font-semibold text-foreground leading-tight">{plan.appliedMoratoriumMonths}m Grace</div>
                      <div className="text-[10px] text-muted-foreground">Moratorium</div>
                    </div>
                  )}

                  <div className="flex w-16 flex-col items-center gap-1.5 bg-card/95 backdrop-blur-md z-10">
                    <div className="flex size-5 items-center justify-center rounded-full bg-foreground text-background">
                      <ArrowRight className="size-3" />
                    </div>
                    <div className="font-semibold text-foreground leading-tight">EMI Starts</div>
                    <div className="text-[10px] text-muted-foreground">{emiStartDate}</div>
                  </div>

                  <div className="flex w-16 flex-col items-center gap-1.5 bg-card/95 backdrop-blur-md z-10">
                    <div className="flex size-5 items-center justify-center rounded-full bg-border text-muted-foreground">
                      <CheckCircle2 className="size-3" />
                    </div>
                    <div className="font-semibold text-foreground leading-tight">Paid Off</div>
                    <div className="text-[10px] text-muted-foreground">{finalRepaymentDate}</div>
                  </div>
                </div>
              </div>

              <div className="rounded-2xl bg-muted/40 border border-border p-3">
                <p className="text-[11px] text-muted-foreground italic leading-tight">
                  {calculationNote}
                </p>
              </div>
            </CardContent>
          </Card>

          <Card className="rounded-3xl border-border shadow-soft">
            <CardContent className="grid grid-cols-2 gap-3 pt-5">
              <Output
                label="Principal Amount"
                value={formatINR(plan.loan)}
                tip="Initial sum borrowed under scheme"
                highlight
              />
              <Output
                label="Interest Component"
                value={formatINR(plan.totalInterest)}
                tip="Total interest accrued over loan period"
              />
              <Output
                label="Total Repayment"
                value={formatINR(plan.totalPayable)}
                tip="Principal + Total interest"
              />
              <Output
                label="Moratorium Charge"
                value={`${formatINR(plan.monthlyDuringMoratorium)}/mo`}
                tip={plan.interestTreatment === 'accrue' ? "Interest is added to principal (₹0 paid during grace period)" : "Interest-only payment during grace months"}
              />
            </CardContent>
          </Card>

          {plan.aboveMax ? (
            <Note tone="warning" icon={AlertTriangle}>
              A project of this size is above the {formatCompactINR(5000000)} programme limit. We&apos;ve capped the plan to the maximum supported loan.
            </Note>
          ) : plan.capApplied ? (
            <Note tone="warning" icon={Info}>
              Your loan has been capped at the {plan.scheme.name}&apos;s maximum of {formatCompactINR(plan.scheme.maxLoan)}.
            </Note>
          ) : (
            <Note tone="success" icon={CheckCircle2}>
              Based on your monthly surplus, this plan looks affordable with a healthy safety margin.
            </Note>
          )}
        </div>

        {/* Repayment Chart & Scheme Cards */}
        <div className="flex flex-col gap-4 min-w-0">
          <div className="grid gap-4 sm:grid-cols-2">
            {SCHEMES.map((s) => {
              const active = s.id === plan.scheme.id
              return (
                <Card
                  key={s.id}
                  className={cn(
                    'relative overflow-hidden rounded-3xl transition-all bg-card/95 backdrop-blur-md',
                    active && 'ring-2 ring-primary border-primary',
                  )}
                >
                  {active && <div className="absolute inset-0 bg-primary/5 pointer-events-none" />}
                  {active && (
                    <span className="absolute right-0 top-0 rounded-bl-2xl bg-primary px-3.5 py-1 text-xs font-bold text-white z-10">
                      Best Match
                    </span>
                  )}
                  <CardHeader className="relative z-10">
                    <CardTitle className="text-base font-bold">{s.name}</CardTitle>
                    <p className="text-xs text-muted-foreground">{s.tagline}</p>
                  </CardHeader>
                  <CardContent className="space-y-2 text-xs font-semibold relative z-10">
                    <SchemeRow k="Interest Rate" v={`${s.interest}% p.a.`} />
                    <SchemeRow k="Tenure" v={`${s.tenureYears} years`} />
                    <SchemeRow k="Moratorium" v={`${s.moratoriumMonths} months`} />
                    <SchemeRow k="Max Loan" v={formatCompactINR(s.maxLoan)} />
                  </CardContent>
                </Card>
              )
            })}
          </div>

          <Card className="rounded-3xl border-border shadow-soft">
            <CardHeader>
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 sm:gap-2">
                <div>
                  <CardTitle className="text-lg">Repayment Schedule Visualization</CardTitle>
                  <p className="text-xs text-muted-foreground">
                    Principal vs Interest distribution over tenure.
                  </p>
                </div>
                <div className="flex rounded-full border border-border p-1 text-xs font-semibold shrink-0">
                  {(['monthly', 'quarterly'] as const).map((m) => (
                    <button
                      key={m}
                      type="button"
                      onClick={() => setMode(m)}
                      className={cn(
                        'rounded-full px-3 py-1.5 capitalize transition-colors',
                        mode === m
                          ? 'bg-primary text-white'
                          : 'text-muted-foreground',
                      )}
                    >
                      {m}
                    </button>
                  ))}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="mb-4 flex flex-wrap items-center gap-4">
                <div className="flex items-center gap-2">
                  <span className="h-3 w-6 rounded-full bg-[var(--chart-1)]" />
                  <span className="text-xs text-muted-foreground">
                    Total repaid{' '}
                    <span className="font-bold text-foreground">
                      {formatCompactINR(plan.totalPayable)}
                    </span>
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="h-3 w-6 rounded-full bg-[var(--chart-4)]" />
                  <span className="text-xs text-muted-foreground">
                    Interest is{' '}
                    <span className="font-bold text-foreground">
                      {interestShare.toFixed(0)}%
                    </span>{' '}
                    of total
                  </span>
                </div>
              </div>
              <RepaymentChart rows={schedule} />
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

function Output({
  label,
  value,
  highlight,
}: {
  label: string
  value: string
  tip: string
  highlight?: boolean
}) {
  return (
    <div
      className={cn(
        'rounded-2xl border border-border p-3.5',
        highlight ? 'bg-primary/10 border-primary/30' : 'bg-background',
      )}
    >
      <span className="text-[11px] font-bold text-muted-foreground uppercase block">{label}</span>
      <span className={cn('text-lg font-black block mt-0.5', highlight ? 'text-primary' : 'text-foreground')}>
        {value}
      </span>
    </div>
  )
}

function SchemeRow({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex items-center justify-between border-b border-border/50 pb-1.5">
      <span className="text-muted-foreground">{k}</span>
      <span className="text-foreground">{v}</span>
    </div>
  )
}

function Note({
  children,
  tone,
  icon: Icon,
}: {
  children: React.ReactNode
  tone: 'warning' | 'success'
  icon: React.ComponentType<{ className?: string }>
}) {
  return (
    <div
      className={cn(
        'flex items-start gap-3 rounded-2xl border p-4 text-xs font-semibold',
        tone === 'warning'
          ? 'border-amber-500/30 bg-amber-500/10 text-amber-800 dark:text-amber-300'
          : 'border-emerald-500/30 bg-emerald-500/10 text-emerald-800 dark:text-emerald-300',
      )}
    >
      <Icon className="size-4 shrink-0 mt-0.5" />
      <span>{children}</span>
    </div>
  )
}
