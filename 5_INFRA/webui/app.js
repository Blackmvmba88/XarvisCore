async function getJSON(path, opts = {}) {
  const r = await fetch(path, opts);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return await r.json();
}

async function refreshStatus() {
  try {
    const s = await getJSON('/api/status');
    const out = `Available: ${(s.available_fraction*100).toFixed(1)}%\nTotal: ${s.total_bytes} bytes\nTop processes:\n` + s.top_processes.map(p => `- ${p.comm} (pid:${p.pid}) ${Math.round(p.rss_bytes/1024)} KB`).join('\n');
    document.getElementById('status').innerText = out;
  } catch(e) {
    document.getElementById('status').innerText = 'Failed to fetch status';
  }
}

async function loadMetrics() {
  try {
    const m = await getJSON('/api/metrics?limit=30');
    document.getElementById('metrics').innerText = JSON.stringify(m, null, 2);
  } catch(e) {
    document.getElementById('metrics').innerText = 'Failed to load metrics';
  }
}

document.getElementById('refresh').addEventListener('click', refreshStatus);
document.getElementById('load-metrics').addEventListener('click', loadMetrics);

document.getElementById('estimate').addEventListener('click', async () => {
  try {
    const r = await getJSON('/api/action', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'estimate' }) });
    alert(`Estimated free: ${Math.round(r.estimated_free_bytes/1024)} KB`);
  } catch(e) { alert('Estimate failed'); }
});

document.getElementById('quit').addEventListener('click', async () => {
  const target = prompt('App name to quit (e.g. Safari):');
  if (!target) return;
  if (!confirm(`Quit ${target}?`)) return;
  const secret = document.getElementById('secret').value.trim();
  try {
    const headers = { 'Content-Type': 'application/json' };
    if (secret) headers['Authorization'] = `Bearer ${secret}`;
    const r = await getJSON('/api/action', { method: 'POST', headers, body: JSON.stringify({ action: 'quit_app', target }) });
    alert(`Result: freed ${Math.round(r.delta_bytes/1024)} KB (success=${r.success})`);
    loadMetrics();
    refreshStatus();
  } catch(e) { alert('Quit failed: ' + e); }
});

document.getElementById('kill').addEventListener('click', async () => {
  const pid = prompt('PID to kill:');
  if (!pid) return;
  if (!confirm(`Kill pid ${pid}?`)) return;
  const secret = document.getElementById('secret').value.trim();
  try {
    const headers = { 'Content-Type': 'application/json' };
    if (secret) headers['Authorization'] = `Bearer ${secret}`;
    const r = await getJSON('/api/action', { method: 'POST', headers, body: JSON.stringify({ action: 'kill_pid', target: pid }) });
    alert(`Result: freed ${Math.round(r.delta_bytes/1024)} KB (success=${r.success})`);
    loadMetrics();
    refreshStatus();
  } catch(e) { alert('Kill failed: ' + e); }
});

// initial load
refreshStatus();
loadMetrics();