# 📤 PUSH TO GITHUB — Complete Guide

## ✅ Files Ready to Push

Your complete project is in: `/mnt/user-data/outputs/iot-vpn-shield/`

```
iot-vpn-shield/
├── dashboard/index.html          # Dashboard ThingsBoard
├── backend/main.py               # FastAPI + WebSocket
├── scripts/
│   ├── iot_sender.py             # IoT Sensors
│   ├── monitoring_sender.py      # VPN Metrics
│   └── kali_sender.py            # Attack Tests
├── README.md                      # Full documentation
├── requirements.txt               # Dependencies
├── config.example.json            # Config template
└── .gitignore                     # Git ignore rules
```

---

## 🚀 HOW TO PUSH TO GITHUB

### Step 1: Clone Your Repo (if you haven't already)

```bash
git clone https://github.com/saad8-byte/Projet-Reseau.git
cd Projet-Reseau
```

### Step 2: Copy Project Files

Copy all files from `/mnt/user-data/outputs/iot-vpn-shield/` into your repo:

```bash
# Copy all files from the generated project
cp -r /mnt/user-data/outputs/iot-vpn-shield/* .

# Verify files are there
ls -la
# Should show: dashboard/, backend/, scripts/, README.md, requirements.txt, etc.
```

### Step 3: Check Git Status

```bash
git status
```

**Should show:**
```
On branch main
Your branch is up to date with 'origin/main'.

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        dashboard/
        backend/
        scripts/
        README.md
        requirements.txt
        config.example.json
        ...
```

### Step 4: Add Files to Git

```bash
# Add all new files
git add .

# Verify what will be committed
git status
```

### Step 5: Commit

```bash
git commit -m "Add: Complete IoT VPN Shield dashboard + backend + scripts

- Dashboard: ThingsBoard-style UI with real-time charts
- Backend: FastAPI + WebSocket for live data streaming
- Scripts: IoT sensors, VPN monitoring, Kali attack sender
- Config: Example config with setup instructions
- Docs: Full README with deployment guide"
```

### Step 6: Push to GitHub

```bash
git push origin main
```

**Success message:**
```
Enumerating objects: 25, done.
Counting objects: 100% (25/25), done.
Delta compression using up to 8 threads
Writing objects: 100% (25/25), 500 KiB | 100 KiB/s, done.
Total 25 (delta 0), reused 0 (delta 0), reused pack 0 (delta 0)
To github.com:saad8-byte/Projet-Reseau.git
   abc1234..def5678 main -> main
```

✅ **Done!** Your code is now on GitHub.

---

## 👥 FOR YOUR TEAM MEMBERS

Once you push, your team can:

```bash
# 1. Clone the updated repo
git clone https://github.com/saad8-byte/Projet-Reseau.git
cd Projet-Reseau

# 2. Create their config (local, never commit!)
cp config.example.json config.json
# Edit with the API IP address

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run their script (each on different VM)
python scripts/iot_sender.py          # Membre 2 (VM IoT)
python scripts/monitoring_sender.py   # Membre 3 (VM Monitoring)
python scripts/kali_sender.py         # Membre 4 (VM Kali)

# 5. Or run the API (main machine)
uvicorn backend/main.py --host 0.0.0.0 --port 8000

# 6. Open dashboard
# http://YOUR_MACHINE_IP:8000
```

---

## 🔄 IF YOU NEED TO UPDATE LATER

When your team makes changes (e.g., add more sensors):

```bash
# Make changes to scripts/iot_sender.py, etc.

# Commit and push
git add .
git commit -m "Update: Add new sensors to IoT script"
git push origin main

# Team members update:
git pull origin main
```

---

## ⚠️ IMPORTANT NOTES

### ✅ `.gitignore` Protects These Files
- ❌ `config.json` — Never pushed (IPs hidden)
- ❌ `__pycache__/` — Auto-generated
- ❌ `*.log` — Logs
- ❌ `.vscode/`, `.idea/` — IDE folders

### ✅ `config.example.json` IS Pushed
- ✓ Shows structure
- ✓ Team copies it to `config.json` locally
- ✓ Never has real IPs

---

## 🎯 FINAL CHECKLIST BEFORE PUSH

- [ ] All Python files copied to `/scripts/` and `/backend/`
- [ ] `dashboard/index.html` exists and is the ThingsBoard version
- [ ] `README.md` has complete setup instructions
- [ ] `requirements.txt` has fastapi, uvicorn, requests
- [ ] `config.example.json` has the correct structure
- [ ] `.gitignore` excludes config.json
- [ ] No `config.json` in the repo (only example)
- [ ] Tested: `git status` shows all files
- [ ] Tested: `git add .` works
- [ ] Tested: `git commit` works
- [ ] Tested: `git push` works

---

## 📞 HELP COMMANDS

```bash
# See what would be pushed (without pushing)
git dry-run

# Undo last commit (if needed)
git reset --soft HEAD~1

# See commit history
git log --oneline

# Check remote
git remote -v
```

---

**Everything is ready! Your team can now collaborate on this project via GitHub. 🚀**
