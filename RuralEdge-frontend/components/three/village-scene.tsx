'use client'

import { Canvas, useFrame, useThree } from '@react-three/fiber'
import {
  ContactShadows,
  Environment,
  Float,
  RoundedBox,
} from '@react-three/drei'
import { useMemo, useRef } from 'react'
import * as THREE from 'three'
import { useTheme } from '@/components/theme-provider'

const COLORS = {
  fieldA: '#7C8B72',
  fieldB: '#93A289',
  soil: '#C96A45',
  road: '#E7D8C9',
  wall: '#F8F5EF',
  wallWarm: '#F1E7DA',
  roofRed: '#C96A45',
  roofGreen: '#7C8B72',
  roofClay: '#A94F35',
  tree: '#66755C',
  treeDark: '#4E5A46',
  water: '#5A7584',
  metal: '#17202A',
  solar: '#17202A',
  wood: '#8C5A3E',
  crop: '#D8A668',
  accentGreen: '#7C8B72',
  accentGold: '#C96A45',
  accentBlue: '#17202A',
}

const DARK_COLORS = {
  fieldA: '#232D21',
  fieldB: '#2B3728',
  soil: '#331E17',
  road: '#303941',
  wall: '#192127',
  wallWarm: '#1F2933',
  roofRed: '#944225',
  roofGreen: '#404C39',
  roofClay: '#7A3620',
  tree: '#3A4734',
  treeDark: '#273223',
  water: '#2B3D47',
  metal: '#303941',
  solar: '#11161B',
  wood: '#523122',
  crop: '#8C6B3E',
}

export interface HotspotInfo {
  id: string
  label: string
  category: string
  pos: [number, number, number]
  color: string
}

export const HOTSPOTS: HotspotInfo[] = [
  { id: 'dairy', label: 'DAIRY', category: 'Local dairy businesses', pos: [-2.6, 2.2, 2.6], color: '#C96A45' },
  { id: 'market', label: 'MARKET', category: 'Retail & local commerce', pos: [-2.9, 1.8, -0.4], color: '#17202A' },
  { id: 'farms', label: 'FARMS', category: 'Agricultural activity', pos: [3.9, 1.4, -3.9], color: '#7C8B72' },
  { id: 'textiles', label: 'TEXTILES', category: 'Local craft & production', pos: [2.6, 1.8, 2.4], color: '#A94F35' },
  { id: 'finance', label: 'FINANCE', category: 'Potential business financing', pos: [-0.2, 2.2, 4.4], color: '#C96A45' },
]

function Ground({ isDark }: { isDark: boolean }) {
  const c = isDark ? DARK_COLORS : COLORS
  return (
    <group>
      {/* Base terrain */}
      <RoundedBox
        args={[16, 1, 16]}
        radius={0.35}
        smoothness={4}
        position={[0, -0.5, 0]}
        receiveShadow
      >
        <meshStandardMaterial color={isDark ? '#192127' : '#E7D8C9'} roughness={0.95} />
      </RoundedBox>
      {/* Field patches with crop rows */}
      {[
        { pos: [-4.2, 0.01, -3.6], c: c.fieldA },
        { pos: [-4.2, 0.01, 1.4], c: c.fieldB },
        { pos: [3.9, 0.01, -3.9], c: c.soil },
      ].map((f, i) => (
        <group key={i} position={f.pos as [number, number, number]}>
          <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
            <planeGeometry args={[5.4, 4.4]} />
            <meshStandardMaterial color={f.c} roughness={1} />
          </mesh>
          {Array.from({ length: 9 }).map((_, r) => (
            <mesh
              key={r}
              position={[-2.3 + r * 0.55, 0.03, 0]}
              castShadow
            >
              <boxGeometry args={[0.08, 0.14, 4]} />
              <meshStandardMaterial color={c.treeDark} roughness={1} />
            </mesh>
          ))}
        </group>
      ))}
    </group>
  )
}

