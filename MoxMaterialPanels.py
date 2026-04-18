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

class ShaderNodeItem:
    def __init__(self):
        self.texture_nodes = [None, None, None]
        self.normal_node = None
        self.uv_map_node = None
        self.mapping_node = None
        
def find_material(material_property_group):
    for mat in bpy.data.materials:
        if not hasattr(mat, "mox_material_properties"):
            continue
        if mat.mox_material_properties == material_property_group:
            return mat
    return None

def build_default_shader(self, material, shader_node_item, bsdf_node, uv_layer_names):
    node_tree = material.node_tree
    
    if not bsdf_node:
        return
        
    #mox_material_properties : MoxMaterialProperties = material.mox_material_properties
    
    texture_1_node = shader_node_item.texture_nodes[0]
    texture_2_node = shader_node_item.texture_nodes[1]
    texture_2_node = shader_node_item.texture_nodes[2]
    normal_node = shader_node_item.normal_node
    
    if texture_1_node:
        node_tree.links.new(texture_1_node.outputs['Color'], bsdf_node.inputs['Base Color'])
        
    if normal_node:
        node_tree.links.new(normal_node.outputs['Normal'], bsdf_node.inputs['Normal'])
    
    color_index = int(bpy.context.scene.mox_material_color_list_preview_enum)
    
    node_diffuse = node_tree.nodes.get(f"diffuse:{color_index}")
    
    # Diffuse
    diffuse_mix_node = node_tree.nodes.new('ShaderNodeMix')
    diffuse_mix_node.blend_type = 'MULTIPLY'
    diffuse_mix_node.data_type = 'RGBA'
    diffuse_mix_node.inputs['Factor'].default_value = 1.0
    
    # TODO: sign operation is not suitable to detect missing textures
    diffuse_sign_math_node = node_tree.nodes.new('ShaderNodeMath')
    diffuse_sign_math_node.operation = 'SIGN'
    diffuse_sign_math_node.use_clamp = True
    
    if texture_1_node:
        node_tree.links.new(texture_1_node.outputs['Color'], diffuse_sign_math_node.inputs[0])
        
    node_tree.links.new(diffuse_sign_math_node.outputs['Value'], diffuse_mix_node.inputs['Factor'])

    if node_diffuse:
        node_tree.links.new(node_diffuse.outputs['Color'], diffuse_mix_node.inputs['A'])
        
    if texture_1_node:
        node_tree.links.new(texture_1_node.outputs['Color'], diffuse_mix_node.inputs['B'])
        
    node_tree.links.new(diffuse_mix_node.outputs['Result'], bsdf_node.inputs['Base Color'])
    
    # Specular2
    node_specular2 = node_tree.nodes.get(f"specular2:{color_index}")

    if node_specular2:
        node_tree.links.new(node_specular2.outputs['Color'], bsdf_node.inputs['Metallic'])
    
    # Reflect2
    node_reflect2 = node_tree.nodes.get(f"reflect2:{color_index}")

    reflect2_multiply_math_node = node_tree.nodes.new('ShaderNodeMath')
    reflect2_multiply_math_node.operation = 'MULTIPLY'
    
    node_tree.links.new(texture_1_node.outputs['Alpha'], reflect2_multiply_math_node.inputs[0])
    
    if node_reflect2:
        node_tree.links.new(node_reflect2.outputs['Color'], reflect2_multiply_math_node.inputs[1])
        
    node_tree.links.new(reflect2_multiply_math_node.outputs['Value'], bsdf_node.inputs['Roughness'])

def build_shader_for_type(self, material, shader_node_item, bsdf_node, uv_layer_names):
    material_sub_type = MaterialSubType[self.sub_type]
    
    if material_sub_type == MaterialSubType.NoTexture and False:
        build_shader_for_type_0(self, material, shader_node_item, bsdf_node, uv_layer_names)
    else:
        build_default_shader(self, material, shader_node_item, bsdf_node, uv_layer_names)

