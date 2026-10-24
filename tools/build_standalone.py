#!/usr/bin/env python3
"""한 파일 버전 만들기 — stage_3d.html → RESONA_무대3D_더블클릭.html

stage_3d.html 은 lib/ 의 three.js·폰트를 불러와서 서버(시작.command)로 열어야 한다.
이 스크립트는 three.js 모듈과 네온 폰트를 HTML 안에 넣어서, 파일 하나만 더블클릭해도
크롬에서 열리는 버전을 만든다. stage_3d.html 을 고친 뒤 꼭 다시 돌릴 것.

실행 (stage_sim 폴더에서):
    python3 tools/build_standalone.py
"""
import base64
import os
import re
import sys

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # stage_sim 폴더
SRC = os.path.join(D, 'stage_3d.html')
OUT = os.path.join(D, 'RESONA_무대3D_더블클릭.html')


def main():
    src = open(SRC, encoding='utf-8').read()

    # 1) three.js + 부속 모듈 → <script type="text/plain" data-mod="..."> 블록
    mods = {'three': 'lib/three/build/three.module.js'}
    for sub in ['controls', 'postprocessing', 'shaders']:
        for f in sorted(os.listdir(os.path.join(D, 'lib/three/addons', sub))):
            if f.endswith('.js'):
                mods[f'three/addons/{sub}/{f}'] = f'lib/three/addons/{sub}/{f}'
    blocks = []
    for spec, path in mods.items():
        code = open(os.path.join(D, path), encoding='utf-8').read()
        sub = spec.split('/')[2] if spec != 'three' else ''
        # blob 주소에선 상대 경로가 안 풀리므로 importmap 이름으로 바꿈
        code = re.sub(r"from '\./([^']+)'", lambda m: f"from 'three/addons/{sub}/{m.group(1)}'", code)
        code = re.sub(r"from '\.\./([^']+)'", lambda m: f"from 'three/addons/{m.group(1)}'", code)
        if '</script' in code.lower():
            sys.exit(f'{spec} 안에 </script 가 있어 넣을 수 없음')
        blocks.append(f'<script type="text/plain" data-mod="{spec}">\n{code}\n</script>')

    loader = """<script>
// 넣어 둔 모듈들을 blob 주소로 바꿔 importmap 을 만든다 — 서버 없이 파일 더블클릭으로 열리게
(()=>{ const map = {imports:{}};
  document.querySelectorAll('script[data-mod]').forEach(s=>{ map.imports[s.dataset.mod] = URL.createObjectURL(new Blob([s.textContent], {type:'text/javascript'})); });
  const im = document.createElement('script'); im.type = 'importmap'; im.textContent = JSON.stringify(map); document.currentScript.after(im); })();
</script>"""
    src, n = re.subn(r'<script type="importmap">.*?</script>',
                     lambda m: '\n'.join(blocks) + '\n' + loader, src, count=1, flags=re.S)
    if n != 1:
        sys.exit('stage_3d.html 에서 importmap 을 못 찾음')

    # 2) 네온 폰트 → data URI 로 넣은 <style>
    css = open(os.path.join(D, 'lib/fonts/fonts.css'), encoding='utf-8').read()

    def datauri(m):
        b = open(os.path.join(D, 'lib/fonts', m.group(1)), 'rb').read()
        return 'url(data:font/woff2;base64,' + base64.b64encode(b).decode() + ')'
    css = re.sub(r'url\(([^)]+\.woff2)\)', datauri, css)
    src, n = re.subn(r'<link href="lib/fonts/fonts.css" rel="stylesheet">[^\n]*',
                     lambda m: '<style>/* 네온 폰트 8종 (내장) */\n' + css + '\n</style>', src, count=1)
    if n != 1:
        sys.exit('stage_3d.html 에서 폰트 링크를 못 찾음')

    # 3) 안내 문구를 한 파일 버전에 맞게
    src = re.sub(r'  - three\.js 0\.160 · 네온 폰트 = lib/[^\n]*',
                 '  - 한 파일 버전: three.js 0.160 · 네온 폰트를 이 파일 안에 넣음 → 더블클릭만으로 열림 (서버·인터넷 불필요). 원본 = stage_3d.html',
                 src, count=1)
    src = re.sub(r"el\.textContent='3D 엔진을 못 불러왔어요\.[^']*';",
                 "el.textContent='3D 엔진을 못 불러왔어요. 크롬 최신 버전으로 열어 주세요.';", src, count=1)

    open(OUT, 'w', encoding='utf-8').write(src)
    print(f'만듦: {os.path.basename(OUT)} ({len(src)/1e6:.2f} MB)')


if __name__ == '__main__':
    main()
