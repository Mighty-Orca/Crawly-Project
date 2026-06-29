import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod


class BaseCrawler(ABC):
    """
    Class induk untuk semua crawler portal berita.
    Setiap crawler portal (detik, kompas, dll) wajib extend class ini.
    """

    # Header biar request kita keliatan kayak browser biasa
    # Tanpa ini, beberapa situs bisa nolak request kita
    HEADERS = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        )
    }

    def __init__(self, keyword, date_from=None, date_to=None):
        self.keyword   = keyword
        self.date_from = date_from  # string 'YYYY-MM-DD' atau None
        self.date_to   = date_to
        self.results   = []         # list artikel yang berhasil dikumpulkan

    # ------------------------------------------------------------------
    # fetch() — ambil konten HTML dari sebuah URL
    # ------------------------------------------------------------------
    def fetch(self, url):
        """
        Kirim HTTP GET ke url, kembalikan objek BeautifulSoup.
        Kalau gagal (timeout, 404, dll) kembalikan None.
        """
        try:
            response = requests.get(url, headers=self.HEADERS, timeout=10)
            response.raise_for_status()  # lempar error kalau status 4xx/5xx
            return BeautifulSoup(response.text, 'lxml')
        except requests.RequestException as e:
            print(f"[ERROR] Gagal fetch {url}: {e}")
            return None

    # ------------------------------------------------------------------
    # to_dict() — struktur data artikel yang seragam
    # ------------------------------------------------------------------
    def to_dict(self, judul, tanggal, isi, jurnalis, url, portal):
        """
        Semua crawler pakai struktur yang sama supaya CSV-nya konsisten.
        """
        return {
            'judul'    : judul    or '-',
            'tanggal'  : tanggal  or '-',
            'isi'      : isi      or '-',
            'jurnalis' : jurnalis or '-',
            'url'      : url      or '-',
            'portal'   : portal,
        }

    # ------------------------------------------------------------------
    # crawl() — method utama yang dipanggil dari routes.py
    # ------------------------------------------------------------------
    @abstractmethod
    def crawl(self):
        """
        Wajib di-override di setiap crawler portal.
        Harus mengisi self.results dengan list of dict (pakai to_dict).
        """
        pass