"""build index.html and ground_truth.csv from lineup.json.

each vehicle gets one slot. in the slot it drives up toward the camera,
stops at the door with the front plate in view, then pulls off to the left.
run: python3 build.py
"""
import csv
import json
from pathlib import Path

HERE = Path(__file__).parent
SLOT = 4.5          # seconds per vehicle
ARRIVE = 1.6        # time to drive up
LEAVE = 3.4         # when it starts pulling away
FPS = 30
CLOCK_START = 9 * 3600 + 14 * 60 + 3   # 09:14:03 on the camera stamp

lineup = json.loads((HERE / "lineup.json").read_text())


def plate(text, x, y, w, grime=False):
    """a plain fleet plate, 2:1, dark text on white."""
    h = w / 2
    bg = "#d9d4c4" if grime else "#ffffff"
    ink = "#3a3f47" if grime else "#0d1b3e"
    dirt = ""
    if grime:
        dirt = (f'<rect x="{x}" y="{y + h*0.55}" width="{w}" height="{h*0.45}" rx="{w*0.04}" '
                f'fill="#7a6a4f" opacity="0.35"/>')
    return f"""
    <g class="plate">
      <rect x="{x-4}" y="{y-4}" width="{w+8}" height="{h+8}" rx="{w*0.05}" fill="#1a1a1a"/>
      <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{w*0.04}" fill="{bg}" stroke="{ink}" stroke-width="{w*0.018}"/>
      <text class="pl-top" x="{x + w/2}" y="{y + h*0.2}" font-size="{h*0.13}"
            fill="{ink}" text-anchor="middle" letter-spacing="2">FLEET</text>
      <text class="pl-main" x="{x + w/2}" y="{y + h*0.84}" font-size="{h*0.64}" fill="{ink}" text-anchor="middle"
            textLength="{w*0.84}" lengthAdjust="spacingAndGlyphs">{text}</text>
      {dirt}
      <circle cx="{x + w*0.12}" cy="{y + h*0.14}" r="{w*0.018}" fill="#888"/>
      <circle cx="{x + w*0.88}" cy="{y + h*0.14}" r="{w*0.018}" fill="#888"/>
    </g>"""


def wheels(xl, xr, top, w=120, bottom=1000):
    return "".join(
        f'<rect x="{x}" y="{top}" width="{w}" height="{bottom-top}" rx="18" fill="#141414"/>'
        f'<rect x="{x+12}" y="{top+10}" width="{w-24}" height="{bottom-top-30}" rx="12" fill="#262626"/>'
        for x in (xl, xr))


def lights(xl, xr, y, w, h, on=False):
    glow = ""
    if False:
        glow = "".join(f'<ellipse cx="{x + w/2}" cy="{y + h/2}" rx="{w*1.1}" ry="{h*1.4}" fill="#fff6c8" opacity="0.35"/>'
                       for x in (xl, xr))
    return glow + "".join(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#f4f1e6" stroke="#555" stroke-width="4"/>'
        f'<rect x="{x+8}" y="{y+8}" width="{w*0.4}" height="{h-16}" rx="6" fill="#fffbe6"/>'
        for x in (xl, xr))


def mirror(x, y):
    return (f'<rect x="{x}" y="{y}" width="46" height="150" rx="10" fill="#1d1d1d"/>'
            f'<rect x="{x+8}" y="{y+10}" width="30" height="130" rx="6" fill="#5f6b78"/>')


def glass(x, y, w, h, rx=16):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="url(#glass)" stroke="#1b1b1b" stroke-width="8"/>'
            f'<path d="M{x+w*0.08} {y+h*0.85} L{x+w*0.35} {y+h*0.12}" stroke="#ffffff" stroke-opacity="0.18" stroke-width="{w*0.05}"/>')


