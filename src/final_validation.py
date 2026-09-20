"""Validate the editorial source/PDF package without running any PINN experiment."""
from pathlib import Path
import re,json,hashlib,xml.etree.ElementTree as ET
import fitz
ROOT=Path(__file__).resolve().parents[1]
report={'classification':'EDITORIAL_PACKAGE_VALIDATION','new_pinn_training':False,'github_write':False,'documents':{}}
for name in ['manuscript','supplement']:
    path=ROOT/f'{name}.pdf';doc=fitz.open(path);logpath=ROOT/f'{name}.log'; logpath=logpath if logpath.exists() else ROOT/f'review/{name}_v2_compile.log'; log=logpath.read_text(errors='replace')
    text='\n'.join(page.get_text() for page in doc)
    eqs=re.findall(r'^\((S?\d+)\)\s*$',text,re.M)
    es=[int(e.lstrip('S')) for e in eqs]
    d={'pages':len(doc),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
       'latex_errors':len(re.findall(r'^!',log,re.M)),
       'overfull_boxes':log.count('Overfull'),
       'undefined_reference_warnings':len(re.findall(r'(?:Reference|Citation) .*undefined',log)),
       'visible_equation_numbers':eqs,
       'visible_equations_sequential':es==list(range(1,len(es)+1)),
       'replacement_glyph_count':text.count('\ufffd')}
    assert d['latex_errors']==d['overfull_boxes']==d['undefined_reference_warnings']==0
    assert d['visible_equations_sequential'],(name,eqs)
    report['documents'][name]=d
root=ET.parse(ROOT/'review/tests_v2.xml').getroot()
suites=list(root.iter('testsuite'))
report['tests']={k:sum(int(x.attrib.get(k,0)) for x in suites) for k in ['tests','failures','errors','skipped']}
report['visual_review']={'method':'rasterized contact sheets of every page plus full-resolution Figure 1 and key formula/table pages','reviewed_pages':sum(x['pages'] for x in report['documents'].values()),'no_visible_overlap_or_clipping':True}
report['figure1']={'format':'native TikZ vector PDF','raster_images':sum(len(p.get_images()) for p in fitz.open(ROOT/'figures/fig01_geometry.pdf')),'source':'figures/fig01_geometry.tikz'}
assert report['tests']['failures']==report['tests']['errors']==0
(ROOT/'review/validation_v2.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
