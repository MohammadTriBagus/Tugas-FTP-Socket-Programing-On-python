
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
