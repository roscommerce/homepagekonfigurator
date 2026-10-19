// HomepageKonfigurator – gemeinsames Skript für alle Seiten
document.documentElement.classList.add('js');

// Sprung zu #start beim Öffnen einer Seite absichern (Bilder darüber können die Position noch verschieben)
if (location.hash === '#start') {
  const jump = () => { const t = document.getElementById('start'); if (t) t.scrollIntoView({ behavior: 'instant', block: 'start' }); };
  addEventListener('DOMContentLoaded', jump);
  addEventListener('load', () => { if (scrollY < 50 || Math.abs(document.getElementById('start').getBoundingClientRect().top - parseFloat(getComputedStyle(document.getElementById('start')).scrollMarginTop)) > 40) jump(); });
}
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

// Lineal der Tischlerei beschriften
document.querySelectorAll('.ruler').forEach(r => {
  for (let x = 60, n = 10; x < 1200; x += 60, n += 10) {
    const s = document.createElement('span'); s.style.left = x + 'px'; s.textContent = n; r.appendChild(s);
  }
});

// Vorschauen auf die Rahmenbreite skalieren
document.querySelectorAll('.viewport').forEach(vp => {
  const site = vp.querySelector('.site');
  const fit = () => site.style.transform = `scale(${vp.clientWidth / 1200})`;
  new ResizeObserver(fit).observe(vp); fit();
});

// Slider mit Skizzen-Effekt (Startseite und "Sonstige Branche")
(() => {
  const slider = document.getElementById('slider');
  if (!slider) return;
  const mocks = [...slider.querySelectorAll('.m')], chips = [...slider.querySelectorAll('.chips button')], bar = slider.querySelector('.chips');
  const vp = slider.querySelector('.viewport'), word = document.getElementById('word');
  const n = mocks.length;
  let cur = 0, timer = null, drafting, auto = !reduce;
  // Bilder der übrigen Vorschauen erst bei Bedarf laden (schnellerer Seitenaufbau am Handy)
  const load = m => m.querySelectorAll('img[data-src]').forEach(i => { i.srcset = i.dataset.srcset; i.src = i.dataset.src; i.removeAttribute('data-src'); });
  addEventListener('load', () => setTimeout(() => mocks.forEach(load), 2500));
  const show = (k, dir = 1) => {
    k = (k + n) % n;
    load(mocks[k]);
    if (k === cur) return;
    mocks[cur].classList.remove('on', 'draft', 'in-r', 'in-l');
    const m = mocks[k]; cur = k;
    m.classList.add('on');
    if (!reduce) {
      m.classList.add(dir > 0 ? 'in-r' : 'in-l', 'draft');
      clearTimeout(drafting); drafting = setTimeout(() => m.classList.remove('draft', 'in-r', 'in-l'), 700);
    }
    chips.forEach((c, i) => c.setAttribute('aria-pressed', i === k));
    vp.setAttribute('aria-label', m.dataset.label);
    if (word && m.dataset.word) {
      word.textContent = m.dataset.word;
      word.classList.remove('swap'); void word.offsetWidth; word.classList.add('swap');
    }
  };
  const pause = () => { clearInterval(timer); bar.classList.remove('auto'); };
  const play = () => {
    if (!auto) return;
    pause(); void bar.offsetWidth; bar.classList.add('auto');
    timer = setInterval(() => { if (!document.hidden) show(cur + 1); }, 5000);
  };
  const manual = (k, dir) => { auto = false; pause(); show(k, dir); };
  chips.forEach((c, i) => c.addEventListener('click', () => manual(i, i >= cur ? 1 : -1)));
  slider.querySelector('.prev').addEventListener('click', () => manual(cur - 1, -1));
  slider.querySelector('.next').addEventListener('click', () => manual(cur + 1, 1));
  // Wischen auf dem Handy
  let x0 = null;
  vp.addEventListener('pointerdown', e => { x0 = e.clientX; });
  vp.addEventListener('pointerup', e => {
    if (x0 === null) return;
    const dx = e.clientX - x0; x0 = null;
    if (Math.abs(dx) > 40) manual(cur + (dx < 0 ? 1 : -1), dx < 0 ? 1 : -1);
  });
  vp.addEventListener('pointercancel', () => { x0 = null; });
  slider.addEventListener('mouseenter', pause);
  slider.addEventListener('mouseleave', play);
  bar.classList.remove('auto'); play();
})();

// Durchstreichen, sobald sichtbar
(() => {
  const s = document.getElementById('strike');
  if (!s) return;
  if (!('IntersectionObserver' in window)) { s.classList.add('run'); return; }
  new IntersectionObserver((e, o) => { if (e[0].isIntersecting) { s.classList.add('run'); o.disconnect(); } }, { threshold: .4 }).observe(s);
})();