function Road({ isDark }: { isDark: boolean }) {
  const c = isDark ? DARK_COLORS : COLORS
  return (
    <group>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.02, 0]} receiveShadow>
        <planeGeometry args={[2, 16]} />
        <meshStandardMaterial color={c.road} roughness={1} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, Math.PI / 2]} position={[0, 0.021, 1]} receiveShadow>
        <planeGeometry args={[1.4, 16]} />
        <meshStandardMaterial color={c.road} roughness={1} />
      </mesh>
      {/* Dashed line */}
      {Array.from({ length: 8 }).map((_, i) => (
        <mesh
          key={i}
          rotation={[-Math.PI / 2, 0, 0]}
          position={[0, 0.03, -6.5 + i * 1.8]}
        >
          <planeGeometry args={[0.12, 0.7]} />
          <meshStandardMaterial color={isDark ? '#6b6456' : '#f2ead8'} roughness={1} />
        </mesh>
      ))}
    </group>
  )
}

function House({
  position,
  wall = COLORS.wall,
  roof = COLORS.roofRed,
  rotation = 0,
  scale = 1,
  isDark = false,
}: {
  position: [number, number, number]
  wall?: string
  roof?: string
  rotation?: number
  scale?: number
  isDark?: boolean
}) {
  return (
    <group position={position} rotation={[0, rotation, 0]} scale={scale}>
      <RoundedBox args={[1.2, 0.9, 1.2]} radius={0.06} position={[0, 0.45, 0]} castShadow receiveShadow>
        <meshStandardMaterial color={isDark ? DARK_COLORS.wall : wall} roughness={0.8} />
      </RoundedBox>
      <mesh position={[0, 1.05, 0]} rotation={[0, Math.PI / 4, 0]} castShadow>
        <coneGeometry args={[1.05, 0.6, 4]} />
        <meshStandardMaterial color={isDark ? DARK_COLORS.roofRed : roof} roughness={0.7} />
      </mesh>
      <mesh position={[0, 0.32, 0.61]}>
        <boxGeometry args={[0.32, 0.5, 0.04]} />
        <meshStandardMaterial color={COLORS.wood} roughness={0.7} />
      </mesh>
      {/* Window glow in dark mode */}
      {isDark && (
        <mesh position={[0.3, 0.5, 0.61]}>
          <planeGeometry args={[0.2, 0.2]} />
          <meshBasicMaterial color="#fcd34d" />
        </mesh>
      )}
    </group>
  )
}

function DairyShed({ position, isDark }: { position: [number, number, number]; isDark: boolean }) {
  return (
    <group position={position}>
      <RoundedBox args={[2.6, 0.8, 1.4]} radius={0.05} position={[0, 0.4, 0]} castShadow receiveShadow>
        <meshStandardMaterial color={isDark ? DARK_COLORS.wallWarm : COLORS.wallWarm} roughness={0.85} />
      </RoundedBox>
      <mesh position={[0, 0.95, 0]} rotation={[0, 0, 0]} castShadow>
        <cylinderGeometry args={[0.72, 0.72, 2.62, 12, 1, false, 0, Math.PI]} />
        <meshStandardMaterial color={isDark ? DARK_COLORS.roofGreen : COLORS.roofGreen} side={THREE.DoubleSide} roughness={0.7} />
      </mesh>
      {/* Milk cans */}
      {[-0.9, -0.4, 0.1].map((x, i) => (
        <mesh key={i} position={[x, 0.28, 0.95]} castShadow>
          <cylinderGeometry args={[0.16, 0.18, 0.5, 12]} />
          <meshStandardMaterial color={COLORS.metal} metalness={0.6} roughness={0.3} />
        </mesh>
      ))}
    </group>
  )
}

