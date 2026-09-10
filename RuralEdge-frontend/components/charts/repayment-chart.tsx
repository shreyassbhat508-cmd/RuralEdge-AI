'use client'

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { formatCompactINR, type RepaymentRow } from '@/lib/data'

export function RepaymentChart({ rows }: { rows: RepaymentRow[] }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={rows} margin={{ left: 4, right: 8, top: 8 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
        <XAxis
          dataKey="label"
          tickLine={false}
          axisLine={false}
          tick={{ fill: 'var(--muted-foreground)', fontSize: 11 }}
        />
        <YAxis
          tickFormatter={(v) => formatCompactINR(v).replace('₹', '')}
          tickLine={false}
          axisLine={false}
          width={46}
          tick={{ fill: 'var(--muted-foreground)', fontSize: 11 }}
        />
        <Tooltip
          formatter={(v: any, n: any) => [
            formatCompactINR(Number(v) || 0),
            n === 'principal' ? 'Principal' : 'Interest',
          ]}
          contentStyle={{
            borderRadius: 12,
            border: '1px solid var(--border)',
            background: 'var(--popover)',
            fontSize: 13,
          }}
        />
        <Legend
          formatter={(v) => (v === 'principal' ? 'Principal' : 'Interest')}
          wrapperStyle={{ fontSize: 12 }}
        />
        <Bar dataKey="principal" stackId="a" fill="var(--chart-1)" radius={[0, 0, 0, 0]} />
        <Bar dataKey="interest" stackId="a" fill="var(--chart-4)" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
