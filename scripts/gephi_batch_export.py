# -*- coding: utf-8 -*-
# Gephi Scripting Plugin (Jython 2.5)
# Batch: importar .gv, correr ForceAtlas2, exportar PNG
import sys
print("=== START gephi_batch_export ===")


import os
from java.io import File
from org.openide.util import Lookup

from org.gephi.project.api import ProjectController
from org.gephi.io.importer.api import ImportController
from org.gephi.graph.api import GraphController

from org.gephi.layout.plugin.forceAtlas2 import ForceAtlas2
from org.gephi.layout.plugin.forceAtlas2 import ForceAtlas2Builder

from org.gephi.preview.api import PreviewController
from org.gephi.io.exporter.api import ExportController


# ---- AJUSTA ESTO A TU RUTA DE PROYECTO 2 ----
ROOT = r"C:\P2"

# IMPORTANTE: usar java.io.File para evitar problemas con 'ñ' en rutas
GV_DIR = File(ROOT, "outputs\\gv")
IMG_DIR = File(ROOT, "outputs\\img") 




print("ROOT =", ROOT)
print("GV_DIR =", GV_DIR.getAbsolutePath(), "exists?", GV_DIR.exists(), "isDir?", GV_DIR.isDirectory())
print("IMG_DIR =", IMG_DIR.getAbsolutePath(), "exists?", IMG_DIR.exists(), "isDir?", IMG_DIR.isDirectory())


# Fuerza el export PNG con tamaño fijo
PNG_WIDTH  = 2400
PNG_HEIGHT = 1600

# Iteraciones de ForceAtlas2 (tiempo fijo por grafo)
FA2_ITERS = 800


def ensure_dir(path_or_file):
    """
    Crea carpeta si no existe.
    Acepta:
      - str (ruta)
      - java.io.File
    """
    if isinstance(path_or_file, File):
        if not path_or_file.exists():
            path_or_file.mkdirs()
    else:
        if not os.path.exists(path_or_file):
            os.makedirs(path_or_file)


def is_tree(name):
    name = name.lower()
    return ("_bfs" in name) or ("_dfs" in name)


def run_forceatlas2(workspace, iters):
    graphModel = Lookup.getDefault().lookup(GraphController).getGraphModel(workspace)

    fa2 = ForceAtlas2(ForceAtlas2Builder())
    fa2.setGraphModel(graphModel)

    # Parámetros razonables y consistentes
    fa2.setScalingRatio(2.0)
    fa2.setGravity(1.0)
    fa2.setStrongGravityMode(False)
    fa2.setLinLogMode(False)
    fa2.setAdjustSizes(True)   # parecido a "Prevent overlap"

    fa2.initAlgo()
    for i in range(iters):
        fa2.goAlgo()
    fa2.endAlgo()


def configure_preview(workspace):
    previewController = Lookup.getDefault().lookup(PreviewController)
    previewModel = previewController.getModel(workspace)
    props = previewModel.getProperties()

    # Nodos
    props.putValue("showNodeLabels", False)

    # Aristas (preview)
    props.putValue("edgeCurved", True)
    props.putValue("edgeThickness", 1.0)

    # Flechas (para digraphs BFS/DFS)
    props.putValue("showArrows", True)
    props.putValue("arrowSize", 6.0)

    previewController.refreshPreview(workspace)


def export_png(workspace, out_file):
    """
    Exporta PNG al path indicado.
    out_file puede ser:
      - str
      - java.io.File
    """
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

    # Verificaciones mínimas
    if not GV_DIR.exists():
        raise IOError("No existe GV_DIR: " + GV_DIR.getAbsolutePath())

    ensure_dir(IMG_DIR)

    # Recorre outputs/gv/<modelo>/*.gv usando java.io.File
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
            importController.process(container, importController.getDefaultProcessor(), workspace)

            # Layout:
            # - árboles: menos iteraciones (se acomodan rápido)
            # - grafos base: más iteraciones
            iters = 250 if is_tree(name) else FA2_ITERS
            run_forceatlas2(workspace, iters)

            configure_preview(workspace)
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

