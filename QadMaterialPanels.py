import bpy
import math
import os

from .QadMaterials import *

from mathutils import Vector

material_type_enum = [
	(MaterialType.mat_4L_diff_L_1234.name, '00 4L diff L 1,2,3,4', 'Description'),
	(MaterialType.mat_1L_diff.name, '01 1L diff', 'Description'),
	(MaterialType.mat_1L_refl.name, '02 1L refl', 'Description'),
	(MaterialType.mat_1L_metal.name, '03 1L metal', 'Description'),
	(MaterialType.mat_1L_spec.name, '04 1L spec', 'Description'),
	(MaterialType.mat_1L_diff_illum.name, '05 1L diff illum', 'Description'),
	(MaterialType.mat_2L_diff_diff_L_12.name, '06 2L diff diff L 1,2', 'Description'),
	(MaterialType.mat_2L_diff_diff_L_13.name, '07 2L diff diff L 1,3', 'Description'),
	(MaterialType.mat_2L_refl_diff_L_12.name, '08 2L refl diff L 1,2', 'Description'),
	(MaterialType.mat_2L_refl_diff_L_13.name, '09 2L refl diff L 1,3', 'Description'),
	(MaterialType.mat_2L_metal_diff_L_12.name, '10 2L metal diff L 1,2', 'Description'),
	(MaterialType.mat_2L_spec_spec_L_12.name, '11 2L spec spec L 1,2', 'Description'),
	(MaterialType.mat_2L_spec_diff_L_13.name, '12 2L spec diff L 1,3', 'Description'),
	(MaterialType.mat_2L_refl_diff_win_L_12.name, '13 2L refl diff win L 1,2', 'Description'),
	(MaterialType.mat_3L_diff_diff_diff.name, '14 3L diff diff diff', 'Description'),
	(MaterialType.mat_3L_refl_diff_diff.name, '15 3L refl diff diff', 'Description'),
	(MaterialType.mat_3L_refl_refl_diff.name, '16 3L refl refl diff', 'Description'),
	(MaterialType.mat_3L_spec_spec_diff.name, '17 3L spec spec diff', 'Description'),
	(MaterialType.mat_3L_spec_diff_diff.name, '18 3L spec diff diff', 'Description'),
	(MaterialType.mat_2L_diff_diff_L_12_ColKey_L_1.name, '19 2L diff diff L 1,2 ColKey L 1', 'Description'),
	(MaterialType.mat_2L_refl_diff_L_12_ColKey_L_12.name, '20 2L refl diff L 1,2 ColKey L 1,2', 'Description'),
	(MaterialType.mat_2L_Water.name, '21 2L Water', 'Description'),
	(MaterialType.mat_1L_diff_Decal_and_spec_mask.name, '22 1L diff Decal + spec mask', 'Description'),
	(MaterialType.mat_1L_diff_Decal_and_win_mask.name, '23 1L diff Decal + win mask', 'Description'),
	(MaterialType.mat_1L_refl_Decal_and_spec_mask.name, '24 1L refl Decal + spec mask', 'Description'),
	(MaterialType.mat_1L_refl_Decal_and_win_mask.name, '25 1L refl Decal + win mask', 'Description'),
	(MaterialType.mat_1L_diff_Decal_and_illum_mask.name, '26 1L diff Decal + illum mask', 'Description'),
	(MaterialType.mat_1L_refl_Decal_and_illum_mask.name, '27 1L refl Decal + illum mask', 'Description')
]

class ShaderNodeItem:
    def __init__(self):
        self.texture_index = 0
        self.texture_node = None
        self.bump_texture_node = None
        self.normal_node = None
        self.uv_map_node = None
        self.mapping_node = None
        
def find_material(material_property_group):
    for mat in bpy.data.materials:
        if not hasattr(mat, "qad_material_properties"):
            continue
        if mat.qad_material_properties == material_property_group:
            return mat
    return None

def build_default_shader(self, material, shader_node_items, bsdf_node, uv_layer_names):
    node_tree = material.node_tree
    
    shader_node_item : ShaderNodeItem = shader_node_items[0]

    tex_node = shader_node_item.texture_node
    normal_node = shader_node_item.normal_node

    node_tree.links.new(tex_node.outputs['Color'], bsdf_node.inputs['Base Color'])
    node_tree.links.new(normal_node.outputs['Normal'], bsdf_node.inputs['Normal'])

