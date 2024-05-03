# TUGAS 2 PEMROGRAMAN JARINGAN 
# FTP SOCKET PROGRAMMING ON PYTHON

### Nama : Mohammad Tri Bagus
### Nim  : 1203220155

## Ringkasan Tugasnya

Membuat Program FTP SOCKET menggunakan Protokol TCP, dengan menggunakan bahasa pemrograman Python.

## Soal 

Buat sebuah program file transfer protocol menggunakan socket programming dengan beberapa perintah dari client seperti berikut.
- ls : ketika client menginputkan command tersebut, maka server akan memberikan daftar file dan folder. 
- rm {nama file} : ketika client menginputkan command tersebut, maka server akan menghapus file dengan acuan nama file yang diberikan pada parameter pertama.
- download {nama file} : ketika client menginputkan command tersebut, maka server akan memberikan file dengan acuan nama file yang diberikan pada parameter pertama.
- upload {nama file} : ketika client menginputkan command tersebut, maka server akan menerima dan menyimpan file dengan acuan nama file yang diberikan pada parameter pertama.
- size {nama file} : ketika client menginputkan command tersebut, maka server akan memberikan informasi file dalam satuan MB (Mega bytes) dengan acuan nama file yang diberikan pada parameter pertama.
- byebye : ketika client menginputkan command tersebut, maka hubungan socket client akan diputus.
- connme : ketika client menginputkan command tersebut, maka hubungan socket client akan terhubung.
- Modifikasi agar file yang diterima dimasukkan ke folder tertentu
- Modifikasi program agar memberikan feedback nama file dan filesize yang diterima.
- Apa yang terjadi jika pengirim mengirimkan file dengan nama yang sama dengan file yang telah dikirim sebelumnya? Dapat menyebabkan masalah kah? Lalu bagaimana solusinya?    Implementasikan ke dalam program, solusi yang Anda berikan.

## 1. Penjelasan

**server.py**