def semi(c, p, on):
    return f"""
    <rect x="70" y="10" width="860" height="230" rx="6" fill="#d7d9dc" stroke="#9aa0a6" stroke-width="6"/>
    <rect x="120" y="150" width="760" height="640" rx="40" fill="{c}"/>
    <rect x="160" y="130" width="680" height="40" rx="12" fill="{c}"/>
    {''.join(f'<rect x="{x}" y="138" width="34" height="16" rx="5" fill="#f6a623"/>' for x in (300, 420, 546, 666))}
    {glass(170, 190, 320, 230)}{glass(510, 190, 320, 230)}
    {mirror(50, 230)}{mirror(904, 230)}
    <rect x="330" y="450" width="340" height="320" rx="14" fill="#c9ccd0" stroke="#8d939a" stroke-width="6"/>
    {''.join(f'<rect x="350" y="{y}" width="300" height="16" rx="4" fill="#4b5157"/>' for y in range(470, 760, 36))}
    {lights(165, 715, 640, 120, 80, on)}
    <rect x="80" y="770" width="840" height="120" rx="14" fill="#cfd3d7" stroke="#80868c" stroke-width="6"/>
    {wheels(110, 770, 880)}
    {plate(p['plate'], 390, 785, 220, p.get('grime'))}
    """


def box(c, p, on):
    return f"""
    <rect x="60" y="0" width="880" height="520" rx="8" fill="{c}" stroke="#9aa0a6" stroke-width="8"/>
    <rect x="180" y="300" width="640" height="520" rx="40" fill="#f2f2f2" stroke="#b5b5b5" stroke-width="6"/>
    {glass(220, 340, 560, 210, 24)}
    {mirror(120, 380)}{mirror(834, 380)}
    <rect x="370" y="590" width="260" height="140" rx="14" fill="#2b2f33"/>
    {''.join(f'<rect x="385" y="{y}" width="230" height="12" rx="4" fill="#555c63"/>' for y in range(605, 720, 26))}
    {lights(215, 665, 600, 120, 70, on)}
    <rect x="160" y="780" width="680" height="110" rx="14" fill="#3a3f44"/>
    {wheels(190, 690, 870)}
    {plate(p['plate'], 410, 785, 180, p.get('grime'))}
    """


def van(c, p, on):
    return f"""
    <path d="M230 300 Q250 160 500 150 Q750 160 770 300 L800 860 L200 860 Z" fill="{c}" stroke="#a7adb3" stroke-width="6"/>
    {glass(250, 230, 500, 250, 40)}
    {mirror(170, 420)}{mirror(784, 420)}
    <rect x="360" y="580" width="280" height="110" rx="30" fill="#2b2f33"/>
    {lights(225, 655, 570, 120, 70, on)}
    <rect x="200" y="760" width="600" height="110" rx="20" fill="#3a3f44"/>
    {wheels(220, 680, 860, 100)}
    {plate(p['plate'], 420, 770, 160, p.get('grime'))}
    """


def car(c, p, on):
    return f"""
    <path d="M300 520 L360 380 Q500 350 640 380 L700 520 Z" fill="{c}" stroke="#222" stroke-width="6"/>
    <path d="M330 515 L380 400 Q500 375 620 400 L670 515 Z" fill="url(#glass)" stroke="#1b1b1b" stroke-width="6"/>
    <rect x="170" y="510" width="660" height="300" rx="70" fill="{c}" stroke="#222" stroke-width="6"/>
    {mirror(140, 470).replace('height="150"', 'height="70"').replace('height="130"', 'height="50"')}
    {mirror(814, 470).replace('height="150"', 'height="70"').replace('height="130"', 'height="50"')}
    <rect x="390" y="600" width="220" height="80" rx="30" fill="#1f2326"/>
    {lights(200, 680, 580, 120, 60, on)}
    <rect x="180" y="720" width="640" height="100" rx="40" fill="#2e3236"/>
    {wheels(200, 700, 800, 100, 930)}
    {plate(p['plate'], 425, 728, 150, p.get('grime'))}
    """


