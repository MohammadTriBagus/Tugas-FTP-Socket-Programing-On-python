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

## 1. Penjelasan

**server.py**

```py

import socket
import os
import struct
import time

TCP_IP = "127.0.0.1"
TCP_PORT = 1234
BUFFER_SIZE = 1024

def handle_upload(conn):
    try:
        conn.send(b"ready")
        file_name_size = struct.unpack("h", conn.recv(2))[0]
        file_name = conn.recv(file_name_size).decode()
        file_size = struct.unpack("i", conn.recv(4))[0]
        with open(file_name, "wb") as f:
            bytes_received = 0
            while bytes_received < file_size:
                data = conn.recv(BUFFER_SIZE)
                f.write(data)
                bytes_received += len(data)
        conn.send(b"received")
        upload_time = time.time()
        conn.send(struct.pack("f", time.time() - upload_time))
        print(f"{file_name} berhasil diunggah ({file_size} bytes) dalam {time.time() - upload_time:.2f} detik")
    except Exception as e:
        print(f"Error saat mengunggah file: {e}")

def handle_list_files(conn):
    try:
        files = os.listdir()
        conn.send(struct.pack("i", len(files)))
        for file_name in files:
            file_size = os.path.getsize(file_name)
            conn.send(struct.pack("i", len(file_name)))
            conn.send(file_name.encode())
            conn.send(struct.pack("i", file_size))
            conn.recv(BUFFER_SIZE)
        total_size = sum(os.path.getsize(f) for f in files)
        conn.send(struct.pack("i", total_size))
    except Exception as e:
        print(f"Error saat mengirim daftar file: {e}")

def handle_download(conn):
    try:
        conn.send(b"ready")
        file_name_size = struct.unpack("h", conn.recv(2))[0]
        file_name = conn.recv(file_name_size).decode()
        if os.path.exists(file_name):
            conn.send(struct.pack("i", os.path.getsize(file_name)))
            with open(file_name, "rb") as f:
                data = f.read(BUFFER_SIZE)
                while data:
                    conn.send(data)
                    data = f.read(BUFFER_SIZE)
            download_time = time.time()
            conn.recv(BUFFER_SIZE)
            conn.send(struct.pack("f", time.time() - download_time))
            print(f"{file_name} berhasil diunduh")
        else:
            conn.send(struct.pack("i", -1)) 
    except Exception as e:
        print(f"Error saat mengunduh file: {e}")

def handle_delete(conn):
    try:
        while True:
            conn.send(b"ready")
            file_name_size = struct.unpack("h", conn.recv(2))[0]
            file_name = conn.recv(file_name_size).decode()
            if os.path.exists(file_name):
                os.remove(file_name)
                conn.send(struct.pack("i", 1))  
                print(f"{file_name} berhasil dihapus")
            else:
                conn.send(struct.pack("i", -1))  
            response = conn.recv(BUFFER_SIZE).decode()
            if response.upper() == "Y":
                continue
            else:
                break
    except Exception as e:
        print(f"Error saat menghapus file: {e}")

def handle_get_file_size(conn):
    try:
        conn.send(b"ready")
        file_name_size = struct.unpack("h", conn.recv(2))[0]
        file_name = conn.recv(file_name_size).decode()
        if os.path.exists(file_name):
            file_size = os.path.getsize(file_name)
            conn.send(struct.pack("i", file_size))
        else:
            conn.send(struct.pack("i", -1))  
    except Exception as e:
        print(f"Error saat mendapatkan ukuran file: {e}")

def handle_connme(conn):
    try:
        conn.send(b"connected")
        print(f"Koneksi dari {conn.getpeername()} berhasil ditambahkan")
    except Exception as e:
        print(f"Error saat menambahkan koneksi: {e}")

def handle_client(conn, addr):
    print(f"Terhubung dengan {addr}")
    while True:
        try:
            command = conn.recv(BUFFER_SIZE).decode()
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
            print(f"Error saat menangani perintah dari {addr}: {e}")
            break
    conn.close()
    print(f"Koneksi dengan {addr} ditutup")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((TCP_IP, TCP_PORT))
        s.listen()
        print(f"Server FTP berjalan di {TCP_IP}:{TCP_PORT}")
        while True:
            print("Menunggu koneksi dari client...")
            conn, addr = s.accept()
            handle_client(conn, addr)

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

- Variabel Pendefinisian Anda menggunakan variabel TCP_IP dan TCP_PORT untuk menentukan alamat IP dan port yang digunakan oleh server. Selain itu, BUFFER_SIZE digunakan sebagai ukuran buffer untuk menerima data.
- Fungsi Handle untuk Setiap Perintah Anda memiliki beberapa fungsi handle untuk menangani perintah dari klien. Ini termasuk fungsi untuk mengunggah file (handle_upload), menampilkan daftar file (handle_list_files), mengunduh file (handle_download), menghapus file (handle_delete), mendapatkan ukuran file (handle_get_file_size), dan menambahkan koneksi (handle_connme).
- Fungsi Handle Client Fungsi ini menerima koneksi dari klien dan menangani perintah yang diterima dengan memanggil fungsi handle yang sesuai.
- Fungsi Utama (Main) Fungsi main() mengikat server ke alamat dan port yang ditentukan, kemudian mulai mendengarkan koneksi masuk. Setiap kali koneksi diterima, fungsi handle_client() dipanggil untuk menangani koneksi tersebut.
- Loop Utama Server berjalan dalam loop tak terbatas, terus mendengarkan koneksi baru dan menangani setiap koneksi masuk dengan memanggil fungsi handle_client(). 

Dengan demikian, server FTP sederhana ini memungkinkan klien untuk berinteraksi dengannya untuk melakukan operasi dasar pada file

<br>

**client.py**

```py

