from pathlib import Path
import subprocess,json,re
ROOT=Path(__file__).resolve().parents[2];WORK=Path(__file__).resolve().parent;REV=ROOT/'filally_22/paper2'
for stem in ['paper2','paper2_clean']:
    for args in [['pdflatex','-interaction=nonstopmode','-halt-on-error',stem+'.tex'],['bibtex',stem],['pdflatex','-interaction=nonstopmode','-halt-on-error',stem+'.tex'],['pdflatex','-interaction=nonstopmode','-halt-on-error',stem+'.tex']]:
        r=subprocess.run(args,cwd=REV,capture_output=True)
        if r.returncode:
            print(r.stdout.decode('utf-8',errors='replace')[-5000:]);raise SystemExit(r.returncode)
    log=(REV/(stem+'.log')).read_text(encoding='utf-8',errors='replace')
    issues=[x for x in log.splitlines() if any(y in x for y in ['Overfull','undefined','multiply defined','Output written'])]
    print(stem,issues,flush=True)
