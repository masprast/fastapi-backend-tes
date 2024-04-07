### Troubleshooting

1. Jika muncul _warning_ saat melakukan pengetesan:
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
