from zipfile import ZipFile
from lxml import etree
from pathlib import Path
p=Path(r'C:\Users\enosh\Downloads\TSB Downloads\CaptionAI - Growth Marketing - Groq(LLaMA 3.3-70B).docx')
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with ZipFile(p) as z:
 root=etree.fromstring(z.read('word/document.xml'))
 for i,para in enumerate(root.xpath('//w:p',namespaces=ns)):
  t=''.join(para.xpath('.//w:t/text()',namespaces=ns))
  print(i, t)
 Path('document-work/source.xml').write_bytes(z.read('word/document.xml'))
 print('PARTS',z.namelist())
 print('SECTIONS', [etree.tostring(s).decode() for s in root.xpath('//w:sectPr',namespaces=ns)])