def build_shader(self, material, uv_layer_names):
    print(f"build_shader()")
    
    material.use_nodes = True
    material.use_backface_culling = True
               
    node_tree = material.node_tree
    node_tree.nodes.clear()
    
    bsdf_node = node_tree.nodes.new(type="ShaderNodeBsdfPrincipled")
    bsdf_node.location = (500, 0)
    
    output_node = node_tree.nodes.new(type="ShaderNodeOutputMaterial")
    output_node.location = (1000, 0)
    output_node.name = "output_custom"
    
    node_tree.links.new(bsdf_node.outputs["BSDF"], output_node.inputs["Surface"])
    
    color_property_keys = ['diffuse', 'ambient', 'specular', 'reflect2', 'specular2', 'xdiffuse', 'xspecular']
    color_property_groups = material.mox_material_properties.color_properties
    
    for color_property_index, color_property_key in enumerate(color_property_keys):
        for color_index, color_property_group in enumerate(color_property_groups):
            color_property = getattr(color_property_group, color_property_key)
        
            color_node = node_tree.nodes.new('ShaderNodeRGB')
            color_node.location = (-1000, (500 * len(color_property_keys) * len(color_property_groups)) - (500 * color_property_index * color_index))
            color_node.name = f"{color_property_key}:{color_index}"
            #color_node.label = color_property_key # ?
            color_node.outputs['Color'].default_value = (color_property[0], color_property[1], color_property[2], 1.0)

    textures = [self.texture_1, self.texture_2, self.texture_3]
    
    shader_node_item = ShaderNodeItem()

    for j in range(len(textures)):
        image = textures[j]
        
        texture_slot_index = j
        node_name = f"texture_{texture_slot_index + 1}"
        node_label = f"Texture {texture_slot_index + 1}"

        tex_node = node_tree.nodes.new('ShaderNodeTexImage')
        tex_node.location = (-1000, -500 * j)
        tex_node.image = image
        tex_node.name = node_name
        tex_node.label = node_label
            
        if j == 1:
            normal_node = node_tree.nodes.new('ShaderNodeNormalMap')
            normal_node.location = (-500, -500 * j)
            
            shader_node_item.normal_node = normal_node
                    
            if tex_node.image:
                node_tree.links.new(tex_node.outputs['Color'], normal_node.inputs['Color'])

        shader_node_item.texture_nodes[j] = tex_node
            
        if not shader_node_item.mapping_node:
            uv_map_node = node_tree.nodes.new('ShaderNodeUVMap')
            uv_map_node.location = (-2000, -500 * j)
            #uv_map_node.uv_map = uv_layer_names[0]
                    
            mapping_node = node_tree.nodes.new(type='ShaderNodeMapping')
            mapping_node.location = (-1500, -500 * j)
            
            node_tree.links.new(uv_map_node.outputs['UV'], mapping_node.inputs['Vector'])
            
            shader_node_item.uv_map_node = uv_map_node
            shader_node_item.mapping_node = mapping_node
                    
        node_tree.links.new(shader_node_item.mapping_node.outputs['Vector'], tex_node.inputs['Vector'])
            
    build_shader_for_type(self, material, shader_node_item, bsdf_node, uv_layer_names)
        
    for obj in bpy.context.scene.objects:
        if obj.active_material == material:
            obj.update_tag(refresh={'DATA'})
           
def update_shader(self, material):
    print(f"update_shader()")
    
    node_tree = material.node_tree
    
    material_sub_type = self.sub_type
    print(f"update_shader() material_sub_type = {material_sub_type}")
    
    # ...
    
    textures = [self.texture_1, self.texture_2, self.texture_3]
    
    for j in range(len(textures)):
        texture = textures[j]
        
        image = None
        node_name = f"texture_{j + 1}"

        if texture:
            image = texture.image
            
        tex_node = node_tree.nodes.get(node_name)
        tex_node.image = image
                    
    for obj in bpy.context.scene.objects:
        if obj.active_material == material:
            obj.update_tag(refresh={'DATA'})
    
def update(self, context):
    if not hasattr(context, 'material'):
        return
    
    obj = context.object
    material = find_material(self)
    
    uv_layer_names = None

    if obj and obj.type == 'MESH':
        uv_layer_names = [uv.name for uv in obj.data.uv_layers[:2]]
    
    build_shader(self, material, uv_layer_names)
    
