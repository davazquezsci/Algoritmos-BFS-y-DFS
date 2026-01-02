import sys
from pathlib import Path

# --------------------------------------------------
# Localizar Proyecto 1 (biblioteca de grafos)
# --------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
P1_SRC = ROOT / "lib" / "Biblioteca-grafos" / "src"
sys.path.insert(0, str(P1_SRC))

from modelos import (
    grafoMalla,
    grafoErdosRenyi,
    grafoGilbert,
    grafoGeografico,
    grafoBarabasiAlbert,
    grafoDorogovtsevMendes,
)

from grafo_traversal import GrafoTraversal

# --------------------------------------------------
# Configuración general
# --------------------------------------------------
OUTPUT_GV = ROOT / "outputs" / "gv"

TAMANIOS = [30, 100, 500]

MODELOS = {
    "malla": lambda n: grafoMalla(
        m=int(n ** 0.5), n=int(n ** 0.5), dirigido=False
    ),
    "erdosrenyi": lambda n: grafoErdosRenyi(
        n=n, m=2 * n, dirigido=False, seed=42
    ),
    "gilbert": lambda n: grafoGilbert(
        n=n, p=0.05, dirigido=False, seed=42
    ),
    "geografico": lambda n: grafoGeografico(
        n=n, r=0.2, dirigido=False, seed=42
    ),
    "barabasi_albert": lambda n: grafoBarabasiAlbert(
        n=n, d=3, dirigido=False, seed=42
    ),
    "dorogovtsev_mendes": lambda n: grafoDorogovtsevMendes(
        n=n, dirigido=False, seed=42
    ),
}

# --------------------------------------------------
# Función auxiliar: convertir Grafo -> GrafoTraversal
# --------------------------------------------------
def to_traversal(g):
    gt = GrafoTraversal(dirigido=g.dirigido)
    gt._nodos = g._nodos
    gt._ady = g._ady
    gt._aristas_key = g._aristas_key
    gt._aristas = g._aristas
    return gt

# --------------------------------------------------
# Generación principal
# --------------------------------------------------
def main():
    for nombre_modelo, generador in MODELOS.items():
        carpeta = OUTPUT_GV / nombre_modelo
        carpeta.mkdir(parents=True, exist_ok=True)

        for n in TAMANIOS:
            print(f"Generando {nombre_modelo} con n={n}")

            # Grafo base
            g = generador(n)
            base_path = carpeta / f"{nombre_modelo}_n{n}.gv"
            g.to_graphviz(str(base_path))

            # Traversal
            gt = to_traversal(g)

            # Nodo fuente (convención global)
            s = min(gt._nodos.keys())

            # BFS
            T_bfs = gt.BFS(s)
            T_bfs.to_graphviz(
                str(carpeta / f"{nombre_modelo}_n{n}_bfs.gv")
            )

            # DFS recursivo
            T_dfs_r = gt.DFS_R(s)
            T_dfs_r.to_graphviz(
                str(carpeta / f"{nombre_modelo}_n{n}_dfs_r.gv")
            )

            # DFS iterativo
            T_dfs_i = gt.DFS_I(s)
            T_dfs_i.to_graphviz(
                str(carpeta / f"{nombre_modelo}_n{n}_dfs_i.gv")
            )


if __name__ == "__main__":
    main()
