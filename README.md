# Platform Basis mit Mehrfachauthentisierung

- Docker für Python Applikation  
- Docker-compose für Infrastruktur mit Postgres DB  
- Postgres DB  
- Python mit Flask  

## Deployment

### Lokales Deployment

1. **Repository klonen**  
   ```bash
   git clone https://github.com/Furerito/teko_projektverwaltung.git
In das Projektverzeichnis wechseln

bash
Kopieren
Bearbeiten
cd teko_projektverwaltung
Container starten

bash
Kopieren
Bearbeiten
docker-compose up
Deployment mit Ansible
SSH-Zugriff
Stelle sicher, dass du SSH-Zugriff auf die Zielhosts hast und dich mit einem Benutzer einloggst, der sudo-Rechte besitzt.

Hosts konfigurieren
Hinterlege deine Zielhosts in der Datei ansible/inventory.ini.

Ansible-Playbook ausführen

bash
Kopieren
Bearbeiten
ansible-playbook -i inventory.ini deploy.yml
Applikation
Nach dem Deployment ist die Applikation unter http://[IP]:3355 erreichbar.
Ein erster Benutzer "Admin" mit dem Passwort "5678" ist bereits angelegt.
