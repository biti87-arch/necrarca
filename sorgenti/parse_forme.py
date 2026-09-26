import re, json
L=[l.rstrip() for l in open('/home/claude/src/forme_non_morte.txt',encoding='utf8')]
def clean(s):
    return s.replace('\\[','[').replace('\\]',']').replace('\\*','*').replace('\\+','+').replace('\\-','-').strip()
L=[clean(l) for l in L]
start=[i for i,l in enumerate(L) if l=='Categoria I'][-1]
hdr=re.compile(r'^(⚔ )?(.+?) \((Scheletro|Zombie|Ghoul|Spirito|Disarticolato), (.+)\)$')
TIPI={'Scheletro','Zombie','Ghoul','Spirito','Disarticolato'}
CATS={'Categoria I':'I','Categoria II':'II','Categoria III':'III','Categoria IV':'IV','Categoria V':'V','Categoria VI':'VI','Categoria Speciale':'Speciale'}
def slug(s):
    s=s.lower()
    for a,b in [('à','a'),('è','e'),('é','e'),('ì','i'),('ò','o'),('ù','u'),("'",'')]: s=s.replace(a,b)
    return re.sub(r'[^a-z0-9]+','_',s).strip('_')
def sgn(s):
    s=s.replace('−','-'); m=re.search(r'[-+]?\d+',s); return int(m.group()) if m else None
forms=[];cat=None;cur=None
for i in range(start,len(L)):
    l=L[i]
    if l in CATS: cat=CATS[l]; cur=None; continue
    if not l or l in TIPI or l.startswith('Sbloccata al') : continue
    m=hdr.match(l)
    if m:
        cur={'id':slug(m.group(2)),'nome':m.group(2),'cat':cat,'tipo':m.group(3),'taglia_raw':m.group(4),
             'combattente':bool(m.group(1)),'pre':[],'post':[]}
        forms.append(cur); continue
    if cur is None: continue
    if 'stat' not in cur and re.match(r'^(For|Des) ',l):
        cur['stat']=l; continue
    if 'stat' in cur or cur['id']=='legione_sciolta' and ('PF separati' in l or l.startswith('▶') or 'PF' in cur.get('_seen','')):
        cur['post'].append(l)
    else:
        cur['pre'].append(l)
    if cur['id']=='legione_sciolta' and l.startswith('PF separati'): cur['_seen']='PF'
for f in forms:
    f.pop('_seen',None)
    tr=f['taglia_raw']
    f['taglia']=next((t for t in ['Minuscola','Piccola','Piccolo','Media','Grande','Enorme'] if t in tr),'Media').replace('Piccolo','Piccola')
    f['sciame']='sciame' in tr
    pre=f.pop('pre')
    if pre: f['descr']=pre[-1]; f['note']=pre[:-1]
    else: f['descr']='';f['note']=[]
    st=f.get('stat','')
    mf=re.search(r'For ([+−-]\d+|—)',st); md=re.search(r'Des ([+−-]\d+)',st)
    f['for']=sgn(mf.group(1)) if mf and mf.group(1)!='—' else (None if mf else 0)
    f['des']=sgn(md.group(1)) if md else 0
    mv=re.search(r'Velocità: (.+?)( — |$)',st); f['velocita']=mv.group(1) if mv else ''
    mc=re.search(r'(CA naturale|Deviazione): ([+−-]\d+)',st)
    f['ca_tipo']=('deviazione' if mc.group(1)=='Deviazione' else 'naturale') if mc else 'naturale'
    f['ca']=sgn(mc.group(2)) if mc else 0
    f['campi']={}; f['extra']=[]
    for p in f.pop('post'):
        mk=re.match(r'^(Attacchi|Sensi|Qualità|Bonus abilità|BAB pieno|BAB ¾): ?(.*)$',p)
        if mk: f['campi'][mk.group(1)]=mk.group(2); continue
        mr=re.match(r'^RD: (.*?) — Vulnerabilità: (.*)$',p)
        if mr: f['rd']=mr.group(1).strip(' —') or '—'; f['vuln']=mr.group(2).strip() ; continue
        f['extra'].append(p)
    txt=' '.join(f['note'])+' '+st
    f['semicorporeo']= f['tipo']=='Spirito' and f['cat']!='Speciale' or 'Semicorporeo' in f['campi'].get('Qualità','')
    f['incorporeo']='INCORPOREO' in txt or 'Incorporeo' in f['campi'].get('Qualità','')
    if f['incorporeo']: f['semicorporeo']=False
