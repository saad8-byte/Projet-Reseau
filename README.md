# 🛡️ IoT VPN Shield — RSSP 2026

Sécurisation d'un réseau de capteurs IoT par VPN avec monitoring en temps réel.
Dashboard ThingsBoard-inspired avec AI Assistant intégré.

**Compétition**: ENSA Marrakech — RSSP 2026  
**Équipe**: 4 membres  
**Deadline**: 16 mai 2026  
**Format démo**: 7 min présentation + 3 min démo + 5 min Q&A

---

## 📋 Architecture

```
┌─────────────────────────────────────┐
│     API FastAPI + WebSocket         │  Backend
│  (Machine Machine: 192.168.1.50)    │
└────────┬────────┬────────┬──────────┘
         │        │        │
    ┌────▼──┐ ┌──▼──┐ ┌───▼──┐
    │ VM 1  │ │ VM2 │ │ VM3  │ ┌─────┐
    │OpenVPN│ │ IoT │ │Monit.│ │ VM4 │
    │WG     │ │Sect.│ │ VPN  │ │Kali │
    └───────┘ └─────┘ └──────┘ └─────┘
         │        │        │        │
         └────────┴────────┴────────┘
                  │
           ┌──────▼────────┐
           │   Dashboard   │
           │  (HTML/JS)    │
           │  ThingsBoard  │
           │  + AI Agent   │
           └───────────────┘
```

### Rôles de l'équipe

| Rôle | VM | Responsabilités |
|------|-----|-----------------|
| **Membre 1** | VM1 | Serveur VPN (OpenVPN + WireGuard) |
| **Membre 2** | VM2 | Client IoT — scripts Python + capteurs |
| **Membre 3** | VM3 | Monitoring VPN — métriques CPU/latence |
| **Membre 4** | VM4 | Kali Linux — attaques de test |

---

## 🚀 Démarrage Rapide

### 1️⃣ Machine API (N'importe où — 192.168.1.50)

```bash
# Clone le repo
git clone https://github.com/saad8-byte/Projet-Reseau.git
cd Projet-Reseau

# Crée config.json
cp config.example.json config.json
# Édite avec ton IP API

# Installe dépendances
pip install -r requirements.txt

# Lance l'API
uvicorn backend/main.py --host 0.0.0.0 --port 8000
```

**La console doit afficher:**
```
Uvicorn running on http://0.0.0.0:8000
Application startup complete
```

### 2️⃣ Dashboard (Browser)

Ouvre: **http://192.168.1.50:8000**

- Dashboard avec capteurs en temps réel
- VPN Stats avec graphiques
- AI Assistant (coin bas-droit 🤖)
- Log attaques en direct

### 3️⃣ VM IoT — Capteurs (VM2)

```bash
cd scripts

# Crée config.json
cp ../config.example.json config.json
# Édite API_URL = "http://192.168.1.50:8000"

# Lance les capteurs
python iot_sender.py
```

**Résultat:**
```
[✓] IOT-01 = 23.4 °C (online)
[✓] IOT-02 = 58.2 % (online)
...
```

Le dashboard **doit afficher les capteurs** en temps réel avec les sparklines.

### 4️⃣ VM Monitoring — Métriques VPN (VM3)

```bash
cd scripts
python monitoring_sender.py

# Quand demandé:
# VPN actif ? wireguard
```

**Résultat:**
- Latence, CPU, Débit en temps réel
- Graphiques VPN Stats mis à jour

### 5️⃣ VM Kali — Attaques (VM4)

```bash
cd scripts
python kali_sender.py

# Menu interactif:
# 1) Scan Nmap
# 2) ARP Spoofing
# 3) DoS Flood
# 4) Wireshark
# 5) Séquence démo (complète)
```

Le **journal des attaques** apparaît sur le dashboard.

---

## 📁 Structure des Fichiers

