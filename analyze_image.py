import os
import json
import hashlib
from PIL import Image
import numpy as np
OUTPUT_DIR = "output"
def extract_qtable_Y(img_path):
    img = Image.open(img_path)
    qtables = img.quantization
    if qtables is None or 0 not in qtables:
        raise ValueError("Imagem não possui tabela Y de quantização JPEG")
    Y = np.array(qtables[0]).reshape((8, 8)).tolist()
    return Y


def hash_Y(Y):
    raw = json.dumps(Y).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load_databases():
    databases = {}
    for file in os.listdir(OUTPUT_DIR):
        if not file.endswith(".json"):
            continue
        if file == "identical_index.json":
            continue
        software = os.path.splitext(file)[0]
        path = os.path.join(OUTPUT_DIR, file)
        with open(path, "r", encoding="utf-8") as f:
            databases[software] = json.load(f)
    return databases


def analyze_image(img_path):
    print(f"\n[+] Analisando imagem: {img_path}")
    Y = extract_qtable_Y(img_path)
    target_hash = hash_Y(Y)
    databases = load_databases()
    matches = []
    for software, db in databases.items():
        for quality, qdata in db.items():
            if "Y" not in qdata:
                continue
            db_hash = hash_Y(qdata["Y"])
            if db_hash == target_hash:
                matches.append({
                    "software": software,
                    "quality": quality
                })
    if not matches:
        print("\n[-] Nenhuma correspondência encontrada na base de dados.")
        print("    A imagem pode ter sido gerada por outro software,")
        print("    ou com um fator de qualidade não catalogado.")
        return
    print("\n[✓] Correspondência(s) encontrada(s):\n")
    for m in matches:
        print(f"  • Software: {m['software']} | Qualidade: {m['quality']}%")
    if len(matches) > 1:
        print("\n[!] Atenção:")
        print("    Existem múltiplas coincidências.")
        print("    Isso indica que diferentes softwares utilizam")
        print("    tabelas Y idênticas para este fator de qualidade.")
        print("    Não é possível afirmar a autoria de forma conclusiva.")
    else:
        print("\n[✓] Resultado único:")
        print("    A tabela Y é compatível com um único software e qualidade.")
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Uso:")
        print("  python analyze_image.py imagem.jpg")
        exit(1)
    image_path = sys.argv[1]
    analyze_image(image_path)
