import requests
from bs4 import BeautifulSoup
import sys
import os

# --- Konfigurasi ---
base_url = "https://monitoring-siasn.bkn.go.id"
main_page_url = base_url + "/"
renew_captcha_url = base_url + "/renew-captcha"
submit_url = base_url + "/cek-usul"
layanan_kode = "penetapannip" # Kode untuk "Penetapan NIP/NI PPPK"
captcha_image_file = "captcha_bkn.png"

# --- Input Pengguna ---
try:
    nomor_peserta = input("Masukkan Nomor Peserta Anda: ")
    tahun_periode = input(f"Masukkan Tahun Periode (cth: 2024) untuk layanan {layanan_kode}: ")
    if not nomor_peserta or not tahun_periode:
        raise ValueError("Nomor Peserta dan Tahun Periode tidak boleh kosong.")
except ValueError as e:
    print(f"Input tidak valid: {e}")
    sys.exit(1)
except EOFError:
    print("\nInput dibatalkan.")
    sys.exit(1)


# --- Buat Sesi ---
# Menggunakan sesi penting untuk menangani cookies jika diperlukan
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
})

try:
    # --- 1. Dapatkan CSRF Token Awal (dari halaman utama) ---
    print("Mengambil halaman utama untuk mendapatkan CSRF token...")
    response_main = session.get(main_page_url, allow_redirects=True)
    response_main.raise_for_status() # Error jika status bukan 2xx

    soup_main = BeautifulSoup(response_main.text, 'html.parser')
    csrf_token_tag = soup_main.find('meta', {'name': 'csrf-token'})

    if not csrf_token_tag or 'content' not in csrf_token_tag.attrs:
        print("Gagal menemukan CSRF token di halaman utama.")
        # Coba cari di cookies (alternatif umum)
        csrf_cookie = session.cookies.get('XSRF-TOKEN')
        if not csrf_cookie:
             print("Gagal menemukan CSRF token di meta tag atau cookie XSRF-TOKEN.")
             sys.exit(1)
        else:
            print("Menggunakan CSRF token dari cookie XSRF-TOKEN.")
            csrf_token = csrf_cookie
    else:
         csrf_token = csrf_token_tag['content']
         print(f"Berhasil mendapatkan CSRF Token: {csrf_token[:5]}...") # Tampilkan sebagian kecil

    # --- 2. Perbarui dan Dapatkan URL CAPTCHA Baru ---
    print("Meminta pembaruan CAPTCHA...")
    headers_captcha = {
        'X-CSRF-TOKEN': csrf_token,
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': main_page_url,
        'Origin': base_url
    }
    response_renew = session.post(renew_captcha_url, headers=headers_captcha)
    response_renew.raise_for_status()

    try:
        renew_data = response_renew.json()
        if 'captcha' not in renew_data:
             print("Respons pembaruan CAPTCHA tidak mengandung URL gambar.")
             print(f"Respons: {renew_data}")
             sys.exit(1)
        captcha_img_url = renew_data['captcha']
        # Pastikan URL lengkap jika hanya path yang dikembalikan
        if not captcha_img_url.startswith('http'):
            captcha_img_url = base_url + captcha_img_url if captcha_img_url.startswith('/') else base_url + '/' + captcha_img_url
        print(f"URL CAPTCHA baru: {captcha_img_url}")

    except requests.exceptions.JSONDecodeError:
        print("Gagal mem-parsing respons JSON dari pembaruan CAPTCHA.")
        print(f"Respons Teks: {response_renew.text}")
        sys.exit(1)


    # --- 3. Unduh Gambar CAPTCHA ---
    print(f"Mengunduh gambar CAPTCHA ke '{captcha_image_file}'...")
    response_img = session.get(captcha_img_url, stream=True)
    response_img.raise_for_status()

    with open(captcha_image_file, 'wb') as f:
        for chunk in response_img.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Gambar CAPTCHA disimpan. Silakan buka '{captcha_image_file}' dan lihat kodenya.")

    # --- 4. Minta Input CAPTCHA dari Pengguna ---
    try:
        captcha_code = input("Masukkan kode CAPTCHA yang Anda lihat: ")
        if not captcha_code:
            raise ValueError("Kode CAPTCHA tidak boleh kosong.")
    except ValueError as e:
        print(f"Input tidak valid: {e}")
        sys.exit(1)
    except EOFError:
        print("\nInput dibatalkan.")
        sys.exit(1)
    finally:
        # Hapus file gambar setelah input (opsional)
        if os.path.exists(captcha_image_file):
            try:
                os.remove(captcha_image_file)
                print(f"File '{captcha_image_file}' dihapus.")
            except OSError as e:
                print(f"Gagal menghapus file '{captcha_image_file}': {e}")


    # --- 5. Siapkan Data dan Header untuk Submit ---
    payload = {
        "nip": nomor_peserta,
        "layanan": layanan_kode,
        "tahun": tahun_periode,
        "captcha": captcha_code
    }

    headers_submit = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-CSRF-TOKEN': csrf_token,
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': main_page_url,
        'Origin': base_url
    }

    # --- 6. Kirim Request Submit ---
    print("\nMengirim request cek status layanan...")
    response_submit = session.post(submit_url, headers=headers_submit, data=payload)
    response_submit.raise_for_status()

    # --- 7. Tampilkan Hasil ---
    print("\n--- Respons Server ---")
    try:
        result_json = response_submit.json()
        print(result_json) # Cetak respons JSON apa adanya

        # Analisis tambahan (opsional)
        if result_json.get("success") or result_json.get("email"):
             print("\nPEMBERITAHUAN: Request berhasil diproses. Periksa Email/WhatsApp Anda.")
        elif result_json.get("error"):
             print(f"\nPERINGATAN: Terjadi error -> {result_json['error']}")
        else:
             print("\nCATATAN: Respons tidak dikenal (bukan format sukses/error yang diharapkan).")

    except requests.exceptions.JSONDecodeError:
        print("Gagal mem-parsing respons JSON dari server submit.")
        print("Respons Teks Mentah:")
        print(response_submit.text)

except requests.exceptions.RequestException as e:
    print(f"\nTerjadi error koneksi atau request HTTP: {e}")
except Exception as e:
    print(f"\nTerjadi error tak terduga: {e}")
finally:
    session.close()
    print("\nSelesai.")