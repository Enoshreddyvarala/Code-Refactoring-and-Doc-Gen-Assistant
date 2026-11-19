import pypdfium2 as pdfium
from PIL import Image,ImageDraw
from pathlib import Path
pdf=pdfium.PdfDocument('document-work/reference.pdf'); print('Pages',len(pdf))
out=Path('document-work/reference-render'); out.mkdir(exist_ok=True)
for i,p in enumerate(pdf):
 p.render(scale=1).to_pil().save(out/f'page-{i+1}.png')
for k in range(0,len(pdf),6):
 canvas=Image.new('RGB',(1224,3*812),'#cccccc')
 for j in range(k,min(k+6,len(pdf))):
  im=Image.open(out/f'page-{j+1}.png'); canvas.paste(im,((j-k)%2*612,(j-k)//2*812))
 canvas.save(out/f'contact-{k//6+1}.png')

