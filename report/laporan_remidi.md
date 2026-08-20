# LAPORAN REMIDI CLOUD COMPUTING

## MINI CLOUD IMAGE STUDIO
**Sistem Pemrosesan Gambar dan Manajemen Metadata Berbasis Cloud Native**

---

### IDENTITAS MAHASISWA

- **Nama**: Rintan Audina
- **NIM**: 32602400035
- **Kelas**: TIF 24
- **Mata Kuliah**: Cloud Computing (Remidi)
- **Dosen Pengampu**: Dosen Cloud Computing
- **Tahun Akademik**: 2026

---

## BAB 1 — PENDAHULUAN

### 1.1 Latar Belakang
Perkembangan teknologi *cloud computing* telah mengubah paradigma arsitektur pengembangan perangkat lunak modern. Pengelolaan aset media seperti gambar pada skala besar memerlukan infrastruktur penyimpanan objek (*Object Storage*) yang dapat ditingkatkan nilainya secara fleksibel (*scalable*), efisien, dan andal. Selain itu, indeks metadata dari aset media tersebut perlu dikelola menggunakan basis data NoSQL berkecepatan tinggi agar proses pencarian, filtering, dan manipulasi data dapat berjalan secara instan.

Amazon Web Services (AWS) menyediakan dua layanan utama untuk kebutuhan ini, yaitu **Amazon S3** (*Simple Storage Service*) untuk penyimpanan biner berkas dan **Amazon DynamoDB** untuk basis data dokumen NoSQL terstruktur. Dalam pengembangan aplikasi tingkat lokal, penggunaan emulasi cloud seperti **MinIO** dan **DynamoDB Local** atau **LocalStack** memungkinkan para pengembang (*developers*) untuk melakukan simulasi arsitektur cloud AWS secara penuh tanpa biaya operasional.

Oleh karena itu, proyek aplikasi **"Mini Cloud Image Studio"** ini dibangun menggunakan pemrograman Python, Streamlit, dan Boto3 SDK. Aplikasi ini dirancang untuk memfasilitasi pengunggahan gambar, ekstraksi dan penyimpanan metadata ke DynamoDB, pemrosesan/filter gambar secara interaktif, penyimpanan kembali hasil manipulasi ke S3, serta penayangan galeri gambar secara terintegrasi.

### 1.2 Tujuan
Tujuan dari pelaksanaan tugas Remidi Cloud Computing ini adalah:
1. Merancang dan membangun aplikasi cloud-native sederhana berbasis Python dan Streamlit.
2. Mengimplementasikan integrasi Boto3 SDK dengan layanan Amazon S3 (MinIO) dan Amazon DynamoDB Local.
3. Membangun fitur manipulasi gambar komprehensif (Resize, Grayscale, Sepia, Invert, Watermark NIM, dan Format Converter) berbasis library Pillow.
4. Mengimplementasikan otomatisasi pembuat (*auto-provisioning*) S3 Bucket dan DynamoDB Table saat aplikasi diinisialisasi.
5. Menerapkan praktik penanganan error (*error handling*) yang ramah pengguna (*user-friendly*) tanpa menampilkan traceback mentah.

### 1.3 Permasalahan
Permasalahan yang diselesaikan dalam proyek ini meliputi:
1. Bagaimana mengintegrasikan Boto3 SDK agar terhubung ke environment cloud lokal (MinIO/LocalStack) tanpa memerlukan kredensial AWS asli?
2. Bagaimana mengarsitekturkan pemisahan antara berkas fisik gambar di S3 dengan metadata biner terstruktur di DynamoDB?
3. Bagaimana mengimplementasikan manipulasi gambar interaktif yang responsif pada Streamlit dan menyimpannya secara konsisten kembali ke cloud storage?

---

## BAB 2 — PERANCANGAN

### 2.1 Arsitektur Sistem
Aplikasi menggunakan arsitektur tiga lapis (*three-tier architecture*) yang disederhanakan:

```text
Browser Client (Streamlit UI)
             │
             ▼
   Python Backend Core
     ├── Image Service (Pillow)
     └── Boto3 SDK Services
             │
     ┌───────┴───────┐
     ▼               ▼
 S3 Bucket        DynamoDB
(MinIO Server) (DynamoDB Local)
```

