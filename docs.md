# Initial Setup


## Installiere Docker

```
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
$(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

## Erstelle das Verzeichnis das in Docker gemountet wird
```
sudo mkdir /mnt/postgresDocker/
```

## Starte Docker

```
sudo systemctl start docker
sudo systemctl enable docker
```

## Füge den aktuellen Benutzer zur Gruppe "Docker" hinzu
```
sudo usermod -aG docker $USER
```

## Starte Postgres Docker
```
sudo docker run -d \
  --name postgres_mfa \
  -e POSTGRES_PASSWORD=MySecretPasswor \
  -p 3356:5432 \
  -v /mnt/postgresDocker/:/var/lib/postgresql/data \
  postgres:15
```

## Datenbank und Tabellen erstellen
### Verbinde mit PGADMIN und erstelle die Datenbank
```
-- Database: 2fa_session

-- DROP DATABASE IF EXISTS "2fa_session";

CREATE DATABASE "2fa_session"
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_GB.UTF-8'
    LC_CTYPE = 'en_GB.UTF-8'
    LOCALE_PROVIDER = 'libc'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

GRANT ALL ON DATABASE "2fa_session" TO "2fa_admin";

GRANT TEMPORARY, CONNECT ON DATABASE "2fa_session" TO PUBLIC;

GRANT ALL ON DATABASE "2fa_session" TO postgres;
```


### Tabelle: Benutzer
```
-- Table: public.users

-- DROP TABLE IF EXISTS public.users;

CREATE TABLE IF NOT EXISTS public.users
(
    id integer NOT NULL DEFAULT nextval('users_id_seq'::regclass),
    username character varying(50) COLLATE pg_catalog."default" NOT NULL,
    password character varying(255) COLLATE pg_catalog."default" NOT NULL,
    otp_secret character varying(255) COLLATE pg_catalog."default",
    two_factor_enabled boolean DEFAULT false,
    two_factor_verified boolean DEFAULT false,
    is_superuser boolean DEFAULT false,
    account_locked boolean DEFAULT false,
    CONSTRAINT users_pkey PRIMARY KEY (id),
    CONSTRAINT users_username_key UNIQUE (username)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.users
    OWNER to postgres;

GRANT ALL ON TABLE public.users TO "2fa_admin";

GRANT ALL ON TABLE public.users TO postgres;
```

## Erstelle Admin Benutzer (PW: 5678)
```
INSERT INTO users (
    id,
    username,
    password,
    otp_secret,
    two_factor_enabled,
    two_factor_verified,
    is_superuser,
    account_locked
) VALUES (
    1,
    'Admin',
    '$2b$12$NYjR6Gymw9Hd4iWNWHjzpud37NheNNm9uclJiw5hC2t6VUAXtDXla',
    'DC3OWJ5XNHWUEFBOISY4UGXPSW4M2ASU',
    false,
    false,
    true,
    false
);
```

## Installiere Python
```
sudo apt install python
sudo apt install python3-pip
```

## Installiere nötige python pakete
```
sudo apt install python3-pyotp
sudo apt install python3-flask
sudo apt install python3-psycopg2
sudo apt install python3-bcrypt
sudo apt install python3-qrcode
sudo apt install python3-docx
sudo apt install python3-mammoth
sudo apt install python3-pandas 
sudo apt install python3-openpyxl
```

## Starte den FLASK Server
Prüfe ob bereits ein Screen mit einer Instanz vorhanden ist
```
screen -ls
```
Wenn vorhanden, übernehme den Screen
```
screen -r NAME_DES_SCREENS
```
Wenn einfaches übernehmen nicht gelingt:
```
screen -d -r NAME_DES_SCREENS
```
Starte den Server
```
# Navigiere ins Verzeichnis
cd /var/www/mfa_presence_check/

# Starte den Dienst
python3 run.py
```

## Autostart nach Server reboot
Erstelle den Eintrag in crontab -e
```
@reboot screen -dmS srk_mfa_presencecheck bash -c 'python3 /var/www/mfa_presence_check/run.py'
```

## ....oder starte den docker compose
