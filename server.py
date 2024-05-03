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
