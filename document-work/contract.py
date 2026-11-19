from pathlib import Path
from zipfile import ZipFile
from lxml import etree
import hashlib,json
p=Path(r'C:\Users\enosh\Downloads\TSB Downloads\CaptionAI - Growth Marketing - Groq(LLaMA 3.3-70B).docx')
w=Path('document-work'); ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with ZipFile(p) as z:
 inventory={n:{'bytes':len(z.read(n)),'sha256':hashlib.sha256(z.read(n)).hexdigest(),'policy':'editable' if n in ['word/document.xml','word/_rels/document.xml.rels','[Content_Types].xml'] else 'preserve'} for n in z.namelist()}
 (w/'package-inventory.json').write_text(json.dumps(inventory,indent=2))
 r=etree.fromstring(z.read('word/document.xml'))
 print('tables',len(r.xpath('//w:tbl',namespaces=ns)),'fields',r.xpath('//w:instrText/text()',namespaces=ns),'controls',len(r.xpath('//w:sdt',namespaces=ns)))
(w/'artifact.md').write_text(f'''# CaptionAI template contract
Reference: {p}
SHA256: {hashlib.sha256(p.read_bytes()).hexdigest()}
Reference render: reference.pdf and reference-render/page-1.png through page-21.png. Word native PDF export used after packaged render_docx.py failed because bundled LibreOffice is absent on Windows.
One portrait Letter section, 12240 x 15840 twips; margins 1440 all sides; header/footer distances 576 twips. Preserve section XML and header exactly.
Typography: Cambria body 11 pt, black, 4 pt before/after; title Cambria bold 20 pt centered, 24 pt before/8 pt after; Heading1 Cambria black 16 pt, 18 pt before/6 pt after; Heading2 14 pt, 12 pt before/6 pt after; activity Heading3 12 pt black. Source paragraph indices 0,1,2,5,37,64,114,140 define these roles. All source styles remain unchanged.
Code pattern: source paragraph 162, Courier New 7.5 pt with syntax colors d2a8ff, c9d1d9, 121314 background; command pattern source 117 Cambria 10 pt white on 121314. Reuse code block pattern with safe line lengths and original colors.
Lists: source paragraph 38 real numId 2, left 720, hanging 360; preserve numbering part. Bold activity lead-ins. No source tables or data model.
Recurring header: SmartBridge left and Skill Wallet right. Preserve header XML, relationships and media byte-for-byte. No footer or page-number field.
Flow: project title and description, three scenarios; technical architecture diagram and prerequisites; six-milestone workflow; detailed milestone activities; setup commands and code excerpts; deployment and verification; project UI walkthrough; conclusion.
Editable slots: word/document.xml body paragraphs indexed 0..445, including screenshots and code examples. Rewrite subject matter for CodeMate AI; clone original paragraph and drawing patterns as needed. All CaptionAI/Groq/Flask-specific figures and links are removed from visible body, replaced by CodeMate architecture and actual UI screenshots. Original unused media remain preserved in package; new figures get new relationships. No invented provider-console screenshots. Page breaks may be adjusted for new text length while retaining original page geometry and typography.
Package inventory: package-inventory.json. All parts except main body, document relationships and content types are preserve-only. Append image relationships; retain original relationships. Source body sample paragraphs remain the authoritative style prototypes. Link styling uses original blue underlined hyperlink run properties.
Fidelity gate: compare every preserved part hash, section geometry, original reference hash, all headings and output pages. Final native Word render must have no overflow, orphaned headings, or unintended blank pages. Reflow is intentional because content and illustrations differ.
''',encoding='utf-8')
