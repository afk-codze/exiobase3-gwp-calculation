# EXIOBASE 3 GWP Calculation

This repository contains a **personal project** developed to compute greenhouse gas (GHG) supply-chain multipliers using the EXIOBASE 3 dataset. All rights to the data provided by EXIOBASE remain with the EXIOBASE team, and any use or redistribution of their data is subject to the terms and conditions of their license.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Project Structure](#project-structure)
3. [Installation & Requirements](#installation--requirements)
4. [Usage](#usage)
5. [Methodology Overview](#methodology-overview)
7. [Data Licensing & Disclaimer](#data-licensing--disclaimer)

---

## Project Overview

This project:
- Parses EXIOBASE 3 data (a multi-regional input-output dataset).
- Computes the Leontief inverse and other I/O system matrices.
- Aggregates specified GHG flows (CO₂, CH₄, N₂O) into a single Global Warming Potential (GWP100) row using AR5 100-year factors (1, 28, 265).
- Calculates supply-chain multipliers (kg CO₂-eq per unit of sector output).
- Exports the results to a CSV file.

---

## Project Structure

```
.
├── exiobase_gwp_factors.csv      # Output CSV containing computed GWP multipliers
├── test_exiobase.py              # Script for testing EXIOBASE 3 computations
├── IOT_2022_pxp/                 # Folder containing EXIOBASE 3 dataset
```

---

## Installation & Requirements

1. **Python 3.7+** (recommended).
2. **[pymrio](https://pymrio.readthedocs.io/en/latest/)** – used for parsing EXIOBASE and performing IO analysis.  
   Install with:
   ```bash
   pip install pymrio
   ```
3. **Other packages**: pandas, numpy (and logging, part of the standard library).

_Optional:_ Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install pymrio pandas numpy
```

If you have a `requirements.txt` file, run:
```bash
pip install -r requirements.txt
```

---

## Usage

1. **Place your EXIOBASE 3 data** in a folder (e.g., `./IOT_2022_pxp`).
2. **Adjust the data path** in `test_exiobase.py` if needed:
   ```python
   path_to_exiobase3 = "./IOT_2022_pxp"
   ```
3. **Run the script**:
   ```bash
   python test_exiobase.py
   ```
4. **Output**: A CSV file named `exiobase_gwp_factors.csv` containing the computed GWP100 multipliers with an index of (Region, Sector).

---

## Methodology Overview

1. **Parsing EXIOBASE 3**:  
   The script uses `pymrio.parse_exiobase3` to load the input-output tables and extension data (S matrix).

2. **Computing the Leontief Inverse**:  
   After calling `exio.calc_all()`, the Leontief inverse \( L = (I - A)^{-1} \) is computed.

3. **Aggregating GHG Flows**:  
   It selects GHG flows (CO₂, CH₄, N₂O) from the S matrix, multiplies them by AR5 GWP100 factors (1, 28, 265), and sums them into a single row.

4. **Supply-chain Multipliers**:  
   Multiplying the aggregated intensities by \( L \) yields the supply-chain multipliers (kg CO₂-eq per unit of sector output).

5. **Exporting Results**:  
   The final multipliers are saved as a CSV file.

---

## Data Licensing & Disclaimer

This is a **personal project**. The EXIOBASE data used in this project is provided under specific licensing terms. All use, analysis, and redistribution of the EXIOBASE data must comply with those terms. Please refer to the official EXIOBASE documentation or website for full details on licensing and permitted usage.
