-- Erstellung der Tabellen und initialer Daten

-- Datenbank 2fa_session ist durch POSTGRES_DB bereits erstellt

-- Tabellen erstellen

CREATE TABLE IF NOT EXISTS public.users (
    id serial PRIMARY KEY,
    username varchar(50) NOT NULL UNIQUE,
    password varchar(255) NOT NULL,
    otp_secret varchar(255),
    two_factor_enabled boolean DEFAULT false,
    two_factor_verified boolean DEFAULT false,
    is_superuser boolean DEFAULT false,
    account_locked boolean DEFAULT false
);

-- Initialen Admin-Benutzer einfügen Password: 5678
INSERT INTO public.users (
    id, username, password, otp_secret, two_factor_enabled, two_factor_verified, is_superuser, account_locked
) VALUES (
    1, 'Admin', '$2b$12$NYjR6Gymw9Hd4iWNWHjzpud37NheNNm9uclJiw5hC2t6VUAXtDXla', 
    'DC3OWJ5XNHWUEFBOISY4UGXPSW4M2ASU', false, false, true, false
);
