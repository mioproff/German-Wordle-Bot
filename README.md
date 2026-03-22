# 🟩 Deutsches Wordle – Discord Bot

Ein vollständiger Wordle-Bot für Discord auf Deutsch, mit Leaderboard, unbegrenzten Spielen und Slash-Commands.

---

## 📁 Dateien

```
wordle_bot/
├── bot.py              ← Haupt-Bot-Datei
├── woerter.py          ← Deutsches Wörterbuch
├── requirements.txt    ← Python-Abhängigkeiten
├── spielstand.json     ← Wird automatisch erstellt (Spielerdaten)
└── README.md           ← Diese Datei
```

---

## ⚙️ Schritt 1 – Python installieren

Stelle sicher dass **Python 3.10 oder neuer** installiert ist:

```bash
python --version
# Ausgabe: Python 3.10.x oder höher
```

Falls nicht: https://www.python.org/downloads/

---

## 🤖 Schritt 2 – Discord Bot erstellen

### 2.1 Zum Discord Developer Portal

👉 Gehe zu: https://discord.com/developers/applications

### 2.2 Neue Application erstellen

1. Klicke auf **"New Application"**
2. Gib dem Bot einen Namen (z.B. `Wordle Bot DE`)
3. Klicke auf **"Create"**

### 2.3 Bot hinzufügen

1. Links im Menü auf **"Bot"** klicken
2. Klicke auf **"Add Bot"** → Bestätige mit **"Yes, do it!"**
3. Unter **"Privileged Gateway Intents"** aktiviere:
   - ✅ `Message Content Intent`
   - ✅ `Server Members Intent` (optional, für Namen)

### 2.4 Bot-Token kopieren

1. Klicke auf **"Reset Token"** → Token erscheint
2. ⚠️ **Diesen Token NIEMALS teilen oder in öffentliche Repos pushen!**
3. Token kopieren und aufbewahren

### 2.5 Bot einladen

1. Links auf **"OAuth2"** → **"URL Generator"**
2. Unter **Scopes** wähle: ✅ `bot` und ✅ `applications.commands`
3. Unter **Bot Permissions** wähle:
   - ✅ `Send Messages`
   - ✅ `Embed Links`
   - ✅ `Read Message History`
4. Generierten Link öffnen und Bot zu deinem Server einladen

---

## 📦 Schritt 3 – Abhängigkeiten installieren

Öffne ein Terminal im Ordner `wordle_bot/`:

```bash
# Empfohlen: Virtual Environment erstellen
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt
```

---

## 🔑 Schritt 4 – Token eintragen

Öffne `bot.py` und ersetze in Zeile 15:

```python
TOKEN = "DEIN_BOT_TOKEN_HIER"
```

mit deinem echten Token:

```python
TOKEN = "MTIzNDU2Nzg5MDEyMzQ1Njc4.XXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```

> **Tipp für Profis:** Verwende eine `.env`-Datei statt den Token direkt einzutragen:
> ```bash
> pip install python-dotenv
> ```
> Erstelle `.env`:
> ```
> DISCORD_TOKEN=dein_token_hier
> ```
> In `bot.py`:
> ```python
> from dotenv import load_dotenv
> import os
> load_dotenv()
> TOKEN = os.getenv("DISCORD_TOKEN")
> ```

---

## 🚀 Schritt 5 – Bot starten

```bash
python bot.py
```

Du siehst:
```
🚀 Starte Wordle Bot...
✅ Slash-Commands synchronisiert!
🟩 Bot ist online als: Wordle Bot DE#1234
```

> ⏱️ **Hinweis:** Slash-Commands können bis zu **1 Stunde** brauchen bis sie bei Discord sichtbar werden. Beim ersten Start evtl. kurz warten.

---

## 🎮 Befehle im Überblick

| Befehl | Beschreibung |
|--------|-------------|
| `/wordle` | Startet ein neues Spiel |
| `/raten <wort>` | Rät ein 5-Buchstaben-Wort |
| `/aufgeben` | Gibt das aktuelle Spiel auf |
| `/leaderboard` | Zeigt die Top 10 Bestenliste |
| `/stats` | Zeigt deine persönlichen Statistiken |
| `/hilfe` | Zeigt die Spielanleitung |

---

## 🧩 Spielablauf (Beispiel)

```
Du: /wordle
Bot: 🟩 Neues Wordle-Spiel gestartet!
     ⬜⬜⬜⬜⬜  _ _ _ _ _
     ⬜⬜⬜⬜⬜  _ _ _ _ _
     ...

Du: /raten haus
Bot: ❌ Das Wort muss 5 Buchstaben haben!

Du: /raten hause
Bot: 🟩⬛🟨⬛⬛  H A U S E
     ⬜⬜⬜⬜⬜  _ _ _ _ _
     ...

Du: /raten hotel
Bot: 🎉 In 2/6 Versuchen gelöst!
```

---

## 🔧 Anpassungen

### Mehr Wörter hinzufügen

Öffne `woerter.py` und füge Wörter zu `LOESUNGSWOERTER` oder `ALLE_WOERTER` hinzu. Alle Wörter müssen **GROSSBUCHSTABEN** und genau **5 Buchstaben** lang sein.

### Maximale Versuche ändern

In `bot.py`, Zeile 18:
```python
MAX_VERSUCHE = 6  # Auf z.B. 8 ändern für einfacherer Modus
```

### Datenbankwechsel (für größere Server)

Für sehr große Server (100+ Spieler täglich) empfiehlt sich statt JSON eine echte Datenbank:
- **SQLite**: `pip install aiosqlite` (einfach, keine Installation nötig)
- **PostgreSQL**: `pip install asyncpg` (für große Server)

---

## 🔄 Bot dauerhaft laufen lassen

### Option A: Screen (Linux/Mac)
```bash
screen -S wordle
python bot.py
# Ctrl+A dann D zum Detachen
```

### Option B: PM2 (Node.js muss installiert sein)
```bash
npm install -g pm2
pm2 start bot.py --interpreter python3
pm2 save
pm2 startup
```

### Option C: Systemd Service (Linux)
Erstelle `/etc/systemd/system/wordle-bot.service`:
```ini
[Unit]
Description=Wordle Discord Bot
After=network.target

[Service]
ExecStart=/usr/bin/python3 /pfad/zu/bot.py
WorkingDirectory=/pfad/zu/wordle_bot/
Restart=always
User=deinuser

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl enable wordle-bot
sudo systemctl start wordle-bot
```

### Option D: Hosting-Dienste
- **Railway.app** (kostenlos, einfach)
- **Render.com** (kostenlos)
- **Hetzner VPS** (günstig, 3-4€/Monat)

---

## ❓ Häufige Probleme

**"Token wurde nicht akzeptiert"**
→ Token nochmal kopieren, keine Leerzeichen!

**Slash-Commands erscheinen nicht**
→ Bis zu 1h warten. Bot neu starten hilft manchmal.

**"ModuleNotFoundError: discord"**
→ `pip install discord.py` nochmal ausführen, Virtual Environment aktivieren!

**Bot ist offline nach PC-Neustart**
→ Einen der "dauerhaft laufen lassen" Methoden oben nutzen.

---

## 📄 Lizenz

Frei verwendbar – viel Spaß beim Spielen! 🟩🟨⬛