```py
import socket
import struct
import os
import time

TCP_IP = "127.0.0.1"
TCP_PORT = 1234
BUFFER_SIZE = 1024
UPLOAD_FOLDER = "uploads"  # Folder untuk menyimpan file yang diunggah

# Fungsi untuk menangani proses upload file dari client
def handle_upload(conn):
    try:
        # Kirim sinyal siap untuk menerima file
        conn.send(b"ready")
        
        # Terima ukuran nama file dan nama file
        file_name_size = struct.unpack("h", conn.recv(2))[0]
        file_name = conn.recv(file_name_size).decode()
        
        # Tentukan path file untuk menyimpan file yang diunggah
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        
        # Jika file dengan nama yang sama sudah ada, tambahkan angka counter di belakang nama file
        file_name_without_extension, file_extension = os.path.splitext(file_name)
        counter = 1
        while os.path.exists(file_path):
            new_file_name = f"{file_name_without_extension}_{counter}{file_extension}"
            file_path = os.path.join(UPLOAD_FOLDER, new_file_name)
            counter += 1
        
        # Terima ukuran file
        file_size = struct.unpack("i", conn.recv(4))[0]
        
        # Terima data file secara bertahap dan tulis ke file
        with open(file_path, "wb") as f:
            bytes_received = 0
            while bytes_received < file_size:
                data = conn.recv(BUFFER_SIZE)
                f.write(data)
                bytes_received += len(data)
        
        # Kirim sinyal bahwa file berhasil diterima
        conn.send(b"received")
        
        # Kirim waktu upload kembali ke client
        upload_time = time.time()
        conn.send(struct.pack("f", time.time() - upload_time))
        
        # Tampilkan informasi tentang file yang diunggah
        print(f"File {file_path} ({file_size} bytes) berhasil diunggah dalam {time.time() - upload_time:.2f} detik")
    except Exception as e:
        print(f"Error saat mengunggah file: {e}")

# Fungsi untuk menangani permintaan daftar file dari client
def handle_list_files(conn):
    try:
        # Dapatkan daftar file di folder upload
        files = os.listdir(UPLOAD_FOLDER)
        
        # Kirim jumlah file ke client
        conn.send(struct.pack("i", len(files)))
        
        # Kirim informasi tentang setiap file ke client
        for file_name in files:
            file_size = os.path.getsize(os.path.join(UPLOAD_FOLDER, file_name))
            conn.send(struct.pack("i", len(file_name)))
            conn.send(file_name.encode())
            conn.send(struct.pack("i", file_size))
            conn.recv(BUFFER_SIZE)
        
        # Kirim total ukuran direktori ke client
        total_size = sum(os.path.getsize(os.path.join(UPLOAD_FOLDER, f)) for f in files)
        conn.send(struct.pack("i", total_size))
    except Exception as e:
        print(f"Error saat mengirim daftar file: {e}")

# Fungsi untuk menangani proses unduh file dari client
def handle_download(conn):
    try:
        # Kirim sinyal siap untuk menerima permintaan unduh file
        conn.send(b"ready")
        
        # Terima nama file yang akan diunduh
        file_name_size = struct.unpack("h", conn.recv(2))[0]
        file_name = conn.recv(file_name_size).decode()
        
        # Tentukan path file yang akan diunduh
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        
        # Jika file ada, kirim ukuran file ke client dan kirim data file secara bertahap
        if os.path.exists(file_path):
            conn.send(struct.pack("i", os.path.getsize(file_path)))
            with open(file_path, "rb") as f:
                data = f.read(BUFFER_SIZE)
                while data:
                    conn.send(data)
                    data = f.read(BUFFER_SIZE)
            
            # Kirim waktu unduh kembali ke client
            download_time = time.time()
            conn.recv(BUFFER_SIZE)
            conn.send(struct.pack("f", time.time() - download_time))
            print(f"File {file_name} berhasil diunduh")
        else:
            # Jika file tidak ditemukan, kirim sinyal -1 ke client
            conn.send(struct.pack("i", -1)) 
    except Exception as e:
        print(f"Error saat mengunduh file: {e}")

# Fungsi untuk menangani proses penghapusan file oleh client
def handle_delete(conn):
    try:
        while True:
            # Kirim sinyal siap untuk menerima permintaan hapus file
            conn.send(b"ready")
            
            # Terima nama file yang akan dihapus
            file_name_size = struct.unpack("h", conn.recv(2))[0]
            file_name = conn.recv(file_name_size).decode()
            
            # Tentukan path file yang akan dihapus
            file_path = os.path.join(UPLOAD_FOLDER, file_name)
            
            # Jika file ada, hapus file tersebut
            if os.path.exists(file_path):
                os.remove(file_path)
                conn.send(struct.pack("i", 1))  
                print(f"File {file_name} berhasil dihapus")
            else:
                # Jika file tidak ditemukan, kirim sinyal -1 ke client
                conn.send(struct.pack("i", -1))  
            
            # Tanyakan kepada client apakah akan melanjutkan penghapusan file
            response = conn.recv(BUFFER_SIZE).decode()
            if response.upper() == "Y":
                continue
            else:
                break
    except Exception as e:
        print(f"Error saat menghapus file: {e}")

# Fungsi untuk menangani permintaan ukuran file dari client
def handle_get_file_size(conn):
    try:
        # Kirim sinyal siap untuk menerima permintaan ukuran file
        conn.send(b"ready")
        
        # Terima nama file yang akan diketahui ukurannya
        file_name_size = struct.unpack("h", conn.recv(2))[0]
        file_name = conn.recv(file_name_size).decode()
        
        # Tentukan path file yang akan diketahui ukurannya
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        
        # Jika file ada, kirim ukuran file ke client
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            conn.send(struct.pack("i", file_size))
        else:
            # Jika file tidak ditemukan, kirim sinyal -1 ke client
            conn.send(struct.pack("i", -1))  
    except Exception as e:
        print(f"Error saat mendapatkan ukuran file: {e}")

# Fungsi untuk menangani permintaan penambahan koneksi
def handle_connme(conn):
    try:
        # Kirim sinyal koneksi berhasil ditambahkan
        conn.send(b"connected")
        print(f"Koneksi dari {conn.getpeername()} berhasil ditambahkan")
    except Exception as e:
        print(f"Error saat menambahkan koneksi: {e}")

# Fungsi untuk menangani setiap klien yang terhubung
def handle_client(conn, addr):
    print(f"Terhubung dengan {addr}")
    while True:
        try:
            # Terima perintah dari klien
            command = conn.recv(BUFFER_SIZE).decode()
            
            # Terapkan fungsi sesuai perintah yang diterima
            if command == "upload":
                handle_upload(conn)
            elif command == "ls":
                handle_list_files(conn)
            elif command == "download":
                handle_download(conn)
            elif command == "rm":
                handle_delete(conn) 
            elif command == "size":
                handle_get_file_size(conn)
            elif command == "connme":
                handle_connme(conn)
            elif command == "byebye":
                break
        except Exception as e:
            # Tangani kesalahan yang terjadi saat menjalankan perintah dari klien
            print(f"Error saat menangani perintah dari {addr}: {e}")
            break
    
    # Tutup koneksi dengan klien setelah selesai
    conn.close()
    print(f"Koneksi dengan {addr} ditutup")

# Fungsi utama untuk menjalankan server
def main():
    try:
        # Buat folder uploads jika belum ada
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        
        # Buat socket untuk server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((TCP_IP, TCP_PORT))
            s.listen()
            print(f"Server FTP berjalan di {TCP_IP}:{TCP_PORT}")
            
            # Terima koneksi dari klien dan tangani masing-masing koneksi
            while True:
                print("Menunggu koneksi dari client...")
                conn, addr = s.accept()
                handle_client(conn, addr)
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

# Jalankan fungsi utama saat program dijalankan sebagai script
if __name__ == "__main__":
    main()
```

