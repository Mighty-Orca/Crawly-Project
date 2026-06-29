from datetime import datetime
import re

# Mapping nama bulan Indonesia → angka
BULAN = {
    'januari': 1, 'februari': 2, 'maret': 3, 'april': 4,
    'mei': 5, 'juni': 6, 'juli': 7, 'agustus': 8,
    'september': 9, 'oktober': 10, 'november': 11, 'desember': 12,
    # Singkatan bahasa Inggris (Republika pakai "May", "Jun", dll)
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
    'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
    'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
}


def parse_date(tanggal_str):
    """
    Coba parse string tanggal dari berbagai format portal ke objek datetime.
    Return datetime atau None kalau gagal.
    """
    if not tanggal_str or tanggal_str == '-':
        return None

    text = tanggal_str.lower().strip()

    # Hapus nama hari (Senin, Selasa, dst) dan kata tidak perlu
    for hari in ['senin', 'selasa', 'rabu', 'kamis', 'jumat', 'sabtu', 'minggu']:
        text = text.replace(hari, '')

    # Hapus "diterbitkan", "oleh", "wib", "|", koma
    for buang in ['diterbitkan', 'wib', 'wita', 'wit', '|', ',']:
        text = text.replace(buang, '')

    text = text.strip()

    # Format 1: "20 mei 2026" atau "20 mei 2026 12:50"
    match = re.search(r'(\d{1,2})\s+([a-z]+)\s+(\d{4})', text)
    if match:
        tgl, bln_str, thn = match.groups()
        bulan = BULAN.get(bln_str.lower())
        if bulan:
            try:
                return datetime(int(thn), bulan, int(tgl))
            except:
                pass

    # Format 2: "2026-06-01" atau "2026/06/01"
    match = re.search(r'(\d{4})[-/](\d{2})[-/](\d{2})', text)
    if match:
        thn, bln, tgl = match.groups()
        try:
            return datetime(int(thn), int(bln), int(tgl))
        except:
            pass

    # Format 3: "01/06/2026" atau "01-06-2026"
    match = re.search(r'(\d{2})[-/](\d{2})[-/](\d{4})', text)
    if match:
        tgl, bln, thn = match.groups()
        try:
            return datetime(int(thn), int(bln), int(tgl))
        except:
            pass

    return None


def filter_by_date(articles, date_from=None, date_to=None):
    """
    Filter list artikel berdasarkan rentang tanggal.
    date_from & date_to berupa string 'YYYY-MM-DD' atau None.
    """
    if not date_from and not date_to:
        return articles  # Tidak ada filter, kembalikan semua

    # Parse date_from dan date_to
    dt_from = datetime.strptime(date_from, '%Y-%m-%d') if date_from else None
    dt_to   = datetime.strptime(date_to,   '%Y-%m-%d') if date_to   else None

    filtered = []
    for artikel in articles:
        dt_artikel = parse_date(artikel.get('tanggal', '-'))

        if dt_artikel is None:
            # Kalau tanggal tidak bisa di-parse, tetap masukkan
            filtered.append(artikel)
            continue

        if dt_from and dt_artikel < dt_from:
            continue
        if dt_to and dt_artikel > dt_to:
            continue

        filtered.append(artikel)

    return filtered