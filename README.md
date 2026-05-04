# IoT VPN Shield 🛡️
**Sécurisation d'un réseau de capteurs IoT par VPN avec monitoring en temps réel**
Compétition RSSP 2026 — ENSA Marrakech

---

## Structure du projet
```
iot-vpn-shield/
├── api/
│   ├── main.py                ← API FastAPI (machine API)
│   ├── requirements.txt       ← dépendances Python
│   ├── iot_sender.py          ← VM IoT client
│   ├── monitoring_sender.py   ← VM Monitoring
│   ├── kali_sender.py         ← VM Kali (attaques)
│   └── config.example.py     ← modèle de configuration
├── dashboard/
│   └── index.html             ← dashboard web temps réel
├── .gitignore
└── README.md
```

---

## 🚀 GUIDE PAR RÔLE

### 👤 Machine API (responsable dashboard)

```bash
# 1. Installer les dépendances
cd api
pip install -r requirements.txt

# 2. Lancer l'API
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 3. Trouver ton IP et la partager avec l'équipe
ip a | grep "inet 192"      # Linux
ipconfig | findstr "IPv4"   # Windows

# 4. Ouvrir le dashboard
# → Ouvre dashboard/index.html dans le navigateur
# → Clique ⚙ en bas à droite
# → Entre l'IP de cette machine + port 8000
# → Clique CONNECTER
```

Vérifier que l'API tourne : http://localhost:8000/status

---

### 🌡️ VM IoT Client (capteurs)

```bash
# 1. Cloner le repo
git clone https://github.com/USERNAME/iot-vpn-shield.git
cd iot-vpn-shield/api

# 2. Créer ton fichier de config (jamais pushé sur GitHub)
cp config.example.py config.py
# Édite config.py → remplace l'IP par celle de la machine API

# 3. Installer les dépendances
pip install requests

# 4. Lancer
python iot_sender.py
```

Tu devrais voir :
```
[✓] API en ligne — 1 client(s) WebSocket connecté(s)
── Cycle 1 ──────────────────────
[✓] IOT-01 = 23.2 °C  (online)  → 1 dashboard(s)
[✓] IOT-02 = 58.3 %   (online)  → 1 dashboard(s)
...
```

**Personnaliser les capteurs** — édite la liste `SENSORS` dans `iot_sender.py` :
```python
SENSORS = [
    {"id": "IOT-01", "name": "Ton capteur", "base": 25.0, "unit": "°C", "noise": 0.5},
    # ajoute autant de capteurs que tu veux
]
```

---

### 📊 VM Monitoring (métriques VPN)

```bash
# 1. Cloner + config (même procédure que IoT)
cp config.example.py config.py   # édite avec l'IP API

# 2. Lancer
pip install requests
python monitoring_sender.py
# → Choisir : wireguard / openvpn / none
```

---

### ⚡ VM Kali Linux (attaques)

```bash
# 1. Config (même procédure)
cp config.example.py config.py

# 2. Lancer
pip install requests
python kali_sender.py
# → Menu interactif : choisir l'attaque + si VPN actif
```

---

## 🔧 Dépannage

| Problème | Solution |
|---|---|
| `Connection refused` | L'API ne tourne pas ou mauvaise IP dans config.py |
| `Network unreachable` | VMs pas sur le même réseau, vérifier VirtualBox |
| Dashboard ne se connecte pas | Clique ⚙, vérifie l'IP, clique CONNECTER |
| `ModuleNotFoundError: requests` | `pip install requests` |

**Tester manuellement l'API :**
```bash
# Depuis n'importe quelle VM
curl http://[IP_API]:8000/status

# Envoyer un capteur test
curl -X POST http://[IP_API]:8000/sensor-event \
  -H "Content-Type: application/json" \
  -d '{"sensor_id":"TEST","name":"Test","value":42.0,"unit":"°C","status":"online"}'
```

---

## 🌐 Travailler à distance (ngrok)

Si vous n'êtes pas sur le même réseau :
```bash
# Sur la machine API
ngrok http 8000
# → Donne une URL publique ex: https://abc123.ngrok.io
# Partagez cette URL avec l'équipe
# Dans config.py : API_URL = "https://abc123.ngrok.io"
```
