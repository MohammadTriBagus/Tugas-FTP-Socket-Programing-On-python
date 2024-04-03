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