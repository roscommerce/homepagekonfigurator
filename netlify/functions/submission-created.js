// Netlify ruft diese Funktion bei jeder gültigen Formular-Einsendung auf (Ereignis "submission-created").
// Für das Formular "konfigurator" bekommt der Kunde eine Bestätigungsmail mit seiner Zusammenstellung.
//
// Zugangsdaten stehen NICHT im Code, sondern in Netlify unter "Environment variables":
//   SMTP_HOST  Postausgangsserver des Postfachs (steht bei INWX beim Postfach)
//   SMTP_PORT  465 (SSL) oder 587 (STARTTLS)
//   SMTP_USER  info@homepagekonfigurator.de
//   SMTP_PASS  Passwort des Postfachs
//   APP_HOOK_SECRET  gemeinsamer Schlüssel mit dem Automatik-Server (app.homepagekonfigurator.de)
const nodemailer = require('nodemailer');

const ABSENDER = 'HomepageKonfigurator <info@homepagekonfigurator.de>';
const SEITE = 'https://homepagekonfigurator.de';

const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const einzeilig = s => String(s ?? '').replace(/[\r\n]+/g, ' ').trim().slice(0, 120);

function mailInhalt(d) {
  const vorname = einzeilig(d.name).split(' ')[0] || '';
  const firma = einzeilig(d.firma);
  const zeilen = String(d.zusammenfassung || '').split('\n').map(z => z.trim()).filter(Boolean).slice(0, 40)
    .map(z => { const i = z.lastIndexOf(': '); return i > 0 ? [z.slice(0, i), z.slice(i + 2)] : [z, '']; });

  const text = [
    `Hallo ${vorname},`,
    '',
    `danke für deine Konfiguration${firma ? ' für ' + firma : ''}. Sie ist bei uns angekommen.`,
    '',
    'Deine Auswahl:',
    ...zeilen.map(([n, p]) => `- ${n}${p ? ': ' + p : ''}`),
    '',
    `Einmalig: ${d.preis_einmalig || '–'}`,
    `Monatlich: ${d.preis_monatlich || '–'}`,
    'Alle Preise zzgl. MwSt.',
    '',
    'So geht es weiter:',
    '1. Wir schauen uns deine Angaben an und melden uns, falls noch etwas fehlt.',
    '2. Deinen kostenlosen Entwurf der Startseite bekommst du innerhalb von 5 Werktagen.',
    '3. Erst wenn er dir gefällt, bestellst du. Bis dahin ist alles unverbindlich.',
    '',
    'Logo oder Fotos kannst du uns schon jetzt schicken: Antworte einfach auf diese Mail und häng sie an.',
    '',
    'Viele Grüße',
    'Sven von HomepageKonfigurator',
    '',
    '--',
    'HomepageKonfigurator · Sven Rosenthal · In der Landwehr 21 · 34376 Immenhausen',
    `${SEITE} · info@homepagekonfigurator.de`,
  ].join('\n');

  const reihe = ([n, p]) => `<tr><td style="padding:8px 0;border-bottom:1px solid #ece9e4;color:#3d4256">${esc(n)}</td><td style="padding:8px 0;border-bottom:1px solid #ece9e4;text-align:right;white-space:nowrap;font-weight:600;color:#141829">${esc(p)}</td></tr>`;
  const html = `<!doctype html><html lang="de"><body style="margin:0;background:#f4f2ee;font-family:Helvetica,Arial,sans-serif;color:#141829">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f4f2ee;padding:24px 12px"><tr><td align="center">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;background:#ffffff;border-radius:18px;overflow:hidden">
<tr><td style="padding:26px 30px;border-bottom:1px solid #ece9e4;font-size:20px;font-weight:700;letter-spacing:-.3px">Homepage<span style="color:#7b4fe8">Konfigurator</span></td></tr>
<tr><td style="padding:30px">
<h1 style="margin:0 0 14px;font-size:24px;line-height:1.25;font-weight:600">Danke, deine Konfiguration ist da.</h1>
<p style="margin:0 0 22px;font-size:16px;line-height:1.6;color:#3d4256">Hallo ${esc(vorname)},<br>danke für deine Konfiguration${firma ? ' für <b>' + esc(firma) + '</b>' : ''}. Sie ist bei uns angekommen.</p>
<p style="margin:0 0 8px;font-size:14px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:#6b7086">Deine Auswahl</p>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="font-size:15px">${zeilen.map(reihe).join('')}</table>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-top:16px;background:#eceeff;border-radius:12px"><tr>
<td style="padding:16px 18px"><div style="font-size:13px;color:#565c72">Einmalig</div><div style="font-size:22px;font-weight:700">${esc(d.preis_einmalig || '–')}</div></td>
<td style="padding:16px 18px"><div style="font-size:13px;color:#565c72">Monatlich</div><div style="font-size:22px;font-weight:700">${esc(d.preis_monatlich || '–')}</div></td></tr></table>
<p style="margin:8px 0 26px;font-size:13px;color:#6b7086">Alle Preise zzgl. MwSt.</p>
<p style="margin:0 0 10px;font-size:14px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:#6b7086">So geht es weiter</p>
<ol style="margin:0 0 22px;padding-left:20px;font-size:16px;line-height:1.6;color:#3d4256">
<li>Wir schauen uns deine Angaben an und melden uns, falls noch etwas fehlt.</li>
<li>Deinen <b>kostenlosen Entwurf</b> der Startseite bekommst du innerhalb von 5 Werktagen.</li>
<li>Erst wenn er dir gefällt, bestellst du. Bis dahin ist alles unverbindlich.</li></ol>
<p style="margin:0 0 22px;font-size:16px;line-height:1.6;color:#3d4256">Logo oder Fotos kannst du uns schon jetzt schicken: Antworte einfach auf diese Mail und häng sie an.</p>
<p style="margin:0;font-size:16px;line-height:1.6;color:#3d4256">Viele Grüße<br>Sven von HomepageKonfigurator</p>
</td></tr>
<tr><td style="padding:18px 30px;background:#12152b;color:#c9cbe0;font-size:12px;line-height:1.6">HomepageKonfigurator · Sven Rosenthal · In der Landwehr 21 · 34376 Immenhausen<br><a href="${SEITE}" style="color:#c9cbe0">homepagekonfigurator.de</a> · <a href="${SEITE}/impressum" style="color:#c9cbe0">Impressum</a> · <a href="${SEITE}/datenschutz" style="color:#c9cbe0">Datenschutz</a></td></tr>
</table></td></tr></table></body></html>`;

  return { text, html };
}

