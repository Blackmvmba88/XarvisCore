import React, { useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

export default function App() {
  const [apiKey, setApiKey] = useState('')
  const [service, setService] = useState('')
  const [username, setUsername] = useState('')
  const [secret, setSecret] = useState('')
  const [secretsIndex, setSecretsIndex] = useState({})
  const [chat, setChat] = useState('')
  const [chatResponse, setChatResponse] = useState('')
  // currently visible secret (svc, usr, value)
  const [visibleSecret, setVisibleSecret] = useState(null)


  async function listSecrets() {
    try {
      const res = await fetch(`${API_BASE}/secrets`, { headers: { 'X-API-KEY': apiKey } })
      const j = await res.json()
      setSecretsIndex(j)
    } catch (e) {
      console.error(e)
      alert('Error fetching secrets; ensure API running and X-API-KEY set')
    }
  }

  async function addSecret() {
    try {
      const res = await fetch(`${API_BASE}/secrets`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-API-KEY': apiKey },
        body: JSON.stringify({ service, username, secret, encrypt: false })
      })
      const j = await res.json()
      if (j.ok) {
        setService('')
        setUsername('')
        setSecret('')
        listSecrets()
      } else {
        alert('Error: ' + JSON.stringify(j))
      }
    } catch (e) {
      console.error(e)
    }
  }

  async function getSecret(svc, usr) {
    try {
      const res = await fetch(`${API_BASE}/secrets/${svc}/${usr}?decrypt=true`, { headers: { 'X-API-KEY': apiKey } })
      const j = await res.json()
      if (j.secret) {
        // show inline viewer instead of alert
        setVisibleSecret({svc, usr, value: j.secret})
      } else {
        alert('No secret')
      }
    } catch (e) {
      console.error(e)
      alert('Error fetching secret')
    }
  }

  async function sendChat() {
    try {
      const res = await fetch(`${API_BASE}/assistant/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-API-KEY': apiKey },
        body: JSON.stringify({ message: chat, dry_run: true })
      })
      const j = await res.json()
      setChatResponse(j.response || JSON.stringify(j))
    } catch (e) {
      console.error(e)
    }
  }

  return (
    <div className="app-wrap">
      <header className="header">
        <div className="brand">
          <div className="logo">
            <svg className="logo-svg" viewBox="0 0 64 64" width="44" height="44" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
              <defs>
                <linearGradient id="g" x1="0" x2="1" y1="0" y2="1">
                  <stop offset="0" stopColor="#cb36f3"/>
                  <stop offset="1" stopColor="#22d3ff"/>
                </linearGradient>
              </defs>
              <g fill="none" stroke="url(#g)" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                <path d="M10 38c4-6 10-10 18-12 7-1 14 0 20 4 4 3 6 7 6 7s-2-7-9-11c-6-3-12-3-18-2C20 26 14 30 10 38z" fill="#0b0b0d" stroke="url(#g)"/>
                <path d="M40 18c2-3 5-6 9-6"/>
                <circle cx="18" cy="38" r="2" fill="#22d3ff"/>
                <path d="M46 26c0 1-1 3-3 4"/>
                <path d="M22 16c-1 3 0 6 2 8"/>
              </g>
              {/* eye + pupil animated */}
              <g className="eye-group">
                <ellipse className="snake-eye" cx="46" cy="18.8" rx="2.4" ry="2" fill="#fff" />
                <circle className="snake-pupil" cx="46" cy="18.8" r="0.9" fill="#0b0b0d" />
                <rect className="snake-closed" x="44.2" y="18.1" width="3.6" height="0.8" rx="0.4" fill="#0b0b0d" opacity="0" />
              </g>
            </svg>
          </div>
          <div>
            <div className="title">Blackmamba Secrets</div>
            <div className="subtitle">Tu bóveda personal</div>
          </div>
        </div>
        <div>
          <button className="ghost" onClick={() => { setApiKey(''); alert('Session cleared on UI'); }}>Cerrar sesión</button>
        </div>
      </header>

      <main className="container">
        <section className="card">
          <h2>Configuración</h2>
          <div className="inputs">
            <label style={{display:'block',marginBottom:8}}>Admin API Key (X-API-KEY):</label>
            <input value={apiKey} onChange={e => setApiKey(e.target.value)} style={{ width: '100%' }} />
            <div style={{ marginTop: 12 }}>
              <button className="btn" onClick={() => listSecrets()}>Refrescar índice</button>
              <button className="ghost" style={{marginLeft:8}} onClick={() => { setApiKey(''); setSecretsIndex({}); }}>Limpiar UI</button>
            </div>
          </div>
        </section>

        <section className="card">
          <h2>Secrets</h2>
          <div style={{display:'flex',gap:8,marginBottom:8,alignItems:'flex-start'}}>
            <input placeholder="service" value={service} onChange={e => setService(e.target.value)} style={{width:120}} />
            <input placeholder="username" value={username} onChange={e => setUsername(e.target.value)} style={{width:140}} />
            <textarea placeholder="secret" value={secret} onChange={e => setSecret(e.target.value)} rows={2} style={{flex:'1 1 240px', minWidth:120, padding:8, borderRadius:8}} />
            <div style={{display:'flex',flexDirection:'column',gap:8}}>
              <button className="btn" onClick={() => addSecret()}>Agregar</button>
              <button className="ghost" onClick={() => setSecret('')}>Limpiar</button>
            </div>
          </div>

          <div style={{marginTop:10}}>
            {Object.entries(secretsIndex).length === 0 ? (
              <div style={{color:'var(--muted)'}}>No hay secretos — presiona "Refrescar índice"</div>
            ) : (
              Object.entries(secretsIndex).map(([svc, users]) => (
                <div key={svc} style={{marginBottom:8}}>
                  <strong>{svc}</strong>
                  <ul>
                    {users.map(u => (
                      <li key={u} style={{marginTop:6}}>
                        {u} <button className="ghost" style={{marginLeft:8}} onClick={() => getSecret(svc, u)}>Mostrar</button>
                        {visibleSecret && visibleSecret.svc===svc && visibleSecret.usr===u ? (
                          <div style={{marginTop:8}}>
                            <textarea className="secret-value" readOnly rows={4} value={visibleSecret.value} />
                            <div style={{marginTop:6}}>
                              <button className="ghost" onClick={() => { navigator.clipboard.writeText(visibleSecret.value); alert('Copiado al portapapeles') }}>Copiar</button>
                              <button className="ghost" style={{marginLeft:8}} onClick={() => setVisibleSecret(null)}>Ocultar</button>
                            </div>
                          </div>
                        ) : null}
                      </li>
                    ))}
                  </ul>
                </div>
              ))
            )}
          </div>
        </section>

        <aside className="card">
          <h2>Assistant (dry-run)</h2>
          <div style={{display:'flex',flexDirection:'column',gap:8}}>
            <textarea rows={4} value={chat} onChange={e => setChat(e.target.value)} />
            <div>
              <button className="btn" onClick={() => sendChat()}>Enviar</button>
            </div>
            <div style={{marginTop:10}}>
              <strong>Respuesta:</strong>
              <pre className="response">{chatResponse}</pre>
            </div>
          </div>
        </aside>
      </main>

      <div className="container" style={{marginTop:18}}>
        <div className="card" style={{textAlign:'center'}}>
          <div className="footer">Blackmamba Secrets — hecho localmente. Mantén tu llave administrativa segura.</div>
        </div>
      </div>
    </div>
  )
}
