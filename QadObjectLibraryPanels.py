
import bpy
import math

class QadObjectDataProperties(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name="Name",
        description="Description",
        default="Default",
        maxlen=32
    )
    
    type: bpy.props.IntProperty(
        name="Type",
        description="Description",
        default=0,
        min=0,
        max=100
    )
    
    kick_type: bpy.props.IntProperty(
        name="Kick Type",
        description="Description",
        default=0,
        min=0,
        max=100
    )
    
    weight: bpy.props.IntProperty(
        name="Weight",
        description="Description",
        default=0
    )
    
    kick_sound: bpy.props.StringProperty(
        name="Kick Sound",
        description="Description",
        default="",
        maxlen=48
    )
    
    bounce_sound: bpy.props.StringProperty(
        name="Bounce Sound",
        description="Description",
        default="",
        maxlen=48
    )
    
    def draw(self, context, layout):
        scene = context.scene
        
        layout.prop(self, "name")
        layout.prop(self, "type")
        layout.prop(self, "kick_type")
        layout.prop(self, "weight")
        layout.prop(self, "kick_sound")
        layout.prop(self, "bounce_sound")
    
class MY_OT_AddObjectData(bpy.types.Operator):
    bl_idname = "qad_object_data_list.add_item"
    bl_label = "Add Object Data"
    bl_description = "Add a new item"
    
    def execute(self, context):
        item = context.scene.qad_object_data_list.add()
        item.name = f"Object Data {len(context.scene.qad_object_data_list)}"
        return {'FINISHED'}
    
class MY_OT_RemoveObjectData(bpy.types.Operator):
    bl_idname = "qad_object_data_list.remove_item"
    bl_label = "Remove Object Data"
    bl_description = "Remove the selected item"
    
    index: bpy.props.IntProperty()
    
    def execute(self, context):
        if 0 <= self.index < len(context.scene.qad_object_data_list):
            context.scene.qad_object_data_list.remove(self.index)
        return {'FINISHED'}

class MY_UL_ObjectDataList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "name", text="", emboss=False, icon='OBJECT_DATA')
        
class MY_PT_ObjectLibraryPanel(bpy.types.Panel):
    bl_label = "QAD Object Library"
    bl_idname = "MY_PT_ObjectLibraryPanel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        row = layout.row()
        row.template_list(
            "MY_UL_ObjectDataList",
            "",  # ID for active list items (unused here)
            scene, "qad_object_data_list",  # The CollectionProperty
            scene, "qad_object_data_list_index",  # The active index
        )
        
        col = row.column(align=True)
        col.operator("qad_object_data_list.add_item", icon="ADD", text="")
        col.operator("qad_object_data_list.remove_item", icon="REMOVE", text="").index = scene.qad_object_data_list_index
        
        if 0 <= scene.qad_object_data_list_index < len(scene.qad_object_data_list):
            item = scene.qad_object_data_list[scene.qad_object_data_list_index]
            item.draw(context, layout)
    
classes = [
    QadObjectDataProperties,
    MY_OT_AddObjectData,
    MY_OT_RemoveObjectData,
    MY_PT_ObjectLibraryPanel,
    MY_UL_ObjectDataList,
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.qad_object_data_list = bpy.props.CollectionProperty(type=QadObjectDataProperties)
    bpy.types.Scene.qad_object_data_list_index = bpy.props.IntProperty()

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    del bpy.types.Scene.qad_object_data_list
    del bpy.types.Scene.qad_object_data_list_index