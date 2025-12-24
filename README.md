# PDB to Gene Info Transformer

This Python tool automates the process of extracting gene names, protein descriptions, and organism info from a list of PDB IDs. It bridges the gap between structural data (PDB) and biological information (UniProt).

## ✨ Features
- Fetches metadata from **RCSB PDB** via web requests.
- Integrates with **UniProt REST API** for detailed gene/protein mapping.
- Processes Excel files using **Pandas**.
- Includes error handling and API rate limiting.

## 🛠 Installation
1. Clone the repo: `git clone https://github.com/USERNAME/REPO-NAME.git`
2. Install dependencies: `pip install -r requirements.txt`

## 🚀 Usage
Place your Excel file (e.g., `PHARMMAPPER_PDBID_WEB.xlsx`) in the directory and run:
```python
python pdb_id_gene_transformer.py