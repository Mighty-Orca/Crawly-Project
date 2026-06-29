import os

class Config:
    # Secret key untuk session Flask (wajib ada)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-ganti-di-produksi'
    
    # Folder hasil crawling disimpan
    RESULTS_FOLDER = os.path.join(os.path.dirname(__file__), 'results')
    
    # Akun user (hardcoded, sesuai scope skripsi — tidak pakai database)
    USERS = {
        'admin': 'admin123',
        'orca': 'orca123'
    }
