import bpy
import math

from .QadMaterials import *

class OBJECT_OT_TexturePropertyGroupAction(bpy.types.Operator):
    """Custom action for any object"""
    bl_idname = "object.qad_texture_property_group_action"
    bl_label = "No Collision"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = context.selected_objects

        if not selected_objects:
            self.report({'WARNING'}, "No objects selected.")
            return {'CANCELLED'}

        def process_object(obj):
            print(f"process_object() {obj.name}")
            
            if obj.type == 'MESH':  # Only consider mesh objects with materials
                for material_slot in obj.material_slots:
                    material = material_slot.material
                        
                    print(f"material: {material.name}")
                        
                    qad_material_properties = material.qad_material_properties
                            
                    textures = [
                        qad_material_properties.texture_1,
                        qad_material_properties.texture_2,
                        qad_material_properties.texture_3,
                        qad_material_properties.texture_4,
                        qad_material_properties.bump_texture_1,
                        qad_material_properties.bump_texture_2,
                        qad_material_properties.bump_texture_3
                    ]
                            
                    for texture in textures:
                        print(f"texture: {texture}")
                                
                        if not texture:
                            continue
                                
                        no_collision_texture_property_group_index = None

                        for i in range(len(bpy.context.scene.qad_texture_property_group_list)):
                            qad_texture_property_group_properties = bpy.context.scene.qad_texture_property_group_list[i]
                            
                            if qad_texture_property_group_properties.collision_options == 1:
                                no_collision_texture_property_group_index = i
                                break
                                     
                        if not no_collision_texture_property_group_index:
                            self.report({'WARNING'}, f"Could not find QAD texture property group with collisions disabled")

                        qad_texture_properties = texture.qad_texture_properties
                                
                        if not qad_texture_properties:
                            self.report({'WARNING'}, f"No QAD texture properties on texture {texture.name}")
                            continue
                                
                        qad_texture_properties.texture_properties_group = f"{no_collision_texture_property_group_index}"

            for child in obj.children:
                process_object(child)

        for obj in selected_objects:
            process_object(obj)
            
        self.report({'INFO'}, f"Done.")
        
        return {'FINISHED'}
    
class OBJECT_PT_TexturePropertyGroupActionPanel(bpy.types.Panel):
    """Creates a panel in the Object Properties"""
    bl_label = "QAD (1)"
    bl_idname = "OBJECT_PT_TexturePropertyGroupActionPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QAD'

    def draw(self, context):
        layout = self.layout
        layout.operator("object.qad_texture_property_group_action")
        
class QadTexturePropertyGroupProperties(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name="Name",
        description="Description",
        default="Default",
        maxlen=64
    )
    
    # Staub
    dust: bpy.props.IntProperty(
        name="Dust",
        description="Description",
        default=0,
        min=0,
        max=100
    )
    
    # GripV
    grip_front: bpy.props.IntProperty(
        name="Grip Front",
        description="Description",
        default=100,
        min=0,
        max=100
    )
    
    # GripH
    grip_rear: bpy.props.IntProperty(
        name="Grip Rear",
        description="Description",
        default=100,
        min=0,
        max=100
    )
    
    # Brems
    brake: bpy.props.IntProperty(
        name="Brake",
        description="Description",
        default=0,
        min=0,
        max=100
    )
    
    # Schlupfmodus
    # 0 - Normal
    # 1 - Gras/etc
    # 2 - Kies
    slip_mode: bpy.props.IntProperty(
        name="Slip Mode",
        description="0: Normal; 1: Dirt; 2: Gravel",
        default=0,
        min=0,
        max=2
    )
    
    skidmark_type_black: bpy.props.BoolProperty(name="Black Skidmarks", default=True)
    
    skidmark_type_colored: bpy.props.BoolProperty(name="Colored Skidmarks", default=False)
    
    sound: bpy.props.StringProperty(
        name="Sound",
        description="Description",
        default="",
        maxlen=64
    )
    
    collision_options: bpy.props.IntProperty(
        name="Collision Options",
        description="Set to 1 to disable collisions for this texture property group.",
        default=0,
        min=0,
        max=100
    )
    
    # Kollisound
    # 0 - Stein
    # 1 - Metall
    # 2 - Erde
    collision_sound_type: bpy.props.IntProperty(
        name="Collision Sound Type",
        description="0: Stone; 1: Metal; 2: Dirt",
        default=0,
        min=0,
        max=2
    )
    
    enable_shadow: bpy.props.BoolProperty(name="Cast Shadow", default=True)
    
    enable_render: bpy.props.BoolProperty(name="Visible", default=True)
    
    emitter: bpy.props.IntProperty(
        name="Particle Emitter",
        description="Description",
        default=0,
        min=0,
        max=255
    )
    
    rumble_slow: bpy.props.IntProperty(
        name="Rumble Slow",
        description="Description",
        default=0,
        min=0,
        max=100
    )
    
    rumble_fast: bpy.props.IntProperty(
        name="Rumble Fast",
        description="Description",
        default=0,
        min=0,
        max=100
    )
    
    def draw(self, context, layout):
        scene = context.scene
        
        layout.prop(self, "name")
        layout.prop(self, "dust")
        layout.prop(self, "grip_front")
        layout.prop(self, "grip_rear")
        layout.prop(self, "brake")
        layout.prop(self, "slip_mode")
        layout.prop(self, "skidmark_type_black")
        layout.prop(self, "skidmark_type_colored")
        layout.prop(self, "sound")
        layout.prop(self, "collision_options")
        layout.prop(self, "collision_sound_type")
        layout.prop(self, "enable_shadow")
        layout.prop(self, "enable_render")
        layout.prop(self, "emitter")
        layout.prop(self, "rumble_slow")
        layout.prop(self, "rumble_fast")
        
        # # Create a row to display the label and property side by side
        # row = layout.row()

        # # Add a label and an IntProperty with limited width
        # row.prop(self, "dust", text="Dust")
        
        # split = row.split(factor=0.3)
        # split.label(text="Dust")
        # split.prop(self, "dust")
    
