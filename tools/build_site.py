# Builds the standalone, password-protected GitHub Pages version of the trainer.
# usage: python3 build_site.py <source index.html> <password> <out dir>
import base64, os, re, sys, json, secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

src, pw, out = sys.argv[1], sys.argv[2], sys.argv[3]
FS = '/tmp/claude-0/-home-claude/16ce2008-663e-5a03-8c35-c560387555d3/scratchpad/fonts/node_modules/@fontsource'
ABC = '/tmp/abc/node_modules/abcjs/dist/abcjs-basic-min.js'
s = open(src, encoding='utf8').read()

# 0. main script -> Safari 12 syntax (older iPads)
import subprocess
ESB='/tmp/claude-0/-home-claude/16ce2008-663e-5a03-8c35-c560387555d3/scratchpad/esb/node_modules/.bin/esbuild'
i=s.rindex('<script>'); j=s.rindex('</script>')
js=subprocess.run([ESB,'--loader=js','--target=safari12'],input=s[i+8:j].encode(),capture_output=True,check=True).stdout.decode()
s=s[:i+8]+js+s[j:]

# 1. abcjs inline
tag = '<script src="https://cdn.jsdelivr.net/npm/abcjs@6.4.4/dist/abcjs-basic-min.js"></script>'
assert s.count(tag) == 1
abc = open(ABC, encoding='utf8').read().replace('</script', '<\\/script')
s = s.replace(tag, '<script>' + abc + '</script>')

# 2. fonts inline (latin + cyrillic subsets with unicode-range)
faces = []
for fam, weights in (('unbounded', (500, 700)), ('golos-text', (400, 500, 600))):
    for w in weights:
        css = open(f'{FS}/{fam}/{w}.css', encoding='utf8').read()
        for name, block in re.findall(r'/\* ([\w-]+) \*/\s*(@font-face\s*{[^}]*})', css):
            if not re.search(r'-(latin|cyrillic)-\d+-normal$', name):
                continue
            f = re.search(r'url\(\./files/([^)]+\.woff2)\)', block).group(1)
            b64 = base64.b64encode(open(f'{FS}/{fam}/files/{f}', 'rb').read()).decode()
            block = re.sub(r'src:[^;]*;', f"src:url(data:font/woff2;base64,{b64}) format('woff2');", block)
            faces.append(block)
assert len(faces) == 10, len(faces)
links = re.findall(r'<link rel="(?:preconnect|stylesheet)" href="https://fonts\.(?:googleapis|gstatic)[^>]*>\n?', s)
assert len(links) == 2, links
for l in links: s = s.replace(l, '')
s = s.replace('<title>', '<style>' + '\n'.join(faces) + '</style>\n<title>', 1)
s = s.replace('<html>', '<html lang="ru">', 1)
assert 'googleapis' not in s and 'jsdelivr' not in s

# 3. encrypt
salt, iv = secrets.token_bytes(16), secrets.token_bytes(12)
ITER = 250000
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(pw.encode())
ct = AESGCM(key).encrypt(iv, s.encode('utf8'), None)
payload = {'salt': base64.b64encode(salt).decode(), 'iv': base64.b64encode(iv).decode(), 'iter': ITER,
           'ct': base64.b64encode(ct).decode()}

os.makedirs(out, exist_ok=True)
loader = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'loader.html'), encoding='utf8').read()
loader = loader.replace('/*PAYLOAD*/null', json.dumps(payload))
open(os.path.join(out, 'index.html'), 'w', encoding='utf8').write(loader)
print('ok', len(s), 'plain;', len(loader), 'site')
