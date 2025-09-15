export type JSONVal = string | number | boolean | null | JSONVal[] | { [k: string]: JSONVal };

const base = typeof window === 'undefined' ? 'http://localhost:3000/api' : '/api';

async function get<T>(path: string): Promise<T> {
  const r = await fetch(`${base}${path}`, { cache: 'no-store' });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

async function post<T>(path: string, body: any): Promise<T> {
  const r = await fetch(`${base}${path}`, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export const api = {
  health: () => get<{status:string,version:string}>('/health'),
  portfolio: () => get<any>('/portfolio'),
  metrics: () => get<any>('/metrics'),
  positions: () => get<any[]>('/positions'),
  symbols: () => get<any>('/symbols'),
  paperBuy: (symbol:string, alloc_eur:number) => post<any>('/paper/buy', { symbol, alloc_eur }),
  paperSell: (symbol:string, qty:number) => post<any>('/paper/sell', { symbol, qty }),
  paperClose: (symbol:string) => post<any>(`/paper/close/${symbol}`, {}),
};
