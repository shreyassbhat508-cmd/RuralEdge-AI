'use client'

import { motion, type HTMLMotionProps } from 'framer-motion'

export function Reveal({
  children,
  delay = 0,
  y = 18,
  className,
  ...props
}: {
  children: React.ReactNode
  delay?: number
  y?: number
} & HTMLMotionProps<'div'>) {
  return (
    <motion.div
      initial={{ opacity: 0, y }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-80px' }}
      transition={{ duration: 0.6, delay, ease: [0.22, 1, 0.36, 1] }}
      className={className}
      {...props}
    >
      {children}
    </motion.div>
  )
}