def build_shader_for_type_0(self, material, shader_node_items, bsdf_node, uv_layer_names):
    node_tree = material.node_tree
        
    qad_material_properties : QadMaterialProperties = material.qad_material_properties

    shader_node_item_1 : ShaderNodeItem = shader_node_items[0]
    shader_node_item_2 : ShaderNodeItem = shader_node_items[1]
    shader_node_item_3 : ShaderNodeItem = shader_node_items[2]

    texture_node_1 = shader_node_item_1.texture_node
    texture_node_2 = shader_node_item_2.texture_node
    texture_node_3 = shader_node_item_3.texture_node
    
    normal_node_1 = shader_node_item_1.normal_node
    normal_node_2 = shader_node_item_2.normal_node
    normal_node_3 = shader_node_item_3.normal_node
    
    uv_map_node_1 = shader_node_item_1.uv_map_node
    uv_map_node_2 = shader_node_item_2.uv_map_node
    uv_map_node_3 = shader_node_item_3.uv_map_node
    
    mapping_node_1 = shader_node_item_1.mapping_node
    mapping_node_2 = shader_node_item_2.mapping_node
    mapping_node_3 = shader_node_item_3.mapping_node
    
    uv_map_nodes = [uv_map_node_1, uv_map_node_2, uv_map_node_3]
    mapping_nodes = [mapping_node_1, mapping_node_2, mapping_node_3]
    
    uv_layer_per_texture = {
        0: 0,
        1: 0,
        2: 1
    }
    
    mix_vertex_color = node_tree.nodes.new(type='ShaderNodeVertexColor')
    #mix_vertex_color.location = (-1500, -500 * j)
    mix_vertex_color.layer_name = "Color"
    
    separate_vertex_color = node_tree.nodes.new(type='ShaderNodeSeparateRGB')
    #separate_vertex_color.location = (-1500, -500 * j)
    
    mix_node_1 = node_tree.nodes.new(type='ShaderNodeMixRGB')
    #mix_node_1.location = (-1500, -500 * j)
    mix_node_1.use_clamp = True
    
    mix_node_2 = node_tree.nodes.new(type='ShaderNodeMixRGB')
    #mix_node_2.location = (-1500, -500 * j)
    mix_node_2.use_clamp = True
    
    mix_node_bump_1 = node_tree.nodes.new(type='ShaderNodeMixRGB')
    #mix_node_bump_1.location = (-1500, -500 * j)
    mix_node_bump_1.use_clamp = True
    
    mix_node_bump_2 = node_tree.nodes.new(type='ShaderNodeMixRGB')
    #mix_node_bump_2.location = (-1500, -500 * j)
    mix_node_bump_2.use_clamp = True
    
    node_tree.links.new(mix_vertex_color.outputs['Color'], separate_vertex_color.inputs['Image'])
    
    # color
    node_tree.links.new(mix_vertex_color.outputs['Alpha'], mix_node_1.inputs['Fac'])
    node_tree.links.new(texture_node_1.outputs['Color'], mix_node_1.inputs['Color1'])
    node_tree.links.new(texture_node_2.outputs['Color'], mix_node_1.inputs['Color2'])
    
    node_tree.links.new(separate_vertex_color.outputs['B'], mix_node_2.inputs['Fac'])
    node_tree.links.new(mix_node_1.outputs['Color'], mix_node_2.inputs['Color1'])
    node_tree.links.new(texture_node_3.outputs['Color'], mix_node_2.inputs['Color2'])
    
    node_tree.links.new(mix_node_2.outputs['Color'], bsdf_node.inputs['Base Color'])
    
    # bump
    node_tree.links.new(mix_vertex_color.outputs['Alpha'], mix_node_bump_1.inputs['Fac'])
    node_tree.links.new(normal_node_1.outputs['Normal'], mix_node_bump_1.inputs['Color1'])
    node_tree.links.new(normal_node_2.outputs['Normal'], mix_node_bump_1.inputs['Color2'])
    
    node_tree.links.new(separate_vertex_color.outputs['B'], mix_node_bump_2.inputs['Fac'])
    node_tree.links.new(mix_node_bump_1.outputs['Color'], mix_node_bump_2.inputs['Color1'])
    node_tree.links.new(normal_node_3.outputs['Normal'], mix_node_bump_2.inputs['Color2'])
    
    node_tree.links.new(mix_node_bump_2.outputs['Color'], bsdf_node.inputs['Normal'])
    
    bsdf_node.inputs["Roughness"].default_value = 1.0

    # TODO
    for texture_index, uv_layer_index in uv_layer_per_texture.items():
        uv_map_node = uv_map_nodes[texture_index]
        mapping_node = mapping_nodes[texture_index]
        
        if uv_layer_names:
            uv_map_node.uv_map = uv_layer_names[uv_layer_index]
        
        # [0] = textures[0].offset.x
        # [1] = textures[0].offset.y
        # [2] = textures[0].scale.x
        # [3] = textures[0].scale.x
            
        scale_factor = 10.0

        if uv_layer_index == 1:
            texture_offset = (qad_material_properties.texture_2_offset.x, qad_material_properties.texture_2_offset.y, 0.0)
            texture_scale = (qad_material_properties.texture_2_scale.x, qad_material_properties.texture_2_scale.y, 0.0)
        else:
            texture_offset = (qad_material_properties.texture_1_offset.x, qad_material_properties.texture_1_offset.y, 0.0)
            texture_scale = (qad_material_properties.texture_1_scale.x, qad_material_properties.texture_1_scale.y, 0.0)

        #mapping_node.inputs['Location'].default_value = Vector(texture_offset)
        #mapping_node.inputs['Scale'].default_value = Vector(texture_scale)
        