**Outputnya**.
```
  Server FTP berjalan di 127.0.0.1:1234
  Menunggu koneksi dari client...
```

**Penjelasan Program Diatas**.

Program diatas adalah sebuah server sederhana untuk berinteraksi dengan client. Berikut analisis Kode program diatas :

- Import Library: Kode dimulai dengan mengimpor modul-modul yang diperlukan, termasuk socket, struct, os, dan time. Modul socket digunakan untuk komunikasi jaringan, struct untuk melakukan packing dan unpacking data, os untuk berinteraksi dengan sistem operasi terkait file dan folder, dan time untuk mengukur waktu eksekusi.
- Inisialisasi Variabel: Variabel seperti TCP_IP, TCP_PORT, dan BUFFER_SIZE diinisialisasi dengan nilai tertentu yang akan digunakan dalam koneksi jaringan. UPLOAD_FOLDER merupakan folder tempat file-file yang diunggah akan disimpan.
- Fungsi handle_upload(conn): Fungsi ini menangani proses upload file dari client ke server. Setelah menerima sinyal siap dari client, fungsi ini menerima nama dan ukuran file, kemudian menerima data file secara bertahap dan menuliskannya ke dalam file di folder UPLOAD_FOLDER. Jika ada file dengan nama yang sama, akan ditambahkan counter di belakang nama file untuk membedakannya. Setelah file selesai diunggah, fungsi mengirimkan sinyal berhasil dan waktu upload kembali ke client, serta mencetak informasi tentang file yang diunggah.
- Fungsi handle_list_files(conn): Fungsi ini menangani permintaan daftar file dari client. Fungsi ini mengirimkan jumlah file, nama, dan ukuran setiap file di folder UPLOAD_FOLDER ke client, serta total ukuran direktori.
- Fungsi handle_download(conn): Fungsi ini menangani permintaan unduh file dari client. Setelah menerima nama file yang diminta, fungsi ini mengirimkan ukuran file dan data file secara bertahap kepada client jika file tersedia di folder UPLOAD_FOLDER. Jika file tidak ditemukan, fungsi mengirimkan sinyal -1.
- Fungsi handle_delete(conn): Fungsi ini menangani permintaan hapus file dari client. Setelah menerima nama file yang akan dihapus, fungsi ini menghapus file tersebut jika ada di folder UPLOAD_FOLDER. Jika file tidak ditemukan, fungsi mengirimkan sinyal -1. Fungsi juga meminta konfirmasi dari client sebelum menghapus file.
- Fungsi handle_get_file_size(conn): Fungsi ini menangani permintaan ukuran file dari client. Setelah menerima nama file, fungsi ini mengirimkan ukuran file jika file tersebut ada di folder UPLOAD_FOLDER. Jika file tidak ditemukan, fungsi mengirimkan sinyal -1.
- Fungsi handle_connme(conn): Fungsi ini menangani permintaan penambahan koneksi dari client. Fungsi ini mengirim sinyal bahwa koneksi berhasil ditambahkan dan mencetak informasi tentang koneksi yang baru ditambahkan.
- Fungsi handle_client(conn, addr): Fungsi ini merupakan inti dari penanganan setiap koneksi dari client. Fungsi ini menerima perintah dari client dan memanggil fungsi yang sesuai untuk menangani perintah tersebut. Setelah selesai, koneksi ditutup.
- Fungsi main(): Fungsi utama untuk menjalankan server. Fungsi ini membuat folder UPLOAD_FOLDER jika belum ada, kemudian membuat socket untuk menerima koneksi dari client. Setiap koneksi diterima, fungsi handle_client dipanggil untuk menangani koneksi tersebut.
<br>

