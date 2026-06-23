#!/usr/bin/env python3
"""Render docs/slides.html into a Signal49-themed, paginated PDF.

The interactive deck (docs/slides.html) is a single-page, JS-driven dark deck.
This script reuses its 12 slide sections + SVG workflow diagrams but re-themes
them to Signal49 Research's visual language (light, Canadian-navy + signal-azure
+ beacon-amber, clean sans-serif, signal-wave brand mark) and lays each slide on
its own fixed 1280x720 page for a portable, presentable PDF.

Usage:  python3 scripts/build_slides_pdf.py
Output: docs/Obsidian-and-the-Agent-Stack.pdf
Requires: weasyprint  (pip install weasyprint)
"""
import re
import pathlib
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "slides.html"
OUT_PDF = ROOT / "docs" / "Obsidian-and-the-Agent-Stack.pdf"

html = SRC.read_text()
sections = re.findall(r'(<section class="slide.*?</section>)', html, flags=re.S)
assert len(sections) >= 12, f"expected >=12 slides, got {len(sections)}"
body = "\n".join(sections)

# 1. strip emoji (corporate look) and the icon blocks that held them
body = re.sub(r'<div class="ic">.*?</div>', "", body, flags=re.S)
for ch in ["📊", "🐍", "🤖", "🕸️", "🕸", "📑", "📄", "🔗", "🧭", "⚡",
           "🧑", "✅", "🔜", "✔", "✓", "️"]:
    body = body.replace(ch + " ", "").replace(ch, "")
body = re.sub(r'<p class="muted"[^>]*>Use <span class="kbd">.*?</p>', "", body, flags=re.S)

# 2. recolour the dark-theme literals baked into the inline SVGs
LIT = {
    "rgba(123,108,246,": "rgba(30,111,224,", "rgba(52,214,200,": "rgba(15,163,163,",
    "rgba(246,169,59,": "rgba(224,144,43,", '"#171c2e"': '"#ffffff"',
    "#9aa6c4": "#5B6B82", "#b3a8ff": "#1E6FE0", "#7ff0e4": "#0E8C8C",
    "#ffce85": "#B5771A", "#34d6c8": "#0FA3A3", "#7b6cf6": "#1E6FE0",
    "#f6a93b": "#E0902B", "#fb7185": "#D64550", "#4ade80": "#1E9E62",
    "#86efac": "#1E9E62", "#fda4b0": "#D64550", "#212845": "#EEF2F8",
    "#cdd6f7": "#28456B", 'stroke="#fff"': 'stroke="#0E2A47"',
    'fill="#fff"': 'fill="#0E2A47"',
}
for k, v in LIT.items():
    body = body.replace(k, v)

# 3. map the CSS custom properties to the Signal49 light palette
VARS = {
    "var(--bg)": "#F6F8FC", "var(--panel)": "#FFFFFF", "var(--ink)": "#12263F",
    "var(--muted)": "#5B6B82", "var(--accent2)": "#0FA3A3", "var(--accent3)": "#E0902B",
    "var(--accent)": "#1E6FE0", "var(--line)": "#D7DFEA", "var(--ok)": "#1E9E62",
    "var(--warn)": "#D64550", "var(--font)": '"Liberation Sans",sans-serif',
}
for k, v in VARS.items():
    body = body.replace(k, v)
body = re.sub(r"clamp\(([^)]*)\)", lambda m: m.group(1).split(",")[-1].strip(), body)
body = body.replace("Consolas,monospace;font-size:13px;line-height:1.5",
                    "Consolas,monospace;font-size:12px;line-height:1.42;white-space:pre-wrap")

# 4. beacon / signal-wave brand mark + a one-line title
BEACON = ('<svg width="120" height="120" viewBox="0 0 120 120" style="margin-bottom:6px" '
          'aria-hidden="true"><g fill="none" stroke-linecap="round">'
          '<path d="M60 96 A40 40 0 0 1 60 24" stroke="#0E2A47" stroke-width="6" opacity=".9"/>'
          '<path d="M76 88 A30 30 0 0 0 76 32" stroke="#1E6FE0" stroke-width="6"/>'
          '<path d="M90 80 A20 20 0 0 1 90 40" stroke="#0FA3A3" stroke-width="6"/>'
          '<circle cx="60" cy="60" r="9" fill="#E0902B" stroke="none"/></g></svg>')
body = body.replace('<h1>Obsidian', BEACON + '<h1>Obsidian', 1)
body = body.replace('<section class="slide center">',
                    '<section class="slide center title">', 1)

