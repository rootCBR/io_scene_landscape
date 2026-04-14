import array
from asyncio.windows_events import NULL
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

from .Markers import *
from .CData import *
from .QadTexturePropertyGroupPanels import *
from .QadObjectLibraryPanels import *
from .MoxImporterExporter import import_mox, swap_yz_axes_of_quaternion
from .utils import *
from .globals import *

class QadMaterial:
    def __init__(self):
        self.textureNameIndices = [0 for _ in range(4)]
        self.bumpTextureNameIndices = [-1 for _ in range(3)]
        self.materialType = 0
        self.textureAnimIndex = 0
        self.texMods = [0.0 for _ in range(4 * 2)]
        self.texModCrcs = [0 for _ in range(2)]

class QadObjectData:
    def __init__(self):
        self.name = ""
        self.type = 0
        self.kick_type = 0
        self.weight = 0
        self.kick_sound = ""
        self.bounce_sound = ""

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

class QadTexAnim:
    def __init__(self):
        self.type = 0
        self.mode = 0
        self.layers = 0
        self.speed = 0
        self.fps = 0
        self.step = 0
        self.begin = 0
        self.end = 0
        self.step_u = 0
        self.step_v = 0
        self.texture_scale_x = 0
        self.texture_scale_y = 0
        self.texture_offset_x = 0
        self.texture_offset_y = 0

class QadPlacedObject:
    def __init__(self):
        self.name = ""
        self.index = 0
        self.path_flag = 0
        self.position_x = 0.0
        self.position_y = 0.0
        self.position_z = 0.0
        self.rotation_x = 0.0
        self.rotation_y = 0.0
        self.rotation_z = 0.0
        self.rotation_w = 0.0
        self.scale = 1.0
        self.matrix = [0.0 for _ in range(9)]
        self.melted_flag = 0
        self.in_shadow = 0
        self.path_z = 0.0

class QadTexturePropertyGroup:
    def __init__(self):
        self.name = ""
        self.dustPercentage = 0
        self.gripPercentageFront = 0
        self.gripPercentageRear = 0
        self.brakePercentage = 0
        self.slipMode = 0
        self.skidmarkType = 0
        self.sound = ""
        self.collisionOptions = 0
        self.collisionSoundType = 0
        self.disableShadow = 0
        self.disableRendering = 0
        self.emitter = 0
        self.rumbleSlow = 0
        self.rumbleFast = 0
        
def create_instance_hierarchy(object_ref, collection, parent=None):
    instance = bpy.data.objects.new(f"Instance_{object_ref.name}", object_ref.data)
    collection.objects.link(instance)
    
    instance.location = object_ref.location
    instance.rotation_euler = object_ref.rotation_euler
    instance.scale = object_ref.scale
    
    if parent:
        instance.parent = parent

    for child in object_ref.children:
        create_instance_hierarchy(child, collection, instance)
    
    return instance