class MY_OT_AddTexturePropertyGroup(bpy.types.Operator):
    bl_idname = "qad_texture_property_group_list.add_item"
    bl_label = "Add Texture Property Group"
    bl_description = "Add a new item"
    
    def execute(self, context):
        item = context.scene.qad_texture_property_group_list.add()
        item.name = f"Texture Property Group {len(context.scene.qad_texture_property_group_list)}"
        return {'FINISHED'}

class MY_OT_RemoveTexturePropertyGroup(bpy.types.Operator):
    bl_idname = "qad_texture_property_group_list.remove_item"
    bl_label = "Remove Texture Property Group"
    bl_description = "Remove the selected texture property group"
    
    index: bpy.props.IntProperty()
    
    def execute(self, context):
        if 0 <= self.index < len(context.scene.qad_texture_property_group_list):
            context.scene.qad_texture_property_group_list.remove(self.index)
        return {'FINISHED'}

class MY_UL_TexturePropertyGroupList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "name", text="", emboss=False, icon='OBJECT_DATA')
        
class MY_PT_TexturePropertyGroupPanel(bpy.types.Panel):
    bl_label = "QAD Texture Property Groups"
    bl_idname = "MY_PT_TexturePropertyGroupPanel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        row = layout.row()
        row.template_list(
            "MY_UL_TexturePropertyGroupList",
            "",  # ID for active list items (unused here)
            scene, "qad_texture_property_group_list",  # The CollectionProperty
            scene, "qad_texture_property_group_list_index",  # The active index
        )
        
        col = row.column(align=True)
        col.operator("qad_texture_property_group_list.add_item", icon="ADD", text="")
        col.operator("qad_texture_property_group_list.remove_item", icon="REMOVE", text="").index = scene.qad_texture_property_group_list_index
        
        if 0 <= scene.qad_texture_property_group_list_index < len(scene.qad_texture_property_group_list):
            item = scene.qad_texture_property_group_list[scene.qad_texture_property_group_list_index]
            item.draw(context, layout)
    
classes = [
    QadTexturePropertyGroupProperties,
    MY_OT_AddTexturePropertyGroup,
    MY_OT_RemoveTexturePropertyGroup,
    MY_PT_TexturePropertyGroupPanel,
    MY_UL_TexturePropertyGroupList,
    OBJECT_OT_TexturePropertyGroupAction,
    OBJECT_PT_TexturePropertyGroupActionPanel
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.qad_texture_property_group_list = bpy.props.CollectionProperty(type=QadTexturePropertyGroupProperties)
    bpy.types.Scene.qad_texture_property_group_list_index = bpy.props.IntProperty()

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    del bpy.types.Scene.qad_texture_property_group_list
    del bpy.types.Scene.qad_texture_property_group_list_index