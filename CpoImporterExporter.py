import bpy
import bmesh

from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from mathutils import Vector, Matrix
from pathlib import Path

from .Cpo import *
from .utils import *

def add_cpo_shape(cpo : CpoFile, shape_index : int):
    cpo_shape : CpoShape = cpo.shapes[shape_index]
    
    landscape_scale = 10
    
    bm = bmesh.new()
    
    vertices = {}
    
    if cpo_shape.type == 1:
        print("collision shape type 1 not supported")
    elif cpo_shape.type == 2:
        print("collision shape type 2 not supported")
    elif cpo_shape.type == 3:
        cpo_shape_data : CpoShapeDataMesh = cpo_shape.data
        
        for i in range(len(cpo_shape_data.polygons)):
            cpo_polygon : CpoPolygon = cpo_shape_data.polygons[i]
            
            number_of_polygons = len(cpo_polygon.vertex_indices)
            
            polygon_vertices = list(range(number_of_polygons))
            
            for j in range(number_of_polygons):
                vertex_index = cpo_polygon.vertex_indices[number_of_polygons - 1 - j]
                
                if vertex_index in vertices:
                    polygon_vertices[j] = vertices[vertex_index]
                else:
                    cpo_vertex = cpo_shape_data.vertices[vertex_index]
                    
                    vertex_position = Vector((cpo_vertex.position_x, cpo_vertex.position_z, cpo_vertex.position_y)) / landscape_scale
                      
                    vertex = bm.verts.new(vertex_position)
                    vertices[vertex_index] = vertex
                    
                    polygon_vertices[j] = vertex
                    
            face_vertices = tuple(polygon_vertices)
                
            face = bm.faces.new(face_vertices)
                
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    
    mesh = bpy.data.meshes.new(name=f"Collision Shape {shape_index} Mesh")
    obj = bpy.data.objects.new(f"Collision Shape {shape_index}", mesh)
    
    bpy.context.collection.objects.link(obj)
    
    bm.to_mesh(mesh)
    bm.free()
        
    mesh.update()
    
    if cpo_shape.type == 1:
        pass
    elif cpo_shape.type == 2:
        pass
    elif cpo_shape.type == 3:
        cpo_shape_data : CpoShapeDataMesh = cpo_shape.data
        
        position = Vector((cpo_shape_data.position_x, cpo_shape_data.position_y, cpo_shape_data.position_z))
        
        print("position:", position)

        matrix = Matrix(cpo_shape_data.matrix).to_4x4().transposed()
        matrix.translation += position
    
        decompose_and_apply_matrix(obj, matrix, landscape_scale)

def retrieve_cpo_shape(cpo : CpoFile, shape_obj):
    cpo_shape = CpoShape()
    cpo_shape.type = 3
    
    cpo_shape.data = CpoShapeDataMesh()
    
    temp_obj = shape_obj.copy()
    temp_obj.data = shape_obj.data.copy()
    bpy.context.collection.objects.link(temp_obj)
    
    bpy.context.view_layer.objects.active = temp_obj
    temp_obj.select_set(True)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    landscape_scale = 10
    
    mesh = temp_obj.data

    mesh.calc_loop_triangles()
    
    used_vertex_indices = {}
    
    for polygon in mesh.polygons:
        cpo_polygon = CpoPolygon()
        
        number_of_vertices = len(polygon.loop_indices)

        for i in range(number_of_vertices):
            loop_index = polygon.loop_indices[number_of_vertices - 1 - i]
            loop = mesh.loops[loop_index]
            source_vertex_index = loop.vertex_index
            
            if source_vertex_index not in used_vertex_indices:
                source_vertex = mesh.vertices[source_vertex_index]
                
                used_vertex_indices[source_vertex_index] = len(cpo_shape.data.vertices)
                    
                position = source_vertex.co
            
                cpo_vertex = CpoVertex()
            
                cpo_vertex.position_x = position.x * landscape_scale
                cpo_vertex.position_y = position.z * landscape_scale
                cpo_vertex.position_z = position.y * landscape_scale
            
                cpo_shape.data.vertices.append(cpo_vertex)
                
            cpo_polygon.vertex_indices.append(used_vertex_indices[source_vertex_index])
            
        cpo_shape.data.polygons.append(cpo_polygon)
        
    bpy.data.objects.remove(temp_obj, do_unlink=True)
        
    input_matrix = compose_matrix(shape_obj, landscape_scale)
    input_position = input_matrix.to_translation()
    
    input_matrix.translation = Vector((0.0, 0.0, 0.0))

    cpo_shape.data.matrix = input_matrix.transposed()
    cpo_shape.data.position_x = input_position.x
    cpo_shape.data.position_y = input_position.y
    cpo_shape.data.position_z = input_position.z
    
    cpo.shapes.append(cpo_shape)

class ImportCpo(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_landscape.collision"
    bl_label = "Import Collision"

    filename_ext = ".cpo"

    filter_glob: StringProperty(
        default="*.cpo",
        options={'HIDDEN'},
        maxlen=255
    )

    def execute(self, context):
        print("ImportCpo.execute() IN")
        cpo_file_path = Path(self.filepath)
        print("cpo_file_path:", cpo_file_path)
        
        cpo = CpoFile()
            
        with cpo_file_path.open('rb') as cpo_reader:
            cpo.deserialize(cpo_reader)
                
        for i in range(len(cpo.shapes)):
            add_cpo_shape(cpo, i)

        print("ImportCpo.execute() OUT")

        return {'FINISHED'}
    
class ExportCpo(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export_landscape.collision"
    bl_label = "Export Collision"

    filename_ext = ".cpo"

    filter_glob: StringProperty(
        default="*.cpo",
        options={'HIDDEN'},
        maxlen=255
    )
    
    def execute(self, context):
        print("ExportCpo.execute() IN")
        cpo_file_path = Path(self.filepath)
        print("cpo_file_path:", cpo_file_path)
        
        cpo = CpoFile()
        
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH' and obj.parent is None and (obj.select_get() and not obj.hide_select):
                retrieve_cpo_shape(cpo, obj)
                
        with cpo_file_path.open('wb') as cpo_writer:
            cpo.serialize(cpo_writer)

        print("ExportCpo.execute() OUT")

        return {'FINISHED'}
    
def menu_func_import(self, context):
    self.layout.operator(ImportCpo.bl_idname, text="Landscape Collision (.cpo)")
    
def menu_func_export(self, context):
    self.layout.operator(ExportCpo.bl_idname, text="Landscape Collision (.cpo)")
    
def register():
    bpy.utils.register_class(ImportCpo)
    bpy.utils.register_class(ExportCpo)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(ImportCpo)
    bpy.utils.unregister_class(ExportCpo)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)