function Store({ position, isDark }: { position: [number, number, number]; isDark: boolean }) {
  return (
    <group position={position}>
      <RoundedBox args={[1.5, 1, 1.3]} radius={0.06} position={[0, 0.5, 0]} castShadow receiveShadow>
        <meshStandardMaterial color={isDark ? '#2f2b24' : '#eadfce'} roughness={0.85} />
      </RoundedBox>
      {/* Awning */}
      <mesh position={[0, 0.86, 0.72]} rotation={[Math.PI / 7, 0, 0]} castShadow>
        <boxGeometry args={[1.6, 0.05, 0.5]} />
        <meshStandardMaterial color={isDark ? DARK_COLORS.roofClay : COLORS.roofClay} roughness={0.7} />
      </mesh>
      {[-0.45, 0, 0.45].map((x, i) => (
        <mesh key={i} position={[x, 0.9, 0.72]}>
          <boxGeometry args={[0.24, 0.05, 0.5]} />
          <meshStandardMaterial color={i % 2 ? (isDark ? '#2a332d' : '#f3ece0') : COLORS.roofClay} />
        </mesh>
      ))}
    </group>
  )
}

function TextileWorkspace({ position, isDark }: { position: [number, number, number]; isDark: boolean }) {
  return (
    <group position={position}>
      <RoundedBox args={[1.6, 0.7, 1.1]} radius={0.05} position={[0, 0.35, 0]} castShadow receiveShadow>
        <meshStandardMaterial color={isDark ? '#3b2f2f' : '#f4e6d4'} roughness={0.8} />
      </RoundedBox>
      {/* Loom frame */}
      <mesh position={[0, 0.85, 0]}>
        <boxGeometry args={[1.2, 0.4, 0.8]} />
        <meshStandardMaterial color={COLORS.wood} roughness={0.7} />
      </mesh>
      {/* Fabric rolls */}
      {[-0.4, 0, 0.4].map((x, i) => (
        <mesh key={i} position={[x, 0.3, 0.65]} rotation={[0, 0, Math.PI / 2]}>
          <cylinderGeometry args={[0.12, 0.12, 0.3, 12]} />
          <meshStandardMaterial color={['#e11d48', '#0284c7', '#d97706'][i]} roughness={0.6} />
        </mesh>
      ))}
    </group>
  )
}

function Tree({
  position,
  scale = 1,
  isDark = false,
}: {
  position: [number, number, number]
  scale?: number
  isDark?: boolean
}) {
  const ref = useRef<THREE.Group>(null)
  const seed = useMemo(() => Math.random() * 10, [])
  useFrame((state) => {
    if (ref.current)
      ref.current.rotation.z = Math.sin(state.clock.elapsedTime * 0.8 + seed) * 0.04
  })
  return (
    <group ref={ref} position={position} scale={scale}>
      <mesh position={[0, 0.35, 0]} castShadow>
        <cylinderGeometry args={[0.09, 0.12, 0.7, 8]} />
        <meshStandardMaterial color={COLORS.wood} roughness={0.9} />
      </mesh>
      <mesh position={[0, 0.95, 0]} castShadow>
        <icosahedronGeometry args={[0.55, 0]} />
        <meshStandardMaterial color={isDark ? DARK_COLORS.tree : COLORS.tree} flatShading roughness={0.9} />
      </mesh>
      <mesh position={[0.15, 1.3, 0.1]} castShadow>
        <icosahedronGeometry args={[0.32, 0]} />
        <meshStandardMaterial color={isDark ? DARK_COLORS.treeDark : COLORS.treeDark} flatShading roughness={0.9} />
      </mesh>
    </group>
  )
}

function WaterTank({ position, isDark }: { position: [number, number, number]; isDark: boolean }) {
  return (
    <group position={position}>
      {[-0.3, 0.3].map((x) =>
        [-0.3, 0.3].map((z, i) => (
          <mesh key={`${x}-${z}-${i}`} position={[x, 0.5, z]} castShadow>
            <cylinderGeometry args={[0.05, 0.05, 1, 6]} />
            <meshStandardMaterial color={COLORS.metal} metalness={0.4} roughness={0.5} />
          </mesh>
        )),
      )}
      <mesh position={[0, 1.15, 0]} castShadow>
        <cylinderGeometry args={[0.5, 0.5, 0.6, 16]} />
        <meshStandardMaterial color={isDark ? DARK_COLORS.water : COLORS.water} roughness={0.4} metalness={0.2} />
      </mesh>
    </group>
  )
}

