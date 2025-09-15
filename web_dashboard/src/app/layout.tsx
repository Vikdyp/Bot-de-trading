import './globals.css';
import Link from 'next/link';

export const metadata = {
  title: '💹 Binance EUR Bot',
  description: 'Dashboard de trading (paper/live) multi-crypto en EUR',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const links = [
    { href: '/', label: 'Overview' },
    { href: '/equity', label: 'Equity' },
    { href: '/positions', label: 'Positions' },
    { href: '/orders', label: 'Orders' },
    { href: '/fills', label: 'Fills' },
    { href: '/risk', label: 'Risk' },
    { href: '/strategy', label: 'Strategy' },
  ];
  return (
    <html lang="fr">
      <body>
        <nav className="nav">
          <div style={{fontWeight:800}}>💹 Binance EUR Bot</div>
          {links.map(l => (
            <Link key={l.href} href={l.href} className={typeof window !== 'undefined' && window.location.pathname===l.href ? 'active' : ''}>{l.label}</Link>
          ))}
        </nav>
        {children}
      </body>
    </html>
  );
}
