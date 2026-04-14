import bpy
import math

from .MoxMaterials import *

from mathutils import Vector

material_matclass_enum = [
	(MaterialClass.Default.name, 'Default', 'Description'),
]

material_sub_type_enum = [
	(MaterialSubType.NoTexture.name, 'NoTexture', 'Description'),
	(MaterialSubType.Textured.name, 'Textured', 'Description'),
	(MaterialSubType.TexturedSpec.name, 'TexturedSpec', 'Description'),
	(MaterialSubType.Overlay.name, 'Overlay', 'Description'),
	(MaterialSubType.OverlaySpec.name, 'OverlaySpec', 'Description'),
	(MaterialSubType.OverlayMul.name, 'OverlayMul', 'Description'),
	(MaterialSubType.ParallaxRL.name, 'ParallaxRL', 'Description')
]

material_alpha_type_enum = [
	(MaterialAlphaType.Disabled.name, 'Disabled', 'Description'),
	(MaterialAlphaType.Normal.name, 'Normal', 'Description'),
	(MaterialAlphaType.Premul.name, 'Premul', 'Description'),
	(MaterialAlphaType.Additive.name, 'Additive', 'Description'),
	(MaterialAlphaType.ColorKey.name, 'ColorKey', 'Description'),
]

texture_tiling_enum = [
	(TextureTiling.Clip.name, 'Clip', 'Description'),
	(TextureTiling.Wrap.name, 'Wrap', 'Description'),
	(TextureTiling.Mirror.name, 'Mirror', 'Description'),
]

class MoxMaterialColorPropertyGroup(bpy.types.PropertyGroup):
    diffuse: bpy.props.FloatVectorProperty(
        name="Diffuse",
        subtype='COLOR',
        size=3,
        default=(0.588235, 0.588235, 0.588235),
        min=0.0, max=1.0,
    )
    ambient: bpy.props.FloatVectorProperty(
        name="Glow",
        subtype='COLOR',
        size=3,
        default=(0.0, 0.0, 0.0),
        min=0.0, max=1.0,
    )
    specular: bpy.props.FloatVectorProperty(
        name="Specular1",
        subtype='COLOR',
        size=3,
        default=(0.0, 0.0, 0.0),
        min=0.0, max=1.0,
    )
    reflect2: bpy.props.FloatVectorProperty(
        name="Reflect2",
        subtype='COLOR',
        size=3,
        default=(0.0, 0.0, 0.0),
        min=0.0, max=1.0,
    )
    specular2: bpy.props.FloatVectorProperty(
        name="Specular2",
        subtype='COLOR',
        size=3,
        default=(0.0, 0.0, 0.0),
        min=0.0, max=1.0,
    )
    xdiffuse: bpy.props.FloatVectorProperty(
        name="XDiffuse",
        subtype='COLOR',
        size=3,
        default=(0.0, 0.0, 0.0),
        min=0.0, max=1.0,
    )
    xspecular: bpy.props.FloatVectorProperty(
        name="XSpecular",
        subtype='COLOR',
        size=3,
        default=(0.0, 0.0, 0.0),
        min=0.0, max=1.0,
    )
    
    def draw(self, context, layout):
        layout.prop(self, "diffuse")
        layout.prop(self, "specular2")
        layout.prop(self, "specular")
        layout.prop(self, "ambient")
        layout.prop(self, "xdiffuse")
        layout.prop(self, "xspecular")
        layout.prop(self, "reflect2")

