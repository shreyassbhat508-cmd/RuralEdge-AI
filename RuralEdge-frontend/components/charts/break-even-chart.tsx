'use client'

import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceDot,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { formatCompactINR } from '@/lib/data'

export function BreakEvenChart({
  data,
  breakEvenMonth,
}: {
  data: { month: number; cumulative: number; investment: number }[]
  breakEvenMonth: number
}) {
  const be = data.find((d) => d.month === breakEvenMonth)
  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={data} margin={{ left: 4, right: 12, top: 8 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
        <XAxis
          dataKey="month"
          tickLine={false}
          axisLine={false}
          tick={{ fill: 'var(--muted-foreground)', fontSize: 12 }}
          tickFormatter={(v) => `M${v}`}
        />
        <YAxis
          tickFormatter={(v) => formatCompactINR(v).replace('₹', '')}
          tickLine={false}
          axisLine={false}
          width={48}
          tick={{ fill: 'var(--muted-foreground)', fontSize: 12 }}
        />
        <Tooltip
          formatter={(v: number, n) => [
            formatCompactINR(v),
            n === 'cumulative' ? 'Cumulative profit' : 'Investment',
          ]}
          labelFormatter={(l) => `Month ${l}`}
          contentStyle={{
            borderRadius: 12,
            border: '1px solid var(--border)',
            background: 'var(--popover)',
            fontSize: 13,
          }}
        />
        <Line
          type="monotone"
          dataKey="investment"
          stroke="var(--chart-3)"
          strokeWidth={2}
          strokeDasharray="5 5"
          dot={false}
        />
        <Line
          type="monotone"
          dataKey="cumulative"
          stroke="var(--chart-1)"
          strokeWidth={2.5}
          dot={false}
        />
        {be && (
          <ReferenceDot
            x={be.month}
            y={be.cumulative}
            r={6}
            fill="var(--chart-2)"
            stroke="var(--card)"
            strokeWidth={2}
          />
        )}
      </LineChart>
    </ResponsiveContainer>
  )
}
