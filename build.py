#!/usr/bin/env python3
"""Erzeugt die statischen HTML-Seiten in site/.

Aufruf:  python3 build.py
Danach liegt die fertige Homepage in site/ (diesen Ordner bei Netlify veröffentlichen).

Inhalte ändern:
  - Branchen (Texte, Seitenvorschläge, Fotos): Liste BRANCHEN – jede Branche ist eine eigene Seite homepage-fuer-….html
  - Neue Branche: Eintrag in BRANCHEN + Vorschau in MOCKS (Schriften in MOCK_FONTS, Styles in style.css)
  - Preise: GRUNDPREIS, HOSTING, SEITE, TEXT_PRO_SEITE, FUNKTIONEN, DOMAIN_OPT, SERVICE_OPT
  - Erklärungen der Infobuttons: TIPS
  - Aussehen: site/assets/style.css   ·   Verhalten: site/assets/app.js

Offene Punkte (vom Inhaber zu entscheiden):
  Marke (19.10.2026): HomepageKonfigurator · homepagekonfigurator.de (homepage-konfigurator.de → 301) · Claim siehe CLAIM · Ansprache „du“
Machbarkeit:
  Domain ~1 €/Monat (INWX, Inhaber = Kunde) · Hosting statisch (Netlify) · Formular: Netlify Forms
  Kontaktformular-Mails laufen über unseren Mail-Dienst an die normale Adresse des Kunden (kein Kunden-Mailkonto nötig)
  Blog-Login: gemeinsamer Redaktionsbereich auf dem eigenen Server, einmal gebaut, für alle Kunden
  Preismodell (19.10.2026): Homepage kaufen ab 499 € + Hosting 9,99 €/Monat (Pflicht, 12 Monate Mindestlaufzeit)
  Extras: Seite 49,99 · Kontakt 99 · Blog 149 · Selbstpflege/Anfrage 149 · Termin/Karte/Galerie (bis 20 Bilder) 49 · Google-Bewertungen 99 · Texte 39/Seite · Bilder 39/Seite
  Monatlich: Domain neu/Umzug 4,99 · Monitoring 4,99 · Wartung 14,99 · Sorglos 17,99
  Keine E-Mail-Postfächer · Rechtstexte liefert der Kunde (wir geben ihm das Technik-Infoblatt aus vorlagen/)
  Monitoring: stündlicher Abruf vom eigenen Server, Benachrichtigung an den Inhaber · Terminbuchung: Einbindung externes Tool des Kunden
  Upload Logo/Fotos: Datei-Anfrage-Link · Feedback auf Entwurf: Kommentar-Skript oder Tool mit Gratis-Stufe
  Schriften und Fotos liegen lokal in site/assets (DSGVO: keine Verbindung zu Google/Unsplash beim Seitenaufruf).
  Fehlende Dateien lädt build.py beim nächsten Lauf automatisch herunter.
TODO Livegang: AGB anwaltlich prüfen lassen, Netlify-Formular testen, E-Mail-Adresse auf eigene Domain umstellen,
  beide Domains bei Netlify eintragen, Sitemap in der Google Search Console einreichen, Vorschaubild (og:image) ergänzen
"""
import re
import shutil
import time
import urllib.request
from html import escape
from pathlib import Path

NAME = "HomepageKonfigurator"
CLAIM = "Deine Homepage. Fertig gebaut."
DOMAIN = "https://homepagekonfigurator.de"  # Hauptdomain; homepage-konfigurator.de leitet per 301 hierher (site/_redirects)
MAIL = "info@homepagekonfigurator.de"  # auch in site/assets/app.js (Fehlermeldung des Konfigurators)
OUT = Path(__file__).parent / "site"
VERSION = str(int(time.time()))  # hängt an CSS/JS, damit Browser keine alte Version aus dem Cache nehmen

# Anbieter (aus dem Impressum von vergleichsheld24.de übernommen)
ANBIETER = dict(name="Sven Rosenthal", strasse="In der Landwehr 21", ort="34376 Immenhausen OT Holzhausen",
                land="Deutschland", ust="DE300044005")

BILDQUALITAET = 62  # WebP-Qualität; bei Änderung den Ordner site/assets/img leeren, dann lädt build.py neu
IMAGES = set()   # alle verwendeten Fotos (Unsplash-ID, Breite) – werden lokal gespeichert
ROOT = "{ROOT}"  # Platzhalter, wird pro Seite durch den relativen Pfad zur Startseite ersetzt


def img(pid, w=900):
    IMAGES.add((pid, w))
    return f"{ROOT}assets/img/{pid}-{w}.webp"


def srcset(pid, widths, sizes):
    """src + srcset + sizes: Handys laden die kleine Fassung, große Bildschirme die große."""
    ws = sorted(widths)
    return f'src="{img(pid, ws[-1])}" srcset="{", ".join(f"{img(pid, w)} {w}w" for w in ws)}" sizes="{sizes}"'


# ---------------------------------------------------------------- Icons
ICONS = {
    "palette": '<path d="M12 3a9 9 0 1 0 0 18c1.1 0 1.5-.8 1.5-1.5 0-.9-.7-1.2-.7-2 0-.9.7-1.5 1.6-1.5H16a5 5 0 0 0 5-5c0-4.4-4-8-9-8Z"/><circle cx="7.5" cy="11" r="1"/><circle cx="10" cy="7" r="1"/><circle cx="15" cy="7.5" r="1"/>',
    "phone": '<rect x="7" y="2.5" width="10" height="19" rx="2.5"/><path d="M11 18.5h2"/>',
    "bolt": '<path d="M13 2 4 14h7l-1 8 9-12h-7l1-8Z"/>',
    "lock": '<rect x="4.5" y="10.5" width="15" height="10" rx="2.5"/><path d="M8 10.5V7a4 4 0 0 1 8 0v3.5"/>',
    "doc": '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8l-5-5Z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>',
    "search": '<circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.2-4.2"/>',
    "pencil": '<path d="M4 20h4L19 9l-4-4L4 16v4Z"/><path d="m13.5 6.5 4 4"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="m4 7 8 6 8-6"/>',
    "calendar": '<rect x="3.5" y="5" width="17" height="15.5" rx="2.5"/><path d="M8 3v4M16 3v4M3.5 10h17"/>',
    "list": '<path d="M9 6h11M9 12h11M9 18h11"/><circle cx="4.5" cy="6" r="1"/><circle cx="4.5" cy="12" r="1"/><circle cx="4.5" cy="18" r="1"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c.8-3.6 3.4-5.5 6.5-5.5s5.7 1.9 6.5 5.5"/><path d="M16 4.8a3.5 3.5 0 0 1 0 6.4M18.5 14.9c1.6.8 2.6 2.5 3 5.1"/>',
    "image": '<rect x="3" y="4.5" width="18" height="15" rx="2.5"/><circle cx="8.5" cy="9.5" r="1.8"/><path d="m21 16-5-5-9 9"/>',
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    "pin": '<path d="M12 21s-6.5-5.6-6.5-11a6.5 6.5 0 0 1 13 0C18.5 15.4 12 21 12 21Z"/><circle cx="12" cy="10" r="2.3"/>',
    "gift": '<rect x="3.5" y="8.5" width="17" height="4" rx="1"/><path d="M5 12.5V20h14v-7.5M12 8.5V20M12 8.5C10 4 6.5 4.5 7 7c.3 1.2 2 1.5 5 1.5ZM12 8.5c2-4.5 5.5-4 5-1.5-.3 1.2-2 1.5-5 1.5Z"/>',
    "shield": '<path d="M12 3 5 6v5.5c0 4.3 3 7.8 7 9.5 4-1.7 7-5.2 7-9.5V6l-7-3Z"/><path d="m9 12 2 2 4-4"/>',
}


def icon(name):
    return f'<svg class="i" viewBox="0 0 24 24">{ICONS[name]}</svg>'


CK = '<span class="ck"><svg class="i" viewBox="0 0 24 24"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg></span>'
ARR_L = '<svg class="i" viewBox="0 0 24 24"><path d="m15 5-7 7 7 7"/></svg>'
ARR_R = '<svg class="i" viewBox="0 0 24 24"><path d="m9 5 7 7-7 7"/></svg>'


# ---------------------------------------------------------------- Vorschauen
MOCK_FONTS = {
    "salon": ["Italiana", "Jost:wght@400;500"],
    "holz": ["Big+Shoulders+Display:wght@700;800", "Barlow:wght@400;500;600"],
    "cafe": ["Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,400", "Manrope:wght@400;500;600"],
    "praxis": ["Plus+Jakarta+Sans:wght@400;500;600;700"],
    "flor": ["Cormorant+Garamond:ital,wght@0,500;0,600;1,500;1,600", "Jost:wght@400;500"],
    "coach": ["DM+Serif+Display:ital@0;1", "DM+Sans:wght@400;500;600"],
    "elek": ["Outfit:wght@400;500;600;700"],
    "dach": ["Archivo:wght@400;500;600;800"],
    "bad": ["Sora:wght@400;500;600"],
    "maler": ["Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,800"],
    "garten": ["Young+Serif", "Figtree:wght@400;500;600"],
    "kfz": ["Barlow+Condensed:wght@700", "Barlow:wght@400;500;600"],
    "metall": ["Space+Grotesk:wght@400;500;700"],
}

