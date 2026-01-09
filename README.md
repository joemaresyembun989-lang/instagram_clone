# instagram_clone

1. Deskripsi Singkat Project
Project ini merupakan aplikasi web berbasis Flask (Python) yang meniru fitur dasar media sosial seperti Instagram. Aplikasi ini memungkinkan pengguna untuk melakukan registrasi dan login, mengunggah postingan berupa foto dan caption, melihat dan mengelola profil pengguna, melakukan follow dan unfollow antar pengguna, memberikan like dan unlike pada postingan, serta melakukan mention pengguna lain. Sistem ini menggunakan MySQL sebagai database untuk menyimpan data pengguna, postingan, dan interaksi, sedangkan tampilan antarmuka dibangun menggunakan HTML, CSS, dan Jinja2 Template dengan desain modern menyerupai Instagram.

2. Cara Menjalankan Aplikasi
1. Pastikan *Python 3* dan *XAMPP (Apache & MySQL)* sudah terinstall.
2. Jalankan *Apache dan MySQL* melalui XAMPP Control Panel.
3. Buka *phpMyAdmin* di http://localhost/phpmyadmin.
4. Buat database baru (misal: instagram_clone).
5. Import file *database.sql* ke database tersebut.
6. Buka folder project menggunakan *VS Code*.
7. Install library yang dibutuhkan:( pip install flask mysql-connector-python werkzeug)
8. Pastikan konfigurasi database di *app.py* sudah sesuai.
9. Jalankan aplikasi:( python app.py)
10. Buka browser dan akses: ( http://127.0.0.1:5000)
11. File *HTML* berada di folder templates/.
12. File *CSS* berada di folder static/.
13. Upload gambar tersimpan di folder static/uploads/.