def update_matclass(self, context):
    #update(self, context)
    pass
    
def update_sub_type(self, context):
    #update(self, context)
    pass
    
def update_alpha_type(self, context):
    #update(self, context)
    pass

def update_texture(self, context, prop_name):
    material = find_material(self)

    node_tree = material.node_tree
    
    if not node_tree.nodes.get("output_custom"):
        update(self, context)
        return
    
    image = getattr(self, prop_name)
    
    tex_node = node_tree.nodes.get(prop_name)
    
    if tex_node:
        tex_node.image = image
    
def update_texture_1(self, context):
    update_texture(self, context, "texture_1")
    
def update_texture_2(self, context):
    update_texture(self, context, "texture_2")
    
def update_texture_3(self, context):
    update_texture(self, context, "texture_3")
    
def update_texture_tiling(self, context):
    #update(self, context)
    pass
    
def update_texture_scale(self, context):
    #update(self, context)
    pass
    
def update_texture_offset(self, context):
    #update(self, context)
    pass
    
def update_texture_angle(self, context):
    #update(self, context)
    pass
    
def update_alpha(self, context):
    #update(self, context)
    pass
    
def update_color(self, context, prop_name):
    material = find_material(self)
    
    if not material:
        return
    
    node_tree = material.node_tree
    
    if not node_tree.nodes.get("output_custom"):
        update(self, context)
        return
    
    color_index = int(bpy.context.scene.mox_material_color_list_preview_enum)
        
    color_property = getattr(self, prop_name)
    
    if color_property:
        color_node = node_tree.nodes.get(f"{prop_name}:{color_index}")
        color_node.outputs['Color'].default_value = (color_property[0], color_property[1], color_property[2], 1.0)
    
def update_color_diffuse(self, context):
    update_color(self, context, "diffuse")
    
def update_color_ambient(self, context):
    update_color(self, context, "ambient")
    
def update_color_specular(self, context):
    update_color(self, context, "specular")
    
def update_color_reflect2(self, context):
    update_color(self, context, "reflect2")
    
def update_color_specular2(self, context):
    update_color(self, context, "specular2")
    
def update_color_xdiffuse(self, context):
    update_color(self, context, "xdiffuse")
    
def update_color_xspecular(self, context):
    update_color(self, context, "xspecular")
    
