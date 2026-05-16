/**
 * api.js - Connects dashboard to FastAPI backend
 * Replaces all Math.random() mock data with real DB readings
 * Polls every 3 seconds automatically
 */

const API = {
  readings: '/readings/?limit=20',
  stats:    '/readings/stats',
  sensors:  '/sensors/',
  onboard:  '/sensors/onboard',
  alarms:   '/alarms/',
  vpn:      '/vpn/gauge',
};

// ── Fetch helpers ────────────────────────────────────────────────────────────

async function apiFetch(url) {
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (e) {
    console.error(`API error ${url}:`, e.message);
    return null;
  }
}

async function apiPost(url, body) {
  try {
    const res = await fetch(url, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(body),
    });
    return await res.json();
  } catch (e) {
    console.error(`POST error ${url}:`, e.message);
    return null;
  }
}

async function apiDelete(url) {
  try {
    const res = await fetch(url, { method: 'DELETE' });
    return await res.json();
  } catch (e) {
    console.error(`DELETE error ${url}:`, e.message);
    return null;
  }
}

// ── Main data refresh (called every 3s) ──────────────────────────────────────

async function refreshDashboard() {
  const [readings, stats, sensors, alarms, vpn] = await Promise.all([
    apiFetch(API.readings),
    apiFetch(API.stats),
    apiFetch(API.sensors),
    apiFetch(API.alarms),
    apiFetch(API.vpn),
  ]);

  if (stats)    updateStats(stats);
  if (sensors)  updateSensorCards(sensors, readings);
  if (alarms)   updateAlarms(alarms);
  if (vpn)      updateVPNGauge(vpn);
  if (readings) updateReadingsTable(readings);
}

// ── Update sidebar stats ─────────────────────────────────────────────────────

function updateStats(stats) {
  const el = (id, val) => {
    const e = document.getElementById(id);
    if (e) e.textContent = val;
  };
  el('stat-online',   stats.sensors_active);
  el('stat-offline',  stats.sensors_offline);
  el('stat-secured',  stats.sensors_active);
  el('stat-total',    stats.sensors_total);

  // Header status text
  const hdr = document.getElementById('global-vpn-status');
  if (hdr) hdr.textContent =
    `${stats.sensors_active} capteur${stats.sensors_active !== 1 ? 's' : ''} protégé${stats.sensors_active !== 1 ? 's' : ''}`;
}

// ── Update sensor cards in dashboard grid ────────────────────────────────────

function updateSensorCards(sensors, readings) {
  const grid = document.getElementById('dashboard-grid') ||
               document.getElementById('sensors-grid');
  if (!grid) return;

  // Build a map: sensor_id → latest reading
  const latest = {};
  if (readings) {
    readings.forEach(r => {
      if (!latest[r.sensor_id]) latest[r.sensor_id] = r;
    });
  }

  grid.innerHTML = sensors.map((s, idx) => {
    const r       = latest[s.sensor_id] || {};
    const value   = r.temperature ?? r.humidity ?? r.pressure ?? '—';
    const unit    = r.unit || '';
    const battery = r.battery ?? '—';
    const history = [value, value, value]; // sparkline placeholder

    const statusColor = s.status === 'active' ? 'var(--accent)' : 'var(--danger)';
    const statusText  = s.status === 'active' ? '● En ligne' : '✕ Hors ligne';

    return `
      <div class="widget">
        <div class="widget-header">
          <div class="widget-title">${s.sensor_id} • ${s.sensor_type}</div>
          <div class="widget-icon">🌡</div>
        </div>
        <div class="widget-value" style="color:${statusColor}">
          ${value}<small style="font-size:14px;color:var(--text-sub)"> ${unit}</small>
        </div>
        <div class="widget-unit">
          IP: ${s.ip_address || 'N/A'} • Batterie: ${battery}%
        </div>
        <canvas id="sparkline-api-${idx}" class="sparkline-chart" width="200" height="40"></canvas>
        <div class="widget-status">
          <div class="widget-status-dot ${s.status === 'active' ? 'online' : 'offline'}"></div>
          <span>${statusText}</span>
          <span style="margin-left:auto;font-size:11px;color:var(--text-sub)">
            ${r.received_at ? new Date(r.received_at).toLocaleTimeString('fr-FR') : '—'}
          </span>
        </div>
        <button class="btn btn-secondary"
          style="margin-top:8px;padding:6px;"
          onclick="deleteSensor('${s.sensor_id}')">
          🗑 Supprimer
        </button>
      </div>`;
  }).join('');

  // Draw sparklines with real history
  sensors.forEach(async (s, idx) => {
    const hist = await apiFetch(`/readings/${s.sensor_id}?limit=20`);
    if (!hist) return;
    const vals = hist.map(r => r.temperature ?? r.humidity ?? r.pressure ?? 0).reverse();
    if (typeof drawSparkline === 'function') {
      drawSparkline(`sparkline-api-${idx}`, vals);
    }
  });
}

