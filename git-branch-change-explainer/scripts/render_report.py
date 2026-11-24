#!/usr/bin/env python3
"""Render an offline report with separate business and technical views."""
import html
import json
import math
import sys
import textwrap
from pathlib import Path


def esc(value):
    return html.escape(str(value), quote=True)


def pill(text, cls=""):
    return f'<span class="pill {esc(cls)}">{esc(text)}</span>'


def list_html(items):
    return "<ul>" + "".join(f"<li>{esc(item)}</li>" for item in items) + "</ul>"


def category(item):
    value = item.get("category", "technical")
    if value not in {"business", "technical"}:
        raise ValueError(f"Unknown scene or unknown category: {value}")
    return value


def svg_text(label, x, y, width=22):
    lines = textwrap.wrap(str(label), width=width) or [""]
    baseline = y - (len(lines) - 1) * 9 + 5
    spans = "".join(
        f'<tspan x="{x}" y="{baseline + index * 18}">{esc(line)}</tspan>'
        for index, line in enumerate(lines)
    )
    return f'<text text-anchor="middle">{spans}</text>'


def graph_svg(graph, mode):
    nodes = graph.get("nodes", [])
    if not nodes:
        raise ValueError("A diagram needs at least one node.")
    positioned, cells = {}, set()
    kinds = {"start", "end", "decision", "action", "component", "store", "external"}
    for index, node in enumerate(nodes):
        node_id = node["id"]
        if node_id in positioned:
            raise ValueError(f"Duplicate diagram node: {node_id}")
        row, column = node.get("row", index), node.get("column", 0)
        if any(type(value) is not int or value < 0 for value in (row, column)):
            raise ValueError("Diagram rows and columns must be nonnegative integers.")
        if (row, column) in cells:
            raise ValueError("Diagram nodes must occupy different grid cells.")
        cells.add((row, column))
        kind = node.get("kind", "component" if mode == "components" else "action")
        if kind not in kinds:
            raise ValueError(f"Unknown diagram node kind: {kind}")
        positioned[node_id] = {
            **node, "kind": kind, "x": 110 + column * 220, "y": 80 + row * 145,
            "w": 28 if kind in {"start", "end"} else 170,
            "h": 28 if kind in {"start", "end"} else 100 if kind == "decision" else 68,
        }
    width = max(node["x"] for node in positioned.values()) + 180
    height = max(node["y"] for node in positioned.values()) + 80
    edges, outgoing = [], {}
    for edge in graph.get("edges", []):
        if edge.get("from") not in positioned or edge.get("to") not in positioned:
            raise ValueError("Diagram edges must reference existing nodes.")
        outgoing.setdefault(edge["from"], []).append(edge)
        a, b = positioned[edge["from"]], positioned[edge["to"]]
        if a["y"] < b["y"]:
            start = (a["x"], a["y"] + a["h"] / 2)
            end = (b["x"], b["y"] - b["h"] / 2)
            middle = (start[1] + end[1]) / 2
            points = [start, (start[0], middle), (end[0], middle), end]
            label_x, label_y = (start[0] + end[0]) / 2, middle - 12
        elif a["y"] == b["y"] and a["x"] != b["x"]:
            direction = 1 if b["x"] > a["x"] else -1
            start = (a["x"] + direction * a["w"] / 2, a["y"])
            end = (b["x"] - direction * b["w"] / 2, b["y"])
            points = [start, end]
            label_x, label_y = (start[0] + end[0]) / 2, start[1] - 12
        else:
            # Route retries and backward connections around the nodes.
            start = (a["x"] + a["w"] / 2, a["y"])
            end = (b["x"] + b["w"] / 2, b["y"])
            side_x = max(start[0], end[0]) + 45
            width = max(width, side_x + 90)
            points = [start, (side_x, start[1]), (side_x, end[1]), end]
            label_x, label_y = side_x + 5, (start[1] + end[1]) / 2
        points = [point for i, point in enumerate(points) if i == 0 or point != points[i - 1]]
        path = "M " + " L ".join(f"{x},{y}" for x, y in points)
        edges.append(f'<path class="edge" d="{path}"/>')
        dx, dy = points[-1][0] - points[-2][0], points[-1][1] - points[-2][1]
        length = math.hypot(dx, dy)
        ux, uy = dx / length, dy / length
        ex, ey = points[-1]
        triangle = [(ex, ey), (ex - ux * 10 - uy * 4, ey - uy * 10 + ux * 4),
                    (ex - ux * 10 + uy * 4, ey - uy * 10 - ux * 4)]
        edges.append('<polygon class="arrowhead" points="' +
                     " ".join(f"{x},{y}" for x, y in triangle) + '"/>')
        if edge.get("label"):
            edges.append(f'<text class="edge-label" x="{label_x}" y="{label_y}" '
                         f'text-anchor="middle">{esc(edge["label"])}</text>')
    for node_id, node in positioned.items():
        if node["kind"] == "decision" and any(
            not edge.get("label") for edge in outgoing.get(node_id, [])
        ):
            raise ValueError("Every decision branch needs an edge label.")
    shapes = []
    for node in positioned.values():
        x, y, w, h, kind = (node[key] for key in ("x", "y", "w", "h", "kind"))
        shape = f'<g class="node {kind}{" changed" if node.get("changed") else ""}">'
        shape += f'<title>{esc(node.get("label", node["id"]))}</title>'
        if kind in {"start", "end"}:
            shape += f'<circle cx="{x}" cy="{y}" r="12"/>'
            if kind == "end":
                shape += f'<circle cx="{x}" cy="{y}" r="7"/>'
            shape += svg_text(node.get("label", ""), x, y - 30 if kind == "start" else y + 30)
        elif kind == "decision":
            shape += f'<polygon points="{x},{y-h/2} {x+w/2},{y} {x},{y+h/2} {x-w/2},{y}"/>'
            shape += svg_text(node.get("label", node["id"]), x, y, 15)
        elif kind == "store":
            shape += f'<path d="M {x-w/2},{y-h/2+10} v {h-20} a {w/2},10 0 0 0 {w},0 v -{h-20}"/>'
            shape += f'<ellipse cx="{x}" cy="{y-h/2+10}" rx="{w/2}" ry="10"/>'
            shape += svg_text(node.get("label", node["id"]), x, y + 5)
        else:
            shape += f'<rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" rx="12"/>'
            shape += svg_text(node.get("label", node["id"]), x, y)
        shapes.append(shape + "</g>")
    title = graph.get("title", "Activity flow" if mode == "activity" else "Component relationships")
    return (f'<figure><figcaption>{esc(title)}</figcaption><div class="diagram-scroll">'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'style="min-width:{min(width, 660)}px;max-width:{width}px" role="img" aria-label="{esc(title)}">'
            f'<title>{esc(title)}</title>{"".join(edges)}{"".join(shapes)}</svg></div></figure>')


