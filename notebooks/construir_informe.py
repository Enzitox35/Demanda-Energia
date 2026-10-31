"""Genera informe_web.html: informe original + seccion de memoria termica + simulador interactivo.
Requiere junto al script: cammesa_preparado.csv e informe_web_1.html (informe original).
Mismo protocolo del cuaderno: arboles, train 2012-2016 / valid 2017 / test 2018, semilla 42."""
import json, re, numpy as np, pandas as pd
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.metrics import mean_absolute_error as mae, confusion_matrix

UC = 30.0
b = pd.read_csv('cammesa_preparado.csv', parse_dates=['datetime'])
b['fecha'] = b.datetime.dt.normalize()
d = b.groupby('fecha').Temp.max().rename('tmax').reset_index()
for k in (1, 2, 3): d[f'tmax_{k}'] = d.tmax.shift(k)
def racha(r):
    n = 0
    for k in (1, 2, 3):
        if r[f'tmax_{k}'] >= UC: n += 1
        else: break
    return n
d['racha_calor'] = d.apply(racha, axis=1); d['calor3'] = d[['tmax_1','tmax_2','tmax_3']].mean(axis=1)
b = b.merge(d[['fecha','racha_calor','calor3']], on='fecha').dropna(subset=['calor3'])
BASE = ['Temp','Hum','Pres','GHI','viento_vel','Holiday','hora','dia_semana','mes','fin_de_semana']
def X(df):
    return np.column_stack([df[BASE], (df.Temp-18).abs(), np.sin(2*np.pi*df.hora/24), np.cos(2*np.pi*df.hora/24),
        np.sin(2*np.pi*(df.mes-1)/12), np.cos(2*np.pi*(df.mes-1)/12), df.racha_calor, df.calor3])
tr, va, te = [b[b.split == s] for s in ('train','valid','test')]
def entrenar(n):                      # n = 15 (base) o 17 (con memoria termica)
    r = DecisionTreeRegressor(max_depth=12, random_state=42).fit(X(tr)[:, :n], tr.DemGBA)
    c = DecisionTreeClassifier(max_depth=8, class_weight={0:1,1:5}, random_state=42).fit(X(tr)[:, :n], tr.alta_demanda)
    pc = c.predict(X(te)[:, :n]); tn, fp, fn, tp = confusion_matrix(te.alta_demanda, pc).ravel()
    return r, c, dict(mv=mae(va.DemGBA, r.predict(X(va)[:, :n])), mt=mae(te.DemGBA, r.predict(X(te)[:, :n])),
                      fp=fp, fn=fn, costo=fp+5*fn, rec=tp/(tp+fn))
rb, cb, mb = entrenar(15); rx, cx, mx = entrenar(17)
print('base', mb); print('memoria', mx)

def exp(m, clf=False):
    t = m.tree_; v = t.value[:, 0, :]; v = v[:, 1]/v.sum(axis=1) if clf else v[:, 0]
    return dict(f=t.feature.tolist(), t=[float(x) for x in t.threshold], l=t.children_left.tolist(),
                r=t.children_right.tolist(), v=[round(float(x), 4) for x in v])
def pj(a, x):
    i = 0
    while a['l'][i] != -1: i = a['l'][i] if float(np.float32(x[a['f'][i]])) <= a['t'][i] else a['r'][i]
    return a['v'][i]
A, B, A0 = exp(rx), exp(cx, True), exp(rb)
Xt = X(te)[:1500]
da = max(abs(pj(A, x)-q) for x, q in zip(Xt, rx.predict(Xt))); db = max(abs(pj(A0, x[:15])-q) for x, q in zip(Xt, rb.predict(Xt[:, :15]))); print("dif exportacion", da, db); assert da < 1e-3 and db < 1e-3
ghi = b[b.split=='train'].groupby(['mes','hora']).GHI.mean().round(0).unstack().values.tolist()
datos = dict(reg=A, clf=B, base=A0, umbral=7307.0, mae=float(mx['mt']), uc=UC, ghi=ghi,
             rangos={c: [float(b[c].min()), float(b[c].max())] for c in ['Temp','Hum','Pres','GHI','viento_vel']})