**client.py**

```py

import socket
import struct
import os
import time

# Inisialisasi parameter koneksi
TCP_IP = "127.0.0.1"
TCP_PORT = 1234
BUFFER_SIZE = 1024

# Fungsi untuk mengunggah file ke server
def upload(file_path, s):
    try:
        # Mengirim perintah "upload" ke server
        s.send(b"upload")
        # Menerima respons dari server
        s.recv(BUFFER_SIZE) 
        # Mendapatkan nama file dari path
        file_name = os.path.basename(file_path)
        # Mengirim panjang nama file ke server
        s.send(struct.pack("h", len(file_name)))
        # Mengirim nama file ke server
        s.send(file_name.encode())
        # Mendapatkan ukuran file
        file_size = os.path.getsize(file_path)
        # Mengirim ukuran file ke server
        s.send(struct.pack("i", file_size))
        # Membuka file untuk dikirim
        with open(file_path, "rb") as f:
            # Membaca data dari file dan mengirim ke server
            data = f.read(BUFFER_SIZE)
            while data:
                s.send(data)
                data = f.read(BUFFER_SIZE)
        # Menerima waktu yang dibutuhkan untuk mengunggah dari server
        s.recv(BUFFER_SIZE)  
        upload_time = struct.unpack("f", s.recv(4))[0]
        # Menampilkan informasi pengunggahan
        print(f"File {file_name} berhasil diunggah dalam {upload_time:.2f} detik")
    except Exception as e:
        print(f"Error saat mengunggah file: {e}")

# Fungsi untuk menampilkan daftar file di server
def list_files(s):
    try:
        # Mengirim perintah "ls" ke server
        s.send(b"ls")
        # Menerima jumlah file dari server
        num_files = struct.unpack("i", s.recv(4))[0]
        print(f"Daftar file ({num_files}):")
        # Menampilkan nama dan ukuran setiap file
        for _ in range(num_files):
            file_name_size = struct.unpack("i", s.recv(4))[0]
            file_name = s.recv(file_name_size).decode()
            file_size = struct.unpack("i", s.recv(4))[0]
            print(f"\t{file_name} - {file_size} bytes")
            s.send(b"1")
        # Menerima total ukuran direktori dari server
        total_size = struct.unpack("i", s.recv(4))[0]
        print(f"Total ukuran direktori: {total_size} bytes")
    except Exception as e:
        print(f"Error saat menerima daftar file: {e}")

# Fungsi untuk mengunduh file dari server
def download(file_name, s):
    try:
        # Mengirim perintah "download" ke server
        s.send(b"download")
        # Menerima respons dari server
        s.recv(BUFFER_SIZE) 
        # Mengirim panjang nama file ke server
        s.send(struct.pack("h", len(file_name)))
        # Mengirim nama file ke server
        s.send(file_name.encode())
        # Menerima ukuran file dari server
        file_size = struct.unpack("i", s.recv(4))[0]
        # Memeriksa apakah file ditemukan di server
        if file_size == -1:
            print("File tidak ditemukan di server")
            return
        # Membuka file untuk ditulis
        with open(file_name, "wb") as f:
            bytes_received = 0
            # Menerima data dan menuliskannya ke file
            while bytes_received < file_size:
                data = s.recv(BUFFER_SIZE)
                f.write(data)
                bytes_received += len(data)
        # Menampilkan informasi pengunduhan
        print(f"File {file_name} berhasil diunduh")
        # Mengirim konfirmasi ke server
        s.send(b"1")
        # Menerima waktu yang dibutuhkan untuk mengunduh dari server
        download_time = struct.unpack("f", s.recv(4))[0]
        print(f"Waktu unduh: {download_time:.2f} detik")
    except Exception as e:
        print(f"Error saat mengunduh file: {e}")

# Fungsi untuk menghapus file di server
def delete(file_name, s):
    try:
        # Mengirim perintah "rm" ke server
        s.send(b"rm")
        # Menerima respons dari server
        s.recv(BUFFER_SIZE) 
        # Mengirim panjang nama file ke server
        s.send(struct.pack("h", len(file_name)))
        # Mengirim nama file ke server
        s.send(file_name.encode())
        # Meminta konfirmasi pengguna untuk menghapus file
        confirm_delete = input(f"Apakah Anda yakin ingin menghapus {file_name}? (Y/N): ").upper()
        if confirm_delete == "Y":
            s.send(b"Y")
            # Menerima status penghapusan dari server
            delete_status = struct.unpack("i", s.recv(4))[0]
            if delete_status == 1:
                print(f"File {file_name} berhasil dihapus dari server")
            else:
                print(f"Gagal menghapus file {file_name}")
        else:
            s.send(b"N")
            print(f"Penghapusan file {file_name} dibatalkan")
    except Exception as e:
        print(f"Error saat menghapus file: {e}")
        # Memeriksa apakah file ada di server
        file_exists = struct.unpack("i", s.recv(4))[0]
        if file_exists == -1:
            print("File tidak ditemukan di server")
            return
        
# Fungsi untuk mendapatkan ukuran file di server
def get_size(file_name, s):
    try:
        # Mengirim perintah "size" ke server
        s.send(b"size")
        # Menerima respons dari server
        s.recv(BUFFER_SIZE) 
        # Mengirim panjang nama file ke server
        s.send(struct.pack("h", len(file_name)))
        # Mengirim nama file ke server
        s.send(file_name.encode())
        # Menerima ukuran file dari server
        file_size = struct.unpack("i", s.recv(4))[0]
        # Memeriksa apakah file ditemukan di server
        if file_size == -1:
            print("File tidak ditemukan di server")
            return
        # Menampilkan ukuran file
        print(f"Ukuran file {file_name}: {file_size} bytes")
    except Exception as e:
        print(f"Error saat mendapatkan ukuran file: {e}")

# Fungsi untuk meminta server untuk menambahkan koneksi
def connme(s):
    try:
        # Mengirim perintah "connme" ke server
        s.send(b"connme")
        # Menerima respons dari server
        response = s.recv(BUFFER_SIZE).decode()
        if response == "connected":
            print("Koneksi berhasil ditambahkan")
    except Exception as e:
        print(f"Error saat menambahkan koneksi: {e}")

# Fungsi utama
def main():
    try:
        # Membuat socket dan terhubung ke server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        print("Terhubung ke server")
        # Loop untuk menerima perintah dari pengguna
        while True:
            command = input("\nPilih perintah (upload/ls/download/rm/size/connme/byebye): ").lower()
            if command == "upload":
                file_path = input("Masukkan path file yang ingin diunggah: ")
                upload(file_path, s)
            elif command == "ls":
                list_files(s)
            elif command == "download":
                file_name = input("Masukkan nama file yang ingin diunduh: ")
                download(file_name, s)
            elif command == "rm":
                file_name = input("Masukkan nama file yang ingin dihapus: ")
                delete(file_name, s)
            elif command == "size":
                file_name = input("Masukkan nama file yang ingin diketahui ukurannya: ")
                get_size(file_name, s)
            elif command == "connme":
                connme(s)
            elif command == "byebye":
                # Mengirim perintah "byebye" ke server untuk menutup koneksi
                s.send(b"byebye")
                print("Menutup koneksi")
                break
            else:
                print("Perintah tidak dikenali")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
    finally:
        # Menutup koneksi saat program selesai
        s.close()

if __name__ == "__main__":
    main()
```

