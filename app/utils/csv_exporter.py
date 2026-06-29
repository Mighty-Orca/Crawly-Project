import csv
import os
from datetime import datetime


def export_to_csv(data, keyword, username='admin', folder='results'):
    """
    Simpan list artikel ke file CSV.
    
    Parameter:
    - data    : list of dict (hasil dari crawler)
    - keyword : kata kunci pencarian (dipakai sebagai nama file)
    - folder  : folder tujuan penyimpanan
    
    Return: path file CSV yang dibuat
    """
    # Buat folder kalau belum ada
    user_folder = os.path.join(folder, username)
    os.makedirs(user_folder, exist_ok=True)

    # Nama file: keyword_tanggal_jam.csv
    # Contoh: banjir_20260601_143022.csv
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_keyword = keyword.replace(' ', '_').lower()
    filename = f"{safe_keyword}_{timestamp}.csv"
    filepath = os.path.join(user_folder, filename)

    # Kolom CSV sesuai struktur to_dict() di base_crawler
    fieldnames = ['judul', 'tanggal', 'isi', 'jurnalis', 'url', 'portal']

    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        # utf-8-sig supaya Excel tidak error pas dibuka (BOM marker)
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"[CSV] Tersimpan: {filepath} ({len(data)} artikel)")
    return filepath