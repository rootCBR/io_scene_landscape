bl_info = {
    "name": "Landscape",
    "blender": (3, 0, 0),
    "category": "Import-Export",
    "version": (1, 0, 0),
    "author": "Cobra",
    "description": "Importer/exporter for 3D Landscape Engine assets ",
    "location": "File > Import/Export",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "support": "COMMUNITY",
}

import bpy
import sys
import os
import importlib

from . import MoxPanels
from . import QadPanels
from . import MoxImporterExporter
from . import CpoImporterExporter
from . import QadImporterExporter
from . import PlgImporterExporter

def reload_modules():
    importlib.reload(MoxPanels)
    importlib.reload(QadPanels)
    importlib.reload(MoxImporterExporter)
    importlib.reload(CpoImporterExporter)
    importlib.reload(QadImporterExporter)
    importlib.reload(PlgImporterExporter)
    
def register():
    MoxPanels.register()
    QadPanels.register()
    MoxImporterExporter.register()
    CpoImporterExporter.register()
    QadImporterExporter.register()
    PlgImporterExporter.register()

def unregister():
    MoxPanels.unregister()
    QadPanels.unregister()
    MoxImporterExporter.unregister()
    CpoImporterExporter.unregister()
    QadImporterExporter.unregister()
    PlgImporterExporter.unregister()
    
if __name__ == "__main__":
    register()
    
    bpy.ops.import_landscape.object('INVOKE_DEFAULT')
