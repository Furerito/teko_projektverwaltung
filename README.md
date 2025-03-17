# Platform Basis mit Mehrfachauthentisierung

- Docker für Python Applikation
- Docker-compose für Infrastruktur mit Postgres DB
- Postgres DB
- Python mit Flask

# Deployment

- Stelle sicher dass du SSH Zugriff auf die Zielhosts hast
- Stelle sicher dass die SSH Verbindung mit einem User der sudo Rechte hat, erstellt wird
- Konfiguriere deine Zielhosts in /ansible/inventory.ini
```
ansible-playbook -i inventory.ini deploy.yml
```

# Applikation

Die Applikation ist nach dem Deployment erreichbar: [IP]:3355
Ein Erster Benutzer "Admin" und Passwort "5678" ist vorhanden
