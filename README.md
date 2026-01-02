# Proyecto 2 — BFS y DFS sobre Grafos

## Descripción general

En este proyecto se implementan los algoritmos de recorrido de grafos:

- **BFS (Breadth-First Search)**
- **DFS recursivo**
- **DFS iterativo**

utilizando la **biblioteca de grafos desarrollada en el Proyecto 1**, sin copiar su código, sino importándola como submódulo.

Dado un **nodo fuente `s`**, cada algoritmo construye y regresa el **árbol inducido** correspondiente al recorrido, el cual se representa como un **grafo dirigido** (padre → hijo).

Además, se generan múltiples grafos base a partir de distintos **modelos aleatorios**, se calculan sus recorridos BFS/DFS, y se visualizan todos los grafos de forma automática.

---

## Objetivos del proyecto

- Implementar correctamente:
  ```python
  def BFS(self, s)
  def DFS_R(self, s)
  def DFS_I(self, s)


Garantizar recorridos deterministas (ordenando vecinos por id).

Generar y exportar:

    Grafos base

    Árboles BFS

    Árboles DFS (recursivo e iterativo)

Visualizar todos los grafos de manera automática, sin intervención manual.


## Estructura del Proyecto  


    PROYECTO 2/
    │
    ├── lib/
    │   └── Biblioteca-grafos/        # Proyecto 1 (importado como submódulo)
    │       ├── src/
    │       │   ├── grafo.py
    │       │   └── modelos.py
    │       └── outputs/
    │
    ├── scripts/
    │   ├── grafo_traversal.py        # Implementación BFS / DFS
    │   ├── generar_traversals.py     # Generación de grafos y recorridos
    │   └── gephi_batch_export.py     # Render automático en Gephi
    │
    ├── outputs/
    │   ├── gv/                       # Grafos en formato GraphViz (.gv)
    │   │   └── <modelo>/
    │   └── img/                      # Imágenes exportadas (.png)
    │       └── <modelo>/
    │
    ├── tests/
    └── README.md

## Modelos de grafos utilizados

Se generan grafos a partir de **6 modelos**, y para cada uno se utilizan los tamaños:

- \( n = 30 \)
- \( n = 100 \)
- \( n = 500 \)

**Total de grafos base:**

\[
6 \text{ modelos} \times 3 \text{ tamaños} = 18 \text{ grafos}
\]

---

## Grafos calculados

Para **cada grafo base** se generan los siguientes recorridos:

- Árbol **BFS**
- Árbol **DFS recursivo**
- Árbol **DFS iterativo**

**Total de grafos calculados:**

\[
18 \text{ grafos base} \times 3 \text{ recorridos} = 54 \text{ grafos}
\]

---

## Visualización (Gephi)

Todos los grafos se visualizan de forma **automática** utilizando **Gephi (v0.10.x)** mediante un script en **Jython**.

### Pipeline de visualización aplicado

Para cada grafo se ejecuta el siguiente flujo:

1. Inicialización aleatoria de posiciones (randomización manual)
2. **ForceAtlas2** sin prevenir *overlap*
3. **Ranking por grado → tamaño de nodos**
   - Tamaño mínimo: **5**
   - Tamaño máximo: **40**
4. **ForceAtlas2** con prevención de *overlap*
5. Exportación a **PNG**

### Características visuales

- **Grafos base**:
  - Aristas curvas
  - Sin flechas
- **Árboles BFS / DFS**:
  - Aristas rectas
  - Grafos dirigidos con flechas
- **Tamaño de nodos** proporcional al **grado**

---

## Cómo ejecutar el proyecto

### 1. Generar grafos y recorridos

Desde la raíz del proyecto:

```bash
python scripts/generar_traversals.py
