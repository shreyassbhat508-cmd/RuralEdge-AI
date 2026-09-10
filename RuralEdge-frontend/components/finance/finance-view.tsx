'use client'

import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import {
  AlertTriangle,
  CheckCircle2,
  IndianRupee,
  Info,
  Calculator,
  ShieldCheck,
  Sparkles,
  Clock,
  ArrowRight,
  RefreshCw,
} from 'lucide-react'
import { useBusiness } from '@/components/business-context'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { PlainTip } from '@/components/plain-tip'
import { RepaymentChart } from '@/components/charts/repayment-chart'
import { formatCompactINR, formatINR } from '@/lib/data'
import { calculateLoan } from '@/lib/api/finance'
import { LoanCalculatorResponse } from '@/lib/api/types'
import { cn } from '@/lib/utils'

export function FinanceView() {
  const { profile, onboarding } = useBusiness()

  // State for Loan Calculator Inputs
  const [projectCost, setProjectCost] = useState<number>(1000000)
  const [marginPercentage, setMarginPercentage] = useState<number>(10)
  const [annualInterestRate, setAnnualInterestRate] = useState<number>(6)
  const [repaymentPeriodMonths, setRepaymentPeriodMonths] = useState<number>(60)
  const [moratoriumMonths, setMoratoriumMonths] = useState<number>(6)

  // API State
  const [calcResult, setCalcResult] = useState<LoanCalculatorResponse | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  // Input validation
  const validationError = (() => {
    if (projectCost <= 0 || projectCost > 100000000) {
      return 'Project cost must be between ₹1 and ₹10,00,00,000'
    }
    if (marginPercentage < 0 || marginPercentage > 100) {
      return 'Margin percentage must be between 0% and 100%'
    }
    if (annualInterestRate < 0 || annualInterestRate > 100) {
      return 'Annual interest rate must be between 0% and 100%'
    }
    if (repaymentPeriodMonths <= 0 || repaymentPeriodMonths > 600) {
      return 'Repayment period must be between 1 and 600 months'
    }
    if (moratoriumMonths < 0 || moratoriumMonths > repaymentPeriodMonths) {
      return 'Moratorium months cannot exceed repayment period'
    }
    return null
  })()

  const runCalculation = useCallback(async () => {
    if (validationError) return

    setLoading(true)
    setError(null)
    try {
      const res = await calculateLoan({
        project_cost: projectCost,
        margin_percentage: marginPercentage,
        annual_interest_rate: annualInterestRate,
        repayment_period_months: repaymentPeriodMonths,
        moratorium_months: moratoriumMonths,
      })
      setCalcResult(res)
    } catch (err: any) {
      console.error('Error calculating loan:', err)
      setError(err.message || 'Failed to calculate loan terms from FastAPI server')
      setCalcResult(null)
    } finally {
      setLoading(false)
    }
  }, [projectCost, marginPercentage, annualInterestRate, repaymentPeriodMonths, moratoriumMonths, validationError])

  useEffect(() => {
    const timer = setTimeout(() => {
      runCalculation()
    }, 300)
    return () => clearTimeout(timer)
  }, [runCalculation])

  // Schedule generator for chart based on backend result
  const chartSchedule = (() => {
    if (!calcResult) return []
    const points: { period: string; principal: number; interest: number }[] = []
    const totalMonths = calcResult.repayment_period_months
    const yearlyStep = Math.max(1, Math.floor(totalMonths / 5))
    
    let remPrincipal = calcResult.loan_amount
    const totalInt = calcResult.total_interest

    for (let m = 0; m <= totalMonths; m += yearlyStep) {
      const progress = m / totalMonths
      const pPaid = calcResult.loan_amount * progress
      const iPaid = totalInt * progress
      points.push({
        period: `Month ${m}`,
        principal: Math.round(pPaid),
        interest: Math.round(iPaid),
      })
    }
    return points
  })()

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      {/* Top Section Header */}
      <div className="mb-8">
        <span className="inline-flex items-center gap-1.5 rounded-full border border-primary/30 bg-primary/10 px-3.5 py-1.5 text-xs font-bold text-primary">
          <Calculator className="size-4 text-primary" />
          FastAPI Loan Calculator API
        </span>
        <h1 className="mt-3 font-display text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
          Financing & EMI Calculator
        </h1>
        <p className="mt-1 text-base text-muted-foreground">
          Real-time financial calculation processed directly by RuralEdge FastAPI backend.
        </p>
      </div>

      {/* Validation Error Banner */}
      {validationError && (
        <div className="mb-6 rounded-2xl border border-destructive/40 bg-destructive/10 p-4 text-xs font-bold text-destructive flex items-center gap-2">
          <AlertTriangle className="size-4 shrink-0" />
          <span>{validationError}</span>
        </div>
      )}

      {/* Large Metric Header Cards */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-5 mb-8">
        <div className="rounded-2xl border border-border bg-card/95 backdrop-blur-md p-5 shadow-soft">
          <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
            PROJECT COST
          </p>
          <p className="mt-2 font-display text-2xl sm:text-3xl font-black text-foreground">
            {formatINR(projectCost)}
          </p>
          <p className="mt-1 text-[11px] text-muted-foreground">Total required capital</p>
        </div>

        <div className="rounded-2xl border border-border bg-card/95 backdrop-blur-md p-5 shadow-soft">
          <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
            YOUR CONTRIBUTION
          </p>
          <p className="mt-2 font-display text-2xl sm:text-3xl font-black text-primary">
            {calcResult ? formatINR(calcResult.margin_amount) : loading ? '...' : 'N/A'}
          </p>
          <p className="mt-1 text-[11px] text-muted-foreground">{marginPercentage}% margin money</p>
        </div>

        <div className="relative rounded-2xl border border-primary/40 bg-card/95 backdrop-blur-md p-5 shadow-soft overflow-hidden">
          <div className="absolute inset-0 bg-primary/10 pointer-events-none" />
          <div className="relative z-10">
            <p className="text-xs font-bold text-primary uppercase tracking-wider">
              LOAN AMOUNT
            </p>
            <p className="mt-2 font-display text-2xl sm:text-3xl font-black text-primary">
              {calcResult ? formatINR(calcResult.loan_amount) : loading ? '...' : 'N/A'}
            </p>
            <p className="mt-1 text-[11px] text-primary/80 font-medium">
              {100 - marginPercentage}% project funding
            </p>
          </div>
        </div>

        <div className="rounded-2xl border border-border bg-card/95 backdrop-blur-md p-5 shadow-soft">
          <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
            APPROX. MONTHLY EMI
          </p>
          <p className="mt-2 font-display text-2xl sm:text-3xl font-black text-foreground">
            {calcResult ? (
              <>
                {formatINR(calcResult.approx_monthly_payment)}
                <span className="text-xs font-normal text-muted-foreground">/mo</span>
              </>
            ) : loading ? (
              '...'
            ) : (
              'N/A'
            )}
          </p>
          <p className="mt-1 text-[11px] text-muted-foreground">
            {moratoriumMonths > 0 ? `After ${moratoriumMonths}m moratorium` : 'From month 1'}
          </p>
        </div>

        <div className="col-span-2 lg:col-span-1 rounded-2xl border border-border bg-card/95 backdrop-blur-md p-5 shadow-soft">
          <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
            TENURE & RATE
          </p>
          <p className="mt-2 font-display text-2xl sm:text-3xl font-black text-foreground">
            {(repaymentPeriodMonths / 12).toFixed(1)} Yrs
          </p>
          <p className="mt-1 text-[11px] text-muted-foreground">
            @ {annualInterestRate}% p.a. interest
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_1.4fr] items-start">
        {/* Calculator Controls Form */}
        <div className="flex flex-col gap-4 min-w-0">
          <Card className="rounded-3xl border-border shadow-soft">
            <CardHeader>
              <CardTitle className="text-xl">Loan Calculator Inputs</CardTitle>
              <p className="text-sm text-muted-foreground">
                Adjust project parameters to query the FastAPI loan calculator.
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Project Cost */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">
                  Total Project Cost (₹)
                </label>
                <input
                  type="number"
                  min="10000"
                  max="100000000"
                  value={projectCost}
                  onChange={(e) => setProjectCost(Number(e.target.value))}
                  className="w-full rounded-2xl border border-input bg-background px-4 py-3 text-base font-bold text-foreground outline-none focus:ring-2 focus:ring-ring"
                />
              </div>

              {/* Margin Percentage Slider */}
              <div>
                <div className="flex justify-between text-xs font-bold text-muted-foreground mb-1.5">
                  <span>Margin Contribution:</span>
                  <span className="text-primary font-black">{marginPercentage}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="50"
                  step="1"
                  value={marginPercentage}
                  onChange={(e) => setMarginPercentage(Number(e.target.value))}
                  className="w-full accent-[#C96A45] cursor-pointer h-2 bg-muted rounded-lg"
                />
              </div>

              {/* Annual Interest Rate */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">
                    Interest Rate (% p.a.)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="100"
                    value={annualInterestRate}
                    onChange={(e) => setAnnualInterestRate(Number(e.target.value))}
                    className="w-full rounded-2xl border border-input bg-background px-4 py-2.5 text-sm font-bold outline-none focus:ring-2 focus:ring-ring"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">
                    Tenure (Months)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="600"
                    value={repaymentPeriodMonths}
                    onChange={(e) => setRepaymentPeriodMonths(Number(e.target.value))}
                    className="w-full rounded-2xl border border-input bg-background px-4 py-2.5 text-sm font-bold outline-none focus:ring-2 focus:ring-ring"
                  />
                </div>
              </div>

              {/* Moratorium Months */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">
                  Moratorium / Grace Period (Months)
                </label>
                <input
                  type="number"
                  min="0"
                  max={repaymentPeriodMonths}
                  value={moratoriumMonths}
                  onChange={(e) => setMoratoriumMonths(Number(e.target.value))}
                  className="w-full rounded-2xl border border-input bg-background px-4 py-2.5 text-sm font-bold outline-none focus:ring-2 focus:ring-ring"
                />
              </div>

              <button
                type="button"
                onClick={runCalculation}
                disabled={loading || !!validationError}
                className="mt-2 w-full rounded-2xl bg-primary px-4 py-3 text-xs font-extrabold text-white shadow-soft hover:bg-primary-hover disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {loading ? <RefreshCw className="size-4 animate-spin" /> : <Calculator className="size-4" />}
                Calculate Loan via FastAPI
              </button>
            </CardContent>
          </Card>
        </div>

        {/* Calculation Result Display */}
        <div className="flex flex-col gap-4 min-w-0">
          {error ? (
            <Card className="rounded-3xl border-destructive/30 bg-destructive/10 shadow-soft">
              <CardContent className="p-8 text-center">
                <AlertTriangle className="mx-auto size-10 text-destructive mb-3" />
                <h3 className="font-bold text-foreground text-lg">Loan Calculation Failed</h3>
                <p className="mt-1 text-xs text-muted-foreground">{error}</p>
                <button
                  type="button"
                  onClick={runCalculation}
                  className="mt-4 rounded-full bg-primary px-5 py-2 text-xs font-bold text-white shadow-soft"
                >
                  Retry Calculation
                </button>
              </CardContent>
            </Card>
          ) : calcResult ? (
            <>
              <Card className="rounded-3xl border-border shadow-soft">
                <CardHeader>
                  <CardTitle className="text-lg">Backend Calculation Breakdown</CardTitle>
                </CardHeader>
                <CardContent className="grid grid-cols-2 gap-3">
                  <Output
                    label="Principal Loan"
                    value={formatINR(calcResult.loan_amount)}
                    tip="Calculated loan principle from project cost minus margin"
                    highlight
                  />
                  <Output
                    label="Total Interest"
                    value={formatINR(calcResult.total_interest)}
                    tip="Total simple interest calculated by backend"
                  />
                  <Output
                    label="Total Repayment"
                    value={formatINR(calcResult.total_repayment)}
                    tip="Principal + Total interest repayment"
                  />
                  <Output
                    label="Monthly Payment"
                    value={`${formatINR(calcResult.approx_monthly_payment)}/mo`}
                    tip="Estimated monthly repayment installment"
                  />
                </CardContent>
              </Card>

              {/* Note from Backend */}
              <div className="rounded-2xl border border-primary/30 bg-primary/8 p-4 text-xs">
                <span className="font-bold text-primary block mb-1">FastAPI Note</span>
                <p className="text-muted-foreground leading-relaxed">
                  {calcResult.calculation_note}
                </p>
              </div>

              {/* Repayment Chart */}
              <Card className="rounded-3xl border-border shadow-soft">
                <CardHeader>
                  <CardTitle className="text-lg">Repayment Schedule Visualization</CardTitle>
                </CardHeader>
                <CardContent>
                  <RepaymentChart rows={chartSchedule} />
                </CardContent>
              </Card>
            </>
          ) : null}
        </div>
      </div>
    </div>
  )
}

function Output({
  label,
  value,
  tip,
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
        'relative rounded-2xl border p-4 bg-card/95 backdrop-blur-md overflow-hidden',
        highlight ? 'border-primary/30' : 'border-border'
      )}
    >
      {highlight && <div className="absolute inset-0 bg-primary/10 pointer-events-none" />}
      <div className="relative z-10">
        <div className="flex items-center gap-1 text-xs font-bold text-muted-foreground uppercase">
          {label}
          <PlainTip text={tip} />
        </div>
        <p
          className={cn(
            'mt-1 font-display text-xl font-extrabold',
            highlight ? 'text-primary' : 'text-foreground',
          )}
        >
          {value}
        </p>
      </div>
    </div>
  )
}
