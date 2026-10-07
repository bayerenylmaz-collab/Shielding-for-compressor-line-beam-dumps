#!/usr/bin/env python3
"""Render exported geometry sections. Requires numpy and matplotlib."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from check_geometry import ROOT,parse_input,classify

bodies,regions=parse_input(ROOT/'model/beam_dump_baseline.inp')
g=json.loads((ROOT/'model/beam_dump_baseline.geometry.json').read_text())
materials={r['name']:r['material'] for r in g['regions']}
palette={'AIR':0,'VACUUM':1,'IRON':2,'COPPER':3,'LEAD':4,'BLCKHOLE':5}
colors=['#f3f6fa','#d9f2fa','#71869b','#bd713d','#7e678e','#333333']
cmap=ListedColormap(colors)


def section(ax,horizontal,vertical,fixed_axis,fixed,limits,title,n=650):
    u=np.linspace(*limits[:2],n);v=np.linspace(*limits[2:],n)
    U,V=np.meshgrid(u,v);p=np.zeros((U.size,3));p[:,horizontal]=U.ravel();p[:,vertical]=V.ravel();p[:,fixed_axis]=fixed
    _,idx,_=classify(bodies,regions,p)
    values=np.array([palette[materials[regions[k][0]]] if k>=0 else 5 for k in idx]).reshape(U.shape)
    ax.imshow(values,extent=limits,origin='lower',cmap=cmap,vmin=-.5,vmax=5.5,interpolation='nearest',aspect='equal')
    ax.set_title(title,loc='left',fontweight='bold',fontsize=12,pad=13)
    labels=['X transverse (cm)','Y height (cm)','Z beam axis (cm)'];ax.set_xlabel(labels[horizontal]);ax.set_ylabel(labels[vertical])
    ax.grid(alpha=.15);ax.set_xlim(limits[:2]);ax.set_ylim(limits[2:])


fig,axs=plt.subplots(1,2,figsize=(15,8),gridspec_kw={'width_ratios':[1.05,1]})
section(axs[0],2,1,0,.031,[-110,40,0,160],'Side section | X = 0.031 cm')
axs[0].annotate('20 MeV electron beam',xy=(-1,140),xytext=(-95,145),fontsize=10,color='#005d80',arrowprops=dict(arrowstyle='->',color='#005d80',lw=2))
axs[0].annotate('Copper dump',xy=(5,140),xytext=(16,133),fontsize=9,arrowprops=dict(arrowstyle='-',color='#bd713d'))
axs[0].annotate('Table top: Y = 123.1 cm',xy=(13,123.1),xytext=(-105,109),fontsize=9,arrowprops=dict(arrowstyle='-',color='#71869b'))
section(axs[1],2,0,1,140.031,[-110,75,-75,75],'Horizontal section | Y = 140.031 cm')
theta=np.linspace(0,2*np.pi,500)
axs[1].plot(60*np.cos(theta),60*np.sin(theta),'--',color='#8b637f',lw=1.2)
axs[1].text(6,62,'600 mm reference distance',fontsize=9,color='#8b637f')
axs[1].annotate('',xy=(0,0),xytext=(-40,0),arrowprops=dict(arrowstyle='->',color='#005d80',lw=2))
fig.suptitle('Compressor beam dump | Simplified geometry',fontsize=19,fontweight='bold',x=.07,ha='left')
fig.legend(handles=[Patch(facecolor=colors[k],label=name) for name,k in palette.items() if name not in ['BLCKHOLE','LEAD']],loc='lower center',ncol=4,frameon=False,bbox_to_anchor=(.5,.03))
fig.text(.07,.012,'Geometry preview only — no dose results. Dashed circle is a distance reference, not an all-around acceptance region.',fontsize=9,color='#475569')
fig.tight_layout(rect=[.02,.09,.99,.92]);fig.savefig(ROOT/'docs/geometry_sections.png',dpi=160);plt.close(fig)

fig,ax=plt.subplots(figsize=(11,6))
section(ax,2,0,1,140.00001,[-8,11,-7,7],'Copper dump | Axial section',900)
ax.plot(-1,0,'o',color='#006f98',ms=7);ax.annotate('Source: Z = -1 cm',xy=(-1,0),xytext=(-7,4.5),arrowprops=dict(arrowstyle='-',color='#006f98'),color='#006f98')
ax.annotate('',xy=(.2,0),xytext=(-1,0),arrowprops=dict(arrowstyle='->',lw=2,color='#006f98'))
ax.annotate('Flat cavity bottom: 5 mm diameter',xy=(0,.25),xytext=(1,3.5),fontsize=10,arrowprops=dict(arrowstyle='-',color='#35445a'))
ax.text(1,-4.6,'90 mm copper behind the bottom',fontsize=10)
ax.text(-7,-6.5,'Main body: diameter 110 mm | Cone: depth 40 mm, mouth diameter 60 mm',fontsize=9)
fig.tight_layout();fig.savefig(ROOT/'docs/dump_section.png',dpi=160);plt.close(fig)
print('Rendered geometry_sections.png and dump_section.png')
