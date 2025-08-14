import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Leave Request System',
  description: 'Employee Leave Request Management System',
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
