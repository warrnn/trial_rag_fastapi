user_charateristics_database = [
    "Umur 47 tahun",
    "Tinggi badan 155 cm",
    "Berat badan 58 kg",
    "Gender Perempuan",
    "Suntik Insulin harian menggunakan Novorapid",
    "Sunti Insulin malam menggunakan Lantus",
    "Tidak minum obat pengontrol gula darah",
    "Last hba1c: 5.4%",
]

hba1c_knowledge_database = [
    # --- Fakta HbA1c ---
    "HbA1c adalah tes darah yang mengukur rata-rata gula darah selama 3 bulan dan disajikan dalam persentase (%).",
    "Hasil tes HbA1c mengindikasikan kadar rata-rata gula darah selama 2-3 bulan terakhir dan dikategorikan sebagai normal, prediabetes, atau diabetes.",
    "eAG (estimated Average Glucose) adalah konversi nilai HbA1c (%) ke satuan mg/dl.",
    "Rumus resmi untuk menghitung eAG (mg/dl) dari HbA1c (%) adalah: (28.7 * HbA1c) - 46.7",
    "Rumus resmi untuk menghitung HbA1c (%) dari eAG (mg/dl) adalah: (eAG + 46.7) / 28.7",
    "Interpretasi hasil HbA1c Normal: Kurang dari 5,7%; Prediabetes: 5,7% - 6,4%; Diabetes: 6,5% atau lebih tinggi.",
]

