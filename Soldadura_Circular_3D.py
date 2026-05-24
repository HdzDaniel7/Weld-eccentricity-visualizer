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
#depths_1     = np.array([Dgoal, 2.8, 2.6, 2.7, 2.4, 2.9], dtype=float)
#hoja         = "Ejemplo"

 #--- OPCIÓN B: Leer desde archivo Excel (descomenta este bloque y pon USE_EXAMPLE_DATA = False) ---
USE_EXAMPLE_DATA = False

if len(sys.argv) < 2:
    print("Por favor, proporciona el nombre de la hoja como argumento.")
    exit()
hoja = sys.argv[1]

archivo_excel = "C:.....Proyecto Analissi de Soldadura/Tabla de excentricidad.xlsm"

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

goal_raw = df.iloc[5, 10]
goal = float(goal_raw) if pd.notna(goal_raw) else None

Dgoal_raw = df.iloc[5, 13]
Dgoal = float(goal_raw) if pd.notna(goal_raw) else None

def filtrar_vacias(angles, dist_1, dist_2):
    mask = ~np.isnan(dist_1) & ~np.isnan(dist_2)
    return angles[mask], dist_1[mask], dist_2[mask]

angles_1, dist_1_1, dist_2_1, depths_1 = extraer_datos(df, *rango_1)
angles_1, dist_1_1, dist_2_1 = filtrar_vacias(angles_1, dist_1_1, dist_2_1)

# ==============================================================================
# FIN DE OPCIONES DE FUENTE DE DATOS
# ==============================================================================

# --- Puntos de control (los 6 puntos medidos) ---
angles_rad_1 = np.radians(angles_1)
mid_dist_1   = (dist_1_1 + dist_2_1) / 2

# --- Interpolación circular suavizada con N_SMOOTH puntos ---
N_SMOOTH = 200   # Resolución del anillo suavizado

def interpolar_circular(angles_rad, valores, n=N_SMOOTH):
    """Interpola circularmente cerrando el ciclo (primer == último) y
    devuelve n puntos uniformemente distribuidos en [0, 2pi)."""
    ang = np.append(angles_rad, angles_rad[0] + 2 * np.pi)
    val = np.append(valores, valores[0])
    f   = interp1d(ang, val, kind='cubic')
    ang_smooth = np.linspace(angles_rad[0], angles_rad[0] + 2 * np.pi, n, endpoint=False)
    return ang_smooth, f(ang_smooth)

ang_s, d1_s    = interpolar_circular(angles_rad_1, dist_1_1)
_,     d2_s    = interpolar_circular(angles_rad_1, dist_2_1)
_,     dep_s   = interpolar_circular(angles_rad_1, depths_1)
_,     mid_s   = interpolar_circular(angles_rad_1, mid_dist_1)

# --- Coordenadas de los anillos suavizados ---
def polar_a_xyz(ang, radio, z):
    return radio * np.cos(ang), radio * np.sin(ang), np.full_like(ang, z)

# Anillo exterior (dist_2) en z=0
x2s, y2s, z2s = polar_a_xyz(ang_s, d2_s, 0)

# Anillo interior (dist_1) en z=0
x1s, y1s, z1s = polar_a_xyz(ang_s, d1_s, 0)

# Puntos medios con profundidad (parte baja de la soldadura)
xms  = mid_s * np.cos(ang_s)
yms  = mid_s * np.sin(ang_s)
zms  = dep_s 

# --- Puntos de control originales (marcadores) ---
x1_ctrl  = dist_1_1 * np.cos(angles_rad_1)
y1_ctrl  = dist_1_1 * np.sin(angles_rad_1)

x2_ctrl  = dist_2_1 * np.cos(angles_rad_1)
y2_ctrl  = dist_2_1 * np.sin(angles_rad_1)

xm_ctrl  = mid_dist_1 * np.cos(angles_rad_1)
ym_ctrl  = mid_dist_1 * np.sin(angles_rad_1)
zm_ctrl  = -depths_1 

# ==============================================================================
# GRÁFICA 3D
# ==============================================================================
fig = plt.figure(figsize=(11, 8))
ax  = fig.add_subplot(111, projection='3d')

