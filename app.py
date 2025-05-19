from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
from mysql.connector import Error
from datetime import datetime

app = Flask(__name__, static_folder='static', static_url_path='/static')


app.secret_key = 'supersecretkey'

def create_connection():
    try:
        connection = mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = 'root',
            database = 'data_db'
        )

        if connection.is_connected():
            return connection

    except Error as e:
        print("Mysql Bağlantı Hatası: ", e)
        return None

@app.route('/')
def Home():
    return render_template('login.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    error_message = None

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        print(f"GİRİŞ DENEMESİ: Email = {email}, Şifre = {password}")  # DEBUG MESAJI

        try:
            connection = create_connection()
            if not connection:
                print("Veritabanına bağlanılamadı!")  # DEBUG
                return render_template("login.html", error_message="Veritabanına bağlanılamadı!")

            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM personel WHERE per_mail = %s", (email,))
            user = cursor.fetchone()

        except Exception as e:
            print("❌ HATA:", e)

            return render_template("login.html", error_message="Sunucu hatası!")

        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'connection' in locals() and connection:
                connection.close()

        print(f"VERİTABANINDAN GELEN KULLANICI: {user}")  # DEBUG MESAJI

        if user and user.get('per_sifre') == password:
            session['user'] = {
                'per_id': user['per_id'],
                'per_ad': user['per_ad'],  # Kullanıcının adı
                'per_soyad': user['per_soyad'],  # Kullanıcının soyadı
                'per_mail': user['per_mail'],  # Kullanıcının email adresi
                'per_telefon': user['per_telefon']

            }
            print("GİRİŞ BAŞARILI! Kullanıcı session'a eklendi.")  # DEBUG
            return redirect(url_for('index'))
        else:
            error_message = "Geçersiz email veya şifre!"
            return render_template("login.html", error_message = error_message)


@app.route('/index')
def index():
    if 'user' not in session:
        print("Kullanıcı oturum açmamış! Tekrar login sayfasına yönlendiriliyor...")
        return redirect(url_for('Home'))

    print(f"SESSION VAR! Kullanıcı: {session['user']}")  # DEBUG

    connection = create_connection()
    if not connection:
        return "Veritabanı bağlantı hatası!"

    try:
        cursor = connection.cursor(dictionary = True)
        cursor.execute("SELECT * FROM sikayetler")
        complaints = cursor.fetchall()

        print(f"Veritabanından çekilen şikayetler: {complaints}")

        return render_template("index.html", user=session['user'], complaints = complaints)

    finally:
        cursor.close()
        connection.close()

@app.route('/check_session')
def check_session():
    if 'user' in session:
        return f"🟢 SESSION VAR! Kullanıcı: {session['user']}"
    return "🔴 SESSION YOK!"



@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        user = session['user']
        return f"Hoşgeldiniz! İsim: {user['per_ad']}! Email: {user['per_mail']}!"



    return "Hata kullanıcı bulunamadı" and redirect(url_for('login'))

@app.route('/logout')
def logout():
    # session.pop('user', None)  # Kullanıcı session'ı sil
    # return redirect(url_for('Home'))  # Kullanıcıyı giriş sayfasına yönlendir
    session.pop('user', None)  # Oturumu sil
    response = redirect(url_for('Home'))  # Kullanıcıyı giriş sayfasına yönlendir
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'  # Önbellek kapatma
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# @app.route('/get_complaint_details/<int:complaint_id>')
# def get_complaint_details(complaint_id):
#     connection = create_connection()
#     if not connection:
#         return jsonify({'error': 'Veritabanına bağlanılamadı'})
#
#     cursor = connection.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM sikayetler WHERE idsikayetler = %s", (complaint_id,))
#     complaint = cursor.fetchone()
#     return jsonify(complaint) if complaint else jsonify({'error': 'Şikayet bulunamadı'})

@app.route('/get_complaint_details/<int:complaint_id>')
def get_complaint_details(complaint_id):
    print(f"Şikayet Detayları İsteniyor: ID = {complaint_id}")  # DEBUG
    connection = create_connection()
    if not connection:
        return jsonify({'error': 'Veritabanına bağlanılamadı'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT sikayetKonu, sikayetAciklama, sikayetTarih, sikayetResim, sikayetEnlem, sikayetBoylam, durum  FROM sikayetler WHERE idsikayetler = %s", (complaint_id,))
        complaint = cursor.fetchone()

        print(f"Veritabanından Gelen Sonuç: {complaint}")  # DEBUG

        if not complaint:
            print("Hata: Şikayet bulunamadı!")  # DEBUG
            return jsonify({'error': 'Şikayet bulunamadı'}), 404

            # Eğer enlem ve boylam Decimal tipindeyse string'e çevir
        if 'sikayetEnlem' in complaint and 'sikayetBoylam' in complaint:
            complaint['sikayetEnlem'] = str(complaint['sikayetEnlem'])
            complaint['sikayetBoylam'] = str(complaint['sikayetBoylam'])

            # Eğer resim yoksa varsayılan bir resim ata
        if not complaint['sikayetResim']:
            complaint['sikayetResim'] = "/static/images/default.jpg"

        print(f"Dönen JSON Yanıt: {complaint}")  # DEBUG

        return jsonify(complaint)
    finally:
        cursor.close()
        connection.close()


@app.route('/sikayet_durum_guncelle/<int:complaint_id>/<int:yeni_durum>', methods=['POST'])
def sikayet_durum_guncelle(complaint_id, yeni_durum):
    connection = create_connection()
    if not connection:
        return "Veritabanı bağlantı hatası", 500

    try:
        cursor = connection.cursor()
        cursor.execute("UPDATE sikayetler SET durum = %s WHERE idsikayetler = %s", (yeni_durum, complaint_id))
        connection.commit()
        return '', 204  # Başarılı ama içerik dönme
    finally:
        cursor.close()
        connection.close()


if __name__ == '__main__':

    app.run(debug = True, port = 5000)