MOCKS = {
    "salon": dict(word="Friseure.", label="Beispiel-Homepage für einen Friseursalon", html=f"""
<div class="mh"><div class="logo">Mira</div><nav><a>Leistungen</a><a>Preise</a><a>Team</a><a>Kontakt</a></nav><a class="mbtn">Termin buchen</a></div>
<div class="hero-m">
  <div>
    <p class="kick">Schnitt &amp; Farbe · Recklinghausen</p>
    <h4>Haare, die zu dir passen.</h4>
    <p class="txt">Wir nehmen uns Zeit für deinen Typ. Termine buchst du online, rund um die Uhr.</p>
    <a class="mbtn big">Freien Termin finden</a>
  </div>
  <div class="arch">
    <img src="{img('1560869713-7d0a29430803', 820)}" alt="" decoding="async">
    <div class="slot"><small>Heute noch frei</small><span>14:30</span><span>16:00</span><span>17:15</span></div>
  </div>
</div>
<ul class="prices"><li>Damenschnitt<b>ab 48 €</b></li><li>Herrenschnitt<b>29 €</b></li><li>Balayage<b>ab 140 €</b></li><li>Hochsteckfrisur<b>ab 65 €</b></li></ul>"""),

    "holz": dict(word="Tischler.", label="Beispiel-Homepage für eine Tischlerei", html=f"""
<div class="mh"><div class="logo">HOLZWERK BRANDT</div><nav><a>Möbel</a><a>Küchen</a><a>Projekte</a><a>Werkstatt</a></nav><a class="mbtn">Anfrage</a></div>
<div class="hero-m">
  <div class="copy">
    <p class="kick">Tischlerei · Meisterbetrieb seit 1987</p>
    <h4>Massivholz nach Maß.</h4>
    <p class="txt">Küchen, Einbauschränke und Tische aus unserer Werkstatt in Marl. Geplant mit dir, gebaut für Jahrzehnte.</p>
    <div class="row"><a class="mbtn fill">Projekt anfragen</a><a class="mbtn">Referenzen</a></div>
  </div>
  <div class="wood">
    <img src="{img('1758977403865-f79e156415b3', 1000)}" alt="" decoding="async">
    <div class="tag"><b>ESSTISCH „LIPPE“</b>Eiche geölt · 240 × 95 cm</div>
  </div>
</div>
<div class="ruler"></div>"""),

    "cafe": dict(word="Cafés.", label="Beispiel-Homepage für ein Café", html=f"""
<div class="mh"><div class="logo"><i></i>Café Laune</div><nav><a>Karte</a><a>Frühstück</a><a>Torten</a><a>Anfahrt</a></nav><a class="mbtn">Tisch reservieren</a></div>
<div class="hero-m">
  <div>
    <span class="kick">Frühstück · Kuchen · Kaffee</span>
    <h4>Guter Kaffee,<br><em>gute Laune.</em></h4>
    <p class="txt">Frühstück bis 14 Uhr, Kuchen aus der eigenen Backstube und Bohnen von einer kleinen Rösterei aus Bochum.</p>
    <div class="row"><a class="mbtn big">Speisekarte ansehen</a><a class="mbtn big ghost">Anfahrt</a></div>
    <div class="info"><div><b>Mo–Sa</b>8–18 Uhr</div><div><b>Sonntag</b>9–17 Uhr</div><div><b>Torten</b>auf Bestellung</div></div>
  </div>
  <div class="vis">
    <img src="{img('1566939937483-6eabe6f79e15', 1000)}" alt="" decoding="async">
    <div class="badge"><small>seit</small>2019</div>
    <div class="card"><h5>Heute frisch</h5><ul><li>Zimtschnecke<b>3,20</b></li><li>Käsekuchen<b>3,90</b></li><li>Flat White<b>3,80</b></li></ul></div>
  </div>
</div>"""),

    "praxis": dict(word="Physiotherapeuten.", label="Beispiel-Homepage für eine Physiopraxis", html=f"""
<div class="mh"><div class="logo"><i></i>Praxis am Park</div><nav><a>Therapien</a><a>Team</a><a>Kurse</a><a>Kontakt</a></nav><a class="mbtn">Termin online</a></div>
<div class="hero-m">
  <div>
    <span class="kick">Physiotherapie · Alle Kassen &amp; privat</span>
    <h4>Wieder <span>schmerzfrei</span> bewegen.</h4>
    <p class="txt">Manuelle Therapie, Krankengymnastik und Hausbesuche. Mit kurzen Wartezeiten und Terminen auch am Abend.</p>
    <div class="row"><a class="mbtn big">Termin buchen</a><a class="mbtn big ghost">Therapien</a></div>
    <div class="trust"><span><i></i>Alle Kassen</span><span><i></i>Hausbesuche</span><span><i></i>Bis 20 Uhr</span></div>
  </div>
  <div class="pvis">
    <img src="{img('1706353399656-210cca727a33', 1000)}" alt="" decoding="async">
    <div class="book">
      <h5>Termin online buchen</h5>
      <p>Ersttermin · 30 Minuten</p>
      <div class="days"><span>Mo<b>13</b></span><span class="sel">Di<b>14</b></span><span>Mi<b>15</b></span><span>Do<b>16</b></span><span>Fr<b>17</b></span></div>
      <div class="slots"><span>07:30</span><span class="sel">09:00</span><span>11:45</span></div>
      <a class="mbtn">Termin bestätigen</a>
    </div>
  </div>
</div>"""),

    "flor": dict(word="Blumenläden.", label="Beispiel-Homepage für einen Blumenladen", html=f"""
<div class="mh"><div class="logo">Blütenreich</div><nav><a>Sträuße</a><a>Hochzeit</a><a>Trauer</a><a>Kontakt</a></nav><a class="mbtn">Strauß bestellen</a></div>
<div class="hero-m">
  <div>
    <p class="kick">Floristik · Dortmund</p>
    <h4>Blumen für<br><em>jeden Moment.</em></h4>
    <p class="txt">Sträuße, Hochzeitsfloristik und Trauerkränze, jeden Tag frisch gebunden. Deinen Wunschstrauß fragst du bequem online an.</p>
    <a class="mbtn big">Strauß anfragen</a>
    <div class="cats"><div><i style="background:#f3c7c9"></i>Sträuße</div><div><i style="background:#e8dcc6"></i>Hochzeit</div><div><i style="background:#cdd6c2"></i>Trauer</div></div>
  </div>
  <div class="fvis">
    <img src="{img('1706796204047-42799881e989', 1000)}" alt="" decoding="async">
    <div class="note">Heute frisch<b>Pfingstrosen</b></div>
    <div class="pill">Lieferung am selben Tag</div>
  </div>
</div>"""),

    "coach": dict(word="Coaches.", label="Beispiel-Homepage für ein Coaching", html=f"""
<div class="mh"><div class="logo">Jonas Kramer<small>Coaching</small></div><nav><a>Angebote</a><a>Über mich</a><a>Artikel</a><a>Kontakt</a></nav><a class="mbtn">Erstgespräch</a></div>
<div class="hero-m">
  <div class="cvis">
    <img src="{img('1789757112859-7a907ef6719c', 900)}" alt="" decoding="async">
    <div class="stat"><b>12</b>Jahre Erfahrung</div>
  </div>
  <div>
    <p class="kick">Business-Coaching</p>
    <h4>Klarheit für deinen <em>nächsten Schritt.</em></h4>
    <p class="txt">Für Selbstständige und Führungskräfte, die Entscheidungen treffen wollen, statt sie zu vertagen.</p>
    <a class="mbtn big">Kostenloses Erstgespräch</a>
    <div class="offers"><div>Einzelcoaching<span>→</span></div><div>Workshops für Teams<span>→</span></div><div>Programm für Führungskräfte<span>→</span></div></div>
  </div>
</div>"""),

    "elek": dict(word="Elektriker.", label="Beispiel-Homepage für einen Elektrobetrieb", html=f"""
<div class="mh"><div class="logo"><i></i><div>Voltwerk<small>Elektrotechnik</small></div></div><nav><a>Leistungen</a><a>Photovoltaik</a><a>Referenzen</a><a>Karriere</a></nav><a class="mbtn">Angebot anfragen</a></div>
<div class="hero-m">
  <div>
    <span class="kick">Meisterbetrieb · Innungsmitglied</span>
    <h4>Strom, der einfach <span>funktioniert.</span></h4>
    <p class="txt">Elektroinstallation, Photovoltaik und Wallboxen für Privat- und Gewerbekunden in Dortmund und Umgebung.</p>
    <div class="row"><a class="mbtn big">Angebot anfragen</a><a class="mbtn big ghost">Leistungen</a></div>
    <div class="svc"><div><i></i>Photovoltaik</div><div><i></i>Wallbox</div><div><i></i>Smart Home</div><div><i></i>E-Check</div></div>
  </div>
  <div class="evis">
    <img src="{img('1646640381839-02748ae8ddf0', 1000)}" alt="" decoding="async">
    <div class="note"><small>Notdienst</small><b>Rund um die Uhr erreichbar</b><span>Auch am Wochenende</span></div>
  </div>
</div>"""),

    "dach": dict(word="Dachdecker.", label="Beispiel-Homepage für einen Dachdecker", html=f"""
<div class="mh"><div class="logo"><i></i><div>KESSLER<small>DACHDECKERMEISTER</small></div></div><nav><a>Leistungen</a><a>Referenzen</a><a>Dachcheck</a><a>Kontakt</a></nav><a class="mbtn">Dachcheck anfragen</a></div>
<div class="hero-m">
  <img src="{img('1763665814538-8ba04597286c', 1400)}" alt="" decoding="async">
  <div class="copy">
    <p class="kick">Steildach · Flachdach · Dachfenster</p>
    <h4>Ein Dach, auf das du dich verlassen kannst.</h4>
    <p class="txt">Neueindeckung, Sanierung und Reparatur im Raum Kassel. Mit festem Ansprechpartner vom Aufmaß bis zur Abnahme.</p>
    <div class="row"><a class="mbtn big">Kostenlosen Dachcheck anfragen</a><a class="mbtn big ghost">Referenzen</a></div>
  </div>
  <div class="stats"><div><b>35</b>Jahre Erfahrung</div><div><b>1.200+</b>Dächer gedeckt</div><div><b>24 h</b>Sturmschaden-Notdienst</div></div>
</div>"""),

    "bad": dict(word="Installateure.", label="Beispiel-Homepage für einen Sanitär- und Heizungsbetrieb", html=f"""
<div class="mh"><div class="logo"><i></i><div>Wassermann<small>Haustechnik</small></div></div><nav><a>Bad</a><a>Heizung</a><a>Wärmepumpe</a><a>Notdienst</a></nav><a class="mbtn">Beratung anfragen</a></div>
<div class="hero-m">
  <div>
    <span class="kick">Notdienst rund um die Uhr</span>
    <h4>Bad und Heizung <span>aus einer Hand.</span></h4>
    <p class="txt">Vom barrierefreien Bad bis zur Wärmepumpe: Wir planen, installieren und warten. Sauber, pünktlich und zum Festpreis.</p>
    <div class="row"><a class="mbtn big">Wunschbad planen</a><a class="mbtn big ghost">Heizung tauschen</a></div>
    <div class="tags"><span>Badsanierung</span><span>Wärmepumpe</span><span>Heizungswartung</span><span>Barrierefrei</span></div>
  </div>
  <div class="bvis">
    <img src="{img('1763485956310-55f3c0e822d5', 1000)}" alt="" decoding="async">
    <div class="plan"><h5>Dein neues Bad in 3 Schritten</h5><ul><li><b>1</b>Beratung bei dir zu Hause</li><li><b>2</b>3D-Planung mit Festpreis</li><li><b>3</b>Einbau in 10 Werktagen</li></ul></div>
  </div>
</div>"""),

    "maler": dict(word="Maler.", label="Beispiel-Homepage für einen Malerbetrieb", html=f"""
<div class="mh"><div class="logo">Farbwerk<span></span></div><nav><a>Innen</a><a>Fassade</a><a>Referenzen</a><a>Kontakt</a></nav><a class="mbtn">Angebot anfragen</a></div>
<div class="hero-m">
  <div>
    <p class="kick">Malermeister Lorenz · Göttingen</p>
    <h4>Farbe macht den <em>Unterschied.</em></h4>
    <p class="txt">Wände, Fassaden und Böden, sauber abgeklebt und pünktlich fertig. Nach dem Aufmaß bekommst du ein Festpreis-Angebot.</p>
    <div class="row"><a class="mbtn big">Kostenloses Aufmaß</a><a class="mbtn big ghost">Referenzen</a></div>
    <div class="svc"><span>Innenanstrich</span><span>Fassade</span><span>Tapeten</span><span>Böden</span></div>
  </div>
  <div class="mvis">
    <img src="{img('1688372199140-cade7ae820fe', 1000)}" alt="" decoding="async">
    <div class="pal"><small>Farben des Monats</small><div><i style="background:#9fb39a"></i><i style="background:#c8714f"></i><i style="background:#1f3a5a"></i><i style="background:#e7d6b8"></i></div></div>
  </div>
</div>"""),

    "garten": dict(word="Gartenbauer.", label="Beispiel-Homepage für einen Garten- und Landschaftsbau", html=f"""
<div class="mh"><div class="logo"><i></i>Grünzeit</div><nav><a>Gartenplanung</a><a>Pflaster</a><a>Pflege</a><a>Projekte</a></nav><a class="mbtn">Beratung vor Ort</a></div>
<div class="hero-m">
  <div class="gvis">
    <img src="{img('1784293449032-200db587788c', 1000)}" alt="" decoding="async">
    <div class="quote"><b>„Unser Garten ist nicht wiederzuerkennen.“</b><span>Familie Weber, Baunatal</span></div>
  </div>
  <div class="copy">
    <p class="kick">Garten- und Landschaftsbau</p>
    <h4>Gärten, in denen man gern draußen ist.</h4>
    <p class="txt">Wir planen, pflastern und pflanzen. Und wenn alles fertig ist, kümmern wir uns auf Wunsch auch um die Pflege.</p>
    <div class="row"><a class="mbtn big">Gartenplanung anfragen</a></div>
    <ul class="list"><li>Gartenplanung</li><li>Pflaster &amp; Wege</li><li>Teiche &amp; Wasser</li><li>Gartenpflege</li></ul>
  </div>
</div>"""),

    "kfz": dict(word="Kfz-Werkstätten.", label="Beispiel-Homepage für eine Kfz-Werkstatt", html=f"""
<div class="kvis"><img src="{img('1615906655593-ad0386982a0f', 1000)}" alt="" decoding="async"></div>
<div class="mh"><div class="logo">Becker<span>.</span><small>Kfz-Meisterbetrieb</small></div><nav><a>Werkstatt</a><a>Reifen</a><a>HU/AU</a><a>Kontakt</a></nav><a class="mbtn">Termin buchen</a></div>
<div class="hero-m">
  <p class="kick">Alle Marken · Meisterwerkstatt</p>
  <h4>Dein Auto in besten Händen.</h4>
  <p class="txt">Inspektion, Reparatur und Reifenservice zum fairen Festpreis. Mit Hol- und Bringservice im Stadtgebiet.</p>
  <div class="book"><div>Leistung<span>Inspektion</span></div><div>Fahrzeug<span>VW Golf</span></div><div>Wunschtermin<span>Di, 14.10.</span></div><a class="mbtn">Anfragen</a></div>
  <div class="svc"><span>HU/AU</span><span>Inspektion</span><span>Reifen</span><span>Klimaservice</span></div>
</div>"""),

    "metall": dict(word="Metallbauer.", label="Beispiel-Homepage für einen Metallbaubetrieb", html=f"""
<div class="mh"><div class="logo"><i></i><div>WENDT<small>Stahl- &amp; Metallbau</small></div></div><nav><a>Leistungen</a><a>Fertigung</a><a>Projekte</a><a>Karriere</a></nav><a class="mbtn">Projekt anfragen</a></div>
<div class="hero-m">
  <div>
    <p class="kick">Metallbau · Fertigung · Montage</p>
    <h4>Stahl. <span>Präzise</span> gefertigt.</h4>
    <p class="txt">Treppen, Geländer, Hallen und Bauteile in Serie. Von der Zeichnung bis zur Montage aus einer Hand.</p>
    <div class="row"><a class="mbtn big">Projekt anfragen</a><a class="mbtn big ghost">Referenzen</a></div>
    <div class="spec"><div><b>25 mm</b>Laserschneiden</div><div><b>EN 1090</b>zertifiziert</div><div><b>48 h</b>Express-Fertigung</div></div>
  </div>
  <div class="xvis">
    <img src="{img('1698664683348-f9f35b809821', 1000)}" alt="" decoding="async">
    <div class="lab"><b>Projekt</b> Außentreppe, feuerverzinkt</div>
  </div>
</div>"""),
}
SLIDER_ORDER = ["elek", "dach", "salon", "bad", "holz", "cafe", "maler", "praxis"]


MOCK_IMG = re.compile(r'<img src="\{ROOT\}assets/img/([\w-]+)-(\d+)\.webp"')


def mock(key, on=False, lazy=False):
    """Vorschau-Canvas. lazy: Bilder erst laden, wenn die Vorschau im Slider gezeigt wird (app.js)."""
    m = MOCKS[key]
    cls = "m m-" + key + (" on" if on else "")
    html = m["html"]
    # Links in den Vorschauen sind Attrappen: <span> statt <a>, damit Google keine toten Links findet
    html = html.replace("<a>", "<span>").replace('<a class="', '<span class="').replace("</a>", "</span>")
    # Kleinere Bildfassung fürs Handy; die Vorschau ist dort nur etwa halb so breit wie der Bildschirm
    sizes = "(max-width: 1240px) 95vw, 1150px" if key == "dach" else "(max-width: 1240px) 48vw, 560px"
    def resp(mt):
        attrs = srcset(mt.group(1), [480, int(mt.group(2))], sizes)
        if lazy:
            attrs = 'src="data:image/gif;base64,R0lGODlhAQABAAAAACw=" ' + attrs.replace('src="', 'data-src="', 1).replace('srcset="', 'data-srcset="')
        return "<img " + attrs
    html = MOCK_IMG.sub(resp, html)
    # Überschriften der Attrappe sind keine Überschriften dieser Seite (Gliederung für Google und Screenreader)
    html = re.sub(r"<h([45])>", r'<p class="h\1">', html)
    html = re.sub(r"</h[45]>", "</p>", html)
    html = html.replace('alt=""', f'alt="{m["label"]}"')
    return f'<article class="{cls}" data-word="{m["word"]}" data-label="{m["label"]}">{html}\n</article>'


# ---------------------------------------------------------------- Branchen
SONST_FOTO = "1542330952-bffc55e812b2"

