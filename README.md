# Proyek deteksi cacat fisik dan kontaminan pada biji kopi.

Sistem ini adalah aplikasi untuk mendeteksi berbagai jenis kategori cacat fisik kopi dan kontaminan yang tercampur dalam kopi secara real-time menggunakan model YOLOv8 yang sudah di fine tuning.

## Fitur

*   **Deteksi Gambar:** Menganalisis gambar statis untuk mengidentifikasi objek.
*   **Deteksi Video:** Menganalisis file video untuk mengidentifikasi objek.
*   **Streaming Real-time:** Melakukan deteksi objek secara langsung dari feed kamera.

## Arsitektur

Proyek ini dibagi menjadi dua komponen utama: **Frontend** dan **Backend**.

### Alasan Pemisahan

Pemisahan ini dilakukan untuk mengoptimalkan kinerja dan fleksibilitas.

*   **Backend (Python/FastAPI):** Bertanggung jawab untuk menjalankan model deteksi objek YOLOv8. Proses ini membutuhkan sumber daya komputasi yang besar dan idealnya dijalankan di server yang dilengkapi dengan **GPU** untuk akselerasi.
*   **Frontend (Svelte/Vite):** Berfungsi sebagai antarmuka pengguna (UI). Komponen ini menangani pengambilan gambar dari kamera pengguna, mengirimkannya ke backend untuk diproses, dan menampilkan hasil deteksi. Ini memungkinkan pengguna untuk berinteraksi dengan sistem dari perangkat apa pun tanpa perlu instalasi perangkat keras khusus.

## Dataset Pelatihan

Dataset yang digunakan untuk melatih model YOLOv8 terletak di dalam direktori `dataset training/`. Dataset ini berisi berbagai gambar biji kopi dan objek terkait lainnya yang telah diklasifikasikan ke dalam folder yang sesuai untuk proses pelatihan.

## Skrip Pelatihan

Proses pelatihan model dilakukan menggunakan skrip Jupyter Notebook `Train_YOLO_Models_(SKRIPSI).ipynb`. Notebook ini berisi semua langkah yang diperlukan untuk melatih model YOLOv8 dari awal menggunakan dataset yang telah disediakan, termasuk pemrosesan data, augmentasi, pelatihan, dan evaluasi model.

## Cara Menjalankan Sistem

### 1. Backend

Pastikan Anda berada di direktori `backend`.

**a. Instalasi Dependensi:**

Buat dan aktifkan virtual environment, lalu instal semua paket yang dibutuhkan.

```bash
# Pindah ke direktori backend
cd backend

# Buat virtual environment (opsional tapi direkomendasikan)
python -m venv venv
source venv/bin/activate  # Untuk Windows: venv\Scripts\activate

# Instal dependensi
pip install -r requirements.txt
```

**b. Menjalankan Server:**

Gunakan `uvicorn` untuk menjalankan server FastAPI.

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Server backend sekarang akan berjalan di `http://localhost:8000`.

**c. Menjalankan Celery Worker:**

Gunakan `celery` untuk menjalankan worker, dan sebelum itu jalankan dulu service redis.

```bash
celery -A celery_app worker -l info
```

### 2. Frontend

Pastikan Anda berada di direktori `frontend`.

**a. Instalasi Dependensi:**

Instal semua paket Node.js yang dibutuhkan.

```bash
# Pindah ke direktori frontend
cd frontend

# Instal dependensi
npm install
```

**b. Menjalankan Aplikasi:**

Jalankan server pengembangan Vite.

```bash
npm run dev
```

Aplikasi frontend sekarang akan dapat diakses melalui browser di alamat yang ditampilkan di terminal (biasanya `http://localhost:5173`).