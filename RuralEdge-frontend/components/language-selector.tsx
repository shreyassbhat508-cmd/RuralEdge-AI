'use client'

import { Check, Globe, ChevronDown } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { LANGUAGES } from '@/lib/data'
import { useBusiness } from '@/components/business-context'
import { cn } from '@/lib/utils'

export function LanguageSelector({ className }: { className?: string }) {
  const { language, setLanguage } = useBusiness()
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)
  const current = LANGUAGES.find((l) => l.code === language) ?? LANGUAGES[0]

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', onClick)
    return () => document.removeEventListener('mousedown', onClick)
  }, [])

  return (
    <div ref={ref} className={cn('relative', className)}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-haspopup="listbox"
        aria-expanded={open}
        className="inline-flex items-center gap-1.5 rounded-full border border-border bg-card px-3 py-2 text-sm font-medium transition-colors hover:bg-muted"
      >
        <Globe className="size-4 text-primary" />
        <span className="hidden sm:inline">{current.native}</span>
        <ChevronDown className="size-3.5 text-muted-foreground" />
      </button>
      {open && (
        <ul
          role="listbox"
          className="absolute right-0 z-50 mt-2 w-44 overflow-hidden rounded-xl border border-border bg-popover py-1 shadow-lift"
        >
          {LANGUAGES.map((l) => (
            <li key={l.code}>
              <button
                type="button"
                role="option"
                aria-selected={l.code === language}
                onClick={() => {
                  setLanguage(l.code)
                  setOpen(false)
                }}
                className="flex w-full items-center justify-between px-3 py-2 text-sm hover:bg-muted"
              >
                <span>
                  <span className="font-medium">{l.native}</span>{' '}
                  <span className="text-xs text-muted-foreground">
                    {l.label}
                  </span>
                </span>
                {l.code === language && (
                  <Check className="size-4 text-primary" />
                )}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