# ---- evidencia descriptiva (misma hora, misma temperatura, laborables de verano) ----
s = b[(b.fin_de_semana==0)&(b.Holiday==0)&b.mes.isin([12,1,2])&b.hora.between(14,18)&b.Temp.between(30,34)]
g = s.groupby('racha_calor').DemGBA.agg(['count','mean']); vals = g['mean'].tolist(); ns = g['count'].tolist()
fm = lambda x: f'{x:,.0f}'.replace(',', '.')
filas = ''.join(f'<tr><td>{k if k<3 else "3 o más"}</td><td class="num">{fm(ns[k])}</td><td class="num">{fm(vals[k])} MW</td>'
                f'<td class="num">{"—" if k==0 else "+"+fm(vals[k]-vals[0])+" MW (+"+f"{(vals[k]/vals[0]-1)*100:.1f}".replace(".",",")+" %)"}</td></tr>' for k in range(4))
lo, hi = 7000, max(vals)*1.04
barras = ''.join(f'<rect x="{70+i*120}" y="{200-(v-lo)/(hi-lo)*170:.0f}" width="80" height="{(v-lo)/(hi-lo)*170:.0f}" rx="5" fill="var(--blue)" opacity="{.45+.18*i:.2f}"/>'
  f'<text x="{110+i*120}" y="{194-(v-lo)/(hi-lo)*170:.0f}" text-anchor="middle" font-size="14" font-weight="700" fill="var(--navy)">{fm(v)}</text>'
  f'<text x="{110+i*120}" y="222" text-anchor="middle" font-size="13" fill="var(--muted)">{i if i<3 else "3 o más"} {"día" if i==1 else "días"}</text>' for i, v in enumerate(vals))
svg = f'<svg viewBox="0 0 580 235" role="img" aria-label="Demanda media según días calurosos consecutivos previos" style="width:100%;height:auto;max-width:620px"><line x1="55" y1="200" x2="560" y2="200" stroke="var(--line)"/>{barras}</svg>'
f1 = lambda x: f'{x:,.0f}'.replace(',', '.')
cmp_rows = ''.join(f'<tr{" class=\"recommended\"" if r else ""}><td>{n}</td><td class="num">{f1(m["mv"])} MW</td><td class="num">{f1(m["mt"])} MW</td><td class="num">{f1(m["fp"])}</td><td class="num">{f1(m["fn"])}</td><td class="num">{f1(m["costo"])}</td></tr>'
                   for n, m, r in [('Modelo base (clima de la hora y calendario)', mb, 0), ('Modelo con memoria térmica', mx, 1)])
pct = (1-mx['mt']/mb['mt'])*100

MEM = open('seccion_memoria.html', encoding='utf-8').read().replace('@@FILAS@@', filas).replace('@@SVG@@', svg).replace('@@CMP@@', cmp_rows) \
      .replace('@@PCT@@', f'{pct:.0f}').replace('@@MB@@', f1(mb['mt'])).replace('@@MX@@', f1(mx['mt'])).replace('@@DIF@@', fm(vals[3]-vals[0])) \
      .replace('@@NB@@', f1(mb['mv'])).replace('@@NX@@', f1(mx['mv']))
SIM = open('seccion_simulador.html', encoding='utf-8').read().replace('/*DATOS*/null', json.dumps(datos, separators=(',', ':')))
CSS = open('estilos_extra.css', encoding='utf-8').read()

h = open('informe_web_1.html', encoding='utf-8').read()
h = h.replace('</style>', CSS + '\n  </style>', 1)
h = h.replace('<li><a href="#probar">Probar el modelo</a></li>', '<li><a href="#memoria">Memoria térmica</a></li>\n      <li><a href="#probar">Simulador</a></li>')
h = re.sub(r'<section id="probar">.*?(?=<section id="limitaciones">)', lambda m: MEM + '\n' + SIM + '\n\n    ', h, flags=re.S)
h = h.replace('07 · Alcance y reproducibilidad', '08 · Alcance y reproducibilidad')
h = h.replace('<li>Los costos relativos 1:5', '<li>Las secciones 03 a 05 evalúan el modelo base. La extensión con memoria térmica (secciones 06 y 07) se probó con el mismo protocolo, pero su ganancia es moderada y proviene de una sola partición temporal.</li>\n            <li>Los costos relativos 1:5', 1)
h = h.replace('<p class="small">La aplicación Flask se encuentra en el repositorio.</p>', '<p class="small">El simulador de la sección 07 se ejecuta en el navegador: los árboles entrenados se incluyen en esta página, sin servidor.</p>')
open('informe_web.html', 'w', encoding='utf-8').write(h)
print('OK', round(len(h)/1024), 'KB')