def build_shader_for_type(self, material, shader_node_items, bsdf_node, uv_layer_names):
    material_type_name = self.type
    material_type = MaterialType[material_type_name].value
    
    if material_type == 0: # mat_4L_diff_L_1234
        build_shader_for_type_0(self, material, shader_node_items, bsdf_node, uv_layer_names)
    else:
        build_default_shader(self, material, shader_node_items, bsdf_node, uv_layer_names)

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
    
    textures = [self.texture_1, self.texture_2, self.texture_3, self.texture_4]
    bump_textures = [self.bump_texture_1, self.bump_texture_2, self.bump_texture_3]
    all_textures = textures + bump_textures
    
    shader_node_items = [ShaderNodeItem() for _ in range(len(textures))]

    for j in range(len(all_textures)):
        image = all_textures[j]
        
        is_bump = (j + 1) > len(textures)
        
        texture_slot_index = 0
        node_name = ""
        node_label = ""

        if is_bump:
            texture_slot_index = j - len(textures)
            node_name = f"bump_texture_{texture_slot_index + 1}"
            node_label = f"Bump Texture {texture_slot_index + 1}"
        else:
            texture_slot_index = j
            node_name = f"texture_{texture_slot_index + 1}"
            node_label = f"Texture {texture_slot_index + 1}"
            
        shader_node_item : ShaderNodeItem = shader_node_items[texture_slot_index]
        shader_node_item.texture_index = texture_slot_index
        
        tex_node = node_tree.nodes.new('ShaderNodeTexImage')
        tex_node.location = (-1000, -500 * j)
        tex_node.image = image
        tex_node.name = node_name
        tex_node.label = node_label
            
        if is_bump:
            normal_node = node_tree.nodes.new('ShaderNodeNormalMap')
            normal_node.location = (-500, -500 * j)
            
            shader_node_item.bump_texture_node = tex_node
            shader_node_item.normal_node = normal_node
                    
            if tex_node.image:
                node_tree.links.new(tex_node.outputs['Color'], normal_node.inputs['Color'])
        else:
            shader_node_item.texture_node = tex_node
            
        if not shader_node_item.mapping_node:
            uv_map_node = node_tree.nodes.new('ShaderNodeUVMap')
            uv_map_node.location = (-2000, -500 * j)
            
            if uv_layer_names:
                uv_map_node.uv_map = uv_layer_names[0]
                    
            mapping_node = node_tree.nodes.new(type='ShaderNodeMapping')
            mapping_node.location = (-1500, -500 * j)
            
            node_tree.links.new(uv_map_node.outputs['UV'], mapping_node.inputs['Vector'])
            
            shader_node_item.uv_map_node = uv_map_node
            shader_node_item.mapping_node = mapping_node
                    
        node_tree.links.new(shader_node_item.mapping_node.outputs['Vector'], tex_node.inputs['Vector'])
            
    build_shader_for_type(self, material, shader_node_items, bsdf_node, uv_layer_names)
        
    for obj in bpy.context.scene.objects:
        if obj.active_material == material:
            obj.update_tag(refresh={'DATA'})
           
