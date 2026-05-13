# ─────────────────────────────────────────────
#  VM Kali Linux — Envoie les attaques
#  Usage : python kali_sender.py
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

def send_attack(attack_type, description, target, blocked):
    try:
        r = requests.post(f"{API_URL}/api/attack", json={
            "type": attack_type,
            "description": description,
            "target": target,
            "blocked": blocked
        }, timeout=3)
        if r.status_code == 200:
            status = "BLOQUÉ" if blocked else "SUCCÈS"
            print(f"[✓] {attack_type} → {target} ({status})")
    except Exception as e:
        print(f"[✗] Erreur : {e}")

def run_nmap(target_network):
    print(f"[*] Nmap scan sur {target_network}...")
    send_attack("NMAP", f"Scan découverte {target_network}", target_network, False)

def run_arp_spoof(target_ip, gateway_ip, vpn_active=False):
    print(f"[*] ARP Spoofing : {target_ip}")
    blocked = vpn_active
    send_attack("ARP", f"Man-in-the-middle {target_ip}", target_ip, blocked)

def run_dos(target_ip, port=1883, vpn_active=False):
    print(f"[*] DoS flood sur {target_ip}:{port}")
    blocked = vpn_active
    send_attack("DOS", f"Saturation port {port}", target_ip, blocked)

def run_wireshark(interface="eth0", vpn_active=False):
    print(f"[*] Capture Wireshark sur {interface}")
    desc = "Trafic chiffré (VPN)" if vpn_active else "Trafic en clair"
    send_attack("WSHARK", desc, interface, vpn_active)

# ─────────────────────────────────────────────
#  MENU
# ─────────────────────────────────────────────

print("=" * 50)
print("   Kali Attack Sender — RSSP VPN Shield")
print("=" * 50)
print("\n1) Scan Nmap")
print("2) ARP Spoofing")
print("3) DoS Flood")
print("4) Wireshark Capture")
print("5) Sequence complète (demo)")

choice = input("\nChoix : ").strip()
vpn = input("VPN actif ? (o/n) : ").strip().lower() == 'o'

if choice == "1":
    run_nmap("10.0.0.0/24")
elif choice == "2":
    run_arp_spoof("10.0.0.2", "10.0.0.1", vpn)
elif choice == "3":
    run_dos("10.0.0.2", vpn_active=vpn)
elif choice == "4":
    run_wireshark(vpn_active=vpn)
elif choice == "5":
    print("\n[DÉMO] Séquence — Sans VPN puis avec VPN\n")
    time.sleep(1)
    run_nmap("10.0.0.0/24")
    time.sleep(2)
    run_wireshark(vpn_active=False)
    time.sleep(2)
    run_arp_spoof("10.0.0.2", "10.0.0.1", False)
    time.sleep(2)
    run_dos("10.0.0.2", vpn_active=False)
    time.sleep(2)
    print("\n[DÉMO] VPN activé — mêmes attaques, résultats différents\n")
    run_arp_spoof("10.0.0.2", "10.0.0.1", True)
    time.sleep(2)
    run_dos("10.0.0.2", vpn_active=True)
    time.sleep(2)
    run_wireshark(vpn_active=True)
    print("\n[✓] Démo terminée")
