import sys
from pathlib import Path
from collections import deque

# --- localizar el src del Proyecto 1 ---
ROOT = Path(__file__).resolve().parent.parent
P1_SRC = ROOT / "lib" / "Biblioteca-grafos" / "src"

sys.path.insert(0, str(P1_SRC))

# --- IMPORT REAL DE LA CLASE ---
from grafo import Grafo




from collections import deque



class GrafoTraversal(Grafo):
    """
    Extiende la clase Grafo del Proyecto 1
    para incluir BFS y DFS (recursivo e iterativo).
    """

    def BFS(self, s):
        """
        Árbol inducido por BFS desde el nodo fuente s (id).
        Regresa un nuevo Grafo.
        """
        if s not in self._nodos:
            raise KeyError(f"El nodo fuente {s} no existe en el grafo")

        T = Grafo(dirigido=self.dirigido)

        visitado = set()
        cola = deque()

        T.add_nodo(s)
        visitado.add(s)
        cola.append(s)

        while cola:
            u_id = cola.popleft()
            for v in self.vecinos(u_id):   # v es Nodo
                v_id = v.id
                if v_id not in visitado:
                    visitado.add(v_id)
                    T.add_nodo(v_id)
                    T.add_arista(u_id, v_id)
                    cola.append(v_id)

        return T

    def DFS_R(self, s):
        """
        Árbol inducido por DFS recursivo desde el nodo fuente s (id).
        """
        if s not in self._nodos:
            raise KeyError(f"El nodo fuente {s} no existe en el grafo")

        T = Grafo(dirigido=self.dirigido)
        visitado = set()

        def dfs(u_id):
            visitado.add(u_id)
            for v in self.vecinos(u_id):
                v_id = v.id
                if v_id not in visitado:
                    T.add_nodo(v_id)
                    T.add_arista(u_id, v_id)
                    dfs(v_id)

        T.add_nodo(s)
        dfs(s)
        return T

    def DFS_I(self, s):
        """
        Árbol inducido por DFS iterativo (pila) desde el nodo fuente s (id).
        """
        if s not in self._nodos:
            raise KeyError(f"El nodo fuente {s} no existe en el grafo")

        T = Grafo(dirigido=self.dirigido)

        visitado = set()
        pila = [s]

        T.add_nodo(s)
        visitado.add(s)

        while pila:
            u_id = pila.pop()

            vecinos = list(self.vecinos(u_id))
            # Si quieres orden determinista:
            # vecinos.sort(key=lambda n: n.id, reverse=True)

            for v in vecinos:
                v_id = v.id
                if v_id not in visitado:
                    visitado.add(v_id)
                    T.add_nodo(v_id)
                    T.add_arista(u_id, v_id)
                    pila.append(v_id)

        return T
