import React, {useEffect, useState} from 'react'
import {api} from '../api'
export default function Signals(){
  const [rows,setRows] = useState([])
  useEffect(()=>{ api('/signals').then(setRows) },[])
  return (
    <div>
      <h3>Signals</h3>
      <table>
        <thead><tr><th>Time</th><th>Symbol</th><th>Type</th><th>Reason</th><th>Value</th></tr></thead>
        <tbody>
        {rows.map((r,i)=>(
          <tr key={i}><td>{new Date(r.created_at).toLocaleString()}</td><td>{r.symbol}</td><td>{r.type}</td><td>{r.reason}</td><td>{r.value.toFixed(4)}</td></tr>
        ))}
        </tbody>
      </table>
    </div>
  )
}
