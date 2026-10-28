"""Styles and the section-nav script of the full report, taken from the layout of Gaurav Mishra's reading template."""

CSS = r"""
:root {
  --ink: #1A1A1A;
  --ink-soft: #3D3D3D;
  --coral: #E8897B;
  --coral-lt: #FBE7E3;
  --orange: #F2921E;
  --orange-dk: #C96F0F;
  --cream: #FBF6EF;
  --gray: #6E6E6E;
  --rule: #E4DCD3;
  --font-head: 'Cambria', Georgia, 'Times New Roman', serif;
  --font-body: 'Calibri', 'Segoe UI', Arial, sans-serif;
}
* { box-sizing: border-box; }
html, body {
  margin: 0; padding: 0;
  font-family: var(--font-body);
  font-size: 16px; line-height: 1.55;
  color: var(--ink); background: #FFFFFF;
  -webkit-text-size-adjust: 100%;
}
img { max-width: 100%; }
a { color: var(--orange-dk); }

/* ---------- Sticky nav (storyboard chrome, not in the print template) ---------- */
#topbar {
  position: sticky; top: 0; z-index: 50;
  background: rgba(255,255,255,0.97); backdrop-filter: blur(6px);
  border-bottom: 1px solid var(--rule);
  display: flex; align-items: center; gap: 10px;
  padding: 10px clamp(14px, 4vw, 28px);
  overflow-x: auto; -webkit-overflow-scrolling: touch;
}
#topbar .brand { font-family: var(--font-head); font-weight: 700; font-size: 0.85rem; white-space: nowrap; flex: 0 0 auto; color: var(--ink); }
#topbar .brand .site { color: var(--orange-dk); font-weight: 400; margin-left: 6px; }
#topbar nav { display: flex; gap: 2px; flex: 0 0 auto; }
#topbar nav a {
  font-size: 0.72rem; font-weight: 700; text-decoration: none; color: var(--gray);
  padding: 5px 9px; border-radius: 20px; white-space: nowrap;
}
#topbar nav a.active, #topbar nav a:hover { background: var(--cream); color: var(--orange-dk); }
#progress { position: sticky; top: 0; height: 3px; background: var(--orange); z-index: 51; width: 0%; }

/* ---------- Cover ---------- */
.cover-page {
  min-height: 90vh; display: flex; flex-direction: column; justify-content: center;
  text-align: center; padding: clamp(24px, 6vw, 48px) 20px;
  background: radial-gradient(ellipse at top, var(--cream) 0%, #FFFFFF 65%);
}
.cover-logo { width: min(3.4in, 60vw); margin: 0 auto clamp(16px, 4vw, 28px); display: block; }
.cover-title-1, .cover-title-2 {
  font-family: var(--font-head); font-weight: 700;
  font-size: clamp(1.4rem, 5vw, 2.1rem); letter-spacing: 0.5px;
  color: var(--ink); margin: 0 0 4px;
}
.cover-title-2 { color: var(--orange-dk); letter-spacing: 1.5px; margin-bottom: 18px; }
.cover-sub { font-style: italic; color: var(--ink-soft); font-size: 1.05rem; margin: 0 0 6px; }
.cover-systems { color: var(--gray); font-size: 0.85rem; margin: 0 0 20px; }
.divider { color: var(--orange); font-size: 1rem; margin: 20px 0; }
.cover-lines { margin-top: 22px; }
.cover-line { font-size: 0.95rem; margin: 8px 0; }
.cover-line .label { font-weight: 700; letter-spacing: 0.5px; font-size: 0.75rem; margin-right: 8px; }
.cover-line .value { font-style: italic; color: var(--ink-soft); }
.cover-site { font-family: var(--font-head); font-weight: 700; color: var(--orange); font-size: 1.05rem; margin-top: 36px; }
.cover-foot-note { font-style: italic; color: var(--gray); font-size: 0.75rem; margin-top: 6px; }
.scroll-hint { margin-top: 30px; font-size: 0.7rem; color: #A89F92; letter-spacing: 0.05em; }

/* ---------- Section content ---------- */
.page { max-width: 760px; margin: 0 auto; padding: clamp(28px, 6vw, 48px) clamp(16px, 4vw, 20px) 8px; scroll-margin-top: 56px; }
.page.tinted { max-width: 100%; background: var(--cream); }
.page.tinted > .inner { max-width: 760px; margin: 0 auto; }

h1.section {
  font-family: var(--font-head); font-size: clamp(1.15rem, 3.4vw, 1.4rem); font-weight: 700; color: var(--ink);
  border-bottom: 2px solid var(--orange); padding-bottom: 8px; margin: 0 0 14px;
}
h1.section .num { color: var(--orange-dk); margin-right: 8px; }
h2.sub { font-family: var(--font-head); font-size: 1.05rem; font-weight: 700; color: var(--ink-soft); margin: 22px 0 8px; }
p { margin: 0 0 12px; }
.guidance { font-style: italic; color: var(--gray); font-size: 0.85rem; margin: 0 0 14px; }
.placeholder { font-style: italic; color: var(--orange-dk); }

ul.bullets { list-style: none; padding: 0; margin: 0 0 14px; }
ul.bullets li { margin: 0 0 8px; padding-left: 18px; position: relative; }
ul.bullets li::before { content: "\25CF"; color: var(--orange); font-size: 8px; position: absolute; left: 0; top: 7px; }

/* Tables scroll horizontally on narrow screens rather than squeezing/breaking */
.table-scroll { overflow-x: auto; -webkit-overflow-scrolling: touch; margin: 0 0 14px; }
table.data { width: 100%; min-width: 420px; border-collapse: collapse; font-size: 0.88rem; margin: 0; }
table.data th {
  background: var(--ink); color: #FFFFFF; text-align: left; font-family: var(--font-head);
  padding: 8px 10px; border: 1px solid var(--rule); white-space: nowrap;
}
table.data td { padding: 8px 10px; border: 1px solid var(--rule); vertical-align: top; }
table.data tr:nth-child(even) td { background: var(--cream); }

.callout { border: 1.5px solid var(--coral); background: var(--coral-lt); padding: 14px 18px; margin: 0 0 16px; border-radius: 2px; }
.callout.orange { border-color: var(--orange); background: #FDF3E7; }
.callout-title { font-family: var(--font-head); font-weight: 700; font-size: 0.95rem; margin: 0 0 6px; }
.callout-body { font-style: italic; color: var(--ink-soft); margin: 0; font-size: 0.92rem; }

.pill { display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 0.72rem; font-weight: 700; color: #fff; }
.pill.severe { background: #C0392B; }
.pill.moderate { background: var(--orange-dk); }
.pill.mild { background: #8A8A3C; }
.pill.none { background: #5A8A5A; }

/* ---------- Closing ---------- */
.closing-rule { border: none; border-top: 1px solid var(--rule); margin: 30px 0 14px; }
.disclaimer { font-style: italic; color: var(--gray); font-size: 0.78rem; }
.closing-brand { text-align: center; margin: 24px 0 48px; }
.closing-brand img { width: 0.6in; }
.closing-brand .name { font-family: var(--font-head); font-weight: 700; }
.closing-brand .site { color: var(--orange-dk); }

@media (max-width: 600px) {
  .cover-line { display: flex; flex-direction: column; gap: 2px; }
}
@media print {
  #topbar, #progress, .scroll-hint { display: none; }
  .page { max-width: 100%; }
}
.lean-up { color: #2F6B3A; font-weight: 700; }
.lean-down { color: #9A3B1B; font-weight: 700; }
.muted { color: var(--gray); }
td.num { white-space: nowrap; }
tr.now td { font-weight: 700; }
.pill { white-space: nowrap; }

"""

JS = r"""
var links = document.querySelectorAll('#topbar nav a');
  var sections = Array.prototype.map.call(links, function(l){ return document.querySelector(l.getAttribute('href')); });
  function onScroll(){
    var y = window.scrollY + 120, idx = 0;
    sections.forEach(function(s,i){ if (s && s.offsetTop <= y) idx = i; });
    Array.prototype.forEach.call(links, function(l,i){ l.classList.toggle('active', i === idx); });
    var doc = document.documentElement;
    var pct = (window.scrollY / (doc.scrollHeight - doc.clientHeight)) * 100;
    document.getElementById('progress').style.width = pct + '%';
  }
  document.addEventListener('scroll', onScroll);
  onScroll();
  Array.prototype.forEach.call(links, function(l){
    l.addEventListener('click', function(e){
      e.preventDefault();
      document.querySelector(l.getAttribute('href')).scrollIntoView({behavior:'smooth'});
    });
  });
"""