// ── Update alarms list ───────────────────────────────────────────────────────

function updateAlarms(alarms) {
  const list = document.getElementById('attack-log') ||
               document.getElementById('alarm-log');
  if (!list) return;

  if (!alarms.length) {
    list.innerHTML = '<div class="empty-state"><div>Aucune alarme active</div></div>';
    return;
  }

  list.innerHTML = alarms.map(a => {
    const color = a.severity === 'critical' ? 'var(--danger)'
                : a.severity === 'high'     ? 'var(--warn)'
                :                             'var(--accent)';
    return `<div class="log-row">
      <span class="log-time">${new Date(a.created_at).toLocaleTimeString('fr-FR')}</span>
      <span class="log-type" style="color:${color}">${a.severity.toUpperCase()}</span>
      <span class="log-desc">${a.message}</span>
      <span class="log-target">${a.sensor_id || '—'}</span>
      <span class="log-result blocked">ALERTE</span>
    </div>`;
  }).join('');
}

// ── Update VPN gauge ─────────────────────────────────────────────────────────

function updateVPNGauge(vpn) {
  // Update any VPN capacity elements
  const els = document.querySelectorAll('[data-vpn-pct]');
  els.forEach(el => el.textContent = vpn.pct + '%');

  const used = document.getElementById('vpn-used');
  const max  = document.getElementById('vpn-max');
  if (used) used.textContent = vpn.used;
  if (max)  max.textContent  = vpn.max;
}

// ── Update readings table (if exists) ───────────────────────────────────────

function updateReadingsTable(readings) {
  const tbody = document.getElementById('readings-tbody');
  if (!tbody) return;

  tbody.innerHTML = readings.map(r => `
    <tr>
      <td>${r.sensor_id}</td>
      <td>${r.temperature ?? '—'}</td>
      <td>${r.humidity ?? '—'}</td>
      <td>${r.pressure ?? '—'}</td>
      <td>${r.battery ?? '—'}%</td>
      <td>${r.status}</td>
      <td>${new Date(r.received_at).toLocaleTimeString('fr-FR')}</td>
    </tr>`).join('');
}

// ── Add sensor ───────────────────────────────────────────────────────────────

async function addSensorFromForm() {
  const name = document.getElementById('sensor-name')?.value?.trim();
  const ip   = document.getElementById('sensor-ip')?.value?.trim();
  const type = document.getElementById('sensor-type')?.value || 'temperature';

  if (!name || !ip) {
    alert('Remplissez le nom/ID et l\'IP du capteur.');
    return;
  }

  const result = await apiPost(API.onboard, {
    sensor_id:   name,
    ip_address:  ip,
    sensor_type: type,
  });

  if (result?.ok) {
    alert(`✅ Capteur ${name} ajouté (${result.ping})`);
    document.getElementById('sensor-name').value = '';
    document.getElementById('sensor-ip').value   = '';
    refreshDashboard();
  } else {
    alert(`❌ Erreur: ${result?.detail || 'inconnue'}`);
  }
}

// ── Delete sensor ────────────────────────────────────────────────────────────

async function deleteSensor(sensorId) {
  if (!confirm(`Supprimer ${sensorId} ?`)) return;
  const result = await apiDelete(`/sensors/${sensorId}`);
  if (result?.ok) {
    refreshDashboard();
  } else {
    alert(`Erreur suppression: ${result?.detail || 'inconnue'}`);
  }
}

// ── Auto-start ───────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  // Initial load
  refreshDashboard();

  // Poll every 3 seconds
  setInterval(refreshDashboard, 3000);

  // Wire up "Add sensor" button if it exists
  const addBtn = document.getElementById('btn-add-sensor') ||
                 document.querySelector('[onclick="manualAddSensor()"]');
  if (addBtn) {
    addBtn.removeAttribute('onclick');
    addBtn.addEventListener('click', addSensorFromForm);
  }
}); 
