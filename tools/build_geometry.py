#!/usr/bin/env python3
"""Build a simplified FLUKA model from measured CAD dimensions (stdlib only).

JSON dimensions are millimetres; FLUKA bodies are centimetres.
The geometry is a CAD-derived starting model, not a shielding qualification.
"""
import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def card(tag, *whats, sdum=""):
    fields = [str(x) if x is not None else "" for x in whats]
    fields += [""] * (6-len(fields))
    if any(len(x)>10 for x in fields) or len(sdum)>10:
        raise ValueError((tag, fields, sdum))
    return f"{tag:<10}" + "".join(f"{x:>10}" for x in fields) + sdum


def transform(p):
    a,b,c = p
    return [(b-446.666667)/10, (1533.5-a)/10, (c-1067.5)/10]


class Model:
    def __init__(self):
        self.bodies = {}
        self.objects = []
        self.regions = []

    def body(self, name, kind, values):
        if name in self.bodies or len(name)>8:
            raise ValueError(name)
        self.bodies[name] = dict(kind=kind, values=[round(x,6) for x in values])
        return name

    def box(self, name, lo, hi):
        return self.body(name, "RPP", [lo[0],hi[0],lo[1],hi[1],lo[2],hi[2]])

    def cylinder(self, name, start, axis, r):
        return self.body(name, "RCC", [*start,*axis,r])

    def aabb(self, name):
        b=self.bodies[name]; v=b['values']
        if b['kind']=='RPP': return [v[0],v[2],v[4]], [v[1],v[3],v[5]]
        p=v[:3];h=v[3:6];r=max(v[6:]);k=max(range(3),key=lambda i:abs(h[i]))
        lo=[min(p[i],p[i]+h[i])-(0 if i==k else r) for i in range(3)]
        hi=[max(p[i],p[i]+h[i])+(0 if i==k else r) for i in range(3)]
        return lo,hi

    def object(self, name, outer, holes=(), material="IRON", hole_material="AIR", note=""):
        lo,hi=self.aabb(outer)
        exclusions=[]
        for o in self.objects:
            a,b=self.aabb(o['outer'])
            if all(min(hi[i],b[i])-max(lo[i],a[i])>1e-7 for i in range(3)):
                exclusions.append(o['outer'])
        base=[outer]+['-'+x for x in exclusions]
        # Outer envelopes partition the world. Separate cavity regions avoid
        # exponential Boolean expansion of AIR around many hollow profiles.
        expr=['+'+outer]+['-'+x for x in exclusions]+['-'+x for x in holes]
        self.regions.append(dict(name=name, material=material, terms=expr, note=note))
        for j,h in enumerate(holes):
            self.regions.append(dict(name=f"{name}V{j}",material=hole_material,
                terms=['+'+outer,'+'+h]+['-'+x for x in exclusions]+['-'+x for x in holes[:j]],
                note=f"Cavity of {name}"))
        self.objects.append(dict(name=name,outer=outer,holes=list(holes),material=material,note=note))


