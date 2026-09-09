'use client'

import dynamic from 'next/dynamic'
import { useEffect, useState } from 'react'

const VillageScene = dynamic(() => import('./village-scene'), {
  ssr: false,
  loading: () => <SceneFallback loading />,
})

function SceneFallback({ loading = false }: { loading?: boolean }) {
  return (
    <div className="relative grid h-full w-full place-items-center bg-gradient-to-b from-background/90 via-muted/60 to-background">
      <div className="flex flex-col items-center gap-3 text-primary z-10">
        <div className="relative size-14">
          <div className="absolute inset-0 rounded-full border-2 border-primary/20" />
          {loading && (
            <div className="absolute inset-0 animate-spin rounded-full border-2 border-transparent border-t-primary" />
          )}
        </div>
        <p className="text-sm font-medium text-muted-foreground">
          {loading ? 'Building your village 3D ecosystem…' : 'Interactive rural ecosystem preview'}
        </p>
      </div>

      {/* Editorial SVG texture background fallback */}
      <svg className="absolute inset-0 size-full opacity-20 pointer-events-none" xmlns="http://www.w3.org/2000/svg">
        <pattern id="grid-pattern" width="40" height="40" patternUnits="userSpaceOnUse">
          <path d="M 40 0 L 0 0 0 40" fill="none" stroke="currentColor" strokeWidth="0.5" className="text-primary" />
        </pattern>
        <rect width="100%" height="100%" fill="url(#grid-pattern)" />
      </svg>
    </div>
  )
}

function useWebGL() {
  const [supported, setSupported] = useState<boolean | null>(null)
  useEffect(() => {
    try {
      const canvas = document.createElement('canvas')
      const gl = canvas.getContext('webgl2') || canvas.getContext('webgl')
      setSupported(!!gl)
    } catch {
      setSupported(false)
    }
  }, [])
  return supported
}

export function Hero3D({
  selectedHotspot = null,
  onSelectHotspot,
}: {
  selectedHotspot?: string | null
  onSelectHotspot?: (id: string) => void
}) {
  const supported = useWebGL()

  return (
    <div className="absolute inset-0">
      {supported === false ? (
        <SceneFallback />
      ) : supported && (
        <VillageScene selectedHotspot={selectedHotspot} onSelectHotspot={onSelectHotspot} />
      )}
      {supported === null && <SceneFallback loading />}
    </div>
  )
}
