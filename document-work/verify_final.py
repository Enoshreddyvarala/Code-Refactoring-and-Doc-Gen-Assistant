from zipfile import ZipFile
from pathlib import Path
from lxml import etree as E
import hashlib,json
out=Path('CodeMate AI - Code Refactoring and Documentation Assistant.docx')
with ZipFile(out) as z:
 ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
 root=E.fromstring(z.read('word/document.xml'));text=' '.join(root.xpath('//w:t/text()',namespaces=ns))
 assert not any(s in text for s in ['CaptionAI','Groq','Flask','Ngrok'])
 assert len(root.xpath('//w:sectPr',namespaces=ns))==1
 inventory=json.loads(Path('document-work/package-inventory.json').read_text())
 preserved=[n for n,v in inventory.items() if v['policy']=='preserve']
 assert all(hashlib.sha256(z.read(n)).hexdigest()==inventory[n]['sha256'] for n in preserved)
 print('Verified:',len(preserved),'unchanged template parts;',len(text.split()),'words;',out.stat().st_size,'bytes')