def pickup(c, p, on):
    return f"""
    <path d="M270 470 L320 300 Q500 270 680 300 L730 470 Z" fill="{c}" stroke="#222" stroke-width="6"/>
    <path d="M300 465 L340 320 Q500 295 660 320 L700 465 Z" fill="url(#glass)" stroke="#1b1b1b" stroke-width="6"/>
    <rect x="150" y="460" width="700" height="380" rx="40" fill="{c}" stroke="#222" stroke-width="6"/>
    {mirror(110, 400).replace('height="150"', 'height="90"').replace('height="130"', 'height="70"')}
    {mirror(844, 400).replace('height="150"', 'height="90"').replace('height="130"', 'height="70"')}
    <rect x="340" y="540" width="320" height="150" rx="12" fill="#9ea4aa"/>
    {''.join(f'<rect x="355" y="{y}" width="290" height="14" rx="4" fill="#3b4045"/>' for y in range(555, 680, 30))}
    {lights(180, 700, 550, 120, 80, on)}
    <rect x="160" y="740" width="680" height="110" rx="20" fill="#c3c7cb" stroke="#80868c" stroke-width="6"/>
    {wheels(180, 700, 830, 120, 980)}
    {plate(p['plate'], 420, 750, 160, p.get('grime'))}
    """


def bus(c, p, on):
    return f"""
    <rect x="130" y="40" width="740" height="860" rx="50" fill="{c}" stroke="#555" stroke-width="6"/>
    <rect x="200" y="70" width="600" height="70" rx="10" fill="#111"/>
    <rect x="230" y="92" width="540" height="26" rx="6" fill="#ff9c1a" opacity="0.55"/>
    {glass(170, 160, 660, 420, 30)}
    {mirror(60, 180)}{mirror(894, 180)}
    {lights(180, 700, 640, 120, 80, on)}
    <rect x="370" y="630" width="260" height="90" rx="10" fill="#222"/>
    <rect x="120" y="780" width="760" height="120" rx="16" fill="#2b2b2b"/>
    {wheels(160, 720, 880)}
    {plate(p['plate'], 410, 792, 180, p.get('grime'))}
    """


DRAW = dict(semi=semi, box=box, van=van, car=car, pickup=pickup, bus=bus)

DEFS = """
<defs>
  <linearGradient id="glass" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#9fb6c9"/><stop offset="1" stop-color="#2c3a46"/>
  </linearGradient>
</defs>"""

vehicles, shadows, tweens, clock, overlays = [], [], [], [], []
total = SLOT * len(lineup)
rows = []

for i, v in enumerate(lineup):
    start = round(i * SLOT, 3)
    vid = f"v{i+1:02d}"
    angle = v.get("angle", 0)
    dusk = v.get("dusk", False)
    svg = DRAW[v["vehicle"]](v["color"], v, dusk)
    vehicles.append(f"""
      <div id="{vid}" class="clip veh" data-start="{start}" data-duration="{SLOT}" data-track-index="2"
           data-layout-allow-overflow data-layout-ignore>
        <div id="{vid}-body" class="body">
          <svg viewBox="0 0 1000 1000" width="900" height="900">{DEFS}
            <ellipse cx="500" cy="1000" rx="470" ry="26" fill="#000" opacity="0.45"/>
            {svg}
          </svg>
        </div>
      </div>""")
    a, l = start + ARRIVE, start + LEAVE
    tweens.append(f"""
    tl.fromTo("#{vid}-body", {{x: 0, y: -700, scale: 0.12, rotationY: {angle}}},
      {{x: 0, y: 0, scale: 1, rotationY: {angle * 0.6}, duration: {ARRIVE}, ease: "power2.out"}}, {start});
    tl.to("#{vid}-body", {{y: 4, duration: 0.25, ease: "sine.inOut", yoyo: true, repeat: 3}}, {a + 0.2});
    tl.to("#{vid}-body", {{x: -1500, y: 30, rotationY: -25, duration: 1.0, ease: "power2.in"}}, {l});""")
    if dusk:
        overlays.append(f'<div id="{vid}-dusk" class="clip dusk" data-start="{start}" data-duration="{SLOT}" data-track-index="3" data-layout-ignore></div>')
    plate_visible = f"{a:.2f}-{l:.2f}"
    rows.append(dict(
        slot=i + 1, start_s=start, end_s=round(start + SLOT, 3),
        plate_clear_from_s=round(a, 2), plate_clear_to_s=round(l, 2),
        start_frame=int(start * FPS), end_frame=int((start + SLOT) * FPS) - 1,
        vehicle=v["vehicle"], plate=v["plate"], on_manifest=v["on_manifest"],
        expected_door=v["expect"], conditions=";".join(k for k in ("angle", "dusk", "grime") if v.get(k)) or "",
        note=v["note"]))

