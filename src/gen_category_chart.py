# Regenerate the static "how each category fails" chart in part4.html from the
# RECORD array in part7_js.html, so the figure can never drift from the data.
# The interactive bar is computed from RECORD at runtime; this computes the
# same aggregates at build time and emits the SVG between the GENERATED markers.
import re, sys

FAM_OF = {
    "noverifier": "demand", "integration": "demand", "liability": "demand",
    "misaligned": "economics", "friction": "economics", "exclusion": "economics",
    "political": "institutional", "coordination": "institutional", "enforcement": "institutional",
    "governance": "temporal", "lockin": "temporal",
}
FAM_ORDER = ["demand", "economics", "institutional", "temporal"]
FAM_COLOR = {"demand": "#B4472E", "economics": "#8A6D1F",
             "institutional": "#3D5A80", "temporal": "#4A6B4F"}
KIND_ORDER = ["national", "govlogin", "tech", "framework", "consortium", "closed"]
KIND_LABEL = {"national": "National scheme", "govlogin": "Public-service login",
              "tech": "Protocol or product", "framework": "Framework or rule",
              "consortium": "Private consortium", "closed": "Closed-loop"}

whole = open("part7_js.html").read()
a = whole.index("const RECORD = [")
js = whole[a:whole.index("];", a)]
entry_re = re.compile(
    r'\{p:"(?:[^"\\]|\\.)*",\s*k:"(\w+)",\s*w:"[^"]*",\s*y:\d+,\s*m:\d,\s*o:"(\w+)",\s*'
    r't:\[((?:\["\w+",\d\],?\s*)*)\]', re.S)
entries = entry_re.findall(js)
declared = js.count('{p:"')
if len(entries) != declared:
    sys.exit(f"gen_category_chart: parsed {len(entries)} of {declared} RECORD entries")

stats = {k: {"n": 0, "worked": 0, "decided": 0,
             "fam": {f: 0 for f in FAM_ORDER}, "tags": []} for k in KIND_ORDER}
for kind, outcome, tags in entries:
    st = stats[kind]
    st["n"] += 1
    if outcome not in ("pending", "uncertain"):
        st["decided"] += 1
        if outcome == "working":
            st["worked"] += 1
    for tag, wt in re.findall(r'\["(\w+)",(\d)\]', tags):
        st["fam"][FAM_OF[tag]] += 1
        st["tags"].append((tag, int(wt)))

BAR_X, BAR_W, ROW_H, ROW0 = 212, 421, 48, 26
rows = []
for i, kind in enumerate(KIND_ORDER):
    st = stats[kind]
    total = sum(st["fam"].values())
    y = ROW0 + ROW_H * i
    g = [f'<g transform="translate(0,{y})">',
         f'  <text x="0" y="12" class="yl">{KIND_LABEL[kind]}</text>'
         f'<text x="0" y="25" class="ys">{st["n"]} programs</text>']
    if total <= 1:
        note = ("no failure tags at all" if total == 0 else
                "one contributing tag between them" if st["tags"][0][1] == 1 else
                "one tag between them")
        g.append(f'  <rect x="{BAR_X}" y="0" width="{BAR_W}" height="26" fill="#F3F3EF" stroke="#C6C6BD"/>')
        g.append(f'  <text x="{BAR_X + 10}" y="17" class="ys">{note}</text>')
    else:
        x = BAR_X
        fams = [f for f in FAM_ORDER if st["fam"][f] > 0]
        for j, fam in enumerate(fams):
            pct = round(100 * st["fam"][fam] / total)
            w = BAR_X + BAR_W - x if j == len(fams) - 1 else round(BAR_W * st["fam"][fam] / total)
            g.append(f'  <rect x="{x}" y="0" width="{w}" height="26" fill="{FAM_COLOR[fam]}"/>')
            if pct >= 10:
                g.append(f'  <text x="{x + 8}" y="17" class="yb">{pct}</text>')
            x += w
    if st["decided"]:
        pct = round(100 * st["worked"] / st["decided"])
        fill = ' fill="#B4472E"' if pct == 0 else ' fill="#4A6B4F"' if pct == 100 else ""
        g.append(f'  <text x="648" y="17" class="yl"{fill}>{pct}%</text>')
    else:
        g.append('  <text x="648" y="17" class="ys">&mdash;</text>'.replace("&mdash;", "n/a"))
    g.append("</g>")
    rows.append("\n".join(g))

legend_y = ROW0 + ROW_H * (len(KIND_ORDER) - 1) + 42
height = legend_y + 19
svg = f'''<svg viewBox="0 0 860 {height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Failure family mix and success rate by category of program, computed from the record. National schemes fail institutionally and over time; protocols and frameworks fail on the demand side; consortium and closed-loop programs carry almost no failure tags.">
<style>
.yl{{font-family:"IBM Plex Sans",sans-serif;font-size:11px;font-weight:600;fill:#16181D}}
.ys{{font-family:"IBM Plex Sans",sans-serif;font-size:9.5px;fill:#6A6F79}}
.yh{{font-family:"IBM Plex Sans",sans-serif;font-size:9.5px;letter-spacing:.1em;font-weight:600;fill:#6A6F79}}
.yn{{font-family:"IBM Plex Mono",monospace;font-size:9.5px;fill:#6A6F79}}
.yb{{font-family:"IBM Plex Mono",monospace;font-size:9px;fill:#fff}}
</style>
<text x="0" y="12" class="yh">HOW EACH CATEGORY FAILS</text>
<text x="212" y="12" class="yh">SHARE OF ITS FAILURE TAGS</text>
<text x="648" y="12" class="yh">WORKED</text>

{chr(10).join(rows)}
<rect x="212" y="{legend_y}" width="12" height="9" fill="#B4472E"/><text x="228" y="{legend_y + 8}" class="yn">demand</text>
<rect x="288" y="{legend_y}" width="12" height="9" fill="#8A6D1F"/><text x="304" y="{legend_y + 8}" class="yn">cost and access</text>
<rect x="404" y="{legend_y}" width="12" height="9" fill="#3D5A80"/><text x="420" y="{legend_y + 8}" class="yn">institutional</text>
<rect x="504" y="{legend_y}" width="12" height="9" fill="#4A6B4F"/><text x="520" y="{legend_y + 8}" class="yn">over time</text>
</svg>'''

f = "part4.html"
src = open(f).read()
BEGIN = "<!-- GENERATED:category-chart -->"
END = "<!-- /GENERATED:category-chart -->"
a, b = src.find(BEGIN), src.find(END)
if a < 0 or b < 0:
    sys.exit("gen_category_chart: markers not found in part4.html")
src = src[:a + len(BEGIN)] + "\n" + svg + "\n" + src[b:]
open(f, "w").write(src)

decided = sum(s["decided"] for s in stats.values())
worked = sum(s["worked"] for s in stats.values())
print(f"category chart regenerated from RECORD: {len(entries)} entries, {worked} of {decided} decided worked")