def make_model(cfg):
    m=Model();d=cfg['dump']
    m.box('world',[-200,-50,-220],[200,300,200])
    m.body('black','SPH',[0,0,0,1000])
    # The dump axis is +Z; Y is physical height above the feet.
    y=140.0
    zfront=(d['front_native_z_mm']-1067.5)/10
    zback=(d['back_native_z_mm']-1067.5)/10
    m.cylinder('cuout',[0,y,zfront],[0,0,zback-zfront],d['core_radius_mm']/10)
    m.body('cone','TRC',[0,y,zfront,0,0,d['cone_depth_mm']/10,
                       d['cone_mouth_radius_mm']/10,d['cone_bottom_radius_mm']/10])
    m.object('DUMP','cuout',['cone'],'COPPER','VACUUM','STL component 7: fins and screw holes omitted')
    lipz=(d['lip_front_native_z_mm']-1067.5)/10
    m.cylinder('lipout',[0,y,lipz],[0,0,zfront-lipz],d['lip_outer_radius_mm']/10)
    m.cylinder('lipin',[0,y,lipz],[0,0,zfront-lipz],d['lip_inner_radius_mm']/10)
    m.object('CULIP','lipout',['lipin'],'COPPER','VACUUM','Copper entrance lip')

    # Axial pipe/flange envelopes, with narrow details and bellows smoothed.
    # Entries: native Z min/max, outer radius, bore radius, all millimetres.
    segments=cfg['pipe_segments_mm']
    # Side port bore opens into the long beam pipe; clipped by each envelope.
    m.cylinder('portin',[0,140,-53],[0,11.7,0],3.3)
    for i,(za,zb,ro,ri) in enumerate(segments):
        p=[0,y,(za-1067.5)/10];h=[0,0,(zb-za)/10]
        outer=m.cylinder(f'po{i:02}',p,h,ro/10)
        inner=m.cylinder(f'pi{i:02}',p,h,ri/10)
        holes=[inner]
        if za<537.5<zb: holes.append('portin')
        m.object(f'PIPE{i:02}',outer,holes,'IRON','VACUUM','Smoothed beam pipe / flange')
    m.cylinder('portout',[0,140,-53],[0,10,0],3.5)
    m.object('PORT','portout',['portin'],'IRON','VACUUM','Vertical T-port, simplified')
    m.cylinder('portfl',[0,150,-53],[0,1.7,0],5.715)
    m.object('PORTFL','portfl',['portin'],'IRON','VACUUM','T-port flange')
    m.cylinder('portcap',[0,151.7,-53],[0,1.25,0],3.5)
    m.object('PORTCAP','portcap',material='IRON',note='Simplified closed port cap')

    for i,s in enumerate(cfg['structural_parts']):
        lo,hi=s['bounds_native_mm']
        a=transform(lo);b=transform(hi)
        mn=[min(x,z) for x,z in zip(a,b)];mx=[max(x,z) for x,z in zip(a,b)]
        outer=m.box(f'so{i:02}',mn,mx);holes=[]
        if s['hollow_axis'] is not None:
            native_axis=s['hollow_axis'];axis={0:1,1:0,2:2}[native_axis]
            il=mn[:];ih=mx[:]
            for k in range(3):
                if k!=axis: il[k]+=s['wall_mm']/10;ih[k]-=s['wall_mm']/10
            holes=[m.box(f'si{i:02}',il,ih)]
        m.object(f'STR{i:02}',outer,holes,note=f"STL component {s['stl_component']}; squared corners")
    # Four upper-frame adjustable feet: a smooth cylinder replaces screw threads.
    for i,(x,z) in enumerate([(-30,-43.3),(30,-43.3),(-30,16.7),(30,16.7)]):
        out=m.cylinder(f'adj{i}',[x,123.1,z],[0,4.5,0],.8)
        m.object(f'ADJ{i}',out,note='Upper frame adjustment screw, simplified')
    for i,(x,z) in enumerate([(-30,-53),(30,-53),(-30,27),(30,27)]):
        out=m.cylinder(f'foot{i}',[x,.2,z],[0,5.8,0],1.5)
        m.object(f'FOOT{i}',out,note='Table leveling foot, thread omitted')
        plate=m.box(f'base{i}',[x-6,0,z-6],[x+6,.2,z+6])
        m.object(f'BASE{i}',plate,note='Foot base plate')
    # Beamline support below the dump inlet, based on the support bounding boxes.
    for i,(lo,hi) in enumerate(cfg['support_boxes_native_mm']):
        a=transform(lo);b=transform(hi)
        out=m.box(f'sup{i}',[min(x,z) for x,z in zip(a,b)],[max(x,z) for x,z in zip(a,b)])
        m.object(f'SUP{i}',out,note='Simplified beam-pipe support')

    # Optional rectangular lead panels in transformed physical coordinates, mm.
    # Disabled in the baseline. Earlier objects take precedence at intersections.
    for i,p in enumerate(cfg['lead_panels']):
        lo=[x/10 for x in p['min_mm']];hi=[x/10 for x in p['max_mm']]
        out=m.box(f'pb{i}',lo,hi)
        m.object(f'LEAD{i}',out,material='LEAD',note=p.get('note','User-defined lead panel'))
    m.regions.insert(0,dict(name='BLKHOLE',material='BLCKHOLE',terms=['+black','-world'],note='Transport termination'))
    m.regions.append(dict(name='AIR',material='AIR',terms=['+world']+['-'+o['outer'] for o in m.objects],note='Ambient air including omitted details'))
    return m


