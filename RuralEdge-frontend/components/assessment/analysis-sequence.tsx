'use client'

import { motion } from 'framer-motion'
import {
  Check,
  MapPin,
  TrendingUp,
  ShieldCheck,
  Landmark,
  Calculator,
  Loader2,
  AlertCircle,
  RefreshCw,
} from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { GramMark } from '@/components/gram-logo'
import { useBusiness } from '@/components/business-context'
import { cn } from '@/lib/utils'

const STAGES = [
  { icon: MapPin, label: 'Analyzing location' },
  { icon: TrendingUp, label: 'Checking local competition' },
  { icon: ShieldCheck, label: 'Calculating financial feasibility' },
  { icon: Landmark, label: 'Matching schemes' },
  { icon: Calculator, label: 'Preparing recommendation' },
]

export function AnalysisSequence({ onDone }: { onDone: () => void }) {
  const { onboarding, runAnalysis, analysisError } = useBusiness()
  const [active, setActive] = useState(0)
  const [percent, setPercent] = useState(15)
  const [isCompleted, setIsCompleted] = useState(false)
  const [localError, setLocalError] = useState<string | null>(null)
  const hasTriggeredRef = useRef(false)

  const executeAnalysis = async () => {
    setLocalError(null)
    setActive(0)
    setPercent(20)
    setIsCompleted(false)

    // Simulate animated UI stages while request is in-flight
    const interval = setInterval(() => {
      setActive((prev) => {
        if (prev < STAGES.length - 2) {
          const next = prev + 1
          setPercent(Math.round(((next + 1) / STAGES.length) * 85))
          return next
        }
        return prev
      })
    }, 600)

    try {
      await runAnalysis()
      clearInterval(interval)
      setActive(STAGES.length)
      setPercent(100)
      setIsCompleted(true)
      setTimeout(onDone, 700)
    } catch (err: unknown) {
      clearInterval(interval)
      const msg =
        err instanceof Error
          ? err.message
          : 'Unable to complete business analysis. Please check your backend connection.'
      setLocalError(msg)
    }
  }

  useEffect(() => {
    if (!hasTriggeredRef.current) {
      hasTriggeredRef.current = true
      executeAnalysis()
    }
  }, [])

  return (
    <div className="mx-auto flex min-h-[75vh] w-full max-w-xl flex-col items-center justify-center px-4 py-10 text-center">
      <motion.div
        initial={{ scale: 0.85, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ type: 'spring', stiffness: 200, damping: 16 }}
      >
        <div className="relative grid size-20 place-items-center">
          <span className="absolute inset-0 animate-ping rounded-2xl bg-primary/20" />
          <GramMark className="size-16" />
        </div>
      </motion.div>

      <h2 className="mt-6 font-display text-3xl font-extrabold tracking-tight text-foreground">
        Analyzing your opportunity
      </h2>
      <p className="mt-2 text-sm text-muted-foreground">
        Evaluating market intelligence in {onboarding.village || 'your locality'}, {onboarding.district || 'district'}, {onboarding.state || 'state'}...
      </p>

      {/* Progress percentage bar */}
      <div className="mt-6 w-full max-w-sm">
        <div className="flex items-center justify-between text-xs font-bold text-primary mb-2">
          <span>AI ANALYZING</span>
          <span className="text-sm font-extrabold">{percent}%</span>
        </div>
        <div className="h-2.5 w-full overflow-hidden rounded-full bg-muted">
          <motion.div
            className="h-full bg-gradient-to-r from-primary to-primary-hover"
            initial={{ width: '15%' }}
            animate={{ width: `${percent}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>
      </div>

      {/* Error Card */}
      {(localError || analysisError) && (
        <div className="mt-6 w-full rounded-2xl border border-destructive/30 bg-destructive/10 p-4 text-left">
          <div className="flex items-start gap-3">
            <AlertCircle className="size-5 shrink-0 text-destructive mt-0.5" />
            <div className="flex-1">
              <h4 className="text-sm font-bold text-destructive">
                Backend Connection Error
              </h4>
              <p className="mt-1 text-xs text-muted-foreground">
                {localError || analysisError}
              </p>
              <div className="mt-3 flex items-center gap-3">
                <button
                  type="button"
                  onClick={executeAnalysis}
                  className="inline-flex items-center gap-1.5 rounded-full bg-destructive px-4 py-1.5 text-xs font-bold text-white shadow-soft hover:bg-destructive/90"
                >
                  <RefreshCw className="size-3.5" />
                  Retry Analysis
                </button>
                <button
                  type="button"
                  onClick={onDone}
                  className="rounded-full border border-border bg-card px-4 py-1.5 text-xs font-bold text-foreground hover:bg-muted"
                >
                  Continue to Plan
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <ul className="mt-8 flex w-full flex-col gap-3">
        {STAGES.map((s, i) => {
          const done = i < active || isCompleted
          const current = i === active && !isCompleted && !localError && !analysisError
          const Icon = s.icon
          return (
            <motion.li
              key={s.label}
              initial={{ opacity: 0.4 }}
              animate={{ opacity: done || current ? 1 : 0.4 }}
              className={cn(
                'flex items-center gap-3.5 rounded-2xl border px-4 py-3 text-left transition-all',
                done
                  ? 'border-primary/30 bg-primary/10 text-foreground'
                  : current
                    ? 'border-primary/50 bg-card shadow-soft ring-1 ring-primary/20'
                    : 'border-border bg-card/60',
              )}
            >
              <span
                className={cn(
                  'grid size-9 shrink-0 place-items-center rounded-xl font-bold transition-all',
                  done
                    ? 'bg-primary text-white'
                    : current
                      ? 'bg-primary/15 text-primary'
                      : 'bg-muted text-muted-foreground',
                )}
              >
                {done ? (
                  <Check className="size-5" />
                ) : current ? (
                  <Loader2 className="size-5 animate-spin text-primary" />
                ) : (
                  <Icon className="size-5" />
                )}
              </span>
              <span className="text-sm font-bold">{s.label}</span>
            </motion.li>
          )
        })}
      </ul>
    </div>
  )
}
