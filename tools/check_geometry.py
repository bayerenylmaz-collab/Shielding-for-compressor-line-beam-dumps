#!/usr/bin/env python3
"""Independent point-membership check of the GENERATED .inp geometry.

Requires numpy. This is not a replacement for FLUKA tracking / Flair debugging.
"""
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def parse_input(path):
    bodies={};regions=[];state=0
    for raw in path.read_text().splitlines():
        if not raw.strip() or raw.startswith('*'):continue
        if raw.startswith('GEOBEGIN'):state=1;continue
        if raw.startswith('GEOEND'):break
        if raw.strip()=='END':state+=1;continue
        tokens=raw.split()
        if state==1 and tokens[0] in ['RPP','RCC','TRC','SPH']:
            bodies[tokens[1]]=(tokens[0],np.array(tokens[2:],float))
        elif state==2:
            if raw[0].isspace():regions[-1][1].extend(tokens)
            else:regions.append([tokens[0],tokens[2:]])
    return bodies,regions


def inside(kind,v,p):
    if kind=='RPP':
        return ((p>=v[[0,2,4]])&(p<=v[[1,3,5]])).all(axis=1)
    if kind=='SPH':return np.sum((p-v[:3])**2,axis=1)<=v[3]**2
    q=p-v[:3];h=v[3:6];h2=h@h;t=q@h/h2
    rr=np.sum((q-t[:,None]*h)**2,axis=1)
    r=v[6] if kind=='RCC' else v[6]+t*(v[7]-v[6])
    return (t>=0)&(t<=1)&(rr<=r*r)


def classify(bodies,regions,p):
    masks={name:inside(k,v,p) for name,(k,v) in bodies.items()}
    counts=np.zeros(len(p),np.uint16);idx=np.full(len(p),-1,int)
    occupancy=[]
    for i,(name,terms) in enumerate(regions):
        a=np.ones(len(p),bool)
        for t in terms:
            if t[0] not in '+-' or t[1:] not in masks:raise ValueError(t)
            a &= masks[t[1:]] if t[0]=='+' else ~masks[t[1:]]
        counts+=a;idx[a]=i;occupancy.append(int(a.sum()))
    return counts,idx,occupancy


def main():
    b,r=parse_input(ROOT/'model/beam_dump_baseline.inp')
    rng=np.random.default_rng(71429)
    clouds=[rng.uniform([-199,-49,-219],[199,299,199],(100000,3)),
            rng.uniform([-46,.01,-105],[46,153,33],(100000,3)),
            rng.uniform([-7,132,-6],[7,148,10],(100000,3))]
    # Probe just inside/outside envelope faces, including thin pipe walls.
    for name,(kind,v) in b.items():
        if name in ['world','black']:continue
        if kind=='RPP':
            lo=v[[0,2,4]];hi=v[[1,3,5]]
            for ax in range(3):
                for edge in [lo[ax],hi[ax]]:
                    for eps in [-1e-5,1e-5]:
                        p=rng.uniform(lo,hi,(30,3));p[:,ax]=edge+eps;clouds.append(p)
        elif kind in ['RCC','TRC']:
            h=v[3:6];k=int(np.argmax(abs(h)));axes=[j for j in range(3) if j!=k]
            t=rng.uniform(.001,.999,200);ang=rng.uniform(0,2*np.pi,200)
            rad=np.full(200,v[6]) if kind=='RCC' else v[6]+t*(v[7]-v[6])
            rad+=rng.choice([-1e-5,1e-5],200)
            p=v[:3]+t[:,None]*h;p[:,axes[0]]+=rad*np.cos(ang);p[:,axes[1]]+=rad*np.sin(ang);clouds.append(p)
    tested=0;missing=0;overlap=0;occ=np.zeros(len(r),int)
    for p in clouds:
        counts,idx,o=classify(b,r,p);tested+=len(p);missing+=int((counts==0).sum());overlap+=int((counts>1).sum());occ+=o
    probes=np.array([[0,140,-1],[0,140,-.0001],[0,140,.0001],[0,140,8.9],[0,140,9.001],[0,140,-50],[0,145,-53]])
    count,idx,_=classify(b,r,probes)
    names=[r[j][0] for j in idx]
    assert names[0]=='DUMPV0' and names[1]=='DUMPV0' and names[2]=='DUMP',names
    assert names[3]=='DUMP' and names[4]=='AIR',names
    report={'method':'Independent RPP/RCC/TRC/SPH point membership on exported INP',
            'sampled_points':tested,'unassigned_points':missing,'multiply_assigned_points':overlap,
            'regions':len(r),'bodies':len(b),'source_and_axis_probes':[{'point_cm':p.tolist(),'region':n} for p,n in zip(probes,names)],
            'unhit_regions':[r[j][0] for j in range(len(r)) if occ[j]==0],
            'transport_run_performed':False,
            'limitations':'Point sampling is not a proof. No FLUKA executable run or native tracking check.'}
    (ROOT/'docs/geometry_check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2));assert missing==0 and overlap==0


if __name__=='__main__':main()
