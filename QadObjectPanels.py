import bpy
import math

from mathutils import Vector

def populate_enum(self, context):
    list_items = context.scene.qad_object_data_list.items()
    populate_enum.items = [("NONE", "None", "")] + [((f"{i}", list_items[i][0], "")) for i in range(len(list_items))]
    return populate_enum.items

class QadObjectProperties(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(name="_Enabled")
    qad_object_dataset: bpy.props.EnumProperty(
        name="Object Dataset",
        items=populate_enum
    )
    
    def draw(self, context, layout):
        layout.prop(self, "qad_object_dataset")
    
class OBJECT_PT_qad(bpy.types.Panel):
    bl_label = "QAD"
    bl_idname = "OBJECT_PT_qad"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        if hasattr(obj, "qad_object_properties"):
            obj.qad_object_properties.draw(context, layout)

def register():
    bpy.utils.register_class(QadObjectProperties)
    bpy.types.Object.qad_object_properties = bpy.props.PointerProperty(type=QadObjectProperties)
    bpy.utils.register_class(OBJECT_PT_qad)

def unregister():
    del bpy.types.Object.qad_object_properties
    bpy.utils.unregister_class(QadObjectProperties)
    bpy.utils.unregister_class(OBJECT_PT_qad)