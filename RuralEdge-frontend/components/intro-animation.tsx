'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { GramMark } from '@/components/gram-logo'

export function IntroAnimation() {
  const [isVisible, setIsVisible] = useState(false)
  const [shouldRender, setShouldRender] = useState(false)

  useEffect(() => {
    // Check if intro has already been played in this session
    const hasPlayed = sessionStorage.getItem('ruraledge_intro_played')
    
    // Also respect prefers-reduced-motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

    if (!hasPlayed && !prefersReducedMotion) {
      setIsVisible(true)
      setShouldRender(true)
      sessionStorage.setItem('ruraledge_intro_played', 'true')
    }
  }, [])

  if (!shouldRender) return null

  return (
    <AnimatePresence onExitComplete={() => setShouldRender(false)}>
      {isVisible && (
        <motion.div
          key="intro-overlay"
          initial={{ opacity: 1 }}
          animate={{ opacity: 1 }}
          exit={{ 
            opacity: 0, 
            y: -20, 
            scale: 1.02,
            transition: { duration: 0.5, ease: [0.22, 1, 0.36, 1] } 
          }}
          // Auto-exit after 1.3 seconds so the exit animation (0.5s) completes by 1.8s
          onAnimationComplete={() => {
            setTimeout(() => {
              setIsVisible(false)
            }, 1300)
          }}
          className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-[#F7F6F0] dark:bg-[#111613]"
        >
          <div className="relative flex flex-col items-center">
            {/* Logo Mark */}
            <motion.div
              initial={{ opacity: 0, scale: 0.85, y: 15 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              transition={{ delay: 0.25, duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
            >
              <GramMark className="size-16 sm:size-20" />
            </motion.div>

            {/* Subtle Growth/Field Line underneath */}
            <motion.div
              initial={{ scaleX: 0, opacity: 0 }}
              animate={{ scaleX: 1, opacity: 1 }}
              transition={{ delay: 0.65, duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
              className="mt-4 h-0.5 w-12 rounded-full bg-primary/80 origin-left"
            />

            {/* Typography */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.9, duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
              className="mt-5 flex flex-col items-center"
            >
              <span className="font-display text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground">
                RuralEdge
              </span>
              <span className="mt-1 text-[11px] sm:text-xs font-semibold tracking-[0.2em] text-primary uppercase">
                Smart Advisory
              </span>
            </motion.div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
