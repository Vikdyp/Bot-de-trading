import React, {useEffect, useState} from 'react'
import {api} from '../api'
export default function Config(){
  const [cfg,setCfg] = useState(null)
  const [pairs, setPairs] = useState('')
  useEffect(()=>{ api('/config').then(d=>{ setCfg(d); setPairs(d.pairs.join(',')) }) },[])
  if(!cfg) return <div>Chargement…</div>
  const save = async () => {
    const payload = { pairs: pairs.split(',').map(x=>x.trim().toUpperCase()) }
    await api('/config',{method:'PATCH', body: JSON.stringify(payload)})
    location.reload()
  }
  return (
    <div>
      <h3>Config</h3>
      <div>Timeframe: <b>{cfg.timeframe}</b> (modifier via API pour v1)</div>
      <div style={{marginTop:8}}>
        <label>Paires (base assets, EUR fixé)</label><br/>
        <input value={pairs} onChange={e=>setPairs(e.target.value)} style={{width:'100%'}}/>
      </div>
      <button onClick={save} style={{marginTop:8}}>Enregistrer</button>
    </div>
  )
}