function Tractor() {
  const ref = useRef<THREE.Group>(null)
  useFrame((state) => {
    if (ref.current) {
      const t = (state.clock.elapsedTime * 0.35) % 12
      ref.current.position.z = -6 + t
    }
  })
  return (
    <group ref={ref} position={[0.45, 0, -6]} scale={0.65} rotation={[0, 0, 0]}>
      <RoundedBox args={[0.7, 0.4, 0.5]} radius={0.05} position={[0, 0.4, 0]} castShadow>
        <meshStandardMaterial color={COLORS.roofGreen} roughness={0.6} />
      </RoundedBox>
      <RoundedBox args={[0.4, 0.35, 0.45]} radius={0.04} position={[0.35, 0.65, 0]} castShadow>
        <meshStandardMaterial color="#3f5a37" roughness={0.6} />
      </RoundedBox>
      <mesh position={[-0.28, 0.28, 0.32]} rotation={[Math.PI / 2, 0, 0]} castShadow>
        <cylinderGeometry args={[0.28, 0.28, 0.12, 16]} />
        <meshStandardMaterial color="#2b2b2b" roughness={0.8} />
      </mesh>
      <mesh position={[-0.28, 0.28, -0.32]} rotation={[Math.PI / 2, 0, 0]} castShadow>
        <cylinderGeometry args={[0.28, 0.28, 0.12, 16]} />
        <meshStandardMaterial color="#2b2b2b" roughness={0.8} />
      </mesh>
      <mesh position={[0.35, 0.2, 0.3]} rotation={[Math.PI / 2, 0, 0]} castShadow>
        <cylinderGeometry args={[0.16, 0.16, 0.1, 16]} />
        <meshStandardMaterial color="#2b2b2b" roughness={0.8} />
      </mesh>
      <mesh position={[0.35, 0.2, -0.3]} rotation={[Math.PI / 2, 0, 0]} castShadow>
        <cylinderGeometry args={[0.16, 0.16, 0.1, 16]} />
        <meshStandardMaterial color="#2b2b2b" roughness={0.8} />
      </mesh>
    </group>
  )
}

function DeliveryVehicle() {
  const ref = useRef<THREE.Group>(null)
  useFrame((state) => {
    if (ref.current) {
      const t = (state.clock.elapsedTime * 0.4) % 14
      ref.current.position.x = 6 - t
    }
  })
  return (
    <group ref={ref} position={[6, 0, 1]} scale={0.5} rotation={[0, Math.PI / 2, 0]}>
      <RoundedBox args={[1.4, 0.6, 0.6]} radius={0.04} position={[0, 0.45, 0]} castShadow>
        <meshStandardMaterial color="#38bdf8" roughness={0.5} />
      </RoundedBox>
      <mesh position={[0.8, 0.35, 0]} castShadow>
        <boxGeometry args={[0.4, 0.5, 0.58]} />
        <meshStandardMaterial color="#e0f2fe" roughness={0.4} />
      </mesh>
      {[-0.4, 0.6].map((x, i) => (
        <mesh key={i} position={[x, 0.18, 0.31]} rotation={[Math.PI / 2, 0, 0]}>
          <cylinderGeometry args={[0.18, 0.18, 0.08, 12]} />
          <meshStandardMaterial color="#1e293b" />
        </mesh>
      ))}
    </group>
  )
}

