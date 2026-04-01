import array
import bpy
import struct
import bmesh
import math;
import numpy as np

from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from mathutils import Vector, Matrix, Quaternion

from pathlib import Path
from io import BufferedReader, BufferedWriter

from .utils import *

class PlgFile:
    def __init__(self):
        self.version = 0
        self.number_of_quads_x = 0
        self.number_of_quads_y = 0
        self.texture_names = []
        self.types = []
        self.collections = []
        self.source_textures = []
        self.vertices = []
        self.triangles = []
        self.chunks = []
        self.quads = []
        
    def deserialize(self, reader : BufferedReader):
        print("PlgFile.deserialize()")
        
        signature = struct.unpack('I', reader.read(4))[0]
        
        if signature != 0x506c476d:
            print("Invalid signature")
            pass
        
        version = struct.unpack('I', reader.read(4))[0]
        
        if version != 0x00010001:
            print("Unsupported version")
            pass
        
        read = struct.unpack('14I', reader.read(56))
        
        options = read[0]
        texture_file_pool_size = read[1]
        
        number_of_texture_names = read[2]
        number_of_types = read[3]
        number_of_collections = read[4]
        number_of_source_textures = read[5]
        number_of_vertices = read[6]
        number_of_triangles = read[7]
        number_of_chunks = read[8]
        self.number_of_quads_x = read[9]
        self.number_of_quads_y = read[10]
        number_of_quads = read[11]
        
        if True:
            print("number_of_quads:", number_of_quads)
            
        # textures names
        for i in range(number_of_texture_names):
            read = struct.unpack('16s', reader.read(16))
            texture_name = read[0].decode().rstrip('\x00')
            self.texture_names.insert(i, texture_name)
            
            if False:
                print("texture_name", i)
                print("texture_name:", texture_name)
                
        # types
        for i in range(number_of_types):
            read = struct.unpack('1I 9f 1I', reader.read(44))
                
            plgtype = PlgType()
            plgtype.texture_index = read[0]
            plgtype.u1 = read[1]
            plgtype.v1 = read[2]
            plgtype.u2 = read[3]
            plgtype.v2 = read[4]
            plgtype.width = read[5]
            plgtype.height = read[6]
            plgtype.size_multiplier_min = read[7]
            plgtype.size_multiplier_max = read[8]
            plgtype.probability = read[9]
            plgtype.options = read[10]
            
            if False:
                print("type", i)
                print("probability:", plgtype.probability)
            
            self.types.insert(i, plgtype)
            
        # collection
        for i in range(number_of_collections):
            read = struct.unpack('2I', reader.read(8))
                
            collection = PlgCollection()
            collection.type_offset = read[0]
            collection.type_count = read[1]
            
            if False:
                print("collection", i)
                print("type_count:", collection.type_count)
            
            self.collections.insert(i, collection)
            
        # source textures
        for i in range(number_of_source_textures):
            source_texture = PlgSourceTexture()
            source_texture.colors = [struct.unpack('16I', reader.read(64))[0:15] for _ in range(16)]
            source_texture.density = struct.unpack('f', reader.read(4))[0]
            
            if False:
                print("source_texture", i)
                print("density:", source_texture.density)
            
            self.source_textures.insert(i, source_texture)
            
        # vertices
        for i in range(number_of_vertices):
            read = struct.unpack('7h 6b 1H', reader.read(22))
                
            vertex = PlgVertex()
            vertex.x = read[0]
            vertex.y = read[1]
            vertex.z = read[2]
            vertex.u1 = read[3]
            vertex.v1 = read[4]
            vertex.u2 = read[5]
            vertex.v2 = read[6]
            vertex.nx = read[7]
            vertex.ny = read[8]
            vertex.nz = read[9]
            vertex.alpha1 = read[10]
            vertex.alpha2 = read[11]
            vertex.shadow = read[12]
            vertex.ambient = read[13]
            
            if False:
                print("vertex", i)
                print("x:", vertex.x)
            
            self.vertices.insert(i, vertex)
            
        # triangles
        for i in range(number_of_triangles):
            read = struct.unpack('3H', reader.read(6))
                
            triangle = PlgTriangle()
            triangle.vertex_index_1 = read[0]
            triangle.vertex_index_2 = read[1]
            triangle.vertex_index_3 = read[2]
            
            if False:
                print("triangle", i)
                print("vertex_index_1:", triangle.vertex_index_1)
            
            self.triangles.insert(i, triangle)
            
        # chunks
        for i in range(number_of_chunks):
            read = struct.unpack('1H 5b 1B 2b 2B', reader.read(12))
                
            chunk = PlgChunk()
            chunk.triangle_count = read[0]
            chunk.material_type = read[1]
            chunk.collection = read[2]
            chunk.source_texture_1 = read[3]
            chunk.source_texture_2 = read[4]
            chunk.source_texture_3 = read[5]
            chunk.layer_2_scale = read[6]
            chunk.layer_2_offset_x = read[7]
            chunk.layer_2_offset_y = read[8]
            chunk.density = read[9]
            chunk.size = read[10]
            
            if False:
                print("chunk", i)
                print("source_texture_1:", chunk.source_texture_1)
            
            self.chunks.insert(i, chunk)
            
        # quads
        for i in range(number_of_quads):
            read = struct.unpack('2f 3I 2H 1I', reader.read(28))
                
            quad = PlgQuad()
            quad.min_y = read[0]
            quad.max_y = read[1]
            quad.vertex_offset = read[2]
            quad.triangle_offset = read[3]
            quad.chunk_offset = read[4]
            quad.vertex_count = read[5]
            quad.chunk_count = read[6]
            quad.random_seed = read[7]
            
            if False:
                print("quad", i)
                print("random_seed:", quad.random_seed)
            
            self.quads.insert(i, quad)

        print("Done reading PLG")
        
    def serialize(self, writer : BufferedWriter):
        print("PlgFile.serialize()")
        
        # ...
    
