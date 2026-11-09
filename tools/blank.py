# Blank manuscript sheets for the teacher: grand staff (treble + bass), equal bars,
# dashed line at the start of every beat, a dot on every second eighth.
# usage: python3 blank.py METER ABC_KEY "KEY_RU" out.pdf [pages=2] [systems=6] [bars=4] [staffsep=46] [sysstaffsep=58]
import sys, json
from playwright.sync_api import sync_playwright

meter, key, key_ru, out = sys.argv[1:5]
a = sys.argv[5:] + [None] * 5
PAGES = int(a[0] or 2); SYSTEMS = int(a[1] or 6); PER = int(a[2] or 4)
STAFFSEP = int(a[3] or 46); SYSSEP = int(a[4] or 58)
beats, unit = map(int, meter.split('/'))
FS = '/tmp/claude-0/-home-claude/16ce2008-663e-5a03-8c35-c560387555d3/scratchpad/fonts/node_modules/@fontsource/golos-text/files'
ABCJS = '/tmp/abc/node_modules/abcjs/dist/abcjs-basic-min.js'

bar = 'x%d' % beats
L = '1/4' if unit == 4 else '1/8'
lines = []
for _ in range(SYSTEMS):
    lines.append('[V:RH] ' + '|'.join([bar] * PER) + '|')
    lines.append('[V:LH] ' + '|'.join([bar] * PER) + '|')
abc = (f"X:1\nL:{L}\nM:{meter}\n%%staffsep {STAFFSEP}\n%%sysstaffsep {SYSSEP}\nK:{key}\n"
       "%%stretchlast 1\n%%staves {RH LH}\nV:RH clef=treble\nV:LH clef=bass\n" + '\n'.join(lines) + '\n')

pages = []
for i in range(PAGES):
    head = (f'<div class="head"><div><b>Название:</b> <span class="line"></span></div>'
            f'<div><b>{meter} · {key_ru}</b> &nbsp; Темп: <span class="small"></span></div></div>') if i == 0 else \
           f'<div class="cont">{meter} · {key_ru} · лист {i + 1}</div>'
    foot = ('<div class="foot">Пунктир — начало каждой доли ({b} в такте), точка — вторая восьмая доли. '
            'Ноту пишите у своего пунктира. Над нижним станом — буква аккорда (м / Б / 7), '
            'под ним — название баса (ре, ля, соль…).</div>').format(b=beats) if i == 0 else ''
    pages.append(f'<section class="pg">{head}<div class="paper"></div>{foot}</section>')

html = """<!doctype html><html><head><meta charset="utf-8">
<style>
@font-face{font-family:Golos;src:url(file://FS/golos-text-cyrillic-400-normal.woff2) format('woff2');}
@font-face{font-family:Golos;font-weight:600;src:url(file://FS/golos-text-cyrillic-600-normal.woff2) format('woff2');}
@page{size:A4;margin:10mm 10mm 8mm 10mm}
html,body{margin:0;padding:0;background:#fff;color:#000;font-family:Golos,sans-serif}
.pg{break-after:page}.pg:last-child{break-after:auto}
.head{display:flex;justify-content:space-between;align-items:flex-end;font-size:12.5pt;margin:0 2mm 2mm}
.head b{font-weight:600}
.line{display:inline-block;border-bottom:.6pt solid #000;min-width:62mm;height:5mm}
.small{display:inline-block;border-bottom:.6pt solid #000;min-width:22mm;height:5mm}
.cont{font-size:9pt;color:#555;margin:0 2mm 2mm}
.foot{font-size:8.5pt;color:#444;margin:1mm 2mm 0;line-height:1.35}
.paper svg{display:block}
</style></head><body>PAGES
<script src="file://ABCJS"></script>
<script>
const abc=ABC, BEATS=NBEATS, NS='http://www.w3.org/2000/svg';
document.querySelectorAll('.paper').forEach(div=>{
  ABCJS.renderAbc(div,abc,{add_classes:true,staffwidth:730,scale:1,paddingtop:0,paddingbottom:0,paddingleft:4,paddingright:4});
  const svg=div.querySelector('svg');
  const add=(tag,at)=>{const e=document.createElementNS(NS,tag);for(const k in at)e.setAttribute(k,at[k]);svg.appendChild(e);return e;};
  const sys={};
  svg.querySelectorAll('.abcjs-staff').forEach(st=>{const l=+/abcjs-l(\\d+)/.exec(st.getAttribute('class'))[1];(sys[l]=sys[l]||[]).push(st.getBBox());});
  Object.keys(sys).forEach(l=>{
    const st=sys[l].sort((a,b)=>a.y-b.y), top=st[0].y, bot=st[st.length-1].y+st[st.length-1].height;
    const bars=[...svg.querySelectorAll('.abcjs-bar.abcjs-l'+l)].map(b=>b.getBBox()).filter(b=>b.y<st[0].y+st[0].height+2).map(b=>b.x+b.width/2).sort((a,b)=>a-b);
    let x0=0; svg.querySelectorAll('.abcjs-l'+l+'.abcjs-clef,.abcjs-l'+l+'.abcjs-key-signature,.abcjs-l'+l+'.abcjs-time-signature').forEach(e=>{const b=e.getBBox(); x0=Math.max(x0,b.x+b.width);});
    const edges=[x0+6]; bars.forEach(x=>{ if(x-edges[edges.length-1]>20) edges.push(x); else edges[edges.length-1]=Math.max(edges[edges.length-1],x); });
    for(let i=0;i+1<edges.length;i++){
      const a=edges[i], z=edges[i+1], pad=Math.min(14,(z-a)*0.08), w=(z-a-pad-4)/BEATS;
      for(let k=0;k<BEATS;k++){
        const x=a+pad+k*w;
        add('line',{x1:x,x2:x,y1:top-6,y2:bot+6,stroke:'#8a8a8a','stroke-width':0.7,'stroke-dasharray':'3 3'});
        add('text',{x:x,y:top-10,'font-size':7.5,fill:'#9a9a9a','text-anchor':'middle','font-family':'Golos'}).textContent=k+1;
        st.forEach(s=>add('circle',{cx:x+w/2,cy:s.y+s.height+6,r:1.4,fill:'#7a7a7a'}));
      }
    }
  });
  const vb=svg.getBBox(); svg.setAttribute('viewBox',`${vb.x-2} ${vb.y-4} ${vb.width+4} ${vb.height+8}`);
  svg.setAttribute('width','190mm'); svg.removeAttribute('height'); svg.style.height='auto';
  div.style.height='auto'; div.style.overflow='visible';
  window.__h=(window.__h||[]).concat([[vb.width,vb.height]]);
});
document.title='ready';
</script></body></html>"""
html = (html.replace('FS', FS).replace('PAGES', ''.join(pages)).replace('ABCJS"', ABCJS + '"')
        .replace('const abc=ABC', 'const abc=' + json.dumps(abc)).replace('NBEATS', str(beats)))
open('/home/claude/blanks/_blank.html', 'w').write(html)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--allow-file-access-from-files'])
    pg = b.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file:///home/claude/blanks/_blank.html'); pg.wait_for_function("document.title==='ready'", timeout=15000)
    print('svg w,h:', pg.evaluate('window.__h'), errs)
    pg.pdf(path=out, format='A4', print_background=True, prefer_css_page_size=True)
print('ok', out)