**Outputnya**.
```
Terhubung ke server

Pilih perintah (upload/ls/download/rm/size/connme/byebye):
```

**Penjelasan Program Diatas**.

Program diatas adalah sebuah client sederhana untuk berinteraksi dengan server. Berikut analisis Kode program diatas :

- upload(file_path, s):
    Fungsi ini bertanggung jawab untuk mengunggah file ke server. Pertama, fungsi ini mengirimkan perintah "upload" ke server. Kemudian, ia menerima respons dari server untuk memastikan koneksi berhasil. Selanjutnya, ia mengambil nama file dari path yang diberikan, mengirimkan panjang nama file ke server, dan mengirimkan nama file itu sendiri. Setelah itu, ia mengambil ukuran file dan mengirimkannya ke server. Fungsi ini membuka file yang akan diunggah dalam mode baca biner ("rb") dan membaca data dalam ukuran buffer hingga selesai, mengirimkan data tersebut ke server. Terakhir, setelah file selesai diunggah, ia menerima waktu yang dibutuhkan untuk mengunggah file dari server dan menampilkannya.
- list_files(s):
    Fungsi ini bertanggung jawab untuk menampilkan daftar file yang ada di server beserta ukurannya. Pertama, ia mengirimkan perintah "ls" ke server. Kemudian, ia menerima jumlah file dari server. Setelah itu, ia menerima nama dan ukuran setiap file satu per satu dari server dan menampilkannya. Terakhir, ia menerima total ukuran direktori dari server dan menampilkannya.
