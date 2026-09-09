import { cn } from '@/lib/utils'

type Tone =
  | 'neutral'
  | 'forest'
  | 'leaf'
  | 'primary'
  | 'charcoal'
  | 'muted'
  | 'sand'
  | 'gold'
  | 'success'
  | 'warning'
  | 'danger'

const tones: Record<Tone, string> = {
  neutral: 'bg-muted text-muted-foreground',
  forest: 'bg-charcoal/10 text-charcoal dark:bg-charcoal/40 dark:text-foreground',
  leaf: 'bg-muted/15 text-muted dark:text-muted',
  primary: 'bg-primary/12 text-primary border border-primary/20',
  charcoal: 'bg-charcoal/10 text-charcoal dark:bg-charcoal/40 dark:text-foreground',
  muted: 'bg-muted/15 text-muted dark:text-muted',
  sand: 'bg-sand/40 text-brown dark:bg-sand/20 dark:text-sand',
  gold: 'bg-sand/50 text-brown dark:bg-sand/30 dark:text-sand',
  success: 'bg-success/12 text-success',
  warning: 'bg-warning/18 text-warning',
  danger: 'bg-danger/12 text-danger',
}

export function Badge({
  tone = 'neutral',
  className,
  ...props
}: React.HTMLAttributes<HTMLSpanElement> & { tone?: Tone }) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold',
        tones[tone],
        className,
      )}
      {...props}
    />
  )
}

export function statusTone(
  status: 'Healthy' | 'Moderate' | 'Attention' | 'High Risk' | string,
): Tone {
  switch (status) {
    case 'Healthy':
      return 'success'
    case 'Moderate':
      return 'gold'
    case 'Attention':
      return 'warning'
    case 'High Risk':
      return 'danger'
    default:
      return 'neutral'
  }
}
