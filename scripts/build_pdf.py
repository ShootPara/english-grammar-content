"""Build the reading/practice PDF and embedded-answer appendix from JSON only."""
import json, re, os, html
from pathlib import Path
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
    PageBreak, Table, TableStyle, KeepTogether, Flowable)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT/'GRAMMAR_BOOK_EDITED.json').read_text(encoding='utf8'))
OUT = ROOT/'output/pdf/English Grammar - Practice and Answers.pdf'
OUT.parent.mkdir(parents=True, exist_ok=True)
fontdir = Path(os.environ.get('GRAMMAR_FONT_DIR', 'C:/Windows/Fonts'))
for name, file in [('Body','arial.ttf'),('Bold','arialbd.ttf'),('Italic','ariali.ttf'),('BI','arialbi.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(fontdir/file)))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold',italic='Italic',boldItalic='BI')
NAVY=colors.HexColor('#183342'); TEAL=colors.HexColor('#087e83'); LIGHT=colors.HexColor('#eaf3f3')
W,H=A4; WIDTH=W-100
styles={}
def sty(name, **kw):
    styles[name]=ParagraphStyle(name,fontName='Body',fontSize=10,leading=14,textColor=NAVY,spaceAfter=5,**kw)
sty('body')
styles['small']=ParagraphStyle('small',parent=styles['body'],fontSize=8,leading=11,textColor=TEAL)
styles['h1']=ParagraphStyle('h1',parent=styles['body'],fontName='Bold',fontSize=24,leading=29,spaceAfter=16,keepWithNext=True)
styles['h2']=ParagraphStyle('h2',parent=styles['body'],fontName='Bold',fontSize=16,leading=21,spaceBefore=12,spaceAfter=10,keepWithNext=True)
styles['instruction']=ParagraphStyle('instruction',parent=styles['body'],fontName='Bold',spaceBefore=8,keepWithNext=True)
styles['cell']=ParagraphStyle('cell',parent=styles['body'],fontSize=9,leading=12,spaceAfter=2)
styles['key']=ParagraphStyle('key',parent=styles['body'],fontSize=9,leading=12,spaceAfter=7)
def p(t, s='body'):return Paragraph(t,styles[s])
def esc(t):return html.escape(t).replace('\n','<br/>').replace('\t',' &nbsp; ')
nodes={}
def index(n):
    nodes[n['id']]=n
    for c in n.get('children',[]):index(c)
    for row in n.get('rows',[]):
        for cell in row['cells']:
            for b in cell['blocks']:index(b)
for b in DATA['source_blocks']:index(b)
rendered=set(); item_labels={}; key_ids=[]
def rich(n):
    text=n.get('text',''); spans=n.get('formatting',[])
    cuts=sorted({0,len(text)}|{f[k] for f in spans for k in ['start','end']})
    chunks=[]
    for a,b in zip(cuts,cuts[1:]):
        t=esc(re.sub(r'_{26,}','_'*25,text[a:b])); marks={}
        for f in spans:
            if f['start']<=a and f['end']>=b:marks.update(f['marks'])
        for tag,key in [('b','bold'),('i','italic'),('u','underline')]:
            if marks.get(key):t=f'<{tag}>{t}</{tag}>'
        chunks.append(t)
    return ''.join(chunks)
def block(bid, rowlabels=None):
    n=nodes[bid];rendered.add(bid);out=[]
    if n['kind']=='paragraph':
        if n.get('text','').strip():out.append(p(rich(n)))
    elif n['kind']=='table':
        rows=[];spans=[]; merges={}
        cols=n['grid_columns']
        for ri,row in enumerate(n['rows']):
            cells=[];ci=0
            for cell in row['cells']:
                content=[]
                if ci==0 and rowlabels and ri+1 in rowlabels:content.append(p(rowlabels[ri+1],'small'))
                for c in cell['blocks']:content.extend(block(c['id']))
                span=cell.get('column_span',1)
                cells.append(content or [Spacer(1,14)])
                cells.extend(['']*(span-1))
                if span>1:spans.append(('SPAN',(ci,ri),(ci+span-1,ri)))
                vm=cell.get('vertical_merge')
                if vm=='restart':merges[ci]=ri
                elif vm=='continue' and ci in merges:
                    spans=[s for s in spans if not(s[1]==(ci,merges[ci]) and s[2][0]==ci+span-1)]
                    spans.append(('SPAN',(ci,merges[ci]),(ci+span-1,ri)))
                else:merges.pop(ci,None)
                ci+=span
            rows.append(cells+['']*max(0,cols-len(cells)))
        if rows:
            t=Table(rows,colWidths=[WIDTH/cols]*cols,hAlign='LEFT')
            t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#bed3d6')),('ROWBACKGROUNDS',(0,0),(-1,-1),[colors.white,LIGHT]),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]+spans))
            out.extend([t,Spacer(1,8)])
    for c in n.get('children',[]):out.extend(block(c['id']))
    return out
class Lines(Flowable):
    def __init__(self,n=1):Flowable.__init__(self);self.width=WIDTH;self.height=n*20;self.n=n
    def draw(self):
        self.canv.setStrokeColor(colors.HexColor('#c4d4d6'));self.canv.setLineWidth(.4)
        for i in range(self.n):self.canv.line(0,6+i*20,WIDTH,6+i*20)
class Doc(BaseDocTemplate):
    def afterFlowable(self,f):
        if hasattr(f,'toc'):
            level,title,key=f.toc
            self.canv.bookmarkPage(key);self.canv.addOutlineEntry(title,key,level=level,closed=False)
            if not key.startswith('answers-'):self.notify('TOCEntry',(level,title,self.page,key))
def page(c,d):
    if d.page==1:return
    c.setStrokeColor(colors.HexColor('#c4d4d6'));c.line(50,H-40,W-50,H-40)
    c.setFont('Body',8);c.setFillColor(TEAL);c.drawString(50,H-30,'ENGLISH GRAMMAR  /  PRACTICE & ANSWERS')
    c.drawRightString(W-50,27,str(d.page))
def heading(text,key,level=1):
    f=p(esc(text),'h1' if level==0 else 'h2');f.toc=(level,text,key);return f
story=[Spacer(1,110),p('ENGLISH GRAMMAR','small'),Spacer(1,18)]
cover=ParagraphStyle('cover',parent=styles['h1'],fontSize=46,leading=52)
story.extend([Paragraph('Learn.<br/>Practise.<br/>Understand.',cover),Spacer(1,24),p('Grammar explanations, exercises &amp; answers','h2'),Spacer(1,20),p('115 lessons • 15 topic sections'),p('Human-created teaching content<br/>with editorial revisions and an AI-assisted answer key'),Spacer(1,60),p('CONTENT EDITION 3.0.0','small'),PageBreak(),p('Contents','h1')])
toc=TableOfContents();toc.levelStyles=[ParagraphStyle('toc0',parent=styles['body'],fontName='Bold',spaceBefore=8),ParagraphStyle('toc1',parent=styles['body'],fontSize=9,leading=12,leftIndent=14,spaceBefore=1,spaceAfter=1)]
story.extend([toc,PageBreak(),p('Using this collection','h1'),p('Read the explanation, study the examples, then attempt the exercises. Write directly on a printed copy or use a separate notebook. Each lesson starts on a new page.'),p('Exercise references use lesson.exercise.item, for example 01.1.2. The answer section uses the same references. Worked examples are labelled and do not require a new response.'),p('Some questions have several valid answers. Model responses illustrate one possibility; listed alternatives are not exhaustive. An empty answer means that no word needs to be inserted.'),p('The core content was commissioned from human writers for the former Dreaming in English project. AI assisted with proofreading, corrections, missing examples, the answer key, and JSON conversion. The source manuscript and detailed provenance are available in the repository.'),p('This PDF is generated from the reusable JSON. The original manuscript remains unchanged.'),PageBreak()])
lessons=[]
for si,sec in enumerate(DATA['sections'],1):
    story.append(heading(f'{si:02d}  {sec["title"]}',sec['id'],0))
    for li,lesson in enumerate(sec['lessons']):
        if li:story.append(PageBreak())
        ln=len(lessons)+1;lessons.append((ln,lesson))
        story.append(heading(f'{ln:02d}  {lesson["title"]}',lesson['id']))
        for bid in lesson['teaching_block_ids']:
            if nodes[bid].get('text')==lesson['title']:rendered.add(bid);continue
            story.extend(block(bid))
        for ai,a in enumerate(lesson['activities'],1):
            exercise_start=len(story)
            story.append(p(f'EXERCISE {ln:02d}.{ai}','h2'))
            story.append(p(esc(a['instruction']),'instruction'));rendered.add(a['instruction_block_id'])
            starts={};ends={};rowlabels={}
            for ii,it in enumerate(a['items'],1):
                label=f'{ln:02d}.{ai}.{ii}';item_labels[it['id']]=label
                refs=it['content_refs'];first=refs[0]['block_id'];last=refs[-1]['block_id']
                starts.setdefault(first,[]).append((label,it));ends.setdefault(last,[]).append((label,it))
                for ref in refs:
                    if ref['row'] is not None:rowlabels.setdefault(ref['block_id'],{})[ref['row']]=label
            item_start=None
            for bid in a['content_block_ids']:
                if bid==a['instruction_block_id']:continue
                for label,it in starts.get(bid,[]):
                    if not rowlabels.get(bid):
                        item_start=exercise_start if it is a['items'][0] else len(story)
                        f=p(label+('  ·  WORKED EXAMPLE' if it['role']=='worked_example' else ''),'small');f.keepWithNext=True;story.append(f)
                story.extend(block(bid,rowlabels.get(bid)))
                for label,it in ends.get(bid,[]):
                    fs=[f for f in it['response_fields'] if f['editable'] and f['placement']=='after_prompt']
                    if fs and not rowlabels.get(bid):
                        for f in fs:
                            story.extend([p((label+'  ' if rowlabels.get(bid) else '')+esc(f['label']),'small'),Lines()])
                    if item_start is not None and not rowlabels.get(bid):
                        segment=story[item_start:]
                        story[item_start:]=[KeepTogether(segment)]
                        item_start=None
            story.append(Spacer(1,8))
    story.append(PageBreak())
story.append(heading('Answer key','answer-key',0))
story.append(p('Match the numbered reference to the exercise. Worked examples are repeated for completeness. Accept other grammatically correct, contextually appropriate responses for open tasks.'))
keys={k['item_id']:k for k in DATA['answer_key']['entries']}
for ln,lesson in lessons:
    story.append(heading(f'{ln:02d}  {lesson["title"]}','answers-'+lesson['id']))
    for a in lesson['activities']:
        for it in a['items']:
            k=keys[it['id']];key_ids.append(k['id']);parts=[]
            for part in k['parts']:
                answer=esc(part['answer']) if not part['is_empty_answer'] else '<i>No word required.</i>'
                if len(k['parts'])>1:answer=f'<b>{part["position"]}.</b> '+answer
                if part['acceptable_alternatives']:answer+=' <i>Also:</i> '+ '; '.join(esc(x) for x in part['acceptable_alternatives'])
                parts.append(answer)
            label=item_labels[it['id']]
            extra=' <i>(model response)</i>' if k['answer_type']=='model_response' else ' <i>(worked example)</i>' if it['role']=='worked_example' else ''
            story.append(KeepTogether([p('<b>'+label+'</b>'+extra+'<br/>'+'<br/>'.join(parts),'key')]))
assert len(key_ids)==len(keys)==1704
required=set()
for _,l in lessons:
    required.update(l['teaching_block_ids'])
    for a in l['activities']:required.update(a['content_block_ids']);required.add(a['instruction_block_id'])
assert not required-rendered, required-rendered
doc=Doc(str(OUT),pagesize=A4,leftMargin=50,rightMargin=50,topMargin=55,bottomMargin=48,title='English Grammar - Practice and Answers',author='')
doc.addPageTemplates(PageTemplate(id='normal',frames=[Frame(50,48,WIDTH,H-103,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=page))
doc.multiBuild(story)
(ROOT/'tmp').mkdir(exist_ok=True)
(ROOT/'tmp/pdf-build-manifest.json').write_text(json.dumps({'lessons':len(lessons),'items':len(item_labels),'answers':len(key_ids),'rendered_blocks':len(rendered)},indent=2))
print(OUT)
