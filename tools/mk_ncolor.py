# 实验: 把 2 卷料模板扩成 N 卷, 生成 N 层叠色方块, 看 Bambu 是否真的按 N 个挤出机切
import json, sys, zipfile
N=int(sys.argv[1]); out=sys.argv[2]
cols=['#D7261E','#FFC800','#111111','#FFFFFF'][:N]
d=json.load(open('reference/project_settings_2PLA.config'))
SKIP=lambda k: k.startswith('machine_') or k=='start_end_points'
for k,v in list(d.items()):
    if isinstance(v,list) and len(v)==2 and not SKIP(k): d[k]=v+[v[-1]]*(N-2) if N>=2 else v[:N]
m=d['flush_volumes_matrix']; off=m[1]
d['flush_volumes_matrix']=[('0' if i==j else off) for i in range(N) for j in range(N)]
d['flush_volumes_vector']=[d['flush_volumes_vector'][0]]*(2*N)
for k in ['different_settings_to_system','inherits_group']:
    v=d[k]; d[k]=[v[0]]+['']*N+[v[-1]] if len(v)==3 else v
d['filament_colour']=cols
d['printable_area']=['0x0','256x0','256x256','0x256']
def box(x0,y0,x1,y1,z0,z1):
    V=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    T=[(0,3,2),(0,2,1),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
    return V,T
objs=[];z=0
for i in range(N):
    inset=i*4; h=2.0 if i==0 else 0.6
    objs.append(box(88+inset,108+inset,168-inset,148-inset,z,z+h)); z+=h
xml=['<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:BambuStudio="http://schemas.bambulab.com/package/2021">\n <metadata name="Application">BambuStudio-02.07.01.62</metadata>\n <metadata name="BambuStudio:3mfVersion">1</metadata>\n<resources>\n']
for i,(V,T) in enumerate(objs):
    xml.append('<object id="%d" type="model"><mesh><vertices>'%(i+2)+''.join('<vertex x="%.4f" y="%.4f" z="%.4f"/>'%v for v in V)+'</vertices><triangles>'+''.join('<triangle v1="%d" v2="%d" v3="%d"/>'%t for t in T)+'</triangles></mesh></object>\n')
xml.append('<object id="1" type="model"><components>'+''.join('<component objectid="%d"/>'%(i+2) for i in range(N))+'</components></object>\n</resources>\n<build>\n<item objectid="1" transform="1 0 0 0 1 0 0 0 1 0 0 0" printable="1"/>\n</build>\n</model>\n')
ms=['<?xml version="1.0" encoding="UTF-8"?>\n<config>\n  <object id="1">\n    <metadata key="name" value="stack"/>\n    <metadata key="extruder" value="1"/>\n']
for i in range(N): ms.append('    <part id="%d" subtype="normal_part"><metadata key="name" value="L%d"/><metadata key="extruder" value="%d"/><metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/></part>\n'%(i+2,i+1,i+1))
ms.append('  </object>\n  <plate>\n    <metadata key="plater_id" value="1"/>\n    <model_instance><metadata key="object_id" value="1"/><metadata key="instance_id" value="0"/></model_instance>\n  </plate>\n</config>\n')
g=zipfile.ZipFile('reference/golden_project_minimal.3mf')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml',g.read('[Content_Types].xml'))
    z.writestr('_rels/.rels',g.read('_rels/.rels'))
    z.writestr('3D/3dmodel.model',''.join(xml))
    z.writestr('Metadata/model_settings.config',''.join(ms))
    z.writestr('Metadata/project_settings.config',json.dumps(d,indent=1))
print('wrote',out)
