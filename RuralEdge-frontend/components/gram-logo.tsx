import { cn } from '@/lib/utils'

export function GramMark({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 40 40"
      className={cn('size-9', className)}
      role="img"
      aria-label="RuralEdge logo"
      fill="none"
    >
      {/* Navy background badge */}
      <rect width="40" height="40" rx="11" fill="var(--charcoal)" />
      {/* Terracotta bridge / path arch */}
      <path
        d="M8 27c3.2-5 7.4-7.5 12-7.5S28.8 22 32 27"
        stroke="var(--primary)"
        strokeWidth="2.4"
        strokeLinecap="round"
      />
      {/* Sand baseline */}
      <path
        d="M8 30.5h24"
        stroke="var(--sand)"
        strokeWidth="1.6"
        strokeOpacity="0.7"
        strokeLinecap="round"
      />
      {/* Sage growth stalk */}
      <path
        d="M20 30.5V15"
        stroke="var(--muted)"
        strokeWidth="2.4"
        strokeLinecap="round"
      />
      {/* Terracotta & Sage leaves */}
      <path
        d="M20 16c0-4 2.4-6.6 6-7-0.2 3.9-2.3 6.6-6 7Z"
        fill="var(--primary)"
      />
      <path
        d="M20 20.5c0-3.3-2-5.6-5-6 .1 3.2 1.9 5.5 5 6Z"
        fill="var(--muted)"
      />
    </svg>
  )
}

export function GramLogo({
  className,
  markClassName,
}: {
  className?: string
  markClassName?: string
}) {
  return (
    <span className={cn('inline-flex items-center gap-2.5', className)}>
      <GramMark className={markClassName} />
      <span className="flex flex-col leading-none">
        <span className="font-display text-lg font-extrabold tracking-tight text-foreground">
          RuralEdge
        </span>
        <span className="text-[10px] font-semibold tracking-[0.14em] text-muted-foreground uppercase">
          Smart Advisory
        </span>
      </span>
    </span>
  )
}

