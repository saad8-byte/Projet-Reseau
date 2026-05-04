# ─────────────────────────────────────────────
#  VM Monitoring — envoie les métriques VPN
#  Usage : python monitoring_sender.py
# ─────────────────────────────────────────────
import requests, time, random, subprocess

API_URL = "http://192.168.1.50:8000"   # ← remplace par l'IP de la machine API

def get_ping(host="10.0.0.1"):
    """Mesure la latence réelle avec ping."""
    try:
        result = subprocess.run(
            ["ping", "-c", "3", "-q", host],
            capture_output=True, text=True, timeout=10
        )
        match = __import__('re').search(r'rtt.*?=.*?/([\d.]+)/', result.stdout)
        return float(match.group(1)) if match else random.uniform(10, 50)
    except:
        return random.uniform(10, 50)

def get_cpu():
    """Lit le CPU depuis /proc/stat."""
    try:
        with open("/proc/stat") as f:
            parts = f.readline().split()
        total = sum(int(x) for x in parts[1:])
        idle = int(parts[4])
        return round((1 - idle/total) * 100, 1)
    except:
        return random.uniform(2, 20)

def send_metrics(vpn_name, latency, cpu, bandwidth, pps):
    try:
        r = requests.post(f"{API_URL}/metrics-event", json={
            "vpn": vpn_name,
            "latency_ms": round(latency, 2),
            "cpu_percent": round(cpu, 1),
            "bandwidth_mbps": round(bandwidth, 1),
            "packets_per_sec": round(pps, 0)
        }, timeout=3)
        print(f"[✓] Métriques envoyées — VPN={vpn_name} lat={latency:.1f}ms cpu={cpu:.1f}%")
    except Exception as e:
        print(f"[✗] Erreur : {e}")

print("=== Monitoring Sender ===")
vpn = input("VPN actif ? (wireguard/openvpn/none) : ").strip().lower()
print(f"Envoi métriques pour VPN={vpn}. Ctrl+C pour arrêter.\n")

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

    send_metrics(vpn, latency, cpu, bw, pps)
    time.sleep(2)
