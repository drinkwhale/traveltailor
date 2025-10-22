import dynamic from 'next/dynamic'

const Hero = dynamic(
  () => import('@/components/landing/Hero').then((mod) => mod.Hero),
  {
    loading: () => (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-gray-400">Loading…</p>
      </main>
    ),
    ssr: false,
  }
)

export default function Home() {
  return <Hero />
}