knowledge_database = [
    # --- Fakta yang Sudah Ada (Karbohidrat) ---
    "Satu porsi 15 gram karbohidrat umumnya dapat menaikkan gula darah sekitar 30-50 mg/dl.",
    "Nasi putih adalah sumber karbohidrat tinggi yang cepat menaikkan gula darah.",
    "Mie, roti tawar putih, dan kentang goreng juga merupakan karbohidrat yang cepat diserap tubuh.",
    "Serat, seperti dari sayuran hijau, dapat membantu memperlambat kenaikan gula darah setelah makan.",
    # --- Fakta Pisang (Tambahan Anda) ---
    "Tingkat kematangan pisang sangat mempengaruhi gula darah. Pisang yang masih hijau (mentah) memiliki lebih banyak pati resisten dan indeks glikemik lebih rendah.",
    "Pisang yang sangat matang (kuning berbintik) memiliki lebih banyak gula sederhana dan indeks glikemik lebih tinggi, sehingga lebih cepat menaikkan gula darah.",
    "Pisang Ambon (Cavendish) ukuran sedang (sekitar 120 gram) mengandung sekitar 27-30 gram karbohidrat.",
    "Pisang Kepok, terutama jika direbus atau dikukus, sering dianggap sebagai pilihan yang lebih baik karena memiliki indeks glikemik yang cenderung lebih rendah.",
    "Pisang Raja memiliki rasa yang manis. Satu buah Pisang Raja ukuran sedang (sekitar 120 gram) mengandung rata-rata 30 gram karbohidrat.",
    # --- FAKTA TAMBAHAN UNTUK DATABASE ---
    # Fakta Pola Makan (Protein & Lemak)
    "Protein, seperti dada ayam, ikan, telur, dan tahu, tidak menaikkan gula darah secara signifikan dan membantu merasa kenyang lebih lama.",
    "Lemak sehat, seperti yang ditemukan di alpukat, kacang almond, dan minyak zaitun, baik untuk kesehatan jantung dan dapat membantu menstabilkan gula darah.",
    "Minuman manis seperti soda, jus buah kemasan, teh manis, dan kopi saset mengandung gula tersembunyi yang sangat tinggi dan harus dihindari.",
    "Penting untuk membaca label nutrisi pada makanan kemasan, perhatikan 'Total Karbohidrat' (Total Carbohydrates) bukan hanya 'Gula' (Sugars).",
    "Metode memasak penting. Merebus, mengukus, atau memanggang lebih baik daripada menggoreng, karena menggoreng menambah lemak tidak sehat.",
    # Fakta Aktivitas Fisik
    "Aktivitas fisik membuat sel-sel tubuh lebih sensitif terhadap insulin, ini membantu tubuh menggunakan gula darah dengan lebih efisien.",
    "Olahraga teratur, seperti jalan cepat 30 menit lima kali seminggu, adalah rekomendasi standar untuk penderita diabetes.",
    "Jalan kaki singkat selama 10-15 menit setelah makan besar dapat membantu menurunkan lonjakan gula darah (postprandial).",
    "Latihan beban (angkat dambel, push-up) juga penting karena membangun otot, dan otot membantu membakar glukosa bahkan saat istirahat.",
    # Fakta Obat & Pemantauan
    "Metformin adalah obat lini pertama yang umum untuk diabetes tipe 2, bekerja dengan mengurangi produksi gula di hati dan meningkatkan sensitivitas insulin.",
    "Insulin suntik digunakan ketika tubuh tidak lagi memproduksi cukup insulin, atau sel-sel tubuh sangat resisten.",
    "Sangat penting untuk meminum obat diabetes pada waktu yang sama setiap hari sesuai anjuran dokter untuk menjaga kadar obat dalam tubuh tetap stabil.",
    "Mencatat gula darah secara teratur (monitoring) membantu Anda dan dokter melihat pola dan menyesuaikan pengobatan atau gaya hidup.",
    "Mengecek gula darah 2 jam setelah makan sangat penting untuk memahami bagaimana tubuh Anda bereaksi terhadap jenis dan porsi makanan tertentu.",
    # Fakta Level Gula Darah & Kondisi
    "Gula darah puasa (pagi hari) yang normal adalah di bawah 100 mg/dl.",
    "Gula darah puasa (pagi hari) di atas 126 mg/dl, seperti 150 mg/dl, mengindikasikan kondisi diabetes.",
    "Gula darah 2 jam setelah makan yang normal adalah di bawah 140 mg/dl.",
    "Target gula darah 2 jam setelah makan untuk penderita diabetes umumnya adalah di bawah 180 mg/dl.",
    "Gula darah 2 jam setelah makan di atas 200 mg/dl mengindikasikan diabetes atau kontrol yang belum baik.",
    "Hipoglikemia adalah kondisi gula darah terlalu rendah (di bawah 70 mg/dl), gejalanya pusing, keringat dingin, lemas, dan gemetar. Harus segera ditangani dengan konsumsi 15 gram gula sederhana (seperti permen atau teh manis).",
    "Hiperglikemia adalah kondisi gula darah terlalu tinggi, gejalanya sering haus, sering buang air kecil, dan pandangan kabur.",
    "Pusing, mual, dan migrain bisa jadi gejala gula darah yang tidak stabil, baik terlalu tinggi (hiperglikemia) atau terlalu rendah (hipoglikemia).",
    # Fakta Gaya Hidup & Komplikasi
    "Stres dapat memicu pelepasan hormon kortisol, yang dapat menaikkan kadar gula darah secara langsung, bahkan jika Anda tidak makan.",
    "Kurang tidur (di bawah 6-7 jam per malam) dapat memperburuk resistensi insulin dan membuat kontrol gula darah lebih sulit.",
    "Penderita diabetes harus memeriksa kaki mereka setiap hari untuk luka kecil, lecet, atau kemerahan, karena kerusakan saraf (neuropati) dapat membuat luka tidak terasa.",
    # Disclaimer
    "Penting untuk berkonsultasi dengan dokter untuk saran medis, karena respons gula darah setiap orang berbeda.",
    "Informasi ini adalah estimasi umum dan tidak menggantikan saran medis profesional dari dokter atau ahli gizi.",
    # --- Fakta Pisang ---
    "Tingkat kematangan pisang sangat mempengaruhi gula darah. Pisang yang masih hijau (mentah) memiliki lebih banyak pati resisten dan indeks glikemik lebih rendah.",
    "Pisang yang sangat matang (kuning berbintik) memiliki lebih banyak gula sederhana dan indeks glikemik lebih tinggi, sehingga lebih cepat menaikkan gula darah.",
    # --- Pisang Raja ---
    "Pisang Raja memiliki rasa yang manis dan sering dikonsumsi langsung atau digoreng.",
    "Satu buah Pisang Raja ukuran sedang (sekitar 120 gram) mengandung rata-rata 30 gram karbohidrat.",
    "Meskipun bergizi, pasien diabetes harus sangat memperhatikan porsi Pisang Raja karena kandungan karbohidrat dan gulanya yang relatif tinggi.",
    "Menggoreng Pisang Raja (seperti pisang goreng) akan menambah kalori dan lemak, yang dapat mempengaruhi sensitivitas insulin dan kontrol gula darah secara keseluruhan."
    # Pisang Ambon (Cavendish)
    "Pisang Ambon (Cavendish) ukuran sedang (sekitar 120 gram) mengandung sekitar 27-30 gram karbohidrat, mirip dengan Pisang Raja.",
    "Pisang Ambon memiliki indeks glikemik (GI) sedang, namun GI-nya akan meningkat seiring semakin matangnya pisang.",
    # Pisang Kepok (Saba)
    "Pisang Kepok, terutama jika direbus atau dikukus, sering dianggap sebagai pilihan yang lebih baik karena memiliki indeks glikemik yang cenderung lebih rendah dibandingkan pisang yang dimakan langsung.",
    "Satu buah Pisang Kepok rebus (sekitar 100 gram) mengandung kira-kira 28 gram karbohidrat.",
    # Pisang Emas / Pisang Susu
    "Pisang Emas atau Pisang Susu berukuran kecil, namun tetap padat gula. Porsi harus diperhatikan, 2-3 buah pisang emas kecil bisa setara dengan 15-20 gram karbohidrat.",
]
