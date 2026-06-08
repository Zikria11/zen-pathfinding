# ZEN – Risk‑Aware Tie‑Breaking for Shortest‑Path‑Preserving A\* Search

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20599031.svg)](https://doi.org/10.5281/zenodo.20599031)

This repository contains the source code and experimental data for the paper  

**"ZEN: Risk‑Aware Tie‑Breaking for Shortest‑Path‑Preserving A\* Search"**  
Zikria Akhtar (2026)

## Overview

**ZEN** (Zonal‑risk Exploration Navigator) is a simple but effective extension of the classical A\* algorithm. It preserves the optimal path length (number of steps) of A\* while significantly reducing cumulative risk by using a local obstacle‑density risk score as a secondary tie‑breaker in the priority queue.

- **Risk score** for a cell = number of obstacles within a Chebyshev radius of 2 (a 5×5 neighbourhood).  
- **No tunable parameters** – ZEN works out of the box.  
- **100% success rate** on solvable maps (unlike chance‑constrained or CVaR‑based methods, which often fail).  
- Evaluated on **216 benchmark maps** (60 real‑world city maps + 156 Dragon Age Origins game levels) from the Moving AI benchmark suite.

### Key results from the paper

| Metric | ZEN vs. A* |
|--------|-------------|
| Path length | **Identical** (optimal on every successful run) |
| Path risk reduction (paired, mean) | **68.6%** |
| Node expansions reduction (best case) | up to **98.3%** |
| Speedup (best case) | up to **28.5×** |
| Overall success rate | **84.4%** (A*: 84.4%; chance‑constrained: 10.8%) |

ZEN never sacrifices path length for safety; it only chooses a different shortest path when a safer one exists with the same length.

## Repository contents

| File | Description |
|------|-------------|
| `z_search_algo.py` | Full Python implementation of ZEN and 11 baseline algorithms (A*, weighted A*, risk‑penalised A*, chance‑constrained A*, CVaR A*, BFS, DFS, Dijkstra, greedy, etc.). |
| `street_map_results.csv` | Benchmark results on 60 city maps (used in the paper’s tables). |
| `dao_results.csv` | Benchmark results on 156 Dragon Age Origins maps. |
| `requirements.txt` | Python dependencies. |
| `LICENSE` | MIT open‑source license. |
| `README.md` | This file. |

## Requirements

- Python 3.10 or higher
- The required packages are listed in `requirements.txt`. Install them with:

```bash
pip install -r requirements.txt
The core algorithm uses only the standard library; the extra packages (pandas, matplotlib, seaborn) are used only for analysis and visualisation. 
```

## Running the code
Reproduce the paper’s results from the provided CSVs
The paper’s tables and figures are generated directly from the two CSV files. You can load and analyse them with pandas, for example:
```bash
python
import pandas as pd

street = pd.read_csv('street_map_results.csv')
dao = pd.read_csv('dao_results.csv')
```
# Average risk of A* and ZEN on street maps
```bash
print(street.groupby('Algorithm')['Path_Risk_Score'].mean())
```
Re‑run the benchmark from scratch (requires the map files)
To re‑run the full benchmark on the street maps, you need the original .map files from the Moving AI benchmark suite (available from Moving AI Lab). Place them in a folder (e.g., street-map/) and run:

```bash
python z_search_algo.py /path/to/street-map/
```
The script will process all .map files in that directory and produce a new CSV with results. The DAO maps can be re‑run similarly if you have the DAO map files.

###### Note: Running the full benchmark on all 216 maps can take several hours on a typical laptop. The provided CSV files contain the exact results used in the paper, so re‑running is only necessary if you want to verify or extend the experiments.

## Reproducibility
All experimental results presented in the paper can be reproduced using the provided CSV files and the code in z_search_algo.py. The exact environment (Python 3.10 on Arch Linux) is described in the paper’s experimental setup section.

## Citation
If you use this code or data in your research, please cite:
```
bibtex
@software{akhtar2026zen,
  author       = {Zikria Akhtar},
  title        = {zen-pathfinding: ZEN algorithm for risk-aware A* tie-breaking},
  year         = 2026,
  publisher    = {Zenodo},
  version      = {v1.0.0},
  doi          = {10.5281/zenodo.20599031},
  url          = {https://doi.org/10.5281/zenodo.20599031}
}
```
If the paper has been published, replace the citation with the official bibliographic information.

## License
This project is licensed under the MIT License – see the LICENCE for details
