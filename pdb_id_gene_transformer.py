"""
Project: PDB ID to Gene Information Transformer
Author: Toritaki (Çağatay YETİM)
License: MIT
Description: Automates biological data mapping via UniProt and RCSB APIs.
"""
import pandas as pd
from Bio import PDB
from Bio.PDB import PDBList
import requests
import time

def get_gene_info_from_uniprot(uniprot_id: str) -> dict:
    """UniProt ID'den gen bilgilerini al"""
    try:
        url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            result = {
                'gene_name': None,
                'protein_name': None,
                'organism': None
            }
            
            # Gen adı
            if 'genes' in data and data['genes']:
                result['gene_name'] = data['genes'][0].get('geneName', {}).get('value')
            
            # Protein adı
            if 'proteinDescription' in data:
                result['protein_name'] = data['proteinDescription'].get('recommendedName', {}).get('fullName', {}).get('value')
            
            # Organizma
            if 'organism' in data:
                result['organism'] = data['organism'].get('scientificName')
            
            return result
    except:
        pass
    
    return None

def process_pdb_ids_with_biopython(pdb_ids: list):
    """BioPython ile PDB ID'leri işle"""
    results = []
    
    for pdb_id in pdb_ids:
        print(f"İşleniyor: {pdb_id}")
        
        try:
            # PDB dosyasını indir (isteğe bağlı)
            pdbl = PDBList()
            # pdbl.retrieve_pdb_file(pdb_id, pdir='./pdb_files')  # İndirmek isterseniz
            
            # PDB parser
            parser = PDB.PDBParser(QUIET=True)
            
            # Online PDB'den bilgi al
            url = f"https://files.rcsb.org/view/{pdb_id}.pdb"
            response = requests.get(url)
            
            if response.status_code == 200:
                # HEADER kısmını oku
                lines = response.text.split('\n')
                title = ""
                for line in lines:
                    if line.startswith('HEADER'):
                        title = line[10:].strip()
                        break
                
                # UniProt ID ara
                uniprot_id = None
                for line in lines:
                    if 'DBREF' in line and 'UNP' in line:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if 'UNP' in part and i+1 < len(parts):
                                uniprot_id = parts[i+1]
                                break
                        if uniprot_id:
                            break
                
                # UniProt'tan gen bilgilerini al
                gene_info = None
                if uniprot_id:
                    gene_info = get_gene_info_from_uniprot(uniprot_id)
                
                results.append({
                    'PDB_ID': pdb_id,
                    'TITLE': title,
                    'UNIPROT_ID': uniprot_id,
                    'GENE_NAME': gene_info['gene_name'] if gene_info else None,
                    'PROTEIN_NAME': gene_info['protein_name'] if gene_info else None,
                    'ORGANISM': gene_info['organism'] if gene_info else None
                })
            else:
                results.append({
                    'PDB_ID': pdb_id,
                    'TITLE': None,
                    'UNIPROT_ID': None,
                    'GENE_NAME': None,
                    'PROTEIN_NAME': None,
                    'ORGANISM': None
                })
            
        except Exception as e:
            print(f"Hata: {pdb_id} - {e}")
            results.append({
                'PDB_ID': pdb_id,
                'TITLE': None,
                'UNIPROT_ID': None,
                'GENE_NAME': None,
                'PROTEIN_NAME': None,
                'ORGANISM': None
            })
        
        time.sleep(1)  # API limitleri için
    
    return pd.DataFrame(results)

# Kullanım
if __name__ == "__main__":
    # Excel dosyasını oku
    df = pd.read_excel("PHARMMAPPER _PDBID_WEB.xlsx")
    
    # PDB ID sütununu belirle
    # İhtiyacınıza göre sütun adını değiştirin
    pdb_column = 'PDB_ID'  # veya 'pdb_id' vb.
    
    if pdb_column in df.columns:
        pdb_ids = df[pdb_column].dropna().astype(str).str.strip().tolist()
        
        # Gen bilgilerini al
        result_df = process_pdb_ids_with_biopython(pdb_ids)
        
        # Orijinal DataFrame ile birleştir
        final_df = pd.merge(df, result_df, on='PDB_ID', how='left')
        
        # Sonuçları kaydet
        final_df.to_excel("pharmmapper_with_gene_info.xlsx", index=False)
        print("İşlem tamamlandı. Sonuçlar 'pharmmapper_with_gene_info.xlsx' dosyasına kaydedildi.")
    else:
        print(f"'{pdb_column}' sütunu bulunamadı. Mevcut sütunlar: {list(df.columns)}")