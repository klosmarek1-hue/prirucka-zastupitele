"""Kontroly kvality výstupu: odkazy na poznámky, osiřelé úlomky, dělení slov."""
import re, glob, sys, collections
root = sys.argv[1] if len(sys.argv) > 1 else '.'
LOW = 'a-záčďéěíňóřšťúůýž'
files = sorted(glob.glob(f'{root}/kapitoly/**/*.md', recursive=True))
bad = []; orph = []; hy = collections.Counter()
for f in files:
    t = open(f).read()
    refs = set(re.findall(r'\[\^([\w-]+)\](?!:)', t)); defs = set(re.findall(r'^\[\^([\w-]+)\]:', t, re.M))
    if refs - defs: bad.append(('bez definice', f.split('/')[-1][:30], sorted(refs - defs)))
    if defs - refs: bad.append(('bez odkazu', f.split('/')[-1][:30], sorted(defs - refs)))
    for m in re.findall(r'\b\w+- [a-záčďéěíňóřšťúůýž]\w*', t): hy[m] += 1
    paras = [p for p in t.split('\n\n') if not p.startswith('<!--')]
    for i, p in enumerate(paras[1:], 1):
        if re.match(f'[{LOW}]', p) and not re.match(r'([a-z]|\d{1,2})\)\s', p) \
           and not re.match(r'(ústavní zákon|zákon|vyhláška|nařízení|http|www)', p):
            orph.append((f.split('/')[-1][:24], paras[i-1][-40:].replace('\n', ' '), p[:45].replace('\n', ' ')))
for b in bad: print(*b)
print('dělení slov:', hy.most_common(20))
print('úlomky:', len(orph))
for o in orph: print('  ', o)
