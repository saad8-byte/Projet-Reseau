# ⚡ QUICK START — Team Edition

## 🎯 TL;DR — 5 Minutes to Running

### Central Machine (API Host)

```bash
# Clone repo
git clone https://github.com/saad8-byte/Projet-Reseau.git
cd Projet-Reseau

# Install & run
pip install -r requirements.txt
uvicorn backend/main.py --host 0.0.0.0 --port 8000
```

**Open browser:** http://YOUR_MACHINE_IP:8000 ✅

### Each Team Member (on different VM)

```bash
# Clone repo
git clone https://github.com/saad8-byte/Projet-Reseau.git
cd Projet-Reseau

# Create local config (never commit!)
cp config.example.json config.json

# Edit config.json:
# Change API_URL to your central machine IP
# Example: "API_URL": "http://192.168.1.50:8000"

# Install & run YOUR script
pip install -r requirements.txt

# Membre 2 (VM IoT):
python scripts/iot_sender.py

# Membre 3 (VM Monitoring):
python scripts/monitoring_sender.py

# Membre 4 (VM Kali):
python scripts/kali_sender.py
```

**Dashboard updates in real-time ✅**

---

## 📊 What Each File Does

| File | Purpose | Who Runs It |
|------|---------|-----------|
| `backend/main.py` | API + WebSocket server | Central machine (member 4) |
| `dashboard/index.html` | Web interface | Browser (everyone) |
| `scripts/iot_sender.py` | Send sensor data | VM2 (member 2) |
| `scripts/monitoring_sender.py` | Send VPN metrics | VM3 (member 3) |
| `scripts/kali_sender.py` | Send attack events | VM4 (member 4) |
| `config.example.json` | Config template | Copy locally, never push |

---

## 🚨 Troubleshooting

**Q: "Connection refused"**
```bash
# Check API is running on central machine
curl http://192.168.1.50:8000/api/status
# Should return: {"status":"running",...}
```

**Q: "config.json not found"**
```bash
# Copy the example
cp config.example.json config.json
# Edit with your API IP
nano config.json  # or vim/code
```

**Q: "ModuleNotFoundError"**
```bash
# Install dependencies
pip install -r requirements.txt
```

---

## 🎬 Demo Flow (7 minutes)

1. **Start**: API running on central machine ✅
2. **2 min**: Show dashboard (empty initially)
3. **2 min**: Start `iot_sender.py` → sensors appear + charts
4. **1 min**: Start `monitoring_sender.py` → VPN stats update
5. **1 min**: Run `kali_sender.py` demo → attack log populates
6. **1 min**: Show AI assistant in dashboard corner

---

## 🔐 Security Notes

- ✅ Never commit `config.json` (it's in `.gitignore`)
- ✅ Never push `ANTHROPIC_API_KEY` in real files
- ✅ Config stays local on each machine
- ✅ `.gitignore` protects you automatically

---

## 📱 Mobile/Remote?

If working remotely, use ngrok to expose the API:

```bash
# Install ngrok (one-time)
brew install ngrok  # or download from ngrok.com

# Expose your API
ngrok http 8000

# You'll get: https://XXXXX.ngrok.io
# Share this URL with your team → they use it as API_URL in config.json
```

---

**That's it! You're ready to demo. 🚀**