function SolarPanels({ position }: { position: [number, number, number] }) {
  return (
    <group position={position}>
      {[-0.5, 0.5].map((x) => (
        <group key={x} position={[x, 0, 0]}>
          <mesh position={[0, 0.2, 0]}>
            <boxGeometry args={[0.04, 0.4, 0.04]} />
            <meshStandardMaterial color={COLORS.metal} />
          </mesh>
          <mesh position={[0, 0.42, 0]} rotation={[-Math.PI / 5, 0, 0]} castShadow>
            <boxGeometry args={[0.8, 0.02, 0.5]} />
            <meshStandardMaterial color={COLORS.solar} metalness={0.7} roughness={0.2} />
          </mesh>
        </group>
      ))}
    </group>
  )
}

function HotspotNode({
  hotspot,
  selected,
  onSelect,
}: {
  hotspot: HotspotInfo
  selected: boolean
  onSelect?: (id: string) => void
}) {
  const ref = useRef<THREE.Mesh>(null)
  useFrame((state) => {
    if (ref.current) {
      ref.current.rotation.y = state.clock.elapsedTime * 1.5
      const s = 1 + Math.sin(state.clock.elapsedTime * 3) * 0.1
      ref.current.scale.set(s, s, s)
    }
  })

  return (
    <Float speed={2.5} rotationIntensity={0.3} floatIntensity={0.6} position={hotspot.pos}>
      <mesh
        ref={ref}
        onClick={(e) => {
          e.stopPropagation()
          onSelect?.(hotspot.id)
        }}
        onPointerOver={() => {
          document.body.style.cursor = 'pointer'
        }}
        onPointerOut={() => {
          document.body.style.cursor = 'auto'
        }}
      >
        <icosahedronGeometry args={[selected ? 0.22 : 0.16, 0]} />
        <meshStandardMaterial
          color={hotspot.color}
          emissive={hotspot.color}
          emissiveIntensity={selected ? 1.2 : 0.7}
          roughness={0.2}
        />
      </mesh>
    </Float>
  )
}

function Particles({ isDark }: { isDark: boolean }) {
  const ref = useRef<THREE.Points>(null)
  const geo = useMemo(() => {
    const g = new THREE.BufferGeometry()
    const count = 75
    const arr = new Float32Array(count * 3)
    for (let i = 0; i < count; i++) {
      arr[i * 3] = (Math.random() - 0.5) * 14
      arr[i * 3 + 1] = Math.random() * 5 + 0.5
      arr[i * 3 + 2] = (Math.random() - 0.5) * 14
    }
    g.setAttribute('position', new THREE.BufferAttribute(arr, 3))
    return g
  }, [])
  useFrame((state) => {
    if (ref.current) ref.current.rotation.y = state.clock.elapsedTime * 0.03
  })
  return (
    <points ref={ref} geometry={geo}>
      <pointsMaterial size={0.07} color={isDark ? '#86efac' : '#cbe08a'} transparent opacity={0.75} />
    </points>
  )
}

function Clouds({ isDark }: { isDark: boolean }) {
  const ref = useRef<THREE.Group>(null)
  useFrame((state) => {
    if (ref.current) {
      ref.current.position.x = ((state.clock.elapsedTime * 0.12) % 22) - 11
    }
  })
  const puff = (p: [number, number, number], s: number) => (
    <mesh position={p}>
      <sphereGeometry args={[s, 12, 12]} />
      <meshStandardMaterial color={isDark ? '#273429' : '#f7f4ec'} roughness={1} />
    </mesh>
  )
  return (
    <group ref={ref} position={[0, 5, -3]}>
      {puff([0, 0, 0], 0.7)}
      {puff([0.7, 0.1, 0], 0.55)}
      {puff([-0.7, 0.05, 0], 0.5)}
      {puff([4, 0.5, -2], 0.6)}
      {puff([4.7, 0.6, -2], 0.45)}
    </group>
  )
}