class PlgType:
    def __init__(self):
        self.texture_index = 0
        self.u1 = 0
        self.v1 = 0
        self.u2 = 0
        self.v2 = 0
        self.width = 0
        self.height = 0
        self.size_multiplier_min = 0
        self.size_multiplier_max = 0
        self.probability = 0
        self.options = 0
        
class PlgCollection:
    def __init__(self):
        self.type_offset = 0
        self.type_count = 0
        
class PlgSourceTexture:
    def __init__(self):
        self.colors = []
        self.density = 0
        
class PlgQuad:
    def __init__(self):
        self.min_y = []
        self.max_y = []
        self.vertex_offset = 0
        self.triangle_offset = 0
        self.chunk_offset = 0
        self.vertex_count = 0
        self.chunk_count = 0
        self.random_seed = 0
        
class PlgVertex:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.u1 = 0.0
        self.v1 = 0.0
        self.u2 = 0.0
        self.v2 = 0.0
        self.nx = 0
        self.ny = 0
        self.nz = 0
        self.alpha1 = 0
        self.alpha2 = 0
        self.shadow = 0
        self.ambient = 0
    
class PlgTriangle:
    def __init__(self):
        self.vertex_index_1 = 0
        self.vertex_index_2 = 0
        self.vertex_index_3 = 0
    
class PlgChunk:
    def __init__(self):
        self.triangle_count = 0
        self.material_type = 0
        self.collection = 0
        self.source_texture_1 = 0
        self.source_texture_2 = 0
        self.source_texture_3 = 0
        self.layer_2_scale = 0
        self.layer_2_offset_x = 0
        self.layer_2_offset_y = 0
        self.density = 0
        self.size = 0
    
