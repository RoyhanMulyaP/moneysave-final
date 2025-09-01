from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from config.koneksi import get_connection
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from functools import wraps
import base64
import re
import os

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Silakan login terlebih dahulu!", "warning")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function

app = Flask(__name__)
app.secret_key = 'nafroyin9947'
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads', 'kartu')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

UPLOAD_FOLDER_WAJAH = os.path.join(app.root_path, 'static', 'uploads', 'wajah')
os.makedirs(UPLOAD_FOLDER_WAJAH, exist_ok=True)

@app.context_processor
def inject_user_id():
    return dict(user_id=session.get('user_id'))

@app.route('/')
def home():
    return render_template('landing_menu.html')

@app.route("/form")
def form_page():
    return render_template('form.html')

@app.route("/sign_in")
def sign_in_page():
    return render_template("sign_in.html")

@app.route("/buka_rekening")
def buka_rekening_page():
    return render_template("buka_rekening.html")

@app.route("/isi_formulir")
def isi_formulir_page():
    return render_template("isi_formulir.html")

@app.route("/setoran_selesai")
def setoran_selesai_page():
    return render_template("setoran_selesai.html")

@app.route("/buat_akun")
def buat_akun_page():
    return render_template("buat_akun.html")

@app.route("/verifikasi_kartu")
def verifikasi_kartu_page():
    return render_template("verifikasi_kartu.html")

@app.route("/foto")
def foto_page():
    return render_template("foto.html")

@app.route("/verifikasi_wajah")
def verifikasi_wajah_page():
    return render_template("verifikasi_wajah.html")

@app.route("/foto_wajah")
def foto_wajah_page():
    return render_template("foto_wajah.html")

# @app.route("/verifikasi_data")
# def verifikasi_data_page():
#     return render_template("verifikasi_data.html")

# @app.route("/isi_no_rek")
# def isi_no_rek_page():
#     return render_template("isi_no_rek.html")

@app.route("/upload_dokumen")
def upload_dokumen_page():
    return render_template("upload_dokumen.html")

# @app.route("/sign_up")
# def sign_up_page():
#     return render_template("sign_up.html")

# @app.route("/validasi_data")
# def validasi_data_page():
#     return render_template("validasi_data.html")

# @app.route("/beranda")
# def beranda_page():
#     return render_template('beranda.html')

@app.route("/barcode")
def barcode_page():
    return render_template('barcode.html')

@app.route("/riwayat")
def riwayat_page():
    return render_template('riwayat.html')

@app.route("/notifikasi")
def notifikasi_page():
    return render_template('notifikasi.html')

# @app.route("/profile")
# def profile_page():
#     return render_template('profile.html')

