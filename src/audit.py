# Rasterise every figure and report any text glyph overlapping a stroked path,
# plus any element whose bounding box escapes the viewBox.
from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":1180,"height":1200})
    pg.goto("file:///home/claude/site/index.html"); pg.wait_for_timeout(2500)
    out = pg.evaluate("""() => {
      const rep=[];
      document.querySelectorAll('svg').forEach((svg,i)=>{
        const vb=svg.viewBox.baseVal;
        const texts=[...svg.querySelectorAll('text')];
        const marks=[...svg.querySelectorAll('path,line,rect')];
        // overflow check
        texts.forEach(t=>{
          let bb; try{bb=t.getBBox()}catch(e){return}
          if(bb.x+bb.width > vb.width+1 || bb.x < -1 || bb.y+bb.height > vb.height+1)
            rep.push({svg:i,type:'overflow',text:t.textContent.slice(0,45),
                      x:Math.round(bb.x),w:Math.round(bb.width),vw:vb.width});
        });
        // text over stroked path/line
        texts.forEach(t=>{
          let tb; try{tb=t.getBBox()}catch(e){return}
          marks.forEach(m=>{
            const st=getComputedStyle(m).stroke;
            if(st==='none'||!st) return;
            if(m.tagName==='rect' && getComputedStyle(m).fill!=='none') return;
            let mb; try{mb=m.getBBox()}catch(e){return}
            // only flag long thin marks (rules/curves), not boxes around text
            const thin = mb.height<6 || mb.width<6;
            const curve = m.tagName==='path' && mb.width>80 && mb.height>20;
            if(!(thin||curve)) return;
            const ox=Math.min(tb.x+tb.width,mb.x+mb.width)-Math.max(tb.x,mb.x);
            const oy=Math.min(tb.y+tb.height,mb.y+mb.height)-Math.max(tb.y,mb.y);
            if(ox>4&&oy>2) rep.push({svg:i,type:'cross',text:t.textContent.slice(0,45),
                                     mark:m.tagName, ox:Math.round(ox), oy:Math.round(oy)});
          });
        });
      });
      return rep;
    }""")
    # connectors must not pass through boxes
    cross = pg.evaluate('''() => {
      const rep=[];
      document.querySelectorAll('svg').forEach((svg,i)=>{
        const rects=[...svg.querySelectorAll('rect')].map(r=>({
          x:+r.getAttribute('x')||0, y:+r.getAttribute('y')||0,
          w:+r.getAttribute('width')||0, h:+r.getAttribute('height')||0}));
        [...svg.querySelectorAll('path')].forEach(p=>{
          const d=p.getAttribute('d')||'';
          const m=d.match(/^M(-?[\\d.]+) (-?[\\d.]+) L(-?[\\d.]+) (-?[\\d.]+)$/);
          if(!m) return;
          const [x1,y1,x2,y2]=m.slice(1).map(Number);
          rects.forEach(r=>{
            const insideX = Math.min(x1,x2) < r.x+r.w-1 && Math.max(x1,x2) > r.x+1;
            const insideY = Math.min(y1,y2) < r.y+r.h-1 && Math.max(y1,y2) > r.y+1;
            if(insideX && insideY) rep.push({svg:i, type:'connector crosses box', d, box:[r.x,r.y,r.w,r.h]});
          });
        });
      });
      return rep;
    }''')
    out = out + cross
    for r in out: print(json.dumps(r))
    print("issues:",len(out))
    b.close()
