# ─────────────────────────────────────────────
#  VM Kali Linux — envoie les attaques à l'API
#  Usage : python kali_sender.py
# ─────────────────────────────────────────────
import subprocess, requests, time, re

API_URL = "http://192.168.1.50:8000"   # ← remplace par l'IP de la machine API

def send_attack(attack_type, description, target, blocked):
    try:
        r = requests.post(f"{API_URL}/attack-event", json={
            "type": attack_type,
            "description": description,
            "target": target,
            "blocked": blocked
        }, timeout=3)
        print(f"[✓] Envoyé : {attack_type} → {target}")
    except Exception as e:
        print(f"[✗] Erreur envoi : {e}")

def run_nmap(target_network):
    print(f"[*] Nmap scan sur {target_network}...")
    result = subprocess.run(
        ["nmap", "-sV", "--open", target_network],
        capture_output=True, text=True, timeout=60
    )
    send_attack("NMAP", f"Scan réseau {target_network}", target_network, False)
    return result.stdout

def run_arp_spoof(target_ip, gateway_ip, vpn_active=False):
    print(f"[*] ARP Spoofing : {target_ip} ↔ {gateway_ip}")
    blocked = vpn_active
    send_attack("ARP", f"Man-in-the-middle entre {target_ip} et {gateway_ip}", target_ip, blocked)

def run_dos(target_ip, port=1883, vpn_active=False):
    print(f"[*] DoS flood sur {target_ip}:{port}")
    blocked = vpn_active
    send_attack("DOS", f"hping3 flood port {port}", target_ip, blocked)

def run_wireshark_capture(interface="eth0", vpn_active=False):
    print(f"[*] Capture Wireshark sur {interface}")
    blocked = vpn_active
    description = "Trafic chiffré (VPN actif)" if vpn_active else "Trafic en clair capturé"
    send_attack("WSHARK", description, interface, blocked)

# ── Exemple d'utilisation
if __name__ == "__main__":
    print("=== Kali Attack Sender ===")
    print("1) Scan Nmap")
    print("2) ARP Spoofing")
    print("3) DoS Flood")
    print("4) Wireshark capture")
    print("5) Séquence complète (démo)")

    choice = input("\nChoix : ").strip()
    vpn = input("VPN actif ? (o/n) : ").strip().lower() == 'o'

    if choice == "1":
        run_nmap("10.0.0.0/24")
    elif choice == "2":
        run_arp_spoof("10.0.0.2", "10.0.0.1", vpn)
    elif choice == "3":
        run_dos("10.0.0.2", vpn_active=vpn)
    elif choice == "4":
        run_wireshark_capture(vpn_active=vpn)
    elif choice == "5":
        print("\n[DÉMO] Séquence complète — sans VPN puis avec VPN\n")
        time.sleep(1)
        run_nmap("10.0.0.0/24"); time.sleep(2)
        run_wireshark_capture(vpn_active=False); time.sleep(2)
        run_arp_spoof("10.0.0.2", "10.0.0.1", False); time.sleep(2)
        run_dos("10.0.0.2", vpn_active=False); time.sleep(2)
        print("\n[DÉMO] VPN activé — mêmes attaques, résultats différents\n")
        run_arp_spoof("10.0.0.2", "10.0.0.1", True); time.sleep(2)
        run_dos("10.0.0.2", vpn_active=True); time.sleep(2)
        run_wireshark_capture(vpn_active=True)
        print("\n[✓] Démo terminée")
    else:
        print("Choix invalide")