// Sanftes Einblenden: nur für Elemente unterhalb des ersten Bildschirms
(() => {
  if (reduce || !('IntersectionObserver' in window)) return;
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.remove('pre'); io.unobserve(e.target); } }), { rootMargin: '0px 0px -8% 0px' });
  document.querySelectorAll('.rv').forEach(el => {
    if (el.getBoundingClientRect().top > innerHeight) { el.classList.add('pre'); io.observe(el); }
  });
})();

// Infobuttons: Erklärung beim Drüberfahren (Computer) oder Antippen (Handy)
(() => {
  const tips = document.querySelectorAll('.tip');
  if (!tips.length) return;
  const box = document.createElement('div');
  box.id = 'tipbox'; box.setAttribute('aria-live', 'polite');
  document.body.appendChild(box);
  let cur = null, shownAt = 0, touch = false;
  const show = t => {
    cur = t; shownAt = Date.now();
    box.textContent = t.dataset.tip; box.classList.add('on');
    tips.forEach(x => x.setAttribute('aria-expanded', x === t));
    const r = t.getBoundingClientRect(), bw = box.offsetWidth, bh = box.offsetHeight;
    const x = Math.max(12, Math.min(r.left + r.width / 2 - bw / 2, innerWidth - bw - 12));
    let y = r.top - bh - 10; if (y < 12) y = r.bottom + 10;
    box.style.left = x + 'px'; box.style.top = y + 'px';
  };
  const hide = () => { cur = null; box.classList.remove('on'); tips.forEach(x => x.setAttribute('aria-expanded', 'false')); };
  addEventListener('pointerdown', e => { touch = e.pointerType !== 'mouse'; }, true);
  tips.forEach(t => {
    t.setAttribute('aria-expanded', 'false');
    t.addEventListener('mouseenter', () => { if (!touch) show(t); });
    t.addEventListener('mouseleave', () => { if (!touch) hide(); });
    t.addEventListener('focus', () => show(t));
    t.addEventListener('blur', hide);
    // Klick darf weder die Auswahl im Konfigurator umschalten noch das Formular abschicken
    t.addEventListener('click', e => {
      e.preventDefault(); e.stopPropagation();
      if (cur === t && Date.now() - shownAt > 350) hide(); else show(t);
    });
  });
  document.addEventListener('click', e => { if (!e.target.closest('.tip')) hide(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') hide(); });
  addEventListener('scroll', hide, { passive: true });
})();

// Konfigurator: Preis live berechnen
(() => {
  const f = document.getElementById('wizard');
  if (!f || !f.dataset.base) return;
  const BASE = +f.dataset.base, HOST = +f.dataset.hosting, SEITE = +f.dataset.seite;
  const fmt = n => n.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + '\u00a0€';
  const wi = document.getElementById('weitere'), list = document.getElementById('sumList');
  const calc = () => {
    let once = BASE, month = HOST;
    const rows = [['Grundpaket: Startseite + Rechtsseiten', BASE, false], ['Hosting', HOST, true]];
    const seiten = [...f.querySelectorAll('input[name=seiten]:checked')];
    seiten.forEach(c => { once += +c.dataset.once; rows.push(['Seite „' + c.value + '“', +c.dataset.once, false]); });
    const w = +wi.value || 0;
    if (w) { once += w * SEITE; rows.push([w + (w === 1 ? ' weitere Seite' : ' weitere Seiten'), w * SEITE, false]); }
    f.querySelectorAll('input[name=funktionen]:checked').forEach(c => { once += +c.dataset.once; rows.push([c.value, +c.dataset.once, false]); });
    // Texte und Bilder: Preis je Seite (Startseite + gewählte + weitere Seiten)
    [['texte', 'Texte'], ['fotos', 'Bilder']].forEach(([nm, label]) => {
      const r = f.querySelector(`input[name=${nm}]:checked`);
      if (!r || !r.dataset.text) return;
      const n = 1 + seiten.length + w, v = n * +r.dataset.text;
      once += v; rows.push([label + ' für ' + n + (n === 1 ? ' Seite' : ' Seiten'), v, false]);
    });
    ['domain_option', 'service'].forEach(nm => {
      const r = f.querySelector(`input[name=${nm}]:checked`);
      if (r && +r.dataset.monthly) { month += +r.dataset.monthly; rows.push([r.value, +r.dataset.monthly, true]); }
    });
    document.getElementById('sumOnce').textContent = fmt(once);
    document.getElementById('sumMonth').textContent = fmt(month);
    list.replaceChildren(...rows.map(([n, v, m]) => {
      const li = document.createElement('li'), a = document.createElement('span'), b = document.createElement('b');
      a.textContent = n; b.textContent = fmt(v) + (m ? ' / Monat' : ''); li.append(a, b); return li;
    }));
    f.elements.preis_einmalig.value = fmt(once);
    f.elements.preis_monatlich.value = fmt(month);
    f.elements.zusammenfassung.value = rows.map(([n, v, m]) => `${n}: ${fmt(v)}${m ? ' / Monat' : ''}`).join('\n');
  };
  f.querySelectorAll('.st-ctrl button').forEach(b => b.addEventListener('click', () => {
    wi.value = Math.max(0, Math.min(20, (+wi.value || 0) + +b.dataset.delta)); calc();
  }));
  const tg = document.getElementById('sumToggle');
  tg.addEventListener('click', () => {
    const open = list.hidden; list.hidden = !open;
    tg.setAttribute('aria-expanded', open); tg.textContent = open ? 'Weniger' : 'Details';
  });
  f.addEventListener('change', calc);
  calc();
})();

// Konfigurator: Schritte
(() => {
  const f = document.getElementById('wizard');
  if (!f) return;
  const panes = [...f.querySelectorAll('.pane')], segs = [...f.querySelectorAll('.segs i')];
  const qno = document.getElementById('qno'), next = document.getElementById('next'), back = document.getElementById('back'), err = document.getElementById('err');
  const sum = document.getElementById('sum');
  const TOTAL = panes.length - 1; let step = 1;
  const render = () => {
    panes.forEach(p => p.classList.toggle('on', +p.dataset.step === step));
    segs.forEach((s, i) => s.classList.toggle('done', i < step));
    qno.textContent = step > TOTAL ? 'Geschafft' : `Schritt ${step} von ${TOTAL}`;
    back.hidden = step === 1 || step > TOTAL;
    next.innerHTML = step === TOTAL ? 'Konfiguration absenden' : 'Weiter <span class="arr">→</span>';
    document.getElementById('wizNav').hidden = step > TOTAL;
    if (sum) sum.hidden = step > TOTAL;
    err.textContent = '';
  };
  const check = () => {
    const p = panes[step - 1];
    const groups = [...new Set([...p.querySelectorAll('input[type=radio]')].map(r => r.name))];
    if (groups.some(n => !f.querySelector(`input[name="${n}"]:checked`))) return 'Bitte wähle jeweils eine Antwort aus.';
    const bad = [...p.querySelectorAll('[required]')].find(el => !el.checkValidity());
    if (!bad) return '';
    bad.focus();
    if (bad.type === 'email') return 'Bitte gib eine gültige E-Mail-Adresse ein, zum Beispiel name@betrieb.de.';
    if (bad.type === 'checkbox') return 'Bitte bestätige die Datenschutzerklärung.';
    return 'Bitte fülle die Felder mit * aus.';
  };
  // Zum Schritt wechseln, Fokus mitnehmen und den Konfigurator wieder ins Bild holen
  const go = (n, focus = true) => {
    step = n; render();
    if (f.getBoundingClientRect().top < 0) f.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
    const first = panes[step - 1].querySelector('input:not([type=hidden]):not([readonly]),textarea');
    if (focus && first && step <= TOTAL) first.focus({ preventScroll: true });
  };
  // Mausklick auf eine Antwort springt weiter, wenn der Schritt nur eine Frage hat (Pfeiltasten nicht)
  let pointer = false;
  f.addEventListener('pointerdown', () => pointer = true);
  f.addEventListener('keydown', () => pointer = false);
  f.querySelectorAll('.pane[data-auto] input[type=radio]').forEach(r => r.addEventListener('change', () => {
    if (!pointer) return;
    const at = step;
    setTimeout(() => { if (step === at && !check()) go(step + 1); }, 320);
  }));
  back.addEventListener('click', () => go(step - 1));
  next.addEventListener('click', async () => {
    const e = check(); if (e) { err.textContent = e; return; }
    if (step < TOTAL) { go(step + 1); return; }
    next.disabled = true; next.textContent = 'Wird gesendet …';
    try {
      const r = await fetch('/', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: new URLSearchParams(new FormData(f)).toString() });
      if (!r.ok) throw new Error();
      step++; render(); f.classList.add('sent');
      // Danke-Meldung ins Bild holen: das Formular wird kürzer, sonst bleibt man weiter unten stehen
      window.scrollTo({ top: f.getBoundingClientRect().top + scrollY - 96, behavior: 'instant' });
    } catch {
      err.textContent = 'Das Senden hat nicht geklappt. Bitte versuch es noch einmal oder schreib uns an info@homepagekonfigurator.de.';
      next.textContent = 'Konfiguration absenden';
    } finally { next.disabled = false; }
  });
  f.addEventListener('submit', e => { e.preventDefault(); next.click(); });
  render();
})();