def render_visual(scene):
    visual = scene.get("visual", {"type": "evidence"})
    kind = visual.get("type", "evidence")
    if category(scene) == "business" and kind in {"contracts", "components", "deployment", "evidence"}:
        raise ValueError(f"Visual '{kind}' belongs in the Technical view.")
    if kind in {"activity", "components"}:
        if "before" in visual or "after" in visual:
            if not isinstance(visual.get("before"), dict) or not isinstance(visual.get("after"), dict):
                raise ValueError("Diagram comparisons need both before and after graph objects.")
            body = '<div class="diagram-pair">' + "".join(
                '<section class="diagram-state">'
                f'<h3 class="state-label">{label}</h3>'
                + graph_svg({"title": label, **visual[key]}, kind) + '</section>'
                for key, label in (("before", "BEFORE"), ("after", "AFTER"))
            ) + "</div>"
        else:
            body = graph_svg(visual, kind)
        if kind == "components":
            body += '<p class="muted">Highlighted nodes identify changed components.</p>'
        return body
    if kind == "contracts":
        rows = "".join(
            "<tr>" + "".join(f"<td>{esc(row.get(key, ''))}</td>"
                            for key in ("name", "before", "after", "compatibility")) + "</tr>"
            for row in visual.get("rows", [])
        )
        return ('<div class="table-scroll"><table><caption>Contract changes</caption>'
                '<thead><tr><th>Contract</th><th>BEFORE</th><th>AFTER</th><th>Compatibility</th>'
                f'</tr></thead><tbody>{rows}</tbody></table></div>')
    if kind == "before-after":
        return ('<div class="comparison">' + "".join(
            f'<div class="box"><h3>{esc(visual.get(key + "_title", key.upper()))}</h3>'
            f'{list_html(visual.get(key, []))}</div>' for key in ("before", "after")
        ) + "</div>")
    if kind == "deployment":
        body = f'<h3>Deployment risk: {esc(visual.get("risk", "unknown"))}</h3>'
        for key, label in (("requires", "Requirements"), ("rollback", "Rollback"),
                           ("verify", "Production verification"), ("compatibility", "Compatibility")):
            content = visual.get(key)
            if content:
                body += f'<div class="box"><h3>{label}</h3>'
                body += list_html(content) if isinstance(content, list) else f'<p>{esc(content)}</p>'
                body += "</div>"
        return body
    if kind == "evidence":
        return evidence_html(scene.get("evidence", []), "technical")
    raise ValueError(f"Unknown visual type: {kind}")


