import bpy
import struct
import bmesh

from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from mathutils import Vector, Color

from pathlib import Path

class QadFile:
    def __init__(self):
        self.version = 0
        # ...
        self.textureNames = []
        self.bumpTextureNames = []
        self.quads = []
        self.chunks = []
        self.materials = []

class QadMaterial:
    def __init__(self):
        self.textureNameIndices = []
        self.bumpTextureNameIndices = []
        self.materialType = 0
        self.textureAnimIndex = 0
        self.texMods = []
        self.texModCrcs = []

class QadQuad:
    def __init__(self):
        self.quadX = 0
        self.quadY = 0
        self.firstFace = 0
        self.numFaces = 0
        self.firstChunk = 0
        self.numChunks = 0
        self.circumSpherePositionX = 0.0
        self.circumSpherePositionY = 0.0
        self.circumSpherePositionZ = 0.0
        self.circumSphereRadius = 0.0
        self.firstObject = 0
        self.numObjects = 0
        self.firstMarker = 0
        self.numMarkers = 0
        self.vertexBufferIndex = 0

class QadChunk:
    def __init__(self):
        self.firstFace = 0
        self.numFaces = 0
        self.materialIndex = 0
        self.viewDistLayer = 0

class GeoFile:
    def __init__(self):
        self.version = 0
        self.vertexFormat = 0
        self.bufferCount = 0
        self.indexCount = 0
        self.bufferVertexCounts = []
        self.vertexBuffers = []
        self.triangles = []

class GeoVertex:
    def __init__(self):
        self.positionX = 0.0
        self.positionY = 0.0
        self.positionZ = 0.0
        self.normal = 0
        self.u1 = 0.0
        self.v1 = 0.0
        self.u2 = 0.0
        self.v2 = 0.0
        self.blend = 0
        self.ambient = 0
    
class GeoTriangle:
    def __init__(self):
        self.VertexIndex1 = 0
        self.VertexIndex2 = 0
        self.VertexIndex3 = 0
        
def create_vertex_from_geo(geo : GeoFile, vertex_buffer_index : int, vertex_index : int, bm, vertices : {}, uvs1 : {}, uvs2 : {}, vertex_colors_blend : {}, vertex_colors_ambient : {}, landscape_scale):
    vertex_buffer = geo.vertexBuffers[vertex_buffer_index]
    geo_vertex : GeoVertex = vertex_buffer[vertex_index]
    
    vertex_position = Vector((geo_vertex.positionX, geo_vertex.positionZ, geo_vertex.positionY)) / landscape_scale
    
    normal = geo_vertex.normal
    normalX = ((normal >> 16) & 0xFF) / 255;
    normalY = ((normal >> 8) & 0xFF) / 255;
    normalZ = ((normal >> 0) & 0xFF) / 255;
    vertex_normal = Vector((normalX, normalZ, normalY))
    
    vertex_uv1 = (geo_vertex.u1, -geo_vertex.v1)
    vertex_uv2 = (geo_vertex.u2, -geo_vertex.v2)
    
    blend = geo_vertex.blend
    blendR = ((blend >> 24) & 0xFF) / 255;
    blendG = ((blend >> 16) & 0xFF) / 255
    blendB = ((blend >> 8) & 0xFF) / 255;
    blendA = ((blend >> 0) & 0xFF) / 255;
    vertex_color_blend = (blendR, blendG, blendB, blendA)
    
    ambient = geo_vertex.ambient
    ambientR = ((ambient >> 24) & 0xFF) / 255;
    ambientG = ((ambient >> 16) & 0xFF) / 255;
    ambientB = ((ambient >> 8) & 0xFF) / 255;
    ambientA = ((ambient >> 0) & 0xFF) / 255;
    vertex_color_ambient = (ambientR, ambientG, ambientB, ambientA)
    
    vertex = bm.verts.new(vertex_position)
    vertex.normal = vertex_normal
    vertices[vertex_index] = vertex
    
    uvs1[vertex_index] = vertex_uv1
    uvs2[vertex_index] = vertex_uv2
    
    vertex_colors_blend[vertex_index] = vertex_color_blend
    vertex_colors_ambient[vertex_index] = vertex_color_ambient
    
    return vertex

