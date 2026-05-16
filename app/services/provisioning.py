import subprocess

def get_peer_status() -> list:
    try:
        out = subprocess.check_output(["sudo", "wg", "show"]).decode()
        peers = []
        current = {}
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("peer:"):
                if current: peers.append(current)
                current = {"public_key": line.split(": ")[1]}
            elif line.startswith("endpoint:"):
                current["endpoint"] = line.split(": ")[1]
            elif line.startswith("allowed ips:"):
                current["allowed_ips"] = line.split(": ")[1]
            elif line.startswith("latest handshake:"):
                current["last_handshake"] = line.split(": ", 1)[1]
        if current: peers.append(current)
        return peers
    except Exception:
        return []