# slug:       Adresse der Landingpage (SEO: "homepage-fuer-…")
# name:       kurzer Name für Kacheln, Listen und Slider
# kw:         kurzes Suchwort für den Seitentitel ("Homepage für … erstellen lassen")
# h1:         "Homepage für …" (Überschrift)
# text:       eigener Absatz pro Branche, damit keine Seite nach Kopie aussieht (wichtig für Google)
# seiten:     Vorschläge für zusätzliche Inhaltsseiten im Konfigurator (je 49,99 €)
# empfohlen:  Schlüssel aus FUNKTIONEN, die bei dieser Branche als "Beliebt" markiert werden
UMKREIS = "In welchem Umkreis arbeitest du?"
BRANCHEN = [
    dict(slug="homepage-fuer-elektriker", kw="Elektriker", name="Elektriker", h1="Elektriker", mock="elek",
         foto="1621905251189-08b45d6a269e",
         lead="Von Photovoltaik bis E-Check: Zeig, was du kannst, und bekomm Anfragen mit allen Infos, die du für ein Angebot brauchst.",
         text="Ob Photovoltaik, Wallbox oder Altbausanierung: Kunden suchen ihren Elektriker heute online. Eine Homepage für Elektriker zeigt deine Leistungen, dein Einsatzgebiet und deine Referenzen und sammelt Anfragen mit allen Infos für dein Angebot.",
         feats=[("bolt", "Leistungen im Überblick", "Photovoltaik, Wallbox, Smart Home: Jede Leistung bekommt ihren eigenen Bereich."),
                ("pencil", "Anfragen mit Details", "Das Anfrageformular fragt Objekt, Umfang und Wunschtermin ab, auf Wunsch mit Fotos."),
                ("pin", "Dein Einzugsgebiet", "Kunden sehen sofort, ob du bei ihnen arbeitest. Das hilft auch bei Google."),
                ("users", "Fachkräfte finden", "Eine Karriereseite für Elektronikerinnen, Elektroniker und Azubis.")],
         seiten=["Leistungen", "Photovoltaik & Wallbox", "Referenzen", "Über uns", "Karriere"],
         empfohlen=["anfrage", "kontakt", "karte"],
         extra=(UMKREIS, "Zum Beispiel: Dortmund und 30 km Umkreis", False)),
    dict(slug="homepage-fuer-dachdecker", kw="Dachdecker", name="Dachdecker", h1="Dachdecker", mock="dach",
         foto="1763665814965-b5c4b3547908",
         lead="Zeig, welche Dächer du deckst, und bekomm Anfragen mit Fotos vom Schaden. Mit Referenzen, Leistungen und einem klaren Weg zum Dachcheck.",
         text="Wer ein undichtes Dach hat oder eine Sanierung plant, sucht zuerst im Internet. Eine gute Homepage für Dachdecker zeigt Referenzen, erklärt Leistungen wie Steildach, Flachdach und Dachfenster und macht es leicht, eine Anfrage mit Fotos zu schicken.",
         feats=[("image", "Referenzen von oben", "Vorher-nachher-Bilder deiner Dächer überzeugen mehr als jeder Text."),
                ("pencil", "Anfragen mit Fotos", "Kunden schicken Fotos vom Schaden gleich mit. So schätzt du besser ein, was zu tun ist."),
                ("pin", "Dein Einsatzgebiet", "Kunden sehen sofort, ob du bei ihnen arbeitest. Das hilft auch bei Google."),
                ("users", "Azubis und Gesellen finden", "Eine Karriereseite zeigt, wie es bei euch auf dem Dach zugeht.")],
         seiten=["Leistungen", "Referenzen", "Dachsanierung & Förderung", "Über uns", "Karriere"],
         empfohlen=["anfrage", "galerie", "bewertungen"],
         extra=(UMKREIS, "Zum Beispiel: Kassel und 50 km Umkreis", False)),
    dict(slug="homepage-fuer-sanitaer-heizung", kw="Installateure", name="Sanitär & Heizung", h1="Installateure & SHK-Betriebe", mock="bad",
         foto="1749532125405-70950966b0e5",
         lead="Bad, Heizung, Wärmepumpe: Zeig, was dein Betrieb kann, und bekomm Anfragen, mit denen du direkt ein Angebot machen kannst.",
         text="Bei einem Rohrbruch zählt jede Minute, bei einer neuen Heizung zählt Vertrauen. Eine Homepage für Installateure und SHK-Betriebe zeigt beides: deinen Notdienst gut sichtbar ganz oben und deine Leistungen von der Badsanierung bis zur Wärmepumpe verständlich erklärt.",
         feats=[("clock", "Notdienst gut sichtbar", "Deine Notdienst-Nummer steht auf jeder Seite ganz oben, auch auf dem Handy."),
                ("list", "Leistungen verständlich", "Badsanierung, Heizungstausch, Wärmepumpe: Jede Leistung kurz und ohne Fachchinesisch erklärt."),
                ("pencil", "Anfragen mit Fotos", "Kunden schicken Fotos vom alten Bad oder vom Typenschild der Heizung gleich mit."),
                ("image", "Badideen zeigen", "Eine Galerie mit fertigen Bädern macht Lust aufs eigene Projekt.")],
         seiten=["Badsanierung", "Heizung & Wärmepumpe", "Notdienst", "Referenzen", "Karriere"],
         empfohlen=["anfrage", "galerie", "kontakt"],
         extra=(UMKREIS, "Zum Beispiel: Göttingen und 30 km Umkreis", False)),
    dict(slug="homepage-fuer-maler", kw="Maler", name="Maler", h1="Maler & Lackierer", mock="maler",
         foto="1742900280861-32bed068938b",
         lead="Farbe wirkt am besten auf großen Bildern. Zeig deine Arbeiten, erkläre deine Leistungen und lass Kunden direkt ein Aufmaß anfragen.",
         text="Ob Innenanstrich, Fassade oder Tapete: Kunden wollen sehen, wie sauber du arbeitest. Eine Homepage für Maler und Lackierer zeigt Vorher-nachher-Bilder, nennt deine Leistungen klar und macht die Anfrage für ein Aufmaß so einfach wie möglich.",
         feats=[("image", "Vorher und nachher", "Bilder deiner Arbeiten zeigen sofort, was du kannst."),
                ("palette", "Leistungen im Überblick", "Innenanstrich, Fassade, Tapeten und Böden, jeweils mit eigenem Bereich."),
                ("pencil", "Aufmaß anfragen", "Kunden schicken Raumgröße, Wunschtermin und Fotos gleich mit."),
                ("search", "In der Nähe gefunden werden", "Mit sauberer Struktur finden dich Kunden, die einen Maler in ihrer Nähe suchen.")],
         seiten=["Leistungen", "Referenzen", "Fassade", "Über uns", "Karriere"],
         empfohlen=["galerie", "anfrage", "bewertungen"],
         extra=(UMKREIS, "Zum Beispiel: Hannover und 40 km Umkreis", False)),
    dict(slug="homepage-fuer-tischler", kw="Tischler", name="Tischler & Schreiner", h1="Tischler & Schreiner", mock="holz",
         foto="1661447133325-a4a73386b9e4",
         lead="Zeig deine Projekte so hochwertig, wie du sie baust. Mit Referenzen, Leistungen und einem Anfrageformular, das die wichtigen Infos gleich mitliefert.",
         text="Maßanfertigungen verkaufen sich über Vertrauen und gute Bilder. Eine Homepage für Tischler und Schreiner zeigt deine schönsten Projekte, erklärt, wie ein Auftrag abläuft, und sammelt Anfragen mit Maßen und Fotos.",
         feats=[("image", "Referenzen, die überzeugen", "Große Fotos deiner Projekte sagen mehr als jede Beschreibung."),
                ("pencil", "Anfragen mit allen Infos", "Das Anfrageformular fragt Maße, Wunschtermin und Fotos ab. So bekommst du Anfragen, mit denen du arbeiten kannst."),
                ("pin", "Dein Einzugsgebiet", "Kunden sehen sofort, ob du bei ihnen arbeitest. Das hilft auch bei Google."),
                ("users", "Fachkräfte finden", "Eine Karriereseite zeigt Bewerbern, wie es bei euch in der Werkstatt ist.")],
         seiten=["Leistungen", "Referenzen", "Über uns & Werkstatt", "Ablauf", "Karriere"],
         empfohlen=["anfrage", "galerie", "karte"],
         extra=(UMKREIS, "Zum Beispiel: Marl und 40 km Umkreis", False)),
    dict(slug="homepage-fuer-gartenbau", kw="Gartenbau", name="Garten- & Landschaftsbau", h1="Garten- und Landschaftsbauer", mock="garten",
         foto="1734079692160-fcbe4be6ab96",
         lead="Große Bilder deiner schönsten Gärten, deine Leistungen auf einen Blick und Anfragen mit Fotos vom Grundstück.",
         text="Ein Garten verkauft sich über Bilder. Eine Homepage für den Garten- und Landschaftsbau zeigt deine Projekte groß, erklärt Planung, Pflasterarbeiten und Pflege verständlich und sorgt dafür, dass Kunden aus deiner Region dich bei Google finden.",
         feats=[("image", "Projekte groß zeigen", "Eine Galerie mit deinen schönsten Gärten, Terrassen und Wegen."),
                ("pencil", "Anfragen mit Fotos", "Kunden schicken Fotos und Maße vom Grundstück gleich mit."),
                ("calendar", "Pflege das ganze Jahr", "Stell deine Pflegeangebote vor, vom Heckenschnitt bis zum Winterdienst."),
                ("pin", "Dein Einzugsgebiet", "Kunden sehen sofort, ob du bei ihnen arbeitest. Das hilft auch bei Google.")],
         seiten=["Gartenplanung", "Pflaster & Wege", "Gartenpflege", "Referenzen", "Über uns"],
         empfohlen=["galerie", "anfrage", "bewertungen"],
         extra=(UMKREIS, "Zum Beispiel: Kassel und 30 km Umkreis", False)),
    dict(slug="homepage-fuer-kfz-werkstaetten", kw="Kfz-Werkstätten", name="Kfz-Werkstatt", h1="Kfz-Werkstätten", mock="kfz",
         foto="1643700973089-baa86a1ab9ee",
         lead="Leistungen, Preise und ein schneller Weg zum Werkstatttermin. Damit Kunden nicht erst anrufen müssen, um zu erfahren, was du anbietest.",
         text="Wer eine Werkstatt sucht, will drei Dinge wissen: Was machst du, was kostet es ungefähr und wann ist ein Termin frei? Eine Homepage für Kfz-Werkstätten beantwortet genau das, zeigt deine Google-Bewertungen und macht die Terminanfrage leicht.",
         feats=[("list", "Leistungen & Festpreise", "Inspektion, HU/AU, Reifen und Klimaservice mit Preisen, die du selbst pflegst."),
                ("calendar", "Termine online", "Wir binden dein Buchungstool ein, damit Kunden Termine auch abends anfragen."),
                ("shield", "Vertrauen durch Bewertungen", "Deine Google-Bewertungen direkt auf der Seite."),
                ("pin", "Anfahrt & Öffnungszeiten", "Das Wichtigste steht ganz oben, auf Wunsch mit Karte.")],
         seiten=["Leistungen & Preise", "Reifenservice", "Über uns", "Karriere"],
         empfohlen=["termin", "bewertungen", "pflege"],
         extra=("Worauf ist deine Werkstatt spezialisiert?", "Zum Beispiel: alle Marken, Oldtimer, Elektroautos", False)),
    dict(slug="homepage-fuer-metallbau", kw="Metallbau", name="Metallbau & Fertigung", h1="Metallbauer & Fertigungsbetriebe", mock="metall",
         foto="1764245546004-e6b743242a80",
         lead="Zeig deine Projekte, deine Fertigung und deine Zertifikate. Und bekomm Anfragen, bei denen Skizzen und Fotos gleich dabei sind.",
         text="Architekten, Bauherren und Industriekunden prüfen einen Metallbauer zuerst online. Eine Homepage für Metallbau und Fertigung zeigt Referenzen, Maschinenpark und Zertifizierungen und nimmt Anfragen mit Skizzen und Fotos direkt entgegen.",
         feats=[("image", "Referenzen", "Treppen, Geländer, Hallen: Große Bilder zeigen die Qualität deiner Arbeit."),
                ("shield", "Zertifikate & Maschinen", "EN 1090, Laser, Kantbank: Zeig, was deine Fertigung kann."),
                ("pencil", "Anfragen mit Skizze", "Kunden schicken Skizzen oder Fotos direkt über das Formular mit."),
                ("users", "Fachkräfte finden", "Eine Karriereseite für Metallbauer, Schweißer und Azubis.")],
         seiten=["Leistungen", "Fertigung & Maschinen", "Referenzen", "Über uns", "Karriere"],
         empfohlen=["anfrage", "galerie", "kontakt"],
         extra=("Für wen fertigst du vor allem?", "Zum Beispiel: Privatkunden, Architekten, Industrie", False)),
    dict(slug="homepage-fuer-friseure", kw="Friseure", name="Friseur", h1="Friseure", mock="salon",
         foto="1582095133179-bfd08e2fc6b3",
         lead="Preise, Online-Termine und dein Team: Alles, was deine Kundinnen und Kunden vor dem Termin wissen wollen. Schön gestaltet und schnell online.",
         text="Bevor jemand einen neuen Friseur ausprobiert, schaut er sich Preise, Bilder und Bewertungen an. Eine Homepage für Friseure zeigt all das auf einen Blick und lässt Kundinnen und Kunden direkt einen Termin buchen, auch nach Feierabend.",
         feats=[("calendar", "Online-Termine", "Wir binden dein Buchungstool ein. So buchen Kunden rund um die Uhr, auch wenn du gerade schneidest."),
                ("list", "Preise immer aktuell", "Mit der Preisliste zum Selbstpflegen änderst du Preise in Sekunden. Oder wir übernehmen das im Wartungspaket."),
                ("users", "Dein Team", "Stell dein Team mit Fotos vor. Das schafft Vertrauen vor dem ersten Besuch."),
                ("image", "Arbeiten zeigen", "Eine Galerie mit Schnitten und Farben zeigt, was ihr könnt.")],
         seiten=["Leistungen & Preise", "Team", "Über uns", "Produkte & Marken", "Karriere"],
         empfohlen=["termin", "bewertungen", "galerie"],
         extra=("Was macht deinen Salon besonders?", "Zum Beispiel: Spezialisiert auf Locken, vegane Produkte, Barber-Ecke.", False)),
    dict(slug="homepage-fuer-cafes-baeckereien", kw="Cafés", name="Café & Bäckerei", h1="Cafés & Bäckereien", mock="cafe",
         foto="1753351052363-53ce102830eb",
         lead="Speisekarte, Öffnungszeiten und Tortenbestellung an einem Ort. Schön gestaltet, damit man schon beim Anschauen Hunger bekommt.",
         text="Wer ein Café sucht, will Öffnungszeiten, Speisekarte und Bilder sehen, am besten auf dem Handy. Eine Homepage für Cafés und Bäckereien zeigt genau das und macht Tortenbestellungen und Reservierungen einfach.",
         feats=[("list", "Speisekarte, immer aktuell", "Pflege deine Speisekarte selbst oder lass sie uns im Wartungspaket aktualisieren."),
                ("clock", "Öffnungszeiten & Anfahrt", "Das Wichtigste steht ganz oben, auf Wunsch mit Anfahrtskarte."),
                ("gift", "Bestellungen & Reservierungen", "Tortenbestellung oder Tischreservierung per Formular, direkt in dein Postfach."),
                ("search", "Gut gefunden werden", "Schnelle Ladezeiten und eine saubere Struktur helfen, wenn jemand ein Café in der Nähe sucht.")],
         seiten=["Speisekarte", "Über uns", "Torten & Catering", "Veranstaltungen"],
         empfohlen=["pflege", "karte", "bewertungen"],
         extra=("Was macht deine Bäckerei oder dein Café besonders?", "Zum Beispiel: Sauerteigbrot, Frühstück bis 14 Uhr, Terrasse.", False)),
    dict(slug="homepage-fuer-physiotherapeuten", kw="Physiotherapeuten", name="Physiotherapie", h1="Physiotherapeuten", mock="praxis",
         foto="1645005512968-0c1fe99f0093",
         lead="Therapien verständlich erklärt, Termine online buchbar und alle Infos zu Kassen und Anfahrt auf einen Blick. Das entlastet deinen Empfang.",
         text="Neue Patientinnen und Patienten suchen online nach einer Praxis in ihrer Nähe. Eine Homepage für Physiotherapeuten erklärt Therapien verständlich, zeigt Kassen und Öffnungszeiten und entlastet mit Online-Terminen den Empfang.",
         feats=[("calendar", "Online-Termine", "Wir binden dein Buchungstool ein, damit weniger Anrufe am Empfang ankommen."),
                ("list", "Therapien verständlich", "Jede Leistung kurz erklärt, damit Patientinnen und Patienten wissen, was sie erwartet."),
                ("shield", "Kassen & privat", "Klar sichtbar, welche Kassen und Leistungen ihr anbietet."),
                ("users", "Team & Stellen", "Stell dein Team vor und finde neue Therapeutinnen und Therapeuten.")],
         seiten=["Therapien", "Team", "Kurse", "Infos für Patienten", "Karriere"],
         empfohlen=["termin", "kontakt", "karte"],
         extra=("Welche Schwerpunkte hat deine Praxis?", "Zum Beispiel: Sportphysiotherapie, Lymphdrainage, Kinder.", False)),
    dict(slug="homepage-fuer-blumenlaeden", kw="Blumenläden", name="Blumenladen", h1="Blumenläden", mock="flor",
         foto="1639696194673-67b86204b885",
         lead="Deine Sträuße verdienen große Bilder. Mit Galerie, Anlässen und einem Formular, über das Kunden ihren Wunschstrauß anfragen.",
         text="Blumen kauft man mit den Augen. Eine Homepage für Blumenläden zeigt deine Sträuße groß und schön, nennt Anlässe und Liefergebiet und lässt Kunden ihren Wunschstrauß direkt anfragen.",
         feats=[("image", "Große Bildergalerie", "Deine schönsten Arbeiten, groß und hochwertig in Szene gesetzt."),
                ("gift", "Anlässe im Überblick", "Hochzeit, Trauer, Geburtstag: Kunden finden schnell, was sie suchen."),
                ("pencil", "Bestellanfrage", "Wunschstrauß, Budget und Liefertermin kommen direkt per E-Mail, auf Wunsch mit Foto."),
                ("clock", "Öffnungszeiten & Lieferung", "Wann du geöffnet hast und wohin du lieferst, steht auf jeder Seite.")],
         seiten=["Sträuße & Anlässe", "Hochzeit", "Trauer", "Über uns"],
         empfohlen=["anfrage", "galerie", "karte"],
         extra=("Wofür ist dein Laden bekannt?", "Zum Beispiel: Trockenblumen, Hochzeiten, Lieferung am selben Tag.", False)),
    dict(slug="homepage-fuer-coaches", kw="Coaches", name="Coaching & Beratung", h1="Coaches & Berater", mock="coach",
         foto="1573496359142-b8d87734a5a2",
         lead="Menschen kaufen Vertrauen. Deine Homepage zeigt, wer du bist und wie du arbeitest, und macht es leicht, ein Erstgespräch zu buchen.",
         text="Bei Coaches und Beratern entscheidet der erste Eindruck. Eine Homepage zeigt, wer du bist, für wen du arbeitest und wie die Zusammenarbeit abläuft, und macht es leicht, ein Erstgespräch zu buchen.",
         feats=[("users", "Du im Mittelpunkt", "Gute Fotos und eine klare Geschichte schaffen Vertrauen vor dem ersten Gespräch."),
                ("list", "Angebote klar erklärt", "Pakete mit Ablauf und Ergebnis, damit Interessenten wissen, was sie bekommen."),
                ("calendar", "Erstgespräch buchen", "Wir binden deinen Kalender ein, damit Interessenten direkt einen Termin wählen."),
                ("doc", "Artikel & Neuigkeiten", "Mit dem Blog schreibst du Beiträge selbst, in einem einfachen Login-Bereich.")],
         seiten=["Angebote", "Über mich", "Referenzen", "Ablauf"],
         empfohlen=["termin", "blog", "kontakt"],
         extra=("Für wen arbeitest du vor allem?", "Zum Beispiel: Führungskräfte im Mittelstand, Gründerinnen, Teams.", False)),
    dict(slug="homepage-fuer-alle-branchen", kw="jede Branche", name="Andere Branche", h1=None, mock=None,
         foto=SONST_FOTO,
         lead="Kein Problem. Wir bauen Homepages für jede Branche. Stell dir im Konfigurator zusammen, was dein Betrieb braucht, und wir bauen die passende Seite.",
         text="Egal ob Hundeschule, Fahrradwerkstatt, Steuerbüro oder Produktionsbetrieb: Wir bauen Homepages für alle Branchen. Du stellst dir im Konfigurator zusammen, was du brauchst, und wir gestalten eine Seite, die zu deinem Betrieb passt.",
         feats=[("palette", "Eigenes Design", "Farben, Schriften und Bildsprache passend zu deinem Betrieb."),
                ("phone", "Zuerst fürs Handy", "Die meisten Besucher kommen mobil. Dafür gestalten wir zuerst."),
                ("search", "Bei Google auffindbar", "Saubere Struktur, Meta-Daten und Sitemap von Anfang an."),
                ("pencil", "Wartung auf Wunsch", "Im Wartungspaket halten wir deine Seite aktuell und setzen jeden Monat Änderungen für dich um.")],
         seiten=["Leistungen", "Über uns", "Referenzen", "Karriere"],
         empfohlen=["kontakt"],
         extra=("Was für einen Betrieb hast du?", "Zum Beispiel: Hundeschule, Fahrradwerkstatt, Steuerberatung", True)),
]