STYLE = """
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:#F6F8FC;color:#12263F;
  font-family:"Liberation Sans","Segoe UI",Arial,sans-serif;}
@page{size:1280px 720px;margin:0}
.slide{position:relative;width:1280px;height:720px;padding:50px 88px 58px;
  display:flex;flex-direction:column;overflow:hidden;page-break-after:always;background:#F6F8FC}
.slide:last-child{page-break-after:auto}
.slide::before{content:"";position:absolute;top:0;left:0;right:0;height:6px;
  background:linear-gradient(90deg,#0E2A47,#1E6FE0 55%,#0FA3A3)}
.slide::after{content:"SIGNAL49 RESEARCH";position:absolute;right:88px;bottom:26px;
  font-size:10.5px;letter-spacing:2.5px;color:#9AA8BC;font-weight:700}
.slide.center{align-items:center;justify-content:center;text-align:center}
h1{font-size:50px;line-height:1.06;margin:0 0 16px;font-weight:800;letter-spacing:-.6px;color:#0E2A47}
.slide.center h1{font-size:44px;margin:10px auto 30px}
.slide.title h1{white-space:nowrap;font-size:42px}
.slide.center .lead{margin:0 auto}
h2{font-size:33px;margin:0 0 22px;font-weight:750;letter-spacing:-.3px;color:#0E2A47}
h2 .dot{display:inline-block;width:.5em;height:.5em;border-radius:50%;margin-right:.45em;vertical-align:middle}
p,li{font-size:18px;line-height:1.55;color:#33425B}
.muted{color:#5B6B82}
.lead{font-size:22px;color:#33425B;max-width:66ch;line-height:1.5;margin:0 0 4px}
ul{margin:.2em 0;padding-left:1.15em}
li{margin:.42em 0}
li b{color:#0E2A47}
.kbd{font:600 13px sans-serif;background:#EEF2F8;border:1px solid #D7DFEA;border-radius:6px;padding:2px 8px;color:#5B6B82}
code{background:#EEF2F8;border:1px solid #DCE3ED;border-radius:5px;padding:1px 6px;
  font-family:"DejaVu Sans Mono",Consolas,monospace;font-size:.82em;color:#1E4D86}
.grid{display:grid;gap:22px}
.cols-2{grid-template-columns:1fr 1fr}
.cols-3{grid-template-columns:1fr 1fr 1fr}
.card{background:#FFFFFF;border:1px solid #DCE3ED;border-radius:12px;padding:18px 22px;
  box-shadow:0 1px 2px rgba(14,42,71,.05)}
.card h3{margin:.1em 0 .4em;font-size:20px;color:#0E2A47;line-height:1.2}
.card p{font-size:17px;line-height:1.5}
.tag{display:inline-block;font-size:11.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  padding:4px 11px;border-radius:6px;margin-bottom:14px}
.tag.a{background:rgba(30,111,224,.10);color:#1E6FE0;border:1px solid rgba(30,111,224,.30)}
.tag.o{background:rgba(15,163,163,.10);color:#0E8C8C;border:1px solid rgba(15,163,163,.30)}
.tag.d{background:rgba(224,144,43,.12);color:#B5771A;border:1px solid rgba(224,144,43,.32)}
.fig{flex:1;display:flex;align-items:center;justify-content:center;margin-top:6px;min-height:0}
svg{max-width:100%;height:auto}
.fig svg{width:100%;height:auto;max-width:1040px;display:block;margin:auto}
.legend{display:flex;gap:26px;flex-wrap:wrap;margin-top:16px;font-size:14.5px;color:#5B6B82;justify-content:center}
.legend span{display:inline-flex;align-items:center;gap:8px;white-space:nowrap}
.slide.center .legend{flex-wrap:nowrap;max-width:none;margin-top:24px}
.sw{width:14px;height:14px;border-radius:4px;display:inline-block}
.stat{font-size:58px;font-weight:800;line-height:1;letter-spacing:-1px}
.stat.p{color:#1E6FE0}.stat.t{color:#0FA3A3}.stat.d{color:#E0902B}
.statlbl{color:#5B6B82;font-size:15px;margin-top:6px}
.center .card,.center .grid{text-align:center}
.slide.center .grid{width:100%;max-width:1000px}
.pill{display:inline-block;background:#EEF2F8;border:1px solid #D7DFEA;border-radius:999px;
  padding:5px 13px;margin:4px 6px 4px 0;font-size:14px;color:#28456B}
text{font-family:"Liberation Sans",sans-serif;fill:#12263F}
.svg-t{font-size:13.5px;font-weight:600}
.svg-s{font-size:11px;fill:#5B6B82}
.svg-lbl{font-size:12px;fill:#5B6B82;font-style:italic}
"""

doc = (f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
       f'<title>Obsidian &amp; the Agent Stack — Signal49 Research</title>'
       f'<style>{STYLE}</style></head><body>{body}</body></html>')

from weasyprint import HTML  # noqa: E402

with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as fh:
    fh.write(doc)
HTML(string=doc, base_url=str(ROOT)).write_pdf(str(OUT_PDF))
print(f"wrote {OUT_PDF} ({OUT_PDF.stat().st_size} bytes)")
