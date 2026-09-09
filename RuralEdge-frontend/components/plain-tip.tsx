'use client'

import { Info } from 'lucide-react'
import { useState } from 'react'
import { cn } from '@/lib/utils'

/**
 * A plain-language explanation tip shown next to a financial term.
 * Opens on hover and keyboard focus so it works for low-literacy users too.
 */
export function PlainTip({
  text,
  className,
  label = 'What does this mean?',
}: {
  text: string
  className?: string
  label?: string
}) {
  const [open, setOpen] = useState(false)

  return (
    <span className={cn('relative inline-flex', className)}>
      <button
        type="button"
        aria-label={label}
        className="grid size-5 place-items-center rounded-full text-muted-foreground transition-colors hover:bg-muted hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none"
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
        onFocus={() => setOpen(true)}
        onBlur={() => setOpen(false)}
        onClick={() => setOpen((v) => !v)}
      >
        <Info className="size-4" />
      </button>
      {open && (
        <span
          role="tooltip"
          className="absolute bottom-full left-1/2 z-30 mb-2 w-56 -translate-x-1/2 rounded-xl border border-border bg-popover p-3 text-left text-xs leading-relaxed text-popover-foreground shadow-lift"
        >
          {text}
        </span>
      )}
    </span>
  )
}
