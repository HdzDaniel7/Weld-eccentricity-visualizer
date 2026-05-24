import subprocess
import sys

# Lista de librerías necesarias
required_libraries = ['matplotlib', 'numpy', 'pandas', 'openpyxl', 'scipy']

def install_libraries():
    for library in required_libraries:
        try:
            __import__(library)
        except ImportError:
            print(f"La librería {library} no está instalada. Instalándola ahora...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", library])

install_libraries()

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.interpolate import interp1d

# ==============================================================================
# FUENTE DE DATOS — Descomenta el bloque que quieras usar
# ==============================================================================

# --- OPCIÓN A: Datos de ejemplo (activa por defecto para pruebas) ---
#USE_EXAMPLE_DATA = True   # <--- Cambia a False para usar Excel
#
#angles_1     = np.array([0, 60, 120, 180, 240, 300], dtype=float)
#dist_1_1     = np.array([3.0, 3.2, 2.9, 3.1, 3.0, 3.3], dtype=float)
#dist_2_1     = np.array([7.0, 7.2, 6.8, 7.1, 6.9, 7.3], dtype=float)
#depths_1     = np.array([2.5, 2.8, 2.6, 2.7, 2.4, 2.9], dtype=float)
#hoja         = "Ejemplo"

#--- OPCIÓN B: Leer desde archivo Excel (descomenta este bloque y pon USE_EXAMPLE_DATA = False) ---
USE_EXAMPLE_DATA = False

if len(sys.argv) < 2:
    print("Por favor, proporciona el nombre de la hoja como argumento.")
    exit()
hoja = sys.argv[1]

archivo_excel = "C:Proyecto Analissi de Soldadura/Tabla de excentricidad.xlsm"

try:
    df = pd.read_excel(archivo_excel, sheet_name=hoja, engine='openpyxl')
    print(f"Datos leídos correctamente de la hoja: {hoja}")
except Exception as e:
    print(f"Error al leer la hoja '{hoja}' del archivo: {e}")
    exit()

rango_1 = (8, 16)   # Filas 10 a 17 en Excel (solo primer rango)

def extraer_datos(df, fila_inicio, fila_fin):
    angles = df.iloc[fila_inicio:fila_fin, 1].dropna().astype(float).values.flatten()
    dist_1 = df.iloc[fila_inicio:fila_fin, 2].dropna().astype(float).values.flatten()
    dist_2 = df.iloc[fila_inicio:fila_fin, 3].dropna().astype(float).values.flatten()
    depths  = df.iloc[fila_inicio:fila_fin, 5].dropna().astype(float).values.flatten()
    return angles, dist_1, dist_2, depths 

def filtrar_vacias(angles, dist_1, dist_2):
    mask = ~np.isnan(dist_1) & ~np.isnan(dist_2)
    return angles[mask], dist_1[mask], dist_2[mask]

angles_1, dist_1_1, dist_2_1, depths_1 = extraer_datos(df, *rango_1)
angles_1, dist_1_1, dist_2_1 = filtrar_vacias(angles_1, dist_1_1, dist_2_1)

# ==============================================================================
# FIN DE OPCIONES DE FUENTE DE DATOS
# ==============================================================================

# --- Mapeo a eje X lineal igualmente espaciado ---
n_pts    = len(angles_1)
x_ctrl   = np.linspace(0, 10, n_pts)   # 10 unidades de largo, puntos igualmente espaciados
mid_dist = (dist_1_1 + dist_2_1) / 2

# --- Interpolación suavizada a lo largo del eje X ---
N_SMOOTH = 200

def interpolar_lineal(x_ctrl, valores, n=N_SMOOTH, extrapolar=False):
    """Interpola con spline cúbico sobre el eje X lineal."""
    f = interp1d(x_ctrl, valores, kind='cubic')
    x_smooth = np.linspace(x_ctrl[0], x_ctrl[-1], n)
    return x_smooth, f(x_smooth)

x_s, d1_s  = interpolar_lineal(x_ctrl, dist_1_1)
_,   d2_s  = interpolar_lineal(x_ctrl, dist_2_1)
_,   dep_s = interpolar_lineal(x_ctrl, depths_1)
_,   mid_s = interpolar_lineal(x_ctrl, mid_dist)

# ==============================================================================
# Coordenadas 3D de la soldadura lineal
# El eje X  → longitud de la soldadura
# El eje Y  → ancho (dist_1 y dist_2 se mapean directamente como Y)
# El eje Z  → profundidad (negativa hacia abajo)
# ==============================================================================

# Borde superior exterior (dist_2) — cordón derecho, z=0
# Borde superior interior (dist_1) — cordón izquierdo, z=0
# Centro   (mid)                   — fondo del cordón, z negativo

# Curvas de borde en el plano superior (z = 0)
#   Borde exterior: y = +dist_2_s  (lado exterior)
#   Borde interior: y = +dist_1_s  (lado interior)
# Punto medio con profundidad:
#   y = +mid_s, z = -dep_s + 2

# Nota: dist_1 y dist_2 representan anchos del cordón; los mapeamos como
# desplazamiento simétrico respecto a y=0 para que la soldadura quede centrada.

y2_pos =  d2_s / 2   # borde externo  (+y)
y2_neg = -d2_s / 2   # borde externo  (−y)
y1_pos =  d1_s / 2   # borde interno  (+y)
y1_neg = -d1_s / 2   # borde interno  (−y)
ym_pos =  mid_s / 2  # centro        (+y)
ym_neg = -mid_s / 2  # centro        (−y)
zm     = -dep_s + 2  # profundidad del centro