# --- Curvas de borde suavizadas ---
ax.plot(np.append(x2s, x2s[0]), np.append(y2s, y2s[0]), np.append(z2s, z2s[0]),
        color='blue', linewidth=1.2, label='Borde exterior (dist 2)')
ax.plot(np.append(x1s, x1s[0]), np.append(y1s, y1s[0]), np.append(z1s, z1s[0]),
        color='green', linewidth=1.2, label='Borde interior (dist 1)')
ax.plot(np.append(xms, xms[0]), np.append(yms, yms[0]), np.append(-zms, -zms[0]),
        color='red', linewidth=1.0, linestyle='--', label='Centro de soldadura')

# --- Puntos de control originales resaltados ---
ax.scatter(x2_ctrl, y2_ctrl, np.zeros_like(x2_ctrl),
           color='blue', s=60, zorder=5, label='Puntos medidos (dist 2)')
ax.scatter(x1_ctrl, y1_ctrl, np.zeros_like(x1_ctrl),
           color='green', s=60, zorder=5, label='Puntos medidos (dist 1)')
ax.scatter(xm_ctrl, ym_ctrl, zm_ctrl,
           color='red', s=80, marker='D', zorder=5, label='Puntos medidos (profundidad)')

# Etiquetas de ángulo en los puntos de dist_2
for i, ang in enumerate(angles_1):
    ax.text(x2_ctrl[i], y2_ctrl[i], 0.15,
            f'{ang:.0f}°', color='black', fontsize=9, ha='center', va='bottom')

# --- Superficie EXTERIOR suavizada (dist_2 → punto medio) ---
faces_ext = []
for i in range(N_SMOOTH):
    j = (i + 1) % N_SMOOTH
    face = [
        [x2s[i], y2s[i], -z2s[i]],
        [x2s[j], y2s[j], -z2s[j]],
        [xms[j], yms[j], -zms[j]],
        [xms[i], yms[i], -zms[i]],
    ]
    faces_ext.append(face)
ax.add_collection3d(Poly3DCollection(faces_ext, facecolors='cyan', alpha=0.45, edgecolor='none'))

# --- Superficie INTERIOR suavizada (dist_1 → punto medio) ---
faces_int = []
for i in range(N_SMOOTH):
    j = (i + 1) % N_SMOOTH
    face = [
        [x1s[i], y1s[i], -z1s[i]],
        [x1s[j], y1s[j], -z1s[j]],
        [xms[j], yms[j], -zms[j]],
        [xms[i], yms[i], -zms[i]],
    ]
    faces_int.append(face)
ax.add_collection3d(Poly3DCollection(faces_int, facecolors='orange', alpha=0.45, edgecolor='none'))

# --- Tapa plana entre dist_1 y dist_2 en z=0 ---
faces_top = []
for i in range(N_SMOOTH):
    j = (i + 1) % N_SMOOTH
    face = [
        [x1s[i], y1s[i], 0],
        [x1s[j], y1s[j], 0],
        [x2s[j], y2s[j], 0],
        [x2s[i], y2s[i], 0],
    ]
    faces_top.append(face)
ax.add_collection3d(Poly3DCollection(faces_top, facecolors='lightgray', alpha=0.25, edgecolor='none'))

# --- Cilindros de referencia ---
def dibujar_cilindro(ax, radio, z_min, z_max, color='black', alpha=0.2):
    theta  = np.linspace(0, goal * np.pi, 120)
    z      = np.linspace(z_min, z_max, 2)
    tg, zg = np.meshgrid(theta, z)
    ax.plot_surface(radio * np.cos(tg), radio * np.sin(tg), zg,
                    color=color, alpha=alpha)

dibujar_cilindro(ax, goal,        0, -Dgoal, color='black')

# Círculos guía punteados en z=0
theta_g = np.linspace(0, goal * np.pi, 200)
ax.plot((goal)        * np.cos(theta_g), goal        * np.sin(theta_g),
        np.zeros(200), linestyle='dotted', color='black', linewidth=1.3, label='Guía interior')

# --- Ejes y título ---
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title(f'Soldadura Circular 3D — {hoja}')
ax.view_init(elev=30, azim=60)

plt.legend(loc='upper left', fontsize=8)
plt.tight_layout()
plt.show()
