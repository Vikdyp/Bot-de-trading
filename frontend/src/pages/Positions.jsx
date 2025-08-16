import React, {useEffect, useState} from 'react'
import {api} from '../api'
export default function Positions(){
  const [rows,setRows] = useState([])
  useEffect(()=>{ api('/positions').then(setRows) },[])
  return (
    <div>
      <h3>Positions</h3>
      <table>
        <thead><tr><th>Symbol</th><th>Qty</th><th>Avg Price</th><th>Stop</th><th>Opened</th></tr></thead>
        <tbody>
          {rows.map((r,i)=>(
            <tr key={i}><td>{r.symbol}</td><td>{r.qty}</td><td>{r.avg_price}</td><td>{r.stop_price}</td><td>{new Date(r.opened_at).toLocaleString()}</td></tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
