import re, json
L=[l.rstrip() for l in open('/home/claude/src/libro_morti.txt',encoding='utf8')]
def clean(s):
    s=s.replace('\\[','[').replace('\\]',']').replace('\\*','*').replace('\\-','-').replace('\\+','+')
    return s.strip()
L=[clean(l) for l in L]
hdr=re.compile(r'^(.+?) \((\d+)°\)$')
idx=[i for i,l in enumerate(L) if l.startswith('non morto ')]
heads=[]
for i in idx:
    j=i-1
    while not hdr.match(L[j]): j-=1
    heads.append(j)
def num(s):
    s=s.replace('−','-').replace('–','-')
    m=re.search(r'[-+]?\d+',s); return int(m.group()) if m else None
def slug(s):
    s=s.lower()
    for a,b in [('à','a'),('è','e'),('é','e'),('ì','i'),('ò','o'),('ù','u'),('ä','a'),("'",'')]: s=s.replace(a,b)
    return re.sub(r'[^a-z0-9]+','_',s).strip('_')
out=[]
for k,i in enumerate(idx):
    h=heads[k]; m=hdr.match(L[h]); nome,liv=m.group(1),int(m.group(2))
    end = heads[k+1] if k+1<len(idx) else len(L)
    descr=' '.join(x for x in L[h+1:i] if x)
    head=L[i]
    mt=re.match(r'non morto (.+?) \((\w+)\)(.*?)\| Iniziativa: (.+)$',head)
    taglia,tipo,nota,ini=mt.group(1),mt.group(2),mt.group(3).strip(' —'),mt.group(4)
    focus='Focus semplice' in nota
    nota=nota.replace('¹Focus semplice','').strip(' —')
    body=[x for x in L[i+1:end] if x and not x.startswith('Non morti di livello')]
    c={'id':slug(nome),'nome':nome,'livello':liv,'tipo':tipo,'taglia':taglia,'sciame':'sciame' in taglia,
       'focus':focus,'nota':nota,'iniziativa':num(ini),'descr':descr,'extra':[],'capacita':[]}
    for b in body:
        if b.startswith('Difesa '):
            for seg in b[7:].split(' | '):
                seg=seg.strip()
                if seg.startswith('CA '):
                    ms=re.findall(r'[-−]?\d+',seg); c['ca'],c['contatto'],c['impreparato']=[num(x) for x in ms[:3]]
                elif seg.startswith('PF '):
                    c['pf']=num(seg); c['dv']=int(re.search(r'\((\d+) DV',seg).group(1))
                elif seg.startswith('TS '):
                    t=re.findall(r'(Tempra|Riflessi|Volontà) ([+−-]\d+)',seg); c['ts']={a:num(b) for a,b in t}
                else: c['extra'].append(seg)
        elif b.startswith('Attacco Velocit'):
            segs=b[8:].split(' | ')
            c['velocita']=segs[0].replace('Velocità ','').strip()
            c['attacchi']=[]; c['att_speciali']=''
            for seg in segs[1:]:
                if seg.startswith('Attacchi speciali:'): c['att_speciali']=seg.split(':',1)[1].strip()
                elif seg.startswith('Spazio') : c['extra'].append(seg)
                else: c['attacchi'].append(seg.strip())
        elif b.startswith('Statistiche '):
            segs=b[12:].split(' | ')
            c['car']={}
            for a,v in re.findall(r'(For|Des|Cos|Int|Sag|Car) ([—\-−]|\d+)',segs[0]):
                c['car'][a]=None if v in '—-−' else int(v)
            for seg in segs[1:]:
                seg=seg.strip()
                if seg.startswith('BMC'):
                    c['bmc']=seg
                elif seg.startswith('Talenti:'): c['talenti']=seg[8:].strip()
                elif seg.startswith('Abilità:'): c['abilita']=seg[8:].strip()
                else: c['extra'].append(seg)
        else:
            mm=re.match(r'^([^:]{2,80}?) \((Sfo|Sop|Mag|Str)\): ?(.*)$',b)
            if mm: c['capacita'].append({'nome':mm.group(1),'tipo':mm.group(2),'testo':mm.group(3)})
            else: c['capacita'].append({'nome':'','tipo':'','testo':b})
    out.append(c)
json.dump(out,open('/home/claude/app/morti.json','w',encoding='utf8'),ensure_ascii=False,indent=1)
print(len(out))
for c in out:
    miss=[k for k in ['ca','pf','ts','velocita','car','bmc'] if k not in c]
    if miss or not c['attacchi']: print('MISS',c['nome'],miss,c['attacchi'])
from collections import Counter
print(Counter(c['tipo'] for c in out))
print(Counter(x['tipo'] for c in out for x in c['capacita']))
for c in out:
    for x in c['capacita']:
        if not x['tipo']: print('NT',c['nome'],'|',x['testo'][:110])
