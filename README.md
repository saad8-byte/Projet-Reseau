# IoT VPN Shield — Guide de lancement

## Structure
```
vpn_iot_api/
├── main.py                  ← API FastAPI (ta machine)
├── requirements.txt         ← dépendances Python
├── kali_sender.py           ← script VM Kali (toi)
├── iot_sender.py            ← script VM IoT (coéquipier 1)
├── monitoring_sender.py     ← script VM Monitoring (coéquipier 2)
└── static/
    └── index.html           ← dashboard (copie le fichier HTML ici)
```

## 1. Lancer l'API (ta machine)

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

Accès dashboard : http://localhost:8000/static/index.html
Documentation API : http://localhost:8000/docs
Vérification : http://localhost:8000/status

## 2. Trouver ton IP

```bash
ip a | grep "inet 192"
```

## 3. Ce que tu donnes à chaque coéquipier

### Coéquipier VM IoT
- Fichier : iot_sender.py
- Modifier la ligne : API_URL = "http://[TON_IP]:8000"
- Lancer : python iot_sender.py

### Coéquipier VM Monitoring
- Fichier : monitoring_sender.py
- Modifier la ligne : API_URL = "http://[TON_IP]:8000"
- Lancer : python monitoring_sender.py

### Toi — VM Kali
- Fichier : kali_sender.py
- API_URL est déjà sur localhost
- Lancer : python kali_sender.py

## 4. Connecter le dashboard au WebSocket

Dans index.html, ajouter avant </script> :

```javascript
const ws = new WebSocket("ws://[TON_IP]:8000/ws");
ws.onmessage = (e) => {
  const msg = JSON.parse(e.data);
  if (msg.type === "attack")  addAttack(msg.data.type, msg.data.description, msg.data.target, msg.data.blocked);
  if (msg.type === "sensor")  { /* mettre à jour capteur */ }
  if (msg.type === "metrics") { /* mettre à jour monitoring */ }
};
```
