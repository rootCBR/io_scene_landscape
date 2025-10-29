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
        
class MY_PT_TexturePanel(bpy.types.Panel):
    bl_label = "QAD Texture"
    bl_idname = "MY_PT_TexturePanel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "texture"

    def draw(self, context):
        layout = self.layout
        texture = context.texture
        
        if texture:
            if hasattr(texture, "qad_texture_properties"):
                texture.qad_texture_properties.draw(context, layout)
        
classes = [
    QadTextureProperties, 
    MY_PT_TexturePanel
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Texture.qad_texture_properties = bpy.props.PointerProperty(type=QadTextureProperties)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    del bpy.types.Texture.qad_texture_properties