from flask import request, session, redirect, url_for, flash
from werkzeug.security import check_password_hash

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        flash("Email dan password harus diisi!", "error")
        return redirect(url_for("sign_in_page"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Ambil user berdasarkan email
    cursor.execute("SELECT id, email, password FROM user WHERE email=%s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        flash("Email tidak ditemukan!", "error")
        return redirect(url_for("sign_in_page"))

    # Cek password hash
    if not check_password_hash(user["password"], password):
        flash("Password salah!", "error")
        return redirect(url_for("sign_in_page"))

    # Login berhasil, simpan session
    session["user_id"] = user["id"]

    # Redirect ke halaman beranda
    return redirect(url_for("beranda_page"))

@app.route('/logout')
def logout():
    session.clear()  # Hapus semua data session
    return redirect(url_for('home'))

@app.route('/simpan_user', methods=['POST'])
def simpan_user():
    nik = request.form.get('nik')
    nama = request.form.get('nama')
    tgl_lahir = request.form.get('tgl_lahir')
    agama = request.form.get('agama')
    alamat = request.form.get('alamat')
    tujuan = request.form.get('tujuan')
    email = request.form.get('email')
    hp = request.form.get('hp')

    conn = get_connection()
    cursor = conn.cursor()

    sql_user = """
        INSERT INTO user (nik, nama, tgl_lahir, agama, alamat, tujuan, email, hp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql_user, (nik, nama, tgl_lahir, agama, alamat, tujuan, email, hp))

    user_id = cursor.lastrowid
    session['user_id'] = user_id

    sql_rekening = """
        INSERT INTO rekening (user_id, nik, nama, status)
        VALUES (%s, %s, %s, 'pending')
    """
    cursor.execute(sql_rekening, (user_id, nik, nama))
    rekening_id = cursor.lastrowid
    
    sql_verfikasi = """
        INSERT INTO verifikasi (user_id, nik, nama)
        VALUES (%s, %s, %s)"""
        
    cursor.execute(sql_verfikasi, (user_id, nik, nama))
    
    sql_target = """
        INSERT INTO target (rekening_id, nama)
        VALUES (%s, %s)
    """
    cursor.execute(sql_target, (rekening_id, nama))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('setoran_pertama'))

@app.route('/setoran_pertama')
def setoran_pertama():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('home'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, status, created_at FROM rekening WHERE user_id=%s", (user_id,))
    rekening = cursor.fetchone()

    if rekening:
        created_time = rekening['created_at']
        end_time = created_time + timedelta(hours=24)
        remaining_seconds = int((end_time - datetime.now()).total_seconds())

        if remaining_seconds <= 0 and rekening['status'] == 'pending':
            cursor.execute("UPDATE rekening SET status='expired' WHERE id=%s", (rekening['id'],))
            conn.commit()
            rekening['status'] = 'expired'
            remaining_seconds = 0
    else:
        remaining_seconds = 0

    cursor.close()
    conn.close()

    if rekening and rekening['status'] == 'confirmed':
        return redirect(url_for('setoran_selesai_page'))

    return render_template('setoran_pertama.html', countdown=remaining_seconds)


@app.route('/upload_foto', methods=['POST'])
def upload_foto():
    try:
        user_id = request.form.get('userId')
        image_data = request.form.get('fotoKartu')

        if not user_id or not image_data:
            return jsonify({"error": "Data tidak lengkap"}), 400

        image_data = re.sub(r'^data:image/.+;base64,', '', image_data)
        img_bytes = base64.b64decode(image_data)

        filename = secure_filename(f"{user_id}_kartu.jpg")
        relative_path = f"uploads/kartu/{filename}"  # relatif ke folder static
        absolute_path = os.path.join(app.root_path, 'static', relative_path)

        with open(absolute_path, 'wb') as f:
            f.write(img_bytes)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE verifikasi SET kartu=%s WHERE user_id=%s",
            (relative_path, user_id)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Foto berhasil diupload!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload_wajah', methods=['POST'])
def upload_wajah():
    try:
        user_id = request.form.get('userId')
        image_data = request.form.get('fotoWajah')

        if not user_id or not image_data:
            return jsonify({"error": "Data tidak lengkap"}), 400

        image_data = re.sub(r'^data:image/.+;base64,', '', image_data)
        img_bytes = base64.b64decode(image_data)

        filename = secure_filename(f"{user_id}_wajah.jpg")
        relative_path = f"uploads/wajah/{filename}"
        absolute_path = os.path.join(UPLOAD_FOLDER_WAJAH, filename)

        with open(absolute_path, 'wb') as f:
            f.write(img_bytes)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE verifikasi SET wajah=%s WHERE user_id=%s",
            (relative_path, user_id)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Foto wajah berhasil diupload!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/verifikasi_data")
def verifikasi_data_page():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('home'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT nik, nama, tgl_lahir, agama, alamat FROM user WHERE id=%s",
        (user_id,)
    )
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template("verifikasi_data.html", user=user_data)
    
@app.route("/update_jenis_kelamin", methods=["POST"])
def update_jenis_kelamin():
    try:
        user_id = request.form.get("userId")
        jenis_kelamin = request.form.get("jenis_kelamin")

        if not user_id or not jenis_kelamin:
            return jsonify({"success": False, "error": "Data tidak lengkap"})

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE user SET jenis_kelamin=%s WHERE id=%s",
            (jenis_kelamin, user_id)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/isi_no_rek")
def isi_no_rek_page():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('home'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT no_rek, nama, created_at FROM rekening WHERE user_id=%s",
        (user_id,)
    )
    rekening = cursor.fetchone()
    cursor.close()
    conn.close()

    if rekening and rekening.get('created_at'):
        rekening['created_at'] = rekening['created_at'].strftime('%Y-%m-%d')

    return render_template("isi_no_rek.html", rekening=rekening)

@app.route("/update_cabang_rekening", methods=["POST"])
def update_cabang_rekening():
    try:
        user_id = request.form.get("userId")
        cabang = request.form.get("cabang")

        if not user_id or not cabang:
            return jsonify({"success": False, "error": "Data tidak lengkap"})

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE rekening SET cabang=%s WHERE user_id=%s",
            (cabang, user_id)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/validasi_data")
def validasi_data_page():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('home'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT nik, nama, tgl_lahir, agama, alamat, jenis_kelamin, email, hp
        FROM user WHERE id=%s
    """, (user_id,))
    user_data = cursor.fetchone()

    cursor.execute("""
        SELECT no_rek, nama AS nama_rekening, cabang, created_at
        FROM rekening WHERE user_id=%s
    """, (user_id,))
    rekening_data = cursor.fetchone()

    cursor.close()
    conn.close()
    
    if rekening_data and rekening_data.get("created_at"):
        rekening_data["created_at"] = rekening_data["created_at"].strftime("%Y-%m-%d")

    return render_template("validasi_data.html", user=user_data, rekening=rekening_data)


@app.route("/update_data_lengkap", methods=["POST"])
def update_data_lengkap():
    try:
        user_id = request.form.get("userId")
        if not user_id:
            return jsonify({"success": False, "error": "User ID tidak ditemukan"})

        nik = request.form.get("nik")
        nama = request.form.get("nama")
        tgl_lahir = request.form.get("tgl_lahir")
        agama = request.form.get("agama")
        alamat = request.form.get("alamat")
        jenis_kelamin = request.form.get("jenis_kelamin")
        email = request.form.get("email")
        hp = request.form.get("hp")

        no_rek = request.form.get("no_rek")
        nama_rekening = request.form.get("nama_rekening")
        cabang = request.form.get("cabang")
        tgl_rekening = request.form.get("tgl_rekening")

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE user
            SET nik=%s, nama=%s, tgl_lahir=%s, agama=%s,
                alamat=%s, jenis_kelamin=%s, email=%s, hp=%s
            WHERE id=%s
        """, (nik, nama, tgl_lahir, agama, alamat, jenis_kelamin, email, hp, user_id))

        cursor.execute("""
            UPDATE rekening
            SET no_rek=%s, nama=%s, cabang=%s, created_at=%s
            WHERE user_id=%s
        """, (no_rek, nama_rekening, cabang, tgl_rekening, user_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/sign_up")
def sign_up_page():
    user_id = session.get("user_id") 
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT email FROM user WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template("sign_up.html", user_id=user_id, email=user["email"] if user else "")


@app.route("/sign_up_process", methods=["POST"])
def sign_up_process():
    data = request.get_json()
    user_id = data.get("user_id")
    email = data.get("email")
    password = data.get("password")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT email FROM user WHERE id=%s", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        conn.close()
        return jsonify({"status": "error", "message": "User tidak ditemukan!"})

    if user["email"].lower() != email.lower():
        cursor.close()
        conn.close()
        return jsonify({"status": "error", "message": "Email tidak cocok dengan data di database!"})

    if len(password) < 8:
        cursor.close()
        conn.close()
        return jsonify({"status": "error", "message": "Password minimal 8 karakter!"})

    hashed_password = generate_password_hash(password)
    cursor.execute("UPDATE user SET password=%s WHERE id=%s", (hashed_password, user_id))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"status": "success"})

@app.route('/beranda')
@login_required
def beranda_page():
    user_id = session['user_id']

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, nama, hp FROM user WHERE id=%s", (user_id,))
    user = cursor.fetchone()

    cursor.execute("SELECT id, cabang, no_rek, setoran FROM rekening WHERE user_id=%s", (user_id,))
    rekening = cursor.fetchone()

    target_list = []

    if rekening:
        cursor.execute("""
            SELECT t.id AS target_id,
                   t.tujuan,
                   rek.setoran AS target_uang,
                   GROUP_CONCAT(CONCAT(r.pengeluaran, ':', r.uang) SEPARATOR '|') AS rincian_list
            FROM target t
            LEFT JOIN rincian r ON r.target_id = t.id
            LEFT JOIN rekening rek ON rek.id = t.rekening_id
            WHERE t.rekening_id=%s
            GROUP BY t.id, t.tujuan, rek.setoran
        """, (rekening['id'],))
        rows = cursor.fetchall()

        for t in rows:
            # Parsing rincian_list menjadi list
            rincian_data = []
            if t['rincian_list']:
                for item in t['rincian_list'].split('|'):
                    pengeluaran, uang = item.split(':')
                    rincian_data.append({
                        "pengeluaran": pengeluaran,
                        "uang": float(uang)
                    })
            t['rincian_list'] = rincian_data

            # Hitung total uang terkumpul
            total_uang = sum(r['uang'] for r in rincian_data)
            t['total_uang'] = total_uang
            t['target_uang'] = float(t['target_uang'] or 0)

            # Hitung persen progress (maks 100%)
            t['persen'] = min((total_uang / t['target_uang']) * 100, 100) if t['target_uang'] > 0 else 0

            target_list.append(t)

    conn.close()

    return render_template(
        'beranda.html',
        user=user,
        rekening=rekening,
        target_list=target_list,
        user_id=user_id
    )


@app.route("/simpan_target", methods=["POST"])
@login_required
def simpan_target():
    try:
        user_id = session['user_id']
        data = request.get_json()
        nama_target = data.get("namaTarget")
        tenggat = data.get("tenggatTarget")
        rincian_list = data.get("rincian", [])

        if not nama_target or not tenggat:
            return jsonify({"success": False, "error": "Nama target atau tenggat kosong"})

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM rekening WHERE user_id=%s", (user_id,))
        rekening = cursor.fetchone()
        if not rekening:
            return jsonify({"success": False, "error": "Rekening tidak ditemukan"})
        rekening_id = rekening[0]

        # Selalu insert target baru
        cursor.execute(
            "INSERT INTO target (rekening_id, tujuan, tenggat) VALUES (%s, %s, %s)",
            (rekening_id, nama_target, tenggat)
        )
        target_id = cursor.lastrowid

        # Insert rincian
        for item in rincian_list:
            pengeluaran = item.get("pengeluaran")
            uang = item.get("uang") or 0
            cursor.execute(
                "INSERT INTO rincian (target_id, pengeluaran, uang) VALUES (%s, %s, %s)",
                (target_id, pengeluaran, uang)
            )

        conn.commit()

        cursor.execute("SELECT SUM(uang) FROM rincian WHERE target_id=%s", (target_id,))
        total_uang = cursor.fetchone()[0] or 0

        cursor.close()
        conn.close()

        return jsonify({"success": True, "total_uang": total_uang})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/profile")
def profile_page():
    user_id = session.get("user_id")  # ambil user_id dari session
    if not user_id:
        return redirect(url_for("home"))  # kalau belum login, redirect ke login

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Ambil nama user dari database
    cursor.execute("SELECT nama FROM user WHERE id=%s", (user_id,))
    user = cursor.fetchone()  # akan berisi dict seperti {'nama': 'Fahri Maulana'}
    
    cursor.close()
    conn.close()

    return render_template("profile.html", user=user)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
