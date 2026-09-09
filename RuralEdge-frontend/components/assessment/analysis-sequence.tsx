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
} from 'lucide-react'
import { useEffect, useState } from 'react'
import { GramMark } from '@/components/gram-logo'
import { useBusiness } from '@/components/business-context'
import { cn } from '@/lib/utils'

const STAGES = [
  { icon: MapPin, label: 'Understanding your location' },
  { icon: TrendingUp, label: 'Analyzing local demand' },
  { icon: ShieldCheck, label: 'Checking business viability' },
  { icon: Landmark, label: 'Matching government schemes' },
  { icon: Calculator, label: 'Calculating financing options' },
]

export function AnalysisSequence({ onDone }: { onDone: () => void }) {
  const { onboarding } = useBusiness()
  const [active, setActive] = useState(0)
  const [percent, setPercent] = useState(12)

  useEffect(() => {
    if (active >= STAGES.length) {
      setPercent(100)
      const t = setTimeout(onDone, 600)
      return () => clearTimeout(t)
    }

    setPercent(Math.min(96, Math.round(((active + 1) / STAGES.length) * 100)))

    const t = setTimeout(() => {
      setActive((a) => a + 1)
    }, 600)
    return () => clearTimeout(t)
  }, [active, onDone])

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
        Evaluating local market density in {onboarding.village || 'your area'}, {onboarding.district || 'district'}...
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
            initial={{ width: '12%' }}
            animate={{ width: `${percent}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>
      </div>

      <ul className="mt-8 flex w-full flex-col gap-3">
        {STAGES.map((s, i) => {
          const done = i < active
          const current = i === active
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