import socket
import struct
import os
import time

TCP_IP = "127.0.0.1"
TCP_PORT = 1234
BUFFER_SIZE = 1024

def upload(file_path, s):
    try:
        s.send(b"upload")
        s.recv(BUFFER_SIZE) 
        file_name = os.path.basename(file_path)
        s.send(struct.pack("h", len(file_name)))
        s.send(file_name.encode())
        file_size = os.path.getsize(file_path)
        s.send(struct.pack("i", file_size))
        with open(file_path, "rb") as f:
            data = f.read(BUFFER_SIZE)
            while data:
                s.send(data)
                data = f.read(BUFFER_SIZE)
        s.recv(BUFFER_SIZE)  
        upload_time = struct.unpack("f", s.recv(4))[0]
        print(f"File {file_name} berhasil diunggah dalam {upload_time:.2f} detik")
    except Exception as e:
        print(f"Error saat mengunggah file: {e}")

def list_files(s):
    try:
        s.send(b"ls")
        num_files = struct.unpack("i", s.recv(4))[0]
        print(f"Daftar file ({num_files}):")
        for _ in range(num_files):
            file_name_size = struct.unpack("i", s.recv(4))[0]
            file_name = s.recv(file_name_size).decode()
            file_size = struct.unpack("i", s.recv(4))[0]
            print(f"\t{file_name} - {file_size} bytes")
            s.send(b"1")
        total_size = struct.unpack("i", s.recv(4))[0]
        print(f"Total ukuran direktori: {total_size} bytes")
    except Exception as e:
        print(f"Error saat menerima daftar file: {e}")

def download(file_name, s):
    try:
        s.send(b"download")
        s.recv(BUFFER_SIZE) 
        s.send(struct.pack("h", len(file_name)))
        s.send(file_name.encode())
        file_size = struct.unpack("i", s.recv(4))[0]
        if file_size == -1:
            print("File tidak ditemukan di server")
            return
        with open(file_name, "wb") as f:
            bytes_received = 0
            while bytes_received < file_size:
                data = s.recv(BUFFER_SIZE)
                f.write(data)
                bytes_received += len(data)
        print(f"File {file_name} berhasil diunduh")
        s.send(b"1")
        download_time = struct.unpack("f", s.recv(4))[0]
        print(f"Waktu unduh: {download_time:.2f} detik")
    except Exception as e:
        print(f"Error saat mengunduh file: {e}")

def delete(file_name, s):
    try:
        s.send(b"rm")
        s.recv(BUFFER_SIZE) 
        s.send(struct.pack("h", len(file_name)))
        s.send(file_name.encode())
        confirm_delete = input(f"Apakah Anda yakin ingin menghapus {file_name}? (Y/N): ").upper()
        if confirm_delete == "Y":
            s.send(b"Y")
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
        file_exists = struct.unpack("i", s.recv(4))[0]
        if file_exists == -1:
            print("File tidak ditemukan di server")
            return
        
def get_size(file_name, s):
    try:
        s.send(b"size")
        s.recv(BUFFER_SIZE) 
        s.send(struct.pack("h", len(file_name)))
        s.send(file_name.encode())
        file_size = struct.unpack("i", s.recv(4))[0]
        if file_size == -1:
            print("File tidak ditemukan di server")
            return
        print(f"Ukuran file {file_name}: {file_size} bytes")
    except Exception as e:
        print(f"Error saat mendapatkan ukuran file: {e}")

def connme(s):
    try:
        s.send(b"connme")
        response = s.recv(BUFFER_SIZE).decode()
        if response == "connected":
            print("Koneksi berhasil ditambahkan")
    except Exception as e:
        print(f"Error saat menambahkan koneksi: {e}")

def main():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        print("Terhubung ke server")
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
                s.send(b"byebye")
                print("Menutup koneksi")
                break
            else:
                print("Perintah tidak dikenali")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
    finally:
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

