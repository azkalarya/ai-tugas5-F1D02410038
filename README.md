# Sistem Pakar Kelayakan Penerima Beasiswa Mahasiswa

Tugas Kecerdasan Buatan, Materi 5: Membuat Sistem Pakar Sederhana.

## 1. Identitas

- Nama: Azkal Arya Habibie
- NIM: F1D02410038

## 2. Topik dan cara menjalankan

**Topik:** Kelayakan awal calon penerima beasiswa prestasi/bantuan mahasiswa (sistem pendukung keputusan). Topik ini tidak berkaitan dengan kesehatan manusia.

**Bahasa dan perintah**

- Bahasa: Python 3.8 atau lebih baru. Tidak ada pustaka tambahan.
- Metode: **Forward Chaining (FC)**.

```bash
python sistem_pakar.py            # mode interaktif, jawab y/t
python sistem_pakar.py --kasus 1  # putar ulang kasus uji nomor 1 (untuk screenshot)
python sistem_pakar.py --uji      # jalankan semua kasus uji dan cek hasilnya
```

**Berkas**

| Berkas | Fungsi |
|---|---|
| `kb_beasiswa.json` | Basis pengetahuan: sumber, pertanyaan, 5 aturan IF-THEN |
| `sistem_pakar.py` | Program FC: tanya fakta, jalankan aturan, tampilkan kesimpulan dan alasan |
| `kasus_uji.json` | 3 kasus uji beserta kesimpulan yang diharapkan |
| `screenshots/` | Tangkapan layar hasil menjalankan program |

## 3. Sumber dan Aturan

### Daftar sumber

| Kode | Judul | Penerbit | URL | Diakses |
|---|---|---|---|---|
| S1 | Panduan Umum Beasiswa Mahasiswa | Biro Kemahasiswaan | https://kemahasiswaan.contoh.ac.id/panduan | 12 November 2026 |
| S2 | Syarat Administrasi dan Akademik Beasiswa | Tim Seleksi Beasiswa | https://beasiswa.contoh.ac.id/ | 12 November 2026 |

### Tabel aturan IF-THEN

Kondisi diawali `!` berarti fakta dasar tersebut **tidak** ada (dijawab "tidak").

| Aturan | IF | Mode | THEN | Sumber |
|---|---|---|---|---|
| R1 | ipk_minimal AND semester_aktif | dan | syarat_akademik_ok | S1 |
| R2 | tidak_mampu AND tidak_ada_beasiswa_lain AND bebas_pelanggaran | dan | syarat_administrasi_ok | S1, S2 |
| R3 | syarat_akademik_ok AND syarat_administrasi_ok | dan | **LAYAK_BEASISWA** | S1, S2 |
| R4 | !bebas_pelanggaran | dan | **GAGAL_ADMINISTRASI** | S2 |
| R5 | syarat_akademik_ok AND !tidak_mampu | dan | **GAGAL_ADMINISTRASI** | S1 |

Dua kesimpulan akhir: `LAYAK_BEASISWA` dan `GAGAL_ADMINISTRASI`. Aturan R1 dan R2 menghasilkan fakta antara yang dipakai oleh R3, sehingga rantai inferensi berjalan terstruktur.

## 4. Metode: Forward Chaining dan alasannya

Pertanyaan pemohon berupa fakta, bukan hipotesis. Pemohon menjawab y/t untuk 5 fakta (IPK, semester, keluarga kurang mampu, beasiswa lain, dan sanksi disiplin), lalu program menurunkan kesimpulan dari fakta tersebut. Arah "dari fakta menuju kesimpulan" ini sangat cocok dengan metode **Forward Chaining (FC)**.

```text
memori <- fakta yang dijawab "ya" oleh user
ULANGI:
    cocok <- aturan yang syaratnya terpenuhi oleh memori DAN hasilnya belum ada di memori
    JIKA cocok kosong: BERHENTI
    r <- cocok[0]
    tambahkan r.maka ke memori
    catat bahwa r.maka berasal dari r
```

Aturan yang hasilnya sudah ada di memori tidak dijalankan ulang, sehingga program pasti berhenti. Kesimpulan akhir dipilih dari fakta turunan yang terdaftar sebagai `kesimpulan_akhir`, lalu alasannya ditampilkan beserta kode sumber (S1 atau S2).

## 5. Screenshot hasil

Tiga kasus berikut dijalankan dengan `python sistem_pakar.py --kasus N`.

**Kasus 1: Memenuhi semua syarat (`LAYAK_BEASISWA`)**

![Kasus 1](screenshots/kasus1.png)

**Kasus 2: Terkena sanksi disiplin (`GAGAL_ADMINISTRASI`)**

![Kasus 2](screenshots/kasus2.png)

**Kasus 3: IPK kurang dari ketentuan (tidak ada kesimpulan)**

![Kasus 3](screenshots/kasus3.png)

### Ringkasan kasus uji

| # | Jawaban "ya" | Kesimpulan yang diharapkan |
|---|---|---|
| 1 | ipk_minimal, semester_aktif, tidak_mampu, tidak_ada_beasiswa_lain, bebas_pelanggaran | LAYAK_BEASISWA |
| 2 | ipk_minimal, semester_aktif, tidak_mampu, tidak_ada_beasiswa_lain | GAGAL_ADMINISTRASI |
| 3 | semester_aktif, tidak_mampu, tidak_ada_beasiswa_lain, bebas_pelanggaran | tidak ada kesimpulan |

`python sistem_pakar.py --uji` menjalankan seluruh kasus dan melaporkan kesesuaian hasilnya.

## 6. Batas keberlakuan

- Aturan hanya memodelkan kriteria umum seleksi beasiswa mahasiswa. Ketentuan dan syarat dapat berubah sewaktu-waktu.
- Hasil program ini merupakan penilaian awal untuk kebutuhan latihan tugas, bukan keputusan mutlak kelulusan beasiswa.
- Program mempercayai jawaban *input* dari pengguna tanpa melakukan validasi dokumen fisik secara langsung.

## 7. Penggunaan alat bantu AI

Alat bantu AI yang dipakai: **Gemini (Google)**. Bantuannya mencakup merancang struktur aturan IF-THEN, menyusun draf basis pengetahuan JSON, dan merapikan dokumentasi README.