def evidence_html(items, view):
    if not items:
        return ""
    if view == "business":
        labels = dict.fromkeys(item.get("label", "unknown") for item in items)
        return '<div class="confidence">Evidence: ' + " ".join(pill(label) for label in labels) + "</div>"
    return '<div class="evidence">' + "".join(
        f'<p><span class="confidence-label">{esc(item.get("label", "unknown"))}</span> '
        f'{esc(item.get("detail", ""))}</p>' for item in items
    ) + "</div>"


def source_register(scenes):
    rows = "".join(
        f'<tr><td>{esc(scene.get("id", index))}</td><td>{esc(category(scene))}</td>'
        f'<td>{esc(item.get("label", "unknown"))}</td><td>{esc(item.get("detail", ""))}</td></tr>'
        for index, scene in enumerate(scenes) for item in scene.get("evidence", [])
    )
    if not rows:
        return ""
    return ('<aside class="sources"><h2>Source evidence</h2><div class="table-scroll"><table>'
            '<thead><tr><th>Scene</th><th>Category</th><th>Confidence</th><th>Source</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div></aside>')


CSS = """
:root{--bg:#080e10;--panel:#101b1e;--text:#f2f0e7;--muted:#a6b8b7;--line:#2a3c3e;--accent:#b8f87a;--cyan:#74d9d0;--read-progress:0;color-scheme:dark}
*{box-sizing:border-box}
[hidden]{display:none!important}
html{scroll-padding-top:100px}
body{margin:0;background:var(--bg);color:var(--text);font-family:"Segoe UI",Arial,Helvetica,sans-serif;line-height:1.65}
body::before{content:"";position:fixed;inset:0;z-index:-1;pointer-events:none;background:radial-gradient(ellipse at 85% 5%,#18353355,transparent 55%)}
::selection{background:var(--accent);color:var(--bg)}
a{color:inherit}
.skip-link{position:absolute;top:10px;left:16px;z-index:10;padding:10px 16px;background:var(--accent);color:var(--bg);transform:translateY(-150%)}
.skip-link:focus{transform:none}
.hero,.view-intro,.sources,.unknowns,footer{max-width:1440px;margin:auto;padding:40px 56px}
.hero{position:relative;isolation:isolate;overflow:hidden;min-height:790px;min-height:min(900px,94svh);display:flex;flex-direction:column;justify-content:space-between;padding-top:34px;padding-bottom:30px}
.masthead{display:flex;align-items:center;justify-content:space-between;gap:24px;z-index:1}
.wordmark{display:flex;align-items:center;gap:12px;font-size:16px;font-weight:750;letter-spacing:-.04em}
.brand-mark{display:grid;place-items:center;width:28px;height:28px;background:var(--accent);color:var(--bg);font-size:22px;font-weight:900;line-height:1;border-radius:7px}
.edition,.hero-bottom,.eyebrow,.scene-number,.tab-number,.visual-label{font-family:Consolas,"Courier New",monospace;font-size:11px;letter-spacing:.12em;text-transform:uppercase}
.edition{color:var(--muted)}
.hero-copy{position:relative;z-index:1;width:66%;padding:90px 0 76px}
.hero .eyebrow{display:flex;align-items:center;gap:12px;color:var(--accent)}
.hero .eyebrow::before{content:"";height:1px;width:36px;background:currentColor}
h1{font-size:clamp(56px,7.8vw,112px);font-weight:600;letter-spacing:-.07em;line-height:.99;max-width:13ch;margin:24px 0 30px;overflow-wrap:anywhere;text-wrap:balance}
.hero-rule{height:5px;width:74px;background:var(--accent);box-shadow:0 0 32px #b8f84230}
.hero-bottom{position:relative;z-index:1;display:flex;align-items:center;justify-content:space-between;gap:24px;color:var(--muted)}
.hero-bottom a{display:flex;align-items:center;gap:28px;text-decoration:none;color:var(--text);padding:12px 0}
.scroll-arrow{font-size:22px;color:var(--accent)}
.hero-art{position:absolute;z-index:0;pointer-events:none;top:100px;right:-25px;bottom:50px;width:53%;overflow:hidden;contain:paint}
.parallax-layer{position:absolute;inset:0}
.art-grid{position:absolute;inset:12% -50% -45% -30%;background-image:linear-gradient(#5b9e9030 1px,transparent 1px),linear-gradient(90deg,#5b9e9030 1px,transparent 1px);background-size:52px 52px;transform:perspective(550px) rotateX(58deg) rotateZ(-24deg);mask-image:radial-gradient(ellipse,#0008,transparent 68%)}
.art-halo{position:absolute;width:460px;height:460px;top:12%;left:10%;border-radius:50%;background:radial-gradient(circle,#5cdcb522,transparent 65%)}
.art-orbit{position:absolute;width:420px;height:420px;top:18%;left:15%;border:1px solid #b8f87a65;border-radius:50%;transform:rotate(-32deg) scaleX(.59);box-shadow:inset 0 0 45px #b8f87a06,0 0 45px #b8f87a06}
.art-orbit::after{content:"";position:absolute;inset:35px;border:1px solid #74d9d035;border-radius:50%}
.art-orbit.second{transform:rotate(38deg) scaleX(.59);border-color:#74d9d055}
.art-orbit.third{transform:rotate(90deg) scaleX(.59);border-color:#b8f87a30}
.art-core{position:absolute;top:calc(18% + 146px);left:calc(15% + 146px);height:128px;width:128px;border:1px solid #c5ffb2aa;border-radius:28px;transform:rotate(-20deg);background:linear-gradient(145deg,#c3ff9f30,#11363990 55%,#080e10);box-shadow:0 0 80px #74d9d025,inset 0 0 28px #b8f87a15;display:grid;place-items:center}
.art-core span{font-size:64px;font-weight:300;line-height:1;color:var(--accent);transform:rotate(20deg)}
.art-satellite{position:absolute;left:24%;top:25%;width:11px;height:11px;background:var(--accent);border-radius:50%;box-shadow:0 0 25px #b8f87a80}
.art-satellite.second{left:77%;top:65%;background:var(--cyan);width:7px;height:7px}
.art-coordinate{position:absolute;top:76%;left:28%;color:#a6b8b7aa;font:10px Consolas,monospace;letter-spacing:.2em}
.change-notice{padding:16px 18px;margin-top:28px;border-left:3px solid var(--accent);background:#14241be6;font-size:17px;font-weight:600;max-width:600px}
.eyebrow{color:var(--accent);font-weight:700}
h2{font-size:clamp(30px,3.4vw,48px);font-weight:550;letter-spacing:-.045em;line-height:1.12;text-wrap:balance}
h3{font-size:14px;margin:0 0 12px}
p{max-width:720px}
.tabs{position:sticky;top:0;z-index:5;background:#080e10f5;border-block:1px solid var(--line)}
.tabs-shell{max-width:1440px;padding:0 56px;margin:auto;display:flex;align-items:center;gap:32px}
.tabs button{position:relative;display:flex;align-items:center;gap:12px;min-height:80px;padding:18px 0;border:0;font:inherit;font-size:14px;font-weight:600;color:var(--muted);background:transparent;cursor:pointer}
.tabs button::after{content:"";position:absolute;bottom:0;left:0;right:0;height:2px;background:transparent}
.tabs button[aria-selected=true]{color:var(--text)}
.tabs button[aria-selected=true]::after{background:var(--accent)}
.tab-number{font-size:10px;color:var(--muted)}
.tabs button[aria-selected=true] .tab-number{color:var(--accent)}
.reading-progress{position:absolute;top:-1px;left:0;width:100%;height:2px;background:var(--accent);transform:scaleX(var(--read-progress));transform-origin:left;pointer-events:none}
:focus-visible{outline:2px solid var(--accent);outline-offset:6px;border-radius:2px}
.view-intro{padding-top:72px;padding-bottom:52px}
.view-intro h2{margin:12px 0 18px}
.view-intro>p{font-size:18px;color:var(--muted);max-width:760px}
.meta,.confidence{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.meta{margin-top:26px}
.pill{border:1px solid var(--line);border-radius:4px;padding:5px 9px;font:11px/1.5 Consolas,monospace;color:var(--muted);overflow-wrap:anywhere;max-width:100%}
.story{max-width:1440px;margin:auto;padding:0 56px;display:grid;grid-template-columns:minmax(0,.88fr) minmax(0,1.12fr);gap:72px}
.story article{min-width:0}
.step{min-height:88vh;display:flex;flex-direction:column;justify-content:center;padding:72px 0;scroll-margin-top:100px;min-width:0}
.scene-heading{display:flex;align-items:center;gap:18px;margin-bottom:12px}
.scene-number{color:var(--muted);border:1px solid var(--line);border-radius:50%;width:34px;height:34px;display:grid;place-items:center;flex-shrink:0;letter-spacing:0}
.step.active .scene-number{background:var(--accent);border-color:var(--accent);color:var(--bg)}
.step h2{margin:16px 0 26px}
.step p{font-size:17px;color:var(--muted);margin:0 0 16px;line-height:1.8}
.step.active h2{color:var(--text)}
.confidence{margin-top:24px;padding-top:20px;border-top:1px solid var(--line);font:11px Consolas,monospace;color:var(--muted)}
.visual-wrap{position:relative;min-width:0}
.visual-card{position:sticky;top:112px;max-height:calc(100vh - 144px);overflow:auto;overscroll-behavior:contain;margin:40px 0;padding:30px;background:linear-gradient(145deg,#162528,#0d171a 80%);border:1px solid #3a5350;border-radius:18px;box-shadow:0 24px 70px #0005,inset 0 1px #ffffff08;scrollbar-color:#48625a transparent;scrollbar-width:thin}
.visual-label{color:var(--accent);margin-bottom:16px;display:flex;align-items:center;gap:8px;font-size:10px}
.visual-label::before{content:"";width:5px;height:5px;background:currentColor;border-radius:50%}
.visual-title{font-size:24px;line-height:1.25;letter-spacing:-.03em;margin-bottom:26px}
.mobile-visual{display:none}
.box{border:1px solid var(--line);background:#080e1040;padding:20px;border-radius:10px;margin:12px 0;overflow-wrap:anywhere}
.box h3{font:11px Consolas,monospace;letter-spacing:.1em;color:var(--muted)}
.comparison .box:last-child{border-color:#587147;background:#b8f87a06}
.comparison .box:last-child h3{color:var(--accent)}
.box p{margin:0}
.comparison{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:12px}
ul{padding-left:20px}
li{margin:8px 0}
li::marker{color:var(--accent)}
.diagram-pair{display:grid;gap:28px}
.diagram-state{min-width:0;border-top:1px solid var(--line);padding-top:18px}
.state-label{display:inline-block;color:var(--muted);font:11px Consolas,monospace;letter-spacing:.12em;border:1px solid var(--line);padding:5px 10px;border-radius:4px}
.diagram-state:last-child .state-label{color:var(--accent);border-color:#587147}
figure{margin:0 0 18px}
figcaption{color:var(--muted);font-size:13px;font-weight:600;margin:4px 0 16px}
.diagram-scroll,.table-scroll{overflow:auto;max-width:100%;scrollbar-width:thin;scrollbar-color:#48625a transparent}
svg{display:block;width:100%;height:auto}
svg text{fill:var(--text);font-family:"Segoe UI",Arial,Helvetica,sans-serif;font-size:16px}
.node rect,.node polygon,.node path,.node ellipse{fill:#15282b;stroke:#78928e;stroke-width:1.5}
.node.changed rect,.node.changed polygon,.node.changed path,.node.changed ellipse{fill:#24432d;stroke:var(--accent);stroke-width:2}
.node.external rect{stroke-dasharray:6 4}
.node circle{fill:var(--accent);stroke:var(--accent);stroke-width:2}
.node.end circle:first-of-type{fill:var(--bg)}
.edge{fill:none;stroke:#89aba4;stroke-width:1.5}
.arrowhead{fill:#89aba4}
.edge-label{font-size:14px;paint-order:stroke;stroke:var(--panel);stroke-width:5px;stroke-linejoin:round}
table{width:100%;border-collapse:collapse;font-size:13px;min-width:440px}
caption{text-align:left;font-size:20px;letter-spacing:-.02em;font-weight:600;margin-bottom:20px}
th,td{text-align:left;vertical-align:top;padding:16px 12px;border-bottom:1px solid var(--line);overflow-wrap:anywhere}
th{color:var(--accent);font:10px Consolas,monospace;letter-spacing:.08em;text-transform:uppercase;background:#b8f87a06}
.sources table{min-width:600px}
.evidence{border-top:1px solid var(--line);margin-top:24px;padding-top:10px;color:var(--muted)}
.evidence p{font-size:13px}
.confidence-label{color:var(--accent);font:11px Consolas,monospace}
.unknowns,.sources{border-top:1px solid var(--line);padding-block:56px}
.unknowns h2,.sources h2{font-size:30px}
.empty{padding:48px 56px;max-width:1440px;margin:auto}
.muted,footer{color:var(--muted);font-size:12px}
footer{border-top:1px solid var(--line);padding-block:32px}
html:not(.enhanced) .visual-wrap{display:none}
html:not(.enhanced) .mobile-visual{display:block}
html:not(.enhanced) .story{grid-template-columns:minmax(0,1fr)}
@media(min-width:761px) and (prefers-reduced-motion:no-preference){.parallax-layer{will-change:transform}}
@media(max-width:1100px){
 .hero,.view-intro,.sources,.unknowns,footer{padding-inline:32px}
 .story,.tabs-shell{padding-inline:32px}.story{gap:40px}
 .hero-art{right:-80px;width:58%;opacity:.8}
}
@media(max-width:900px){
 .story{grid-template-columns:minmax(0,1fr);gap:0}
 .visual-wrap{display:none}
 .mobile-visual{display:block;margin:28px 0 0;background:var(--panel);padding:22px;border-radius:14px;border:1px solid var(--line)}
 .step{min-height:0;padding:42px 0;border-top:1px solid var(--line)}
 .step p{max-width:680px}
}
@media(max-width:760px){
 .hero{min-height:680px;padding-top:24px}
 .hero-copy{width:100%;padding:86px 0 80px}
 h1{font-size:clamp(52px,10vw,78px);max-width:12ch}
 .hero-art{top:100px;right:-160px;bottom:20px;width:560px;opacity:.3;z-index:-1}
 .parallax-layer{transform:none!important}
 .edition{font-size:9px;letter-spacing:.06em}
 .hero-bottom{font-size:9px;letter-spacing:.08em}
 .view-intro{padding-top:46px;padding-bottom:36px}
}
@media(max-width:560px){
 .hero,.view-intro,.sources,.unknowns,footer{padding-inline:22px}
 .story,.tabs-shell{padding-inline:22px}
 .hero{min-height:640px}
 .hero-copy{padding-top:70px;padding-bottom:70px}
 .masthead{gap:12px}.edition{max-width:94px;text-align:right}
 .hero-bottom>span{max-width:110px}
 .hero-bottom a{gap:14px}
 .tabs-shell{gap:26px}
 .tabs button{min-height:72px;font-size:12px;gap:8px}
 .comparison{grid-template-columns:minmax(0,1fr)}
 .mobile-visual{padding:18px}
 .step h2{font-size:34px}
 .step p,.view-intro>p{font-size:16px}
 .empty{padding:32px 22px}
}
@media(prefers-reduced-motion:reduce){
 *,*::before,*::after{scroll-behavior:auto!important;animation:none!important;transition:none!important}
 .parallax-layer{transform:none!important;will-change:auto!important}
}
@media print{
 :root{--bg:#fff;--panel:#fff;--text:#172526;--muted:#425653;--line:#acbdb7;--accent:#315b23;color-scheme:light}
 body{background:#fff}body::before,.hero-art,.tabs,.hero-bottom,.hero-rule{display:none!important}
 .hero{min-height:0;padding:24px 0}.hero-copy{padding:20px 0;width:100%}h1{font-size:42px;max-width:none}
 .hero,.view-intro,.story,.sources,.unknowns,footer{max-width:none;padding-inline:0}
 .view-intro{padding-block:24px}.story{display:block}.visual-wrap{display:none}
 .step{min-height:0;padding-block:24px;break-inside:avoid}
 .mobile-visual{display:block;padding:16px;border:1px solid var(--line);border-radius:8px;margin-block:16px}
 .box{background:#fff}.diagram-scroll,.table-scroll{overflow:visible}
 svg{min-width:0!important;max-width:100%!important}table,.sources table{min-width:0}
 .node rect,.node polygon,.node path,.node ellipse{fill:#eef3ef;stroke:#536c63}
 .node.changed rect,.node.changed polygon,.node.changed path,.node.changed ellipse{fill:#dceacd;stroke:var(--accent)}
 .edge{stroke:#536c63}.arrowhead{fill:#536c63}.change-notice{background:#eef3ef}
 footer{font-size:10px}
}
"""