- Fungsi Upload: Fungsi ini bertujuan untuk mengunggah file ke server. Klien mengirim perintah “upload” diikuti dengan nama file, ukuran file, dan data file secara bertahap. Setelah pengunggahan selesai, klien menerima waktu pengunggahan dari server dan mencetaknya.
- Fungsi List Files: Fungsi ini meminta daftar file dari server dengan mengirim perintah “ls”. Setelah menerima daftar file, klien mencetak nama dan ukuran setiap file, serta total ukuran direktori.
- Fungsi Download: Fungsi ini digunakan untuk mengunduh file dari server. Klien mengirim perintah “download” diikuti dengan nama file yang diinginkan. Klien kemudian menerima data file dari server dan menyimpannya ke dalam file lokal. Setelah selesai, klien menerima waktu pengunduhan dari server dan mencetaknya.
- Fungsi Delete: Fungsi ini bertujuan untuk menghapus file dari server. Klien mengirim perintah “rm” diikuti dengan nama file yang ingin dihapus. Sebelum menghapus file, klien meminta konfirmasi dari pengguna. Setelah menerima konfirmasi, klien menerima status penghapusan dari server dan mencetak pesan sesuai.
- Fungsi Get Size: Fungsi ini digunakan untuk mengetahui ukuran file. Klien mengirim perintah “size” diikuti dengan nama file yang ingin diketahui ukurannya. Klien menerima ukuran file dari server dan mencetaknya.
- Fungsi Connme: Fungsi ini mengirim perintah “connme” ke server untuk meminta konfirmasi koneksi. Setelah menerima konfirmasi, klien mencetak pesan yang sesuai.
- penggunaan perintah "byebye" dalam kode tersebut adalah untuk memberi tahu server bahwa klien ingin mengakhiri koneksi dengan aman. Ini adalah bagian dari protokol komunikasi antara klien dan server yang mengizinkan pengguna untuk menutup koneksi setelah selesai menggunakan layanan yang disediakan oleh server.
- Fungsi Main: Fungsi utama yang mengelola logika utama klien. Dalam loop tak terbatas, klien dapat berinteraksi dengan server dengan memilih perintah yang diinginkan.
- Exception Handling: Program memiliki penanganan kesalahan yang memadai untuk mengatasi situasi yang tidak terduga, seperti kegagalan koneksi atau kesalahan dalam operasi file.

Jadi Secara keseluruhan, program ini memungkinkan pengguna untuk terhubung ke server FTP, melakukan berbagai operasi file, dan menerima umpan balik dari server sesuai dengan hasil dari setiap operasi.


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

### Pilih Perintah

- **upload**.

```
Pilih perintah (upload/ls/download/rm/size/connme/byebye): upload
Masukkan path file yang ingin diunggah: E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\tes.txt
```

Disini saya memasukkan file yang diunggahnya yaitu ``E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\tes.txt`` ini digunakan untuk mengupload file. Jika berhasil maka akan muncul output seperti dibawah ini :

```
File tes.txt berhasil diunggah dalam 0.02 detik
```

- **ls**.

```
Pilih perintah (upload/ls/download/rm/size/connme/byebye): ls
Daftar file (4):
        .git - 4096 bytes
        client.py - 5477 bytes
        server.py - 5034 bytes
        tes.txt - 2 bytes
Total ukuran direktori: 14609 bytes
```

- **download**.
  
```
Pilih perintah (upload/ls/download/rm/size/connme/byebye): download
Masukkan nama file yang ingin diunduh: E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\tes.txt 
```

Kemudian masukkan  filenya disini saya memasukkan di ``E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\tes.txt`` dan jika berhasil maka akan muncul output sebagai berikut :

```
File E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\tes.txt  berhasil diunduh
Waktu unduh: 0.00 detik
```

- **rm**.
  
```
Pilih perintah (upload/ls/download/rm/size/connme/byebye): rm
```

ini digunakan untuk menghapus file yang ada difolder. disini saya menggunakan file_pathnta nya yaitu  E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\tes.txt , seperti dibawah ini :

```
Masukkan nama file yang ingin dihapus: E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\tes.txt 
```

Kemudian sistemnya mengkonfirmasi, apakah yakin menghapus file tersebut atau tidak(Y/N) seperti dibawah ini :

```
Apakah Anda yakin ingin menghapus E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\tes.txt ? (Y/N): Y
```

Jika menekan ``Y`` maka akan memunculkan output seperti dibawah ini :

```
File E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\tes.txt  berhasil dihapus dari server
```

Jika menekan ``N`` maka akan memunculkan output seperti dibawah ini :

```
Penghapusan file  E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\tes.txt  dibatalkan
```

- **size**.
  
```
Pilih perintah (upload/ls/download/rm/size/connme/byebye): size
```

disini saya menggunakan ``E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\tes.txt`` seperti dibawah ini :

```
Masukkan nama file yang ingin diketahui ukurannya: E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\tes.txt 
Ukuran file E:\Semester 4\Pemrograman jaringan\Tugas Dosen\Tugas 2\tes.txt : 2 bytes
```

disini saya menggunakan byte untuk ukuran filenya

- **connme**.

```
Pilih perintah (upload/ls/download/rm/size/connme/byebye): connme
```

ini digunakan untuk melakukan koneksi antaraa server dan client, Jika berhasil maka akan muncul output dibawah ini :

```
Koneksi berhasil ditambahkan
```

- **byebye**.

```
  Pilih perintah (upload/ls/download/rm/size/connme/byebye): byebye  
  Menutup koneksi
```

Ini digunakan untuk memutus koneksi antara server dan client.
