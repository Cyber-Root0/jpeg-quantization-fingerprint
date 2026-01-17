import os
import json
from PIL import Image
import numpy as np
DATASET_PATH = "dataset"
OUTPUT_DIR = "output"
def extract_qtables(img_path):
    img = Image.open(img_path)
    qtables = img.quantization
    if qtables is None:
        raise ValueError("Imagem não possui tabela de quantização JPEG")
    data = {}
    # Luminância
    if 0 in qtables:
        data["Y"] = np.array(qtables[0]).reshape((8, 8)).tolist()
    # Crominância (normalmente Cb e Cr usam a mesma tabela)
    if 1 in qtables:
        chroma = np.array(qtables[1]).reshape((8, 8)).tolist()
        data["Cb"] = chroma
        data["Cr"] = chroma
    return data
def build_software_database(software_path):
    database = {}
    for file in os.listdir(software_path):
        if not file.lower().endswith(".jpg"):
            continue
        quality = os.path.splitext(file)[0]
        img_path = os.path.join(software_path, file)
        try:
            qdata = extract_qtables(img_path)
            database[int(quality)] = qdata
            print(f"  └─ Qualidade {quality}% OK")
        except Exception as e:
            print(f"  [ERRO] {file}: {e}")
    return database
if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for software in os.listdir(DATASET_PATH):
        software_path = os.path.join(DATASET_PATH, software)
        if not os.path.isdir(software_path):
            continue
        print(f"\n[+] Processando dataset: {software}")
        db = build_software_database(software_path)
        output_file = os.path.join(OUTPUT_DIR, f"{software}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=4)
        print(f"[✓] Banco salvo em: {output_file}")
