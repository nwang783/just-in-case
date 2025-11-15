import type { Metadata } from 'next'
import '../index.css'

export const metadata: Metadata = {
  title: 'Company Directory',
  description: 'Browse and discover companies',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
