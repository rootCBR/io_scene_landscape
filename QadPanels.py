import bpy

from . import QadTexturePanels
from . import QadMaterialPanels
from . import QadTexturePropertyGroupPanels
from . import QadObjectLibraryPanels
from . import QadObjectPanels

def register():
    QadMaterialPanels.register()
    QadTexturePropertyGroupPanels.register()
    QadTexturePanels.register()
    QadObjectLibraryPanels.register()
    QadObjectPanels.register()

def unregister():
    QadMaterialPanels.unregister()
    QadTexturePropertyGroupPanels.unregister()
    QadTexturePanels.unregister()
    QadObjectLibraryPanels.unregister()
    QadObjectPanels.unregister()