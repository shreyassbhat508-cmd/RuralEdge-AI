'use client'

import { motion } from 'framer-motion'

export function HealthGauge({
  score,
  size = 200,
  label = 'Business Health',
}: {
  score: number
  size?: number
  label?: string
}) {
  const stroke = 16
  const r = (size - stroke) / 2
  const c = 2 * Math.PI * r
  const pct = Math.max(0, Math.min(100, score)) / 100
  const dash = c * 0.75 // three-quarter arc
  const offset = dash * (1 - pct)

  const color =
    score >= 75 ? 'var(--success)' : score >= 55 ? 'var(--gold)' : 'var(--warning)'
  const status = score >= 75 ? 'Healthy' : score >= 55 ? 'Moderate' : 'Needs attention'

  return (
    <div className="relative grid place-items-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-[135deg]">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="var(--muted)"
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={`${dash} ${c}`}
        />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={`${dash} ${c}`}
          initial={{ strokeDashoffset: dash }}
          whileInView={{ strokeDashoffset: offset }}
          viewport={{ once: true }}
          transition={{ duration: 1.4, ease: [0.22, 1, 0.36, 1] }}
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="font-display text-4xl font-extrabold text-foreground">
          {Math.round(score)}
        </span>
        <span className="text-xs font-medium text-muted-foreground">/ 100</span>
        <span className="mt-1 text-sm font-semibold" style={{ color }}>
          {status}
        </span>
        <span className="text-[11px] text-muted-foreground">{label}</span>
      </div>
    </div>
  )
}