# ---------------------------------------------------------------- Preise (alle netto, zzgl. MwSt.)
GRUNDPREIS = 499.0      # einmalig: Startseite + bis zu 3 Rechtsseiten
HOSTING = 9.99          # monatlich, Pflicht
SEITE = 49.99           # einmalig je weitere Inhaltsseite
TEXT_PRO_SEITE = 39.0   # einmalig je Seite, wenn wir die Texte schreiben
BILD_PRO_SEITE = 39.0   # einmalig je Seite, wenn wir lizenzfreie Bilder aussuchen

# Schlüssel, Name, Preis einmalig, Art, Beschreibung
FUNKTIONEN = [
    ("kontakt", "Kontaktformular", 99.0, "Funktion", "Besucher schreiben dir direkt über die Seite, die Nachricht landet in deinem Postfach."),
    ("blog", "Blog mit eigenem Login", 149.0, "Funktion", "Du schreibst Neuigkeiten selbst, in einem einfachen Login-Bereich."),
    ("pflege", "Preisliste oder Speisekarte zum Selbstpflegen", 149.0, "Funktion", "Preise und Angebote änderst du selbst, ganz ohne uns."),
    ("anfrage", "Anfrageformular mit Foto-Upload", 149.0, "Funktion", "Kunden schicken Maße, Wünsche und Fotos gleich mit."),
    ("termin", "Online-Terminbuchung", 49.0, "Einbindung", "Wir binden dein Buchungstool ein, zum Beispiel Calendly. Das Tool selbst buchst du beim Anbieter."),
    ("bewertungen", "Google-Bewertungen", 99.0, "Funktion", "Deine besten echten Google-Bewertungen auf deiner Seite, mit Link zu deinem Google-Profil."),
    ("karte", "Anfahrtskarte", 49.0, "Einbindung", "Eine Karte, damit Kunden dich leicht finden."),
    ("galerie", "Bildergalerie", 49.0, "Funktion", "Bis zu 20 Fotos deiner Arbeiten, groß in Szene gesetzt, zum Durchblättern."),
]
# Wert, Titel, Erklärung, monatlicher Preis
DOMAIN_OPT = [
    ("Neue Domain", "Ich brauche eine neue Domain", "Wir registrieren sie auf deinen Namen.", 4.99),
    ("Domain behalten", "Ich habe eine und behalte sie bei meinem Anbieter", "Wir schicken dir die Einstellungen, die du dort einträgst.", 0.0),
    ("Domain-Umzug", "Ich habe eine und möchte sie zu euch umziehen", "Danach kümmern wir uns um alles.", 4.99),
    ("Domain unklar", "Weiß ich noch nicht", "Wir klären das per E-Mail mit dir.", 0.0),
]
SERVICE_OPT = [
    ("Nur Hosting", "Nur Hosting", "Wenn etwas nicht geht, meldest du dich bei uns.", 0.0),
    ("Monitoring", "Monitoring &amp; Ausfallmanagement", "Wir prüfen stündlich, ob deine Seite läuft, und kümmern uns bei einem Ausfall innerhalb von 48 Stunden an Werktagen.", 4.99),
    ("Wartung", "Wartung", "Wir halten deine Seite aktuell und setzen bis zu 2 Text- und 2 Bildänderungen im Monat um.", 14.99),
    ("Sorglos-Paket", "Sorglos-Paket", "Monitoring und Wartung zusammen. Du sparst 1,99 € im Monat.", 17.99),
]


def eur(x):
    """Deutsches Preisformat: 499 €, 49,99 €, 1.690 €"""
    if float(x).is_integer():
        return f"{int(x):,}".replace(",", ".") + "\u00a0€"
    return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + "\u00a0€"


# Erklärungen für die Infobuttons (Fachbegriffe)
TIPS = {
    "hosting": ("Hosting", "Hosting ist der Platz im Internet, auf dem deine Homepage liegt. Ohne Hosting ist die Seite nicht erreichbar. Eine verschlüsselte Verbindung (SSL) ist inklusive."),
    "domain": ("Domain", "Die Domain ist die Adresse deiner Homepage, zum Beispiel friseur-mueller.de."),
    "dns": ("DNS-Einstellungen", "DNS-Einstellungen verbinden deine Domain mit deiner Homepage. Du trägst sie einmal bei deinem Domain-Anbieter ein, wir sagen dir genau, was."),
    "umzug": ("Domain-Umzug", "Deine Domain wechselt von deinem bisherigen Anbieter zu uns. Danach kümmern wir uns um alles. Wir sagen dir, wann du beim alten Anbieter kündigen kannst."),
    "monitoring": ("Monitoring", "Wir prüfen jede Stunde automatisch, ob deine Seite erreichbar ist. Fällt sie aus, werden wir sofort benachrichtigt und kümmern uns innerhalb von 48 Stunden an Werktagen darum."),
    "wartung": ("Wartung", "Wir halten deine Seite technisch aktuell und setzen bis zu 2 Textänderungen und 2 Bildänderungen pro Monat für dich um."),
    "rechtsseiten": ("Rechtsseiten", "Impressum, Datenschutzerklärung und AGB. Die Seiten legen wir an, die Texte lieferst du, zum Beispiel aus einem Rechtstext-Generator. Wir sagen dir, welche Technik deine Seite nutzt."),
    "inhaltsseite": ("Weitere Seite", "Eine zusätzliche Seite mit Text und Bildern, zum Beispiel „Leistungen“ oder „Team“. Sie erscheint im Menü deiner Homepage."),
    "einbindung": ("Einbindung", "Bei einer Einbindung zeigen wir ein Werkzeug eines anderen Anbieters auf deiner Seite an, zum Beispiel deinen Terminkalender oder eine Karte. Damit der Datenschutz stimmt, lädt es erst, wenn der Besucher darauf klickt."),
    "blog": ("Blog", "Ein Bereich für Neuigkeiten. Du loggst dich ein, schreibst einen Beitrag, und er erscheint auf deiner Homepage."),
    "texte": ("Texte", "Wir schreiben die Texte für deine Seiten passend zu deiner Branche, auf Grundlage deiner Angaben und mit Unterstützung von KI. Vor dem Onlinegang prüfst du alle Inhalte und gibst sie frei."),
    "bilder": ("Lizenzfreie Bilder", "Hast du keine eigenen Fotos, suchen wir passende lizenzfreie Bilder aus Bilddatenbanken aus und bereiten sie für deine Seite auf. Du darfst sie dauerhaft auf deiner Homepage nutzen."),
    "ssl": ("SSL", "SSL sorgt für eine verschlüsselte Verbindung. Besucher erkennen das am Schloss in der Adresszeile."),
}


def tip(key):
    label, text = TIPS[key]
    return f'<button type="button" class="tip" data-tip="{escape(text)}" aria-label="Was ist {escape(label)}?">i</button>'


# ---------------------------------------------------------------- Bausteine
BASE_FONT = "Hanken+Grotesk:wght@300..700"


def logo_svg(uid):
    """Logo-Icon: Browserfenster mit Schraubenschlüssel. uid hält die Verlaufs-ID pro Seite eindeutig."""
    g = f"url(#lg{uid})"
    return (f'<svg class="logo-ic" viewBox="0 0 48 40" aria-hidden="true"><defs><linearGradient id="lg{uid}" x1="0" y1="0" x2="48" y2="40" gradientUnits="userSpaceOnUse">'
            f'<stop offset="0" stop-color="#ff9e6d"/><stop offset=".5" stop-color="#b55cf0"/><stop offset="1" stop-color="#3b7bff"/></linearGradient></defs>'
            f'<rect x="1" y="2" width="40" height="32" rx="7" fill="{g}"/><rect class="lw" x="4.5" y="10" width="33" height="20.5" rx="3.5"/>'
            f'<circle cx="7.6" cy="6.1" r="1.4" fill="#fff"/><circle cx="12" cy="6.1" r="1.4" fill="#fff"/><circle cx="16.4" cy="6.1" r="1.4" fill="#fff"/>'
            f'<rect x="8" y="13.5" width="26" height="6" rx="2" fill="{g}" opacity=".35"/><rect class="lb" x="8" y="22.6" width="11" height="2.2" rx="1.1"/><rect class="lb" x="8" y="26.2" width="7" height="2.2" rx="1.1"/>'
            f'<circle class="lr" cx="37" cy="29" r="9.6" fill="{g}"/><g transform="translate(31 23) scale(.5)"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/></g></svg>')


def brand(root, uid):
    return f'<a class="brand" href="{root}index.html" aria-label="{NAME}, zur Startseite">{logo_svg(uid)}<span class="wm">Homepage<b>Konfigurator</b></span></a>'


def _hauptschrift():
    f = OUT / "assets" / "fonts.css"
    m = re.search(r"font-family: 'Hanken Grotesk';[^}]*?url\(fonts/([^)]+)\)", f.read_text(encoding="utf-8")) if f.exists() else None
    return m.group(1) if m else ""


HAUPTSCHRIFT = _hauptschrift()


def _css_klein(css):
    """Stylesheet verkleinern: Kommentare und überflüssige Leerzeichen raus."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};])\s*", r"\1", css)
    return css.replace(";}", "}").strip()


def _hauptschrift_css(root):
    """@font-face der Hauptschrift, damit sie ohne Umweg über fonts.css sofort bekannt ist."""
    f = OUT / "assets" / "fonts.css"
    if not f.exists():
        return ""
    m = re.search(r"@font-face\s*{[^}]*font-family: 'Hanken Grotesk';[^}]*}", f.read_text(encoding="utf-8"))
    return _css_klein(m.group(0).replace("url(fonts/", f"url({root}assets/fonts/")) if m else ""


# style.css wird verkleinert direkt in jede Seite eingebettet: Der Browser muss nicht erst eine Datei laden,
# bevor er etwas anzeigt (wichtig für die Ladezeit am Handy). Gepflegt wird weiter site/assets/style.css.
STYLE_INLINE = _css_klein((OUT / "assets" / "style.css").read_text(encoding="utf-8"))


def head(title, desc, root, mock_keys=(), path="", extra=""):
    # Schriften liegen lokal (assets/fonts.css); der Browser lädt nur die, die eine Seite wirklich nutzt.
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{NAME}">
<meta property="og:locale" content="de_DE">
<meta property="og:url" content="{DOMAIN}/{path}">
<link rel="canonical" href="{DOMAIN}/{path}">
<meta name="theme-color" content="#3346ff">
<link rel="icon" href="{root}assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{root}assets/apple-touch-icon.png">{extra}
<!-- Erzeugt mit build.py – bitte dort ändern, nicht hier. -->
<link rel="preload" href="{root}assets/fonts/{HAUPTSCHRIFT}" as="font" type="font/woff2" crossorigin>
<style>{_hauptschrift_css(root)}{STYLE_INLINE}</style>
<!-- Schriften der Beispiel-Vorschauen: laden im Hintergrund, blockieren den Seitenaufbau nicht -->
<link rel="preload" href="{root}assets/fonts.css?v={VERSION}" as="style" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="{root}assets/fonts.css?v={VERSION}"></noscript>
</head>
<body>
"""


def header(root, home, legal=False):
    # Auf Rechtsseiten zeigen alle Anker auf die Startseite
    base = f"{root}index.html" if legal else ""
    start = "#branchen" if home else f"{root}index.html#branchen"
    label = "Beispiele" if home else "Branchen"
    cta = "Homepage konfigurieren" if home or legal else "Konfigurieren"
    return f"""
<header class="top">
  <div class="nav">
    {brand(root, "h")}
    <ul>
      <li><a href="{start}">{label}</a></li>
      <li><a href="{base}#woche">Ablauf</a></li>
      <li><a href="{base}#preise">Preise</a></li>
      <li><a href="{base}#fragen">Fragen</a></li>
    </ul>
    <a class="btn" href="{base}#start"><span class="long">{cta}</span><span class="short">Konfigurieren</span></a>
  </div>
</header>
"""


def slider(keys):
    chips = "\n".join(
        f'<button type="button" aria-pressed="{"true" if i == 0 else "false"}">{escape(next(b["name"] for b in BRANCHEN if b["mock"] == k))}</button>'
        for i, k in enumerate(keys))
    arts = "\n".join(mock(k, i == 0, lazy=i > 0) for i, k in enumerate(keys))
    first = MOCKS[keys[0]]["label"]
    return f"""
<div class="slider" id="slider">
  <button type="button" class="arrow prev" aria-label="Vorheriges Beispiel">{ARR_L}</button>
  <button type="button" class="arrow next" aria-label="Nächstes Beispiel">{ARR_R}</button>
  <div class="stage">
    <div class="chrome"><i></i><i></i><i></i></div>
    <div class="viewport" role="img" aria-label="{first}">
      <div class="site" aria-hidden="true">
{arts}
      </div>
    </div>
  </div>
  <div class="slide-nav"><div class="chips auto" role="group" aria-label="Beispiel-Branche wählen">
{chips}
  </div></div>
</div>
"""


def single_preview(key):
    return f"""
<div class="stage">
  <div class="chrome"><i></i><i></i><i></i></div>
  <div class="viewport" role="img" aria-label="{MOCKS[key]['label']}">
    <div class="site" aria-hidden="true">
{mock(key, True)}
    </div>
  </div>
</div>
"""


def week():
    return """
<section class="sec tint" id="woche">
  <div class="wrap">
    <div class="head rv">
      <h2>Montag konfigurieren.<br><strong>Freitag Entwurf.</strong></h2>
      <p class="lead">Du brauchst nur ein paar Minuten. Den Rest der Woche arbeiten wir.</p>
    </div>
    <ol class="week rv">
      <li class="du"><div class="day"><b>Mo</b><span class="who">Du</span></div><h3>Konfigurator</h3><p>Seiten und Funktionen zusammenklicken, in wenigen Minuten. Logo, Texte und Fotos schickst du uns einfach per E-Mail.</p></li>
      <li class="wir"><div class="day"><b>Di</b><span class="who">Wir</span></div><h3>Struktur</h3><p>Wir planen den Aufbau deiner Seiten, damit Besucher schnell finden, was sie suchen.</p></li>
      <li class="wir"><div class="day"><b>Mi</b><span class="who">Wir</span></div><h3>Design</h3><p>Farben, Schriften und Bilder, die zu deinem Betrieb passen.</p></li>
      <li class="wir"><div class="day"><b>Do</b><span class="who">Wir</span></div><h3>Bauen &amp; testen</h3><p>Wir bauen die Seite und prüfen sie auf Handy, Tablet und Rechner.</p></li>
      <li class="du"><div class="day"><b>Fr</b><span class="who">Du</span></div><h3>Entwurf ansehen</h3><p>Du bekommst einen Link zum Entwurf deiner Startseite. Kostenlos und unverbindlich.</p></li>
    </ol>
    <div class="after rv"><b>Danach</b><p>Gefällt dir der Entwurf, bestellst du deine Homepage zum Preis aus dem Konfigurator. Wir bauen die übrigen Seiten, du markierst Änderungswünsche direkt auf der Seite. Zwei Korrekturrunden sind dabei, dann geht deine Homepage online.</p></div>
  </div>
</section>
"""