class QadFile:
    def __init__(self):
        self.version = 0
        # ...
        self.terrain_size_x = 0
        self.terrain_size_y = 0
        self.number_of_quads_x = 0
        self.number_of_quads_y = 0
        self.number_of_quads = 0
        self.number_of_polygons = []
        self.textureNames = []
        self.bumpTextureNames = []
        self.quads = []
        self.collision_data = []
        self.object_data = []
        self.chunks = []
        self.materials = []
        self.texture_anims = []
        self.placed_objects = []
        self.named_object_string_pool = []
        self.named_object_map = []
        self.markers = []
        self.marker_parameters = []
        self.texture_property_groups = []
        self.texture_group_indices = []
        self.sounds = []
        self.stringSection = []
        
    def deserialize(self, reader : BufferedReader, qad_format_version : int):
        print("QadFile.deserialize()")
        
        signature = struct.unpack('I', reader.read(4))[0]
        
        is_format_wr2 = qad_format_version == 1
        is_format_ct0 = qad_format_version == 2
        is_format_ct1 = qad_format_version == 3
        is_new_format = False
        
        print("qad_format_version:", qad_format_version)
        
        if signature == 0x51554144:
            is_new_format = True
            
            readData_initial = struct.unpack('31I', reader.read(124))
            
            version = readData_initial[0]
            _ = readData_initial[1]
            _ = readData_initial[2]
            numberOfQuadsX = readData_initial[3]
            numberOfQuadsY = readData_initial[4]
            numberOfQuads = readData_initial[5]
            numberOfChunks = readData_initial[6]
            numberOfTextureNamesTotal = readData_initial[7]
            numberOfObjectNames = readData_initial[8]
            numberOfPolygons = readData_initial[9]
            numberOfMaterials = readData_initial[10]
            numberOfPlacedObjects = readData_initial[11]
            numberOfTexturePropertyGroups = readData_initial[12]
            sizeOfCollisionQuads = readData_initial[13]
            marker_version_and_count = readData_initial[14]
            flagKickdata = readData_initial[15]
            numberOfSounds = readData_initial[16]
            sizeOfNamedObjectStringPool = readData_initial[17]
            numberOfNamedObjects = readData_initial[18]
            size_of_marker_parameters = readData_initial[19]
            _ = readData_initial[20]
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
        else:
            
            readData_initial = struct.unpack('15I', reader.read(60))
            
            _ = readData_initial[0]
            numberOfQuadsX = readData_initial[1]
            numberOfQuadsY = readData_initial[2]
            numberOfQuads = readData_initial[3]
            numberOfChunks = readData_initial[4]
            numberOfTextureNamesTotal = readData_initial[5]
            numberOfObjectNames = readData_initial[6]
            numberOfPolygons = readData_initial[7]
            numberOfMaterials = readData_initial[8]
            numberOfPlacedObjects = readData_initial[9]
            numberOfTexturePropertyGroups = readData_initial[10]
            sizeOfCollisionQuads = readData_initial[11]
            marker_version_and_count = readData_initial[12]
            flagKickdata = readData_initial[13]
            numberOfSounds = readData_initial[14]
            
        numberOfTextureNames = numberOfTextureNamesTotal & 0xFFFF

        numberOfBumpTextureNames = (numberOfTextureNamesTotal >> 16) & 0xFFFF

        numberOfTexGroupIndices = max(((numberOfTextureNamesTotal & 0xFFFF) + 1) & ~1, 256)

        number_of_texture_animations = 16
        
        marker_version = (marker_version_and_count >> 24) & 0xFF;
        number_of_markers = marker_version_and_count & 0x00FFFFFF;

        if True:
            print("numberOfQuads:", numberOfQuads)
            print("numberOfChunks:", numberOfChunks)
            print("numberOfTextureNames:", numberOfTextureNames)
            print("numberOfBumpTextureNames:", numberOfBumpTextureNames)
            print("numberOfObjectNames:", numberOfObjectNames)
            print("numberOfPolygons:", numberOfPolygons)
            print("numberOfMaterials:", numberOfMaterials)
            print("numberOfPlacedObjects:", numberOfPlacedObjects)
            print("numberOfTexturePropertyGroups:", numberOfTexturePropertyGroups)
            print("numberOfTexGroupIndices:", numberOfTexGroupIndices)
            print("numberOfSounds:", numberOfSounds)
            
            print("marker_version:", marker_version)
            print("number_of_markers:", number_of_markers)

        for i in range(numberOfTextureNames):
            readData_textureName = struct.unpack('32s', reader.read(32))
            textureName = readData_textureName[0].decode().rstrip('\x00')
            self.textureNames.insert(i, textureName)
            
            print(f"textureName = {textureName}")
                
        for _ in range(numberOfBumpTextureNames):
            readData_bumpTextureName = struct.unpack('32s', reader.read(32))
            bumpTextureName = readData_bumpTextureName[0].decode().rstrip('\x00')
            self.bumpTextureNames.insert(i, bumpTextureName)
            
            print(f"bumpTextureName = {bumpTextureName}")
                
        for i in range(numberOfObjectNames):
            readData_objectName = struct.unpack('32s', reader.read(32))
            
            name_decoded = readData_objectName[0].decode().rstrip('\x00')
            
            object_data = QadObjectData()
            object_data.name = name_decoded

            self.object_data.append(object_data)
            
            print(f"object_data.name = {object_data.name}")
                
        for i in range(numberOfObjectNames):
            readData_objectData = struct.unpack('2H 4I 48s 48s', reader.read(116))
            
            object_data : QadObjectData = self.object_data[i]
            
            object_data.type = readData_objectData[0]
            object_data.kick_type = readData_objectData[1]
            object_data.weight = readData_objectData[2]
            _ = readData_objectData[3]
            _ = readData_objectData[4]
            _ = readData_objectData[5]
            object_data.kick_sound = readData_objectData[6].decode().rstrip('\x00')
            object_data.bounce_sound = readData_objectData[7].decode().rstrip('\x00')
                
        for i in range(numberOfQuads):
            readData_quad = struct.unpack('2H 4I 4f 6H', reader.read(48))
                
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
            self.quads.insert(i, quad)
                    
        collisionQuads = reader.read(sizeOfCollisionQuads)
                
        for i in range(numberOfChunks):
            readData_chunk = struct.unpack('2L 1H 2B', reader.read(12))
                
            chunk = QadChunk()
            chunk.firstFace = readData_chunk[0]
            chunk.numFaces = readData_chunk[1]
            chunk.materialIndex = readData_chunk[2]
            chunk.viewDistLayer = readData_chunk[3]
            _ = readData_chunk[4]
            self.chunks.insert(i, chunk)
                    
        for i in range(numberOfMaterials):
            material = QadMaterial()
            
            if is_format_wr2:
                readData_material = struct.unpack('3H 1h 24f 3L', reader.read(116))
                
                material.textureNameIndices = [ readData_material[0], readData_material[1], readData_material[2] ]
                material.materialType = readData_material[3]
            
                # texMatrix[8 * 3]
                
                material.texModCrcs = [ readData_material[28], readData_material[29], readData_material[30] ]
            elif is_format_ct0 or is_format_ct1:
                readData_material = struct.unpack('4H 3h 1H 4f 4f 2L', reader.read(56))
                
                material.textureNameIndices = [ readData_material[0], readData_material[1], readData_material[2], readData_material[3] ]
                material.bumpTextureNameIndices = [ readData_material[4], readData_material[5], readData_material[6] ]
                material.materialType = readData_material[7]
            
                material.texMods = [ readData_material[8], readData_material[9], readData_material[10], readData_material[11], readData_material[12], readData_material[13], readData_material[14], readData_material[15] ]
                material.texModCrcs = [ readData_material[16], readData_material[17] ]
            elif is_new_format:
                readData_material = struct.unpack('4H 3h 3H 4f 4f 2L', reader.read(60))
                
                material.textureNameIndices = [ readData_material[0], readData_material[1], readData_material[2], readData_material[3] ]
                material.bumpTextureNameIndices = [ readData_material[4], readData_material[5], readData_material[6] ]
                material.materialType = readData_material[7]
            
                material.textureAnimIndex = readData_material[8]
                _ = readData_material[9]
                
                material.texMods = [ readData_material[10], readData_material[11], readData_material[12], readData_material[13], readData_material[14], readData_material[15], readData_material[16], readData_material[17] ]
                material.texModCrcs = [ readData_material[18], readData_material[19] ]
                
            self.materials.insert(i, material)
                
        # texture animations
        if is_new_format:
            for i in range(number_of_texture_animations):
                readData_texAnim = struct.unpack('14i', reader.read(56))
            
                texture_animation = QadTexAnim()
                texture_animation.type = readData_texAnim[0]
                texture_animation.mode = readData_texAnim[1]
                texture_animation.layers = readData_texAnim[2]
                texture_animation.speed = readData_texAnim[3]
                texture_animation.fps = readData_texAnim[4]
                texture_animation.step = readData_texAnim[5]
                texture_animation.begin = readData_texAnim[6]
                texture_animation.end = readData_texAnim[7]
                texture_animation.step_u = readData_texAnim[8]
                texture_animation.step_v = readData_texAnim[9]
                texture_animation.texture_scale_x = readData_texAnim[10]
                texture_animation.texture_scale_y = readData_texAnim[11]
                texture_animation.texture_offset_x = readData_texAnim[12]
                texture_animation.texture_offset_y = readData_texAnim[13]
                self.texture_anims.insert(i, texture_animation)
            
        # placed objects
        for i in range(numberOfPlacedObjects):
            placed_object = QadPlacedObject()
                
            name_decoded = struct.unpack('32s', reader.read(32))[0].split(b'\x00')[0].decode('latin-1')
            
            placed_object.name = name_decoded
            placed_object.index = struct.unpack('H', reader.read(2))[0]
            
            placed_object.path_flag = struct.unpack('H', reader.read(2))[0]
            placed_object.position_x = struct.unpack('f', reader.read(4))[0]
            placed_object.position_y = struct.unpack('f', reader.read(4))[0]
            placed_object.position_z = struct.unpack('f', reader.read(4))[0]
            placed_object.rotation_x = struct.unpack('f', reader.read(4))[0]
            placed_object.rotation_y = struct.unpack('f', reader.read(4))[0]
            placed_object.rotation_z = struct.unpack('f', reader.read(4))[0]
            placed_object.rotation_w = struct.unpack('f', reader.read(4))[0]
            placed_object.scale = struct.unpack('f', reader.read(4))[0]
                
            placed_object.matrix[0] = struct.unpack('f', reader.read(4))[0]
            placed_object.matrix[1] = struct.unpack('f', reader.read(4))[0]
            placed_object.matrix[2] = struct.unpack('f', reader.read(4))[0]
            placed_object.matrix[3] = struct.unpack('f', reader.read(4))[0]
            placed_object.matrix[4] = struct.unpack('f', reader.read(4))[0]
                
            if is_new_format or is_format_ct1:
                placed_object.matrix[5] = struct.unpack('f', reader.read(4))[0]
                placed_object.matrix[6] = struct.unpack('f', reader.read(4))[0]
                placed_object.matrix[7] = struct.unpack('f', reader.read(4))[0]
                placed_object.matrix[8] = struct.unpack('f', reader.read(4))[0]
                
            placed_object.melted_flag = struct.unpack('H', reader.read(2))[0]
            placed_object.in_shadow = struct.unpack('H', reader.read(2))[0]
            placed_object.path_z = struct.unpack('f', reader.read(4))[0]

            if is_format_wr2 or is_format_ct0:
                unk13 = struct.unpack('I', reader.read(4))[0]
            
            #print(f"placed_objects[{i}].name = {placed_object.name}")
            #print(f"placed_objects[{i}].index = {placed_object.index}")
            
            self.placed_objects.append(placed_object)
            
        if is_new_format:
            # named object string pool
            named_object_string_pool_buffer = reader.read(sizeOfNamedObjectStringPool)
        
            # named object map
            for i in range(numberOfNamedObjects):
                readData_namedObject = struct.unpack('2I', reader.read(8))
            
        # markers
        # marker extra data
        for i in range(number_of_markers):
            if marker_version == 2:
                read_marker = struct.unpack('2I 2h 12f', reader.read(60))
                
                marker = MoxMarkerV3()
                marker.type = read_marker[0]
                marker.extraOffset = read_marker[1]
                marker.options = read_marker[2]
                marker.partIndex = read_marker[3]
                marker.matrix = [
                        [ read_marker[4],  read_marker[5],  read_marker[6] ],
                        [ read_marker[7],  read_marker[8],  read_marker[9] ],
                        [ read_marker[10], read_marker[11], read_marker[12] ],
                        [ read_marker[13], read_marker[14], read_marker[15] ],
                    ]
            else:
                read_type = struct.unpack('I', reader.read(4))
                
                marker = MoxMarker()
                marker.type = read_type[0]
                    
                marker_parameters_generic = GenericParameters()
                marker_parameters_generic.deserialize(reader)
                    
                marker_parameters_class = get_marker_parameters_class(marker.type)
                marker_parameters = marker_parameters_class()
                marker_parameters.from_generic(marker_parameters_generic)
                self.marker_parameters.insert(i, marker_parameters)
                    
                read_marker = struct.unpack('2h 16f', reader.read(68))
                    
                marker.options = read_marker[0]
                marker.partIndex = read_marker[1]
                marker.matrix = [
                        [ read_marker[2],  read_marker[3],  read_marker[4],  read_marker[5] ],
                        [ read_marker[6],  read_marker[7],  read_marker[8],  read_marker[9] ],
                        [ read_marker[10], read_marker[11], read_marker[12], read_marker[13] ],
                        [ read_marker[14], read_marker[15], read_marker[16], read_marker[17] ],
                    ]
                    
            if False:
                print("")
                print("type:", marker.type)
                    
            self.markers.insert(i, marker)
                
        if marker_version == 2:
            position = reader.tell()
                
            for i in range(number_of_markers):
                marker = self.markers[i]
                
                reader.seek(position + marker.extraOffset)
                    
                marker_parameters_class = get_marker_parameters_class(marker.type)
                marker_parameters = marker_parameters_class()
                marker_parameters.deserialize(reader)
                self.marker_parameters.insert(i, marker_parameters)
                    
            reader.seek(position + size_of_marker_parameters)
                
        #self.stringSection = reader.read(stringSectionSize)

        # texture property groups
        for i in range(numberOfTexturePropertyGroups):
            readData_texturePropertyGroup = struct.unpack('64s 6H 64s 4H 4B 1I', reader.read(156))
            
            texture_property_group = QadTexturePropertyGroup()
            texture_property_group.name = readData_texturePropertyGroup[0].split(b"\x00", 1)[0].decode('latin-1')
            texture_property_group.dustPercentage = readData_texturePropertyGroup[1]
            texture_property_group.gripPercentageFront = readData_texturePropertyGroup[2]
            texture_property_group.gripPercentageRear = readData_texturePropertyGroup[3]
            texture_property_group.brakePercentage = readData_texturePropertyGroup[4]
            texture_property_group.slipMode = readData_texturePropertyGroup[5]
            texture_property_group.skidmarkType = readData_texturePropertyGroup[6]
            texture_property_group.sound = readData_texturePropertyGroup[7].split(b"\x00", 1)[0].decode('latin-1')
            texture_property_group.collisionOptions = readData_texturePropertyGroup[8]
            texture_property_group.collisionSoundType = readData_texturePropertyGroup[9]
            texture_property_group.disableShadow = readData_texturePropertyGroup[10]
            texture_property_group.disableRendering = readData_texturePropertyGroup[11]
            texture_property_group.emitter = readData_texturePropertyGroup[12]
            texture_property_group.rumbleSlow = readData_texturePropertyGroup[13]
            texture_property_group.rumbleFast = readData_texturePropertyGroup[14]
            _ = readData_texturePropertyGroup[15]
            _ = readData_texturePropertyGroup[16]
            self.texture_property_groups.insert(i, texture_property_group)
            
            print(f"texture_property_group.name = {texture_property_group.name}")
            
        for i in range(numberOfTexGroupIndices):
            self.texture_group_indices.append(struct.unpack('H', reader.read(2))[0])
            
        for i in range(numberOfSounds):
            #readData_texturePropertyGroup = struct.unpack('64s 6H 64s 4H 4B 1I', reader.read(68))
            _ = reader.read(68)

        print("Done reading QAD")
        
    def serialize(self, writer : BufferedWriter):
        print("QadFile.serialize()")
        
        number_of_chunks =  len(self.chunks)
        number_of_texture_names = len(self.textureNames)
        number_of_bump_texture_names = len(self.bumpTextureNames)
        number_of_texture_names_total = ((number_of_bump_texture_names & 0xffff) << 16) | (number_of_texture_names & 0xffff)
        number_of_object_names = len(self.object_data)
        number_of_quads =  self.number_of_quads
        number_of_polygons = self.number_of_polygons
        number_of_materials = len(self.materials)
        number_of_texture_anims = len(self.texture_anims)
        number_of_texture_property_groups = len(self.texture_property_groups)
        number_of_placed_objects = len(self.placed_objects)
        number_of_named_objects = len(self.named_object_map)
        number_of_markers = len(self.markers)
        number_of_sounds = len(self.sounds)
        
        size_of_collision_quads = self.collision_data_size
        size_of_named_object_string_pool = 0
        size_of_marker_parameters = 0
        
        print(f"number_of_texture_names = {number_of_texture_names}")
        print(f"number_of_bump_texture_names = {number_of_bump_texture_names}")
        print(f"number_of_texture_names_total = {number_of_texture_names_total}")

        writer.write(struct.pack("32I", 
            0x51554144, 
            self.version, 
            self.terrain_size_x, 
            self.terrain_size_y, 
            self.number_of_quads_x, 
            self.number_of_quads_y, 
            number_of_quads,
            number_of_chunks,
            number_of_texture_names | (number_of_bump_texture_names << 16),
            number_of_object_names,
            number_of_polygons,
            number_of_materials,
            number_of_placed_objects,
            number_of_texture_property_groups,
            size_of_collision_quads,
            (0x02 << 24) | (number_of_markers & 0x00FFFFFF),
            0x00010000,
            number_of_sounds,
            size_of_named_object_string_pool,
            number_of_named_objects,
            size_of_marker_parameters,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
        ))
        
        # texture names
        for i in range(number_of_texture_names):
            texture_name = self.textureNames[i]
            
            texture_name_encoded = texture_name.encode("latin-1")[:32]
            
            writer.write(struct.pack("32s", 
                texture_name_encoded
            ))
            
        # bump texture names
        for i in range(number_of_bump_texture_names):
            bump_texture_name = self.bumpTextureNames[i]
            
            bump_texture_name_encoded = bump_texture_name.encode("latin-1")[:32]
            
            writer.write(struct.pack("32s", 
                bump_texture_name_encoded
            ))
            
        # object names
        for i in range(number_of_object_names):
            object_data : QadObjectData = self.object_data[i]
            
            object_name_encoded = object_data.name.encode("latin-1")[:32]
            
            writer.write(struct.pack("32s", 
                object_name_encoded
            ))
            
        # object data
        for i in range(number_of_object_names):
            object_data : QadObjectData = self.object_data[i]
            
            object_kick_sound_encoded = object_data.kick_sound.encode("latin-1")[:48]
            object_bounce_sound_encoded = object_data.bounce_sound.encode("latin-1")[:48]
            
            writer.write(struct.pack("3H 7H 48s 48s", 
                object_data.type,
                object_data.kick_type,
                object_data.weight,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                object_kick_sound_encoded,
                object_bounce_sound_encoded,
            ))
        
        # quads
        for i in range(number_of_quads):
            quad : QadQuad = self.quads[i]
            
            writer.write(struct.pack("2H 1i 1I 1i 1I 4f 6h", 
                quad.quadX,
                quad.quadY,
                quad.firstFace,
                quad.numFaces,
                quad.firstChunk,
                quad.numChunks,
                quad.circumSpherePositionX,
                quad.circumSpherePositionY,
                quad.circumSpherePositionZ,
                quad.circumSphereRadius,
                quad.firstObject,
                quad.numObjects,
                quad.firstMarker,
                quad.numMarkers,
                quad.vertexBufferIndex,
                0,
            ))
        
        # collision data
        writer.write(self.collision_data)
            
        # chunks
        for i in range(number_of_chunks):
            chunk : QadChunk = self.chunks[i]
            
            writer.write(struct.pack("2L 1H 2B", 
                chunk.firstFace,
                chunk.numFaces,
                chunk.materialIndex,
                chunk.viewDistLayer,
                0,
            ))
        
        # materials
        for i in range(number_of_materials):
            material : QadMaterial = self.materials[i]
            
            writer.write(struct.pack("4H 3h 3h 4f 4f 2L", 
                material.textureNameIndices[0],
                material.textureNameIndices[1],
                material.textureNameIndices[2],
                material.textureNameIndices[3],
                material.bumpTextureNameIndices[0],
                material.bumpTextureNameIndices[1],
                material.bumpTextureNameIndices[2],
                material.materialType,
                material.textureAnimIndex,
                0,
                material.texMods[0],
                material.texMods[1],
                material.texMods[2],
                material.texMods[3],
                material.texMods[4],
                material.texMods[5],
                material.texMods[6],
                material.texMods[7],
                material.texModCrcs[0],
                material.texModCrcs[1],
            ))
            
        # texture anims
        for i in range(number_of_texture_anims):
            texture_anim : QadTexAnim = self.texture_anims[i]
            
            writer.write(struct.pack("14i", 
                texture_anim.type,
                texture_anim.mode,
                texture_anim.layers,
                texture_anim.speed,
                texture_anim.fps,
                texture_anim.step,
                texture_anim.begin,
                texture_anim.end,
                texture_anim.step_u,
                texture_anim.step_v,
                texture_anim.texture_scale_x,
                texture_anim.texture_scale_y,
                texture_anim.texture_offset_x,
                texture_anim.texture_offset_y
            ))
            
        # placed objects
        for i in range(number_of_placed_objects):
            placed_object : QadPlacedObject = self.placed_objects[i]
            
            object_name_encoded = placed_object.name.encode("latin-1")[:32]
            
            #matrix_flat = [item for sublist in placed_object.matrix for item in sublist]
            
            writer.write(struct.pack("32s 2H 8f 9f 2H 1f", 
                object_name_encoded,
                placed_object.index,
                placed_object.path_flag,
                placed_object.position_x,
                placed_object.position_y,
                placed_object.position_z,
                placed_object.rotation_x,
                placed_object.rotation_y,
                placed_object.rotation_z,
                placed_object.rotation_w,
                placed_object.scale,
                *placed_object.matrix, # *matrix_flat,
                placed_object.melted_flag,
                placed_object.in_shadow,
                placed_object.path_z
            ))
            
        # named object string pool
        # named object map
        # markers
        # (marker extra data)
            
        # texture property groups
        for i in range(number_of_texture_property_groups):
            texture_property_group : QadTexturePropertyGroup = self.texture_property_groups[i]
            
            name_encoded = texture_property_group.name.encode("latin-1")[:64]
            sound_encoded = texture_property_group.sound.encode("latin-1")[:64]
            
            writer.write(struct.pack("64s 6H 64s 4H 4B 1I", 
                name_encoded,
                texture_property_group.dustPercentage,
                texture_property_group.gripPercentageFront,
                texture_property_group.gripPercentageRear,
                texture_property_group.brakePercentage,
                texture_property_group.slipMode,
                texture_property_group.skidmarkType,
                sound_encoded,
                texture_property_group.collisionOptions,
                texture_property_group.collisionSoundType,
                texture_property_group.disableShadow,
                texture_property_group.disableRendering,
                texture_property_group.emitter,
                texture_property_group.rumbleSlow,
                texture_property_group.rumbleFast,
                0,
                0
            ))
            
        # texture group indices
        for i in range(len(self.texture_group_indices)):
            writer.write(struct.pack("H", 
                self.texture_group_indices[i]
            ))
            
        # sounds
        # ...    
        
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
        self.color = 0xffffffff
        self.specular = 0
        
