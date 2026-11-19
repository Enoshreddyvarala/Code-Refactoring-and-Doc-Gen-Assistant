from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from copy import deepcopy
from lxml import etree as E
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
ROOT=Path.cwd(); WORK=ROOT/'document-work'
REF=Path(r'C:\Users\enosh\Downloads\TSB Downloads\CaptionAI - Growth Marketing - Groq(LLaMA 3.3-70B).docx')
OUT=ROOT/'CodeMate AI - Code Refactoring and Documentation Assistant.docx'
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'; R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
ns={'w':W,'r':R,'a':'http://schemas.openxmlformats.org/drawingml/2006/main','wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}
q=lambda t:'{'+W+'}'+t
with ZipFile(REF) as z: parts={n:z.read(n) for n in z.namelist()}
root=E.fromstring(parts['word/document.xml']); body=root.find('w:body',ns); originals=root.xpath('//w:p',namespaces=ns); section=deepcopy(body.find('w:sectPr',ns)); rels=E.fromstring(parts['word/_rels/document.xml.rels'])
for child in list(body):body.remove(child)
roles={'title':0,'h1':1,'h2':5,'h3':114,'p':2,'bold':140,'list':38,'code':162,'cmd':117}
def para(role,text):
 template=originals[roles[role]]; p=E.Element(q('p')); prop=deepcopy(template.find('w:pPr',ns)); p.append(prop)
 if role in ['h1','h2','h3','title']:E.SubElement(prop,q('keepNext')).set(q('val'),'1')
 rpr=deepcopy(template.find('w:r/w:rPr',ns))
 if role=='list':
  for b in rpr.findall('w:b',ns)+rpr.findall('w:bCs',ns):rpr.remove(b)
 if role=='code':
  rpr.find('w:color',ns).set(q('val'),'c9d1d9');sp=prop.find('w:spacing',ns);sp.set(q('before'),'0');sp.set(q('after'),'0');sp.set(q('line'),'326')
 for i,s in enumerate(text.split('**')):
  if not s:continue
  r=E.SubElement(p,q('r'));rp=deepcopy(rpr)
  if i%2:E.SubElement(rp,q('b')).set(q('val'),'1')
  r.append(rp);t=E.SubElement(r,q('t'));t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=s
 body.append(p)
def page():
 p=E.SubElement(body,q('p'));pr=E.SubElement(p,q('pPr'));sp=E.SubElement(pr,q('spacing'));sp.set(q('after'),'0');sp.set(q('before'),'0');sp.set(q('line'),'20');sp.set(q('lineRule'),'exact');E.SubElement(E.SubElement(p,q('r')),q('br')).set(q('type'),'page')
def code(text):
 for line in text.strip('\n').split('\n'):para('code',line or ' ')
new_images={}
def pic(path,width=6.5):
 sample=next(p for p in originals if p.find('.//w:drawing',ns) is not None);p=deepcopy(sample)
 for child in list(p):
  if child.tag!=q('pPr') and child.find('.//w:drawing',ns) is None:p.remove(child)
 for pr in p.findall('w:pPr',ns):p.remove(pr)
 pr=E.Element(q('pPr'));E.SubElement(pr,q('jc')).set(q('val'),'center');p.insert(0,pr)
 path=Path(path);im=Image.open(path);cx=int(width*914400);cy=int(cx*im.height/im.width)
 rid='rIdCodeMate'+str(len(new_images)+1);name='word/media/codemate-'+str(len(new_images)+1)+'.png';new_images[name]=path.read_bytes()
 rr=E.SubElement(rels,'{http://schemas.openxmlformats.org/package/2006/relationships}Relationship');rr.set('Id',rid);rr.set('Type',R+'/image');rr.set('Target',name.replace('word/',''))
 p.find('.//a:blip',ns).set('{'+R+'}embed',rid)
 for el in p.findall('.//wp:extent',ns)+p.findall('.//a:ext',ns):el.set('cx',str(cx));el.set('cy',str(cy))
 for el in p.findall('.//a:srcRect',ns):el.getparent().remove(el)
 for el in p.findall('.//wp:docPr',ns):el.set('id',str(200+len(new_images)));el.set('name',path.name);el.set('descr',path.stem+' CodeMate AI illustration')
 body.append(p)
# Recreate the reference's simple architecture box-and-arrow treatment.
im=Image.new('RGB',(1500,500),'white');d=ImageDraw.Draw(im);f=ImageFont.truetype('C:/Windows/Fonts/calibri.ttf',28)
def box(x,y,w,h,text):
 d.rectangle((x,y,x+w,y+h),fill='#dce5ef',outline='#293341',width=2)
 for i,line in enumerate(text.split('\n')):
  bb=d.textbbox((0,0),line,font=f);d.text((x+(w-bb[2])/2,y+25+i*35),line,font=f,fill='black')
box(20,170,270,130,'React Frontend\nCode Workspace');box(440,170,300,130,'FastAPI Backend\nRoutes and Schemas');box(980,40,360,110,'AST and Black\nAnalysis and Validation');box(980,250,360,110,'Google Gemini API\nRefactor Explain Docs');box(440,380,300,100,'Environment\nAPI Key and Model')
import math
for a,b in [((290,235),(440,235)),((740,200),(980,95)),((740,260),(980,305)),((590,380),(590,300))]:
 d.line([a,b],fill='black',width=3);ang=math.atan2(b[1]-a[1],b[0]-a[0]);d.polygon([b,(b[0]-16*math.cos(ang-.4),b[1]-16*math.sin(ang-.4)),(b[0]-16*math.cos(ang+.4),b[1]-16*math.sin(ang+.4))],fill='black')
im.save(WORK/'architecture.png')
# Content is expressed as source-derived paragraph roles, with deliberate page boundaries.
content=(WORK/'report-content.txt').read_text(encoding='utf-8-sig')
for block in content.split('\n'):
 if not block:continue
 role,text=block.split('|',1)
 if role=='page':page()
 elif role=='pic':pic(WORK/text)
 elif role=='code':code(text.replace('\\n','\n'))
 else:para(role,text)
body.append(section)
parts['word/document.xml']=E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
parts['word/_rels/document.xml.rels']=E.tostring(rels,xml_declaration=True,encoding='UTF-8',standalone=True);parts.update(new_images)
with ZipFile(OUT,'w',ZIP_DEFLATED) as z:
 for name,data in parts.items():z.writestr(name,data)
inventory=json.loads((WORK/'package-inventory.json').read_text())
for name,info in inventory.items():
 if info['policy']=='preserve':assert hashlib.sha256(parts[name]).hexdigest()==info['sha256'],name
print(OUT);print('Preserved package parts verified. Paragraphs:',len(body.findall('w:p',ns)))