def pricing():
    inkl = ["Startseite, individuell gestaltet", f"Bis zu 3 Rechtsseiten {tip('rechtsseiten')}", "Für Handy und Computer optimiert",
            "Entwurf kostenlos in 5 Werktagen", "2 Korrekturrunden vor dem Livegang", f"Hosting mit SSL {tip('hosting')}"]
    once = [(f"Weitere Seite {tip('inhaltsseite')}", eur(SEITE)), ("Kontaktformular", eur(99)),
            (f"Blog mit eigenem Login {tip('blog')}", eur(149)), ("Preisliste oder Speisekarte zum Selbstpflegen", eur(149)),
            ("Anfrageformular mit Foto-Upload", eur(149)), (f"Terminbuchung oder Anfahrtskarte {tip('einbindung')}", "je " + eur(49)),
            ("Bildergalerie<small>bis zu 20 Fotos</small>", eur(49)),
            ("Google-Bewertungen<small>ausgewählte echte Bewertungen mit Link zu deinem Google-Profil</small>", eur(99)),
            (f"Texte schreiben wir für dich {tip('texte')}<small>passend zu deiner Branche, mit KI erstellt</small>", eur(TEXT_PRO_SEITE) + " pro Seite"),
            (f"Lizenzfreie Bilder für dich {tip('bilder')}<small>falls du keine eigenen Fotos hast</small>", eur(BILD_PRO_SEITE) + " pro Seite")]
    monthly = [(f"Neue Domain oder Umzug zu uns {tip('domain')}", eur(4.99)), ("Eigene Domain behalten", eur(0)),
               (f"Monitoring &amp; Ausfallmanagement {tip('monitoring')}", eur(4.99)), (f"Wartung {tip('wartung')}", eur(14.99))]
    li_inkl = "".join(f"<li>{CK}<span>{x}</span></li>" for x in inkl)
    li_once = "".join(f"<li><span>{n}</span><b>{p}</b></li>" for n, p in once)
    li_month = "".join(f"<li><span>{n}</span><b>{p}</b></li>" for n, p in monthly)
    bsp_once = GRUNDPREIS + 2 * SEITE + 99
    bsp_month = HOSTING + 4.99
    return f"""
<section class="sec tint" id="preise" style="padding-top:0">
  <div class="wrap">
    <div class="head rv"><h2>Du zahlst nur, <strong>was du brauchst.</strong></h2><p class="lead">Ein fester Einstiegspreis. Alles andere klickst du im Konfigurator dazu und siehst sofort, was es kostet.</p></div>
    <div class="pricing rv">
      <div class="base-card">
        <span class="flag">Grundpaket</span>
        <h3>Deine Homepage</h3>
        <div class="price"><span class="amt">{eur(GRUNDPREIS)}</span><span class="unit">einmalig</span></div>
        <p class="plus">+ {eur(HOSTING)} im Monat für Hosting {tip('hosting')}</p>
        <ul class="feat">{li_inkl}</ul>
        <a class="btn" href="#start">Homepage konfigurieren <span class="arr">→</span></a>
      </div>
      <div class="extras">
        <div class="xbox"><h3>Einmalig dazu</h3><ul class="xlist">{li_once}</ul></div>
        <div class="xbox"><h3>Monatlich dazu</h3><ul class="xlist">{li_month}</ul>
          <div class="sorglos"><div><b>Sorglos-Paket</b><span>Monitoring und Wartung zusammen, du sparst 1,99 € im Monat</span></div><b class="p">{eur(17.99)}</b></div>
        </div>
      </div>
    </div>
    <div class="example rv">
      <p class="ex-title">Beispiel Friseursalon</p>
      <p><span>Startseite + 2 weitere Seiten + Kontaktformular</span><b>{eur(bsp_once)} einmalig</b></p>
      <p><span>Hosting + neue Domain</span><b>{eur(bsp_month)} im Monat</b></p>
    </div>
    <p class="fine">Alle Preise zzgl. MwSt. Keine Einrichtungsgebühr. Hosting und monatliche Optionen haben eine Mindestlaufzeit von 12 Monaten, danach sind sie monatlich kündbar. Nach der Bezahlung gehört die Homepage dir.</p>
  </div>
</section>
"""


def vergleich():
    def col(cls, titel, punkte, flag=""):
        li = "".join(f'<li class="{k}">{t}</li>' for k, t in punkte)
        return f'<div class="vs-col {cls}">{flag}<h3>{titel}</h3><ul>{li}</ul></div>'
    return f"""
<section class="sec" id="vergleich">
  <div class="wrap">
    <div class="head rv">
      <h2>Kein Baukasten. <strong>Keine Agentur.</strong></h2>
      <p class="lead">Beim Baukasten machst du alles selbst. Bei der Agentur zahlst du für Termine und Abstimmungen. Bei uns lässt du deine Homepage erstellen: Du stellst in fünf Minuten zusammen, was du brauchst, und wir bauen sie.</p>
    </div>
    <div class="vs rv">
      {col("", "Homepage-Baukasten", [("no", "Du baust alles selbst"), ("no", "Viele Abende, bis alles passt"), ("no", "Design aus Vorlagen"), ("no", "Technik und Updates behältst du selbst im Blick")])}
      {col("", "Klassische Agentur", [("ok", "Profis bauen für dich"), ("no", "Mehrere Termine und Abstimmungen"), ("no", "Oft mehrere tausend Euro"), ("no", "Wochen bis zum ersten Entwurf")])}
      {col("us", "Du klickst, wir bauen", [("ok", "Wir bauen deine Homepage für dich"), ("ok", "5 Minuten im Konfigurator, keine Termine"), ("ok", f"Ab {eur(GRUNDPREIS)} einmalig, Preis sofort sichtbar"), ("ok", "Kostenloser Entwurf in 5 Werktagen")], f'<span class="vs-flag">{NAME}</span>')}
    </div>
  </div>
</section>
"""


def howto(branche_fertig):
    """So funktioniert der Konfigurator: drei Schritte, auf Branchenseiten ist Schritt 1 schon erledigt."""
    s1 = "Branche gewählt" if branche_fertig else "Branche wählen"
    return f"""
      <ol class="howto">
        <li{' class="done"' if branche_fertig else ' class="now"'}><b>{CK if branche_fertig else "1"}</b><span>{s1}</span></li>
        <li{' class="now"' if branche_fertig else ''}><b>2</b><span>In 7 kurzen Schritten zusammenklicken, der Preis läuft mit</span></li>
        <li><b>3</b><span>Kostenlosen Entwurf in 5 Werktagen bekommen</span></li>
      </ol>"""


def promises():
    return f"""
      <ul class="promise">
        <li>{CK}Entwurf deiner Startseite kostenlos und unverbindlich</li>
        <li>{CK}Keine Zahlungsdaten nötig</li>
        <li>{CK}Du siehst deinen Preis sofort</li>
      </ul>"""


def choice(kind, name, pid, items, cls="opts stack"):
    """Auswahl-Karten. items: (Wert, Titel, Erklärung, Daten-Attribute, Zusatz-HTML im Titel)"""
    out = []
    for i, (val, title, small, data, extra) in enumerate(items):
        sm = f"<small>{small}</small>" if small else ""
        out.append(f'<label><input type="{kind}" name="{name}" id="{pid}-{i}" value="{escape(val)}"{data}><span class="o">{title}{extra}{sm}</span></label>')
    return f'<div class="{cls}">' + "".join(out) + "</div>"


def konfigurator(b):
    seiten = choice("checkbox", "seiten", "se",
                    [(s, s, None, f' data-once="{SEITE}"', f'<em class="pr">+ {eur(SEITE)}</em>') for s in b["seiten"]],
                    "opts multi cards")
    fn_items = []
    for key, name, price, art, desc in FUNKTIONEN:
        pop = '<em class="pop">Beliebt</em>' if key in b["empfohlen"] else ""
        art_tip = f" {tip('einbindung')}" if art == "Einbindung" else (f" {tip('blog')}" if key == "blog" else "")
        fn_items.append((name, f"{name}{art_tip}", desc, f' data-once="{price}"', f'<em class="pr">+ {eur(price)}{pop}</em>'))
    # Beliebte Funktionen zuerst
    fn_items.sort(key=lambda it: 0 if 'class="pop"' in it[4] else 1)  # stabil: Reihenfolge sonst wie FUNKTIONEN
    funktionen = choice("checkbox", "funktionen", "fn", fn_items, "opts multi cards wide")
    domain = choice("radio", "domain_option", "do",
                    [(v, t + (f" {tip('dns')}" if v == "Domain behalten" else f" {tip('umzug')}" if v == "Domain-Umzug" else ""), s,
                      f' data-monthly="{m}"', f'<em class="pr">{"+ " + eur(m) + " / Monat" if m else "0 €"}</em>') for v, t, s, m in DOMAIN_OPT])
    service = choice("radio", "service", "sv",
                     [(v, t + (f" {tip('monitoring')}" if v == "Monitoring" else f" {tip('wartung')}" if v == "Wartung" else ""), s,
                       f' data-monthly="{m}"', ('<em class="pop">Empfohlen</em>' if v == "Sorglos-Paket" else "") + f'<em class="pr">{"+ " + eur(m) + " / Monat" if m else "kein Aufpreis"}</em>') for v, t, s, m in SERVICE_OPT])
    texte = choice("radio", "texte", "tx", [
        ("Texte liefere ich", "Ich liefere die Texte", None, "", '<em class="pr">0 €</em>'),
        ("Texte schreibt ihr", f"Schreibt ihr die Texte für mich {tip('texte')}", "Passend zu deiner Branche, mit Unterstützung von KI erstellt. Du prüfst sie vor dem Onlinegang.", f' data-text="{TEXT_PRO_SEITE}"', f'<em class="pr">{eur(TEXT_PRO_SEITE)} pro Seite</em>')])
    fotos = choice("radio", "fotos", "fo", [
        ("Eigene Fotos", "Ich habe eigene Fotos", None, "", '<em class="pr">0 €</em>'),
        ("Lizenzfreie Bilder", f"Sucht ihr Bilder für mich aus {tip('bilder')}", "Passende lizenzfreie Fotos aus Bilddatenbanken, für jede Seite.", f' data-text="{BILD_PRO_SEITE}"', f'<em class="pr">{eur(BILD_PRO_SEITE)} pro Seite</em>')])
    stil = ('<div class="opts styles">'
            '<label><input type="radio" name="stil" id="st-0" value="Klar &amp; sachlich"><span class="o"><span class="sw"><i style="background:#eef0f3"></i><i style="background:#1c1f26"></i><i style="background:#3a6df0"></i></span>Klar &amp; sachlich<small>Viel Luft, ruhige Farben</small></span></label>'
            '<label><input type="radio" name="stil" id="st-1" value="Warm &amp; persönlich"><span class="o"><span class="sw"><i style="background:#f5e9e3"></i><i style="background:#d99f95"></i><i style="background:#3a1f2b"></i></span>Warm &amp; persönlich<small>Weich und einladend</small></span></label>'
            '<label><input type="radio" name="stil" id="st-2" value="Kräftig &amp; auffällig"><span class="o"><span class="sw"><i style="background:#0f172a"></i><i style="background:#facc15"></i><i style="background:#f1f5f9"></i></span>Kräftig &amp; auffällig<small>Starke Farben, Charakter</small></span></label>'
            '</div>')
    fn_hint = "Alles optional. Wähle einfach aus, was dir hilft." if b["mock"] is None else "Alles optional. Was in deiner Branche beliebt ist, haben wir markiert."
    ex_label, ex_ph, ex_req = b["extra"]
    req = " required" if ex_req else ""
    star = " *" if ex_req else ""
    segs = "<i></i>" * 7
    return f"""
    <form class="wizard rv" id="wizard" name="konfigurator" method="POST" data-netlify="true" netlify-honeypot="bot-field" novalidate
          data-base="{GRUNDPREIS}" data-hosting="{HOSTING}" data-seite="{SEITE}">
      <input type="hidden" name="form-name" value="konfigurator">
      <input type="hidden" name="branche" value="{escape(b['name'])}">
      <input type="hidden" name="preis_einmalig" value="">
      <input type="hidden" name="preis_monatlich" value="">
      <input type="hidden" name="zusammenfassung" value="">
      <p hidden><label>Nicht ausfüllen <input name="bot-field" id="bot-field"></label></p>
      <span class="anchor" id="start"></span>
      <p class="wiz-branche">Branche: <b>{escape(b['name'])}</b> · <a href="{ROOT}index.html#start">ändern</a></p>
      <div class="segs">{segs}</div>
      <p class="qno" id="qno">Schritt 1 von 7</p>

      <fieldset class="pane on" data-step="1">
        <legend>Welche Seiten brauchst du?</legend>
        <p class="hint">Startseite und Rechtsseiten sind immer dabei. Jede weitere Seite kostet {eur(SEITE)} einmalig.</p>
        <div class="incl-chips"><span>{CK}Startseite <em>inklusive</em></span><span>{CK}Rechtsseiten {tip('rechtsseiten')} <em>inklusive</em></span></div>
        {seiten}
        <div class="stepper"><span>Noch weitere Seiten? {tip('inhaltsseite')}</span>
          <div class="st-ctrl"><button type="button" data-delta="-1" aria-label="Eine Seite weniger">−</button><input type="number" name="weitere_seiten" id="weitere" value="0" min="0" max="20" readonly aria-label="Anzahl weiterer Seiten"><button type="button" data-delta="1" aria-label="Eine Seite mehr">+</button></div>
        </div>
      </fieldset>

      <fieldset class="pane" data-step="2">
        <legend>Welche Funktionen brauchst du?</legend>
        <p class="hint">{fn_hint}</p>
        {funktionen}
      </fieldset>

      <fieldset class="pane" data-step="3">
        <legend>Wie sieht es mit deiner Domain aus? {tip('domain')}</legend>
        <p class="hint">Die Domain ist die Adresse deiner Homepage, zum Beispiel friseur-mueller.de.</p>
        {domain}
        <label class="field" style="margin-top:16px"><span>Deine Domain oder dein Wunschname (falls schon bekannt)</span><input id="domain" name="domain" placeholder="z. B. mein-betrieb.de"></label>
      </fieldset>

      <fieldset class="pane" data-step="4" data-auto>
        <legend>Wie viel sollen wir uns kümmern?</legend>
        <p class="hint">Hosting {tip('hosting')} für {eur(HOSTING)} im Monat ist immer dabei.</p>
        {service}
      </fieldset>

      <fieldset class="pane" data-step="5">
        <legend>Texte, Fotos und Stil</legend>
        <p class="subq" style="margin-top:6px">Wer schreibt die Texte?</p>
        {texte}
        <p class="subq">Hast du Fotos?</p>
        {fotos}
        <p class="subq">Welche Richtung gefällt dir?</p>
        {stil}
      </fieldset>

      <fieldset class="pane" data-step="6">
        <legend>Erzähl uns kurz von dir.</legend>
        <p class="hint">Stichpunkte reichen völlig.</p>
        <div class="two">
          <label class="field"><span>Name deines Betriebs *</span><input id="firma" name="firma" required autocomplete="organization"></label>
          <label class="field"><span>Ort *</span><input id="ort" name="ort" required autocomplete="address-level2"></label>
        </div>
        <label class="field"><span>{ex_label}{star}</span><input id="extra" name="extra" placeholder="{ex_ph}"{req}></label>
        <label class="field"><span>Was bietest du an, und für wen? *</span><textarea id="beschreibung" name="beschreibung" rows="3" required placeholder="Zwei Sätze reichen."></textarea></label>
      </fieldset>

      <fieldset class="pane" data-step="7">
        <legend>Wohin schicken wir deinen Entwurf?</legend>
        <p class="hint">Du bekommst ihn in 5 Werktagen, kostenlos und unverbindlich.</p>
        <label class="field"><span>Dein Name *</span><input id="name" name="name" required autocomplete="name"></label>
        <label class="field"><span>E-Mail *</span><input id="email" name="email" type="email" required autocomplete="email"></label>
        <label class="check"><input type="checkbox" id="datenschutz" name="datenschutz" required><span>Ich habe die <a href="{ROOT}datenschutz.html" target="_blank">Datenschutzerklärung</a> gelesen und bin einverstanden, dass meine Angaben zur Bearbeitung meiner Anfrage genutzt werden. *</span></label>
      </fieldset>

      <div class="pane done-msg" data-step="8">
        <span class="done-ic" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg></span>
        <p class="q">Danke, deine Konfiguration ist da.</p>
        <p>Wir schauen uns deine Angaben an und melden uns per E-Mail, falls wir noch etwas brauchen, zum Beispiel dein Logo oder Fotos. Deinen Entwurf bekommst du innerhalb von 5 Werktagen.</p>
        <p class="mail-hint">Du bekommst gleich eine Bestätigung mit deiner Zusammenstellung per E-Mail. Falls sie in 10 Minuten nicht da ist, schau bitte in deinem Spam-Ordner nach.</p>
      </div>

      <div class="sum" id="sum" aria-live="polite">
        <div class="sum-top">
          <div><small>Einmalig</small><b id="sumOnce">{eur(GRUNDPREIS)}</b></div>
          <div><small>Monatlich</small><b id="sumMonth">{eur(HOSTING)}</b></div>
          <button type="button" class="sum-toggle" id="sumToggle" aria-expanded="false" aria-controls="sumList">Details</button>
        </div>
        <ul class="sum-list" id="sumList" hidden></ul>
        <p class="sum-note">zzgl. MwSt. · Entwurf kostenlos und unverbindlich</p>
      </div>

      <p class="err" id="err" role="alert"></p>
      <div class="wiz-nav" id="wizNav">
        <button type="button" class="btn ghost" id="back" hidden>← Zurück</button>
        <button type="button" class="btn" id="next" style="margin-left:auto">Weiter <span class="arr">→</span></button>
      </div>
    </form>"""


