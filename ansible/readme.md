# Applikation auf Hosts verteilen
## Vorbereitung
- Lege den Public Key der Zielmaschinen in inventory.ini ab
- Stelle sicher, dass

## Start deploy
Navigiere in Verzeichnis "ansible"
```
ansible-playbook -i inventory.ini deploy.yml --ask-become-pass
```

## Voilà
- Erstellt das Verzeichnis /var/www
- Klont das Git-Repository nach /var/www/the_project
- Installiert Docker & Docker-Compose
- Konfiguriert einen Systemd-Service für docker-compose
- Startet den docker-compose-Dienst automatisch

Die Applikation ist anschliessend unter den konfigurierten IP auf Port 3355 erreichbar.
Verwende den User "Admin" und das Passwort "5678" für das erste Login.