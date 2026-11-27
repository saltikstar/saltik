from pathlib import Path
import re,json
P=Path(__file__).resolve().parent
S=(P.parent/'index.html').read_text(encoding='utf-8')
M=json.loads((P/'manifest.json').read_text(encoding='utf-8'))
OUT=P/'generated';OUT.mkdir(exist_ok=True)
H=re.search(r'<head>(.*?)</head>',S,re.S).group(1)
B=re.search(r'<body[^>]*>(.*?)</body>',S,re.S).group(1)
PREFIX='https://raw.githack.com/saltikstar/saltik/'+M['source']+'/siteai/elitedentalclinic/assets/'
def assets(s): return re.sub(r"""(["'])assets/""",lambda m:m[1]+PREFIX,s)
def put(n,s): (OUT/n).write_text(assets(s)+'\n',encoding='utf-8')
def extract(tag,id):
    start=re.search(r'<'+tag+r'\b[^>]*\bid="'+re.escape(id)+r'"[^>]*>',B)
    if not start: raise ValueError(id)
    depth=0
    for m in re.finditer(r'</?'+tag+r'\b[^>]*>',B[start.start():]):
        depth+= -1 if m[0].startswith('</') else 1
        if depth==0:return B[start.start():start.start()+m.end()]
    raise ValueError(id)
scripts=re.findall(r'<script\b[^>]*>.*?</script>',B,re.S)
def clean(s):return re.sub(r'<script\b[^>]*>.*?</script>','',s,flags=re.S)
styles=re.findall(r'<style\b[^>]*>.*?</style>',H,re.S)
# Remove standalone document reset; scope root theme to Tilda page only after inspecting its actual DOM.
styles=[x for x in styles if x!='<style>body{margin:0;}</style>']
put('00-global.html','\n'.join(styles))
for block in M['blocks']:
    markup=clean(extract(block['tag'],block['id']))
    if block['id']=='edc-site-header':
        markup='<a class="edc-skip-link" href="#edc-main">Перейти к содержанию</a>\n'+markup
    if block['id']=='edc-gnathology-hero':
        markup='<div id="edc-main" tabindex="-1">'+markup+'</div>'
    put(block['file'],markup)
put('13-booking.html',clean(extract('dialog','edc-booking')))
put('14-scripts.html','\n'.join(scripts))
meta=re.findall(r'<(?:meta|link)\b[^>]*>',H)
meta=[x for x in meta if re.search(r'name="description"|rel="canonical"|property="og:|name="twitter:',x)]
put('head-seo.html','\n'.join(meta+re.findall(r'<script type="application/ld\+json"[^>]*>.*?</script>',H,re.S)))
body='\n'.join((OUT/x['file']).read_text() for x in M['blocks'])+(OUT/'13-booking.html').read_text()
ids=re.findall(r'\bid="([^"]+)"',body)
assert len(ids)==len(set(ids)), 'Duplicate IDs'
assert set(re.findall(r'href="#([^"]+)"',body))<=set(ids), 'Missing anchors'
assert len(scripts)==10
print('Generated',len(M['blocks']),'content blocks; grouped sections still require parity testing')
