"""Lightweight source audit. Counts are approximate, not a grammar certificate."""
from pathlib import Path
import json,re,sys,platform
import numpy as np, pandas as pd, matplotlib
R=Path(__file__).resolve().parents[1]
s=(R/'manuscript.tex').read_text().split(r'\section*{Acknowledgments}')[0]
# Count prose lines only; the manuscript uses approximately one sentence per line.
# Discard math/figure/table blocks and retain captions in a separate visual audit.
s=re.sub(r'\\begin\{(equation\*?|align\*?|figure|table)\}.*?\\end\{\1\}', '',s,flags=re.S)
s=s.split(r'\begin{abstract}',1)[1]
rows=[]
for line in s.splitlines():
 if not line.strip() or line.lstrip().startswith(('%','\\')):continue
 line=re.sub(r'\$[^$]*\$', ' FORMULA ', line)
 line=re.sub(r'\\\([^)]*\\\)', ' FORMULA ', line)
 line=re.sub(r'\\(?:cite|ref|eqref|label|path|url)\{[^}]*\}', ' REFERENCE ', line)
 line=re.sub(r'\\[A-Za-z]+(?:\{[^}]*\})?', ' TOKEN ', line)
 for sent in re.split(r'(?<=[.!?])\s+(?=[A-Z])',line):
  words=re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)*|\d+(?:\.\d+)?",sent)
  if len(words)>3:rows.append({'words':len(words),'sentence':sent.strip()})
report={'classification':'APPROXIMATE_PROSE_LINE_AUDIT','sentence_like_units':len(rows),
 'units_at_most_20_words':sum(x['words']<=20 for x in rows),
 'fraction_at_most_20_words':sum(x['words']<=20 for x in rows)/len(rows),
 'median_words':float(np.median([x['words'] for x in rows])),
 'longer_units':[x for x in rows if x['words']>20],
 'note':'Math/citation macros replaced with tokens; captions, equations, tables, acknowledgments and bibliography excluded.'}
(R/'review/sentence_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
env={'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'pandas':pd.__version__,'matplotlib':matplotlib.__version__,'purpose':'revision-time data reconstruction and algebraic tests, not historical training'}
(R/'review/environment.json').write_text(json.dumps(env,indent=2))
print('Prose audit:',report['sentence_like_units'], 'units;',report['fraction_at_most_20_words'],'at most 20 approximate words')
for x in report['longer_units']:print(x['words'],x['sentence'])