FAQ = [
    ("Was kostet meine Homepage?", f"Das Grundpaket kostet {eur(GRUNDPREIS)} einmalig. Darin sind deine Startseite und bis zu 3 Rechtsseiten enthalten. Jede weitere Seite kostet {eur(SEITE)}, Funktionen wie ein Kontaktformular gibt es ab {eur(49)}. Dazu kommt das Hosting für {eur(HOSTING)} im Monat. Im Konfigurator siehst du deinen Preis sofort."),
    ("Ist das ein Homepage-Baukasten?", "Nein. Bei einem Baukasten baust du deine Homepage selbst. Bei uns stellst du im Konfigurator nur zusammen, was du brauchst. Gestaltung, Aufbau, Technik und Onlinegang übernehmen wir."),
    ("Warum muss ich Hosting buchen?", "Ohne Hosting ist deine Homepage im Internet nicht erreichbar. Wir kümmern uns um schnelle Server und eine verschlüsselte Verbindung, damit du dich um nichts kümmern musst."),
    ("Brauche ich einen Beratungstermin?", "Nein. Du stellst dir deine Homepage im Konfigurator zusammen, siehst dir den Entwurf über einen Link an und markierst Änderungen direkt auf der Seite. Fragen beantworten wir per E-Mail."),
    ("Was ist, wenn mir der Entwurf nicht gefällt?", "Der Entwurf ist kostenlos und unverbindlich. Solange du nichts bestellt hast, zahlst du nichts. Nach der Bestellung sind zwei Korrekturrunden inklusive."),
    ("Was ist mit meiner Domain?", f"Du hast drei Möglichkeiten: Wir registrieren eine neue Domain auf deinen Namen ({eur(4.99)} im Monat). Du behältst deine Domain bei deinem Anbieter, dann schicken wir dir die Einstellungen zum Eintragen, das kostet nichts. Oder deine Domain zieht zu uns um ({eur(4.99)} im Monat)."),
    ("Gehört mir die Homepage?", "Ja. Nach der Bezahlung gehört die Homepage dir. Kündigst du das Hosting, bekommst du alle Dateien. Funktionen, die auf unserer Technik laufen, wie der Blog-Login, enden mit dem Hosting."),
    ("Wer liefert Texte und Bilder?", f"Texte und Bilder lieferst du. Keine Zeit? Dann schreiben wir die Texte für {eur(TEXT_PRO_SEITE)} pro Seite, passend zu deiner Branche und mit Unterstützung von KI. Hast du keine eigenen Fotos, suchen wir für {eur(BILD_PRO_SEITE)} pro Seite passende lizenzfreie Bilder aus. Vor dem Onlinegang prüfst du alle Inhalte und gibst sie frei."),
    ("Wer kümmert sich um Impressum und Datenschutz?", "Die Seiten legen wir an, die Texte lieferst du, zum Beispiel aus einem Rechtstext-Generator. Eine Rechtsberatung leisten wir nicht. Wir sagen dir aber genau, welche Technik deine Seite nutzt, damit du sie dort eintragen kannst."),
    ("Kann ich später etwas ändern lassen?", "Mit dem Wartungspaket setzen wir bis zu 2 Text- und 2 Bildänderungen im Monat für dich um. Ohne Wartungspaket bekommst du für jeden Wunsch vorher einen Festpreis."),
    ("Bekomme ich auch E-Mail-Postfächer?", "E-Mail-Postfächer sind nicht enthalten. Wir empfehlen dir einen passenden Anbieter und schicken dir eine Anleitung, wie du ihn mit deiner Domain verbindest."),
    ("Wie lange läuft der Vertrag?", "Hosting und monatliche Optionen laufen mindestens 12 Monate. Danach kannst du sie jeden Monat kündigen."),
]


def faq():
    items = "\n".join(f"      <details><summary>{q}</summary><p>{a}</p></details>" for q, a in FAQ)
    return f"""
<section class="sec tint" id="fragen">
  <div class="wrap faq-grid">
    <div class="head rv" style="align-content:start"><h2>Gut <strong>zu wissen.</strong></h2></div>
    <div class="faq rv">
{items}
    </div>
  </div>
</section>
"""


def footer(root, home, legal=False):
    branchen = "".join(f'<li><a href="{root}{b["slug"]}.html">{escape(b["name"])}</a></li>' for b in BRANCHEN)
    base = f"{root}index.html" if legal else ""
    seite = "#branchen" if home else f"{root}index.html#branchen"
    return f"""
<footer class="final">
  <div class="cta-panel">
    <div class="blobs" aria-hidden="true"><i></i><i></i><i></i></div>
    <div class="cta-inner">
      <div class="closing">
        <h2>Fünf Minuten. <strong>Dann sind wir dran.</strong></h2>
        <a class="btn inv" href="{base}#start">Homepage konfigurieren <span class="arr">→</span></a>
      </div>
      <div class="foot">
        <div>{brand(root, "f")}<p class="claim">{CLAIM}</p><p>Wir bauen Homepages für Handwerk, Dienstleister und kleine Betriebe. Einmal bezahlen, Hosting {eur(HOSTING)} im Monat.</p></div>
        <div><h3>Seite</h3><ul><li><a href="{seite}">Beispiele</a></li><li><a href="{base}#woche">Ablauf</a></li><li><a href="{base}#preise">Preise</a></li><li><a href="{base}#fragen">Fragen</a></li></ul></div>
        <div><h3>Branchen</h3><ul>{branchen}</ul></div>
        <div><h3>Rechtliches</h3><ul><li><a href="{root}impressum.html">Impressum</a></li><li><a href="{root}datenschutz.html">Datenschutz</a></li><li><a href="{root}agb.html">AGB</a></li><li><a href="{root}kontakt.html">Kontakt</a></li><li><a href="mailto:{MAIL}">{MAIL}</a></li></ul></div>
      </div>
      <p class="copy">© 2026 {NAME}</p>
    </div>
  </div>
</footer>
<script src="{root}assets/app.js?v={VERSION}"></script>
</body>
</html>
"""


# ---------------------------------------------------------------- Startseite
def page_home():
    tiles = []
    for b in BRANCHEN:
        if b["mock"] is None:
            tiles.append(f'<a class="tile other" href="{b["slug"]}.html"><span><b class="big">Deine Branche ist <strong>nicht dabei?</strong></b></span><em>Zum Konfigurator →</em></a>')
        else:
            tiles.append(f'<a class="tile" href="{b["slug"]}.html"><img {srcset(b["foto"], [360, 600], "(max-width: 700px) 66vw, 270px")} alt="Foto zur Branche {escape(b["name"])}" loading="lazy" decoding="async"><span>{escape(b["name"])} <em>Ansehen →</em></span></a>')
    picks = []
    for b in BRANCHEN:
        pic = '<span class="pic"></span>' if b["mock"] is None else f'<img src="{img(b["foto"], 160)}" alt="Foto zur Branche {escape(b["name"])}" loading="lazy" decoding="async">'
        picks.append(f'<li><a href="{b["slug"]}.html#start">{pic}{escape(b["name"])}<span class="arr">→</span></a></li>')
    ld = ('\n<script type="application/ld+json">{"@context":"https://schema.org","@type":"ProfessionalService",'
          f'"name":"{NAME}","slogan":"{CLAIM}","url":"{DOMAIN}/","email":"{MAIL}","areaServed":"DE",'
          '"description":"Homepages für Handwerk, Dienstleister und kleine Betriebe: online konfiguriert, von uns gebaut."}</script>')
    html = head(f"Homepage erstellen lassen ab {eur(GRUNDPREIS)} · {NAME}",
                f"Homepage erstellen lassen statt selbst basteln: in 5 Minuten konfiguriert, von uns gebaut. Ab {eur(GRUNDPREIS)} einmalig, Entwurf kostenlos.",
                "", SLIDER_ORDER, "", ld)
    html += header("", True)
    html += f"""
<main>
<section class="hero">
  <div class="blobs" aria-hidden="true"><i></i><i></i><i></i></div>
  <div class="wrap">
    <div class="hero-top">
      <div>
        <span class="eyebrow"><b>Neu</b> Entwurf deiner Startseite kostenlos</span>
        <h1>Deine Homepage.<span class="h1b"><strong>Fertig gebaut.</strong></span></h1>
        <p class="for">Für <span class="switch" id="word">{MOCKS[SLIDER_ORDER[0]]['word']}</span></p>
      </div>
      <div class="hero-side">
        <p class="lead">Stell dir deine Firmen-Homepage in wenigen Minuten zusammen. Wir bauen sie für dich und bringen sie online. Kein Baukasten, kein Basteln, keine Termine.</p>
        <div>
          <div class="ctas">
            <a class="btn" href="#start">Homepage konfigurieren <span class="arr">→</span></a>
            <a class="btn ghost" href="#preise">Preise ansehen</a>
          </div>
          <p class="from"><b>Ab {eur(GRUNDPREIS)}</b> einmalig</p>
          <p class="from-note">Dazu Hosting {tip('hosting')} für {eur(HOSTING)} im Monat · Entwurf kostenlos in 5 Werktagen</p>
        </div>
      </div>
    </div>
{slider(SLIDER_ORDER)}
  </div>
</section>

<section class="sec" id="branchen">
  <div class="wrap">
    <div class="head rv">
      <h2>Für Betriebe <strong>wie deinen.</strong></h2>
      <p class="lead">Jede Branche braucht etwas anderes. Deshalb gibt es für jede Branche eine eigene Seite und einen passenden Konfigurator.</p>
    </div>
    <div class="tiles rv">
      {''.join(tiles)}
    </div>
    <p class="swipe-hint">Wische für weitere Branchen →</p>
  </div>
</section>

<section class="photo-band" id="ohne">
  <img {srcset('1603464021578-f327592a89de', [900, 1800], "100vw")} alt="Laptop auf einem Schreibtisch" loading="lazy" decoding="async">
  <div class="inner">
    <p class="intro">Was du dir bei uns sparst:</p>
    <ul class="strike" id="strike">
      <li style="--i:0"><span>Mehrere tausend Euro für die Agentur</span></li>
      <li style="--i:1"><span>Wochenlanges Warten auf den Entwurf</span></li>
      <li style="--i:2"><span>Technik, Hosting und Updates selbst regeln</span></li>
      <li style="--i:3"><span>Termine für jede Abstimmung</span></li>
      <li style="--i:4"><span>Abende im Baukasten, bis endlich alles passt</span></li>
      <li style="--i:5"><span>Pakete mit Dingen, die du nie brauchst</span></li>
    </ul>
    <div class="instead">
      <p class="big">Stattdessen: <strong>Du klickst, wir bauen.</strong></p>
      <p>Im Konfigurator stellst du zusammen, was dein Betrieb braucht, und siehst sofort den Preis. Den Rest machen wir. Du startest mit {eur(GRUNDPREIS)}, Hosting kostet {eur(HOSTING)} im Monat, alles andere ist freiwillig.</p>
    </div>
  </div>
</section>
{vergleich()}{week()}{pricing()}
<section class="sec">
  <div class="wrap">
    <div class="head rv"><h2>Das ist <strong>immer dabei.</strong></h2></div>
    <ul class="incl rv">
      <li><span class="ic">{icon('palette')}</span><h3>Eigenes Design</h3><p>Farben, Schriften und Bildsprache passend zu deinem Betrieb.</p></li>
      <li><span class="ic">{icon('phone')}</span><h3>Zuerst fürs Handy</h3><p>Die meisten Besucher kommen mobil. Dafür gestalten wir zuerst.</p></li>
      <li><span class="ic">{icon('bolt')}</span><h3>Schnell geladen</h3><p>Schlanker Code statt Baukasten. Gut für Besucher und für Google.</p></li>
      <li><span class="ic">{icon('gift')}</span><h3>Entwurf kostenlos</h3><p>Den Entwurf deiner Startseite bekommst du kostenlos und unverbindlich.</p></li>
      <li><span class="ic">{icon('doc')}</span><h3>Rechtsseiten angelegt</h3><p>Bis zu 3 Rechtsseiten sind dabei. Die Texte lieferst du, wir sagen dir, welche Technik deine Seite nutzt.</p></li>
      <li><span class="ic">{icon('search')}</span><h3>Bei Google auffindbar</h3><p>Saubere Struktur, Meta-Daten und Sitemap von Anfang an.</p></li>
      <li><span class="ic">{icon('pencil')}</span><h3>2 Korrekturrunden</h3><p>Vor dem Livegang setzen wir deine Änderungswünsche in zwei Runden um.</p></li>
      <li><span class="ic">{icon('lock')}</span><h3>Sichere Verbindung</h3><p>Dein Hosting kommt mit SSL-Verschlüsselung, erkennbar am Schloss im Browser.</p></li>
    </ul>
  </div>
</section>

<section class="sec start" id="konfigurator">
  <div class="blobs" aria-hidden="true"><i></i><i></i><i></i></div>
  <div class="wrap start-grid">
    <div class="intro rv">
      <span class="anchor" id="start"></span>
      <h2>Konfiguriere <strong>deine Homepage.</strong></h2>{howto(False)}
    </div>
    <div class="picker rv">
      <p class="step-k">Los geht&#39;s</p>
      <p class="q">Was für einen Betrieb hast du?</p>
      <p>Tipp auf deine Branche, dann geht es direkt mit dem Konfigurator weiter.</p>
      <ul class="picks">
        {''.join(picks)}
      </ul>
    </div>
    <div class="intro-more">{promises()}
      <div class="start-photo">
        <img {srcset(SONST_FOTO, [600, 1000], "(max-width: 1000px) 92vw, 520px")} alt="Frau stellt am Laptop ihre Homepage zusammen" loading="lazy" decoding="async">
        <span class="badge"><i>5</i>Minuten, wann es dir passt</span>
      </div>
    </div>
  </div>
</section>
{faq()}
</main>
"""
    html += footer("", True)
    return html


