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

from .MoxPanels import *
from .MoxImporterExporter import *
from .CpoImporterExporter import *
from .QadImporterExporter import *

def init():
    MoxPanels.init()
    
def reload_modules():
    importlib.reload(MoxPanels)
    importlib.reload(MoxImporterExporter)
    importlib.reload(CpoImporterExporter)
    importlib.reload(QadImporterExporter)
    
def register():
    MoxPanels.register()
    MoxImporterExporter.register()
    CpoImporterExporter.register()
    QadImporterExporter.register()

def unregister():
    MoxPanels.unregister()
    MoxImporterExporter.unregister()
    CpoImporterExporter.unregister()
    QadImporterExporter.unregister()
    
if __name__ == "__main__":
    register()
    init()
    
    bpy.ops.import_landscape.object('INVOKE_DEFAULT')