JS = """
const tabs = Array.from(document.querySelectorAll('[role="tab"]'));
const panels = Array.from(document.querySelectorAll('[data-view]'));
let current = document.querySelector('[data-view]:not([hidden])');
const root = document.documentElement;
const hero = document.querySelector('.hero');
const layers = Array.from(document.querySelectorAll('.hero-art [data-parallax]'));
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const compactViewport = window.matchMedia('(max-width: 760px)');
let scheduled = false;
function updateDepth() {
  const distance = Math.max(0, root.scrollHeight - window.innerHeight);
  root.style.setProperty('--read-progress', distance ? Math.min(1, Math.max(0, window.scrollY / distance)) : 0);
  if (reducedMotion.matches || compactViewport.matches) {
    layers.forEach(layer => layer.style.removeProperty('transform'));
    return;
  }
  // Read layout once; transform decorative wrappers only. Native scrolling stays intact.
  const offset = Math.max(0, Math.min(window.scrollY, hero.offsetHeight));
  layers.forEach(layer => {
    const shift = offset * Number(layer.dataset.parallax);
    layer.style.transform = 'translate3d(0,' + shift.toFixed(2) + 'px,0)';
  });
}
function activate(step) {
  current.querySelectorAll('.step').forEach(item => item.classList.toggle('active', item === step));
  const card = current.querySelector('.visual-card');
  const template = document.getElementById('visual-' + step.dataset.scene);
  if (card && template && card.dataset.scene !== step.dataset.scene) {
    card.replaceChildren(template.content.cloneNode(true));
    card.dataset.scene = step.dataset.scene;
    card.scrollTop = 0;
  }
}
function update() {
  scheduled = false;
  updateDepth();
  const steps = Array.from(current.querySelectorAll('.step'));
  if (!steps.length) return;
  const focus = window.innerHeight * 0.5;
  const nearest = steps.reduce((best, step) => {
    const rect = step.getBoundingClientRect();
    const distance = Math.abs(rect.top + rect.height / 2 - focus);
    return !best || distance < best.distance ? {step, distance} : best;
  }, null);
  activate(nearest.step);
}
function selectTab(tab, scroll = true) {
  tabs.forEach(item => {
    const selected = item === tab;
    item.setAttribute('aria-selected', String(selected));
    item.tabIndex = selected ? 0 : -1;
  });
  panels.forEach(panel => { panel.hidden = panel.id !== tab.getAttribute('aria-controls'); });
  current = document.getElementById(tab.getAttribute('aria-controls'));
  if (scroll) document.querySelector('.tabs').scrollIntoView({block:'start', behavior:'instant'});
  update();
}
tabs.forEach((tab, index) => {
  tab.addEventListener('click', () => selectTab(tab));
  tab.addEventListener('keydown', event => {
    if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    const next = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1
      : (index + (event.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
    tabs[next].focus();
    selectTab(tabs[next]);
  });
});
function scheduleUpdate() {
  if (!scheduled) { scheduled = true; requestAnimationFrame(update); }
}
window.addEventListener('scroll', scheduleUpdate, {passive:true});
window.addEventListener('resize', scheduleUpdate);
reducedMotion.addEventListener('change', scheduleUpdate);
compactViewport.addEventListener('change', scheduleUpdate);
update();
root.classList.add('enhanced');
"""


