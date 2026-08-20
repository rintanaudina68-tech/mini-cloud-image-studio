# ☁️ Mini Cloud Image Studio

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Streamlit-1.30%2B-red.svg)](https://streamlit.io/)
[![Cloud SDK](https://img.shields.io/badge/Boto3-AWS%20SDK-orange.svg)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
[![Storage](https://img.shields.io/badge/Object%20Storage-MinIO%20%2F%20S3-blue.svg)](https://min.io/)
[![Database](https://img.shields.io/badge/Database-DynamoDB%20Local-blueviolet.svg)](https://aws.amazon.com/dynamodb/)

**Mini Cloud Image Studio** adalah aplikasi *Cloud-Native Image Processing & Metadata Management System* berbasis **Python**, **Streamlit**, dan **Boto3 SDK** yang terintegrasi penuh dengan infrastruktur cloud lokal (**MinIO** dan **DynamoDB Local** / **LocalStack**). 

Proyek ini disusun untuk memenuhi tugas **Remidi Cloud Computing**, menyajikan implementasi arsitektur cloud terstruktur, fitur manipulasi gambar komprehensif, otomatisasi inisialisasi resource, serta penanganan error yang andal.

---

## 📋 Daftar Isi
- [1. Ringkasan & Tujuan Aplikasi](#1-ringkasan--tujuan-aplikasi)
- [2. Konsep Arsitektur Cloud](#2-konsep-arsitektur-cloud)
- [3. Fitur Utam Aplikasi](#3-fitur-utama-aplikasi)
- [4. Teknologi yang Digunakan](#4-teknologi-yang-digunakan)
- [5. Struktur Folder Proyek](#5-struktur-folder-proyek)
- [6. Skema Storage & Database](#6-skema-storage--database)
- [7. Prasyarat System](#7-prasyarat-system)
- [8. Panduan Instalasi & Penggunaan](#8-panduan-instalasi--penggunaan)
- [9. Penanganan Error (Troubleshooting)](#9-penanganan-error-troubleshooting)
- [10. Daftar Prompt AI yang Digunakan](#10-daftar-prompt-ai-yang-digunakan)
- [11. Identitas Penulis](#11-identitas-penulis)

---

## 1. Ringkasan & Tujuan Aplikasi

### Deskripsi
Mini Cloud Image Studio memungkinkan pengguna untuk mengunggah gambar, memuat metadata ke dalam basis data NoSQL (DynamoDB), melakukan berbagai manipulasi/filter gambar secara interaktif (Resize, Grayscale, Sepia, Invert, Watermark NIM, Format Conversion), menyimpan hasil pemrosesan kembali ke Object Storage (S3), serta mengelola histori gambar melalui antarmuka web modern.

### Tujuan Aplikasi
1. **Penerapan Layanan Cloud Storage & NoSQL**: Mengimplementasikan penyimpanan objek tanpa batas berbasis Amazon S3 dan basis data dokumen NoSQL terstruktur menggunakan Amazon DynamoDB.
2. **Emulasi Environment Cloud Lokal**: Menggunakan container MinIO / LocalStack untuk menjalankan pengujian cloud secara lokal tanpa memerlukan akun AWS sungguhan atau kunci kredensial berbayar.
3. **Automated Resource Provisioning**: Otomatisasi pembuatan S3 Bucket (`mini-cloud-image-studio`) dan DynamoDB Table (`MiniCloudImages`) saat aplikasi pertama kali dijalankan melalui Python & Boto3 SDK.
4. **Antarmuka Interaktif & Responsif**: Menyediakan UI berbasis Streamlit yang intuitif untuk pengguna akhir.

---

## 2. Konsep Arsitektur Cloud

Alur komunikasi data pada aplikasi dirancang mengikuti pola arsitektur cloud terdistribusi:

```text
Browser User (Streamlit Client UI)
              │
              ▼
   Python Application Core
     ├── Image Engine (Pillow / PIL)
     └── Boto3 AWS SDK Client
              │
      ┌───────┴───────┐
      ▼               ▼
  S3 Bucket        DynamoDB
(Binary Objects)  (Metadata Items)
      │               │
      └───────┬───────┘
              ▼
    MinIO / LocalStack Container
         (Local Cloud)
```

### Hubungan Antar Komponen:
1. **Streamlit (Presentation Layer)**: Berfungsi sebagai antarmuka pengguna berbasis browser yang menangani input berkas, pengoperasian slider/filter, dan penayangan galeri.
2. **Pillow / PIL (Business Logic - Image Processing)**: Melakukan transformasi biner gambar (filtering, resizing, watermarking) di tingkat memory server Python.
3. **Boto3 (Cloud SDK Integrator)**: Library resmi AWS SDK untuk Python yang menjembatani komunikasi HTTP/REST API antara aplikasi Python dengan layanan S3 dan DynamoDB.
4. **Amazon S3 / MinIO (Object Storage Layer)**: Menyimpan berkas gambar mentah (original) dan hasil manipulasi (processed) dalam struktur bucket terisolasi.
5. **Amazon DynamoDB (NoSQL Metadata Layer)**: Menyimpan metadata terstruktur setiap berkas (dimensi, format, ukuran, timestamp, riwayat operasi) dalam bentuk item NoSQL terindeks.

---

## 3. Fitur Utama Aplikasi

| Fitur | Deskripsi | Status |
| :--- | :--- | :---: |
| **Dashboard Cloud Metrics** | Menampilkan statistik jumlah gambar, ukuran penyimpanan S3, status koneksi cloud, dan ringkasan aktivitas. | ✅ Aktif |
| **Auto Resource Setup** | Pengecekan otomatis ketersediaan bucket S3 & tabel DynamoDB pada startup aplikasi. | ✅ Aktif |
| **Image Upload** | Mengunggah gambar (PNG, JPG, JPEG, WEBP) dan menyimpan metadatan eksplisit. | ✅ Aktif |
| **Resize Filter** | Mengubah dimensi gambar (width x height) dengan opsi pertahankan aspect ratio. | ✅ Aktif |
| **Grayscale Filter** | Transformasi warna gambar menjadi hitam-putih. | ✅ Aktif |
| **Sepia Filter** | Transformasi warna nuansa vintage/warm sepia. | ✅ Aktif |
| **Invert Filter** | Membalikkan spektrum warna gambar (color inversion). | ✅ Aktif |
| **Custom Watermark** | Penambahan teks watermark beserta **NIM Mahasiswa** di sudut gambar secara dinamis. | ✅ Aktif |
| **Format Converter** | Konversi format gambar secara fleksibel antar format PNG, JPEG, dan WEBP. | ✅ Aktif |
| **Cloud Gallery** | Menampilkan daftar riwayat gambar, opsi View high-res, Download, dan Delete object & metadata. | ✅ Aktif |

---

## 4. Teknologi yang Digunakan

* **Bahasa Pemrograman**: Python 3.10+
* **Framework Frontend / UI**: Streamlit 1.30+
* **Cloud SDK**: Boto3 (Amazon Web Services SDK for Python)
* **Image Processing Engine**: Pillow (PIL) 10.0+
* **Local Cloud Environment**: MinIO / Amazon DynamoDB Local / LocalStack
* **Containerization**: Docker & Docker Compose
* **Laporan Dokumentasi**: FPDF2 & Markdown

---

## 5. Struktur Folder Proyek

```text
mini-cloud-image-studio/
├── app.py                      # Core Streamlit Web Application
├── requirements.txt            # Package Dependencies
├── README.md                   # Technical Documentation & User Guide
├── .env.example                # Environment Variable Template
├── .env                        # Local Environment Configuration (Ignored by Git)
├── .gitignore                  # Git Ignore Specifications
├── docker-compose.yml          # Docker Infrastructure for MinIO & DynamoDB Local
│
├── config/
│   └── settings.py             # Global Application Configuration & Env Loader
│
├── services/
│   ├── s3_service.py           # S3 Boto3 Service Wrapper (Upload, Download, Delete, List)
│   ├── dynamodb_service.py     # DynamoDB Boto3 Service Wrapper (Metadata CRUD)
│   └── image_service.py        # Image Processing Logic (Pillow)
│
├── utils/
│   └── helpers.py              # UI Helpers, Custom CSS Styling, Formatting Utilities
│
├── screenshots/
│   └── .gitkeep                # Application Test Screenshots
│
└── report/
    ├── laporan_remidi.md       # Source Laporan Remidi (Markdown Format)
    ├── generate_pdf.py         # PDF Compilation Generator Script
    └── Laporan_Remidi_Cloud_Computing.pdf # Generated Official PDF Report
```

---

## 6. Skema Storage & Database

### A. Skema Amazon S3 (Bucket: `mini-cloud-image-studio`)
Penyimpanan objek dikelompokkan ke dalam dua prefix folder utama:
- `originals/{image_id}.{ext}`: Berkas gambar asli yang diunggah pengguna.
- `processed/{image_id}.{ext}`: Berkas gambar hasil manipulasi / filter.

### B. Skema Amazon DynamoDB (Table: `MiniCloudImages`)
- **Partition Key**: `image_id` (String)

| Attribute Name | Data Type | Deskripsi Contoh |
| :--- | :---: | :--- |
| `image_id` | String (HASH) | `IMG-20260820173000-A1B2C3` |
| `file_name` | String | `sample_photo.jpg` |
| `object_key` | String | `originals/IMG-20260820173000-A1B2C3.jpg` |
| `original_format` | String | `JPEG` |
| `processed_format` | String | `PNG` |
| `operation` | String | `Watermark` / `Grayscale` / `Resize` |
| `width` | Number | `1920` |
| `height` | Number | `1080` |
| `file_size` | Number | `245120` (Bytes) |
| `uploaded_at` | String | `2026-08-20T17:30:00.123456` (ISO Format) |
| `status` | String | `Active` / `Processed` |

---

## 7. Prasyarat System

Sebelum menjalankan aplikasi, pastikan perangkat komputer Anda telah terinstall:
1. **Python**: Versi 3.10 atau lebih baru.
2. **Docker & Docker Desktop**: Untuk menjalankan MinIO dan DynamoDB Local.
3. **Git**: Untuk melakukan clone/push repositori.

---

## 8. Panduan Instalasi & Penggunaan

### Langkah 1: Clone Repositori
```bash
git clone https://github.com/USERNAME/mini-cloud-image-studio.git
cd mini-cloud-image-studio
```

### Langkah 2: Setup Environment File
Salin berkas `.env.example` menjadi `.env`:
```bash
cp .env.example .env
```

### Langkah 3: Jalankan Cloud Environment Lokal (MinIO & DynamoDB)
Jalankan container menggunakan Docker Compose:
```bash
docker compose up -d
```
*Verifikasi status container dengan `docker compose ps`.*

### Langkah 4: Install Dependensi Python
Sangat disarankan menggunakan Virtual Environment:
```bash
python -m venv venv
# Aktifkan Virtual Environment:
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate

# Install dependensi:
pip install -r requirements.txt
```

### Langkah 5: Jalankan Aplikasi Streamlit
```bash
streamlit run app.py
```
Aplikasi secara otomatis terbuka di browser pada alamat: `http://localhost:8501`.

---

## 9. Penanganan Error (Troubleshooting)

| Masalah | Kemungkinan Penyebab | Solusi |
| :--- | :--- | :--- |
| **S3 / DynamoDB Status OFFLINE** | Docker Container belum berjalan. | Jalankan `docker compose up -d` di terminal lalu klik **Trigger Connection Re-check** pada aplikasi. |
| **Boto3 Connection Refused** | Endpoint URL di `.env` tidak sesuai. | Pastikan `S3_ENDPOINT_URL=http://localhost:9000` dan `DYNAMODB_ENDPOINT_URL=http://localhost:8000`. |
| **Unsupported Image Format** | Format file yang diupload bukan PNG/JPG/WEBP. | Unggah berkas gambar dengan format standar yang didukung. |
| **ModuleNotFoundError** | Library Python belum terinstall. | Jalankan kembali `pip install -r requirements.txt`. |

---

## 10. Daftar Prompt AI yang Digunakan

Proyek ini dibangun secara independen dengan bantuan AI Assistant sebagai pair-programmer. Berikut adalah daftar prompt eksplisit yang digunakan:

1. **Prompt Architecture & Setup**:
   > *"Buatlah arsitektur modular aplikasi Python Streamlit bernama Mini Cloud Image Studio yang terhubung ke MinIO (S3) dan DynamoDB Local menggunakan Boto3. Sertakan file settings.py, s3_service.py, dynamodb_service.py, image_service.py, dan helpers.py."*

2. **Prompt Boto3 Service Auto-Provisioning**:
   > *"Tulis kode Python boto3 untuk S3 dan DynamoDB service yang secara otomatis mengecek ketersediaan bucket 'mini-cloud-image-studio' dan tabel DynamoDB 'MiniCloudImages' (Partition Key: image_id). Jika belum ada, buat resource tersebut secara otomatis tanpa melempar raw exception."*

3. **Prompt Image Manipulation Logic**:
   > *"Implementasikan class ImageService menggunakan Pillow untuk melakukan manipulasi gambar: Resize (keep aspect ratio option), Grayscale, Sepia filter, Invert color, Watermark teks dengan input NIM Mahasiswa, dan Format Converter (PNG, JPEG, WEBP)."*

4. **Prompt UI & Custom Styling**:
   > *"Buat antarmuka Streamlit di app.py dengan tema dark modern, metric cards, status badge online/offline untuk cloud endpoints, serta tab navigasi: Dashboard, Upload Image, Image Studio, Gallery & History, dan Cloud Status."*

5. **Prompt Laporan Remidi Generation**:
   > *"Buat script Python menggunakan library FPDF2 yang membaca dokumen Markdown laporan_remidi.md dan menghasilkan berkas Laporan_Remidi_Cloud_Computing.pdf yang rapi dan profesional sesuai struktur BAB 1 sampai BAB 5."*

---

## 11. Identitas Penulis

* **Nama Mahasiswa**: Rintan Audina
* **NIM**: 32602400035
* **Kelas**: TIF 24
* **Mata Kuliah**: Cloud Computing (Remidi)
* **Dosen Pengampu**: Dosen Cloud Computing
* **Tahun Akademik**: 2026
