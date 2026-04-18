import bpy
import math

from .QadTexturePropertyGroupPanels import *

def populate_enum(self, context):
    list_items = context.scene.qad_texture_property_group_list.items()
    populate_enum.items = [((f"{i}", list_items[i][0], "")) for i in range(len(list_items))]
    return populate_enum.items

populate_enum.items = []

class QadTextureProperties(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(name="_Enabled")
    
    texture_properties_group: bpy.props.EnumProperty(
        name="Texture Property Group",
        items=populate_enum
    )
    
    def draw(self, context, layout):
        layout.prop(self, "texture_properties_group")
        
class LANDSCAPE_PT_texture_panel(bpy.types.Panel):
    bl_label = "QAD Texture"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "QAD"

    def draw(self, context):
        layout = self.layout
        
        image = context.space_data.image
        
        if image is None:
            return
        
        if not hasattr(image, "qad_texture_properties"):
            return
        
        image.qad_texture_properties.draw(context, layout)
        
classes = [
    QadTextureProperties, 
    LANDSCAPE_PT_texture_panel
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Image.qad_texture_properties = bpy.props.PointerProperty(type=QadTextureProperties)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    del bpy.types.Image.qad_texture_properties
