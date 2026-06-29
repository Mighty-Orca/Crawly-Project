from app import create_app

app = create_app()

if __name__ == '__main__':
    # debug=True → auto-reload kalau ada perubahan kode (jangan pakai di produksi)
    app.run(debug=True, port=5000)