def update_shader(self, material):
    print(f"update_shader()")
    
    node_tree = material.node_tree
    
    material_type = self.type
    print(f"update_shader() material_type = {material_type}")
    
    # ...
    
    textures = [self.texture_1, self.texture_2, self.texture_3, self.texture_4]
    bump_textures = [self.bump_texture_1, self.bump_texture_2, self.bump_texture_3]
    all_textures = textures + bump_textures
    
    for j in range(len(all_textures)):
        texture = all_textures[j]
        
        is_bump = (j + 1) > len(textures)
        
        image = None
        texture_slot_index = 0
        node_name = ""

        if texture:
            image = texture.image
            
        if is_bump:
            texture_slot_index = j - len(textures)
            node_name = f"bump_texture_{texture_slot_index + 1}"
        else:
            texture_slot_index = j
            node_name = f"texture_{texture_slot_index + 1}"
            
        tex_node = node_tree.nodes.get(node_name)
        tex_node.image = image
                    
    for obj in bpy.context.scene.objects:
        if obj.active_material == material:
            obj.update_tag(refresh={'DATA'})
    
def update(self, context):
    obj = context.object
    material = find_material(self)

    if not material:
        return
    
    uv_layer_names = None

    if obj and obj.type == 'MESH':
        uv_layer_names = [uv.name for uv in obj.data.uv_layers[:2]]
    
    build_shader(self, material, uv_layer_names)
    
def update_type(self, context):
    update(self, context)
    
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
    
def update_texture_4(self, context):
    update_texture(self, context, "texture_4")
    
def update_bump_texture_1(self, context):
    update_texture(self, context, "bump_texture_1")
    
def update_bump_texture_2(self, context):
    update_texture(self, context, "bump_texture_2")
    
def update_bump_texture_3(self, context):
    update_texture(self, context, "bump_texture_3")
    
def update_tex_mod(self, context):
    update(self, context)

