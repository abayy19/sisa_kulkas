import streamlit as st
from PIL import Image
from ultralytics import YOLO

from matcher import clean_ingredients, load_recipes, recommend

st.set_page_config(page_title="SisaKulkas", page_icon="🍳", layout="wide")

@st.cache_resource
def get_model():
    return YOLO("model/best.pt")

@st.cache_data
def get_recipes():
    return load_recipes()

model = get_model()
recipes = get_recipes()
all_classes = clean_ingredients(model.names.values())

st.title("🍳 SisaKulkas")
st.caption("Foto bahan makanan di kulkasmu, dapatkan rekomendasi masakan.")

with st.sidebar:
    st.header("Pengaturan")
    conf = st.slider("Ambang keyakinan deteksi", 0.1, 0.9, 0.4, 0.05)
    min_score = st.slider("Kecocokan minimal resep", 0.3, 1.0, 0.6, 0.1,
                          help="Persentase bahan utama resep yang harus sudah kamu miliki.")

source = st.radio("Sumber gambar", ["Unggah foto", "Kamera"], horizontal=True)
file = st.file_uploader("Pilih foto", type=["jpg", "jpeg", "png"]) if source == "Unggah foto" \
    else st.camera_input("Ambil foto")

if file is None:
    st.info("Unggah atau ambil foto bahan makanan untuk memulai.")
    st.stop()

img = Image.open(file).convert("RGB")
with st.spinner("Mendeteksi bahan..."):
    res = model.predict(img, conf=conf, verbose=False)[0]

detected = clean_ingredients([model.names[int(c)] for c in res.boxes.cls])

col1, col2 = st.columns(2)
col1.subheader("Hasil deteksi")
col1.image(res.plot()[:, :, ::-1], use_container_width=True)  # BGR -> RGB

col2.subheader("Bahan yang kamu punya")
col2.caption("Hasil deteksi bisa salah. Hapus yang keliru atau tambahkan yang terlewat.")
ingredients = col2.multiselect("Bahan", options=all_classes, default=detected)

st.divider()
st.subheader("Rekomendasi masakan")

if not ingredients:
    st.warning("Belum ada bahan terpilih.")
    st.stop()

hasil = recommend(ingredients, recipes, min_score=min_score)
if not hasil:
    st.warning("Belum ada resep yang cocok. Coba tambah bahan atau turunkan kecocokan minimal.")
    st.stop()

for r in hasil:
    siap = not r["kurang"]
    label = "✅ Bisa dibuat sekarang" if siap else f"⚠️ Kurang: {', '.join(r['kurang'])}"
    with st.expander(f"{r['nama']}  -  {int(r['skor']*100)}% cocok  |  {label}"):
        st.markdown(f"**Bahan utama:** {', '.join(r['utama'])}")
        if r["opsional"]:
            st.markdown(f"**Bahan opsional:** {', '.join(r['opsional'])}")
        st.markdown(f"**Bumbu dapur:** {r['pantry']}")
        st.markdown("**Langkah:**")
        for i, s in enumerate(r["langkah"], 1):
            st.markdown(f"{i}. {s}")
