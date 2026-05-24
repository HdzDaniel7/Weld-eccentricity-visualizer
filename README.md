# Weld Eccentricity 3D Visualizer

3D visualization tools for circular and linear weld inspection data. Given 8 measured points per weld (inner edge radius, outer edge radius, and center depth at 8 angular positions)against a reference used as 0, the scripts generate smooth 3D surface models of the weld geometry using cubic spline interpolation.

\---

## Repository Structure

```
weld-eccentricity-visualizer/
│
├── Soldadura_Circular_3D.py          # Circular weld visualizer
├── Soldadura_Lineal_3D.py            # Linear weld visualizer
├── Tabla de excentricidad.xlsm # Example data file (fictitious data)
├── .gitignore
└── README.md
```

\---

## What the Scripts Do

### `Soldadura_Circular_3D.py` — Circular Weld

Models a weld that runs around a circular joint (e.g., a pipe or cylindrical part).

* Reads 8 measurement points at angular positions (e.g., 0°, 45°, 90°, 135°, 180°, 225°, 270°, 315°)
* Each point has: **inner edge radius** (`dist_1`), **outer edge radius** (`dist_2`), and **weld depth**
* Interpolates all 4 curves circularly with a cubic spline (200-point resolution) so the result is a smooth ring, not a hexagon
* Builds two 3D surfaces: outer wall (cyan) and inner wall (orange), plus a flat top annulus (gray)
* Original 8 measured points remain visible as distinct markers
* Reference cylinders and dotted guide circles are drawn at fixed radii



### `Soldadura_Lineal_3D.py` — Linear Weld

Models a weld that runs in a straight line (e.g., a butt weld or fillet on a flat plate).

* Uses the same 8 measurement points, distributed equally along the X axis
* Interpolates with a cubic spline along X; the weld profile is shown symmetrically on ±Y
* Builds the same surface structure (cyan outer wall, orange inner wall, gray top)
* End caps are drawn at both ends of the weld bead
* Original measurement points remain visible as distinct markers



---

## Data Format

Both scripts read from an Excel file (`.xlsm` or `.xlsx`). The relevant block is the **first measurement range only** (`df.iloc[8:16]`), which maps to approximately rows 9–16 in Excel (assuming row 1 is the header).

|Script column index|Excel column|Content|
|-|-|-|
|1|B|Angle of measurement (degrees)|
|2|N|`dist_1` — inner edge radius (mm)|
|3|O|`dist_2` — outer edge radius (mm)|
|5|P|Weld center depth (mm)|

> The file `Tabla de excentricidad.xlsm` included in this repo uses exactly this layout with It contains VBA macros and ActiveX controls that drive the calculation tables — *enable macros when prompted by Excel* to ensure the workbook functions correctly. No sensitive data, paths, or company references are present in this file.

---

## Requirements

Python 3.8+ and the following libraries (auto-installed on first run if missing):

|Library|Purpose|
|-|-|
|`numpy`|Array math|
|`pandas`|Excel reading|
|`matplotlib`|3D plotting|
|`openpyxl`|`.xlsx` / `.xlsm` engine|
|`scipy`|Cubic spline interpolation|

Install manually if preferred:

```bash
pip install numpy pandas matplotlib openpyxl scipy
```

---

## Usage

### Option A — Example data (no Excel needed)

Inside each script there are two clearly marked blocks. By default, **Option A** (example data) is active and **Option B** (Excel) is commented out.

Just run:

```bash
python Soldadura_Circular_3D.py
python Soldadura_Lineal_3D.py
```

### Option B — Your own Excel file

1. Open the script and find the `FUENTE DE DATOS` section.
2. Comment out Option A (add `#` to each line).
3. Uncomment Option B (remove `#` from each line).
4. Set the correct path to your file in `archivo_excel`.
5. Pass the sheet name as a command-line argument:

```bash
python Soldadura_Circular_3D.py MySheetName
python Soldadura_Lineal_3D.py  MySheetName
```

**Important:** Your Excel file must follow the column layout described in the [Data Format](#data-format) section above. Use `Tabla de excentricidad.xlsm` as a structural reference.

---

## Switching Between Modes — Quick Reference

```python
# ── Inside each script, find this block: ──────────────────────────────────────

# --- OPTION A: Example data (active by default) ---
USE_EXAMPLE_DATA = True       # <── set to False to use Excel
angles_1 = np.array([...])
...

# --- OPTION B: Read from Excel (uncomment and set USE_EXAMPLEDATA = False) ---
# USE_EXAMPLE_DATA = False
# hoja = sys.argv[1]
# archivo_excel = "path/to/your/file.xlsm"
# ...
```

---

## Output Examples

### Circular weld (`Soldadura_Circular_3D.py`)

A smooth toroidal-section surface showing the weld bead running around a circular joint. The 6 original measurement points are highlighted in blue (outer edge), green (inner edge), and red diamonds (depth).

### Linear weld (`Soldadura_Lineal_3D.py`)

The same weld bead "unrolled" into a straight line along the X axis. Both scripts share the same data structure so you can compare circular vs. linear geometry from the same measurement.

---

### Circular weld

![Circular weld example](images/circular\_weld\_example.png)

### Circular weld

![circular_weld_example_2](images/circular\_weld\_example_2.png)

### Linear weld

![Linear weld example](images/linear\_weld\_example.png)

## Privacy Note

Only a fictitious example file is provided.

---

## License

This project is shared for reference and educational purposes. No specific license is applied — contact the author for usage permissions.