class QadMaterialProperties(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(name="_Enabled")
    
    type: bpy.props.EnumProperty(
        name="Type",
        description="Description",
        items=material_type_enum,
        default=MaterialType.mat_1L_diff.value,
        update=update_type
    )
    
    texture_1: bpy.props.PointerProperty(
        name="Texture 1",
        type=bpy.types.Image,
        description="Description",
        update=update_texture_1
    )
    texture_2: bpy.props.PointerProperty(
        name="Texture 2",
        type=bpy.types.Image,
        description="Description",
        update=update_texture_2
    )
    texture_3: bpy.props.PointerProperty(
        name="Texture 3",
        type=bpy.types.Image,
        description="Description",
        update=update_texture_3
    )
    texture_4: bpy.props.PointerProperty(
        name="Texture 4",
        type=bpy.types.Image,
        description="Description",
        update=update_texture_4
    )
    
    bump_texture_1: bpy.props.PointerProperty(
        name="Bump Texture 1",
        type=bpy.types.Image,
        description="Description",
        update=update_bump_texture_1
    )
    bump_texture_2: bpy.props.PointerProperty(
        name="Bump Texture 2",
        type=bpy.types.Image,
        description="Description",
        update=update_bump_texture_2
    )
    bump_texture_3: bpy.props.PointerProperty(
        name="Bump Texture 3",
        type=bpy.types.Image,
        description="Description",
        update=update_bump_texture_3
    )
    
    texture_1_offset: bpy.props.FloatVectorProperty(
        name='Offset', 
        description="Description",
        size=2,
        default=(0.0, 0.0),
        subtype='XYZ',
        update=update_tex_mod)
    
    texture_1_scale: bpy.props.FloatVectorProperty(
        name='Scale', 
        description="Inverse texture scale",
        size=2,
        default=(1.0, 1.0),
        subtype='XYZ',
        update=update_tex_mod)
    
    texture_2_offset: bpy.props.FloatVectorProperty(
        name='Offset', 
        description="Description",
        size=2,
        default=(0.0, 0.0),
        subtype='XYZ',
        update=update_tex_mod)
    
    texture_2_scale: bpy.props.FloatVectorProperty(
        name='Scale', 
        description="Inverse texture scale",
        size=2,
        default=(1.0, 1.0),
        subtype='XYZ',
        update=update_tex_mod)

    def setup(self, material, uv_layer_names):
        build_shader(self, material, uv_layer_names)
        
    def draw(self, context, layout):
        layout.prop(self, "type")
        layout.prop(self, "texture_1")
        layout.prop(self, "texture_2")
        layout.prop(self, "texture_3")
        layout.prop(self, "texture_4")
        layout.prop(self, "bump_texture_1")
        layout.prop(self, "bump_texture_2")
        layout.prop(self, "bump_texture_3")
        layout.label(text="Texture 1")
        layout.prop(self, "texture_1_offset")
        layout.prop(self, "texture_1_scale")
        layout.label(text="Texture 2")
        layout.prop(self, "texture_2_offset")
        layout.prop(self, "texture_2_scale")
    
class LANDSCAPE_PT_qad_material(bpy.types.Panel):
    bl_label = "QAD"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    def draw(self, context):
        layout = self.layout
        material = context.material
        
        if material:
            if hasattr(material, "qad_material_properties"):
                material.qad_material_properties.draw(context, layout)
				  
def get_texture_node(material, input_name):
    if not material or not material.use_nodes:
        return
    
    if not input_name:
        return
        
    nodes = material.node_tree.nodes
        
    bsdf = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if not bsdf:
        return
        
    base_color_input = bsdf.inputs[input_name]
        
    if not base_color_input.is_linked:
        return
        
    linked_node = base_color_input.links[0].from_node
        
    if linked_node.type == 'TEX_IMAGE':
        return linked_node
        
    # Recursively search upstream for any TEX_IMAGE node
    def find_image_upstream(node, visited=None):
        if visited is None:
            visited = set()
        if node.name in visited:
            return None
        visited.add(node.name)
            
        if node.type == 'TEX_IMAGE':
            return node
            
        for inp in node.inputs:
            if inp.is_linked:
                upstream = inp.links[0].from_node
                result = find_image_upstream(upstream, visited)
                if result:
                    return result
        return None
        
    tex_node = find_image_upstream(linked_node)
    
    return tex_node

@bpy.app.handlers.persistent
def on_load_post(filepath):
    scene = bpy.context.scene
    
    for obj in scene.objects:
        if obj.type == 'MESH':
            for material_slot in obj.material_slots:
                material = material_slot.material
                
                if material is None:
                    continue
                
                if not hasattr(material, "qad_material_properties"):
                    continue
                
                qad_material_properties : QadMaterialProperties = material.qad_material_properties
                
                if qad_material_properties.texture_1:
                    continue
                
                tex_node = get_texture_node(material, "Base Color")

                if tex_node is None:
                    continue

                qad_material_properties.texture_1 = tex_node.image
                
def register():
    bpy.utils.register_class(QadMaterialProperties)
    bpy.types.Material.qad_material_properties = bpy.props.PointerProperty(type=QadMaterialProperties)
    bpy.utils.register_class(LANDSCAPE_PT_qad_material)
    bpy.app.handlers.load_post.append(on_load_post)
    
def unregister():
    del bpy.types.Material.qad_material_properties
    bpy.utils.unregister_class(QadMaterialProperties)
    bpy.utils.unregister_class(LANDSCAPE_PT_qad_material)
    bpy.app.handlers.load_post.remove(on_load_post)