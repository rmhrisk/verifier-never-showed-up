#!/usr/bin/env python3
"""Pull the document structure out of the built index.html for the Word build.
   --figs also rasterises the inline SVGs (needs Playwright)."""
import re, json, html as H, sys, os, base64
D = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.abspath(os.path.join(D, '..', '..'))   # repo root: src/docx -> ..
IDX = os.path.join(SITE, 'index.html')
if not os.path.exists(IDX):
    IDX = os.path.abspath(os.path.join(D, '..', '..', 'index.html'))
assert os.path.exists(IDX), 'index.html not found; run from the repo'
h = open(IDX).read()
txt = lambda x: H.unescape(' '.join(re.sub(r'<[^>]+>', '', re.sub(r'<sup>.*?</sup>', '', x, flags=re.S)).split()))

if '--figs' in sys.argv:
    from playwright.sync_api import sync_playwright
    os.makedirs(f'{D}/figs', exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width':1400,'height':1000}, device_scale_factor=2)
        pg.goto('file://' + IDX); pg.wait_for_timeout(2600)
        for i, el in enumerate(pg.query_selector_all('figure .fig-frame svg')):
            el.screenshot(path=f'{D}/figs/fig{i:02d}.png')
        b.close()
    for i, m in enumerate(re.finditer(r'<img src="data:image/jpeg;base64,([^"]+)"', h)):
        open(f'{D}/figs/photo{i}.jpg', 'wb').write(base64.b64decode(m.group(1)))
    print('figures and photos written')

# sources, record, diagnostic, artifacts, and the block structure
json.dump([re.sub(r'\s+',' ',txt(x)) for x in re.findall(r'<li id="r\d+">(.*?)</li>', h, re.S)],
          open(f'{D}/sources.json','w'), indent=1)

# the body: every block the document needs, in document order
bodyhtml = h[h.index('<div class="wrap">'):h.index('<div class="quiz"')]
bodyhtml = re.sub(r'<script.*?</script>', '', bodyhtml, flags=re.S)
bodyhtml = re.sub(r'<nav class="rail".*?</nav>', '', bodyhtml, flags=re.S)
bodyhtml = re.sub(r'<div class="toc">.*?</div>\s*(?=<div class="part")', '', bodyhtml, flags=re.S)
blocks = []; figi = 0; photoi = 0
pat = re.compile(
  r'<div class="part">.*?<div class="eyebrow">(?P<part>.*?)</div>\s*<h2>(?P<ph>.*?)</h2>'
  r'|<h1>(?P<h1>.*?)</h1>|<p class="standfirst">(?P<sf>.*?)</p>|<p class="byline">(?P<by>.*?)</p>'
  r'|<p class="snapshot">(?P<snap>.*?)</p>|<h3>(?P<h3>.*?)</h3>|<h4>(?P<h4>.*?)</h4>'
  r'|<div class="thesis">(?P<thesis>.*?)</div>\s*(?=<p)|<blockquote><p>(?P<bq>.*?)</p></blockquote>'
  r'|<div class="lesson">.*?<p>(?P<lesson>.*?)</p>\s*</div>|<figure[^>]*>(?P<fig>.*?)</figure>'
  r'|<div class="record"(?P<record>)|<div class="scorecard"(?P<score>)|<p>(?P<p>.*?)</p>', re.S)
for m in pat.finditer(bodyhtml):
    g = m.groupdict()
    if g['part'] is not None: blocks.append({"t":"part","eyebrow":txt(g['part']),"title":txt(g['ph'])})
    elif g['h1'] is not None: blocks.append({"t":"title","v":txt(g['h1'])})
    elif g['sf'] is not None: blocks.append({"t":"standfirst","v":txt(g['sf'])})
    elif g['by'] is not None: blocks.append({"t":"byline","v":txt(g['by'])})
    elif g['snap'] is not None: blocks.append({"t":"snapshot","v":txt(g['snap'])})
    elif g['h3'] is not None:
        num = re.search(r'class="sn">(\d+)</span>', g['h3'])
        blocks.append({"t":"h3","n":num.group(1) if num else "","v":txt(re.sub(r'<span class="sn">.*?</span>','',g['h3']))})
    elif g['h4'] is not None: blocks.append({"t":"h4","v":txt(g['h4'])})
    elif g['thesis'] is not None:
        items=[{"claim":txt(li.group(1)),"refs":txt(li.group(2))} for li in
               re.finditer(r'<span class="tc">(.*?)</span>\s*<span class="tw">(.*?)</span>', g['thesis'], re.S)]
        blocks.append({"t":"thesis","items":items})
    elif g['bq'] is not None: blocks.append({"t":"quote","v":txt(g['bq'])})
    elif g['lesson'] is not None: blocks.append({"t":"lesson","v":txt(g['lesson'])})
    elif g['fig'] is not None:
        cap = re.search(r'<figcaption>(.*?)</figcaption>', g['fig'], re.S)
        c = txt(cap.group(1)) if cap else ""
        if '<svg' in g['fig']:
            blocks.append({"t":"figure","img":f"figs/fig{figi:02d}.png","cap":c}); figi += 1
        elif '<img' in g['fig']:
            for _ in re.finditer(r'<img ', g['fig']):
                blocks.append({"t":"strip" if photoi==0 and 'artifacts' in bodyhtml[max(0,m.start()-260):m.start()] else
                                    ("skip" if photoi<4 and 'artifacts' in bodyhtml[max(0,m.start()-260):m.start()] else "photo"),
                               "img":f"figs/photo{photoi}.jpg","cap":c}); photoi += 1
    elif g['record'] is not None: blocks.append({"t":"record"})
    elif g['score'] is not None: blocks.append({"t":"scorecard"})
    elif g['p'] is not None:
        v = txt(g['p'])
        if v: blocks.append({"t":"p","v":v})
# the first four photos are the artifact strip, rendered as one table
pn = 0
for bl in blocks:
    if bl['t'] in ('photo','strip') and bl.get('img','').startswith('figs/photo'):
        if pn < 4: bl['t'] = 'strip' if pn == 0 else 'skip'
        pn += 1
json.dump(blocks, open(f'{D}/content.json','w'), indent=1)
print(f'{len(blocks)} body blocks extracted')

# the artifact strip's own captions
am = re.search(r'<div class="artifacts[^"]*">(.*?)</div>\s*</div>', h, re.S)
if am:
    arts=[{"name":txt(x.group(2)),"desc":txt(x.group(3)),"src":txt(x.group(4)),"fail":txt(x.group(5))}
          for x in re.finditer(r'<figure>\s*<img[^>]*alt="([^"]*)"[^>]*>\s*<div class="cap"><b>(.*?)</b>(.*?)<i>(.*?)</i></div>\s*<div class="fail">(.*?)</div>', am.group(0), re.S)]
    cap = re.search(r'<figcaption>(.*?)</figcaption>', am.group(0), re.S)
    json.dump({"items":arts,"cap":txt(cap.group(1)) if cap else ""}, open(f'{D}/artifacts.json','w'), indent=1)
    print(f'{len(arts)} artifact captions extracted')

# the record, from the page's own JS data
js = h[h.index('const RECORD = ['):h.index('/* ============ RENDER')]
tagblk = h[h.index('const TAG = {'):h.index('const KIND = {')]
MODE = {m.group(1): m.group(2) for m in re.finditer(r'(\w+):\{f:"\w+", label:"([^"]+)"', tagblk)}
outblk = h[h.index('const OUTCOME = {'):h.index('};', h.index('const OUTCOME = {'))]
OUT = {m.group(1): m.group(2) for m in re.finditer(r'(\w+):\s*\{label:"([^"]+)"', outblk)}
rec = []
for c in re.split(r'\n \{p:"', js)[1:]:
    g = lambda k, d='': (re.search(k, c).group(1) if re.search(k, c) else d)
    tags = re.findall(r'\["(\w+)",(\d)\]', c[:c.index('n:"')])
    rec.append({'p': c[:c.index('"')], 'w': g(r'w:"([^"]*)"'), 'y': g(r'y:(\d+)'),
                'o': OUT.get(g(r'o:"(\w+)"'), '?'),
                'tags': [MODE[t] + ('' if w == '2' else ' (contributing)') for t, w in tags],
                'n': txt(re.search(r'n:"([^"]*)"', c).group(1))})
json.dump(rec, open(f'{D}/record.json', 'w'), indent=1)
print(f'{len(rec)} record rows extracted')

qs = [{'q': txt(m.group(1)), 's': txt(m.group(2))} for m in
      re.finditer(r'<div class="sc-q"[^>]*>\s*<p class="qt">(.*?)</p>\s*<p class="qs">(.*?)</p>', h, re.S)]
json.dump(qs, open(f'{D}/diagnostic.json','w'), indent=1)
print(f'sources and {len(qs)} questions extracted')
