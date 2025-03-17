Hier ein mögliches aktualisiertes `README.md`, in dem auch das **lokale Deployment** ergänzt wurde:

```md
# Platform Basis mit Mehrfachauthentisierung

- Docker für Python Applikation  
- Docker-compose für Infrastruktur mit Postgres DB  
- Postgres DB  
- Python mit Flask  

---

## Deployment

### Lokales Deployment

1. **Repository klonen:**
   ```bash
   git clone https://github.com/Furerito/teko_projektverwaltung.git
   ```

2. **In das Projektverzeichnis wechseln:**
   ```bash
   cd teko_projektverwaltung
   ```

3. **Docker-Compose ausführen:**
   ```bash
   docker-compose up
   ```
   *Dadurch werden die Python-Applikation und die Postgres-Datenbank lokal gestartet.*

### Deployment mit Ansible

1. **SSH-Zugriff prüfen**  
   Stelle sicher, dass du **SSH-Zugriff** auf die Zielhosts hast und dich mit einem Benutzer einloggst, der **sudo**-Rechte besitzt.

2. **Konfiguration der Zielhosts**  
   Hinterlege deine Zielhosts in der Datei `ansible/inventory.ini`.

3. **Deployment starten**  
   Führe das Playbook aus:
   ```bash
   ansible-playbook -i inventory.ini deploy.yml
   ```

---

## Applikation

Nach einem erfolgreichen Deployment (lokal oder über Ansible) ist die Applikation unter der entsprechenden IP und Port erreichbar (standardmäßig Port **3355**):
```
http://[IP]:3355
```

Ein erster Benutzer **"Admin"** mit dem Passwort **"5678"** ist bereits angelegt. Du kannst dich damit anmelden und weitere Benutzer verwalten.
```
