import os
import json
import hashlib
OUTPUT_DIR = "output"
INDEX_FILE = os.path.join(OUTPUT_DIR, "identical_index.json")
def hash_qtable(qdata):
    """
    Gera um hash considerando SOMENTE a tabela Y (luminância).
    Cb e Cr são ignoradas.
    """
    if "Y" not in qdata:
        raise ValueError("Tabela Y não encontrada nos dados de quantização")
    raw = json.dumps(qdata["Y"]).encode("utf-8")
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
def compare_databases(databases):
    """
    Retorna um dicionário no formato:
    {
        "75": ["photoshop", "gimp"],
        "90": ["gimp", "paintnet"]
    }
    apenas quando houver igualdade entre dois ou mais softwares.
    """
    quality_map = {}
    all_qualities = set()
    for db in databases.values():
        all_qualities.update(db.keys())
    for quality in sorted(all_qualities, key=int):
        hash_map = {}
        for software, db in databases.items():
            if quality not in db:
                continue
            qdata = db[quality]
            qhash = hash_qtable(qdata)
            if qhash not in hash_map:
                hash_map[qhash] = []
            hash_map[qhash].append(software)
        # Só nos interessam hashes que aparecem em mais de um software
        for softwares in hash_map.values():
            if len(softwares) > 1:
                quality_map.setdefault(quality, []).append(softwares)
    return quality_map
if __name__ == "__main__":
    databases = load_databases()
    identical = compare_databases(databases)
    print("\n[+] Comparação entre datasets:\n")
    for quality, groups in identical.items():
        for group in groups:
            print(f"{quality}%: " + " e ".join(group) + " são idênticos")
    # Arquivo de índice apenas observacional
    index_data = {
        "warning": (
            "Este arquivo indica apenas que existem tabelas de quantização "
            "idênticas entre softwares para determinados fatores de qualidade. "
            "Isso NÃO é evidência conclusiva de autoria ou origem da imagem."
        ),
        "identical_qualities": identical
    }
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=4, ensure_ascii=False)

    print(f"\n[✓] Arquivo de índice salvo em: {INDEX_FILE}")
