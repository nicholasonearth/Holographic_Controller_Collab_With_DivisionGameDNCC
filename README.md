# Holographic AI Controller (DNCC Project)

Sistem kontrol game revolusioner berbasis _Computer Vision_ yang memungkinkan navigasi game tanpa menggunakan perangkat keras fisik (keyboard/mouse). Proyek ini merupakan hasil kolaborasi inovatif antara **Divisi Game** dan **Divisi Data** di DNCC.

---

### Dikembangkan Oleh:

**Nicholas Devin Daniardi - NIM: A11.2025.16355 - AI Programeer, Divisi Data DNCC**

---

## 🚀 Fitur Utama

Sistem ini menggunakan _AI Hand Tracking_ untuk membagi kendali menjadi dua zona aktif:

- **L-DRIVE (Virtual Analog):** Mengubah telapak tangan kiri menjadi _joystick_ virtual untuk navigasi WASD yang responsif.
- **R-DRIVE (Snap Aim):** Menggunakan telunjuk kanan untuk membidik target dengan akurasi 1:1.
- **Smart Interaction:** Dilengkapi fitur _auto-shoot_ terintegrasi dan pendeteksian gestur jari untuk navigasi menu tanpa menyentuh keyboard.
- **Virtual Stabilizer:** Algoritma pemulus gerakan (_LERP Smoothing_) untuk meredam getaran kamera, menjamin bidikan tetap stabil dan akurat.

## 🛠 Tech Stack

- **Language:** Python
- **AI Engine:** Google MediaPipe (21-Point Hand Landmark Tracking)
- **Computer Vision:** OpenCV (Real-time frame processing)
- **OS Integration:** Pynput (Virtual Key & Mouse Injection)

## 📋 Persyaratan Sistem

Pastikan perangkat Anda memenuhi prasyarat berikut:

1. Webcam dengan pencahayaan yang cukup.
2. Python 3.x terinstal.
3. _Install_ library yang dibutuhkan:
   ```bash
   pip install opencv-python mediapipe pynput numpy
   ```