class GeoTangent:
    def __init__(self):
        self.x1 = 0.0
        self.y1 = 0.0
        self.z1 = 0.0
        self.w1 = 0.0
        self.x2 = 0.0
        self.y2 = 0.0
        self.z2 = 0.0
        self.w2 = 0.0
    
class GeoTriangle:
    def __init__(self):
        self.VertexIndex1 = 0
        self.VertexIndex2 = 0
        self.VertexIndex3 = 0
        
class GeoFile:
    def __init__(self):
        self.version = 0
        self.vertexFormat = 0
        self.bufferCount = 0 # remove
        self.indexCount = 0 # remove
        self.bufferVertexCounts = []
        self.vertexBuffers = []
        self.tangent_buffers = []
        self.triangles = [] # remove
        self.indices = []
        
    def deserialize(self, reader : BufferedReader):
        print("GeoFile.deserialize()")
        
        use_tangent_2 = False # use 32 bit tangents
        
        readData_initial = struct.unpack('8I', reader.read(32))
            
        signature = readData_initial[0]
        self.version = readData_initial[1]
        self.vertexFormat = readData_initial[2]
        self.bufferCount = readData_initial[3]
        self.indexCount = readData_initial[4]
        _ = readData_initial[5]
        _ = readData_initial[6]
        _ = readData_initial[7]
            
        if True:
            print("version:", self.version)
            print("vertexFormat:", self.vertexFormat)
            print("bufferCount:", self.bufferCount)
            print("indexCount:", self.indexCount)

        for i in range(self.bufferCount):
            readData_bufferVertexCount = struct.unpack('I', reader.read(4))
            bufferVertexCount = readData_bufferVertexCount[0]
            self.bufferVertexCounts.insert(i, bufferVertexCount)
            if False:
                print("")
                print("bufferVertexCount:", bufferVertexCount)
                
        for i in range(self.bufferCount):
            vertices = []
            for j in range(self.bufferVertexCounts[i]):
                readData_vertex = struct.unpack('3f I 4f 2I', reader.read(40))
                    
                vertex = GeoVertex()
                vertex.positionX = readData_vertex[0]
                vertex.positionY = readData_vertex[1]
                vertex.positionZ = readData_vertex[2]
                vertex.normal = readData_vertex[3]
                vertex.u1 = readData_vertex[4]
                vertex.v1 = readData_vertex[5]
                vertex.u2 = readData_vertex[6]
                vertex.v2 = readData_vertex[7]
                vertex.color = readData_vertex[8]
                vertex.specular = readData_vertex[9]
                vertices.insert(j, vertex)
                        
            self.vertexBuffers.insert(i, vertices)
                        
        if self.vertexFormat > 2 or use_tangent_2:
            for i in range(self.bufferCount):
                for j in range(self.bufferVertexCounts[i]):
                    if use_tangent_2:
                        readData_uv1Tangent = struct.unpack('4f', reader.read(16))
                        readData_uv2Tangent = struct.unpack('4f', reader.read(16))
                    else:
                        readData_uv1Tangent = struct.unpack('4H', reader.read(8))
                        readData_uv2Tangent = struct.unpack('4H', reader.read(8))
            
        for i in range(self.indexCount // 3):
            readData_triangle = struct.unpack('3H', reader.read(6))
                
            triangle = GeoTriangle()
            triangle.vertexIndex1 = readData_triangle[0]
            triangle.vertexIndex2 = readData_triangle[1]
            triangle.vertexIndex3 = readData_triangle[2]
            self.triangles.insert(i, triangle)
            
        print("Done reading GEO")
        
    def serialize(self, writer : BufferedWriter):
        print("GeoFile.serialize()")
        
        number_of_vertex_buffers = len(self.vertexBuffers)
        number_of_indices = len(self.indices)
        
        writer.write(struct.pack("8I", 
            0x47454F4D, 
            self.version, 
            self.vertexFormat,
            number_of_vertex_buffers,
            number_of_indices,
            0,
            0,
            0
        ))
        
        for i in range(number_of_vertex_buffers):
            writer.write(struct.pack("I", 
                self.bufferVertexCounts[i]
            ))
            
        for i in range(number_of_vertex_buffers):
            for i2 in range(self.bufferVertexCounts[i]):
                vertex : GeoVertex = self.vertexBuffers[i][i2]
            
                writer.write(struct.pack("3f I 4f 2I", 
                    vertex.positionX,
                    vertex.positionY,
                    vertex.positionZ,
                    vertex.normal,
                    vertex.u1,
                    vertex.v1,
                    vertex.u2,
                    vertex.v2,
                    vertex.color,
                    vertex.specular
                ))
                
        if self.vertexFormat == 3:
            for i in range(number_of_vertex_buffers):
                for i2 in range(self.bufferVertexCounts[i]):
                    tangent : GeoTangent = self.tangent_buffers[i][i2]
            
                    writer.write(struct.pack("8e", 
                        tangent.x1,
                        tangent.y1,
                        tangent.z1,
                        tangent.w1,
                        tangent.x2,
                        tangent.y2,
                        tangent.z2,
                        tangent.w2
                    ))
                
        for i in range(number_of_indices):
            writer.write(struct.pack("H", 
                self.indices[i],
            ))
            
class VtxFile:
    def __init__(self):
        self.bufferCount = 64
        self.bufferVertexCounts = []
        self.vertexBuffers = []
        
    def deserialize(self, reader : BufferedReader):
        print("VtxFile.deserialize()")
        
        for i in range(self.bufferCount):
            readData_bufferVertexCount = struct.unpack('I', reader.read(4))
            bufferVertexCount = readData_bufferVertexCount[0]
            self.bufferVertexCounts.insert(i, bufferVertexCount)
            if False:
                print("")
                print("bufferVertexCount:", bufferVertexCount)
                
        for i in range(self.bufferCount):
            vertices = []
            for j in range(self.bufferVertexCounts[i]):
                readData_vertex = struct.unpack('3f I 2f 2I', reader.read(32))
                    
                vertex = GeoVertex()
                vertex.positionX = readData_vertex[0]
                vertex.positionY = readData_vertex[1]
                vertex.positionZ = readData_vertex[2]
                vertex.normal = readData_vertex[3]
                vertex.u1 = readData_vertex[4]
                vertex.v1 = readData_vertex[5]
                vertex.u2 = vertex.u1
                vertex.v2 = vertex.v1
                vertex.color = readData_vertex[6]
                vertex.specular = readData_vertex[7]
                vertices.insert(j, vertex)
                        
            self.vertexBuffers.insert(i, vertices)
            
        print("Done reading VTX")
                
class IdxFile:
    def __init__(self):
        self.indexCount = 0 # remove
        self.triangles = [] # remove
        
    def deserialize(self, reader : BufferedReader):
        print("IdxFile.deserialize()")
        
        self.indexCount = struct.unpack('I', reader.read(4))[0]
            
        if True:
            print("indexCount:", self.indexCount)

        for i in range(self.indexCount // 3):
            readData_triangle = struct.unpack('3H', reader.read(6))
                
            triangle = GeoTriangle()
            triangle.vertexIndex1 = readData_triangle[0]
            triangle.vertexIndex2 = readData_triangle[1]
            triangle.vertexIndex3 = readData_triangle[2]
            self.triangles.insert(i, triangle)
            
        print("Done reading IDX")
            
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
    
    blend = geo_vertex.color
    blendR = linear_to_srgb(((blend >> 24) & 0xFF) / 255)
    blendG = linear_to_srgb(((blend >> 16) & 0xFF) / 255)
    blendB = linear_to_srgb(((blend >> 8) & 0xFF) / 255)
    blendA = linear_to_srgb(((blend >> 0) & 0xFF) / 255)
    vertex_color_blend = (blendR, blendG, blendB, blendA)
    
    ambient = geo_vertex.specular
    ambientR = linear_to_srgb(((ambient >> 24) & 0xFF) / 255)
    ambientG = linear_to_srgb(((ambient >> 16) & 0xFF) / 255)
    ambientB = linear_to_srgb(((ambient >> 8) & 0xFF) / 255)
    ambientA = linear_to_srgb(((ambient >> 0) & 0xFF) / 255)
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

    qad_format_version: EnumProperty(
        name="QAD Version",
        description="QAD file format version",
        items=(
            ('4', "4 (since CT2)", "QAD file format as used since Crash Time 2."),
            ('3', "3 (CT1)", "QAD file format as used in Crash Time: Autobahn Pursuit."),
            ('2', "2 (Nitro)", "QAD file format as used in Alarm for Cobra 11: Nitro."),
            ('1', "1 (WR2)", "QAD file format as used in World Racing 2.")
        ),
        default='4',
    )

    def execute(self, context):
        print("ImportQad.execute() IN")
        qadFilePath = Path(self.filepath)
        geoFilePath = qadFilePath.with_suffix(".geo")
        vtxFilePath = qadFilePath.with_suffix(".vtx")
        idxFilePath = qadFilePath.with_suffix(".idx")
        textureFolderPath = qadFilePath.parent / "Textures"
        print("qadFilePath:", qadFilePath)
        print("geoFilePath:", geoFilePath)
        print("textureFolderPath:", textureFolderPath)
    
        collection = bpy.context.collection
        
        object_reference_collection = bpy.data.collections.new("Object References")
        collection.children.link(object_reference_collection)
        
        object_instance_collection = bpy.data.collections.new("Objects")
        collection.children.link(object_instance_collection)
        
        qad_format_version = int(self.qad_format_version) or 4

        qad = QadFile()
        geo = GeoFile()
        
        with qadFilePath.open('rb') as qad_file:
            qad.deserialize(qad_file, qad_format_version)

        if qad_format_version == 1:
            vtx = VtxFile()
            idx = IdxFile()
            
            with vtxFilePath.open('rb') as vtx_file:
                vtx.deserialize(vtx_file)
                
            with idxFilePath.open('rb') as idx_file:
                idx.deserialize(idx_file)
                
            geo.bufferVertexCounts = vtx.bufferVertexCounts
            geo.vertexBuffers = vtx.vertexBuffers
            geo.indexCount = idx.indexCount
            geo.triangles = idx.triangles
        else:
            with geoFilePath.open('rb') as geo_file:
                geo.deserialize(geo_file)

        loaded_textures = {}

        materials = []
        
        landscape_scale = 10.0
        
        vertex_dicts = {}
        uvs1_dicts = {}
        uvs2_dicts = {}
        vertex_colors_blend_dicts = {}
        vertex_colors_ambient_dicts = {}
        
        bm = bmesh.new()
    
        uv_layer1 = bm.loops.layers.uv.new("UV1")
        uv_layer2 = bm.loops.layers.uv.new("UV2")
        
        uv_layer_names = [uv_layer1.name, uv_layer2.name]
        
        color_layer_blend = bm.loops.layers.color.new("Color")
        color_layer_ambient = bm.loops.layers.color.new("Specular")
    
        mesh = bpy.data.meshes.new(name=f"Scenario Mesh")
        
        for i in range(len(qad.texture_property_groups)):
            texture_property_group : QadTexturePropertyGroup = qad.texture_property_groups[i]
            
            texture_property_group_properties : QadTexturePropertyGroupProperties = context.scene.qad_texture_property_group_list.add()
            
            texture_property_group_properties.name = texture_property_group.name
            texture_property_group_properties.dust = texture_property_group.dustPercentage
            texture_property_group_properties.grip_front = texture_property_group.gripPercentageFront
            texture_property_group_properties.grip_rear = texture_property_group.gripPercentageRear
            texture_property_group_properties.brake = texture_property_group.brakePercentage
            texture_property_group_properties.slip_mode = texture_property_group.slipMode
            texture_property_group_properties.skidmark_type_black = (texture_property_group.skidmarkType & 1) == 1
            texture_property_group_properties.skidmark_type_colored = ((texture_property_group.skidmarkType >> 1) & 1) == 1
            texture_property_group_properties.sound = texture_property_group.sound
            texture_property_group_properties.collision_options = texture_property_group.collisionOptions
            texture_property_group_properties.collision_sound_type = texture_property_group.collisionSoundType
            texture_property_group_properties.enable_shadow = not texture_property_group.disableShadow
            texture_property_group_properties.enable_render = not texture_property_group.disableRendering
            texture_property_group_properties.emitter = texture_property_group.emitter
            texture_property_group_properties.rumble_slow = texture_property_group.rumbleSlow
            texture_property_group_properties.rumble_fast = texture_property_group.rumbleFast
        
        for i in range(len(qad.object_data)):
            object_data : QadObjectData = qad.object_data[i]
            
            object_data_properties : QadObjectDataProperties = context.scene.qad_object_data_list.add()
            object_data_properties.name = object_data.name
            object_data_properties.type = object_data.type
            object_data_properties.kick_type = object_data.kick_type
            object_data_properties.weight = object_data.weight
            object_data_properties.kick_sound = object_data.kick_sound
            object_data_properties.bounce_sound = object_data.bounce_sound

        for i in range(len(qad.materials)):
            qadMaterial : QadMaterial = qad.materials[i]
            
            qad_material_type = qadMaterial.materialType >> 4

            material_name = f"Material {i} {qad_material_type}"
            
            print(f"material_name = {material_name}")
            
            print(f"qadMaterial.textureNameIndices = {qadMaterial.textureNameIndices}")
            print(f"qadMaterial.bumpTextureNameIndices = {qadMaterial.bumpTextureNameIndices}")
            
            textureNames = [None, None, None, None]
            bumpTextureNames = [None, None, None]
            
            if len(qad.textureNames) > 0:
                for j in range(len(qadMaterial.textureNameIndices)):
                    textureNameIndex = qadMaterial.textureNameIndices[j]
                    if textureNameIndex != 0:
                        textureNames[j] = qad.textureNames[textureNameIndex]
                
                if len(qad.bumpTextureNames) > 0:
                    for j in range(len(qadMaterial.bumpTextureNameIndices)):
                        bumpTextureNameIndex = qadMaterial.bumpTextureNameIndices[j]
                        if bumpTextureNameIndex != -1:
                            bumpTextureNames[j] = qad.bumpTextureNames[bumpTextureNameIndex]
                
            if textureNames[0]:
                material_name += f" {textureNames[0]}"

            material = bpy.data.materials.new(name=material_name)
            
            all_texture_names = textureNames + bumpTextureNames
            
            for j in range(len(all_texture_names)):
                texture_name = all_texture_names[j]
                
                if not texture_name:
                    continue
                
                is_bump = texture_name in bumpTextureNames
                
                texture_slot_index = 0
                texture_property_name = ""
                
                if is_bump:
                    texture_slot_index = j - len(textureNames)
                    texture_property_name = f"bump_texture_{texture_slot_index + 1}"
                else:
                    texture_slot_index = j
                    texture_property_name = f"texture_{texture_slot_index + 1}"
                
                texture_file_path = textureFolderPath / f"{texture_name}.tga"
            
                loaded_texture = None

                if texture_name in loaded_textures:
                    loaded_texture = loaded_textures[texture_name]
                else:
                    loaded_texture = bpy.data.textures.new(name=texture_name, type='IMAGE')
                    loaded_texture.use_fake_user = True
                    
                    if texture_file_path.exists():
                        image = bpy.data.images.load(str(texture_file_path))
                        #image.use_fake_user = True
                        
                        if is_bump:
                            image.colorspace_settings.name = 'Non-Color'
                
                        loaded_texture.image = image
                        
                        if not is_bump:
                            texture_name_index = qad.textureNames.index(texture_name)
                            texture_property_group_index = qad.texture_group_indices[texture_name_index] # TODO
                            #texture_property_group_name = qad.texture_property_groups[texture_property_group_index].name
                            loaded_texture.qad_texture_properties.texture_properties_group = f"{texture_property_group_index}"
            
                    loaded_textures[texture_name] = loaded_texture
                    
                print(f"{texture_property_name} = {loaded_texture} ({texture_name})")
                material.qad_material_properties[texture_property_name] = loaded_texture
                
            material.qad_material_properties.enabled = True
            material.qad_material_properties.type = MaterialType(qad_material_type).name
            
            tex_mod_1 = qadMaterial.texMods[0:4]
            tex_mod_2 = qadMaterial.texMods[4:8]
            
            # texture_1_scale = tex_mod_1[2]
            # texture_2_scale = tex_mod_2[2]
            
            # # TxScale = 100 + (math.log(texture_1_scale * 480.0) / math.log(2.0)) * 20.0
            # # TxScale2 = 100 + (math.log(texture_2_scale * 480.0) / math.log(2.0)) * 20.0
            
            # # Lx = (TxScale - 100) / 20.0
            # # L = math.exp(Lx * math.log(2.0)) / 480.0

            # # Ax = (TxScale2 - 100) / 20.0
            # # A = math.exp(Ax * math.log(2.0)) / 480.0
            
            # # remapped_texture_1_scale = L
            # # remapped_texture_2_scale = A
            
            # # print(f"[1] {texture_1_scale} -> {TxScale} -> ({Lx}) {remapped_texture_1_scale}")
            # # print(f"[2] {texture_2_scale} -> {TxScale2} -> ({Ax}) {remapped_texture_2_scale}")
            
            # remapped_texture_1_scale = texture_1_scale# / landscape_scale
            # remapped_texture_2_scale = texture_2_scale# / landscape_scale
            
            # material.qad_material_properties.texture_1_offset = (tex_mod_1[0], tex_mod_1[1])
            # material.qad_material_properties.texture_1_scale = (remapped_texture_1_scale, remapped_texture_1_scale)
            
            # material.qad_material_properties.texture_2_offset = (tex_mod_2[0], tex_mod_2[1])
            # material.qad_material_properties.texture_2_scale = (remapped_texture_2_scale, remapped_texture_2_scale)
            
            material.qad_material_properties.texture_1_offset = (tex_mod_1[0], tex_mod_1[1])
            material.qad_material_properties.texture_1_scale = (tex_mod_1[2], tex_mod_1[2])
            
            material.qad_material_properties.texture_2_offset = (tex_mod_2[0], tex_mod_2[1])
            material.qad_material_properties.texture_2_scale = (tex_mod_2[2], tex_mod_2[2])
            
            material.qad_material_properties.setup(material, uv_layer_names)
            
            materials.insert(i, material)
            
            mesh.materials.append(material)
        
        for h in range(len(qad.quads)):
            qad_quad : QadQuad = qad.quads[h]
            #print("Iterating quad", h)
            
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
                
                chunk_material_index = qad_chunk.materialIndex

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

                        face.material_index = chunk_material_index
        
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        
        scenario_obj = bpy.data.objects.new("Scenario", mesh)
        
        collection.objects.link(scenario_obj)
        
        bm.to_mesh(mesh)
        bm.free()
        
        mesh.normals_split_custom_set_from_vertices([v.normal for v in mesh.vertices])
    
        if bpy.app.version < (4, 1, 0):
            mesh.use_auto_smooth = True
    
        mesh.update()
        
        object_instances = {}
        object_skip_instances = []
        loaded_objects_counter = 0

        for i in range(len(qad.placed_objects)):
            qad_placed_object : QadPlacedObject = qad.placed_objects[i]
            
            #print(f"qad_placed_object.name = {qad_placed_object.name}")
            
            qad_object_data : QadObjectData = qad.object_data[qad_placed_object.index]
            
            #print(f"qad_object_data.name = {qad_object_data.name}")

            qad_object_data_name = qad_object_data.name
            
            if qad_object_data_name in object_skip_instances:
                continue
            
            if qad_object_data_name.startswith("X\\"):
                continue

            if qad_object_data_name not in object_instances:
                texture_folder_path = qadFilePath.parent / "Textures"
                object_file_path = qadFilePath.parent / "Objects" / f"{qad_object_data_name}.mox"
                
                try:
                    mox_obj = import_mox(object_file_path, texture_folder_path, object_reference_collection)
                    object_instances[qad_object_data_name] = mox_obj
                    loaded_objects_counter += 1
                except:
                    print(f"Failed to load object: {qad_object_data_name}") 
                    object_skip_instances.append(qad_object_data_name)
                    continue
                
            object_ref = object_instances[qad_object_data_name]
                
            instance = create_instance_hierarchy(object_ref, object_instance_collection)
            
            instance.qad_object_properties.qad_object_dataset = f"{qad_placed_object.index}"

            instance.location = Vector((qad_placed_object.position_x, qad_placed_object.position_z, qad_placed_object.position_y)) / landscape_scale
            
            input_quaternion = Quaternion((-qad_placed_object.rotation_w, qad_placed_object.rotation_x, qad_placed_object.rotation_y, qad_placed_object.rotation_z))
            
            instance.rotation_mode = 'QUATERNION'
            instance.rotation_quaternion = swap_yz_axes_of_quaternion(input_quaternion)
            instance.rotation_mode = 'XZY'
            
            instance.scale = Vector((qad_placed_object.scale, qad_placed_object.scale, qad_placed_object.scale))

        print(f"ImportQad.execute() loaded_objects_counter = {loaded_objects_counter}")
        print(f"ImportQad.execute() len(qad.placed_objects) = {len(qad.placed_objects)}")
        print(f"ImportQad.execute() len(qad.object_data) = {len(qad.object_data)}")

        print("ImportQad.execute() OUT")

        return {'FINISHED'}
    
    def execute2(self, context):
        print("ImportQad.execute() IN")
        qadFilePath = Path(self.filepath)
        geoFilePath = qadFilePath.with_suffix(".geo")
        textureFolderPath = qadFilePath.parent / "Textures"
        print("qadFilePath:", qadFilePath)
        print("geoFilePath:", geoFilePath)
        print("textureFolderPath:", textureFolderPath)

        qad = QadFile()
        geo = GeoFile()
        
        with qadFilePath.open('rb') as qad_file:
            qad.deserialize(qad_file)
        
        with geoFilePath.open('rb') as geo_file:
            geo.deserialize(geo_file)
        
        landscape_scale = 10.0
        
        for i in range(len(geo.vertexBuffers)):
        
            buffer_length = geo.bufferVertexCounts[i]
            
            if buffer_length < 1:
                continue
            
            bm = bmesh.new()
            
            for i2 in range(buffer_length):
                vertex : GeoVertex = geo.vertexBuffers[i][i2]
                
                position = Vector((vertex.positionX, vertex.positionZ, vertex.positionY)) / landscape_scale

                bm.verts.new(position)

            mesh = bpy.data.meshes.new(name=f"Vertex Buffer {i} Mesh")
            obj = bpy.data.objects.new(f"Vertex Buffer {i}", mesh)
        
            bpy.context.collection.objects.link(obj)
        
            bm.to_mesh(mesh)
            bm.free()
        
            #mesh.normals_split_custom_set_from_vertices([v.normal for v in mesh.vertices])
    
            #mesh.use_auto_smooth = True
    
            mesh.update()
        
        print("ImportQad.execute() OUT")

        return {'FINISHED'}

class ExportQad(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export_landscape.scenario"
    bl_label = "Export Scenario"

    filename_ext = ".qad"

    filter_glob: StringProperty(
        default="*.qad",
        options={'HIDDEN'},
        maxlen=255
    )

    qad_format_version: EnumProperty(
        name="Version",
        description="Target QAD format version",
        items=(
            ('4', "4", "Placeholder (CT5)"),
        ),
        default='4',
    )

    def execute(self, context):
        print("ExportQad.execute() IN")
        qad_file_path = Path(self.filepath)
        geo_file_path = qad_file_path.with_suffix(".geo")
        texture_folder_path = qad_file_path.parent / "Textures"
        print("qad_file_path:", qad_file_path)
        print("geo_file_path:", geo_file_path)
        print("texture_folder_path:", texture_folder_path)
        
        qad = QadFile()
        geo = GeoFile()
        
        landscape_scale = 10.0
        
        root_objs = []
        placed_objs = []
        
        for obj in bpy.context.scene.collection.all_objects:
            if obj.parent is None and (obj.select_get() and not obj.hide_select):
                if hasattr(obj, "qad_object_properties") and obj.qad_object_properties.qad_object_dataset != "NONE":
                    placed_objs.append(obj)
                elif obj.type == 'MESH':
                    root_objs.append(obj)
                
        print(f"placed_objs = {placed_objs}")
                    
        ctx = bpy.context.copy()

        ctx['active_object'] = root_objs[0]
        ctx['selected_objects'] = root_objs
        
        if len(root_objs) > 1:
            bpy.ops.object.join(ctx)

        scenario_obj = ctx['active_object']
        
        c_data = CData()
        c_data.LoadTerrainFile(context.scene, scenario_obj, placed_objs, landscape_scale)
        c_data.DoExportToXbox(False, True)
        
        BumpRemap = [0 for _ in range(c_data.TEXTURES_NUM)]
        MaxBump = 0
        MaxChunk = 0
        MaxChunk2 = 0
        NamedObjBufSize = 0
        NamedObjCount = 0

        for i in range(c_data.FacesTexChunksNum2):
            if c_data.FacesTexChunksPtr2[i].fcChunk > MaxChunk2:
                MaxChunk2 = c_data.FacesTexChunksPtr2[i].fcChunk
                
        MaxChunk2 += 1
        #
        RemapChunk = [0 for _ in range(MaxChunk2)]
        
        for i in range(c_data.FacesTexChunksNum2):
            RemapChunk[c_data.FacesTexChunksPtr2[i].fcChunk] = 1
            
        i = 0
        i2 = -1
        MaxChunk = 0
        
        while i < MaxChunk2:
            if RemapChunk[i] == 0:
                RemapChunk[i] = -1
                continue
            
            if i2 >= 0:
                skip = True
                
                # check if two following chunks are equal (only engine relevant data)
                
                for j in range(4):
                    if skip and (c_data.FacesTexChunksPtr[i].fcTextures[j] != c_data.FacesTexChunksPtr[i2].fcTextures[j]):
                        skip = False
                        
                if skip and ((c_data.FacesTexChunksPtr[i].fcTyp >> 4) != (c_data.FacesTexChunksPtr[i2].fcTyp >> 4)):
                    skip = False
                    
                if skip and (c_data.FacesTexChunksPtr[i].fcTexAni != c_data.FacesTexChunksPtr[i2].fcTexAni):
                    skip = False
                    
                for j in range(4 * 2):
                    if skip and (c_data.FacesTexChunksPtr[i].fcTexMod[j] != c_data.FacesTexChunksPtr[i2].fcTexMod[j]):
                        skip = False
                        
                #
                #
                #
                
                if skip:
                    RemapChunk[i] = RemapChunk[i2]
                    continue
                
            RemapChunk[i] = MaxChunk
            MaxChunk += 1
            i2 = i
            
            i += 1 # TODO
        
        print(f"MaxChunk = {MaxChunk}")
        print(f"MaxChunk2 = {MaxChunk2}")

        #
        for i in range(c_data.LedMaterialsNum):
            BumpRemap[i] = -1
            
        for i in range(c_data.LedMaterialsNum):
            if c_data.LedMaterialsList[i].lmTexObj2 != None:
                BumpRemap[i] = MaxBump
                MaxBump += 1
                
        # --- TODO

        geo_buffer_count = len(c_data.VxBufDriveSizes)
        tex_anim_count = len(c_data.TexAniData)

        # geo
        use_tangents = True # TODO

        geo.version = 0x00010004
        geo.bufferVertexCounts = [0 for _ in range(geo_buffer_count)]
        geo.vertexBuffers = [[] for _ in range(geo_buffer_count)]
        
        if use_tangents:
            geo.vertexFormat = 3
            geo.tangent_buffers = [[] for _ in range(geo_buffer_count)]
        else:
            geo.vertexFormat = 2
            geo.tangent_buffers = []
            
        for i in range(geo_buffer_count):
            for i2 in range(c_data.VxBufDriveSizes[i]):
                c_vertex : MyVtxStructE = c_data.VxBufDrive[i][i2]
                c_tangent : MyTang1 = c_data.VxBufDrive2[i][i2]
                
                geo_vertex = GeoVertex()
                geo_vertex.positionX = c_vertex.x
                geo_vertex.positionY = c_vertex.y
                geo_vertex.positionZ = c_vertex.z
                geo_vertex.normal = c_vertex.normal
                geo_vertex.u1 = c_vertex.tu
                geo_vertex.v1 = c_vertex.tv
                geo_vertex.u2 = c_vertex.tu2
                geo_vertex.v2 = c_vertex.tv2
                geo_vertex.color = c_vertex.color
                geo_vertex.specular = c_vertex.specular
                geo.vertexBuffers[i].append(geo_vertex)
                
                if use_tangents:
                    geo_tangent = GeoTangent()
                    geo_tangent.x1 = c_tangent.tx1
                    geo_tangent.y1 = c_tangent.ty1
                    geo_tangent.z1 = c_tangent.tz1
                    geo_tangent.w1 = c_tangent.tw1
                    geo_tangent.x2 = c_tangent.tx2
                    geo_tangent.y2 = c_tangent.ty2
                    geo_tangent.z2 = c_tangent.tz2
                    geo_tangent.w2 = c_tangent.tw2
                    geo.tangent_buffers[i].append(geo_tangent)
                
                geo.bufferVertexCounts[i] += 1
        
        geo.indices = c_data.IxBuf2
        
        with geo_file_path.open('wb') as geo_writer:
            geo.serialize(geo_writer)
            
        #return {'FINISHED'} # TODO
    
        # qad
        qad.version = 0x00010001
        qad.terrain_size_x = c_data.TerrainSizeX
        qad.terrain_size_y = c_data.TerrainSizeY
        qad.number_of_quads_x = c_data.QuadsNumX
        qad.number_of_quads_y = c_data.QuadsNumY
        qad.number_of_quads = c_data.QuadsNum
        qad.number_of_polygons = c_data.Indices1Num // 3
        qad.collision_data = c_data.CollQuadsData
        qad.collision_data_size = c_data.CollQuadsDataSize
        
        for i in range(c_data.LedMaterialsNum):
            c_material : LedMaterial = c_data.LedMaterialsList[i]
            
            qad_texture_name = c_material.lmTexName1
            qad.textureNames.append(qad_texture_name)
            
        for i in range(c_data.LedMaterialsNum):
            c_material : LedMaterial = c_data.LedMaterialsList[i]
            
            if c_material.lmTexObj2 != None:
                qad_texture_name = c_material.lmTexName1
                qad_bump_texture_name = f"{qad_texture_name}_bump"
                qad.bumpTextureNames.append(qad_bump_texture_name)
            
        for i in range(c_data.LedObjectsTotal):
            c_object_data : LedObject = c_data.LedObjectsList[i]
            
            qad_object_data = QadObjectData()
            qad_object_data.name = c_object_data.loObjName
            qad_object_data.type = c_object_data.loObjectType
            qad_object_data.kick_type = c_object_data.loKickType
            qad_object_data.weight = c_object_data.loObjWeight
            qad_object_data.kick_sound = c_object_data.loKickSound
            qad_object_data.bounce_sound = c_object_data.loBounceSound
            qad.object_data.append(qad_object_data)
            
        for i in range(c_data.LedObjectsSetNum):
            c_placed_object : LedObjectPos = c_data.LedObjectPosList[i]
            
            qad_placed_object = QadPlacedObject()
            qad_placed_object.name = c_placed_object.lpObjName
            qad_placed_object.index = c_placed_object.lpObjIndex
            qad_placed_object.path_flag = c_placed_object.lpPathFlag
            qad_placed_object.position_x = c_placed_object.lpXpos
            qad_placed_object.position_y = c_placed_object.lpYpos
            qad_placed_object.position_z = c_placed_object.lpZpos
            qad_placed_object.rotation_x = c_placed_object.lpOrientation[0]
            qad_placed_object.rotation_y = c_placed_object.lpOrientation[1]
            qad_placed_object.rotation_z = c_placed_object.lpOrientation[2]
            qad_placed_object.rotation_w = c_placed_object.lpOrientation[3]
            qad_placed_object.scale = c_placed_object.lpScale
            qad_placed_object.matrix = c_placed_object.lpObjMatrix
            qad_placed_object.melted_flag = c_placed_object.lpMeltedFlag
            qad_placed_object.in_shadow = c_placed_object.lpInShadow
            qad_placed_object.path_z = c_placed_object.lpPathZ
            qad.placed_objects.append(qad_placed_object)
            
        for i in range(c_data.QuadsNum):
            c_quad = c_data.TerrainQuadList[i]
            
            qad_quad = QadQuad()
            qad_quad.quadX = c_quad.qiQuadX
            qad_quad.quadY = c_quad.qiQuadY
            qad_quad.circumSpherePositionX = c_quad.qiMidX
            qad_quad.circumSpherePositionY = c_quad.qiMidY
            qad_quad.circumSpherePositionZ = c_quad.qiMidZ
            qad_quad.circumSphereRadius = c_quad.qiRadius
            qad_quad.firstFace = c_quad.qiStartIndex
            qad_quad.numFaces = c_quad.qiPolysNum
            qad_quad.firstChunk = c_quad.qiChunk1
            qad_quad.numChunks = c_quad.qiChunksNum
            qad_quad.firstMarker = c_quad.qiLight1
            qad_quad.numMarkers = c_quad.qiLightsNum
            qad_quad.firstObject = c_quad.qiObject1
            qad_quad.numObjects = c_quad.qiObjectsNum
            qad_quad.vertexBufferIndex = c_quad.qiVxBufIndex
            qad.quads.append(qad_quad)
            
        # "Quad-Chunks"
        for i in range(c_data.FacesTexChunksNum2):
            c_chunk : FaceMatChunk = c_data.FacesTexChunksPtr2[i]
            
            qad_chunk = QadChunk()
            qad_chunk.firstFace = c_chunk.fcFirstPoly
            qad_chunk.numFaces = c_chunk.fcNumPolys
            qad_chunk.materialIndex = RemapChunk[c_chunk.fcChunk]
            qad_chunk.viewDistLayer = c_chunk.fcGeoLayer
            qad.chunks.append(qad_chunk)
            
        # "Tex-Chunks"
        qad.materials = [QadMaterial() for _ in range(MaxChunk)]

        for i in range(MaxChunk2):
            j = RemapChunk[i]
            
            if j < 0:
                continue
            
            qad.materials[j].materialType = c_data.FacesTexChunksPtr[i].fcTyp
            qad.materials[j].textureAnimIndex = c_data.FacesTexChunksPtr[i].fcTexAni
            
            for i2 in range(4):
                qad.materials[j].textureNameIndices[i2] = c_data.FacesTexChunksPtr[i].fcTextures[i2]
                
            for i2 in range(3):
                qad.materials[j].bumpTextureNameIndices[i2] = BumpRemap[c_data.FacesTexChunksPtr[i].fcTextures[i2]]
                
            for i2 in range(4 * 2):
                qad.materials[j].texMods[i2] = c_data.FacesTexChunksPtr[i].fcTexMod[i2]
                
            for i2 in range(2):
                qad.materials[j].texModCrcs[i2] = c_data.FacesTexChunksPtr[i].fcTMCRC[i2]
            
        for i in range(tex_anim_count):
            c_tex_anim : TexAniItem = c_data.TexAniData[i]
            
            qad_tex_anim = QadTexAnim()
            qad_tex_anim.type = c_tex_anim.Typ
            qad_tex_anim.mode = c_tex_anim.Mode
            qad_tex_anim.layers = c_tex_anim.Layers
            qad_tex_anim.speed = c_tex_anim.Speed
            qad_tex_anim.fps = c_tex_anim.Fps
            qad_tex_anim.step = c_tex_anim.Step
            qad_tex_anim.begin = c_tex_anim.Begin
            qad_tex_anim.end = c_tex_anim.End
            qad_tex_anim.step_u = c_tex_anim.StepU
            qad_tex_anim.step_v = c_tex_anim.StepV
            qad_tex_anim.texture_scale_x = c_tex_anim.TexScaleX
            qad_tex_anim.texture_scale_y = c_tex_anim.TexScaleY
            qad_tex_anim.texture_offset_x = c_tex_anim.TexOffsX
            qad_tex_anim.texture_offset_y = c_tex_anim.TexOffsY
            qad.texture_anims.append(qad_tex_anim)
            
        for i in range(len(context.scene.qad_texture_property_group_list)):
            texture_property_group_properties : QadTexturePropertyGroupProperties = context.scene.qad_texture_property_group_list[i]
            
            qad_texture_property_group = QadTexturePropertyGroup()
            qad_texture_property_group.name = texture_property_group_properties.name
            qad_texture_property_group.dustPercentage = texture_property_group_properties.dust
            qad_texture_property_group.gripPercentageFront = texture_property_group_properties.grip_front
            qad_texture_property_group.gripPercentageRear = texture_property_group_properties.grip_rear
            qad_texture_property_group.brakePercentage = texture_property_group_properties.brake
            qad_texture_property_group.slipMode = texture_property_group_properties.slip_mode
            qad_texture_property_group.skidmarkType = (texture_property_group_properties.skidmark_type_colored << 1) | (texture_property_group_properties.skidmark_type_black & 1)
            qad_texture_property_group.sound = texture_property_group_properties.sound
            qad_texture_property_group.collisionOptions = texture_property_group_properties.collision_options
            qad_texture_property_group.collisionSoundType = texture_property_group_properties.collision_sound_type
            qad_texture_property_group.disableShadow = not texture_property_group_properties.enable_shadow
            qad_texture_property_group.disableRendering = not texture_property_group_properties.enable_render
            qad_texture_property_group.emitter = texture_property_group_properties.emitter
            qad_texture_property_group.rumbleSlow = texture_property_group_properties.rumble_slow
            qad_texture_property_group.rumbleFast = texture_property_group_properties.rumble_fast
            qad.texture_property_groups.append(qad_texture_property_group)
            
            # TODO
            print(f"texture_property_group_properties.dust = {texture_property_group_properties.dust}")
            print(f"qad_texture_property_group.dustPercentage = {qad_texture_property_group.dustPercentage}")
            
        qad.texture_group_indices = c_data.TexData

        with qad_file_path.open('wb') as qad_writer:
            qad.serialize(qad_writer)

        print("ExportQad.execute() OUT")

        return {'FINISHED'}
    
def menu_func_import(self, context):
    self.layout.operator(ImportQad.bl_idname, text="Landscape Scenario (.qad)")

def menu_func_export(self, context):
    self.layout.operator(ExportQad.bl_idname, text="Landscape Scenario (.qad)")
    
def register():
    bpy.utils.register_class(ImportQad)
    bpy.utils.register_class(ExportQad)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(ImportQad)
    bpy.utils.unregister_class(ExportQad)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)