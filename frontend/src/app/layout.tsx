import type { Metadata } from 'next'
import { Cairo } from 'next/font/google'
import './globals.css'

const cairo = Cairo({ 
  subsets: ['arabic'],
  weight: ['300', '400', '500', '600', '700', '800']
})

export const metadata: Metadata = {
  title: 'AutoCreator AI - وكيل الذكاء الاصطناعي لصناعة المحتوى',
  description: 'منصة ذكية متكاملة لصناعة ونشر المحتوى على يوتيوب باستخدام الذكاء الاصطناعي',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ar" dir="rtl">
      <body className={cairo.className}>{children}</body>
    </html>
  )
}
