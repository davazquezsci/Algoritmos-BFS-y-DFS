# -*- coding: utf-8 -*-
# Gephi Scripting Plugin (Jython 2.5)
# Batch: importar .gv, layouts + appearance ranking, exportar PNG

print("=== START gephi_batch_export ===")

import os
from java.io import File
from org.openide.util import Lookup

from org.gephi.project.api import ProjectController
from org.gephi.io.importer.api import ImportController
from org.gephi.io.processor.plugin import DefaultProcessor
from org.gephi.graph.api import GraphController

# Layouts
from org.gephi.layout.plugin.forceAtlas2 import ForceAtlas2
from org.gephi.layout.plugin.forceAtlas2 import ForceAtlas2Builder

from java.util import Random as JRandom




# Preview + Export
from org.gephi.preview.api import PreviewController
from org.gephi.io.exporter.api import ExportController


# ---- AJUSTA ESTO A TU RUTA ----
ROOT = r"C:\P2"

GV_DIR = File(ROOT, "outputs\\gv")
IMG_DIR = File(ROOT, "outputs\\img")

print("ROOT =", ROOT)
print("GV_DIR =", GV_DIR.getAbsolutePath(), "exists?", GV_DIR.exists(), "isDir?", GV_DIR.isDirectory())
print("IMG_DIR =", IMG_DIR.getAbsolutePath(), "exists?", IMG_DIR.exists(), "isDir?", IMG_DIR.isDirectory())

# PNG
PNG_WIDTH  = 2400
PNG_HEIGHT = 1600

# Layout config
RANDOM_ITERS = 1

FA2_ITERS_1 = 400   # FA2 sin overlap
FA2_ITERS_2 = 400   # FA2 con overlap (ajustando tamaños)

# Appearance sizes
MIN_NODE_SIZE = 5.0
MAX_NODE_SIZE = 40.0


def ensure_dir(path_or_file):
    if isinstance(path_or_file, File):
        if not path_or_file.exists():
            path_or_file.mkdirs()
    else:
        if not os.path.exists(path_or_file):
            os.makedirs(path_or_file)


def is_tree(name):
    name = name.lower()
    return ("_bfs" in name) or ("_dfs" in name)


def randomize_positions(workspace, seed=1337, scale=1000.0):
    """
    Inicializa posiciones (x,y) al azar sin depender del Random layout plugin.
    Evita API mismatch de layouts en 0.10.x.
    """
    graphModel = Lookup.getDefault().lookup(GraphController).getGraphModel(workspace)
    graph = graphModel.getGraphVisible()

    rng = JRandom(seed)

    graph.writeLock()
    try:
        it = graph.getNodes().iterator()
        while it.hasNext():
            n = it.next()
            # valores en [-scale/2, scale/2]
            x = (rng.nextDouble() - 0.5) * scale
            y = (rng.nextDouble() - 0.5) * scale
            n.setX(float(x))
            n.setY(float(y))
    finally:
        graph.writeUnlock()



def run_forceatlas2(workspace, iters, prevent_overlap):
    graphModel = Lookup.getDefault().lookup(GraphController).getGraphModel(workspace)

    fa2 = ForceAtlas2(ForceAtlas2Builder())
    fa2.setGraphModel(graphModel)

    # Parámetros base
    fa2.setScalingRatio(2.0)
    fa2.setGravity(1.0)
    fa2.setStrongGravityMode(False)
    fa2.setLinLogMode(False)

    # Este switch es el que usamos como "Prevent overlap"
    fa2.setAdjustSizes(True if prevent_overlap else False)

    fa2.initAlgo()
    for i in range(iters):
        fa2.goAlgo()
    fa2.endAlgo()


