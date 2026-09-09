'use client'

import { Milk, Wheat, Store, Scissors, Landmark, Utensils, Palette, Wrench, Building } from 'lucide-react'
import type { BusinessType } from '@/lib/data'

interface Business3DBadgeProps {
  type: BusinessType
  size?: 'sm' | 'md' | 'lg'
  active?: boolean
}

const BADGE_CONFIG: Record<
  BusinessType,
  { icon: React.ElementType; label: string; color: string; bg: string; shadow: string }
> = {
  dairy: {
    icon: Milk,
    label: 'Dairy',
    color: 'text-primary dark:text-primary',
    bg: 'from-primary/20 to-sand/20',
    shadow: 'shadow-primary/20',
  },
  poultry: {
    icon: Building,
    label: 'Poultry',
    color: 'text-amber-700 dark:text-amber-400',
    bg: 'from-amber-500/20 to-sand/20',
    shadow: 'shadow-amber-500/20',
  },
  farming: {
    icon: Wheat,
    label: 'Farming',
    color: 'text-muted dark:text-muted',
    bg: 'from-muted/25 to-sand/20',
    shadow: 'shadow-muted/20',
  },
  retail: {
    icon: Store,
    label: 'Retail',
    color: 'text-charcoal dark:text-sand',
    bg: 'from-charcoal/20 to-sand/20',
    shadow: 'shadow-charcoal/20',
  },
  textiles: {
    icon: Scissors,
    label: 'Textiles',
    color: 'text-primary dark:text-primary',
    bg: 'from-primary/20 to-sand/20',
    shadow: 'shadow-primary/20',
  },
  food: {
    icon: Utensils,
    label: 'Food Processing',
    color: 'text-primary-hover dark:text-primary',
    bg: 'from-primary/20 to-sand/20',
    shadow: 'shadow-primary/20',
  },
  handicrafts: {
    icon: Palette,
    label: 'Handicrafts',
    color: 'text-charcoal dark:text-sand',
    bg: 'from-charcoal/20 to-sand/20',
    shadow: 'shadow-charcoal/20',
  },
  services: {
    icon: Wrench,
    label: 'Services',
    color: 'text-charcoal dark:text-sand',
    bg: 'from-charcoal/20 to-sand/20',
    shadow: 'shadow-charcoal/20',
  },
  other: {
    icon: Landmark,
    label: 'Other',
    color: 'text-charcoal dark:text-sand',
    bg: 'from-charcoal/20 to-sand/20',
    shadow: 'shadow-charcoal/20',
  },
}

export function Business3DBadge({ type, size = 'md', active = false }: Business3DBadgeProps) {
  const config = BADGE_CONFIG[type] || BADGE_CONFIG.other
  const Icon = config.icon

  const sizeClasses = {
    sm: 'size-10 text-xs',
    md: 'size-14 text-sm',
    lg: 'size-20 text-base',
  }[size]

  const iconSizes = {
    sm: 'size-4.5',
    md: 'size-6',
    lg: 'size-9',
  }[size]

  return (
    <div
      className={`group relative grid ${sizeClasses} place-items-center rounded-2xl bg-gradient-to-br ${config.bg} border border-border/70 backdrop-blur-md transition-all duration-300 ${
        active
          ? `scale-110 shadow-lg ${config.shadow} border-primary/50 ring-2 ring-primary/40`
          : 'hover:scale-105 hover:border-border'
      }`}
    >
      <div className="absolute inset-0 rounded-2xl bg-white/5 opacity-0 transition-opacity group-hover:opacity-100" />
      <Icon className={`${iconSizes} ${config.color} transition-transform group-hover:rotate-6`} />
    </div>
  )
}