- download(file_name, s):
    Fungsi ini digunakan untuk mengunduh file dari server. Pertama, ia mengirimkan perintah "download" ke server. Kemudian, ia menerima respons dari server untuk memastikan koneksi berhasil. Selanjutnya, ia mengirimkan panjang nama file yang akan diunduh dan nama file itu sendiri. Setelah itu, ia menerima ukuran file dari server. Jika file tidak ditemukan, ia menampilkan pesan kesalahan. Jika file ditemukan, ia membuka file untuk ditulis dalam mode baca biner ("wb") dan menerima data dari server hingga ukuran file terpenuhi. Terakhir, setelah file berhasil diunduh, ia mengirimkan konfirmasi ke server dan menerima waktu yang dibutuhkan untuk mengunduh file dari server.
- delete(file_name, s):
    Fungsi ini bertanggung jawab untuk menghapus file di server. Pertama, ia mengirimkan perintah "rm" ke server. Kemudian, ia menerima respons dari server untuk memastikan koneksi berhasil. Selanjutnya, ia mengirimkan panjang nama file yang akan dihapus dan nama file itu sendiri. Setelah itu, ia meminta konfirmasi dari pengguna untuk menghapus file. Jika pengguna menyetujui, ia mengirimkan konfirmasi ke server dan menerima status penghapusan dari server. Terakhir, ia menampilkan pesan berhasil atau gagal berdasarkan status penghapusan.
- get_size(file_name, s):
    Fungsi ini digunakan untuk mendapatkan ukuran file dari server. Pertama, ia mengirimkan perintah "size" ke server. Kemudian, ia menerima respons dari server untuk memastikan koneksi berhasil. Selanjutnya, ia mengirimkan panjang nama file yang ukurannya ingin diketahui dan nama file itu sendiri. Setelah itu, ia menerima ukuran file dari server. Jika file tidak ditemukan, ia menampilkan pesan kesalahan. Jika file ditemukan, ia menampilkan ukuran file tersebut.
- connme(s):
    Fungsi ini bertanggung jawab untuk meminta server untuk menambahkan koneksi. Pertama, ia mengirimkan perintah "connme" ke server. Kemudian, ia menerima respons dari server untuk memastikan koneksi berhasil ditambahkan. Jika berhasil, ia menampilkan pesan koneksi berhasil ditambahkan.
- main():
    Fungsi ini merupakan fungsi utama yang mengatur alur program. Pertama, ia membuat koneksi socket ke server. Selanjutnya, ia meminta pengguna untuk memasukkan perintah dan menangani setiap perintah yang dimasukkan dengan memanggil fungsi yang sesuai. Ketika pengguna memilih untuk keluar dengan perintah "byebye", ia mengirim perintah "byebye" ke server dan menutup koneksi.