# ---------------------------------------------------------------- Branchenseite
def page_branche(b):
    root = ""
    sonst = b["mock"] is None
    h1t = escape(b["h1"]) if b["h1"] else ""
    keys = SLIDER_ORDER if sonst else [b["mock"]]
    wer = "jede Branche" if sonst else h1t
    title = f"Homepage für {escape(b['kw'])} erstellen lassen · {NAME}"
    desc = f"Homepage für {escape(b['kw'])} erstellen lassen: online konfiguriert, von uns gebaut. Ab {eur(GRUNDPREIS)} einmalig, Entwurf kostenlos in 5 Werktagen."
    h1 = "Deine Branche ist <strong>nicht dabei?</strong>" if sonst else f"Homepage für <strong>{h1t}.</strong>"
    feats = "".join(f'<li><span class="ic">{icon(i)}</span><h3>{t}</h3><p>{p}</p></li>' for i, t, p in b["feats"])
    others = "".join(f'<a href="{o["slug"]}.html">{escape(o["name"])}</a>' for o in BRANCHEN if o is not b)
    if sonst:
        preview = f"""<p class="cap-h">Ein paar Beispiele, wie unterschiedlich unsere Homepages aussehen:</p>{slider(keys)}"""
        feats_h = "Das bekommt <strong>jeder Betrieb.</strong>"
        start_h = "Konfiguriere <strong>deine Homepage.</strong>"
    else:
        preview = f"""<p class="cap-h">So könnte deine Homepage aussehen:</p>{single_preview(b['mock'])}"""
        feats_h = f"Das braucht eine Homepage für <strong>{h1t}.</strong>"
        start_h = f"Deine Homepage für <strong>{h1t}.</strong>"

    html = head(title, desc, root, keys, f"{b['slug']}.html")
    html += header(root, False)
    html += f"""
<main>
<section class="hero sub-hero">
  <div class="blobs" aria-hidden="true"><i></i><i></i><i></i></div>
  <div class="wrap">
    <div class="hero-top">
      <div>
        <nav class="crumbs" aria-label="Brotkrumen"><a href="{root}index.html">Startseite</a><span>/</span><a href="{root}index.html#branchen">Branchen</a><span>/</span><span>{escape(b['name'])}</span></nav>
        <h1>{h1}</h1>
        <p class="lead">{b['lead']}</p>
        <div class="ctas">
          <a class="btn" href="#start">Homepage konfigurieren <span class="arr">→</span></a>
          <a class="btn ghost" href="#preise">Preise ansehen</a>
        </div>
        <p class="from"><b>ab {eur(GRUNDPREIS)}</b> einmalig · Entwurf in 5 Werktagen</p>
        <p class="from-note">Dazu Hosting {tip('hosting')} für {eur(HOSTING)} im Monat</p>
      </div>
      <div class="sub-photo"><img {srcset(b['foto'], [600, 1000], "(max-width: 1000px) 92vw, 520px")} alt="Foto zur Branche {escape(b['name'])}" fetchpriority="high" decoding="async"></div>
    </div>
    <div class="preview">{preview}</div>
  </div>
</section>

<section class="sec" id="leistungen">
  <div class="wrap">
    <div class="head rv"><h2>{feats_h}</h2><p class="lead">{b['text']} {"Bei uns lässt du sie erstellen, ohne selbst zu basteln." if sonst else f"Bei uns kannst du deine Homepage für {escape(b['kw'])} erstellen lassen, ohne selbst zu basteln."}</p></div>
    <ul class="feats rv">{feats}</ul>
  </div>
</section>
{week()}{pricing()}
<section class="sec start" id="konfigurator">
  <div class="blobs" aria-hidden="true"><i></i><i></i><i></i></div>
  <div class="wrap start-grid">
    <div class="intro rv">
      <h2>{start_h}</h2>{howto(not sonst)}
    </div>
{konfigurator(b)}
    <div class="intro-more">{promises()}
      <div class="start-photo">
        <img {srcset(SONST_FOTO, [600, 1000], "(max-width: 1000px) 92vw, 520px")} alt="Frau stellt am Laptop ihre Homepage zusammen" loading="lazy" decoding="async">
        <span class="badge"><i>5</i>Minuten, wann es dir passt</span>
      </div>
    </div>
  </div>
</section>
{faq()}
<section class="sec tint" style="padding-top:0">
  <div class="wrap">
    <div class="head rv" style="margin-bottom:0"><h2>Andere <strong>Branchen.</strong></h2></div>
    <div class="others rv">{others}</div>
  </div>
</section>
</main>
"""
    html += footer(root, False)
    return html


# ---------------------------------------------------------------- Rechtsseiten
A = ANBIETER
ANSCHRIFT = f"{A['name']}<br>{A['strasse']}<br>{A['ort']}<br>{A['land']}"

IMPRESSUM = f"""
<h2>Angaben gemäß § 5 DDG</h2>
<p>{ANSCHRIFT}</p>
<h2>Kontakt</h2>
<p>E-Mail: <a href="mailto:{MAIL}">{MAIL}</a><br>Kontaktformular: <a href="kontakt.html">homepagekonfigurator.de/kontakt</a></p>
<h2>Umsatzsteuer-ID</h2>
<p>Umsatzsteuer-Identifikationsnummer gemäß § 27a Umsatzsteuergesetz: {A['ust']}</p>
<h2>Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV</h2>
<p>{A['name']}, {A['strasse']}, {A['ort']}</p>
<h2>Verbraucherstreitbeilegung</h2>
<p>Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p>
<h2>Haftung für Inhalte</h2>
<p>Als Diensteanbieter sind wir für eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich. Wir sind jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen zu überwachen oder nach Umständen zu forschen, die auf eine rechtswidrige Tätigkeit hinweisen. Verpflichtungen zur Entfernung oder Sperrung der Nutzung von Informationen nach den allgemeinen Gesetzen bleiben hiervon unberührt.</p>
<h2>Haftung für Links</h2>
<p>Unser Angebot enthält Links zu externen Webseiten Dritter, auf deren Inhalte wir keinen Einfluss haben. Für die Inhalte der verlinkten Seiten ist stets der jeweilige Anbieter oder Betreiber verantwortlich. Bei Bekanntwerden von Rechtsverletzungen entfernen wir derartige Links umgehend.</p>
<h2>Urheberrecht und Bildnachweis</h2>
<p>Die durch den Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten unterliegen dem deutschen Urheberrecht. Die Fotos stammen von Unsplash (unsplash.com) und werden gemäß der Unsplash-Lizenz verwendet. Die Beispiel-Homepages zeigen erfundene Betriebe.</p>
"""

DATENSCHUTZ = f"""
<h2>1. Verantwortlicher</h2>
<p>Verantwortlich im Sinne der Datenschutz-Grundverordnung (DSGVO) ist:</p>
<p>{ANSCHRIFT}<br>E-Mail: <a href="mailto:{MAIL}">{MAIL}</a></p>
<h2>2. Deine Rechte</h2>
<p>Du hast gegenüber uns folgende Rechte hinsichtlich deiner personenbezogenen Daten:</p>
<ul>
  <li>Auskunft (Art. 15 DSGVO)</li>
  <li>Berichtigung (Art. 16 DSGVO)</li>
  <li>Löschung (Art. 17 DSGVO)</li>
  <li>Einschränkung der Verarbeitung (Art. 18 DSGVO)</li>
  <li>Datenübertragbarkeit (Art. 20 DSGVO)</li>
  <li>Widerspruch gegen die Verarbeitung (Art. 21 DSGVO)</li>
</ul>
<p>Außerdem hast du das Recht, dich bei einer Datenschutz-Aufsichtsbehörde zu beschweren (Art. 77 DSGVO). Zuständig ist: Der Hessische Beauftragte für Datenschutz und Informationsfreiheit, Postfach 3163, 65021 Wiesbaden, <a href="https://datenschutz.hessen.de" rel="noopener">datenschutz.hessen.de</a>.</p>
<h2>3. Hosting und Server-Logfiles</h2>
<p>Diese Homepage wird bei Netlify, Inc. (San Francisco, USA) gehostet. Beim Aufruf der Seiten speichert Netlify automatisch Informationen, die dein Browser übermittelt: Browsertyp und -version, Betriebssystem, Referrer-URL, Hostname des zugreifenden Rechners, Uhrzeit der Anfrage und IP-Adresse. Diese Daten werden nicht mit anderen Datenquellen zusammengeführt.</p>
<p>Rechtsgrundlage ist Art. 6 Abs. 1 lit. f DSGVO. Unser berechtigtes Interesse liegt in einem sicheren und stabilen Betrieb der Homepage. Netlify ist unter dem EU-US Data Privacy Framework zertifiziert. Weitere Informationen: <a href="https://www.netlify.com/privacy/" rel="noopener">netlify.com/privacy</a>.</p>
<h2>4. Homepage-Konfigurator</h2>
<p>Wenn du unseren Homepage-Konfigurator nutzt, verarbeiten wir deine Angaben, um deine Anfrage zu bearbeiten, dir einen Entwurf zu erstellen und ein Angebot zu machen. Das sind: deine Branche, die gewählten Seiten, Funktionen und monatlichen Leistungen, deine Angaben zur Domain, deine Wünsche zu Texten, Fotos und Stil, Name und Ort deines Betriebs, deine Beschreibung, dein Name, deine E-Mail-Adresse sowie der daraus berechnete Preis.</p>
<p>Rechtsgrundlage ist Art. 6 Abs. 1 lit. b DSGVO (Durchführung vorvertraglicher Maßnahmen auf deine Anfrage). Die Angaben werden über den Formulardienst von Netlify übertragen und gespeichert; wir erhalten sie zusätzlich per E-Mail. Zur Bestätigung schicken wir dir eine E-Mail mit deiner Zusammenstellung an die angegebene Adresse; der Versand läuft über unseren E-Mail-Anbieter INWX (Berlin). Zur Prüfung deiner Angaben auf Vollständigkeit und zur Erstellung von Entwürfen und Texten setzen wir den KI-Dienst Claude der Anthropic, PBC (San Francisco, USA) ein; dabei werden deine Angaben aus dem Konfigurator übermittelt. Anthropic nutzt diese Daten nach seinen Bedingungen für Geschäftskunden nicht zum Training seiner KI-Modelle. Die Übermittlung in die USA erfolgt auf Grundlage der EU-Standardvertragsklauseln. Die Verarbeitung erfolgt auf unserem eigenen Server bei der Hetzner Online GmbH (Deutschland). Über neue Anfragen informieren wir uns intern per Telegram (Telegram FZ-LLC, Dubai) mit einer kurzen Zusammenfassung. Kommt kein Auftrag zustande, löschen wir deine Angaben spätestens sechs Monate nach Eingang. Kommt ein Auftrag zustande, speichern wir sie für die Dauer der Zusammenarbeit und im Rahmen der gesetzlichen Aufbewahrungspflichten.</p>
<h2>5. Kontakt per E-Mail und Kontaktformular</h2>
<p>Wenn du uns per E-Mail oder über unser Kontaktformular schreibst, verarbeiten wir deine E-Mail-Adresse, deinen Namen und den Inhalt deiner Nachricht, um dein Anliegen zu bearbeiten. Rechtsgrundlage ist Art. 6 Abs. 1 lit. b DSGVO, sofern es um einen Auftrag geht, sonst Art. 6 Abs. 1 lit. f DSGVO. Nachrichten aus dem Kontaktformular werden über den Formulardienst von Netlify übertragen und gespeichert. Die Daten werden gelöscht, sobald dein Anliegen erledigt ist und keine Aufbewahrungspflichten entgegenstehen.</p>
<h2>6. Keine Cookies, kein Tracking</h2>
<p>Diese Homepage setzt keine Cookies und verwendet keine Analyse- oder Marketing-Dienste. Schriftarten und Bilder sind lokal auf unserem Server gespeichert. Beim Aufruf der Seite werden dadurch keine Daten an Dritte wie Google oder Unsplash übertragen.</p>
<h2>7. Speicherdauer</h2>
<p>Wir speichern personenbezogene Daten nur so lange, wie es für den jeweiligen Zweck nötig ist oder gesetzliche Aufbewahrungsfristen es verlangen.</p>
<h2>8. Datensicherheit</h2>
<p>Diese Homepage nutzt eine SSL/TLS-Verschlüsselung. Eine verschlüsselte Verbindung erkennst du an „https://“ in der Adresszeile deines Browsers.</p>
<p class="stand">Stand: Oktober 2026</p>
"""