def build_html(data):
    scenes = data.get("scenes", [])
    for scene in scenes:
        category(scene)
    meta, summary = data.get("meta", {}), data.get("summary", {})
    statuses = {key: summary.get(key) for key in
                ("change_status", "business_change_status", "technical_change_status")}
    for key, status in statuses.items():
        if status is not None and status not in {"changed", "unchanged", "unknown"}:
            raise ValueError(f"Invalid {key}: {status}")
    if statuses["change_status"] == "unchanged":
        if scenes or any(statuses[key] not in {None, "unchanged"}
                         for key in ("business_change_status", "technical_change_status")):
            raise ValueError("An unchanged comparison cannot contain change scenes or conflicting category statuses.")
        statuses.update(business_change_status="unchanged", technical_change_status="unchanged")
    notice = {
        "unchanged": "No changes in the selected comparison.",
        "unknown": "Could not determine whether the selected comparison contains changes."
    }.get(statuses["change_status"], "")
    notice = f'<p class="change-notice" role="status">{notice}</p>' if notice else ""
    visuals = {index: render_visual(scene) for index, scene in enumerate(scenes)}
    initial = "business" if any(category(scene) == "business" for scene in scenes) else "technical"
    tabs, panels = [], []
    for view, label in (("business", "Business changes"), ("technical", "Technical changes")):
        status = statuses[view + "_change_status"]
        if status == "unchanged" and any(category(scene) == view for scene in scenes):
            raise ValueError(f"An unchanged {view} view cannot contain change scenes.")
        selected = view == initial
        tabs.append(f'<button id="tab-{view}" role="tab" aria-controls="view-{view}" '
                    f'aria-selected="{str(selected).lower()}" tabindex="{0 if selected else -1}">'
                    f'<span class="tab-number" aria-hidden="true">0{len(tabs) + 1}</span>{label}</button>')
        if view == "business":
            intro = summary.get("purpose", "") if initial == "business" else ""
        else:
            intro = summary.get("technical_purpose", summary.get("purpose", "") if initial == "technical" else "")
        context = f'<p>{esc(intro)}</p>' if intro else ""
        if view == "technical":
            context += '<div class="meta">' + "".join(
                pill(f"{key}: {meta.get(key, 'unknown')}") for key in ("branch", "base", "head")
            ) + pill("risk: " + str(summary.get("risk_level", "unknown")))
            if meta.get("worktree_status"):
                context += pill(meta["worktree_status"])
            context += "</div>"
            if summary.get("deployment_action"):
                context += f'<p>{esc(summary["deployment_action"])}</p>'
        steps = []
        for index, scene in enumerate(scenes):
            if category(scene) != view:
                continue
            steps.append(
                f'<section class="step" id="scene-{index}" data-scene="{index}">'
                '<div class="scene-heading">'
                f'<span class="scene-number" aria-hidden="true">{len(steps) + 1:02d}</span>'
                f'<div class="eyebrow">{esc(scene.get("eyebrow", label))}</div></div>'
                f'<h2>{esc(scene.get("title", ""))}</h2>'
                + "".join(f'<p>{esc(item)}</p>' for item in scene.get("narrative", []))
                + evidence_html(scene.get("evidence", []), view)
                + f'<div class="mobile-visual">{visuals[index]}</div></section>'
            )
        empty_message = {
            "unchanged": f"No {view} changes identified.",
            "unknown": f"Could not determine whether there are {view} changes.",
            "changed": f"{label} were identified, but scene details were not provided."
        }.get(status, f"No {view} change analysis was recorded. This does not establish that there are no changes.")
        story = ('<main class="story"><article>' + "".join(steps) + '</article>'
                 '<aside class="visual-wrap" aria-label="Scene visual"><div class="visual-card"></div></aside></main>'
                 if steps else f'<p class="empty" role="status">{empty_message}</p>')
        if steps and status == "unknown":
            context += f'<p role="status">{empty_message}</p>'
        unknowns = []
        for item in data.get("unknowns", []):
            item = item if isinstance(item, dict) else {"category": "technical", "detail": item}
            if category(item) == view:
                unknowns.append(item.get("detail", ""))
        extra = f'<section class="unknowns"><h2>Unknowns</h2>{list_html(unknowns)}</section>' if unknowns else ""
        if view == "technical":
            extra += source_register(scenes)
            if meta.get("commit_range"):
                extra += f'<p class="view-intro muted">{esc(meta["commit_range"])}</p>'
        panels.append(
            f'<section id="view-{view}" data-view="{view}" role="tabpanel" aria-labelledby="tab-{view}"'
            f'{" hidden" if not selected else ""}><div class="view-intro"><h2>{label}</h2>{context}</div>'
            f'{story}{extra}</section>'
        )
    templates = "".join(
        f'<template id="visual-{index}"><div class="visual-label">{esc(category(scene))} view</div>'
        f'<div class="visual-title">{esc(scene.get("title", ""))}</div>'
        f'{visuals[index]}</template>' for index, scene in enumerate(scenes)
    )
    return f'''<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(meta.get("title", "Branch change explanation"))}</title><style>{CSS}</style></head>
<body>
<a class="skip-link" href="#change-views">Skip to report</a>
<header class="hero">
  <div class="masthead"><div class="wordmark"><span class="brand-mark" aria-hidden="true">t</span>Tovli Explain</div><span class="edition">Change report / Before &amp; After</span></div>
  <div class="hero-copy"><div class="eyebrow">Understand the change</div><h1>{esc(meta.get("title", "Branch change explanation"))}</h1><div class="hero-rule" aria-hidden="true"></div>{notice}</div>
  <div class="hero-art" aria-hidden="true">
    <div class="parallax-layer" data-parallax="0.08"><div class="art-grid"></div><div class="art-halo"></div></div>
    <div class="parallax-layer" data-parallax="0.18"><div class="art-orbit"></div><div class="art-orbit second"></div><div class="art-orbit third"></div></div>
    <div class="parallax-layer" data-parallax="0.28"><div class="art-core"><span>&#916;</span></div><div class="art-coordinate">BEFORE &nbsp; &#8594; &nbsp; AFTER</div></div>
    <div class="parallax-layer" data-parallax="0.36"><div class="art-satellite"></div><div class="art-satellite second"></div></div>
  </div>
  <div class="hero-bottom"><span>Business + Technical</span><a href="#change-views">Explore the report <span class="scroll-arrow" aria-hidden="true">&#8595;</span></a></div>
</header>
<nav id="change-views" class="tabs" role="tablist" aria-label="Change category"><div class="reading-progress" aria-hidden="true"></div><div class="tabs-shell">{"".join(tabs)}</div></nav>
{"".join(panels)}
<footer>STE status: {esc(meta.get("ste_status", "Writing rules applied. Controlled vocabulary not formally verified."))}</footer>
{templates}<script>{JS}</script>
</body></html>'''


def main():
    if len(sys.argv) != 3:
        print("Usage: render_report.py <report-data.json> <output.html>", file=sys.stderr)
        return 2
    try:
        data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        output = build_html(data)
        destination = Path(sys.argv[2])
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(output, encoding="utf-8")
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(f"Cannot render report: {error}", file=sys.stderr)
        return 1
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