def create_vertex_from_plg(plg : PlgFile, quad_index : int, vertex_index : int, bm, vertices : {}, uvs1 : {}, uvs2 : {}, quad_size, landscape_scale):
    quad : PlgQuad = plg.quads[quad_index]
    
    plg_vertex : PlgVertex = plg.vertices[vertex_index]

    # orig
	#const float qxMin = (float) ((i % (int) mQuadsNumX) - (int) (mQuadsNumX >> 1)) * 512.0f;
	#const float qzMin = (float) ((i / (int) mQuadsNumX) - (int) (mQuadsNumZ >> 1)) * 512.0f;
	#const float qxMax = qxMin + 512.0f;
	#const float qzMax = qzMin + 512.0f;
    
    qxMin = ((quad_index % plg.number_of_quads_x) - (plg.number_of_quads_x >> 1)) * 512.0
    qzMin = ((quad_index // plg.number_of_quads_x) - (plg.number_of_quads_y >> 1)) * 512.0
    
    if False:
        print("vertex_index:", vertex_index)
        
    if False:
        print("")
        print("quad_index:", quad_index)
        print("qxMin:", qxMin)
        print("qzMin:", qzMin)
    
    #orig
	#int x = (int) floorf((src.xPos + 768.0f - qxMin) * (65535.0f / 2048.0f) + 0.5f);
	#int y = (int) floorf((src.yPos - mQuads[i].yMin) * 65535.0f / (mQuads[i].yMax - mQuads[i].yMin) + 0.5f);
	#int z = (int) floorf((src.zPos + 768.0f - qzMin) * (65535.0f / 2048.0f) + 0.5f);
    
    range_y = quad.max_y - quad.min_y
    
    value_range = 65535.0
    scale_xz = value_range / 2048.0
    scale_y = value_range / range_y
    
    # v2
    #x = (plg_vertex.x + qxMin - 768.0) / scale_xz
    #y = (plg_vertex.y + quad.min_y) / scale_y
    #z = (plg_vertex.z + qzMin - 768.0) / scale_xz
    
    # v3
    x = (plg_vertex.x / scale_xz) + qxMin - 768.0
    y = (plg_vertex.y / scale_y)  + quad.min_y
    z = (plg_vertex.z / scale_xz) + qzMin - 768.0
    
    # llm (v4)
    #float worldX = dst.xPos * (2048.0f / 65535.0f) + qxMin - 768.0f;
    #float worldY = dst.yPos * (quad.yMax - quad.yMin) / 65535.0f + quad.yMin;
    #float worldZ = dst.zPos * (2048.0f / 65535.0f) + qzMin - 768.0f;
    
    vertex_position = Vector((x, z, y)) / landscape_scale
    
    normal_x = plg_vertex.nx / 0xFF
    normal_y = plg_vertex.ny / 0xFF
    normal_z = plg_vertex.nz / 0xFF
    vertex_normal = Vector((normal_x, normal_z, normal_y))
    
    vertex_uv1 = (plg_vertex.u1, -plg_vertex.v1)
    vertex_uv2 = (plg_vertex.u2, -plg_vertex.v2)
    
    vertex = bm.verts.new(vertex_position)
    vertex.normal = vertex_normal
    vertices[vertex_index] = vertex
    
    uvs1[vertex_index] = vertex_uv1
    uvs2[vertex_index] = vertex_uv2
    
    return vertex

class ImportPlg(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_landscape.planting"
    bl_label = "Import Planting"

    filename_ext = ".plg"

    filter_glob: StringProperty(
        default="*.plg",
        options={'HIDDEN'},
        maxlen=255
    )

    def execute(self, context):
        print("ImportPlg.execute() IN")
        
        plg_file_path = Path(self.filepath)
        
        print("plg_file_path:", plg_file_path)
        
        collection = bpy.context.collection
        
        planting_area_collection = bpy.data.collections.new("Planting Areas")
        collection.children.link(planting_area_collection)
        
        plg = PlgFile()
        
        with plg_file_path.open('rb') as plg_file:
            plg.deserialize(plg_file)
        
        landscape_scale = 10.0
        quad_size = 102.4
        
        for h in range(len(plg.quads)):
            plg_quad : PlgQuad = plg.quads[h]
            print("Iterating quad", h)
        
            vertex_dicts = {}
            uvs1_dicts = {}
            uvs2_dicts = {}
                
            bm = bmesh.new()
        
            uv_layer1 = bm.loops.layers.uv.new("UV1")
            uv_layer2 = bm.loops.layers.uv.new("UV2")
        
            mesh = bpy.data.meshes.new(name=f"Planting Mesh {h}")
        
            vertex_buffer_index = 0
            
            if vertex_buffer_index not in vertex_dicts:
                vertex_dicts[vertex_buffer_index] = {}
                
            if vertex_buffer_index not in uvs1_dicts:
                uvs1_dicts[vertex_buffer_index] = {}
                
            if vertex_buffer_index not in uvs2_dicts:
                uvs2_dicts[vertex_buffer_index] = {}
                
            vertices = vertex_dicts[vertex_buffer_index]
            uvs1 = uvs1_dicts[vertex_buffer_index]
            uvs2 = uvs2_dicts[vertex_buffer_index]
            
            for i in range(0, plg_quad.chunk_count):
                chunk_index = plg_quad.chunk_offset + i
                vertex_offset = plg_quad.vertex_offset
                
                plg_chunk : PlgChunk = plg.chunks[chunk_index]
                #print("Iterating chunk", chunk_index)
                
                #chunk_material_index = 0

                for j in range(0, plg_chunk.triangle_count):
                    triangle_index = plg_quad.triangle_offset + j
                    
                    plg_triangle : PlgTriangle = plg.triangles[triangle_index]
                    #print("Iterating triangle", triangle_index)
                        
                    vertex_indices = [
                        vertex_offset + plg_triangle.vertex_index_3, 
                        vertex_offset + plg_triangle.vertex_index_2, 
                        vertex_offset + plg_triangle.vertex_index_1
                    ]
            
                    if len(set(vertex_indices)) < 3:
                        print(f"triangle {triangle_index} is degenerate, vertices {vertex_indices}")
                    else:
                        triangle_vertices = list(range(3))
                            
                        for k, vertex_index in enumerate(vertex_indices):
                            if vertex_index in vertices:
                                triangle_vertices[k] = vertices[vertex_index]
                            else:
                                triangle_vertices[k] = create_vertex_from_plg(plg, h, vertex_index, bm, vertices, uvs1, uvs2, quad_size, landscape_scale)
                    
                        face_vertices = (triangle_vertices[0], triangle_vertices[1], triangle_vertices[2])
            
                        if bm.faces.get(face_vertices):
                           #print("face with vertices already exists:", vertex_indices);
                           for k, vertex_index in enumerate(vertex_indices):
                               triangle_vertices[k] = create_vertex_from_plg(plg, h, vertex_index, bm, vertices, uvs1, uvs2, quad_size, landscape_scale)
                           face_vertices = (triangle_vertices[0], triangle_vertices[1], triangle_vertices[2])
                
                        face = bm.faces.new(face_vertices)
        
                        face.smooth = True
        
                        for k, loop in enumerate(face.loops):
                            vertex_index = vertex_indices[k]
                            
                            loop[uv_layer1].uv = uvs1[vertex_index]
                            loop[uv_layer2].uv = uvs2[vertex_index]

                        #face.material_index = chunk_material_index
                
            bm.verts.ensure_lookup_table()
            bm.faces.ensure_lookup_table()
        
            planting_obj = bpy.data.objects.new(f"Planting {h}", mesh)
        
            planting_area_collection.objects.link(planting_obj)
        
            bm.to_mesh(mesh)
            bm.free()
        
            #mesh.normals_split_custom_set_from_vertices([v.normal for v in mesh.vertices])
    
            #mesh.use_auto_smooth = True
    
            mesh.update()
        
        print("ImportPlg.execute() OUT")

        return {'FINISHED'}
    
class ExportPlg(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export_landscape.planting"
    bl_label = "Export Planting"

    filename_ext = ".plg"

    filter_glob: StringProperty(
        default="*.plg",
        options={'HIDDEN'},
        maxlen=255
    )

    def execute(self, context):
        print("ExportPlg.execute() IN")
        
        # ...

        print("ExportPlg.execute() OUT")

        return {'FINISHED'}
    
def menu_func_import(self, context):
    self.layout.operator(ImportPlg.bl_idname, text="Landscape Planting (.plg)")

def menu_func_export(self, context):
    self.layout.operator(ExportPlg.bl_idname, text="Landscape Planting (.plg)")
    
def register():
    bpy.utils.register_class(ImportPlg)
    bpy.utils.register_class(ExportPlg)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(ImportPlg)
    bpy.utils.unregister_class(ExportPlg)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)