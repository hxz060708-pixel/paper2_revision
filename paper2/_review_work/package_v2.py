from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'paper2_审稿意见'/'第二版_结合模板'
REV=OUT/'paper2_修改副本'
ZIP=ROOT/'paper2_审稿意见'/'paper2_第一份审稿与修改包_第二版.zip'
files=list(OUT.glob('*.docx'))+[OUT/'00_阅读说明.txt',OUT/'paper2_修改对照.diff']
files += [REV/'paper2.tex',REV/'ref2.bib',REV/'paper2.pdf']
files += sorted(p for p in (REV/'figs').rglob('*') if p.is_file())
assert len(list(OUT.glob('*.docx')))==2
with ZipFile(ZIP,'w',ZIP_DEFLATED) as z:
    for f in files:
        z.write(f,arcname=str(Path('第二版_结合模板')/f.relative_to(OUT)))
with ZipFile(ZIP) as z:
    assert z.testzip() is None
print(json.dumps(dict(zip=str(ZIP),bytes=ZIP.stat().st_size,files=len(files)),ensure_ascii=False))
