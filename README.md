# SisaKulkas

Deteksi bahan makanan dari foto (YOLOv8) dan rekomendasi resep masakan Indonesia.

## Jalankan
```
pip install -r requirements.txt
streamlit run app.py
```

## Struktur
- `app.py` - antarmuka Streamlit
- `matcher.py` - logika pencocokan bahan dengan resep
- `recipes.json` - database resep (tambah resep baru di sini)
- `model/best.pt` - model YOLOv8 hasil training
