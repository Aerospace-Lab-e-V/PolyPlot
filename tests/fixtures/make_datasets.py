"""Writes the dummy workbook the backend tests use (tests/dataset_1.xlsx).

The numbers are random and mean nothing; they only give the plots and the importer something to work with.
The layout follows real material databases: one row per material, and every quantity as a
"<name> low", "<name> high" and "<name> unit" column.

Run from the repository root:  python tests/fixtures/make_datasets.py
"""
from __future__ import annotations

import random
from pathlib import Path

import pandas as pd

OUTPUT_DIR = Path(__file__).resolve().parents[1]
FAMILIES = ['ABS', 'PA6', 'PC', 'PEEK', 'PLA', 'PP']
ROWS_PER_FAMILY = 8

# name -> (unit, smallest possible value, largest possible value)
QUANTITIES = {
    'Deflection Temperature at 1.8 MPa 264 psi': ('°C', 40, 300),
    'Tensile Strength': ('MPa', 10, 160),
    'Bed Temp': ('°C', 20, 120),
    'CTE linear': ('µm/m-°C', 5, 200),
    'Charpy Impact Notched': ('kJ/m²', 1, 80),
}


def make_rows(quantities: dict[str, tuple[str, float, float]], rng: random.Random) -> pd.DataFrame:
    rows = []
    for family in FAMILIES:
        for number in range(1, ROWS_PER_FAMILY + 1):
            row = {
                'Gruppe': family,
                'Material': family,
                'Hersteller': f'Maker {rng.randint(1, 5)}',
                'Variante': f'{family} grade {number}',
                'URL': f'https://example.com/{family.lower()}/{number}',
            }
            for name, (unit, smallest, largest) in quantities.items():
                low = round(rng.uniform(smallest, largest), 1)
                # about a third of the materials list one value instead of a range
                high = None if rng.random() < 0.33 else round(min(largest, low + rng.uniform(0, (largest - smallest) / 5)), 1)
                row[f'{name} low'] = low
                row[f'{name} high'] = high
                row[f'{name} unit'] = unit
            rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    rng = random.Random(1)  # fixed seed: running the script again gives the same file
    path = OUTPUT_DIR / 'dataset_1.xlsx'
    make_rows(QUANTITIES, rng).to_excel(path, index=False)
    print(f'wrote {path}')


if __name__ == '__main__':
    main()
