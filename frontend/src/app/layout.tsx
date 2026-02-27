import type { Metadata } from 'next';
import './globals.css';
import { AuthProvider } from '@/context/AuthContext';
import CookieConsent from '@/components/CookieConsent/CookieConsent';

export const metadata: Metadata = {
  title: 'Cura3.ai — AI-Powered Medical Diagnostics',
  description:
    'Advanced AI agents that analyze medical reports with multi-specialist insights. Get comprehensive diagnostic assessments powered by OpenAI GPT-4.1.',
  keywords: 'AI, medical diagnostics, healthcare, machine learning, diagnosis, medical AI',
  openGraph: {
    title: 'Cura3.ai — AI-Powered Medical Diagnostics',
    description: 'Multi-specialist AI analysis for comprehensive medical diagnostics.',
    type: 'website',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          {children}
          <CookieConsent />
        </AuthProvider>
      </body>
    </html>
  );
}
