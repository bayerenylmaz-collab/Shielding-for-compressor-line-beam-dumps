#!/usr/bin/env python3
"""Read/check INP and write a native Flair project using the installed Flair API."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--flair-root',type=Path,required=True,help='Directory containing deck/, fluka/, lib/, db/')
a=p.parse_args()
sys.path[:0]=[str(a.flair_root.resolve()),str((a.flair_root/'lib').resolve())]
import deck
import fluka
from stream import Stream
deck.init();fluka.init()
i=fluka.Fluka()
loaded=i.load(str(ROOT/'model/beam_dump_baseline.inp'))
if not loaded:raise RuntimeError('Flair could not load the input')
invalid=[]
for c in i.children:
    errors=c.validate()
    if errors:invalid.append([c.tag,c.sdum(),str(errors)])
if invalid:raise RuntimeError(invalid)
s=Stream(str(ROOT/'model/beam_dump_baseline.flair'),'w')
s.write('# flair project file\nVersion: 300\nMode: fluka\nTitle: Compressor beam dump - simplified CAD geometry\nInput:\n')
s.commentChar='*'
for c in i.children:c.write(s,'fluka')
s.write('EndInput\n');s.close()
print(f'Flair loaded {len(i.children)} cards, no invalid cards; project exported.')