json.dump(forms,open('/home/claude/app/forme.json','w',encoding='utf8'),ensure_ascii=False,indent=1)
from collections import Counter
print(len(forms),Counter(f['cat'] for f in forms))
for f in forms:
    print(f"{f['cat']:>8} {f['tipo'][:5]} {f['taglia'][:4]} {'⚔' if f['combattente'] else ' '} {'S' if f['semicorporeo'] else ' '}{'I' if f['incorporeo'] else ' '} For{f['for']} Des{f['des']} {f['ca_tipo'][:3]}{f['ca']} | {f['nome']} | {f['velocita'][:30]} | extra{len(f['extra'])} campi{list(f['campi'])}")

UMANOIDI={'scheletro_corazzato','scheletro_insanguinato','zombie_putrescente','zombie_balzante','zombie_della_peste','ghoul','lacedon',
 'scheletro_elementale','scheletro_condottiero','zombie_corruttore','zombie_del_muschio_giallo','ghast','cavaliere_scheletrico',
 'scheletro_saettante','zombie_vermivoro','signore_della_peste_zombie','ghul','cavaliere_senza_testa','zombie_radiante_necrotico',
 'zombie_infestato','mohrg','cavaliere_della_tomba','harionago','baykok','maestro_della_guerra','re_ghoul','lich','vampiro'}
SEC=('coda','ala','ali','tentacol','zoccol','lingua','pinz')
atk=re.compile(r"^(?:(\d+) )?([a-zà-ù'’ ]+?)(?: \(([^)]*)\))?:? (\d+d\d+(?:\+(?:\d+|For))?)")
def parse_armi(txt):
    armi=[]
    txt=txt.replace('(o ',' oppure ').replace('))',')')
    for seg in re.split(r' \+ | e (?=\d )|,? oppure |; |, (?=in mischia)|in mischia, ',txt):
        seg=seg.strip()
        if 'impugnat' in seg and not armi or seg.startswith('arma '):
            armi.append({'n':1,'nome':'arma impugnata','dado':'arma','arma':True,'nota':seg}); continue
        m=atk.match(seg)
        if not m: continue
        nome=m.group(2).strip(); par=(m.group(3) or '').lower()
        if nome.startswith('danni da sciame'): 
            armi.append({'n':1,'nome':'sciame','dado':m.group(4),'sciame':True}); continue
        armi.append({'n':int(m.group(1) or 1),'nome':nome,'dado':m.group(4),
          'contatto':'contatto' in nome or 'contatto' in par or 'tocco' in nome,
          'des':'des' in par,'secondario':nome.startswith(SEC) or 'secondario' in par})
    return armi
for f in forms:
    f['umanoide']=f['id'] in UMANOIDI
    src=f['campi'].get('Attacchi')
    if not src:
        cand=[e for e in f['extra'] if e.startswith(('Attacco (1)','Attacchi melee','Attacchi alternativi'))]
        src=' + '.join(e.split(':',1)[1].strip() for e in cand) if cand else ''
    f['armi']=parse_armi(src)
json.dump(forms,open('/home/claude/app/forme.json','w',encoding='utf8'),ensure_ascii=False,indent=1)
for f in forms:
    print(f"{f['nome'][:26]:26} {'U' if f['umanoide'] else '-'} ", '; '.join(f"{a['n']}×{a['nome']} {a['dado']}{' C' if a.get('contatto') else ''}{' S' if a.get('secondario') else ''}" for a in f['armi']) or '!!! '+f['campi'].get('Attacchi','')[:80])
