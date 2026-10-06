#!/usr/bin/env python3
import html
import json
import sys
from pathlib import Path


def esc(value):
    return html.escape(str(value), quote=True)


def pill(text, cls=""):
    return f'<span class="pill {esc(cls)}">{esc(text)}</span>'


def narrative_html(items):
    return "".join(f"<p>{esc(item)}</p>" for item in items)


def evidence_html(items):
    if not items:
        return ""
    output = ['<div class="evidence-list"><div class="mini-title">Evidence</div>']
    for item in items:
        label = item.get("label", "unknown")
        detail = item.get("detail", "")
        output.append(
            '<div class="evidence-item">'
            f'<span class="evidence-label">{esc(label)}</span>'
            f'<span>{esc(detail)}</span>'
            '</div>'
        )
    output.append('</div>')
    return "".join(output)


def build_steps(scenes):
    output = []
    for index, scene in enumerate(scenes):
        active = " active" if index == 0 else ""
        scene_id = scene.get("id", f"scene-{index}")
        block = (
            f'<section class="step{active}" data-scene="{index}" id="{esc(scene_id)}">'
            f'<div class="eyebrow">{esc(scene.get("eyebrow", ""))}</div>'
            f'<h2>{esc(scene.get("title", ""))}</h2>'
            f'{narrative_html(scene.get("narrative", []))}'
            f'{evidence_html(scene.get("evidence", []))}'
            '</section>'
        )
        output.append(block)
    return "".join(output)


def build_html(data):
    meta = data.get("meta", {})
    summary = data.get("summary", {})
    scenes = data.get("scenes", [])
    unknowns = data.get("unknowns", [])

    steps_html = build_steps(scenes)
    raw_json = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    unknown_html = "".join(f"<li>{esc(x)}</li>" for x in unknowns)
    if not unknown_html:
        unknown_html = "<li>No unknowns were recorded.</li>"

    risk = str(summary.get("risk_level", "unknown")).lower()
    risk_class = risk if risk in {"low", "medium", "high", "critical"} else "unknown"

    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(meta.get("title", "Branch change explanation"))}</title>
