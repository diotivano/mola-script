**Monitoring SIASN BKN - Penetapan NIP/NI PPPK Script** <br />
Skrip Python ini dibuat untuk mempermudah proses pemeriksaan status layanan Penetapan NIP/NI PPPK melalui situs [MOLA BKN](https://monitoring-siasn.bkn.go.id/). Skrip ini melakukan beberapa langkah otomatisasi, termasuk:

- Mengambil CSRF token dari halaman utama
- Meminta dan mengunduh gambar CAPTCHA terbaru
- Meminta input pengguna untuk kode CAPTCHA
- Mengirim permintaan ke endpoint pengecekan status layanan
- Menampilkan hasil respons dari server dalam format JSON

🛠️ Teknologi & Library
- requests
- BeautifulSoup (bs4)
- Python Standard Library (os, sys)

⚠️ Catatan
- CAPTCHA tetap harus dimasukkan secara manual, file gambar CAPTCHA akan terunduh dalam folder yang sama.
- File gambar CAPTCHA akan dihapus secara otomatis setelah pengguna memasukkan kodenya.
- Pastikan koneksi internet stabil saat menjalankan skrip.

✅ Cara Penggunaan
- install Python 3
- install library requests dan BeautifulSoup (bs4)
- jalankan python mola.py
- Ikuti instruksi input di terminal untuk menyelesaikan proses pengecekan status.

