import bpy
import math

def AddColor(context, color_name):
    scene = context.scene
    
    item = scene.mox_material_color_list.add()
    item.name = color_name
    
    for obj in scene.objects:
        if obj.type == 'MESH' and obj.active_material:
            mat = obj.active_material
            
            if hasattr(mat, "mox_material_properties"):
                mat.mox_material_properties.color_properties.add()
    
def RemoveColor(context, index):
    scene = context.scene
    
    if 0 <= index < len(scene.mox_material_color_list):
        scene.mox_material_color_list.remove(index)
        
    for obj in scene.objects:
        if obj.type == 'MESH' and obj.active_material:
            mat = obj.active_material
            
            if hasattr(mat, "mox_material_properties"):
                mat.mox_material_props.color_properties.remove(index)
    
class MoxMaterialColorProperties(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name="Name",
        description="Description",
        default="Default",
        maxlen=64
    )
    def draw(self, context, layout):
        layout.prop(self, "name")
    
class MY_OT_AddColor(bpy.types.Operator):
    bl_idname = "mox_material_color_list.add_item"
    bl_label = "Add Color"
    bl_description = "Add a new color to the set"
    
    def execute(self, context):
        AddColor(context, f"{len(context.scene.mox_material_color_list)}")
        return {'FINISHED'}
    
class MY_OT_AddDefaultColorset(bpy.types.Operator):
    bl_idname = "mox_material_color_list.add_default_items"
    bl_label = "Add Default Colorset"
    bl_description = "Add the full range of default colors to the set"
    
    def execute(self, context):
        color_names = ["Black", "White", "Silver", "Light Blue", "Blue", "Red", "Dark Red", "Yellow", "Orange", "Green"]
        
        for color_name in color_names:
            AddColor(context, color_name)
            
        return {'FINISHED'}
    
class MY_OT_RemoveColor(bpy.types.Operator):
    bl_idname = "mox_material_color_list.remove_item"
    bl_label = "Remove Color"
    bl_description = "Remove the selected color from the set"
    
    index: bpy.props.IntProperty()
    
    def execute(self, context):
        RemoveColor(context, self.index)
        return {'FINISHED'}

class MY_UL_MaterialColorList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "name", text="", emboss=False, icon='OBJECT_DATA')
        
class MY_PT_MaterialColorListPanel(bpy.types.Panel):
    bl_label = "MOX Material Colorset"
    bl_idname = "MY_PT_MaterialColorListPanel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        row = layout.row()
        row.template_list(
            "MY_UL_MaterialColorList",
            "",  # ID for active list items (unused here)
            scene, "mox_material_color_list",  # The CollectionProperty
            scene, "mox_material_color_list_index",  # The active index
        )
        
        col = row.column(align=True)
        col.operator("mox_material_color_list.add_item", icon="ADD", text="")
        col.operator("mox_material_color_list.remove_item", icon="REMOVE", text="").index = scene.mox_material_color_list_index
        
        col.operator("mox_material_color_list.add_default_items", icon="NONE", text="Add Default Colorset")
        
        if 0 <= scene.mox_material_color_list_index < len(scene.mox_material_color_list):
            item = scene.mox_material_color_list[scene.mox_material_color_list_index]
            item.draw(context, layout)
    
classes = [
    MoxMaterialColorProperties,
    MY_OT_AddColor,
    MY_OT_AddDefaultColorset,
    MY_OT_RemoveColor,
    MY_PT_MaterialColorListPanel,
    MY_UL_MaterialColorList
]

def get_material_color_items(self, context):
    scene = context.scene
    items = []
    for i, item in enumerate(scene.mox_material_color_list):
        items.append((str(i), item.name, "", i))
    return items

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.mox_material_color_list = bpy.props.CollectionProperty(type=MoxMaterialColorProperties)
    bpy.types.Scene.mox_material_color_list_index = bpy.props.IntProperty()
    bpy.types.Scene.mox_material_color_list_preview_enum = bpy.props.EnumProperty(
        name="Preview",
        items=get_material_color_items
    )

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    del bpy.types.Scene.mox_material_color_list
    del bpy.types.Scene.mox_material_color_list_index
    del bpy.types.Scene.mox_selected_color_list_enum