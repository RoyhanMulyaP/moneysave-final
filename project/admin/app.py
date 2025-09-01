from flask import Flask, render_template, request, redirect, url_for
from config.koneksi import get_connection
import random
from datetime import datetime

admin = Flask(__name__)

# Halaman utama (menampilkan data rekening yang belum memiliki no_rek)
@admin.route('/')
def home():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    # Tampilkan semua rekening, urutkan terbaru di atas
    cursor.execute("SELECT * FROM rekening ORDER BY created_at DESC")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('setoran.html', data=data)

@admin.route('/setoran')
def setoran_page():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    # Tampilkan semua rekening
    cursor.execute("SELECT * FROM rekening ORDER BY created_at DESC")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("setoran.html", data=data)

@admin.route('/konfirmasi/<int:id>', methods=['POST'])
def konfirmasi_setoran(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT user_id FROM rekening WHERE id=%s", (id,))
    rekening = cursor.fetchone()
    if not rekening or rekening['user_id'] is None:
        cursor.close()
        conn.close()
        return "Error: Rekening tidak memiliki user_id yang valid"

    # Generate nomor rekening 10 digit unik
    no_rek = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    setoran = 10000
    updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute("""
        UPDATE rekening 
        SET no_rek=%s, setoran=%s, updated_at=%s, status='confirmed'
        WHERE id=%s
    """, (no_rek, setoran, updated_at, id))

    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('setoran_page'))


@admin.route("/verifikasi")
def verifikasi_page():
    return render_template("verifikasi.html")

if __name__ == "__main__":
    admin.run(host='0.0.0.0', port=5001, debug=True)
