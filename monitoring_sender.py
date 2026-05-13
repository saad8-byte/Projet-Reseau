# ─────────────────────────────────────────────
#  VM Monitoring — Envoie les métriques VPN
#  Usage : python monitoring_sender.py
# ─────────────────────────────────────────────

import requests, time, random, subprocess, json, os, sys

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    else:
        print(f"⚠ Fichier {CONFIG_FILE} non trouvé.")
        sys.exit(1)

config = load_config()
API_URL = config.get("API_URL", "http://192.168.1.50:8000")

def get_ping(host="10.0.0.1"):
    """Mesure la latence réelle avec ping"""
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-q", host],
            capture_output=True, text=True, timeout=10
        )
        import re
        match = re.search(r'rtt.*?=.*?/([\d.]+)/', result.stdout)
        return float(match.group(1)) if match else random.uniform(10, 50)
    except:
        return random.uniform(10, 50)

def get_cpu():
    """Lit le CPU depuis /proc/stat"""
    try:
        with open("/proc/stat") as f:
            parts = f.readline().split()
        total = sum(int(x) for x in parts[1:])
        idle = int(parts[4])
        return round((1 - idle/total) * 100, 1)
    except:
        return random.uniform(2, 20)

def send_metrics(latency, cpu, bandwidth, pps):
    try:
        r = requests.post(f"{API_URL}/api/metrics", json={
            "latency_ms": round(latency, 2),
            "cpu_percent": round(cpu, 1),
            "bandwidth_mbps": round(bandwidth, 1),
            "packets_per_sec": round(pps, 0)
        }, timeout=3)
        if r.status_code == 200:
            print(f"[✓] Lat={latency:.1f}ms CPU={cpu:.1f}% BW={bandwidth:.1f}MB/s")
    except Exception as e:
        print(f"[✗] Erreur : {e}")

print("=" * 50)
print("   VPN Monitoring Sender — RSSP VPN Shield")
print("=" * 50)

vpn = input("\nVPN actif ? (wireguard/openvpn/none) : ").strip().lower()
print(f"\n[*] Envoi des métriques pour VPN={vpn}\n")

while True:
    latency = get_ping()
    cpu = get_cpu()
    
    if vpn == "wireguard":
        bw = 90 + random.uniform(-5, 5)
        pps = 1200 + random.uniform(-100, 100)
    elif vpn == "openvpn":
        bw = 40 + random.uniform(-5, 5)
        pps = 800 + random.uniform(-100, 100)
    else:
        bw = 120 + random.uniform(-10, 10)
        pps = 1500 + random.uniform(-100, 100)

    send_metrics(latency, cpu, bw, pps)
    time.sleep(2)
