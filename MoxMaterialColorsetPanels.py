import bpy
import math

def add_color(context, color_name):
    scene = context.scene

    item = scene.mox_material_color_list.add()
    item.name = color_name

    all_materials = set()
    for obj in scene.objects:
        if obj.type == 'MESH':
            for slot in obj.material_slots:
                if slot.material and hasattr(slot.material, "mox_material_properties"):
                    all_materials.add(slot.material)

    for mat in all_materials:
        mat.mox_material_properties.color_properties.add()
    
def remove_color(context, index):
    scene = context.scene
    
    if 0 <= index < len(scene.mox_material_color_list):
        scene.mox_material_color_list.remove(index)
        
    all_materials = set()
    for obj in scene.objects:
        if obj.type == 'MESH':
            for slot in obj.material_slots:
                if slot.material and hasattr(slot.material, "mox_material_properties"):
                    all_materials.add(slot.material)

    for mat in all_materials:
        mat.mox_material_properties.color_properties.remove(index)
    
class MoxMaterialColorProperties(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name="Name",
        description="Description",
        default="Default",
        maxlen=64
    )
    def draw(self, context, layout):
        layout.prop(self, "name")
    
class LANDSCAPE_OT_add_color(bpy.types.Operator):
    bl_idname = "mox_material_color_list.add_item"
    bl_label = "Add Color"
    bl_description = "Add a new color to the set"
    
    def execute(self, context):
        add_color(context, f"{len(context.scene.mox_material_color_list)}")
        return {'FINISHED'}
    
class LANDSCAPE_OT_add_default_colorset(bpy.types.Operator):
    bl_idname = "mox_material_color_list.add_default_items"
    bl_label = "Add Default Colorset"
    bl_description = "Add the full range of default colors to the set"
    
    def execute(self, context):
        color_names = ["Black", "White", "Silver", "Light Blue", "Blue", "Red", "Dark Red", "Yellow", "Orange", "Green"]
        
        for color_name in color_names:
            add_color(context, color_name)
            
        return {'FINISHED'}
    
class LANDSCAPE_OT_remove_color(bpy.types.Operator):
    bl_idname = "mox_material_color_list.remove_items"
    bl_label = "Remove Color"
    bl_description = "Remove the selected color from the set"
    
    index: bpy.props.IntProperty()
    
    def execute(self, context):
        scene = context.scene
        color_list = scene.mox_material_color_list
    
        if len(color_list) <= 1:
            self.report({'WARNING'}, "A minimum of 1 color must be present.")
            return {'CANCELLED'}
    
        remove_color(context, self.index)
        return {'FINISHED'}

class LANDSCAPE_UL_material_color_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "name", text="", emboss=False, icon='OBJECT_DATA')
        
class LANDSCAPE_MT_material_color_context_menu(bpy.types.Menu):
    bl_label = "Color Specials"

    def draw(self, _context):
        layout = self.layout
        
        layout.operator("mox_material_color_list.add_default_items", icon="NONE", text="Add Color Preset")
        
class LANDSCAPE_PT_material_color_list_panel(bpy.types.Panel):
    bl_label = "MOX Material Colorset"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        row = layout.row()
        row.template_list(
            "LANDSCAPE_UL_material_color_list",
            "",  # ID for active list items (unused here)
            scene, "mox_material_color_list",  # The CollectionProperty
            scene, "mox_material_color_list_index",  # The active index
        )
        
        col = row.column(align=True)
        
        row = col.row()
        row.operator("mox_material_color_list.add_item", icon="ADD", text="")
        row.enabled = len(scene.mox_material_color_list) < 32
        
        row = col.row()
        row.operator("mox_material_color_list.remove_items", icon="REMOVE", text="").index = scene.mox_material_color_list_index
        row.enabled = len(scene.mox_material_color_list) > 1

        col.separator()

        col.menu("LANDSCAPE_MT_material_color_context_menu", icon='DOWNARROW_HLT', text="")
        
        if 0 <= scene.mox_material_color_list_index < len(scene.mox_material_color_list):
            item = scene.mox_material_color_list[scene.mox_material_color_list_index]
            item.draw(context, layout)
    
classes = [
    MoxMaterialColorProperties,
    LANDSCAPE_OT_add_color,
    LANDSCAPE_OT_add_default_colorset,
    LANDSCAPE_OT_remove_color,
    LANDSCAPE_MT_material_color_context_menu,
    LANDSCAPE_PT_material_color_list_panel,
    LANDSCAPE_UL_material_color_list
]

def get_material_color_items(self, context):
    scene = context.scene
    items = []
    for i, item in enumerate(scene.mox_material_color_list):
        items.append((str(i), item.name, "", i))
    return items

@bpy.app.handlers.persistent
def on_load_post(filepath):
    context = bpy.context
    scene = context.scene
    color_list = scene.mox_material_color_list
    
    if len(color_list) < 1:
        add_color(context, "Default")
            
def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.mox_material_color_list = bpy.props.CollectionProperty(type=MoxMaterialColorProperties)
    bpy.types.Scene.mox_material_color_list_index = bpy.props.IntProperty()
    bpy.types.Scene.mox_material_color_list_preview_enum = bpy.props.EnumProperty(
        name="Preview",
        items=get_material_color_items
    )
    bpy.app.handlers.load_factory_startup_post.append(on_load_post)
    bpy.app.handlers.load_post.append(on_load_post)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    del bpy.types.Scene.mox_material_color_list
    del bpy.types.Scene.mox_material_color_list_index
    del bpy.types.Scene.mox_selected_color_list_enum
    bpy.app.handlers.load_factory_startup_post.remove(on_load_post)
    bpy.app.handlers.load_post.remove(on_load_post)