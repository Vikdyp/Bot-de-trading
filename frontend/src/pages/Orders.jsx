import React, {useEffect, useState} from 'react'
import {api} from '../api'
export default function Orders(){
  const [rows,setRows] = useState([])
  useEffect(()=>{ api('/orders').then(setRows) },[])
  return (
    <div>
      <h3>Orders</h3>
      <table>
        <thead><tr><th>ID</th><th>Time</th><th>Live</th><th>Symbol</th><th>Side</th><th>Qty</th><th>Price</th><th>Status</th></tr></thead>
        <tbody>
        {rows.map(r=>(
          <tr key={r.id}><td>{r.id}</td><td>{new Date(r.created_at).toLocaleString()}</td><td>{String(r.live)}</td><td>{r.symbol}</td><td>{r.side}</td><td>{r.qty}</td><td>{r.price}</td><td>{r.status}</td></tr>
        ))}
        </tbody>
      </table>
    </div>
  )
}