## 2. Cara Menggunakan Setiap Command
Untuk menggunakan program ini, kita harus menjalankan 2 file yaitu kita jalankan server.py terlebih dahulu kemudian menjalankan client.py
```
> server.py
  Server FTP berjalan di 127.0.0.1:1234
  Menunggu koneksi dari client...
```
```
> client.py
  Terhubung ke server

  Pilih perintah (upload/ls/download/rm/size/connme/byebye): 
```
![alt text](https://github.com/MohammadTriBagus/Tugas-FTP-Socket-Programing-On-python/blob/main/Asset/Output%20server%20dan%20client.png?raw=true)

### Pilih Perintah

## a) **upload**.

- Kita Ketik upload
  
    ```
    Pilih perintah (upload/ls/download/rm/size/connme/byebye): upload
    Masukkan path file yang ingin diunggah:
    ```
    ![alt text](https://github.com/MohammadTriBagus/Tugas-FTP-Socket-Programing-On-python/blob/main/Asset/uploadstep1.png?raw=true)

- Kemudian kita masukan file yang ingin diunggah 
    ```
    Pilih perintah (upload/ls/download/rm/size/connme/byebye): upload
    Masukkan path file yang ingin diunggah: E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\uploads\hanyates.txt
    ```
    ![alt text](https://github.com/MohammadTriBagus/Tugas-FTP-Socket-Programing-On-python/blob/main/Asset/uploadstep2.png?raw=true)

    Disini saya memasukkan file yang diunggahnya yaitu ``E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\uploads\hanyates.txt`` ini digunakan untuk mengupload file.      Jika berhasil maka akan muncul output seperti dibawah ini :

    ```
    Pilih perintah (upload/ls/download/rm/size/connme/byebye): upload
    Masukkan path file yang ingin diunggah: E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\uploads\hanyates.txt
    File hanyates.txt berhasil diunggah dalam 0.00 detik
    ```
    ![alt text](?raw=true)
  
## b) **ls**.
    ```
    Pilih perintah (upload/ls/download/rm/size/connme/byebye): ls
    ```
   ![alt text](?raw=true)
   
     ```
     Pilih perintah (upload/ls/download/rm/size/connme/byebye): ls
     Daftar file (2):
        hanyates.txt - 33 bytes
        hanyates_1.txt - 33 bytes
     Total ukuran direktori: 66 bytes
     ```
     ![alt text](?raw=true)
     
## c) **download**.
  
    ```
    Pilih perintah (upload/ls/download/rm/size/connme/byebye): download
    Masukkan nama file yang ingin diunduh: 
    ```
  ![alt text](https://github.com/MohammadTriBagus/Tugas-FTP-Socket-Programing-On-python/blob/main/Asset/download1.png?raw=true)
  
  Kemudian masukkan  filenya disini saya memasukkan di ``E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\uploads\hanyates.txt`` 
    
    ```
    Pilih perintah (upload/ls/download/rm/size/connme/byebye): download
    Masukkan nama file yang ingin diunduh: E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\uploads\hanyates.txt
    ```
   ![alt text](https://github.com/MohammadTriBagus/Tugas-FTP-Socket-Programing-On-python/blob/main/Asset/download_2.png?raw=true)

    jika berhasil maka akan muncul output sebagai berikut :
    ```
    Pilih perintah (upload/ls/download/rm/size/connme/byebye): download
    Masukkan nama file yang ingin diunduh: E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\uploads\hanyates.txt
    File E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\uploads\hanyates.txt berhasil diunduh
    Waktu unduh: 0.00 detik
    ```

  ![alt text](https://github.com/MohammadTriBagus/Tugas-FTP-Socket-Programing-On-python/blob/main/Asset/download_3.png?raw=true)
    
    
## d) **rm**.
  
    ```
    Pilih perintah (upload/ls/download/rm/size/connme/byebye): rm
    ```
   ![alt text](https://github.com/MohammadTriBagus/Tugas-FTP-Socket-Programing-On-python/blob/main/Asset/rm1.png?raw=true)

   ini digunakan untuk menghapus file yang ada difolder. disini saya menggunakan file_pathnta nya yaitu E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas          2\uploads\hanyates.txt , seperti dibawah ini :

    ```
    Pilih perintah (upload/ls/download/rm/size/connme/byebye): rm
    Masukkan nama file yang ingin dihapus: E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\uploads\hanyates.txt
    ```
   ![alt text](https://github.com/MohammadTriBagus/Tugas-FTP-Socket-Programing-On-python/blob/main/Asset/rm_2.png?raw=true)
    
   Kemudian sistemnya mengkonfirmasi, apakah yakin menghapus file tersebut atau tidak(Y/N) seperti dibawah ini :

    ```
    Pilih perintah (upload/ls/download/rm/size/connme/byebye): rm
    Masukkan nama file yang ingin dihapus: E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\uploads\hanyates.txt
    Apakah Anda yakin ingin menghapus E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\uploads\hanyates.txt? (Y/N): Y
    ```
   ![alt text](?raw=true)

  Jika menekan ``Y`` maka akan memunculkan output seperti dibawah ini :

    ```
    Pilih perintah (upload/ls/download/rm/size/connme/byebye): rm
    Masukkan nama file yang ingin dihapus: E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\uploads\hanyates.txt
    Apakah Anda yakin ingin menghapus E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\uploads\hanyates.txt? (Y/N): Y
    File E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\uploads\hanyates.txt berhasil dihapus dari server
    ```
   ![alt text](https://github.com/MohammadTriBagus/Tugas-FTP-Socket-Programing-On-python/blob/main/Asset/rm_hanyatesterhapus%20%20-%20Copy.png?raw=true)

   Jika menekan ``N`` maka akan memunculkan output seperti dibawah ini :

    ```
    Pilih perintah (upload/ls/download/rm/size/connme/byebye): rm
    Masukkan nama file yang ingin dihapus: E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\uploads
    Apakah Anda yakin ingin menghapus E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\uploads? (Y/N): N
    Penghapusan file E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\uploads dibatalkan
    ```
   ![alt text](?raw=true)

## e) **size**.
  
    ```
    Pilih perintah (upload/ls/download/rm/size/connme/byebye): size
    ```
  ![alt text](https://github.com/MohammadTriBagus/Tugas-FTP-Socket-Programing-On-python/blob/main/Asset/Size_1.png?raw=true)
  disini saya menggunakan `` E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\uploads\hanyates.txt`` seperti dibawah ini :

    ```
    Pilih perintah (upload/ls/download/rm/size/connme/byebye): size
    Masukkan nama file yang ingin diketahui ukurannya: E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\uploads\hanyates.txt
    ```
  ![alt text](https://github.com/MohammadTriBagus/Tugas-FTP-Socket-Programing-On-python/blob/main/Asset/size_2.png?raw=true)

  ```
  Pilih perintah (upload/ls/download/rm/size/connme/byebye): size
  Masukkan nama file yang ingin diketahui ukurannya: E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\uploads\hanyates.txt
  Ukuran file E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\uploads\hanyates.txt: 33 bytes
  ```
 ![alt text]( https://github.com/MohammadTriBagus/Tugas-FTP-Socket-Programing-On-python/blob/main/Asset/Size_3.png?raw=true)
  
  disini saya menggunakan byte untuk ukuran filenya

## f) **connme**.

    ```
    Pilih perintah (upload/ls/download/rm/size/connme/byebye): connme
    ```
 ![alt text](https://github.com/MohammadTriBagus/Tugas-FTP-Socket-Programing-On-python/blob/main/Asset/connme_1.png?raw=true)

ini digunakan untuk melakukan koneksi antaraa server dan client, Jika berhasil maka akan muncul output dibawah ini :

    ```
    Pilih perintah (upload/ls/download/rm/size/connme/byebye): connme
    Koneksi berhasil ditambahkan
    ```
   ![alt text](https://github.com/MohammadTriBagus/Tugas-FTP-Socket-Programing-On-python/blob/main/Asset/connme_2.png?raw=true)

## g) **byebye**.

    ```
     Pilih perintah (upload/ls/download/rm/size/connme/byebye): byebye
    ```
   ![alt text](https://github.com/MohammadTriBagus/Tugas-FTP-Socket-Programing-On-python/blob/main/Asset/bye_1.png?raw=true)

    ```
    Pilih perintah (upload/ls/download/rm/size/connme/byebye): byebye
    Menutup koneksi
    ```
   ![alt text](https://github.com/MohammadTriBagus/Tugas-FTP-Socket-Programing-On-python/blob/main/Asset/byebye.png?raw=true)

  Ini digunakan untuk memutus koneksi antara server dan client.