class MoxMaterialColorPropertyGroup(bpy.types.PropertyGroup):
    diffuse: bpy.props.FloatVectorProperty(
        name="Diffuse",
        subtype='COLOR',
        size=3,
        default=(0.588235, 0.588235, 0.588235),
        min=0.0, max=1.0,
        update=update_color_diffuse
    )
    ambient: bpy.props.FloatVectorProperty(
        name="Glow",
        subtype='COLOR',
        size=3,
        default=(0.0, 0.0, 0.0),
        min=0.0, max=1.0,
        update=update_color_ambient
    )
    specular: bpy.props.FloatVectorProperty(
        name="Specular1",
        subtype='COLOR',
        size=3,
        default=(0.0, 0.0, 0.0),
        min=0.0, max=1.0,
        update=update_color_specular
    )
    reflect2: bpy.props.FloatVectorProperty(
        name="Reflect2",
        subtype='COLOR',
        size=3,
        default=(0.588235, 0.588235, 0.588235),
        min=0.0, max=1.0,
        update=update_color_reflect2
    )
    specular2: bpy.props.FloatVectorProperty(
        name="Specular2",
        subtype='COLOR',
        size=3,
        default=(0.0, 0.0, 0.0),
        min=0.0, max=1.0,
        update=update_color_specular2
    )
    xdiffuse: bpy.props.FloatVectorProperty(
        name="XDiffuse",
        subtype='COLOR',
        size=3,
        default=(0.0, 0.0, 0.0),
        min=0.0, max=1.0,
        update=update_color_xdiffuse
    )
    xspecular: bpy.props.FloatVectorProperty(
        name="XSpecular",
        subtype='COLOR',
        size=3,
        default=(0.0, 0.0, 0.0),
        min=0.0, max=1.0,
        update=update_color_xspecular
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
        update=update_matclass
    )
    sub_type: bpy.props.EnumProperty(
        name="Subtype",
        description="Description",
        items=material_sub_type_enum,
        default=MaterialSubType.NoTexture.value,
        update=update_sub_type
    )
    alpha_type: bpy.props.EnumProperty(
        name="Alpha Type",
        description="Description",
        items=material_alpha_type_enum,
        default=MaterialAlphaType.Disabled.value,
        update=update_alpha_type
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
        type=bpy.types.Image,
        description="Description",
        update=update_texture_1
    )
    texture_2: bpy.props.PointerProperty(
        name="Normal Map",
        type=bpy.types.Image,
        description="Description",
        update=update_texture_2
    )
    texture_3: bpy.props.PointerProperty(
        name="Extra",
        type=bpy.types.Image,
        description="Description",
        update=update_texture_3
    )
    
    texture_tiling_u: bpy.props.EnumProperty(
        name="Texture Tiling U",
        description="Description",
        items=texture_tiling_enum,
        default=TextureTiling.Wrap.value,
        update=update_texture_tiling
    )
    texture_tiling_v: bpy.props.EnumProperty(
        name="Texture Tiling V",
        description="Description",
        items=texture_tiling_enum,
        default=TextureTiling.Wrap.value,
        update=update_texture_tiling
    )
    
    texture_offset: bpy.props.FloatVectorProperty(
        name='Texture Offset', 
        description="Description",
        size=2,
        default=(0.0, 0.0),
        subtype='XYZ',
        update=update_texture_offset
    )
    texture_scale: bpy.props.FloatVectorProperty(
        name='Texture Scale', 
        description="Description",
        size=2,
        default=(1.0, 1.0),
        subtype='XYZ',
        update=update_texture_scale
    )
    texture_angle: bpy.props.FloatProperty(
        name="Texture Angle",
        default=0.0,
        update=update_texture_angle
    )
    
    alpha: bpy.props.IntProperty(
        name="Alpha",
        description="Description",
        default=0,
        min=0,
        max=100,
        update=update_alpha
    )
    
    spec_sharp_1: bpy.props.IntProperty(
        name="Sharp1",
        description="Description",
        default=79,
        min=0,
        max=200
    )
    spec_size_1: bpy.props.IntProperty(
        name="Size1",
        description="Description",
        default=10,
        min=0,
        max=100
    )
    spec_sharp_2: bpy.props.IntProperty(
        name="Sharp2",
        description="Description",
        default=50,
        min=0,
        max=200
    )
    
    fresnel_intensity: bpy.props.IntProperty(
        name="Intensity",
        description="Description",
        default=97,
        min=0,
        max=100
    )
    fresnel_curve: bpy.props.IntProperty(
        name="Curve",
        description="Description",
        default=50,
        min=0,
        max=50
    )
    fresnel_level: bpy.props.IntProperty(
        name="Level",
        description="Description",
        default=80,
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
        default=30,
        min=00,
        max=50
    )
    
    def setup(self, material, uv_layer_names):
        build_shader(self, material, uv_layer_names)
    
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
    
class LANDSCAPE_PT_mox_material(bpy.types.Panel):
    bl_label = "MOX"
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
         
@bpy.app.handlers.persistent
def on_depsgraph_update_post(scene, depsgraph):
    for update in depsgraph.updates:
        if not isinstance(update.id, bpy.types.Material):
            continue

        mat = bpy.data.materials.get(update.id.name)

        if mat is None or not hasattr(mat, "mox_material_properties"):
            continue

        props = mat.mox_material_properties.color_properties
        expected = len(scene.mox_material_color_list)

        while len(props) < expected:
            props.add()
        while len(props) > expected:
            props.remove(len(props) - 1)
                
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
    bpy.utils.register_class(LANDSCAPE_PT_mox_material)
    bpy.app.handlers.depsgraph_update_post.append(on_depsgraph_update_post)
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
    bpy.utils.unregister_class(LANDSCAPE_PT_mox_material)
    bpy.app.handlers.depsgraph_update_post.remove(on_depsgraph_update_post)
    bpy.app.handlers.load_post.remove(on_load_post)