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