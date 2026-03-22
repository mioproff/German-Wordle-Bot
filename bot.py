"""
🇩🇪 Deutsches Wordle Discord Bot
Erstellt mit discord.py 2.x und Slash-Commands
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import asyncio
from datetime import datetime
from woerter import zufalls_wort, ist_gueltiges_wort

# ─────────────────────────────────────────────
# ⚙️  Konfiguration
# ─────────────────────────────────────────────
TOKEN = "https://discord.com/oauth2/authorize?client_id=1485379963577438370&permissions=83968&integration_type=0&scope=bot+applications.commandsR"           # <-- Bot-Token einfügen
DATEN_DATEI = "spielstand.json"         # Lokale Speicherdatei
MAX_VERSUCHE = 6                         # Maximale Versuche pro Spiel

# ─────────────────────────────────────────────
# 🗃️  Datenverwaltung
# ─────────────────────────────────────────────

def lade_daten() -> dict:
    if os.path.exists(DATEN_DATEI):
        with open(DATEN_DATEI, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"spieler": {}, "spiele": {}}

def speichere_daten(daten: dict):
    with open(DATEN_DATEI, "w", encoding="utf-8") as f:
        json.dump(daten, f, ensure_ascii=False, indent=2)

def spieler_erstellen(daten: dict, user_id: str, name: str):
    if user_id not in daten["spieler"]:
        daten["spieler"][user_id] = {
            "name": name,
            "siege": 0,
            "niederlagen": 0,
            "spiele_gesamt": 0,
            "aktueller_streak": 0,
            "bester_streak": 0,
            "versuchs_verteilung": {"1":0,"2":0,"3":0,"4":0,"5":0,"6":0},
        }
    else:
        daten["spieler"][user_id]["name"] = name  # Name aktualisieren

# ─────────────────────────────────────────────
# 🎮  Spiellogik
# ─────────────────────────────────────────────

def bewerte_guess(guess: str, loesung: str) -> list[str]:
    """
    Gibt eine Liste von Emojis zurück:
    🟩 = Richtiger Buchstabe, richtige Position
    🟨 = Richtiger Buchstabe, falsche Position
    ⬛ = Buchstabe nicht im Wort
    """
    guess = guess.upper()
    loesung = loesung.upper()
    ergebnis = ["⬛"] * 5
    loesung_liste = list(loesung)
    
    # Erst: Grüne (exakte Treffer)
    for i in range(5):
        if guess[i] == loesung[i]:
            ergebnis[i] = "🟩"
            loesung_liste[i] = None
    
    # Dann: Gelbe (falsche Position)
    for i in range(5):
        if ergebnis[i] == "⬛" and guess[i] in loesung_liste:
            ergebnis[i] = "🟨"
            loesung_liste[loesung_liste.index(guess[i])] = None
    
    return ergebnis

def erstelle_tastatur(versuche: list[dict]) -> str:
    """Erstellt eine Emoji-Tastatur die zeigt welche Buchstaben schon versucht wurden."""
    buchstaben_status = {}
    for versuch in versuche:
        wort = versuch["wort"]
        emojis = versuch["emojis"]
        for i, (b, e) in enumerate(zip(wort, emojis)):
            aktuell = buchstaben_status.get(b, "⬜")
            if e == "🟩":
                buchstaben_status[b] = "🟩"
            elif e == "🟨" and aktuell != "🟩":
                buchstaben_status[b] = "🟨"
            elif e == "⬛" and aktuell == "⬜":
                buchstaben_status[b] = "⬛"

    reihen = [
        "QWERTZUIOP",
        "ASDFGHJKL",
        "YXCVBNM",
    ]
    tastatur = ""
    for reihe in reihen:
        for b in reihe:
            tastatur += buchstaben_status.get(b, "⬜")
        tastatur += "\n"
    return tastatur

def erstelle_spielfeld(versuche: list[dict]) -> str:
    """Erstellt das Wordle-Spielfeld als Text."""
    zeilen = []
    for v in versuche:
        emoji_reihe = "".join(v["emojis"])
        buchstaben_reihe = " ".join(f"`{b}`" for b in v["wort"])
        zeilen.append(f"{emoji_reihe}  {buchstaben_reihe}")
    
    # Leere Zeilen auffüllen
    while len(zeilen) < MAX_VERSUCHE:
        zeilen.append("⬜⬜⬜⬜⬜  `_` `_` `_` `_` `_`")
    
    return "\n".join(zeilen)

# ─────────────────────────────────────────────
# 🤖  Bot Setup
# ─────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True

class WordleBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.aktive_spiele: dict[str, dict] = {}  # user_id -> Spielzustand

    async def setup_hook(self):
        await self.tree.sync()
        print("✅ Slash-Commands synchronisiert!")

    async def on_ready(self):
        print(f"🟩 Bot ist online als: {self.user}")
        await self.change_presence(
            activity=discord.Game(name="Deutsches Wordle 🇩🇪 | /wordle")
        )

bot = WordleBot()

# ─────────────────────────────────────────────
# 📖  /hilfe
# ─────────────────────────────────────────────

@bot.tree.command(name="hilfe", description="Zeigt die Spielanleitung für Wordle")
async def hilfe(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📖 Deutsches Wordle – Anleitung",
        color=discord.Color.from_rgb(83, 141, 78)
    )
    embed.add_field(
        name="🎯 Ziel",
        value="Rate das geheime **5-Buchstaben-Wort** in maximal **6 Versuchen**!",
        inline=False
    )
    embed.add_field(
        name="🟩 Grün",
        value="Buchstabe ist **richtig** und an der **richtigen Position**",
        inline=True
    )
    embed.add_field(
        name="🟨 Gelb",
        value="Buchstabe ist im Wort, aber an der **falschen Position**",
        inline=True
    )
    embed.add_field(
        name="⬛ Schwarz",
        value="Buchstabe kommt im Wort **nicht vor**",
        inline=True
    )
    embed.add_field(
        name="📌 Befehle",
        value=(
            "`/wordle` – Neues Spiel starten\n"
            "`/raten <wort>` – Wort raten\n"
            "`/aufgeben` – Aktuelles Spiel aufgeben\n"
            "`/leaderboard` – Bestenliste anzeigen\n"
            "`/stats` – Deine Statistiken\n"
            "`/hilfe` – Diese Hilfe"
        ),
        inline=False
    )
    embed.add_field(
        name="ℹ️ Hinweis",
        value="Du kannst **unbegrenzt viele Spiele** pro Tag spielen! Jedes Spiel hat ein neues Zufallswort.",
        inline=False
    )
    embed.set_footer(text="Viel Spaß! 🍀")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ─────────────────────────────────────────────
# 🆕  /wordle – Neues Spiel
# ─────────────────────────────────────────────

@bot.tree.command(name="wordle", description="Startet ein neues Wordle-Spiel")
async def wordle(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    
    # Laufendes Spiel prüfen
    if user_id in bot.aktive_spiele:
        embed = discord.Embed(
            title="⚠️ Du hast bereits ein aktives Spiel!",
            description="Benutze `/raten <wort>` um zu raten oder `/aufgeben` um aufzugeben.",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Neues Spiel erstellen
    wort = zufalls_wort()
    bot.aktive_spiele[user_id] = {
        "wort": wort,
        "versuche": [],
        "gestartet": datetime.now().isoformat(),
        "channel_id": interaction.channel_id,
    }
    
    # Spielerdaten laden/erstellen
    daten = lade_daten()
    spieler_erstellen(daten, user_id, interaction.user.display_name)
    speichere_daten(daten)
    
    embed = discord.Embed(
        title="🟩 Neues Wordle-Spiel gestartet!",
        description=(
            f"Rate das geheime **5-Buchstaben-Wort**!\n"
            f"Du hast **{MAX_VERSUCHE} Versuche**.\n\n"
            f"{erstelle_spielfeld([])}\n\n"
            f"Benutze `/raten <wort>` um zu beginnen!"
        ),
        color=discord.Color.from_rgb(83, 141, 78)
    )
    embed.set_author(
        name=f"{interaction.user.display_name}s Spiel",
        icon_url=interaction.user.display_avatar.url
    )
    embed.set_footer(text="💡 Tipp: /hilfe für die Anleitung")
    await interaction.response.send_message(embed=embed)

# ─────────────────────────────────────────────
# 🔤  /raten – Wort raten
# ─────────────────────────────────────────────

@bot.tree.command(name="raten", description="Rate ein Wort im laufenden Spiel")
@app_commands.describe(wort="Dein 5-Buchstaben-Wort")
async def raten(interaction: discord.Interaction, wort: str):
    user_id = str(interaction.user.id)
    wort = wort.upper().strip()
    
    # Kein aktives Spiel
    if user_id not in bot.aktive_spiele:
        embed = discord.Embed(
            title="❌ Kein aktives Spiel",
            description="Starte mit `/wordle` ein neues Spiel!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Länge prüfen
    if len(wort) != 5:
        embed = discord.Embed(
            title="❌ Ungültige Eingabe",
            description=f"Das Wort muss genau **5 Buchstaben** haben! (Du hast {len(wort)} eingegeben)",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Nur Buchstaben
    if not wort.replace("Ä","A").replace("Ö","O").replace("Ü","U").replace("ß","S").isalpha():
        embed = discord.Embed(
            title="❌ Ungültige Eingabe",
            description="Bitte nur Buchstaben eingeben!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Wort im Wörterbuch?
    if not ist_gueltiges_wort(wort):
        embed = discord.Embed(
            title="❌ Unbekanntes Wort",
            description=f"**{wort}** ist nicht im Wörterbuch!\nBitte ein anderes deutsches Wort versuchen.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    spiel = bot.aktive_spiele[user_id]
    loesung = spiel["wort"]
    
    # Bereits geraten?
    bereits_geraten = [v["wort"] for v in spiel["versuche"]]
    if wort in bereits_geraten:
        embed = discord.Embed(
            title="⚠️ Bereits geraten",
            description=f"Du hast **{wort}** bereits versucht! Probiere ein anderes Wort.",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Bewerten
    emojis = bewerte_guess(wort, loesung)
    spiel["versuche"].append({"wort": wort, "emojis": emojis})
    
    versuch_nr = len(spiel["versuche"])
    gewonnen = all(e == "🟩" for e in emojis)
    verloren = (not gewonnen) and (versuch_nr >= MAX_VERSUCHE)
    
    # Embed aufbauen
    spielfeld = erstelle_spielfeld(spiel["versuche"])
    tastatur = erstelle_tastatur(spiel["versuche"])
    
    if gewonnen:
        farbe = discord.Color.from_rgb(83, 141, 78)
        titel = f"🎉 Glückwunsch! In {versuch_nr}/{MAX_VERSUCHE} Versuchen gelöst!"
        beschreibung = f"{spielfeld}\n\n🔤 **Tastatur:**\n{tastatur}"
        # Stats updaten
        daten = lade_daten()
        spieler_erstellen(daten, user_id, interaction.user.display_name)
        s = daten["spieler"][user_id]
        s["siege"] += 1
        s["spiele_gesamt"] += 1
        s["aktueller_streak"] += 1
        s["bester_streak"] = max(s["bester_streak"], s["aktueller_streak"])
        vstr = str(versuch_nr)
        if vstr in s["versuchs_verteilung"]:
            s["versuchs_verteilung"][vstr] += 1
        speichere_daten(daten)
        del bot.aktive_spiele[user_id]
        
    elif verloren:
        farbe = discord.Color.from_rgb(184, 64, 64)
        titel = f"😢 Schade! Das Wort war: **{loesung}**"
        beschreibung = f"{spielfeld}\n\n🔤 **Tastatur:**\n{tastatur}"
        # Stats updaten
        daten = lade_daten()
        spieler_erstellen(daten, user_id, interaction.user.display_name)
        s = daten["spieler"][user_id]
        s["niederlagen"] += 1
        s["spiele_gesamt"] += 1
        s["aktueller_streak"] = 0
        speichere_daten(daten)
        del bot.aktive_spiele[user_id]
        
    else:
        farbe = discord.Color.blurple()
        verbleibend = MAX_VERSUCHE - versuch_nr
        titel = f"Versuch {versuch_nr}/{MAX_VERSUCHE} – noch {verbleibend} übrig"
        beschreibung = f"{spielfeld}\n\n🔤 **Tastatur:**\n{tastatur}\n\nWeiter mit `/raten <wort>`"
    
    embed = discord.Embed(title=titel, description=beschreibung, color=farbe)
    embed.set_author(
        name=f"{interaction.user.display_name}s Spiel",
        icon_url=interaction.user.display_avatar.url
    )
    
    if gewonnen:
        embed.set_footer(text="🎊 Starte ein neues Spiel mit /wordle!")
    elif verloren:
        embed.set_footer(text="💪 Beim nächsten Mal klappt's! Starte neu mit /wordle")
    
    await interaction.response.send_message(embed=embed)

# ─────────────────────────────────────────────
# 🏳️  /aufgeben
# ─────────────────────────────────────────────

@bot.tree.command(name="aufgeben", description="Gibt das aktuelle Spiel auf")
async def aufgeben(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    
    if user_id not in bot.aktive_spiele:
        embed = discord.Embed(
            title="❌ Kein aktives Spiel",
            description="Du hast kein laufendes Spiel. Starte mit `/wordle`!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    loesung = bot.aktive_spiele[user_id]["wort"]
    versuche = bot.aktive_spiele[user_id]["versuche"]
    
    # Stats updaten
    daten = lade_daten()
    spieler_erstellen(daten, user_id, interaction.user.display_name)
    s = daten["spieler"][user_id]
    s["niederlagen"] += 1
    s["spiele_gesamt"] += 1
    s["aktueller_streak"] = 0
    speichere_daten(daten)
    del bot.aktive_spiele[user_id]
    
    embed = discord.Embed(
        title=f"🏳️ Spiel aufgegeben! Das Wort war: **{loesung}**",
        description=f"{erstelle_spielfeld(versuche)}\n\nStarte ein neues Spiel mit `/wordle`!",
        color=discord.Color.greyple()
    )
    embed.set_author(
        name=f"{interaction.user.display_name}",
        icon_url=interaction.user.display_avatar.url
    )
    await interaction.response.send_message(embed=embed)

# ─────────────────────────────────────────────
# 🏆  /leaderboard
# ─────────────────────────────────────────────

@bot.tree.command(name="leaderboard", description="Zeigt die Bestenliste")
async def leaderboard(interaction: discord.Interaction):
    daten = lade_daten()
    spieler = daten.get("spieler", {})
    
    if not spieler:
        embed = discord.Embed(
            title="🏆 Bestenliste",
            description="Noch keine Spiele gespielt! Starte mit `/wordle`.",
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed)
        return
    
    # Sortieren nach Siegen (dann Winrate)
    def sortier_key(item):
        s = item[1]
        gesamt = s["spiele_gesamt"]
        winrate = s["siege"] / gesamt if gesamt > 0 else 0
        return (s["siege"], winrate, s["bester_streak"])
    
    sortiert = sorted(spieler.items(), key=sortier_key, reverse=True)[:10]
    
    medals = ["🥇", "🥈", "🥉"] + ["🎖️"] * 7
    zeilen = []
    
    for i, (uid, s) in enumerate(sortiert):
        gesamt = s["spiele_gesamt"]
        winrate = round(s["siege"] / gesamt * 100) if gesamt > 0 else 0
        name = s["name"][:15]
        zeilen.append(
            f"{medals[i]} **{name}** — "
            f"🏆 {s['siege']} Siege | "
            f"📊 {winrate}% | "
            f"🔥 {s['bester_streak']} Streak"
        )
    
    embed = discord.Embed(
        title="🏆 Wordle Bestenliste",
        description="\n".join(zeilen) if zeilen else "Noch keine Einträge",
        color=discord.Color.gold()
    )
    embed.set_footer(text=f"Top {len(zeilen)} von {len(spieler)} Spielern")
    await interaction.response.send_message(embed=embed)

# ─────────────────────────────────────────────
# 📊  /stats
# ─────────────────────────────────────────────

@bot.tree.command(name="stats", description="Zeigt deine persönlichen Statistiken")
async def stats(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    daten = lade_daten()
    spieler_erstellen(daten, user_id, interaction.user.display_name)
    s = daten["spieler"][user_id]
    speichere_daten(daten)
    
    gesamt = s["spiele_gesamt"]
    winrate = round(s["siege"] / gesamt * 100) if gesamt > 0 else 0
    
    # Versuchs-Verteilung als Balken
    vert = s["versuchs_verteilung"]
    max_val = max(int(v) for v in vert.values()) if any(int(v) > 0 for v in vert.values()) else 1
    
    balken = ""
    for i in range(1, 7):
        anz = int(vert.get(str(i), 0))
        breite = round(anz / max_val * 10) if max_val > 0 and anz > 0 else 0
        balken += f"`{i}` {'█' * breite}{'░' * (10 - breite)} {anz}\n"
    
    embed = discord.Embed(
        title=f"📊 Statistiken von {interaction.user.display_name}",
        color=discord.Color.blurple()
    )
    embed.add_field(name="🎮 Spiele gesamt", value=str(gesamt), inline=True)
    embed.add_field(name="🏆 Siege", value=str(s["siege"]), inline=True)
    embed.add_field(name="📈 Gewinnrate", value=f"{winrate}%", inline=True)
    embed.add_field(name="🔥 Aktueller Streak", value=str(s["aktueller_streak"]), inline=True)
    embed.add_field(name="⭐ Bester Streak", value=str(s["bester_streak"]), inline=True)
    embed.add_field(name="❌ Niederlagen", value=str(s["niederlagen"]), inline=True)
    embed.add_field(name="📊 Versuchs-Verteilung", value=balken, inline=False)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    
    await interaction.response.send_message(embed=embed)

# ─────────────────────────────────────────────
# 🚀  Bot starten
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("🚀 Starte Wordle Bot...")
    bot.run(TOKEN)
