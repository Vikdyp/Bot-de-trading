import React, {useEffect, useState} from 'react'
import Overview from './pages/Overview'
import Signals from './pages/Signals'
import Orders from './pages/Orders'
import Positions from './pages/Positions'
import Config from './pages/Config'

export default function App(){
  const [tab, setTab] = useState('Overview')
  const Tabs = {Overview, Signals, Orders, Positions, Config}
  const Current = Tabs[tab]
  return (
    <div style={{fontFamily:'system-ui', padding:16}}>
      <h2>Binance EUR Bot</h2>
      <nav style={{display:'flex', gap:8, marginBottom:12}}>
        {Object.keys(Tabs).map(t => (
          <button key={t} onClick={()=>setTab(t)} style={{padding:'8px 12px', borderRadius:6, border:'1px solid #ccc', background: tab===t ? '#eee':'#fff'}}>{t}</button>
        ))}
      </nav>
      <Current />
    </div>
  )
}