<style>
:root {{
  --bg:#0b0d10; --panel:#12161b; --panel2:#171c22; --text:#f4f7f9; --muted:#9da8b3;
  --line:#27303a; --accent:#7bdcff; --good:#9be7b0; --warn:#ffd479; --bad:#ff9a9a;
}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{margin:0;background:var(--bg);color:var(--text);font-family:Arial,Helvetica,sans-serif;line-height:1.5}}
header{{min-height:74vh;display:grid;place-items:center;padding:64px 24px;border-bottom:1px solid var(--line);background:radial-gradient(circle at 70% 20%,#173141 0,transparent 36%),var(--bg)}}
.hero{{width:min(1080px,100%)}}
.kicker{{text-transform:uppercase;letter-spacing:.16em;color:var(--accent);font-size:12px;font-weight:700}}
h1{{font-size:clamp(42px,7vw,86px);line-height:.98;max-width:900px;margin:16px 0 24px;letter-spacing:-.04em}}
.lede{{font-size:clamp(18px,2.2vw,26px);max-width:780px;color:#d6dde3}}
.meta{{display:flex;gap:10px;flex-wrap:wrap;margin-top:28px}}
.pill{{border:1px solid var(--line);background:#11161b;border-radius:999px;padding:8px 12px;color:#dce5ea;font-size:13px}}
.pill.low{{border-color:#315d3c;color:var(--good)}}
.pill.medium{{border-color:#6c5930;color:var(--warn)}}
.pill.high,.pill.critical{{border-color:#6d3434;color:var(--bad)}}
.story{{width:min(1180px,100%);margin:auto;display:grid;grid-template-columns:minmax(0,1fr) minmax(380px,.9fr);gap:72px;padding:0 24px}}
.steps{{padding:20vh 0}}
.step{{min-height:76vh;display:flex;flex-direction:column;justify-content:center;opacity:.34;transition:opacity .25s ease,transform .25s ease;transform:translateY(8px)}}
.step.active{{opacity:1;transform:none}}
.eyebrow{{color:var(--accent);font-size:12px;text-transform:uppercase;letter-spacing:.14em;font-weight:700}}
h2{{font-size:clamp(28px,4vw,48px);line-height:1.08;margin:10px 0 18px;letter-spacing:-.025em}}
.step p{{font-size:18px;color:#d9e0e5;max-width:680px}}
.visual-wrap{{position:relative}}
.visual{{position:sticky;top:9vh;height:82vh;margin:9vh 0;display:flex;align-items:center}}
.visual-card{{width:100%;min-height:520px;border:1px solid var(--line);border-radius:24px;background:linear-gradient(180deg,var(--panel2),var(--panel));padding:28px;box-shadow:0 28px 80px rgba(0,0,0,.28);overflow:hidden}}
.visual-top{{display:flex;justify-content:space-between;gap:16px;align-items:center;border-bottom:1px solid var(--line);padding-bottom:18px;margin-bottom:22px}}
.visual-top strong{{font-size:18px}}
.ba{{display:grid;grid-template-columns:1fr 42px 1fr;gap:12px;align-items:stretch}}
.state{{border:1px solid var(--line);border-radius:18px;padding:18px;background:#0f1317}}
.state h3{{margin:0 0 14px;font-size:13px;letter-spacing:.12em;color:var(--muted)}}
.state ul,.deploy-list{{padding-left:18px;margin:0}}
.state li,.deploy-list li{{margin:10px 0;color:#e3e9ed}}
.arrow{{display:grid;place-items:center;color:var(--accent);font-size:30px}}
.deploy-grid{{display:grid;gap:14px}}
.deploy-box{{border:1px solid var(--line);border-radius:16px;padding:16px;background:#0f1317}}
.deploy-box .label{{font-size:11px;text-transform:uppercase;letter-spacing:.13em;color:var(--muted);margin-bottom:8px}}
.risk-banner{{font-size:34px;font-weight:800;text-transform:uppercase;letter-spacing:-.02em;margin:8px 0 24px}}
.risk-banner.low{{color:var(--good)}}
.risk-banner.medium{{color:var(--warn)}}
.risk-banner.high,.risk-banner.critical{{color:var(--bad)}}
.evidence-list{{margin-top:22px;border-top:1px solid var(--line);padding-top:16px}}
.mini-title{{font-size:11px;text-transform:uppercase;letter-spacing:.13em;color:var(--muted);margin-bottom:8px}}
.evidence-item{{display:flex;gap:10px;margin:8px 0;color:#bdc7ce;font-size:14px}}
.evidence-label{{color:var(--accent);min-width:88px}}
.unknowns{{border-top:1px solid var(--line);padding:76px 24px 100px}}
.unknowns-inner{{width:min(980px,100%);margin:auto}}
.unknowns h2{{font-size:36px}}
.unknowns li{{margin:12px 0;color:#d5dde2}}
footer{{border-top:1px solid var(--line);padding:32px 24px;color:var(--muted);font-size:13px}}
footer div{{width:min(980px,100%);margin:auto}}
.codeish{{font-family:Consolas,Monaco,monospace;font-size:12px;color:#c8d3db;word-break:break-word}}
@media (max-width:900px){{
  .story{{grid-template-columns:1fr;gap:0}}
  .visual-wrap{{order:-1}}
  .visual{{position:relative;top:auto;height:auto;margin:36px 0 0}}
  .visual-card{{min-height:0}}
  .steps{{padding:6vh 0}}
  .step{{min-height:70vh}}
}}
@media (max-width:560px){{
  .ba{{grid-template-columns:1fr}}
  .arrow{{transform:rotate(90deg);height:32px}}
  header{{min-height:66vh}}
  .visual-card{{padding:18px;border-radius:18px}}
}}
@media (prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}} .step{{transition:none}}}}
</style>
</head>
<body>
<header>
  <div class="hero">
    <div class="kicker">Git branch change explainer</div>
    <h1>{esc(meta.get("title", "Branch change explanation"))}</h1>
    <div class="lede">{esc(summary.get("purpose", ""))}</div>
    <div class="meta">
      {pill("branch: " + str(meta.get("branch", "unknown")))}
      {pill("base: " + str(meta.get("base", "unknown")))}
      {pill("head: " + str(meta.get("head", "unknown")))}
      {pill("risk: " + risk, risk_class)}
      {pill("evidence: " + str(summary.get("confidence", "unknown")))}
    </div>
  </div>
</header>
<main class="story">
  <article class="steps">{steps_html}</article>
  <aside class="visual-wrap"><div class="visual"><div class="visual-card" id="visual-card"></div></div></aside>
</main>
<section class="unknowns"><div class="unknowns-inner"><div class="eyebrow">Open items</div><h2>Unknowns</h2><ul>{unknown_html}</ul></div></section>
<footer><div><strong>STE status:</strong> {esc(meta.get("ste_status", "Writing rules applied. Controlled vocabulary not formally verified."))}<br><span class="codeish">{esc(meta.get("commit_range", ""))}</span></div></footer>
<script>
const REPORT = {raw_json};
const card = document.getElementById('visual-card');
const steps = Array.from(document.querySelectorAll('.step'));
function e(tag, cls, text) {{
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text !== undefined) n.textContent = text;
  return n;
}}
function list(items, cls='deploy-list') {{
  const ul = e('ul', cls);
  (items || []).forEach(x => {{ const li=e('li','',x); ul.appendChild(li); }});
  return ul;
}}
function render(scene) {{
  card.innerHTML = '';
  const top = e('div','visual-top');
  top.appendChild(e('strong','',scene.eyebrow || 'Change'));
  top.appendChild(e('span','pill',scene.id || ''));
  card.appendChild(top);
  const v = scene.visual || {{type:'evidence'}};
  if (v.type === 'before-after') {{
    const ba = e('div','ba');
    const before = e('div','state');
    before.appendChild(e('h3','',v.before_title || 'BEFORE'));
    before.appendChild(list(v.before || []));
    const arrow = e('div','arrow','→');
    const after = e('div','state');
    after.appendChild(e('h3','',v.after_title || 'AFTER'));
    after.appendChild(list(v.after || []));
    ba.append(before, arrow, after);
    card.appendChild(ba);
  }} else if (v.type === 'deployment') {{
    const risk = (v.risk || REPORT.summary?.risk_level || 'unknown').toLowerCase();
    card.appendChild(e('div','risk-banner ' + risk,'Deployment risk: ' + risk));
    const grid = e('div','deploy-grid');
    const addBox = (label, content, isList=false) => {{
      if (!content || (Array.isArray(content) && !content.length)) return;
      const b = e('div','deploy-box');
      b.appendChild(e('div','label',label));
      b.appendChild(isList ? list(content) : e('div','',content));
      grid.appendChild(b);
    }};
    addBox('Requirements',v.requires || [],true);
    addBox('Rollback',v.rollback || '');
    addBox('Production verification',v.verify || [],true);
    addBox('Compatibility',v.compatibility || [],true);
    card.appendChild(grid);
  }} else {{
    const grid = e('div','deploy-grid');
    const box = e('div','deploy-box');
    box.appendChild(e('div','label','Evidence'));
    const all = scene.evidence || [];
    if (all.length) {{
      all.forEach(x => box.appendChild(e('div','evidence-item',(x.label || 'unknown') + ': ' + (x.detail || ''))));
    }} else {{
      box.appendChild(e('div','','No evidence item was recorded.'));
    }}
    grid.appendChild(box);
    card.appendChild(grid);
  }}
}}
const io = new IntersectionObserver(entries => {{
  const visible = entries.filter(x => x.isIntersecting).sort((a,b) => b.intersectionRatio - a.intersectionRatio)[0];
  if (!visible) return;
  steps.forEach(x => x.classList.remove('active'));
  visible.target.classList.add('active');
  render(REPORT.scenes[Number(visible.target.dataset.scene)]);
}}, {{rootMargin:'-25% 0px -45% 0px',threshold:[0,.2,.4,.6,.8,1]}});
steps.forEach(s => io.observe(s));
if (REPORT.scenes?.length) render(REPORT.scenes[0]);
</script>
</body>
</html>'''


def main():
    if len(sys.argv) != 3:
        print("Usage: render_report.py <report-data.json> <output.html>", file=sys.stderr)
        return 2
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    data = json.loads(src.read_text(encoding="utf-8"))
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(build_html(data), encoding="utf-8")
    print(dst)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
