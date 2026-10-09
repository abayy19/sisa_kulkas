"""Logika pencocokan bahan terdeteksi dengan database resep."""
import json
from pathlib import Path

IGNORED_CLASSES = {"image_9"}  # kelas tidak bermakna dari dataset

def norm(s: str) -> str:
    return s.strip().lower()

def load_recipes(path=None):
    path = path or Path(__file__).parent / "recipes.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def clean_ingredients(names):
    """Buang kelas yang diabaikan dan duplikat, pertahankan urutan."""
    seen, out = set(), []
    for n in names:
        k = norm(n)
        if k in IGNORED_CLASSES or k in seen:
            continue
        seen.add(k)
        out.append(n)
    return out

def recommend(ingredients, recipes, min_score=0.5):
    """Kembalikan resep terurut dari yang paling cocok.

    skor = bahan utama yang dimiliki / total bahan utama.
    Resep dengan skor di bawah min_score tidak ditampilkan.
    """
    have = {norm(i) for i in ingredients}
    results = []
    for r in recipes:
        utama = r["utama"]
        ada = [b for b in utama if norm(b) in have]
        kurang = [b for b in utama if norm(b) not in have]
        if not ada:
            continue
        score = len(ada) / len(utama)
        if score < min_score:
            continue
        opsi_ada = [b for b in r.get("opsional", []) if norm(b) in have]
        results.append({**r, "skor": score, "ada": ada, "kurang": kurang, "opsi_ada": opsi_ada})
    results.sort(key=lambda x: (-x["skor"], len(x["kurang"]), -len(x["ada"]), x["nama"]))
    return results