# ENTWURF – vor Veröffentlichung anwaltlich prüfen lassen.
AGB = f"""
<h2>§ 1 Geltungsbereich</h2>
<p>(1) Diese Allgemeinen Geschäftsbedingungen gelten für alle Verträge zwischen {A['name']}, {A['strasse']}, {A['ort']} (im Folgenden „wir“), und unseren Kundinnen und Kunden (im Folgenden „du“) über die Erstellung von Homepages und die damit verbundenen Leistungen wie Hosting, Domain, Monitoring und Wartung unter der Marke {NAME}.</p>
<p>(2) Unser Angebot richtet sich ausschließlich an Unternehmer im Sinne von § 14 BGB, also an Personen, die bei Vertragsschluss in Ausübung ihrer gewerblichen oder selbstständigen beruflichen Tätigkeit handeln. Verträge mit Verbrauchern schließen wir nicht.</p>
<p>(3) Abweichende Bedingungen gelten nur, wenn wir ihnen ausdrücklich in Textform zugestimmt haben.</p>

<h2>§ 2 Konfigurator, Entwurf und Vertragsschluss</h2>
<p>(1) Die Angaben im Homepage-Konfigurator auf unserer Homepage sind eine unverbindliche Anfrage. Der dort angezeigte Preis ist eine unverbindliche Berechnung auf Grundlage deiner Auswahl.</p>
<p>(2) Auf Grundlage deiner Anfrage erstellen wir einen Entwurf deiner Startseite. Der Entwurf ist kostenlos und unverbindlich. Wir können Anfragen ohne Angabe von Gründen ablehnen.</p>
<p>(3) Der Vertrag kommt zustande, wenn du unser Angebot in Textform annimmst (zum Beispiel per E-Mail oder durch Bestätigung auf unserer Angebotsseite) und wir die Bestellung in Textform bestätigen.</p>

<h2>§ 3 Leistungen bei der Erstellung</h2>
<p>(1) Der Umfang unserer Leistungen ergibt sich aus deinem Angebot. Das Grundpaket umfasst die Gestaltung und technische Umsetzung einer Startseite sowie das Anlegen von bis zu drei Rechtsseiten (zum Beispiel Impressum, Datenschutzerklärung und AGB).</p>
<p>(2) Weitere Inhaltsseiten, Funktionen (zum Beispiel Kontaktformular oder Blog) und Einbindungen von Diensten Dritter (zum Beispiel Terminbuchung oder Karte) sind nur enthalten, wenn sie im Angebot aufgeführt sind. Für Einbindungen brauchst du in der Regel ein eigenes Konto beim jeweiligen Anbieter; dessen Kosten und Bedingungen sind nicht Teil unseres Vertrags.</p>
<p>(3) Nach der Bestellung erstellen wir die übrigen Seiten. Zwei Korrekturrunden sind enthalten. Danach schalten wir die Homepage nach deiner Freigabe online.</p>
<p>(4) Wenn du den Texte-Service gebucht hast, erstellen wir die Werbetexte deiner Seiten auf Grundlage deiner Angaben und mit Unterstützung von KI. Wenn du den Bilder-Service gebucht hast, suchen wir lizenzfreie Bilder aus Bilddatenbanken aus. Rechtstexte schreiben wir nicht.</p>
<p>(5) Du prüfst alle Inhalte vor der Freigabe. Für sachliche Angaben wie Leistungen, Preise, Öffnungszeiten, Qualifikationen und Zertifikate bist du verantwortlich, auch wenn wir die Texte formuliert haben.</p>

<h2>§ 4 Hosting und Domain</h2>
<p>(1) Für den Betrieb der Homepage ist unser Hosting erforderlich. Es umfasst die Bereitstellung der Homepage bei einem spezialisierten Hosting-Dienstleister und eine verschlüsselte Verbindung (SSL). Eine ständige Verfügbarkeit können wir nicht garantieren; kurze Unterbrechungen, etwa für Wartungsarbeiten des Dienstleisters, sind möglich.</p>
<p>(2) Auf Wunsch registrieren wir eine neue Domain auf deinen Namen als Inhaber oder übernehmen deine bestehende Domain (Umzug). Bei Vertragsende erhältst du die Daten, die du für einen Umzug zu einem anderen Anbieter brauchst.</p>
<p>(3) Behältst du deine Domain bei deinem Anbieter, schicken wir dir die nötigen Einstellungen. Das Eintragen und die Kosten bei deinem Anbieter liegen bei dir. E-Mail-Postfächer sind nicht Teil unserer Leistungen.</p>

<h2>§ 5 Monitoring und Wartung</h2>
<p>(1) Mit dem Monitoring prüfen wir automatisch etwa einmal pro Stunde, ob deine Homepage erreichbar ist. Bei einem Ausfall beginnen wir innerhalb von 48 Stunden an Werktagen mit der Behebung. Ohne Monitoring meldest du uns Ausfälle selbst.</p>
<p>(2) Mit der Wartung halten wir deine Homepage technisch aktuell und setzen pro Kalendermonat bis zu zwei Textänderungen und zwei Bildänderungen um. Eine Textänderung ist das Ändern oder Ergänzen eines Textabschnitts; eine Bildänderung ist das Austauschen oder Ergänzen eines Bildes, das du lieferst. Nicht genutzte Änderungen verfallen am Monatsende.</p>
<p>(3) Änderungen außerhalb der Wartung und größere Wünsche bieten wir dir vorab zu einem Festpreis an.</p>

<h2>§ 6 Deine Mitwirkung</h2>
<p>(1) Du stellst uns die nötigen Inhalte wie Logo, Texte, Fotos und Angaben zu deinem Betrieb rechtzeitig zur Verfügung, soweit du nicht den Texte- oder Bilder-Service gebucht hast.</p>
<p>(2) Du versicherst, dass du die Rechte an den Inhalten besitzt, die du uns überlässt, und dass ihre Nutzung keine Rechte Dritter verletzt. Wirst du deswegen von Dritten in Anspruch genommen, stellst du uns davon frei.</p>
<p>(3) Für die Inhalte deiner Homepage, insbesondere für Impressum, Datenschutzerklärung und AGB, bist du verantwortlich. Die Texte dieser Rechtsseiten lieferst du. Wir teilen dir mit, welche technischen Dienste deine Homepage nutzt. Eine Rechtsberatung leisten wir nicht.</p>

<h2>§ 7 Preise und Zahlung</h2>
<p>(1) Es gelten die Preise aus deinem Angebot. Alle Preise verstehen sich zuzüglich der gesetzlichen Umsatzsteuer.</p>
<p>(2) Eine Anzahlung verlangen wir nicht. Den einmaligen Preis für die Erstellung stellen wir nach dem Onlinegang der Homepage in Rechnung. Monatliche Entgelte für Hosting, Domain, Monitoring und Wartung sind jeweils monatlich im Voraus fällig, erstmals ab dem Onlinegang.</p>
<p>(3) Du erhältst eine Rechnung per E-Mail. Rechnungen sind innerhalb von 14 Tagen ohne Abzug per Überweisung zu zahlen.</p>
<p>(4) Bist du mit einer Zahlung länger als 30 Tage im Rückstand, dürfen wir die Homepage nach vorheriger Ankündigung offline nehmen, bis die Zahlung eingegangen ist.</p>

<h2>§ 8 Laufzeit und Kündigung</h2>
<p>(1) Hosting und gebuchte monatliche Leistungen haben eine Mindestlaufzeit von 12 Monaten ab Onlinegang. Danach verlängern sie sich jeweils um einen Monat und können mit einer Frist von einem Monat zum Monatsende gekündigt werden.</p>
<p>(2) Monitoring und Wartung können nach Ablauf der Mindestlaufzeit auch einzeln gekündigt werden. Mit dem Ende des Hostings enden alle monatlichen Leistungen.</p>
<p>(3) Die Kündigung bedarf der Textform. Das Recht zur außerordentlichen Kündigung aus wichtigem Grund bleibt unberührt.</p>
<p>(4) Mit dem Ende des Hostings nehmen wir die Homepage offline. Auf Wunsch übergeben wir dir die Dateien deiner Homepage. Funktionen, die auf unserer Technik laufen (zum Beispiel der Blog-Login), enden mit dem Hosting.</p>

<h2>§ 9 Nutzungsrechte</h2>
<p>(1) Nach vollständiger Zahlung des einmaligen Preises erhältst du ein einfaches, zeitlich unbeschränktes Recht, die Homepage und ihre Dateien für deinen Betrieb zu nutzen und zu bearbeiten.</p>
<p>(2) Für lizenzierte Fotos und Schriften gelten zusätzlich die Bedingungen der jeweiligen Lizenz.</p>
<p>(3) Wir dürfen deine Homepage als Referenz auf unserer Homepage nennen und zeigen. Du kannst dem jederzeit in Textform widersprechen.</p>

<h2>§ 10 Haftung</h2>
<p>(1) Wir haften unbeschränkt bei Vorsatz und grober Fahrlässigkeit sowie bei der Verletzung von Leben, Körper oder Gesundheit.</p>
<p>(2) Bei leichter Fahrlässigkeit haften wir nur bei der Verletzung wesentlicher Vertragspflichten, also solcher Pflichten, deren Erfüllung die Durchführung des Vertrags erst ermöglicht und auf deren Einhaltung du regelmäßig vertrauen darfst. In diesem Fall ist die Haftung auf den vertragstypischen, vorhersehbaren Schaden begrenzt.</p>
<p>(3) Für Datenverluste haften wir nur in dem Umfang, der bei regelmäßiger Datensicherung entstanden wäre.</p>

<h2>§ 11 Schlussbestimmungen</h2>
<p>(1) Es gilt das Recht der Bundesrepublik Deutschland unter Ausschluss des UN-Kaufrechts.</p>
<p>(2) Ist der Kunde Kaufmann, juristische Person des öffentlichen Rechts oder öffentlich-rechtliches Sondervermögen, ist Gerichtsstand für alle Streitigkeiten unser Geschäftssitz.</p>
<p>(3) Sollte eine Bestimmung dieser AGB unwirksam sein, bleibt die Wirksamkeit der übrigen Bestimmungen unberührt.</p>
<p class="stand">Stand: Oktober 2026</p>
"""


LEGAL = [
    ("impressum", "Impressum", IMPRESSUM),
    ("datenschutz", "Datenschutzerklärung", DATENSCHUTZ),
    ("agb", "Allgemeine Geschäftsbedingungen", AGB),
]


def page_legal(slug, title, body):
    html = head(f"{title} · {NAME}", f"{title} von {NAME}.", "", (), f"{slug}.html")
    html += header("", False, legal=True)
    html += f"""
<main>
<section class="hero legal">
  <div class="blobs" aria-hidden="true"><i></i><i></i><i></i></div>
  <div class="wrap">
    <h1>{title}</h1>
    <div class="legal-text">{body}</div>
  </div>
</section>
</main>
"""
    html += footer("", False, legal=True)
    return html


# ---------------------------------------------------------------- Lokale Schriften und Fotos
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def ensure_images():
    """Lädt alle verwendeten Unsplash-Fotos einmalig herunter (WebP) und speichert sie in assets/img."""
    d = OUT / "assets" / "img"
    d.mkdir(parents=True, exist_ok=True)
    neu = 0
    for pid, w in sorted(IMAGES):
        f = d / f"{pid}-{w}.webp"
        if not f.exists():
            f.write_bytes(fetch(f"https://images.unsplash.com/photo-{pid}?w={w}&q={BILDQUALITAET}&fm=webp&fit=crop"))
            neu += 1
    # Nicht mehr verwendete Fotos entfernen, damit nichts Unnötiges veröffentlicht wird
    genutzt = {f"{pid}-{w}.webp" for pid, w in IMAGES}
    for f in d.glob("*.webp"):
        if f.name not in genutzt:
            f.unlink()
    return neu


def ensure_fonts():
    """Lädt alle Schriften (nur lateinischer Zeichensatz) und schreibt assets/fonts.css."""
    fams = [BASE_FONT] + [f for fs in MOCK_FONTS.values() for f in fs]
    fams = list(dict.fromkeys(fams))
    css_file = OUT / "assets" / "fonts.css"
    marker = "/* " + "|".join(fams) + " */"
    if css_file.exists() and css_file.read_text(encoding="utf-8").startswith(marker):
        return 0
    d = OUT / "assets" / "fonts"
    d.mkdir(parents=True, exist_ok=True)
    url = "https://fonts.googleapis.com/css2?" + "&".join("family=" + f for f in fams) + "&display=swap"
    css = fetch(url).decode("utf-8")
    blocks = re.findall(r"/\* ([\w-]+) \*/\s*(@font-face\s*{[^}]*})", css)
    out, n = [marker], 0
    for subset, block in blocks:
        if subset != "latin":
            continue
        src = re.search(r"url\((https://fonts\.gstatic\.com/[^)]+\.woff2)\)", block).group(1)
        name = re.sub(r"[^\w.-]", "_", src.split("/s/")[1])
        f = d / name
        if not f.exists():
            f.write_bytes(fetch(src))
            n += 1
        out.append(block.replace(src, f"fonts/{name}"))
    css_file.write_text("\n".join(out) + "\n", encoding="utf-8")
    return n


def page_kontakt():
    html = head(f"Kontakt · {NAME}", f"Schreib uns: Fragen zu deiner Homepage beantworten wir per E-Mail. {NAME}.", "", (), "kontakt.html")
    html += header("", False, legal=True)
    html += f"""
<main>
<section class="hero legal">
  <div class="blobs" aria-hidden="true"><i></i><i></i><i></i></div>
  <div class="wrap">
    <h1>Schreib <strong>uns.</strong></h1>
    <p class="lead" style="margin:22px 0 34px">Du hast eine Frage, bevor du konfigurierst? Schreib uns, wir antworten in der Regel am selben oder nächsten Werktag. Oder direkt per E-Mail an <a href="mailto:{MAIL}">{MAIL}</a>.</p>
    <form class="contact" name="kontakt" method="POST" action="danke.html" data-netlify="true" netlify-honeypot="bot-field">
      <input type="hidden" name="form-name" value="kontakt">
      <p hidden><label>Nicht ausfüllen: <input name="bot-field"></label></p>
      <label class="field"><span>Dein Name *</span><input name="name" required autocomplete="name"></label>
      <label class="field"><span>E-Mail *</span><input type="email" name="email" required autocomplete="email"></label>
      <label class="field"><span>Nachricht *</span><textarea name="nachricht" rows="6" required></textarea></label>
      <label class="check"><input type="checkbox" name="datenschutz" value="ja" required><span>Ich habe die <a href="datenschutz.html">Datenschutzerklärung</a> gelesen und bin einverstanden, dass meine Angaben zur Beantwortung meiner Anfrage genutzt werden. *</span></label>
      <button class="btn" type="submit">Nachricht senden <span class="arr">→</span></button>
    </form>
  </div>
</section>
</main>
"""
    html += footer("", False, legal=True)
    return html


def page_danke():
    html = head(f"Danke · {NAME}", "Deine Nachricht ist angekommen.", "", (), "danke.html").replace(
        '<meta name="viewport"', '<meta name="robots" content="noindex">\n<meta name="viewport"')
    html += header("", False, legal=True)
    html += f"""
<main>
<section class="hero legal">
  <div class="blobs" aria-hidden="true"><i></i><i></i><i></i></div>
  <div class="wrap">
    <h1>Danke, <strong>ist angekommen.</strong></h1>
    <p class="lead" style="margin:22px 0 30px">Wir melden uns per E-Mail bei dir, in der Regel am selben oder nächsten Werktag.</p>
    <div class="ctas"><a class="btn" href="index.html#start">Homepage konfigurieren <span class="arr">→</span></a><a class="btn ghost" href="index.html">Zur Startseite</a></div>
  </div>
</section>
</main>
"""
    html += footer("", False, legal=True)
    return html


def page_404():
    # Wird von Netlify unter jeder Adresse ausgeliefert, deshalb absolute Pfade ("/")
    html = head(f"Seite nicht gefunden · {NAME}", "Diese Seite gibt es nicht.", "/", (), "404.html").replace(
        '<meta name="viewport"', '<meta name="robots" content="noindex">\n<meta name="viewport"')
    html += header("/", False, legal=True)
    html += f"""
<main>
<section class="hero legal">
  <div class="blobs" aria-hidden="true"><i></i><i></i><i></i></div>
  <div class="wrap">
    <h1>Hier ist <strong>nichts.</strong></h1>
    <p class="lead" style="margin:22px 0 30px">Diese Seite gibt es nicht oder nicht mehr. Vielleicht hilft dir einer dieser Wege weiter.</p>
    <div class="ctas"><a class="btn" href="/index.html">Zur Startseite <span class="arr">→</span></a><a class="btn ghost" href="/index.html#branchen">Branchen ansehen</a></div>
  </div>
</section>
</main>
"""
    html += footer("/", False, legal=True)
    return html


FAVICON = logo_svg("x").replace('<svg class="logo-ic"', '<svg xmlns="http://www.w3.org/2000/svg"').replace(
    ' aria-hidden="true"', "").replace('class="lw"', 'fill="#fff"').replace('class="lb"', 'fill="#e3e1ee"').replace('class="lr" ', 'stroke="#fff" stroke-width="2.4" ')


def write(path, html, root):
    path.write_text(html.replace(ROOT, root), encoding="utf-8")


def main():
    alt = OUT / "branchen"  # frühere Adressen der Branchenseiten
    if alt.exists():
        shutil.rmtree(alt)
    pages = [(OUT / "index.html", page_home(), "")]
    pages += [(OUT / f"{b['slug']}.html", page_branche(b), "") for b in BRANCHEN]
    pages += [(OUT / f"{slug}.html", page_legal(slug, t, body), "") for slug, t, body in LEGAL]
    pages.append((OUT / "kontakt.html", page_kontakt(), ""))
    for path, html, root in pages:
        write(path, html, root)
    write(OUT / "404.html", page_404(), "/")
    write(OUT / "danke.html", page_danke(), "")
    (OUT / "assets" / "favicon.svg").write_text(FAVICON + "\n", encoding="utf-8")

    # Suchmaschinen: Sitemap und robots.txt
    heute = time.strftime("%Y-%m-%d")
    urls = "".join(f"  <url><loc>{DOMAIN}/{'' if p.name == 'index.html' else p.name}</loc><lastmod>{heute}</lastmod></url>\n" for p, _, _ in pages)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n', encoding="utf-8")
    # Netlify: Bilder, Schriften, CSS und JS lange zwischenspeichern (CSS/JS haben ?v=…, neue Fassungen haben also eine neue Adresse)
    jahr = "  Cache-Control: public, max-age=31536000, immutable\n"
    (OUT / "_headers").write_text("".join(f"{pfad}\n{jahr}" for pfad in ("/assets/img/*", "/assets/fonts/*", "/assets/*.css", "/assets/*.js")), encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n", encoding="utf-8")

    # Netlify: Zweitdomain und www per 301 auf die Hauptdomain
    host = DOMAIN.split("//")[1]
    (OUT / "_redirects").write_text(
        "".join(f"https://{d}/* {DOMAIN}/:splat 301!\n" for d in ("homepage-konfigurator.de", "www.homepage-konfigurator.de", f"www.{host}")),
        encoding="utf-8")

    print(f"Fertig: {len(pages) + 2} Seiten in {OUT}")
    print(f"Fotos neu geladen: {ensure_images()} · Schriftdateien neu geladen: {ensure_fonts()}")


if __name__ == "__main__":
    main()
