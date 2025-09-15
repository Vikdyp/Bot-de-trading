'use client';
import React from 'react';
import { api } from '@/lib/api';

export default function OrdersPage(){
  const [orders, setOrders] = React.useState<any[]>([]);
  const refresh = async ()=> setOrders(await api.orders?.() ?? []);
  React.useEffect(()=>{ 
    // L’endpoint /orders existe déjà chez toi, on l’a vu plus tôt
    // On le mappe via api.orders si tu l’ajoutes; en attendant fetch direct:
    (async ()=>{ 
      const r = await fetch('/api/orders'); 
      if (r.ok) setOrders(await r.json()); 
    })();
    const id=setInterval(async ()=>{
      const r = await fetch('/api/orders'); 
      if (r.ok) setOrders(await r.json());
    }, 8000);
    return ()=>clearInterval(id);
  },[]);

  return (
    <div className="container">
      <div className="card"><h3>Orders</h3></div>
      <div className="card" style={{marginTop:16}}>
        <table className="table">
          <thead><tr><th>Time</th><th>Symbol</th><th>Side</th><th>Qty</th><th>Price</th><th>Status</th></tr></thead>
          <tbody>
            {orders.length===0 && <tr><td className="sub" colSpan={6}>Aucun ordre</td></tr>}
            {orders.map((o:any,i:number)=>(
              <tr key={i}>
                <td>{o.time || o.created_at || ''}</td>
                <td>{o.symbol}</td>
                <td>{o.side}</td>
                <td>{o.qty}</td>
                <td>{o.price}</td>
                <td>{o.status || ''}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
