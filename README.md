# Platform Basis mit Mehrfachauthentisierung

- Docker für Python Applikation  
- Docker-compose für Infrastruktur mit Postgres DB  
- Postgres DB  
- Python mit Flask  

## Deployment

### Lokales Deployment

#### Repository klonen
```bash
git clone https://github.com/Furerito/teko_projektverwaltung.git
```
#### In das Projektverzeichnis wechseln
```bash
cd teko_projektverwaltung
```
#### Container starten
```bash
docker-compose up
```
### Deployment mit Ansible

Stelle sicher, dass du SSH-Zugriff auf die Zielhosts hast. 
Stelle sicher dass ansible sich mit einem Benutzer einloggt, der sudo-Rechte besitzt.

#### Hosts konfigurieren
Hinterlege deine Zielhosts und ansible user in der Datei **ansible/inventory.ini**.

Ansible-Playbook ausführen
```bash
ansible-playbook -i inventory.ini deploy.yml
```

# Applikation
Nach dem Deployment ist die Applikation unter http://[IP]:3355 erreichbar.
Ein erster Benutzer "Admin" mit dem Passwort "5678" ist bereits angelegt.
Verwende deine bevorzugte Authenticator App