```
iot-vpn-shield/
├── dashboard/
│   └── index.html                 # Dashboard complet (ThingsBoard)
├── backend/
│   └── main.py                    # API FastAPI + WebSocket
├── scripts/
│   ├── iot_sender.py              # Envoie données capteurs
│   ├── monitoring_sender.py       # Envoie métriques VPN
│   └── kali_sender.py             # Envoie attaques
├── docs/
│   ├── SETUP.md                   # Guide détaillé
│   └── API.md                     # Documentation API
├── config.example.json            # Configuration template
├── requirements.txt               # Dépendances Python
├── .gitignore                     # Fichiers à ignorer
└── README.md                      # Ce fichier
```

---

## 🔌 API Endpoints

### REST POST Endpoints

```bash
# Ajouter un capteur
POST /api/sensor
{
  "sensor_id": "IOT-01",
  "name": "Température Bureau",
  "ip": "192.168.1.10",
  "value": 23.4,
  "unit": "°C",
  "status": "online",
  "vpn_active": true
}

# Ajouter une attaque
POST /api/attack
{
  "type": "NMAP",
  "description": "Scan découverte",
  "target": "10.0.0.0/24",
  "blocked": false
}

# Ajouter une métrique VPN
POST /api/metrics
{
  "latency_ms": 12.5,
  "cpu_percent": 3.1,
  "bandwidth_mbps": 94.2,
  "packets_per_sec": 1200
}
```

### GET Endpoints

```bash
# Status de l'API
GET /api/status
→ { "status": "running", "ws_clients": 2, ... }

# Health check
GET /api/health
→ { "status": "healthy" }
```

### WebSocket

```javascript
// Client JavaScript
const ws = new WebSocket('ws://192.168.1.50:8000/ws');
ws.onmessage = (e) => {
  const data = JSON.parse(e.data);
  console.log(data); // { type: 'sensor', time: '14:32:15', data: {...} }
};
```

---

## ⚙️ Configuration

Copie `config.example.json` → `config.json` et édite:

```json
{
  "API_URL": "http://192.168.1.50:8000",     # ← IP de la machine API
  "API_PORT": 8000,
  "DASHBOARD_URL": "http://192.168.1.50:8000",
  "SENSORS_UPDATE_INTERVAL": 2,
  "MONITORING_UPDATE_INTERVAL": 2,
  "ANTHROPIC_API_KEY": "sk-ant-..."          # ← Pour AI Agent
}
```

---

## 🎮 Dashboard Features

### 📊 Pages

1. **Dashboard** — Vue globale des capteurs + stats clés
2. **Capteurs** — Ajouter/gérer capteurs manuellement
3. **VPN Stats** — Métriques VPN détaillées avec graphiques 24h
4. **Sécurité** — Journal des attaques Kali

### 🤖 AI Assistant

Coin bas-droit: bouton 🤖 → chat interactif  
Connecte avec Anthropic Claude pour aide:
- Ajouter capteurs naturellement
- Questions sur la sécurité IoT
- Explications attaques VPN

**Configuration AI:** Édite `config.example.json` avec ta clé API Anthropic

### 📈 Graphiques