def write_input(m,cfg,path):
    lines=['TITLE','Compressor beam dump - CAD simplified baseline, not dose validated',
           '* All geometry dimensions below are cm; source CAD dimensions were mm.',
           '* X transverse; Y vertical from feet; Z beam direction; dump bottom Z=0.',
           '* 20 MeV electron pencil beam, 1 cm upstream of cavity bottom.',
           card('DEFAULTS',sdum='PRECISIO'),
           card('BEAM',-cfg['beam']['energy_MeV']/1000,0,0,0,0,1,sdum='ELECTRON'),
           card('BEAMPOS',0,140,cfg['beam']['source_z_mm']/10,0,0),
           card('GEOBEGIN',sdum='COMBNAME'),
           '    0    0          CAD simplified geometry']
    for name,b in m.bodies.items():
        lines.append(f"{b['kind']} {name} "+' '.join(f'{v:.6f}'.rstrip('0').rstrip('.') if v else '0' for v in b['values']))
    lines.append('END')
    for r in m.regions:
        lines.append('* '+r['note'])
        prefix=f"{r['name']:<8} 5 "
        line=prefix
        for term in r['terms']:
            if len(line)+len(term)+1>120:lines.append(line.rstrip());line=' '*12
            line+=term+' '
        lines.append(line.rstrip())
    lines+=['END',card('GEOEND')]
    for r in m.regions:lines.append(card('ASSIGNMA',r['material'],r['name']))
    lines+=['* Include photonuclear and electronuclear channels in used materials.']
    for mat in ['COPPER','IRON','LEAD','AIR']:
        lines.append(card('PHOTONUC',1,None,None,mat,mat,1,sdum='ELECTNUC'))
    lines+=['* Broad 2-cm 3D mesh: select the actual electronics sector after inspection.',
            '* DOSE-EQ output is pSv/primary; at 1 uA multiply by 2.2469432668E7',
            '* to obtain mSv/h. No transport calculation has been performed here.']
    for unit,particle,name in [(21,'DOSE-EQ','DoseMap'),(22,'PHOTON','PhotMap'),(23,'NEUTRON','NeutMap')]:
        lines.append(card('USRBIN',10,particle,-unit,100,180,100,sdum=name))
        lines.append(card('USRBIN',-100,100,-120,100,40,110,sdum='&'))
    lines += [card('RANDOMIZ',1,1234567), '* 10000 histories is a smoke run, NOT production shielding statistics.',
              card('START',10000),card('STOP')]
    path.write_text('\n'.join(lines)+'\n')


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,default=ROOT/'model/geometry_mm.json')
    p.add_argument('--output',type=Path,default=ROOT/'model/beam_dump_baseline.inp');a=p.parse_args()
    cfg=json.loads(a.config.read_text());m=make_model(cfg)
    a.output.parent.mkdir(parents=True,exist_ok=True);write_input(m,cfg,a.output)
    a.output.with_suffix('.geometry.json').write_text(json.dumps(dict(bodies=m.bodies,regions=m.regions,objects=m.objects),indent=2)+'\n')
    print(f'{a.output}: {len(m.bodies)} bodies, {len(m.regions)} regions')


if __name__=='__main__': main()
