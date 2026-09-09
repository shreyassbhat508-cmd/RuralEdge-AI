'use client'

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import { COST_BREAKDOWN, formatINR } from '@/lib/data'

const COLORS = [
  'var(--chart-1)',
  'var(--chart-2)',
  'var(--chart-3)',
  'var(--chart-4)',
  'var(--chart-5)',
]

export function CostBreakdownChart() {
  const total = COST_BREAKDOWN.reduce((s, c) => s + c.value, 0)
  return (
    <div className="flex flex-col items-center gap-4 sm:flex-row">
      <ResponsiveContainer width={180} height={180}>
        <PieChart>
          <Pie
            data={COST_BREAKDOWN}
            dataKey="value"
            nameKey="name"
            innerRadius={52}
            outerRadius={82}
            paddingAngle={2}
            stroke="none"
          >
            {COST_BREAKDOWN.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            formatter={(v: number, n) => [formatINR(v), n as string]}
            contentStyle={{
              borderRadius: 12,
              border: '1px solid var(--border)',
              background: 'var(--popover)',
              fontSize: 13,
            }}
          />
        </PieChart>
      </ResponsiveContainer>
      <ul className="flex-1 space-y-2.5">
        {COST_BREAKDOWN.map((c, i) => (
          <li key={c.name} className="flex items-center justify-between gap-3 text-sm">
            <span className="flex items-center gap-2">
              <span
                className="size-3 rounded-full"
                style={{ background: COLORS[i % COLORS.length] }}
              />
              {c.name}
            </span>
            <span className="font-semibold">
              {Math.round((c.value / total) * 100)}%
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}