- **Sparklines** sur chaque widget (20 points d'historique)
- **Graphiques 24h** sur page VPN Stats (60px+ hauteur)
- **Charts canvas** (pas de dépendances externes)
- **Mise à jour live** toutes les 2.5s

---

## 🧪 Dépannage

### ❌ Erreur: "Connection refused"

```bash
# Vérifie que l'API tourne
lsof -i :8000

# Ou tente d'accéder à l'API:
curl http://192.168.1.50:8000/api/status
```

### ❌ Les capteurs n'apparaissent pas

1. Vérifie `config.json` → `API_URL` correcte
2. Teste manuellement:
   ```bash
   curl -X POST http://192.168.1.50:8000/api/sensor \
     -H "Content-Type: application/json" \
     -d '{"sensor_id":"TEST","name":"Test","ip":"10.0.0.1","value":25,"unit":"°C","status":"online","vpn_active":true}'
   ```

### ❌ AI Assistant ne fonctionne pas

- Clé API Anthropic manquante → clique "Plus tard" et rentre-la quand demandé
- Clé invalide → supprime `localStorage` → recharde la page

---

## 📊 Dépendances

### Backend
- **FastAPI** 0.104.1 — API web moderne
- **Uvicorn** 0.24.0 — Serveur ASGI
- **Pydantic** 2.4.2 — Validation données

### Scripts
- **requests** 2.31.0 — HTTP client

### Frontend
- HTML5 + CSS3 + Vanilla JS (zéro dépendances)

Installe tout:
```bash
pip install -r requirements.txt
```

---

## 🔒 Sécurité

### Best Practices

- ✅ `config.json` ignée dans `.gitignore` → ne push jamais les IPs sensibles
- ✅ API en CORS wildcard pour démo — **à restreindre en prod**
- ✅ WebSocket sans auth pour démo — **ajoute tokens en prod**
- ✅ Clés API jamais en dur dans le code

---

## 📝 Pour la Présentation

### Slides PowerPoint

Voir `docs/presentation.pptx` (généré séparément)

### Demo Flow (7 min)

1. **Intro 1 min** — Problème IoT + Solution
2. **Dashboard 2 min** — Montrer interface ThingsBoard, capteurs en direct
3. **Attaques 2 min** — Lancer Kali, montrer SANS VPN (succès), AVEC VPN (bloqué)
4. **VPN Stats 1 min** — Graphiques latence/CPU (WireGuard > OpenVPN)
5. **AI Chat 1 min** — Ajouter capteur par la parole/texte naturel

### Points Clés à Souligner

- ✨ Interface moderne (ThingsBoard-style)
- ✨ Temps réel (WebSocket)
- ✨ Comparaison OpenVPN vs WireGuard
- ✨ Sécurité prouvée (attaques Kali)
- ✨ AI intégré (Claude)

---

## 👥 Team Workflow

### Chaque coéquipier:

```bash
# 1) Clone le repo
git clone https://github.com/saad8-byte/Projet-Reseau.git

# 2) Crée config.json (local)
cp config.example.json config.json
# Édite avec l'IP API de la machine centrale

# 3) Installe dépendances
pip install -r requirements.txt

# 4) Lance ton script:
python scripts/iot_sender.py          # Membre 2
python scripts/monitoring_sender.py   # Membre 3
python scripts/kali_sender.py         # Membre 4
```

### Chef de projet (Membre 4 — saad8-byte):

```bash
# Lance l'API
uvicorn backend/main.py --host 0.0.0.0 --port 8000

# Ouvre le dashboard
# http://192.168.1.50:8000

# Monitor les logs
# (voir console de l'API pour [SENSOR], [ATTACK], [METRICS])
```

---

## 📚 Documentation

- `docs/SETUP.md` — Guide détaillé d'installation
- `docs/API.md` — Référence complète API
- Code commenté en français dans les scripts

---

## ✅ Checklist Avant Présentation

- [ ] API tourne sur machine centrale
- [ ] Dashboard accessible (http://machine:8000)
- [ ] Capteurs envoient des données (IoT sender lance)
- [ ] VPN Stats affiche des graphiques
- [ ] Attaques Kali s'envoient (journal à jour)
- [ ] AI Assistant configuré (clé API rentrée)
- [ ] Les 3 scripts Python testés
- [ ] PowerPoint prêt
- [ ] Internet stable (démo live!)

---

## 🎯 Objectifs Atteints

✅ Sécurisation IoT par VPN  
✅ Dashboard temps réel (ThingsBoard)  
✅ Monitoring VPN (latence, CPU, débit)  
✅ Tests attaques (Kali + résultats)  
✅ Comparaison OpenVPN vs WireGuard  
✅ AI Assistant intégré  
✅ Projet scalable (architecture claire)  
✅ Code commenté + documentation

---

## 📧 Support

**Questions?** Ouvre une issue sur GitHub ou contacte saad8-byte

---

**Made with ❤️ for RSSP 2026 — ENSA Marrakech**