def apply_degree_size_ranking(workspace, min_size, max_size):
    """
    Ranking por degree -> size, aplicado manualmente:
    size = min_size + (deg - deg_min)/(deg_max-deg_min) * (max_size-min_size)
    """
    graphModel = Lookup.getDefault().lookup(GraphController).getGraphModel(workspace)
    graph = graphModel.getGraphVisible()

    # 1) calcula grados y min/max
    degrees = {}
    deg_min = None
    deg_max = None

    it = graph.getNodes().iterator()
    while it.hasNext():
        n = it.next()
        # Para grafos dirigidos (BFS/DFS), total degree = in + out
        d = n.getInDegree() + n.getOutDegree()
        degrees[n.getId()] = d

        if deg_min is None or d < deg_min:
            deg_min = d
        if deg_max is None or d > deg_max:
            deg_max = d

    # Evita división entre cero (por ejemplo, si todos tienen el mismo degree)
    denom = float(deg_max - deg_min) if (deg_max is not None and deg_min is not None and deg_max != deg_min) else 1.0
    span = float(max_size - min_size)

    # 2) asigna size
    graph.writeLock()
    try:
        it2 = graph.getNodes().iterator()
        while it2.hasNext():
            n = it2.next()
            d = degrees.get(n.getId(), 0)
            t = float(d - deg_min) / denom
            size = float(min_size + t * span)
            n.setSize(size)
    finally:
        graph.writeUnlock()



def configure_preview(workspace, tree_mode):
    previewController = Lookup.getDefault().lookup(PreviewController)
    previewModel = previewController.getModel(workspace)
    props = previewModel.getProperties()

    # Limpio y consistente
    props.putValue("showNodeLabels", False)
    props.putValue("edgeCurved", (not tree_mode))     # grafos base curvos, árboles rectos
    props.putValue("edgeThickness", 0.3 if not tree_mode else 0.8)

    # Flechas solo para árboles (BFS/DFS dirigidos)
    props.putValue("showArrows", True if tree_mode else False)
    props.putValue("arrowSize", 8.0 if tree_mode else 0.0)

    previewController.refreshPreview(workspace)


def export_png(workspace, out_file):
    exportController = Lookup.getDefault().lookup(ExportController)
    pngExporter = exportController.getExporter("png")

    pngExporter.setWidth(PNG_WIDTH)
    pngExporter.setHeight(PNG_HEIGHT)

    if isinstance(out_file, File):
        exportController.exportFile(out_file, pngExporter)
    else:
        exportController.exportFile(File(out_file), pngExporter)


def main():
    pc = Lookup.getDefault().lookup(ProjectController)
    importController = Lookup.getDefault().lookup(ImportController)

    if not GV_DIR.exists():
        print("No existe GV_DIR:", GV_DIR.getAbsolutePath())
        raise IOError

    ensure_dir(IMG_DIR)

    model_dirs = [f for f in GV_DIR.listFiles() if f.isDirectory()]
    model_dirs.sort(key=lambda f: f.getName().lower())

    for modelo_dir in model_dirs:
        modelo = modelo_dir.getName()
        out_dir = File(IMG_DIR, modelo)
        ensure_dir(out_dir)

        gv_files = [f for f in modelo_dir.listFiles()
                    if f.isFile() and f.getName().lower().endswith(".gv")]
        gv_files.sort(key=lambda f: f.getName().lower())

        for gv_file in gv_files:
            name = gv_file.getName()[:-3]  # quita ".gv"
            out_png = File(out_dir, name + ".png")

            print("Importando:", gv_file.getAbsolutePath())

            pc.newProject()
            workspace = pc.getCurrentWorkspace()

            container = importController.importFile(gv_file)
            importController.process(container, DefaultProcessor(), workspace)

            tree_mode = is_tree(name)

            # 1) Random layout
            randomize_positions(workspace, seed=1337, scale=1000.0)


            # 2) ForceAtlas2 SIN prevent overlap
            # (si es árbol puedes bajar iters; pero lo dejo igual para uniformidad)
            run_forceatlas2(workspace, FA2_ITERS_1, prevent_overlap=False)

            # 3) Appearance: Ranking Degree -> Size (5..40)
            apply_degree_size_ranking(workspace, MIN_NODE_SIZE, MAX_NODE_SIZE)

            # 4) ForceAtlas2 CON prevent overlap (ya tomando en cuenta tamaños)
            run_forceatlas2(workspace, FA2_ITERS_2, prevent_overlap=True)

            # Preview + Export
            configure_preview(workspace, tree_mode)
            export_png(workspace, out_png)

            print("Exportado:", out_png.getAbsolutePath())

    print("DONE.")


try:
    main()
    print("=== END gephi_batch_export ===")
except Exception:
    import traceback
    err = traceback.format_exc()
    print(err)
    f = open(r"C:\P2\scripts\gephi_batch_error.txt", "w")
    f.write(err)
    f.close()
    print("ERROR guardado en C:\\P2\\scripts\\gephi_batch_error.txt")
    print("=== END gephi_batch_export ===")