function SceneContent({
  isDark,
  selectedHotspot,
  onSelectHotspot,
}: {
  isDark: boolean
  selectedHotspot: string | null
  onSelectHotspot?: (id: string) => void
}) {
  const group = useRef<THREE.Group>(null)
  const { pointer } = useThree()
  useFrame(() => {
    if (group.current) {
      group.current.rotation.y = THREE.MathUtils.lerp(
        group.current.rotation.y,
        pointer.x * 0.24,
        0.05,
      )
      group.current.rotation.x = THREE.MathUtils.lerp(
        group.current.rotation.x,
        -pointer.y * 0.09,
        0.05,
      )
    }
  })

  return (
    <>
      <ambientLight intensity={isDark ? 0.4 : 0.75} />
      <directionalLight
        position={[6, 9, 4]}
        intensity={isDark ? 0.9 : 1.6}
        color={isDark ? '#93c5fd' : '#fff2d6'}
        castShadow
        shadow-mapSize={[1024, 1024]}
      />
      <hemisphereLight args={isDark ? ['#1e293b', '#14241b', 0.4] : ['#cfe6ff', '#8a7d5f', 0.5]} />

      <group ref={group} position={[0, -0.2, 0]}>
        <Ground isDark={isDark} />
        <Road isDark={isDark} />
        <DairyShed position={[-2.6, 0, 2.6]} isDark={isDark} />
        <House position={[2.6, 0, 2.4]} roof={COLORS.roofRed} rotation={-0.3} isDark={isDark} />
        <House position={[3.4, 0, 0.4]} wall={COLORS.wallWarm} roof={COLORS.roofClay} rotation={-0.6} scale={0.9} isDark={isDark} />
        <Store position={[-2.9, 0, -0.4]} isDark={isDark} />
        <TextileWorkspace position={[2.6, 0, 2.4]} isDark={isDark} />
        <House position={[-3.6, 0, -2.6]} roof={COLORS.roofGreen} rotation={0.4} scale={0.85} isDark={isDark} />
        <WaterTank position={[2.7, 0, -2.5]} isDark={isDark} />
        <SolarPanels position={[-0.2, 0, 4.4]} />
        <Tractor />
        <DeliveryVehicle />

        <Tree position={[1.4, 0, 3.4]} scale={1.1} isDark={isDark} />
        <Tree position={[-1.4, 0, 4.6]} scale={0.9} isDark={isDark} />
        <Tree position={[4.4, 0, -1.6]} scale={1} isDark={isDark} />
        <Tree position={[-4.4, 0, 3.2]} scale={0.8} isDark={isDark} />
        <Tree position={[1.6, 0, -4.4]} scale={0.95} isDark={isDark} />

        {HOTSPOTS.map((spot) => (
          <HotspotNode
            key={spot.id}
            hotspot={spot}
            selected={selectedHotspot === spot.id}
            onSelect={onSelectHotspot}
          />
        ))}

        <Particles isDark={isDark} />

        <ContactShadows
          position={[0, 0.02, 0]}
          opacity={isDark ? 0.5 : 0.35}
          scale={20}
          blur={2.4}
          far={6}
          color={isDark ? '#09120b' : '#3c4a2a'}
        />
      </group>

      <Clouds isDark={isDark} />
      <Environment preset={isDark ? 'night' : 'sunset'} />
    </>
  )
}

export default function VillageScene({
  selectedHotspot = null,
  onSelectHotspot,
}: {
  selectedHotspot?: string | null
  onSelectHotspot?: (id: string) => void
}) {
  const { theme } = useTheme()
  const isDark = theme === 'dark'
  const bgColor = isDark ? '#0f1511' : '#eef1e4'

  return (
    <Canvas
      shadows
      dpr={[1, 1.8]}
      camera={{ position: [7, 5.5, 7], fov: 38 }}
      gl={{ antialias: true }}
    >
      <color attach="background" args={[bgColor]} />
      <fog attach="fog" args={[bgColor, 14, 26]} />
      <SceneContent isDark={isDark} selectedHotspot={selectedHotspot} onSelectHotspot={onSelectHotspot} />
    </Canvas>
  )
}