1. **Presentation Layer**: Streamlit Web User Interface running pada port `8501`.
2. **Application & Business Logic Layer**: Python modules (`services/s3_service.py`, `services/dynamodb_service.py`, `services/image_service.py`).
3. **Infrastructure / Data Layer**: MinIO S3 API (Port `9000`) dan DynamoDB Local API (Port `8000`).

### 2.2 Teknologi Utama
- **Python 3.10+**: Bahasa pemroses utama.
- **Boto3 SDK**: Library klien resmi AWS untuk interaksi S3 dan DynamoDB.
- **Streamlit**: Framework UI web interaktif.
- **Pillow (PIL)**: Engine manipulasi dan transformasi gambar.
- **MinIO & DynamoDB Local**: Emunator cloud lokal berbasis Docker.

### 2.3 Skema Database DynamoDB
- **Nama Tabel**: `MiniCloudImages`
- **Partition Key**: `image_id` (String / HASH)

Attribute schema:
- `image_id` (String): ID unik gambar (e.g., `IMG-20260820173000-A1B2C3`).
- `file_name` (String): Nama asli berkas gambar.
- `object_key` (String): Key jalur penyimpanan di S3 bucket.
- `original_format` (String): Format asli gambar (PNG/JPEG/WEBP).
- `processed_format` (String): Format hasil olahan.
- `operation` (String): Nama operasi manipulasi yang dilakukan.
- `width` (Number): Lebar gambar dalam piksel.
- `height` (Number): Tinggi gambar dalam piksel.
- `file_size` (Number): Ukuran berkas dalam bytes.
- `uploaded_at` (String): Waktu unggah format ISO.
- `status` (String): Status gambar (`Active` / `Processed`).

### 2.4 Struktur Object Storage S3
- **Nama Bucket**: `mini-cloud-image-studio`
- **Hierarki Object**:
  - `originals/`: Jalur penyimpan gambar asli.
  - `processed/`: Jalur penyimpan gambar hasil olahan studio.

---

## BAB 3 — IMPLEMENTASI

### 3.1 Konfigurasi Cloud Lokal (.env & settings.py)
Pengaturan endpoint dialokasikan melalui variabel lingkungan:

```env
AWS_ACCESS_KEY_ID=mock_access_key
AWS_SECRET_ACCESS_KEY=mock_secret_key
AWS_REGION=us-east-1
S3_ENDPOINT_URL=http://localhost:9000
DYNAMODB_ENDPOINT_URL=http://localhost:8000
S3_BUCKET_NAME=mini-cloud-image-studio
DYNAMODB_TABLE_NAME=MiniCloudImages
```

### 3.2 Implementasi S3 Service (`s3_service.py`)
Mengimplementasikan fungsi utama Boto3 S3:
- `check_connection()`: Menguji responsibilitas endpoint S3.
- `ensure_bucket_exists()`: Membuat bucket secara otomatis jika belum ada.
- `upload_image()`: Mengirim byte data ke S3.
- `download_image()`: Mengambil byte data dari S3.
- `delete_image()`: Menghapus object S3.
- `list_images()`: Mengambil daftar objek dalam bucket.

### 3.3 Implementasi DynamoDB Service (`dynamodb_service.py`)
Mengimplementasikan fungsi CRUD metadata:
- `check_connection()`: Menguji responsibilitas endpoint DynamoDB.
- `ensure_table_exists()`: Membuat tabel `MiniCloudImages` secara otomatis.
- `save_image_metadata()`: Menyimpan item metadata gambar.
- `get_image_metadata()`: Mengambil item tunggal berdasarkan `image_id`.
- `list_image_metadata()`: Melakukan scan seluruh item metadata.
- `delete_image_metadata()`: Menghapus metadata item berdasarkan `image_id`.