class MoxMaterialProperties(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(name="_Enabled")
    
    # 0 = Mat-Class, 1 = SubType, 2 = AlphaType, 3 = Abhaengigkeit
    
    matclass: bpy.props.EnumProperty(
        name="Class",
        description="Description",
        items=material_matclass_enum,
        default=MaterialClass.Default.value,
        #update=update_matclass
    )
    sub_type: bpy.props.EnumProperty(
        name="Subtype",
        description="Description",
        items=material_sub_type_enum,
        default=MaterialSubType.NoTexture.value,
        #update=update_subtype
    )
    alpha_type: bpy.props.EnumProperty(
        name="Alpha Type",
        description="Description",
        items=material_alpha_type_enum,
        default=MaterialAlphaType.Disabled.value,
        #update=update_alpha_type
    )
    matflag_preset: bpy.props.BoolProperty(
        name="Preset",
        description="Description",
        default=False
    )
    matflag_standard: bpy.props.BoolProperty(
        name="Standard",
        description="Description",
        default=False
    )
    matflag_dirt: bpy.props.BoolProperty(
        name="Dirt",
        description="Description",
        default=True
    )
    matflag_chrome: bpy.props.BoolProperty(
        name="Chrome",
        description="Description",
        default=False
    )
    
    color_properties: bpy.props.CollectionProperty(type=MoxMaterialColorPropertyGroup)
    
    texture_1: bpy.props.PointerProperty(
        name="Diffuse Map",
        type=bpy.types.Texture,
        description="Description",
        #update=update_texture_1
    )
    texture_2: bpy.props.PointerProperty(
        name="Normal Map",
        type=bpy.types.Texture,
        description="Description",
        #update=update_texture_2
    )
    texture_3: bpy.props.PointerProperty(
        name="Extra",
        type=bpy.types.Texture,
        description="Description",
        #update=update_texture_3
    )
    
    texture_tiling_u: bpy.props.EnumProperty(
        name="Texture Tiling U",
        description="Description",
        items=texture_tiling_enum,
        default=TextureTiling.Wrap.value,
        #update=update_texture_tiling
    )
    texture_tiling_v: bpy.props.EnumProperty(
        name="Texture Tiling V",
        description="Description",
        items=texture_tiling_enum,
        default=TextureTiling.Wrap.value,
        #update=update_texture_tiling
    )
    
    texture_offset: bpy.props.FloatVectorProperty(
        name='Texture Offset', 
        description="Description",
        size=2,
        default=(0.0, 0.0),
        subtype='XYZ',
        #update=update_tex_mod
    )
    texture_scale: bpy.props.FloatVectorProperty(
        name='Texture Scale', 
        description="Description",
        size=2,
        default=(1.0, 1.0),
        subtype='XYZ',
        #update=update_tex_mod
    )
    texture_angle: bpy.props.FloatProperty(name="Texture Angle", default=0.0)
    
    alpha: bpy.props.IntProperty(
        name="Alpha",
        description="Description",
        default=0,
        min=0,
        max=100
    )
    
    spec_sharp_1: bpy.props.IntProperty(
        name="Sharp1",
        description="Description",
        default=0,
        min=0,
        max=200
    )
    spec_size_1: bpy.props.IntProperty(
        name="Size1",
        description="Description",
        default=0,
        min=0,
        max=100
    )
    spec_sharp_2: bpy.props.IntProperty(
        name="Sharp2",
        description="Description",
        default=0,
        min=0,
        max=200
    )
    
    fresnel_intensity: bpy.props.IntProperty(
        name="Intensity",
        description="Description",
        default=0,
        min=0,
        max=100
    )
    fresnel_curve: bpy.props.IntProperty(
        name="Curve",
        description="Description",
        default=0,
        min=0,
        max=50
    )
    fresnel_level: bpy.props.IntProperty(
        name="Level",
        description="Description",
        default=0,
        min=0,
        max=100
    )
    
    falloff_intensity: bpy.props.IntProperty(
        name="Intensity",
        description="Description",
        default=0,
        min=0,
        max=100
    )
    falloff_curve: bpy.props.IntProperty(
        name="Curve",
        description="Description",
        default=0,
        min=0,
        max=50
    )
    
    def draw(self, context, layout):
        scene = context.scene
        
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        layout.prop(scene, "mox_material_color_list_preview_enum")
        
        layout.prop(self, "matclass")
        layout.prop(self, "sub_type")
        layout.prop(self, "alpha_type")
        
        col = layout.column()
        row = col.row()
        row.prop(self, "matflag_preset")
        row.prop(self, "matflag_standard")
        row.prop(self, "matflag_dirt")
        #row.prop(self, "matflag_chrome")
        
        box = layout.box()
        col = box.column()
        row = col.row()
        row.prop(scene, "mox_material_show_color_group",
            icon="TRIA_DOWN" if scene.mox_material_show_color_group else "TRIA_RIGHT",
            emboss=False
        )
        if scene.mox_material_show_color_group:
            col.separator(factor=0.5)
            #col = box.column(align=True)
            
            color_index = int(scene.mox_material_color_list_preview_enum)
        
            if 0 <= color_index < len(self.color_properties):
                self.color_properties[color_index].draw(context, col)
        
        box = layout.box()
        col = box.column()
        row = col.row()
        row.prop(scene, "mox_material_show_texture_group",
            icon="TRIA_DOWN" if scene.mox_material_show_texture_group else "TRIA_RIGHT",
            emboss=False
        )
        if scene.mox_material_show_texture_group:
            col.separator(factor=0.5)
            #col = box.column(align=True)
            col.prop(self, "texture_1")
            col.prop(self, "texture_2")
            col.prop(self, "texture_3")
            col.prop(self, "texture_tiling_u")
            col.prop(self, "texture_tiling_v")
            col.prop(self, "texture_offset")
            col.prop(self, "texture_scale")
            col.prop(self, "texture_angle")
        
        box = layout.box()
        col = box.column()
        row = col.row()
        row.prop(scene, "mox_material_show_falloff_group",
            icon="TRIA_DOWN" if scene.mox_material_show_falloff_group else "TRIA_RIGHT",
            emboss=False
        )
        if scene.mox_material_show_falloff_group:
            col.separator(factor=0.5)
            #col = box.column(align=True)
            col.prop(self, "falloff_intensity")
            col.prop(self, "falloff_curve")
        


        box = layout.box()
        col = box.column()
        row = col.row()
        row.prop(scene, "mox_material_show_fresnel_group",
            icon="TRIA_DOWN" if scene.mox_material_show_fresnel_group else "TRIA_RIGHT",
            emboss=False
        )
        if scene.mox_material_show_fresnel_group:
            col.separator(factor=0.5)
            #col = box.column(align=True)
            col.prop(self, "fresnel_intensity")
            col.prop(self, "fresnel_curve")
            col.prop(self, "fresnel_level")
        


        box = layout.box()
        col = box.column()
        row = col.row()
        row.prop(scene, "mox_material_show_spec_group",
            icon="TRIA_DOWN" if scene.mox_material_show_spec_group else "TRIA_RIGHT",
            emboss=False
        )
        if scene.mox_material_show_spec_group:
            col.separator(factor=0.5)
            #col = box.column(align=True)
            col.prop(self, "spec_sharp_1")
            col.prop(self, "spec_size_1")
            col.prop(self, "spec_sharp_2")
        


        box = layout.box()
        col = box.column()
        row = col.row()
        row.prop(scene, "mox_material_show_alpha_group",
            icon="TRIA_DOWN" if scene.mox_material_show_alpha_group else "TRIA_RIGHT",
            emboss=False
        )
        if scene.mox_material_show_alpha_group:
            col.separator(factor=0.5)
            #col = box.column(align=True)
            col.prop(self, "alpha")
    
class OBJECT_PT_mox_material(bpy.types.Panel):
    bl_label = "MOX"
    bl_idname = "OBJECT_PT_mox_material"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    def draw(self, context):
        layout = self.layout
        material = context.material
        
        if material:
            if hasattr(material, "mox_material_properties"):
                material.mox_material_properties.draw(context, layout)
                
@bpy.app.handlers.persistent
def on_load_post(filepath):
    scene = bpy.context.scene
    
    for obj in scene.objects:
        if obj.type == 'MESH':
            for mat_slot in obj.material_slots:
                mat = mat_slot.material
                if mat is None:
                    continue
                if not hasattr(mat, "mox_material_properties"):
                    continue
                color_props = mat.mox_material_properties.color_properties
                if len(color_props) != len(scene.mox_material_color_list):
                    color_props.clear()
                    for _ in scene.mox_material_color_list:
                        color_props.add()
                
def register():
    bpy.types.Scene.mox_material_show_color_group = bpy.props.BoolProperty(name="Colors", default=True)
    bpy.types.Scene.mox_material_show_texture_group = bpy.props.BoolProperty(name="Textures", default=True)
    bpy.types.Scene.mox_material_show_alpha_group = bpy.props.BoolProperty(name="Transparency", default=True)
    bpy.types.Scene.mox_material_show_spec_group = bpy.props.BoolProperty(name="Speculars", default=True)
    bpy.types.Scene.mox_material_show_fresnel_group = bpy.props.BoolProperty(name="Fresnel reflection", default=True)
    bpy.types.Scene.mox_material_show_falloff_group = bpy.props.BoolProperty(name="Diffuse shading falloff", default=True)
    bpy.utils.register_class(MoxMaterialColorPropertyGroup)
    bpy.utils.register_class(MoxMaterialProperties)
    bpy.types.Material.mox_material_properties = bpy.props.PointerProperty(type=MoxMaterialProperties)
    bpy.utils.register_class(OBJECT_PT_mox_material)
    bpy.app.handlers.load_post.append(on_load_post)
    
def unregister():
    del bpy.types.Scene.mox_material_show_color_group
    del bpy.types.Scene.mox_material_show_texture_group
    del bpy.types.Scene.mox_material_show_alpha_group
    del bpy.types.Scene.mox_material_show_spec_group
    del bpy.types.Scene.mox_material_show_fresnel_group
    del bpy.types.Scene.mox_material_show_falloff_group
    bpy.utils.unregister_class(MoxMaterialColorPropertyGroup)
    bpy.utils.unregister_class(MoxMaterialProperties)
    del bpy.types.Material.mox_material_properties
    bpy.utils.unregister_class(OBJECT_PT_mox_material)
    bpy.app.handlers.load_post.remove(on_load_post)