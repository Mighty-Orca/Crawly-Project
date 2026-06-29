import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from app.utils.csv_exporter import export_to_csv
from app.utils.date_filter import filter_by_date

# Import semua crawler
from app.crawler.detik import DetikCrawler
from app.crawler.kompas import KompasCrawler
from app.crawler.republika import RepublikaCrawler
from app.crawler.beritasatu import BeritaSatuCrawler
from app.crawler.rri import RRICrawler
from app.crawler.antara import AntaraCrawler

main_bp = Blueprint('main', __name__)

# Mapping value form → class crawler
CRAWLER_MAP = {
    'detik'     : DetikCrawler,
    'kompas'    : KompasCrawler,
    'republika' : RepublikaCrawler,
    'beritasatu': BeritaSatuCrawler,
    'rri'       : RRICrawler,
    'antara'    : AntaraCrawler
}


# ------------------------------------------------------------------
# Dashboard — halaman utama
# ------------------------------------------------------------------
@main_bp.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.id)


# ------------------------------------------------------------------
# /crawl — proses crawling
# ------------------------------------------------------------------
@main_bp.route('/crawl', methods=['POST'])
@login_required
def crawl():
    keyword  = request.form.get('keyword', '').strip()
    portals  = request.form.getlist('portals')   # list checkbox yang dicentang
    date_from = request.form.get('date_from', '')
    date_to   = request.form.get('date_to', '')

    # Validasi input
    if not keyword:
        flash('Kata kunci tidak boleh kosong.', 'error')
        return redirect(url_for('main.dashboard'))

    if not portals:
        flash('Pilih minimal satu portal berita.', 'error')
        return redirect(url_for('main.dashboard'))

    # Jalankan crawler untuk tiap portal yang dipilih
    all_results = []
    for portal in portals:
        crawler_class = CRAWLER_MAP.get(portal)
        if not crawler_class:
            continue

        print(f"[CRAWL] Mulai crawling {portal} dengan keyword '{keyword}'")
        crawler = crawler_class(
            keyword=keyword,
            date_from=date_from or None,
            date_to=date_to or None
        )
        hasil = crawler.crawl(max_page=5)
        all_results.extend(hasil)
        print(f"[CRAWL] {portal} selesai: {len(hasil)} artikel")

        # Filter berdasarkan tanggal kalau diisi
        all_results = filter_by_date(all_results, date_from or None, date_to or None)

    if not all_results:
    # Kalau habis difilter jadi kosong
        if date_from or date_to:
            flash('Tidak ada artikel dalam rentang tanggal tersebut.', 'error')
        else:
            flash('Tidak ada artikel yang berhasil dikumpulkan. Coba keyword lain.', 'error')
        return redirect(url_for('main.dashboard'))

    # Simpan ke CSV
    results_folder = os.path.join(os.path.dirname(__file__), '..', 'results')
    csv_path = export_to_csv(
        all_results,
        keyword,
        username=current_user.id,
        folder=results_folder
    )
    csv_filename = os.path.basename(csv_path)

    # Kirim ke halaman hasil
    return render_template(
        'result.html',
        username=current_user.id,
        keyword=keyword,
        total=len(all_results),
        portals=portals,
        articles=all_results[:50],   # preview max 50 artikel
        csv_filename=csv_filename
    )


# ------------------------------------------------------------------
# /download/<filename> — download file CSV
# ------------------------------------------------------------------
@main_bp.route('/download/<filename>')
@login_required
def download(filename):
    results_folder = os.path.join(os.path.dirname(__file__), '..', 'results')
    filepath = os.path.abspath(os.path.join(results_folder, current_user.id, filename))
    
    if not os.path.exists(filepath):
        flash('File tidak ditemukan.', 'error')
        return redirect(url_for('main.dashboard'))

    return send_file(filepath, as_attachment=True, download_name=filename)