### 3.4 Fitur Pemrosesan Gambar (`image_service.py`)
1. **Resize**: Mengubah dimensi gambar dengan opsi mempertahankan aspect ratio.
2. **Grayscale**: Transformasi mode ke warna hitam-putih.
3. **Sepia**: Penambahan matriks warna warm vintage.
4. **Invert**: Membalikkan saluran warna RGB.
5. **Watermark**: Menambahkan teks watermark dan **NIM Mahasiswa** pada posisi kanan bawah gambar.
6. **Format Converter**: Mengubah enkripsi biner gambar ke format target (PNG, JPEG, WEBP).

### 3.5 Antarmuka Streamlit (`app.py`)
UI disusun menjadi 5 bagian utama:
1. **Dashboard**: Menampilkan metrik utama, status server, dan ringkasan aktivitas.
2. **Upload Image**: Form unggah berkas, pratinjau, dan tombol upload cloud.
3. **Image Studio**: Panel kontrol manipulasi gambar interaktif.
4. **Gallery & History**: Menampilkan kartu galeri berkas lengkap dengan tombol View, Save, dan Delete.
5. **Cloud Status**: Halaman diagnostik jaringan cloud lokal dan panduan Docker.

---

## BAB 4 — HASIL PENGUJIAN

Pengujian dilakukan untuk memastikan seluruh fungsi aplikasi berjalan sesuai persyaratan tugas:

### Tabel Hasil Pengujian Sistem

| No | Pengujian | Skenario Pengujian | Hasil Pengujian | Status |
| :-: | :--- | :--- | :--- | :-: |
| 1 | Menjalankan Cloud Lokal | Menjalankan container MinIO dan DynamoDB Local via Docker Compose | Service aktif pada port 9000 & 8000 | **BERHASIL** |
| 2 | Aplikasi Streamlit | Menjalankan perintah `streamlit run app.py` | Aplikasi terbuka di browser localhost:8501 | **BERHASIL** |
| 3 | Auto Bucket S3 | Startup aplikasi mengecek bucket `mini-cloud-image-studio` | Bucket terbuat otomatis di MinIO | **BERHASIL** |
| 4 | Auto Table DynamoDB | Startup aplikasi mengecek tabel `MiniCloudImages` | Tabel terbuat otomatis dengan partition key `image_id` | **BERHASIL** |
| 5 | Upload Gambar | Mengunggah gambar PNG/JPG via form Upload | Gambar tersimpan di S3 & preview tampil | **BERHASIL** |
| 6 | Metadata DynamoDB | Pengecekan data setelah upload gambar | Item metadata berhasil masuk ke DynamoDB | **BERHASIL** |
| 7 | Fitur Resize | Mengubah ukuran gambar dengan slider dimensi | Dimensi gambar berubah sesuai masukan | **BERHASIL** |
| 8 | Fitur Grayscale | Mengaplikasikan filter Grayscale | Gambar berubah menjadi hitam-putih | **BERHASIL** |
| 9 | Fitur Watermark | Menambahkan watermark teks & NIM Mahasiswa | Teks watermark terlukis di pojok kanan bawah | **BERHASIL** |
| 10 | Format Converter | Mengubah format gambar dari PNG ke WEBP | Berkas berhasil dikonversi dan disimpan ke S3 | **BERHASIL** |
| 11 | Download Hasil | Mengklik tombol Save/Download pada galeri | Berkas tersimpan ke direktori komputer lokal | **BERHASIL** |
| 12 | Delete Gambar | Mengklik tombol Delete pada galeri | Object di S3 dan metadata di DynamoDB terhapus | **BERHASIL** |

---

## BAB 5 — KESIMPULAN

Berdasarkan hasil perancangan, implementasi, dan pengujian yang telah dilakukan, dapat disimpulkan bahwa:
1. Aplikasi **Mini Cloud Image Studio** telah berhasil dikembangkan menggunakan Python, Streamlit, Boto3 SDK, MinIO (S3), dan DynamoDB Local.
2. Seluruh kebutuhan fungsionalitas mencakup upload gambar, manipulasi gambar (Resize, Grayscale, Sepia, Invert, Watermark NIM, Format Converter), penyimpanan metadata NoSQL, serta fitur galeri (View, Download, Delete) telah **100% terpenuhi**.
3. Aplikasi mampu melakukan *automated resource initialization* untuk bucket S3 dan tabel DynamoDB tanpa memerlukan konfigurasi manual dari pengguna.
4. Penggunaan emulasi cloud lokal memungkinkan aplikasi diuji dan dijalankan secara mandiri di komputer lokal tanpa ketergantungan pada akun AWS berbayar.