for s in range(int(total)):
    t = CLOCK_START + s
    stamp = f"2026-10-26 {t//3600:02d}:{t%3600//60:02d}:{t%60:02d}"
    clock.append(f'<span id="clk{s:03d}" class="clip clk" data-start="{s}" data-duration="1" data-track-index="5">{stamp}</span>')

html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: #8a8f94; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; }}
      .scene {{ position: absolute; inset: 0; }}
      .veh {{ position: absolute; left: 510px; top: 150px; width: 900px; height: 900px; perspective: 1600px; z-index: 2; }}
      .body {{ width: 900px; height: 900px; transform-origin: 50% 100%; }}
      .plate text.pl-main {{ font-family: "Oswald"; font-weight: 700; }}
      .plate text.pl-top {{ font-family: "Inter"; font-weight: 700; }}
      .dusk {{ position: absolute; inset: 0; background: rgba(12, 18, 34, 0.55); z-index: 3; }}
      .stamp {{ position: absolute; left: 40px; top: 32px; font-family: "JetBrains Mono"; font-size: 26px;
               color: #f2f2f2; text-shadow: 0 0 4px #000; z-index: 5; }}
      .clk {{ position: absolute; right: 40px; top: 32px; font-family: "JetBrains Mono"; font-size: 26px;
             color: #f2f2f2; text-shadow: 0 0 4px #000; z-index: 5; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}"
         data-width="1920" data-height="1080">
      <svg id="lot" class="scene" viewBox="0 0 1920 1080" width="1920" height="1080" style="z-index:1">
        <defs>
          <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stop-color="#b9c6d1"/><stop offset="1" stop-color="#dfe4e8"/>
          </linearGradient>
          <linearGradient id="asphalt" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stop-color="#5e6266"/><stop offset="1" stop-color="#3d4043"/>
          </linearGradient>
        </defs>
        <rect width="1920" height="300" fill="url(#sky)"/>
        <rect x="0" y="170" width="1920" height="130" fill="#8c8270"/>
        {''.join(f'<rect x="{x}" y="190" width="150" height="110" fill="#6e6658"/><rect x="{x+10}" y="200" width="130" height="90" fill="#7b8691"/>' for x in range(60, 1900, 240))}
        <polygon points="0,1080 1920,1080 1920,300 0,300" fill="url(#asphalt)"/>
        <polygon points="930,300 990,300 1240,1080 680,1080" fill="#4a4e52"/>
        {''.join(f'<polygon points="{957-2*k},{300+k*70} {963+2*k},{300+k*70} {964+3*k},{330+k*70} {956-3*k},{330+k*70}" fill="#e9d36a" opacity="0.8"/>' for k in range(0, 11))}
        <polygon points="560,300 600,300 120,1080 20,1080" fill="#e8e8e8" opacity="0.6"/>
        <polygon points="1320,300 1360,300 1900,1080 1800,1080" fill="#e8e8e8" opacity="0.6"/>
      </svg>
      {''.join(vehicles)}
      {''.join(overlays)}
      <div id="stamp" class="stamp">DOCK CAM 01 · DOOR 1</div>
      {''.join(clock)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {''.join(tweens)}
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""
(HERE / "index.html").write_text(html)

with open(HERE / "ground_truth.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"{len(rows)} vehicles, {total}s")
