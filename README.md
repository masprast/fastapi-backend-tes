# Tes _skill backend_

Repositori ini ditujukan untuk proses rekrutmen untuk posisi _backend developer_. _Tech stack_ yang digunakan untuk repo ini adalah **FastAPI** dan **Docker**.

## Prerequisites

Berikut paket-paket yang dibutuhkan dalam pembuatan API:

1. Python `--` 3.10
2. virtualenv `--` 20.13
3. [Docker](https://docs.docker.com/desktop) `--` 24.0
4. [Docker Compose](https://docs.docker.com/compose/install/) `--` 1.29
5. pip `--` 22.0

- sedangkan editor yang digunakan adalah VSCode.

> Sebelum melakukan pengetesan pastikan paket-paket yang dibutuhkan telah terinstall.

---

## Testing

Selanjutnya silahkan kloning repo ini ke dalam sebuah folder.

1. buat folder untuk menampung repo. ( **_updated_** )

   ```sh
   mkdir fastapi_backend_tes
   cd fastapi_backend_tes
   ```

   > penulis menggunakan sistem operasi Linux, untuk sistem operasi lain, silahkan menyesuaikan

2. kloning repo dari github.com.

   ```sh
   git clone https://github.com/masprast/fastapi-backend-tes .
   ```

---

### Konfigurasi _environtment_

Selanjutnya adalah melakukan konfigurasi _environtment_ agar repositori tetap terisolasi, menghindari _conflict_ dengan paket-paket yang yang sama dan telah terinstall pada komputer.

1. Menyiapkan _environtment_

   ```sh
   python3 -m venv venv
   ```

2. Mengaktifkan _environtment_

   ```sh
   . /env/bin/activate
   ```

3. Menginstall paket-paket yang dibutuhkan

   ```sh
   pip install -r requirements.txt
   ```

---

### Database (in container)

_Database_ yang digunakan adalah **PostgreSQL** dalam bentuk container dan **Adminer** sebagai RDBMS-nya. Untuk memulai _database_ + RDBMS, jalankan perintah berikut:

```sh
docker-compose up &
```

Dan tunggu hingga muncul `LOG:  database system is ready to accept connections`, sebagai tanda bahwa _server_ (container) siap untuk digunakan.

### Jalankan **FastAPI**

Buka terminal baru pada panel bawah **VSCode** untuk pengoperasian **FastAPI**. Ketikkan perintah berikut pada terminal untuk menjalankan _web server_ **FastAPI**:

```sh
python main.py
```

Tidak lama akan muncul `INFO:     Application startup complete.` sebagai tanda **FastAPI** siap digunakan.

### Testing

Untuk melakukan pengetesan pada backend, jalankan web browser dan buka alamat `localhost:8000/docs` kemudian dapat dilihat pada video di bawah ini.

![video](video.webm)
file:///home/pras/Unduhan/video.webm

> Informasi _login_ untuk `superuser` : `{"email": "super@super.su", "password": "superuser"}`

### Troubleshooting

1. Jika muncul _warning_ saat melakukan pengetesan (_running_ **FastAPI**):
   > ```sh
   > (trapped) error reading bcrypt version
   > Traceback (most recent call last):
   > File "<direktori virtual environtment>/lib/python3.10/site-packages/passlib/handlers/bcrypt.py", line 620, in _load_backend_mixin
   >  version = _bcrypt.__about__.__version__
   > AttributeError: module 'bcrypt' has no attribute '__about__'
   > ```

- Solusi: tambahkan / ganti baris kode pada informasi **_error_**

  > ```py
  > version = getattr(_bcrypt, '__version__', '<unknown>')
  > ```

- Hal ini disebabkan adanya _conflict_ antara **passlib** dengan **bcrypt** versi terbaru

## Catatan

- Masih belum bisa mengirim _email_ verifikasi ke alamat _email user_
- Tidak ada _error_ saat mengunggah _file_ atau pun memuat _file_, tetapi _file_ yang diunggah tidak dapat ditampilkan
- Superuser untuk CRUD tidak dapat login (padahal tadi siang berhasil, tiba-tiba malam _errar-error_ terus)
