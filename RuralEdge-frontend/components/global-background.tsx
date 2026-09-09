'use client'

export function GlobalBackground() {
  return (
    <div className="fixed inset-0 z-[-1] overflow-hidden pointer-events-none">
      {/* 1. Base Image Layer */}
      <div 
        className="absolute inset-0 bg-cover bg-center transition-opacity duration-700" 
        style={{ backgroundImage: "url('/hero-bg.jpg')" }} 
      />
      
      {/* 2. Light Mode Overlay (Warm off-white/cream, 20% opacity) */}
      <div className="absolute inset-0 bg-white/20 dark:opacity-0 transition-opacity duration-500" />
      
      {/* 3. Dark Mode Overlay (Dark charcoal/black, 55% opacity) */}
      <div className="absolute inset-0 bg-[#030712]/55 opacity-0 dark:opacity-100 transition-opacity duration-500" />
    </div>
  )
}