---

## LAMPIRAN — DAFTAR SCREENSHOT APLIKASI

Berikut adalah daftar dokumentasi tangkapan layar (screenshot) pengujian aplikasi yang tersimpan dalam direktori `screenshots/`:

1. `screenshots/01_minio_running.png` — Container MinIO / LocalStack Berjalan di Docker Desktop.
2. `screenshots/02_terminal_running.png` — Eksekusi Aplikasi Streamlit (`app.py`) pada Terminal.
3. `screenshots/03_dashboard.png` — Tampilan Dashboard Utama & Cloud Metrics.
4. `screenshots/04_upload_page.png` — Halaman Form Upload Gambar.
5. `screenshots/05_preview_original.png` — Preview Gambar Asli dan Analisis Informasi File.
6. `screenshots/06_image_processing.png` — Panel Kontrol Pemrosesan Gambar (Image Studio).
7. `screenshots/07_grayscale_resize.png` — Hasil Pemrosesan Filter Grayscale dan Resize.
8. `screenshots/08_watermark_result.png` — Hasil Penambahan Custom Watermark dan NIM Mahasiswa.
9. `screenshots/09_format_converter.png` — Fitur Format Converter (PNG / JPEG / WEBP).
10. `screenshots/10_gallery_history.png` — Halaman Galeri Gambar dan Riwayat Aktivitas Cloud.
11. `screenshots/11_s3_bucket_objects.png` — Tampilan Berkas Objek Gambar pada S3 Bucket (MinIO Console).
12. `screenshots/12_dynamodb_metadata.png` — Tampilan Item Metadata Gambar pada Tabel DynamoDB Local.
13. `screenshots/13_download_result.png` — Proses Download Berkas Hasil Pemrosesan ke Komputer Lokal.
14. `screenshots/14_delete_image.png` — Proses Penghapusan Objek S3 dan Item Metadata DynamoDB.
15. `screenshots/15_github_repository.png` — Struktur Repositori Publik GitHub Proyek.

---

## PROMPT AI YANG DIGUNAKAN

Sesuai dengan ketentuan tugas, berikut adalah daftar *prompt AI* yang secara nyata digunakan selama proses analisis, perancangan, dan pengembangan aplikasi:

```text
1. PROMPT ARCHITECTURE:
"Buatlah arsitektur modular aplikasi Python Streamlit bernama Mini Cloud Image Studio yang terhubung ke MinIO (S3) dan DynamoDB Local menggunakan Boto3. Sertakan file settings.py, s3_service.py, dynamodb_service.py, image_service.py, dan helpers.py."

2. PROMPT BOTO3 RESOURCE AUTO-PROVISIONING:
"Tulis kode Python boto3 untuk S3 dan DynamoDB service yang secara otomatis mengecek ketersediaan bucket 'mini-cloud-image-studio' dan tabel DynamoDB 'MiniCloudImages' (Partition Key: image_id). Jika belum ada, buat resource tersebut secara otomatis tanpa melempar raw exception."

3. PROMPT IMAGE MANIPULATION LOGIC:
"Implementasikan class ImageService menggunakan Pillow untuk melakukan manipulasi gambar: Resize (keep aspect ratio option), Grayscale, Sepia filter, Invert color, Watermark teks dengan input NIM Mahasiswa, dan Format Converter (PNG, JPEG, WEBP)."

4. PROMPT UI & CUSTOM STYLING:
"Buat antarmuka Streamlit di app.py dengan tema dark modern, metric cards, status badge online/offline untuk cloud endpoints, serta tab navigasi: Dashboard, Upload Image, Image Studio, Gallery & History, dan Cloud Status."

5. PROMPT REPORT GENERATION:
"Buat script Python menggunakan library FPDF2 yang membaca dokumen Markdown laporan_remidi.md dan menghasilkan berkas Laporan_Remidi_Cloud_Computing.pdf yang rapi dan profesional sesuai struktur BAB 1 sampai BAB 5."
```
