from zipfile import ZipFile
from lxml import etree
from collections import Counter
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with ZipFile(r'C:\Users\enosh\Downloads\TSB Downloads\CaptionAI - Growth Marketing - Groq(LLaMA 3.3-70B).docx') as z:
 r=etree.fromstring(z.read('word/document.xml')); ps=r.xpath('//w:p',namespaces=ns)
 for i in [0,1,2,5,17,22,23,36,37,38,62,64,66,79,114,117,132,140,156,162,300,442]:
  p=ps[i]; print(i,etree.tostring(p).decode().split('>')[0] if False else '')
  print('pPr',etree.tostring(p.find('w:pPr',ns)).decode() if p.find('w:pPr',ns) is not None else '')
  print('runs',[(x.xpath('string(w:t)',namespaces=ns),etree.tostring(x.find('w:rPr',ns)).decode() if x.find('w:rPr',ns) is not None else '') for x in p.findall('w:r',ns)][:3])
 print('HEADER',z.read('word/header1.xml').decode())
 print('STYLE',z.read('word/styles.xml').decode()[:4000])
