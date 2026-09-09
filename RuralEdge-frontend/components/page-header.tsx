import { cn } from '@/lib/utils'

export function PageHeader({
  eyebrow,
  title,
  description,
  children,
  className,
}: {
  eyebrow?: string
  title: string
  description?: string
  children?: React.ReactNode
  className?: string
}) {
  return (
    <div
      className={cn(
        'border-b border-border bg-secondary/30 bg-contour',
        className,
      )}
    >
      <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-8 sm:px-6 md:flex-row md:items-end md:justify-between md:py-10">
        <div className="max-w-2xl">
          {eyebrow && (
            <p className="mb-2 text-xs font-semibold tracking-[0.16em] text-primary uppercase">
              {eyebrow}
            </p>
          )}
          <h1 className="font-display text-3xl font-extrabold tracking-tight text-balance md:text-4xl">
            {title}
          </h1>
          {description && (
            <p className="mt-3 text-base leading-relaxed text-muted-foreground md:text-lg">
              {description}
            </p>
          )}
        </div>
        {children && <div className="shrink-0">{children}</div>}
      </div>
    </div>
  )
}