class ImportQad(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_landscape.scenario"
    bl_label = "Import Scenario"

    filename_ext = ".qad"

    filter_glob: StringProperty(
        default="*.qad",
        options={'HIDDEN'},
        maxlen=255
    )

    use_setting: BoolProperty(
        name="Example Boolean",
        description="Example Tooltip",
        default=True,
    )

    type: EnumProperty(
        name="Example Enum",
        description="Choose between two items",
        items=(
            ('OPT_A', "First Option", "Description one"),
            ('OPT_B', "Second Option", "Description two"),
        ),
        default='OPT_A',
    )

    def execute(self, context):
        print("ImportQad.execute() IN")
        qadFilePath = Path(self.filepath)
        geoFilePath = qadFilePath.with_suffix(".geo")
        textureFolderPath = qadFilePath.parent / "Textures" / "tga"
        print("qadFilePath:", qadFilePath)
        print("geoFilePath:", geoFilePath)
        print("textureFolderPath:", textureFolderPath)

        qad = QadFile()
        geo = GeoFile()
        
        landscapeScale = 10
        
        with qadFilePath.open('rb') as qadFile:
            readData_initial = struct.unpack('32I', qadFile.read(128))
            
            signature = readData_initial[0]
            version = readData_initial[1]
            _ = readData_initial[2]
            _ = readData_initial[3]
            numberOfQuadsX = readData_initial[4]
            numberOfQuadsY = readData_initial[5]
            numberOfQuads = readData_initial[6]
            numberOfChunks = readData_initial[7]
            numberOfTextureNamesTotal = readData_initial[8]
            numberOfObjectNames = readData_initial[9]
            numberOfPolygons = readData_initial[10]
            numberOfMaterials = readData_initial[11]
            numberOfPlacedObjects = readData_initial[12]
            numberOfTexturePropertyGroups = readData_initial[13]
            sizeOfCollisionQuads = readData_initial[14]
            markerVersionAndCount = readData_initial[15]
            flagKickdata = readData_initial[16]
            numberOfSounds = readData_initial[17]
            sizeOfNamedObjectStringPool = readData_initial[18]
            numberOfNamedObjects = readData_initial[19]
            sizeOfMarkerExtraData = readData_initial[20]
            _ = readData_initial[21]
            _ = readData_initial[22]
            _ = readData_initial[23]
            _ = readData_initial[24]
            _ = readData_initial[25]
            _ = readData_initial[26]
            _ = readData_initial[27]
            _ = readData_initial[28]
            _ = readData_initial[29]
            _ = readData_initial[30]
            _ = readData_initial[31]
            
            numberOfTextureNames = numberOfTextureNamesTotal & 0xFFFF

            numberOfBumpTextureNames = (numberOfTextureNamesTotal >> 16) & 0xFFFF

            numberOfTexGroupIndices = max(((numberOfTextureNamesTotal & 0xFFFF) + 1) & ~1, 256)

            if True:
                print("version:", version)
                print("numberOfQuads:", numberOfQuads)
                print("numberOfChunks:", numberOfChunks)
                print("numberOfTextureNames:", numberOfTextureNames)
                print("numberOfBumpTextureNames:", numberOfBumpTextureNames)
                print("numberOfTexGroupIndices:", numberOfTexGroupIndices)
                print("sizeOfMarkerExtraData:", sizeOfMarkerExtraData)

            for i in range(numberOfTextureNames):
                readData_textureName = struct.unpack('32s', qadFile.read(32))
                textureName = readData_textureName[0].decode().rstrip('\x00')
                qad.textureNames.insert(i, textureName)
                #print("textureName:", textureName)
                
            for _ in range(numberOfBumpTextureNames):
                readData_bumpTextureName = struct.unpack('32s', qadFile.read(32))
                bumpTextureName = readData_bumpTextureName[0].decode().rstrip('\x00')
                qad.bumpTextureNames.insert(i, bumpTextureName)
                #print("bumpTextureName:", bumpTextureName)
                
            for _ in range(numberOfObjectNames):
                readData_objectName = struct.unpack('32s', qadFile.read(32))
                objectName = readData_objectName[0].decode().rstrip('\x00')
                #print("objectName:", objectName)
                
            for _ in range(numberOfObjectNames):
                readData_objectData = struct.unpack('2H 4I 48s 48s', qadFile.read(116))
                typeA = readData_objectData[0]
                typeB = readData_objectData[1]
                weight = readData_objectData[2]
                _ = readData_objectData[3]
                _ = readData_objectData[4]
                _ = readData_objectData[5]
                soundA = readData_objectData[6].decode().rstrip('\x00')
                soundB = readData_objectData[7].decode().rstrip('\x00')
                
            for i in range(numberOfQuads):
                readData_quad = struct.unpack('2H 4I 4f 6H', qadFile.read(48))
                
                quad = QadQuad()
                quad.quadX = readData_quad[0]
                quad.quadY = readData_quad[1]
                quad.firstFace = readData_quad[2]
                quad.numFaces = readData_quad[3]
                quad.firstChunk = readData_quad[4]
                quad.numChunks = readData_quad[5]
                quad.circumSpherePositionX = readData_quad[6]
                quad.circumSpherePositionY = readData_quad[7]
                quad.circumSpherePositionZ = readData_quad[8]
                quad.circumSphereRadius = readData_quad[9]
                quad.firstObject = readData_quad[10]
                quad.numObjects = readData_quad[11]
                quad.firstMarker = readData_quad[12]
                quad.numMarkers = readData_quad[13]
                quad.vertexBufferIndex = readData_quad[14]
                _ = readData_quad[15]
                qad.quads.insert(i, quad)
                    
            collisionQuads = qadFile.read(sizeOfCollisionQuads)
                
            for i in range(numberOfChunks):
                readData_chunk = struct.unpack('2L 1H 2B', qadFile.read(12))
                
                chunk = QadChunk()
                chunk.firstFace = readData_chunk[0]
                chunk.numFaces = readData_chunk[1]
                chunk.materialIndex = readData_chunk[2]
                chunk.viewDistLayer = readData_chunk[3]
                _ = readData_chunk[4]
                qad.chunks.insert(i, chunk)
                    
            for i in range(numberOfMaterials):
                readData_material = struct.unpack('4H 3H 3H 4f 4f 2L', qadFile.read(60))
                
                material = QadMaterial()
                material.textureNameIndices = [ readData_material[0], readData_material[1], readData_material[2], readData_material[3] ]
                material.bumpTextureNameIndices = [ readData_material[4], readData_material[5], readData_material[6] ]
                material.materialType = readData_material[7]
                material.textureAnimIndex = readData_material[8]
                _ = readData_material[9]
                material.texMods = [ [ readData_material[10], readData_material[11], readData_material[12], readData_material[13] ], [ readData_material[14], readData_material[15], readData_material[16], readData_material[17] ] ]
                material.texModCrcs = [ readData_material[18], readData_material[19] ]
                qad.materials.insert(i, material)
                
            # continue reading QAD
               
            print("Done reading QAD")
        
        with geoFilePath.open('rb') as geoFile:
            readData_initial = struct.unpack('8I', geoFile.read(32))
            
            signature = readData_initial[0]
            geo.version = readData_initial[1]
            geo.vertexFormat = readData_initial[2]
            geo.bufferCount = readData_initial[3]
            geo.indexCount = readData_initial[4]
            _ = readData_initial[5]
            _ = readData_initial[6]
            _ = readData_initial[7]
            
            if True:
                print("version:", geo.version)
                print("vertexFormat:", geo.vertexFormat)
                print("bufferCount:", geo.bufferCount)
                print("indexCount:", geo.indexCount)

            for i in range(geo.bufferCount):
                readData_bufferVertexCount = struct.unpack('I', geoFile.read(4))
                bufferVertexCount = readData_bufferVertexCount[0]
                geo.bufferVertexCounts.insert(i, bufferVertexCount)
                if False:
                    print("")
                    print("bufferVertexCount:", bufferVertexCount)
                
            for i in range(geo.bufferCount):
                vertices = []
                for j in range(geo.bufferVertexCounts[i]):
                    readData_vertex = struct.unpack('3f I 4f 2I', geoFile.read(40))
                    
                    vertex = GeoVertex()
                    vertex.positionX = readData_vertex[0]
                    vertex.positionY = readData_vertex[1]
                    vertex.positionZ = readData_vertex[2]
                    vertex.normal = readData_vertex[3]
                    vertex.u1 = readData_vertex[4]
                    vertex.v1 = readData_vertex[5]
                    vertex.u2 = readData_vertex[6]
                    vertex.v2 = readData_vertex[7]
                    vertex.blend = readData_vertex[8]
                    vertex.ambient = readData_vertex[9]
                    vertices.insert(j, vertex)
                        
                geo.vertexBuffers.insert(i, vertices)
                        
            if geo.vertexFormat > 2:
                for i in range(geo.bufferCount):
                    for j in range(geo.bufferVertexCounts[i]):
                        readData_uv1Tangent = struct.unpack('4H', geoFile.read(8))
                        readData_uv2Tangent = struct.unpack('4H', geoFile.read(8))
                        if False:
                            print("")
            
            for i in range(geo.indexCount // 3):
                readData_triangle = struct.unpack('3H', geoFile.read(6))
                
                triangle = GeoTriangle()
                triangle.vertexIndex1 = readData_triangle[0]
                triangle.vertexIndex2 = readData_triangle[1]
                triangle.vertexIndex3 = readData_triangle[2]
                geo.triangles.insert(i, triangle)
            
            print("Done reading GEO")
        
        loadedTextures = {}

        materials = []
        
        landscape_scale = 10.0
        
        bm = bmesh.new()
    
        uv_layer1 = bm.loops.layers.uv.new("UV1")
        uv_layer2 = bm.loops.layers.uv.new("UV2")
        
        color_layer_blend = bm.loops.layers.color.new("Blend")
        color_layer_ambient = bm.loops.layers.color.new("Ambient")
    
        vertex_dicts = {}
        uvs1_dicts = {}
        uvs2_dicts = {}
        vertex_colors_blend_dicts = {}
        vertex_colors_ambient_dicts = {}

        part_material_indices = []
        
        for i in range(len(qad.materials)):
            qadMaterial = qad.materials[i]
            material = bpy.data.materials.new(name=f"Material {i} Type {qadMaterial.materialType}")
            
            textureNames = []
            bumpTextureNames = []

            for j in range(len(qadMaterial.textureNameIndices)):
                textureNameIndex = qadMaterial.textureNameIndices[j]
                textureName = qad.textureNames[textureNameIndex]
                textureNames.insert(j, textureName)
                
            for j in range(len(qadMaterial.bumpTextureNameIndices)):
                bumpTextureNameIndex = qadMaterial.bumpTextureNameIndices[j]
                if bumpTextureNameIndex != 0xFFFF:
                    bumpTextureName = qad.bumpTextureNames[bumpTextureNameIndex]
                    bumpTextureNames.insert(j, bumpTextureName)
                
            firstTextureName = textureNames[0]
                
            firstTextureFilePath = textureFolderPath / f"{firstTextureName}.tga"
            
            #print("firstTextureFilePath:", firstTextureFilePath)
            
            loadedTexture = None

            if firstTextureName in loadedTextures:
                loadedTexture = loadedTextures[firstTextureName]
            else:
                if firstTextureFilePath.exists():
                    loadedTexture = bpy.data.images.load(str(firstTextureFilePath))
                    loadedTextures[firstTextureName] = loadedTexture
            
            material.use_nodes = True
            material.use_backface_culling = True
                    
            material_output = material.node_tree.nodes.get('Material Output')
            principled_BSDF = material.node_tree.nodes.get('Principled BSDF')

            tex_node = material.node_tree.nodes.new('ShaderNodeTexImage')

            if loadedTexture != None:
                tex_node.image = loadedTexture

            material.node_tree.links.new(tex_node.outputs[0], principled_BSDF.inputs[0])
        
            materials.insert(i, material)
        
        for h in range(len(qad.quads)):
            qad_quad : QadQuad = qad.quads[h]
            print("Iterating quad", h)
            
            vertex_buffer_index = qad_quad.vertexBufferIndex
            
            if vertex_buffer_index not in vertex_dicts:
                vertex_dicts[vertex_buffer_index] = {}
                
            if vertex_buffer_index not in uvs1_dicts:
                uvs1_dicts[vertex_buffer_index] = {}
                
            if vertex_buffer_index not in uvs2_dicts:
                uvs2_dicts[vertex_buffer_index] = {}
                
            if vertex_buffer_index not in vertex_colors_blend_dicts:
                vertex_colors_blend_dicts[vertex_buffer_index] = {}
                
            if vertex_buffer_index not in vertex_colors_ambient_dicts:
                vertex_colors_ambient_dicts[vertex_buffer_index] = {}
                
            vertices = vertex_dicts[vertex_buffer_index]
            uvs1 = uvs1_dicts[vertex_buffer_index]
            uvs2 = uvs2_dicts[vertex_buffer_index]
            vertex_colors_blend = vertex_colors_blend_dicts[vertex_buffer_index]
            vertex_colors_ambient = vertex_colors_ambient_dicts[vertex_buffer_index]
        
            for i in range(qad_quad.firstChunk, qad_quad.firstChunk + qad_quad.numChunks):
                qad_chunk : QadChunk = qad.chunks[i]
                #print("Iterating chunk", j)
                
                for j in range(qad_chunk.firstFace, qad_chunk.firstFace + qad_chunk.numFaces):
                    qad_triangle = geo.triangles[j]
                    #print("Iterating triangle", j)
                    
                    vertex_indices = [qad_triangle.vertexIndex3, qad_triangle.vertexIndex2, qad_triangle.vertexIndex1]
            
                    if len(set(vertex_indices)) < 3:
                        print(f"triangle {j} is degenerate, vertices {vertex_indices}")
                    else:
                        triangle_vertices = list(range(3))

                        for k, vertex_index in enumerate(vertex_indices):
                            if vertex_index in vertices:
                                triangle_vertices[k] = vertices[vertex_index]
                            else:
                                triangle_vertices[k] = create_vertex_from_geo(geo, vertex_buffer_index, vertex_index, bm, vertices, uvs1, uvs2, vertex_colors_blend, vertex_colors_ambient, landscape_scale)
                    
                        face_vertices = (triangle_vertices[0], triangle_vertices[1], triangle_vertices[2])
            
                        if bm.faces.get(face_vertices):
                            print("face with vertices already exists:", vertex_indices);
                            for k, vertex_index in enumerate(vertex_indices):
                                triangle_vertices[k] = create_vertex_from_geo(geo, vertex_buffer_index, vertex_index, bm, vertices, uvs1, uvs2, vertex_colors_blend, vertex_colors_ambient, landscape_scale)
                            face_vertices = (triangle_vertices[0], triangle_vertices[1], triangle_vertices[2])
                
                        face = bm.faces.new(face_vertices)
        
                        face.smooth = True
        
                        for k, loop in enumerate(face.loops):
                            vertex_index = vertex_indices[k]
                            
                            loop[uv_layer1].uv = uvs1[vertex_index]
                            loop[uv_layer2].uv = uvs2[vertex_index]
                            
                            loop[color_layer_blend] = vertex_colors_blend[vertex_index]
                            loop[color_layer_ambient] = vertex_colors_ambient[vertex_index]

                        face.material_index = len(part_material_indices)
                
                part_material_indices.append(qad_chunk.materialIndex)
                    
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
    
        mesh = bpy.data.meshes.new(name=f"Scenario Mesh")
        obj = bpy.data.objects.new("Scenario", mesh)
        
        bpy.context.collection.objects.link(obj)
        
        bm.to_mesh(mesh)
        bm.free()
        
        for i in range(len(part_material_indices)):
            part_material_index = part_material_indices[i]
            part_material = materials[part_material_index]
            mesh.materials.append(part_material)
            #print(f"part material {i} -> index {part_material_index}")

        mesh.normals_split_custom_set_from_vertices([v.normal for v in mesh.vertices])
    
        mesh.use_auto_smooth = True
    
        mesh.update()
        
        print("ImportQad.execute() OUT")

        return {'FINISHED'}

def menu_func_import(self, context):
    self.layout.operator(ImportQad.bl_idname, text="Landscape Scenario (.qad)")

def register():
    bpy.utils.register_class(ImportQad)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(ImportQad)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)