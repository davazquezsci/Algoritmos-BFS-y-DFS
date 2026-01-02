import subprocess
from pathlib import Path

# --------------------------------------------------
# Rutas base del proyecto
# --------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
GV_DIR = ROOT / "outputs" / "gv"
IMG_DIR = ROOT / "outputs" / "img"
GRAPHVIZ_BIN = r"C:\Program Files\Graphviz\bin"

# --------------------------------------------------
# Regla de layout según el tipo de grafo
# --------------------------------------------------
def elegir_layout(nombre_archivo: str) -> str:
    """
    Árboles BFS / DFS -> dot
    Grafos base        -> sfdp
    """
    nombre = nombre_archivo.lower()
    if "bfs" in nombre or "dfs" in nombre:
        return "dot"
    return "sfdp"

# --------------------------------------------------
# Render batch
# --------------------------------------------------
def main():
    for modelo_dir in GV_DIR.iterdir():
        if not modelo_dir.is_dir():
            continue

        img_modelo_dir = IMG_DIR / modelo_dir.name
        img_modelo_dir.mkdir(parents=True, exist_ok=True)

        print(f"\nProcesando modelo: {modelo_dir.name}")

        for gv_file in modelo_dir.glob("*.gv"):
            layout = elegir_layout(gv_file.stem)
            salida = img_modelo_dir / f"{gv_file.stem}.png"

            comando = [
                str(Path(GRAPHVIZ_BIN) / f"{layout}.exe"),
                str(gv_file),
                "-Tpng",
                "-o",
                str(salida)
            ]

            subprocess.run(comando, check=True)



            print(f"  ✔ {salida.name}")

    print("\n✔ Renderizado completo.")

# --------------------------------------------------
if __name__ == "__main__":
    main()