# Puntos de control originales (misma lógica)
y2c_pos =  dist_2_1 / 2
y2c_neg = -dist_2_1 / 2
y1c_pos =  dist_1_1 / 2
y1c_neg = -dist_1_1 / 2
ymc_pos =  mid_dist / 2
ymc_neg = -mid_dist / 2
zmc     = -depths_1 + 2

# ==============================================================================
# GRÁFICA 3D
# ==============================================================================
fig = plt.figure(figsize=(13, 7))
ax  = fig.add_subplot(111, projection='3d')

z0 = np.zeros(N_SMOOTH)   # z=0 para las curvas superiores

# --- Curvas de borde suavizadas ---
ax.plot(x_s, y2_pos, z0, color='blue',  linewidth=1.4, label='Borde exterior +Y (dist 2)')
#ax.plot(x_s, y2_neg, z0, color='blue',  linewidth=1.4, linestyle='--', label='Borde exterior −Y (dist 2)')
ax.plot(x_s, y1_pos, z0, color='green', linewidth=1.4, label='Borde interior +Y (dist 1)')
#ax.plot(x_s, y1_neg, z0, color='green', linewidth=1.4, linestyle='--', label='Borde interior −Y (dist 1)')
ax.plot(x_s, ym_pos, zm, color='red',   linewidth=1.0, linestyle='-',  label='Centro +Y (profundidad)')
#ax.plot(x_s, ym_neg, zm, color='red',   linewidth=1.0, linestyle='--', label='Centro −Y (profundidad)')

# --- Puntos de control originales ---
z0c = np.zeros(n_pts)
ax.scatter(x_ctrl, y2c_pos, z0c,  color='blue',  s=60, zorder=5)
#ax.scatter(x_ctrl, y2c_neg, z0c,  color='blue',  s=60, zorder=5)
ax.scatter(x_ctrl, y1c_pos, z0c,  color='green', s=60, zorder=5)
#ax.scatter(x_ctrl, y1c_neg, z0c,  color='green', s=60, zorder=5)
ax.scatter(x_ctrl, ymc_pos, zmc,  color='red',   s=80, marker='D', zorder=5, label='Puntos medidos (profundidad)')
#ax.scatter(x_ctrl, ymc_neg, zmc,  color='red',   s=80, marker='D', zorder=5)

# Etiqueta del ángulo original sobre cada punto de control
for i, ang in enumerate(angles_1):
    ax.text(x_ctrl[i], y2c_pos[i], 0.15,
            f'{ang:.0f}°', color='black', fontsize=9, ha='center', va='bottom')

# --- Superficies suavizadas ---
def hacer_superficie(x_s, y_a, z_a, y_b, z_b, color, alpha=0.45):
    """Crea caras entre dos curvas (a→b) a lo largo de x_s."""
    faces = []
    for i in range(N_SMOOTH - 1):
        j = i + 1
        face = [
            [x_s[i], y_a[i], z_a[i]],
            [x_s[j], y_a[j], z_a[j]],
            [x_s[j], y_b[j], z_b[j]],
            [x_s[i], y_b[i], z_b[i]],
        ]
        faces.append(face)
    ax.add_collection3d(Poly3DCollection(faces, facecolors=color, alpha=alpha, edgecolor='none'))

# Cara exterior +Y: dist_2 → centro
hacer_superficie(x_s, y2_pos, z0, ym_pos, zm, color='cyan')
# Cara exterior −Y: dist_2 → centro
#hacer_superficie(x_s, y2_neg, z0, ym_neg, zm, color='cyan')

# Cara interior +Y: dist_1 → centro
hacer_superficie(x_s, y1_pos, z0, ym_pos, zm, color='orange')
# Cara interior −Y: dist_1 → centro
#hacer_superficie(x_s, y1_neg, z0, ym_neg, zm, color='orange')

# Tapa superior +Y: dist_1 ↔ dist_2 en z=0
hacer_superficie(x_s, y1_pos, z0, y2_pos, z0, color='lightgray', alpha=0.25)
# Tapa superior −Y: dist_1 ↔ dist_2 en z=0
#hacer_superficie(x_s, y1_neg, z0, y2_neg, z0, color='lightgray', alpha=0.25)

# Tapas en los extremos (inicio y fin)
def tapa_extremo(x_val, i):
    """Dibuja el perfil transversal en un extremo de la soldadura."""
    ys = [y2_pos[i], y1_pos[i], ym_pos[i], y2_pos[i]]
    zs = [z0[i],     z0[i],     zm[i],     z0[i]]
    xs = [x_val] * len(ys)
    ax.plot(xs, ys, zs, color='gray', linewidth=1.0)

tapa_extremo(x_s[0],  0)
tapa_extremo(x_s[-1], N_SMOOTH - 1)

# --- Configuración ---
ax.set_xlabel('Longitud de soldadura (X)')
ax.set_ylabel('Ancho (Y)')
ax.set_zlabel('Profundidad (Z)')
ax.set_title(f'Soldadura Lineal 3D — {hoja}')
ax.view_init(elev=28, azim=-60)

plt.legend(loc='upper left', fontsize=7)
plt.tight_layout()
plt.show()