exports.mailInhalt = mailInhalt;

exports.handler = async (event) => {
  const payload = JSON.parse(event.body || '{}').payload || {};
  const d = payload.data || {};
  const formular = payload.form_name || d['form-name'];
  if (formular !== 'konfigurator') return { statusCode: 200, body: 'kein Konfigurator' };

  // Anfrage an den Automatik-Server weiterreichen (Prüfung, Telegram an Sven). Fehler hier blockieren die Mail nicht.
  const { APP_HOOK_URL = 'https://app.homepagekonfigurator.de/hook/anfrage', APP_HOOK_SECRET } = process.env;
  if (APP_HOOK_SECRET) {
    try {
      const r = await fetch(APP_HOOK_URL, {
        method: 'POST', headers: { 'content-type': 'application/json', 'x-hk-secret': APP_HOOK_SECRET },
        body: JSON.stringify({ id: payload.id, form_name: formular, data: d }), signal: AbortSignal.timeout(8000),
      });
      console.log('Weitergabe an Automatik:', r.status);
    } catch (e) {
      console.error('Weitergabe an Automatik fehlgeschlagen:', e.message);
    }
  }

  const an = einzeilig(d.email || payload.email);
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(an)) return { statusCode: 200, body: 'keine gültige E-Mail' };

  const { SMTP_HOST, SMTP_PORT = '465', SMTP_USER, SMTP_PASS } = process.env;
  if (!SMTP_HOST || !SMTP_USER || !SMTP_PASS) {
    console.log('Bestätigungsmail übersprungen: SMTP-Zugangsdaten fehlen in Netlify');
    return { statusCode: 200, body: 'SMTP nicht eingerichtet' };
  }

  const transport = nodemailer.createTransport({
    host: SMTP_HOST, port: +SMTP_PORT, secure: +SMTP_PORT === 465,
    auth: { user: SMTP_USER, pass: SMTP_PASS },
  });
  const { text, html } = mailInhalt(d);
  try {
    const info = await transport.sendMail({
      from: ABSENDER, to: an, replyTo: 'info@homepagekonfigurator.de',
      bcc: 'info@homepagekonfigurator.de',  // Kopie an uns: so sehen wir, was der Kunde bekommen hat
      subject: 'Deine Homepage-Konfiguration ist da',
      text, html,
    });
    console.log('Bestätigungsmail gesendet:', info.response, '| angenommen:', (info.accepted || []).length, '| abgelehnt:', (info.rejected || []).length);
  } catch (e) {
    // Fehler nur protokollieren: Die Anfrage selbst ist bei Netlify trotzdem gespeichert
    console.error('Bestätigungsmail fehlgeschlagen:', e.code || '', e.responseCode || '', e.message);
    return { statusCode: 200, body: 'Versand fehlgeschlagen' };
  }
  return { statusCode: 200, body: 'gesendet' };
};
