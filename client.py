import socket
import struct
import os
import time

TCP_IP = "127.0.0.1"
TCP_PORT = 1234
BUFFER_SIZE = 1024

def upload(file_path, s):
    """
    Fungsi untuk mengunggah file ke server.

    Parameters:
        file_path (str): Path lengkap file yang ingin diunggah.
        s (socket): Objek socket yang terhubung ke server.
    """
    try:
        # Mengirim perintah upload ke server
        s.send(b"upload")
        # Menerima konfirmasi dari server
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
        # Membuka file dan mengirim datanya secara berulang-ulang hingga selesai
        with open(file_path, "rb") as f:
            data = f.read(BUFFER_SIZE)
            while data:
                s.send(data)
                data = f.read(BUFFER_SIZE)
        # Menerima konfirmasi pengunggahan selesai dari server
        s.recv(BUFFER_SIZE)  
        # Menerima dan mencetak waktu yang diperlukan untuk mengunggah file
        upload_time = struct.unpack("f", s.recv(4))[0]
        print(f"File {file_name} berhasil diunggah dalam {upload_time:.2f} detik")
    except Exception as e:
        print(f"Error saat mengunggah file: {e}")

def list_files(s):
    """
    Fungsi untuk meminta dan mencetak daftar file yang ada di server.

    Parameters:
        s (socket): Objek socket yang terhubung ke server.
    """
    try:
        # Mengirim perintah ls (list) ke server
        s.send(b"ls")
        # Menerima jumlah file dari server
        num_files = struct.unpack("i", s.recv(4))[0]
        print(f"Daftar file ({num_files}):")
        # Menerima dan mencetak informasi setiap file
        for _ in range(num_files):
            file_name_size = struct.unpack("i", s.recv(4))[0]
            file_name = s.recv(file_name_size).decode()
            file_size = struct.unpack("i", s.recv(4))[0]
            print(f"\t{file_name} - {file_size} bytes")
            s.send(b"1")
        # Menerima dan mencetak total ukuran direktori
        total_size = struct.unpack("i", s.recv(4))[0]
        print(f"Total ukuran direktori: {total_size} bytes")
    except Exception as e:
        print(f"Error saat menerima daftar file: {e}")

def download(file_name, s):
    """
    Fungsi untuk mengunduh file dari server.

    Parameters:
        file_name (str): Nama file yang ingin diunduh.
        s (socket): Objek socket yang terhubung ke server.
    """
    try:
        # Mengirim perintah download ke server
        s.send(b"download")
        # Menerima konfirmasi dari server
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
        # Menerima data file secara berulang-ulang dan menuliskannya ke file lokal
        with open(file_name, "wb") as f:
            bytes_received = 0
            while bytes_received < file_size:
                data = s.recv(BUFFER_SIZE)
                f.write(data)
                bytes_received += len(data)
        print(f"File {file_name} berhasil diunduh")
        # Mengirim konfirmasi bahwa unduhan selesai ke server
        s.send(b"1")
        # Menerima dan mencetak waktu yang diperlukan untuk mengunduh file
        download_time = struct.unpack("f", s.recv(4))[0]
        print(f"Waktu unduh: {download_time:.2f} detik")
    except Exception as e:
        print(f"Error saat mengunduh file: {e}")

def delete(file_name, s):
    """
    Fungsi untuk menghapus file dari server.

    Parameters:
        file_name (str): Nama file yang ingin dihapus.
        s (socket): Objek socket yang terhubung ke server.
    """
    try:
        # Mengirim perintah delete ke server
        s.send(b"rm")
        # Menerima konfirmasi dari server
        s.recv(BUFFER_SIZE) 
        # Mengirim panjang nama file ke server
        s.send(struct.pack("h", len(file_name)))
        # Mengirim nama file ke server
        s.send(file_name.encode())
        # Meminta konfirmasi dari pengguna
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
        # Memeriksa apakah file ditemukan di server
        file_exists = struct.unpack("i", s.recv(4))[0]
        if file_exists == -1:
            print("File tidak ditemukan di server")
            return
        
def get_size(file_name, s):
    """
    Fungsi untuk meminta dan mencetak ukuran file dari server.

    Parameters:
        file_name (str): Nama file yang ukurannya ingin diketahui.
        s (socket): Objek socket yang terhubung ke server.
    """
    try:
        # Mengirim perintah size ke server
        s.send(b"size")
        # Menerima konfirmasi dari server
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
        print(f"Ukuran file {file_name}: {file_size} bytes")
    except Exception as e:
        print(f"Error saat mendapatkan ukuran file: {e}")

def connme(s):
    """
    Fungsi untuk meminta koneksi tambahan dari server.

    Parameters:
        s (socket): Objek socket yang terhubung ke server.
    """
    try:
        # Mengirim perintah connme ke server
        s.send(b"connme")
        # Menerima respons dari server
        response = s.recv(BUFFER_SIZE).decode()
        if response == "connected":
            print("Koneksi berhasil ditambahkan")
    except Exception as e:
        print(f"Error saat menambahkan koneksi: {e}")

def main():
    try:
        # Membuat koneksi socket dengan server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        print("Terhubung ke server")
        while True:
            # Meminta perintah dari pengguna
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
                # Mengirim perintah untuk menutup koneksi
                s.send(b"byebye")
                print("Menutup koneksi")
                break
            else:
                print("Perintah tidak dikenali")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
    finally:
        # Menutup koneksi socket
        s.close()

if __name__ == "__main__":
    main()
