import bpy
import bpy_extras
import bmesh
import struct
import math
import io
import os
import numpy as np

from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from mathutils import Vector, Matrix
from math import radians, degrees
from typing import List

from pathlib import Path
from io import BufferedReader, BufferedWriter

from .MoxPanels import *
from .Markers import *
from .utils import *
from .globals import *

from .MoxMaterials import *

tex_property_names = ["Tex1Name", "Tex2Name", "Tex3Name"]
          
material_color_keys = {
    'diffuse':   'Diffuse',
    'ambient':   'Ambient',
    'specular':  'Specular',
    'reflect2':  'Reflect2',
    'specular2': 'Specular2',
    'xdiffuse':  'XDiffuse',
    'xspecular': 'XSpecular',
}

def unpack_color(packed):
    return (
        ((packed >> 16) & 0xFF) / 255.0,
        ((packed >> 8)  & 0xFF) / 255.0,
        (packed         & 0xFF) / 255.0,
    )

def pack_color(unpacked):
    rgb = 0
    rgb |= int(unpacked[2] * 255.0) & 0xFF
    rgb |= (int(unpacked[1] * 255.0) & 0xFF) << 8
    rgb |= (int(unpacked[0] * 255.0) & 0xFF) << 16
    return rgb & 0xFFFFFF

class MoxFile:
    def __init__(self):
        self.options = 0
        self.version = 0
        self.vertices = []
        self.tangents = []
        self.triangles = []
        self.chunks = []
        self.materials = []
        self.parts = []
        self.markers = []
        self.markerParameters = []
        self.stringSection = []
        self.reservedSection1 = []
        self.reservedSection2 = []
        
    def deserialize(self, reader : BufferedReader):
        print("MoxFile.deserialize()")
        
        readData_initial = struct.unpack('1I 2H 6I', reader.read(32))
            
        signature = readData_initial[0]
        options = readData_initial[1]
        version = readData_initial[2]
        numberOfVertices = readData_initial[3]
        numberOfTriangles = readData_initial[4]
        numberOfChunks = readData_initial[5]
        numberOfMaterials = readData_initial[6]
        numberOfParts = readData_initial[7]
        numberOfMarkers = readData_initial[8]
            
        use_big_indices = (options & 1) == 1
        use_tangents = ((options >> 1) & 1) == 1

        self.options = options
        self.version = version

        if True:
            print("use_big_indices:", use_big_indices)
            print("use_tangents:", use_tangents)
                
        markerParametersSize = 0
        stringSectionSize = 0
        reservedSectionSize1 = 0
        reservedSectionSize2 = 0
            
        if self.version == 0x0203:
            readData_extra = struct.unpack('4I', reader.read(16))
                
            markerParametersSize = readData_extra[0]
            stringSectionSize = readData_extra[1]
            reservedSectionSize1 = readData_extra[2]
            reservedSectionSize2 = readData_extra[3]
                
            if True:
                print("markerParametersSize:", markerParametersSize)
                print("stringSectionSize:", stringSectionSize)
                print("reservedSectionSize1:", reservedSectionSize1)
                print("reservedSectionSize2:", reservedSectionSize2)

        for i in range(numberOfVertices):
            readData_vertex = struct.unpack('6f 4f', reader.read(40))
                    
            vertex = MoxVertex()
            vertex.positionX = readData_vertex[0]
            vertex.positionY = readData_vertex[1]
            vertex.positionZ = readData_vertex[2]
            vertex.normalX = readData_vertex[3]
            vertex.normalY = readData_vertex[4]
            vertex.normalZ = readData_vertex[5]
            vertex.u1 = readData_vertex[6]
            vertex.v1 = readData_vertex[7]
            vertex.u2 = readData_vertex[8]
            vertex.v2 = readData_vertex[9]
            self.vertices.insert(i, vertex)
                
        if use_tangents:
            for i in range(numberOfVertices):
                read_tangent = struct.unpack('8H', reader.read(16))
                    
                tangent = MoxTangent()
                tangent.uv1 = [ read_tangent[0], read_tangent[1], read_tangent[2], read_tangent[3] ]
                tangent.uv2 = [ read_tangent[4], read_tangent[5], read_tangent[6], read_tangent[7] ]
                self.tangents.insert(i, tangent)

        for i in range(numberOfTriangles):
            if use_big_indices:
                readData_triangle = struct.unpack('3I', reader.read(12))
            else:
                readData_triangle = struct.unpack('3H', reader.read(6))
                
            triangle = MoxTriangle()
            triangle.vertexIndex1 = readData_triangle[0]
            triangle.vertexIndex2 = readData_triangle[1]
            triangle.vertexIndex3 = readData_triangle[2]
            self.triangles.insert(i, triangle)
                
        for i in range(numberOfChunks):
            if True: # ?
                readData_chunk = struct.unpack('6I', reader.read(24))
            else:
                readData_chunk = struct.unpack('6H', reader.read(12))
                    
            chunk = MoxChunk()
            chunk.materialIndex = readData_chunk[0]
            chunk.materialId = readData_chunk[1]
            chunk.firstTriangle = readData_chunk[2]
            chunk.triangleCount = readData_chunk[3]
            chunk.firstVertex = readData_chunk[4]
            chunk.lastVertex = readData_chunk[5]
            self.chunks.insert(i, chunk)
                
            if False:
                print("")
                print("materialIndex:", chunk.materialIndex)
                print("materialId:", chunk.materialId)
                
        for i in range(numberOfMaterials):
            readData_material = struct.unpack('I 76s 64s 64s 64s 64s', reader.read(336))
                    
            material = MoxMaterial()
            material.id = readData_material[0]
            self.materials.insert(i, material)
                
            if False:
                print("")
                print("id:", material.id)
                    
        for i in range(numberOfParts):
            readData_part = struct.unpack('64s 16f 4h 2H 4f 4H 6f 2I', reader.read(196))
                
            part = MoxPart()
            part.name = readData_part[0].split(b"\x00", 1)[0].decode('latin-1')
            part.matrix = [
                    [ readData_part[1],  readData_part[2],  readData_part[3],  readData_part[4] ],
                    [ readData_part[5],  readData_part[6],  readData_part[7],  readData_part[8] ],
                    [ readData_part[9],  readData_part[10], readData_part[11], readData_part[12] ],
                    [ readData_part[13], readData_part[14], readData_part[15], readData_part[16] ],
                ]
            part.parent = readData_part[17]
            part.child = readData_part[18]
            part.prevInLevel = readData_part[19]
            part.nextInLevel = readData_part[20]
            part.firstChunk = readData_part[21]
            part.chunkCount = readData_part[22]
            part.midX = readData_part[23]
            part.midY = readData_part[24]
            part.midZ = readData_part[25]
            part.radius = readData_part[26]
            part.w1 = readData_part[27]
            part.w2 = readData_part[28]
            part.w3 = readData_part[29]
            part.typeId = readData_part[30]
            part.x1 = readData_part[31]
            part.x2 = readData_part[32]
            part.y1 = readData_part[33]
            part.y2 = readData_part[34]
            part.z1 = readData_part[35]
            part.z2 = readData_part[36]
            part.options = readData_part[37]
            part.w5 = readData_part[38]
            self.parts.insert(i, part)
                
            if False:
                print("")
                print("name:", part.name)
                print("parent:", part.parent)
                print("child:", part.child)
                print("prevInLevel:", part.prevInLevel)
                print("nextInLevel:", part.nextInLevel)
                print("firstMaterial:", part.firstMaterial)
                print("materialCount:", part.materialCount)
                    
        for i in range(numberOfMarkers):
            if self.version == 0x0203:
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
                self.markerParameters.insert(i, marker_parameters)
                    
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
                
        if self.version == 0x0203:
            position = reader.tell()
                
            for i in range(numberOfMarkers):
                marker = self.markers[i]
                
                reader.seek(position + marker.extraOffset)
                    
                marker_parameters_class = get_marker_parameters_class(marker.type)
                marker_parameters = marker_parameters_class()
                marker_parameters.deserialize(reader)
                self.markerParameters.insert(i, marker_parameters)
                    
            reader.seek(position + markerParametersSize)
                
            self.stringSection = reader.read(stringSectionSize)
            self.reservedSection1 = reader.read(reservedSectionSize1)
            self.reservedSection2 = reader.read(reservedSectionSize2)
            
        print("Done reading MOX")
        
    def serialize(self, writer : BufferedWriter):
        print("MoxFile.serialize()")
        
        numberOfVertices = len(self.vertices)
        numberOfTriangles = len(self.triangles)
        numberOfChunks = len(self.chunks)
        numberOfMaterials = len(self.materials)
        numberOfParts = len(self.parts)
        numberOfMarkers = len(self.markers)
            
        options = self.options
        
        use_big_indices = (options & 1) == 1
        use_tangents = ((options >> 1) & 1) == 1

        if True:
            print("use_big_indices:", use_big_indices)
            print("use_tangents:", use_tangents)

        writer.write(struct.pack("1I 2H 6I", 
            0x4D4F5821, 
            self.options, 
            self.version, 
            numberOfVertices, 
            numberOfTriangles, 
            numberOfChunks, 
            numberOfMaterials, 
            numberOfParts, 
            numberOfMarkers
        ))
        
        marker_parameters_buffer = io.BytesIO()
        marker_parameters_writer = io.BufferedWriter(marker_parameters_buffer)

        position_post_header = writer.tell()
        
        if self.version == 0x0203:
            writer.write(struct.pack('4I', 0, 0, 0, 0))
        
        for i in range(numberOfVertices):
            vertex = self.vertices[i]
            
            if False:
                print("vertex:", vertex)
                print("vertex.positionX:", vertex.positionX)
                print("vertex.positionY:", vertex.positionY)
                print("vertex.positionZ:", vertex.positionZ)
                print("vertex.normalX:", vertex.normalX)
                print("vertex.normalY:", vertex.normalY)
                print("vertex.normalZ:", vertex.normalZ)
                print("vertex.u1:", vertex.u1)
                print("vertex.v1:", vertex.v1)
                print("vertex.u2:", vertex.u2)
                print("vertex.v2:", vertex.v2)
            
            writer.write(struct.pack("6f 4f", 
                vertex.positionX, 
                vertex.positionY, 
                vertex.positionZ, 
                vertex.normalX, 
                vertex.normalY, 
                vertex.normalZ, 
                vertex.u1, 
                vertex.v1,
                vertex.u2,
                vertex.v2
            ))
            
        if use_tangents:
            for i in range(numberOfVertices):
                tangent : MoxTangent = self.tangents[i]
                
                writer.write(struct.pack("8e", 
                    *tangent.uv1, 
                    *tangent.uv2
                ))
                
        for i in range(numberOfTriangles):
            triangle = self.triangles[i]
            
            struct_format = ""
            
            if use_big_indices:
                struct_format = "3I"
            else:
                struct_format = "3H"
                
            writer.write(struct.pack(struct_format, 
                triangle.vertexIndex1, 
                triangle.vertexIndex2, 
                triangle.vertexIndex3
            ))
            
        for i in range(numberOfChunks):
            chunk = self.chunks[i]
                
            struct_format = ""
            
            if True:
                struct_format = "6I"
            else:
                struct_format = "6H"
                
            writer.write(struct.pack(struct_format, 
                chunk.materialIndex,
                chunk.materialId,
                chunk.firstTriangle,
                chunk.triangleCount,
                chunk.firstVertex,
                chunk.lastVertex,
            ))

        for i in range(numberOfMaterials):
            material = self.materials[i]
            
            writer.write(struct.pack("I", 
                material.id,
            ))
            
            writer.write(bytearray(332))
            
        for i in range(numberOfParts):
            part = self.parts[i]
            
            name_encoded = part.name.encode("latin-1")[:64]
            matrix_flat = [item for sublist in part.matrix for item in sublist]

            writer.write(struct.pack("64s 16f 4h 2H 4f 4H 6f 2I", 
                name_encoded,
                *matrix_flat,
                part.parent,
                part.child,
                part.prevInLevel,
                part.nextInLevel,
                part.firstChunk,
                part.chunkCount,
                part.midX,
                part.midY,
                part.midZ,
                part.radius,
                part.w1,
                part.w2,
                part.w3,
                part.typeId,
                part.x1,
                part.x2,
                part.y1,
                part.y2,
                part.z1,
                part.z2,
                part.options,
                part.w5
            ))
            
        if self.version == 0x0203:
            for i in range(numberOfMarkers):
                marker = self.markers[i]
                marker_parameters = self.markerParameters[i]
            
                marker.extraOffset = marker_parameters_writer.tell()
                
                marker_parameters.serialize(marker_parameters_writer)
                
            marker_parameters_writer.flush()
            
        for i in range(numberOfMarkers):
            
            if self.version == 0x0203:
                marker : MoxMarkerV3 = self.markers[i]
            
                matrix_flat = [item for sublist in marker.matrix for item in sublist]
            
                writer.write(struct.pack("2I 2h 12f", 
                    marker.type,
                    marker.extraOffset,
                    marker.options,
                    marker.partIndex,
                    *matrix_flat,
                ))
            else:
                marker : MoxMarker = self.markers[i]
                marker_parameters = self.markerParameters[i]
            
                matrix_flat = [item for sublist in marker.matrix for item in sublist]
            
                writer.write(struct.pack("I", marker.type))
                    
                marker_parameters.serialize(writer)
                
                writer.write(struct.pack("2h 16f", 
                    marker.options,
                    marker.partIndex,
                    *matrix_flat
                ))
            
        if self.version == 0x0203:
            writer.write(marker_parameters_buffer.getvalue())
        
            writer.seek(position_post_header)
        
            marker_parameters_size = marker_parameters_buffer.tell()
                
            writer.write(struct.pack('4I', 
                marker_parameters_size, 
                0, 
                0, 
                0
            ))
        
class MoxVertex:
    def __init__(self):
        self.positionX = 0.0
        self.positionY = 0.0
        self.positionZ = 0.0
        self.normalX = 0.0
        self.normalY = 0.0
        self.normalZ = 0.0
        self.u1 = 0.0
        self.v1 = 0.0
        self.u2 = 0.0
        self.v2 = 0.0
    
class MoxTangent:
    def __init__(self):
        self.uv1 = None
        self.uv2 = None

class MoxTriangle:
    def __init__(self):
        self.vertexIndex1 = 0
        self.vertexIndex2 = 0
        self.vertexIndex3 = 0

class MoxChunk:
    def __init__(self):
        self.materialIndex = 0
        self.materialId = 0
        self.firstTriangle = 0
        self.triangleCount = 0
        self.firstVertex = 0
        self.lastVertex = 0
    
class MoxMaterial:
    def __init__(self):
        self.id = 0
    
class MoxPart:
    def __init__(self):
        self.name = ""
        self.matrix = Matrix.Identity(4)
        self.parent = -1
        self.child = -1
        self.prevInLevel = -1
        self.nextInLevel = -1
        self.firstChunk = 0
        self.chunkCount = 0
        self.midX = 0.0
        self.midY = 0.0
        self.midZ = 0.0
        self.radius = 1.0
        self.w1 = 0
        self.w2 = 0
        self.w3 = 0
        self.typeId = 0
        self.x1 = 0.0
        self.x2 = 0.0
        self.y1 = 0.0
        self.y2 = 0.0
        self.z1 = 0.0
        self.z2 = 0.0
        self.options = 0
        self.w5 = 0
       
class MaterialDefinitionEntry:
    def __init__(self):
        pass

class MtlFile:
    def __init__(self):
        pass
    
    def deserialize(self, file_path):
        pass

class MaterialData:
    def __init__(self):
        self.color_sets = []
        self.material_definitions = []
        self.materials = []
    
class Ref:
    def __init__(self, value):
        self.value = value
        
    def increment(self):
        self.value += 1
        
    def get(self):
        return self.value
    
class NativePart:
    def __init__(self, obj, mox_part : MoxPart, parent_part : 'NativePart', index : int, child_index : int):
        self.obj = obj
        self.mox_part = mox_part
        self.parent_part = parent_part
        self.index = index
        self.child_index = child_index
        self.child_parts : List['NativePart'] = []

def get_used_materials():
    used_materials = []
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            for slot in obj.material_slots:
                material = slot.material
                if material:
                    if material not in used_materials:
                        used_materials.append(slot.material)
    return used_materials

def parse_hex_color(hex_str):
    """Convert a hex color string to an integer."""
    return int(hex_str, 16)

def strip_quotes(s):
    """Remove quotes from the beginning and end of a string if present."""
    return s.strip('"')

def parse_header_line(header_line):
    """Parse the header line to extract ColSetInf values."""
    _, *colset_values = header_line.split()
    # Remove quotes from around values if present
    return [val.strip('"') for val in colset_values]

def parse_data_block(block):
    """Parse a block of text data into a dictionary with relevant types."""
    lines = block.strip().split('\n')
    data = {}

    # Handle the block identification line (e.g., # 0x1000)
    if lines[0].startswith('#'):
        data['ID'] = int(lines[0].strip().split()[1], 16)

    # Parse the rest of the lines
    for line in lines[1:]:
        if line.strip():  # Ensure the line is not empty
            key, *values = line.split(maxsplit=1)
            if not values:
                continue
            values = values[0].split()
            
            if key in {'MatClass'}:
                data[key] = [int(v, 16) for v in values]
            elif key in {'Diffuse', 'Ambient', 'Specular', 'Reflect2', 'Specular2', 'XDiffuse', 'XSpecular'}:
                data[key] = [int(v, 16) for v in values]
            elif key in {'TexFlags'}:
                data[key] = [int(v, 16) for v in values]
            elif key in {'Alpha'}:
                data[key] = int(values[0])
            elif key in {'SpecProps', 'Fresnel', 'FallOff'}:
                data[key] = [int(v) for v in values]
            elif key in {'TexOffset', 'TexScale'}:
                data[key] = [float(v) for v in values]
            elif key in {'TexAngle'}:
                data[key] = float(values[0])
            elif key in {'Tex1Name', 'Tex2Name', 'Tex3Name'}:
                data[key] = ' '.join(values).strip('"')
            else:
                data[key] = ' '.join(values)

    return data

def read_text_file_to_dicts(file_path):
    """Read a text file and return a header and a list of dictionaries."""
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Split the content by double newlines to separate blocks
    blocks = content.strip().split('\n\n')
    
    # The first line is the header
    header_line = blocks[0]
    header_values = parse_header_line(header_line)
    
    # The rest are data blocks
    data_blocks = blocks[1:]
    
    # Parse each block into a dictionary
    parsed_data = [parse_data_block(block) for block in data_blocks]
    
    return header_values, parsed_data

def write_dicts_to_text_file(file_path, header_values, parsed_data):
    """Write a header and list of dictionaries back to a text file."""
    blocks = []
    
    # Write the header line
    blocks.append(serialize_header_line(header_values))

    # Write each data block
    for data in parsed_data:
        blocks.append(serialize_data_block(data))

    content = '\n\n'.join(blocks) + '\n'

    with open(file_path, 'w') as file:
        file.write(content)

def serialize_header_line(header_values):
    """Serialize ColSetInf header values back to a header line string."""
    quoted = [f'"{val}"' for val in header_values]
    return 'ColSetInf ' + ' '.join(quoted)

def serialize_data_block(data):
    """Serialize a dictionary back into a block of text data."""
    lines = []

    if 'ID' in data:
        lines.append(f'# {hex(data["ID"])}')

    for key, value in data.items():
        if key == 'ID':
            continue
        
        if key in {'MatClass'}:
            values = ' '.join(f'{v:02x}' for v in value)
            lines.append(f'{key} {values}')
        elif key in {'Diffuse', 'Ambient', 'Specular', 'Reflect2', 'Specular2', 'XDiffuse', 'XSpecular'}:
            values = ' '.join(f'0x{v:06x}' for v in value)
            lines.append(f'{key} {values}')
        elif key in {'TexFlags'}:
            values = ' '.join(f'0x{v:02x}' for v in value)
            lines.append(f'{key} {values}')
        elif key in {'Alpha'}:
            lines.append(f'{key} {value:03d}')
        elif key in {'SpecProps', 'Fresnel', 'FallOff'}:
            values = ' '.join(f'{v:03d}' for v in value)
            lines.append(f'{key} {values}')
        elif key in {'TexOffset', 'TexScale'}:
            values = ' '.join(f'{v:.6f}' for v in value)
            lines.append(f'{key} {values}')
        elif key in {'TexAngle'}:
            lines.append(f'{key} {value:.6f}')
        elif key in {'Tex1Name', 'Tex2Name', 'Tex3Name'}:
            lines.append(f'{key} "{value}"')
        #else:
        #    lines.append(f'{key} {value}')

    return '\n'.join(lines)

def add_hex_color(int_value):
    """Convert an integer back to a hex color string."""
    return hex(int_value)

def add_quotes(s):
    """Add quotes around a string."""
    return f'"{s}"'
    
def addMarker(mox, marker_index, lens_flare_image, marker_objs, parent_obj, collection):
    marker = mox.markers[marker_index]
    marker_parameters = mox.markers[marker_index]
    
    axes_size = 0.2
    axes_scale = 1
        
    landscape_scale = 10
    
    matrix = Matrix(marker.matrix).to_4x4().transposed()
        
    matrix_translation = matrix.to_translation()
    matrix_quaternion  = matrix.to_3x3().to_quaternion()
    matrix_scale = matrix.to_scale()
    
    translation = matrix_translation.copy()
    scale = matrix_scale.copy()
    
    translation.x = matrix_translation.x
    translation.y = matrix_translation.z
    translation.z = matrix_translation.y
    
    scale.x = matrix_scale.x
    scale.y = matrix_scale.z
    scale.z = matrix_scale.y
    
    translation /= landscape_scale
    
    quaternion = swap_yz_axes_of_quaternion(matrix_quaternion)
    
    obj_axes = bpy.data.objects.new(f"Marker {marker_index}", None)
    obj_axes.parent = parent_obj
    #obj.empty_display_type = 'IMAGE'
    obj_axes.empty_display_size = axes_size * axes_scale
    
    marker_objs.insert(marker_index, obj_axes)
    
    #obj.data = lens_flare_image
    
    obj_axes.location = translation
    obj_axes.scale = scale
    
    obj_axes.rotation_mode = 'QUATERNION'
    obj_axes.rotation_quaternion = quaternion
    obj_axes.rotation_mode = 'XYZ'
    
    collection.objects.link(obj_axes)
    
def add_marker_parameters(mox : MoxFile, marker_index : int, marker_objs : [], part_objs = []):
    marker : MoxMarkerV3 = mox.markers[marker_index]
    marker_parameters = mox.markerParameters[marker_index]
    
    obj = marker_objs[marker_index]
    
    part_index = marker.partIndex

    part_obj = part_objs[part_index]
    
    marker_type_name = MarkerType(marker.type).name

    obj.mox_marker_properties.enabled = True
    obj.mox_marker_properties.type = marker_type_name
    obj.mox_marker_properties.part = part_objs[part_index]
    
    print("")
    print("marker index:", marker_index)
    print("part index:", part_index)
    print("part name:", part_obj.name)
    
    group = obj.mox_marker_properties
    
    type_name = MarkerType(marker.type).name
    
    prop = None
        
    if type_name == MarkerType.UNKNOWN.name:
        prop = group.no_properties
    elif type_name == MarkerType.NITRO.name:
        prop = group.nitro_properties
    elif type_name == MarkerType.HEADLIGHT.name:
        prop = group.headlight_properties
    elif type_name == MarkerType.REAR_AND_BRAKE_LIGHT.name:
        prop = group.rear_and_brake_light_properties
    elif type_name == MarkerType.REVERSING_LIGHT.name:
        prop = group.reversing_light_properties
    elif type_name == MarkerType.INDICATOR_LEFT.name:
        prop = group.blinking_light_properties
    elif type_name == MarkerType.INDICATOR_RIGHT.name:
        prop = group.blinking_light_properties
    elif type_name == MarkerType.GENERIC_LIGHT.name:
        prop = group.generic_light_properties
    elif type_name == MarkerType.BLINKING_LIGHT.name:
        prop = group.blinking_light_properties
    elif type_name == MarkerType.ROTATING_LIGHT.name:
        prop = group.rotating_light_properties
    elif type_name == MarkerType.TUNNEL_LIGHT.name:
        prop = group.tunnel_light_properties
    elif type_name == MarkerType.MOTOR.name:
        prop = group.no_properties
    elif type_name == MarkerType.DRONE_HOOK.name:
        prop = group.no_properties
    elif type_name == MarkerType.WHEEL_HOOK.name:
        prop = group.no_properties
    elif type_name == MarkerType.TRAILER_HOOK.name:
        prop = group.no_properties
    elif type_name == MarkerType.STREET_HOOK.name:
        prop = group.no_properties
    elif type_name == MarkerType.OLD_PARTICLES.name:
        prop = group.particle_emitter_properties
    elif type_name == MarkerType.MUZZLE_FLASH.name:
        prop = group.muzzle_flash_properties
    elif type_name == MarkerType.OLD_PARTICLES_NO_WIND.name:
        prop = group.particle_emitter_properties
    elif type_name == MarkerType.PARTICLE_EMITTER.name:
        prop = group.particle_emitter_properties
    elif type_name == MarkerType.SOUND_EMITTER.name:
        prop = group.sound_emitter_properties
    elif type_name == MarkerType.INVALID.name:
        prop = group.no_properties
    
    #print("prop:", prop)
            
    if isinstance(prop, MarkerProperties):
        prop.set_parameters(marker_parameters)
        
def float_to_half(val):
    f32 = struct.unpack('>I', struct.pack('>f', val))[0]
    f16 = ((f32 >> 16) & 0x8000) | ((((f32 & 0x7f800000) - 0x38000000) >> 13) & 0x7c00) | ((f32 >> 13) & 0x03ff)
    return f16

def create_vertex_from_mox(mox : MoxFile, vertex_index : int, bm, vertices : {}, uvs1 : {}, uvs2 : {}, landscape_scale):
    mox_vertex = mox.vertices[vertex_index]
    vertex_position = Vector((mox_vertex.positionX, mox_vertex.positionZ, mox_vertex.positionY)) / landscape_scale
    vertex_normal = Vector((mox_vertex.normalX, mox_vertex.normalZ, mox_vertex.normalY))
    vertex_uv1 = (mox_vertex.u1, -mox_vertex.v1 + 1.0)
    vertex_uv2 = (mox_vertex.u2, -mox_vertex.v2 + 1.0)
                      
    vertex = bm.verts.new(vertex_position)
    vertex.normal = vertex_normal
    vertices[vertex_index] = vertex
                    
    uvs1[vertex_index] = vertex_uv1
    uvs2[vertex_index] = vertex_uv2
    
    return vertex

def add_part(mox, part_index, parent_obj, material_data, part_objs : [], collection):
    print("")
    print(f"part_index = {part_index}")
    print(f"len(mox.parts) = {len(mox.parts)}")
    
    mox_part = mox.parts[part_index]
    
    landscape_scale = 10.0
    
    bm = bmesh.new()
    
    uv_layer1 = bm.loops.layers.uv.new("UV1")
    uv_layer2 = bm.loops.layers.uv.new("UV2")
    
    uv_layer_names = [uv_layer1.name, uv_layer2.name]
    
    vertices = {}
    uvs1 = {}
    uvs2 = {}
    
    part_material_indices = []
    
    for i in range(mox_part.firstChunk, mox_part.firstChunk + mox_part.chunkCount):
        mox_chunk : MoxChunk = mox.chunks[i]
    
        for j in range(mox_chunk.firstTriangle, mox_chunk.firstTriangle + mox_chunk.triangleCount):
            mox_triangle = mox.triangles[j]
            
            vertex_indices = [mox_triangle.vertexIndex3, mox_triangle.vertexIndex2, mox_triangle.vertexIndex1]
            
            if len(set(vertex_indices)) < 3:
                print(f"triangle {j} is degenerate, vertices {vertex_indices}")
            else:
                triangle_vertices = list(range(3))

                for k, vertex_index in enumerate(vertex_indices):
                    if vertex_index in vertices:
                        triangle_vertices[k] = vertices[vertex_index]
                    else:
                        triangle_vertices[k] = create_vertex_from_mox(mox, vertex_index, bm, vertices, uvs1, uvs2, landscape_scale)
                    
                face_vertices = (triangle_vertices[0], triangle_vertices[1], triangle_vertices[2])
            
                if bm.faces.get(face_vertices):
                    print("face with vertices already exists:", vertex_indices);
                    for k, vertex_index in enumerate(vertex_indices):
                        triangle_vertices[k] = create_vertex_from_mox(mox, vertex_index, bm, vertices, uvs1, uvs2, landscape_scale)
                    face_vertices = (triangle_vertices[0], triangle_vertices[1], triangle_vertices[2])
                
                face = bm.faces.new(face_vertices)
        
                face.smooth = True
        
                for k, loop in enumerate(face.loops):
                    vertex_index = vertex_indices[k]
                    loop[uv_layer1].uv = uvs1[vertex_index]
                    loop[uv_layer2].uv = uvs2[vertex_index]

                face.material_index = len(part_material_indices)
                
        part_material_indices.append(mox_chunk.materialIndex)
          
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    
    mesh = bpy.data.meshes.new(name=f"{mox_part.name} Mesh")
    obj = bpy.data.objects.new(f"{mox_part.name}", mesh)
    
    part_objs[part_index] = obj
    
    #print("part name:", obj.name)
    
    #bpy.context.collection.objects.link(obj)
    collection.objects.link(obj)
    
    bm.to_mesh(mesh)
    bm.free()
        
    for i in range(len(part_material_indices)):
        part_material_index = part_material_indices[i]
        part_material = material_data.materials[part_material_index]
        
        part_material.mox_material_properties.setup(part_material, uv_layer_names)
        
        mesh.materials.append(part_material)
        #print(f"part material {i} -> index {part_material_index}")
        
    mesh.normals_split_custom_set_from_vertices([v.normal for v in mesh.vertices])
    
    if bpy.app.version < (4, 1, 0):
        mesh.use_auto_smooth = True
    
    mesh.update()

    matrix = Matrix(mox_part.matrix).transposed()
    
    decompose_and_apply_matrix(obj, matrix, landscape_scale)
    
    options = mox_part.options

    enable_deformation = ((options >> 0) & 1) == 0
    enable_detachment = ((options >> 1) & 1) == 0
    enable_animation = ((options >> 2) & 1) == 0
    
    obj.mox_part_properties.enabled = True
    obj.mox_part_properties.type = PartType(mox_part.typeId).name
    obj.mox_part_properties.enable_deformation = enable_deformation
    obj.mox_part_properties.enable_detachment = enable_detachment
    obj.mox_part_properties.enable_animation = enable_animation
    obj.mox_part_properties.swing_min = Vector((degrees(mox_part.x1), degrees(mox_part.z1), degrees(mox_part.y1)))
    obj.mox_part_properties.swing_max = Vector((degrees(mox_part.x2), degrees(mox_part.z2), degrees(mox_part.y2)))
    obj.mox_part_properties.center = Vector((mox_part.midX, mox_part.midZ, mox_part.midY)) / landscape_scale
    obj.mox_part_properties.radius = mox_part.radius / landscape_scale
    
    if parent_obj != None:
        obj.parent = parent_obj

    if mox_part.nextInLevel != -1:
        add_part(mox, mox_part.nextInLevel, parent_obj, material_data, part_objs, collection)
        
    if mox_part.child != -1:
        add_part(mox, mox_part.child, obj, material_data, part_objs, collection)
        
    return obj
        
def retrieve_native_part(native_part : NativePart, part_index_ref : Ref):
    part_index_ref.increment()
    
    native_part.index = part_index_ref.get() - 1
    
    for i, child_part_obj in enumerate(native_part.obj.children):
        if child_part_obj.type == 'MESH' and child_part_obj.visible_get():
            child_mox_part = MoxPart()
            child_mox_part.name = child_part_obj.name
            child_native_part = NativePart(child_part_obj, child_mox_part, native_part, part_index_ref.get(), i)
            native_part.child_parts.append(child_native_part)
            retrieve_native_part(child_native_part, part_index_ref)
    
def retrieve_part(mox : MoxFile, native_part : NativePart, source_materials : [], part_objs : [], use_triangulate : bool):
    part_obj = native_part.obj
    
    part_index = native_part.index
    
    part_objs[part_index] = part_obj
    
    print(f"part {part_index}: {part_obj.name}:")
    
    temp_obj = part_obj.copy()
    temp_obj.data = part_obj.data.copy()
    bpy.context.collection.objects.link(temp_obj)
    
    bpy.context.view_layer.objects.active = temp_obj
    temp_obj.select_set(True)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    if use_triangulate:
        tri_mod = temp_obj.modifiers.new(name="Triangulate", type='TRIANGULATE')
        bpy.ops.object.modifier_apply(modifier=tri_mod.name)
        
    landscape_scale = 10
    
    mox_part = MoxPart()
    mox_part.name = part_obj.name
    
    part_type_name = part_obj.mox_part_properties.type
    part_type = PartType[part_type_name].value
    mox_part.typeId = part_type
    
    enable_deformation = part_obj.mox_part_properties.enable_deformation
    enable_detachment = part_obj.mox_part_properties.enable_detachment
    enable_animation = part_obj.mox_part_properties.enable_animation
    
    options = 0
    
    options |= (not enable_deformation) << 0
    options |= (not enable_detachment) << 1
    options |= (not enable_animation) << 2

    mox_part.options = options
    
    mox_part.x1 = radians(part_obj.mox_part_properties.swing_min.x)
    mox_part.y1 = radians(part_obj.mox_part_properties.swing_min.z)
    mox_part.z1 = radians(part_obj.mox_part_properties.swing_min.y)
    
    mox_part.x2 = radians(part_obj.mox_part_properties.swing_max.x)
    mox_part.y2 = radians(part_obj.mox_part_properties.swing_max.z)
    mox_part.z2 = radians(part_obj.mox_part_properties.swing_max.y)
    
    mox_part.midX = part_obj.mox_part_properties.center.x * landscape_scale
    mox_part.midY = part_obj.mox_part_properties.center.z * landscape_scale
    mox_part.midZ = part_obj.mox_part_properties.center.y * landscape_scale
    
    mox_part.radius = part_obj.mox_part_properties.radius * landscape_scale

    input_matrix = compose_matrix(part_obj, landscape_scale)
    mox_part.matrix = input_matrix.transposed()
    
    mox_part.firstChunk = len(mox.chunks)
    
    chunk_triangle_indices = {}
    
    mesh = temp_obj.data

    mesh.calc_loop_triangles()
    
    if bpy.app.version < (4, 1, 0):
        mesh.calc_normals_split()
    
    uv_layers = [uv_layer.name for uv_layer in mesh.uv_layers]
    
    uv_layer_count = len(uv_layers)
    
    has_uv2 = uv_layer_count > 1
    
    if not has_uv2:
        has_uv2 = False
        print("expected 2 UV maps, found", uv_layer_count)
    
    for uv_index in range(min(len(uv_layers), 2)):
        uv_layer_name = uv_layers[uv_index]
        mesh.calc_tangents(uvmap=uv_layer_name)
    
    has_material_slots = len(part_obj.material_slots) > 0

    for material_slot_index in range(max(1, len(part_obj.material_slots))):
        chunk_triangle_indices[material_slot_index] = []

    for polygon in mesh.polygons:
        polygon_index = polygon.index
        material_slot_index = polygon.material_index
        
        chunk_triangle_indices[material_slot_index].append(polygon_index)
        
    for material_slot_index in range(max(1, len(part_obj.material_slots))):
        source_triangle_indices = chunk_triangle_indices[material_slot_index]
        
        chunk_first_vertex = 0
        chunk_first_triangle = 0
        chunk_last_vertex = 0
        chunk_triangle_count = 0
        
        used_vertex_indices = {}
        
        for i, source_triangle_index in enumerate(source_triangle_indices):
            polygon = mesh.polygons[source_triangle_index]
            
            if len(polygon.loop_indices) > 3:
                print("found non-triangle polygon, aborting")
                return
            
            polygon.use_smooth = True
            
            triangle_index = len(mox.triangles)

            vertex_indices = []

            for loop_index in polygon.loop_indices:
                loop = mesh.loops[loop_index]
                
                source_vertex_index = loop.vertex_index
                
                source_vertex = mesh.vertices[source_vertex_index]
                
                position = source_vertex.co
                normal = loop.normal
                
                u1 = None
                v1 = None
                u2 = None
                v2 = None
                
                t1 = None
                t2 = None
                
                for uv_index in range(min(uv_layer_count, 2)):
                    uv_layer_name = uv_layers[uv_index]
                        
                    uv_layer = mesh.uv_layers.get(uv_layer_name)
                    source_uv = uv_layer.data[loop_index].uv
                    
                    tangent = loop.tangent
                
                    tangent_x = tangent[0]
                    tangent_y = tangent[1]
                    tangent_z = tangent[2]
                    bitangent_sign = loop.bitangent_sign
                        
                    np_tangents = np.array([tangent_x, tangent_z, tangent_y, bitangent_sign], dtype=np.float32)
                    np_tangents_half = np_tangents.astype(np.float16)
                    
                    if uv_index == 0:
                        u1 = source_uv[0]
                        v1 = -source_uv[1] + 1.0
                            
                        t1 = np_tangents_half
                        
                        if not has_uv2:
                            u2 = u1
                            v2 = v1
                            
                            t2 = t1
                    elif uv_index == 1:
                        u2 = source_uv[0]
                        v2 = -source_uv[1] + 1.0
                            
                        t2 = np_tangents_half
                
                vertex_key = (tuple(position), (u1, v1, u2, v2), tuple(normal))
                
                if vertex_key not in used_vertex_indices:
                    used_vertex_indices[vertex_key] = len(mox.vertices)
            
                    mox_vertex = MoxVertex()
                    mox_tangent = MoxTangent()
            
                    mox_vertex.positionX = position.x * landscape_scale
                    mox_vertex.positionY = position.z * landscape_scale
                    mox_vertex.positionZ = position.y * landscape_scale
            
                    mox_vertex.normalX = normal.x
                    mox_vertex.normalY = normal.z
                    mox_vertex.normalZ = normal.y
            
                    mox_vertex.u1 = u1
                    mox_vertex.v1 = v1
                    
                    mox_vertex.u2 = u2
                    mox_vertex.v2 = v2
                            
                    mox_tangent.uv1 = t1
                    mox_tangent.uv2 = t2
                
                    mox.vertices.append(mox_vertex)
                    mox.tangents.append(mox_tangent)
            
                vertex_indices.append(used_vertex_indices[vertex_key])
                
            mox_triangle = MoxTriangle()
            mox_triangle.vertexIndex1 = vertex_indices[2]
            mox_triangle.vertexIndex2 = vertex_indices[1]
            mox_triangle.vertexIndex3 = vertex_indices[0]
            mox.triangles.append(mox_triangle)
            
            if i == 0:
                chunk_first_triangle = triangle_index
                chunk_first_vertex = min(vertex_indices)
                
            iterations_triangles = i + 1
            
            max_vertex_index = max(vertex_indices)

            if max_vertex_index > chunk_last_vertex:
                chunk_last_vertex = max_vertex_index

            if iterations_triangles > chunk_triangle_count:
                chunk_triangle_count = iterations_triangles
               
        material = None

        if has_material_slots:
            material = part_obj.material_slots[material_slot_index].material
        else:
            material_index = len(bpy.data.materials)
            material = bpy.data.materials.new(name=f"{material_index} {(0x1000 + material_index):04x}")

        material_name = material.name
        
        if material_name not in source_materials:
            source_materials.append(material_name)
            
        material_index = source_materials.index(material_name)

        mox_chunk = MoxChunk()
        mox_chunk.materialIndex = material_index
        mox_chunk.materialId = 0x1000 + material_index
        
        mox_chunk.firstTriangle = chunk_first_triangle
        mox_chunk.triangleCount = chunk_triangle_count
        
        mox_chunk.firstVertex = chunk_first_vertex
        mox_chunk.lastVertex = chunk_last_vertex
        
        mox.chunks.append(mox_chunk)
        
        mox_part.chunkCount += 1
        
    mox.parts.append(mox_part)
    
    bpy.data.objects.remove(temp_obj, do_unlink=True)
    
    parent_part = native_part.parent_part

    has_children = len(native_part.child_parts) > 0
    
    parent_children = parent_part.child_parts
    child_index = parent_children.index(native_part)
        
    mox_part.parent = parent_part.index
            
    if child_index > 0:
        prev_index = parent_children[child_index - 1].index
                
        mox_part.prevInLevel = prev_index
                
    if child_index < len(parent_children) - 1:
        next_index = parent_children[child_index + 1].index
                
        mox_part.nextInLevel = next_index
        
    if has_children:
        mox_part.child = native_part.child_parts[0].index
        
    for i, child_part in enumerate(native_part.child_parts):
        retrieve_part(mox, child_part, source_materials, part_objs, use_triangulate)

def retrieve_marker(mox : MoxFile, marker_index : int, marker_objs : [], part_objs : []):
    marker_obj = marker_objs[marker_index]

    landscape_scale = 10
    
    input_matrix = compose_matrix(marker_obj, landscape_scale).transposed()
    
    mox_marker = None
    
    if mox.version == 0x0203:
        mox_marker = MoxMarkerV3()
        mox_marker.matrix = [
            [input_matrix[0][0], input_matrix[0][1], input_matrix[0][2]], 
            [input_matrix[1][0], input_matrix[1][1], input_matrix[1][2]], 
            [input_matrix[2][0], input_matrix[2][1], input_matrix[2][2]], 
            [input_matrix[3][0], input_matrix[3][1], input_matrix[3][2]]
        ]
    else:
        mox_marker = MoxMarker()
        mox_marker.matrix = [
            [input_matrix[0][0], input_matrix[0][1], input_matrix[0][2], input_matrix[0][3]], 
            [input_matrix[1][0], input_matrix[1][1], input_matrix[1][2], input_matrix[1][3]], 
            [input_matrix[2][0], input_matrix[2][1], input_matrix[2][2], input_matrix[2][3]], 
            [input_matrix[3][0], input_matrix[3][1], input_matrix[3][2], input_matrix[3][3]]
        ]
        
    #print("matrix:", mox_marker.matrix)
    
    marker_type_name = marker_obj.mox_marker_properties.type
    marker_type = MarkerType[marker_type_name].value
    
    marker_part_obj = marker_obj.mox_marker_properties.part
    
    mox_marker.type = marker_type
    
    if marker_part_obj in part_objs:
        marker_part_index = part_objs.index(marker_part_obj)
        mox_marker.partIndex = marker_part_index
        #print(f"marker {marker_index} -> part {marker_part_index}: {marker_part_obj.name}")
        
    group = marker_obj.mox_marker_properties
    
    prop : MarkerProperties = None
    
    if marker_type_name == MarkerType.UNKNOWN.name:
        prop = group.no_properties
    elif marker_type_name == MarkerType.NITRO.name:
        prop = group.nitro_properties
    elif marker_type_name == MarkerType.HEADLIGHT.name:
        prop = group.headlight_properties
    elif marker_type_name == MarkerType.REAR_AND_BRAKE_LIGHT.name:
        prop = group.rear_and_brake_light_properties
    elif marker_type_name == MarkerType.REVERSING_LIGHT.name:
        prop = group.reversing_light_properties
    elif marker_type_name == MarkerType.INDICATOR_LEFT.name:
        prop = group.blinking_light_properties
    elif marker_type_name == MarkerType.INDICATOR_RIGHT.name:
        prop = group.blinking_light_properties
    elif marker_type_name == MarkerType.GENERIC_LIGHT.name:
        prop = group.generic_light_properties
    elif marker_type_name == MarkerType.BLINKING_LIGHT.name:
        prop = group.blinking_light_properties
    elif marker_type_name == MarkerType.ROTATING_LIGHT.name:
        prop = group.rotating_light_properties
    elif marker_type_name == MarkerType.TUNNEL_LIGHT.name:
        prop = group.tunnel_light_properties
    elif marker_type_name == MarkerType.MOTOR.name:
        prop = group.no_properties
    elif marker_type_name == MarkerType.DRONE_HOOK.name:
        prop = group.no_properties
    elif marker_type_name == MarkerType.WHEEL_HOOK.name:
        prop = group.no_properties
    elif marker_type_name == MarkerType.TRAILER_HOOK.name:
        prop = group.no_properties
    elif marker_type_name == MarkerType.STREET_HOOK.name:
        prop = group.no_properties
    elif marker_type_name == MarkerType.OLD_PARTICLES.name:
        prop = group.particle_emitter_properties
    elif marker_type_name == MarkerType.MUZZLE_FLASH.name:
        prop = group.muzzle_flash_properties
    elif marker_type_name == MarkerType.OLD_PARTICLES_NO_WIND.name:
        prop = group.particle_emitter_properties
    elif marker_type_name == MarkerType.PARTICLE_EMITTER.name:
        prop = group.particle_emitter_properties
    elif marker_type_name == MarkerType.SOUND_EMITTER.name:
        prop = group.sound_emitter_properties
    elif marker_type_name == MarkerType.INVALID.name:
        prop = group.no_properties
        
    mox_marker_parameters = prop.get_parameters()
    
    mox_marker_parameters_final = None
    
    if mox.version == 0x0203:
        mox_marker_parameters_final = mox_marker_parameters
    else:
        mox_marker_parameters_final = mox_marker_parameters.to_generic()
    
    mox.markers.insert(marker_index, mox_marker)
    mox.markerParameters.insert(marker_index, mox_marker_parameters_final)
    
def import_mox(context, moxFilePath, texture_folder_path, collection):
    print("import_mox() IN")
    
    scene = context.scene
        
    mox_file_name = moxFilePath.stem
    mtlFilePath = moxFilePath.with_suffix(".mtl")
    textureFolderPath = texture_folder_path
    print("mox_file_name:", mox_file_name)
    print("moxFilePath:", moxFilePath)
    print("mtlFilePath:", mtlFilePath)
    print("textureFolderPath:", textureFolderPath)
        
    addon_directory = Path(__file__).parent
    
    # Construct the full path to the image file
    lens_flare_image_path = addon_directory / "lensflare.tga"
    
    mox = MoxFile()
        
    loaded_textures = {}

    material_data = MaterialData()
        
    with moxFilePath.open('rb') as mox_reader:
        mox.deserialize(mox_reader)
            
    part_objs = list(range(len(mox.parts)))
    marker_objs = []
    
    if mtlFilePath.exists():
        material_data.color_sets, material_data.material_definitions = read_text_file_to_dicts(mtlFilePath)
        
        scene.mox_material_color_list.clear()
        
        for mtl_color in material_data.color_sets:
            item = scene.mox_material_color_list.add()
            item.name = mtl_color
    
    for i in range(len(mox.materials)):
        mox_material = mox.materials[i]

        material = bpy.data.materials.new(name=f"{i} {mox_material.id:04x}")
            
        material.use_nodes = True
        material.use_backface_culling = True
        
        material_definition = next((m for m in material_data.material_definitions if m.get('ID') == mox_material.id), None)
            
        if material_definition:
            material_property_group = material.mox_material_properties
            
            for j in range(len(tex_property_names)):
                tex_property_name = tex_property_names[j]
                
                if tex_property_name in material_definition:
                    tex_name = material_definition[tex_property_name]
                
                    if tex_name:
                        tex_file_path = textureFolderPath / tex_name
            
                        print("tex_name:", tex_name)

                        loaded_texture = None

                        if tex_name in loaded_textures:
                            loaded_texture = loaded_textures[tex_name]
                        else:
                            loaded_texture = bpy.data.textures.new(name=tex_name, type='IMAGE')
                            loaded_texture.use_fake_user = True
                    
                            if tex_file_path.exists():
                                image = bpy.data.images.load(str(tex_file_path))
                                
                                if j == 1:
                                    image.colorspace_settings.name = 'Non-Color'
                                    
                                loaded_texture.image = image
                                    
                        loaded_textures[tex_name] = loaded_texture
                    
                        if loaded_texture != None:
                            setattr(material_property_group, f"texture_{j + 1}", loaded_texture)
                
            material_property_group.enabled = True
            
            try:
                material_property_group.matclass = MaterialClass(material_definition['MatClass'][0]).name
                material_property_group.sub_type = MaterialSubType(material_definition['MatClass'][1]).name
                material_property_group.alpha_type = MaterialAlphaType(material_definition['MatClass'][2]).name
            
                material_property_group.matflag_preset = (material_definition['MatClass'][3] & 1) != 0
                material_property_group.matflag_standard = (material_definition['MatClass'][3] & 2) != 0
                material_property_group.matflag_dirt = (material_definition['MatClass'][3] & 4) != 0
                material_property_group.matflag_chrome = (material_definition['MatClass'][3] & 8) != 0
            
                material_property_group.texture_tiling_u = TextureTiling(material_definition['TexFlags'][0] & 15).name
                material_property_group.texture_tiling_v = TextureTiling(material_definition['TexFlags'][0] >> 4).name
            
                material_property_group.texture_offset = material_definition['TexOffset']
                material_property_group.texture_scale = material_definition['TexScale']
                material_property_group.texture_angle = material_definition['TexAngle']
                material_property_group.alpha = material_definition['Alpha']
            
                material_property_group.spec_sharp_1 = material_definition['SpecProps'][0]
                material_property_group.spec_size_1 = material_definition['SpecProps'][1]
                material_property_group.spec_sharp_2 = material_definition['SpecProps'][2]
            
                material_property_group.fresnel_intensity = material_definition['Fresnel'][0]
                material_property_group.fresnel_curve = material_definition['Fresnel'][1]
                material_property_group.fresnel_level = material_definition['Fresnel'][2]
            
                material_property_group.falloff_intensity = material_definition['FallOff'][0]
                material_property_group.falloff_curve = material_definition['FallOff'][1]
                    
                for scene_color_index, scene_color in enumerate(scene.mox_material_color_list):
                    if hasattr(material, "mox_material_properties"):
                        material_property_group.color_properties.add()
                    
                        color_property_group = material_property_group.color_properties[scene_color_index]

                        for prop_name, dict_key in material_color_keys.items():
                            packed = material_definition[dict_key][scene_color_index]
                            setattr(color_property_group, prop_name, unpack_color(packed))
            except:
                print(f"Error reading material {mox_material.id}")
            
        material_data.materials.insert(i, material)
        
    obj = bpy.data.objects.new(f"{mox_file_name}", None)
    
    add_part(mox, 0, obj, material_data, part_objs, collection)
    
    collection.objects.link(obj)
    
    lens_flare_image = bpy.data.images.load(str(lens_flare_image_path))
        
    #print("number of markers:", len(mox.markers))
    
    for i in range(len(mox.markers)):
        addMarker(mox, i, lens_flare_image, marker_objs, obj, collection)
            
    for i in range(len(mox.markers)):
        add_marker_parameters(mox, i, marker_objs, part_objs)
    
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
        
    print("import_mox() OUT")
        
    return obj
    
class ImportMox(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_landscape.object"
    bl_label = "Import Object"
    
    filename_ext = ".mox"

    filter_glob: StringProperty(
        default="*.mox",
        options={'HIDDEN'},
        maxlen=255
    )

    def execute(self, context):
        collection = bpy.context.collection
        #bpy.context.scene.collection.children.link(collection)
        
        mox_file_path = Path(self.filepath)
        texture_folder_path = mox_file_path.parent / "Textures"
        
        import_mox(context, mox_file_path, texture_folder_path, collection)
        
        return {'FINISHED'}
    
class ExportMox(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export_landscape.object"
    bl_label = "Export Object"

    filename_ext = ".mox"

    filter_glob: StringProperty(
        default="*.mox",
        options={'HIDDEN'},
        maxlen=255
    )

    use_triangulate: BoolProperty(
        name="Triangulate",
        description="Triangulate all meshes",
        default=False,
    )
    
    write_material: BoolProperty(
        name="Write Material",
        description="Write an accompanying MTL file",
        default=False,
    )

    mox_version: EnumProperty(
        name="Version",
        description="Target MOX version",
        items=(
            ('3', "2.03", "Newest format that features enhanced markers and tangents for normal map support. Not compatible with games before CT5."),
            ('2', "2.02", "Less advanced format used by older games. Also required for some models such as drivers.")
        ),
        default='3',
    )

    def execute(self, context):
        print("ExportMox.execute() IN")
        
        scene = context.scene

        mox_file_path = Path(self.filepath)
        mtl_file_path = mox_file_path.with_suffix(".mtl")
        texture_folder_path = mox_file_path.parent / "Textures"
        print("mox_file_path:", mox_file_path)
        print("mtl_file_path:", mtl_file_path)
        print("texture_folder_path:", texture_folder_path)
                
        version = 0
        
        if self.mox_version == '3':
            version = 0x0203
        else:
            version = 0x0202

        mox = MoxFile()
        mox.version = version
        
        part_index_ref = Ref(0)

        root_objs = []
        marker_objs = []
        native_parts = []
        
        root_native_part = NativePart(None, None, None, -1, 0)
        
        #for obj in bpy.context.scene.objects:
            #if obj.type == 'MESH' and obj.parent is None and (obj.select_get() and not obj.hide_select)):
            #    root_objs.append(obj)
            
        root_obj = bpy.context.active_object
        
        if root_obj:
            if root_obj.type == 'EMPTY':
                for obj in root_obj.children:
                    if obj.type == 'MESH':
                       root_objs.append(obj)
                       print(f"collecting object: {obj.name}")
            elif root_obj.type == 'MESH':
                root_objs.append(root_obj)
        else:
            for obj in bpy.context.scene.objects:
                if obj.type == 'MESH':
                   root_objs.append(obj)
        
        for i, obj in enumerate(root_objs):
            if not obj.visible_get():
                continue
            
            mox_part = MoxPart()
            mox_part.name = obj.name
            native_part = NativePart(obj, mox_part, root_native_part, part_index_ref.get(), i)
            native_parts.append(native_part)
            root_native_part.child_parts.append(native_part)
            retrieve_native_part(native_part, part_index_ref)
                
        part_objs = list(range(part_index_ref.get()))
        
        source_materials = []
        
        for native_part in native_parts:
            retrieve_part(mox, native_part, source_materials, part_objs, self.use_triangulate)
        
        use_big_indices = len(mox.vertices) > 0xFFFF
        use_tangents = mox.version == 0x0203 and len(mox.tangents) > 0
        
        options = 0
        options |= (int(use_big_indices) & 1) << 0
        options |= (int(use_tangents) & 1) << 1
        
        mox.options = options
        
        for obj in root_obj.children_recursive:
            if obj != root_obj and obj != obj.type == 'EMPTY':
                marker_objs.append(obj)
            
        for i, obj in enumerate(marker_objs):
            if not obj.visible_get():
                continue
            
            retrieve_marker(mox, i, marker_objs, part_objs)
            
        mox.materials = list(range(len(source_materials)))
            
        material_data = MaterialData()
        
        scene_colors = context.scene.mox_material_color_list
            
        if scene_colors and len(scene_colors) > 0:
            for i, scene_color in enumerate(scene_colors):
                material_data.color_sets.insert(i, scene_color.name)
        else:
            material_data.color_sets = ["Default"] # should be impossible

        for i, source_material in enumerate(source_materials):
            mox_material = MoxMaterial()
            mox_material.id = 0x1000 + i
            mox.materials[i] = mox_material
            
            material = bpy.data.materials.get(source_material)
            
            material_definition = {
                'ID': mox_material.id,
                'MatClass': [0, 0, 0, 0],
                'Diffuse': [0 for _ in material_data.color_sets],
                'Ambient': [0 for _ in material_data.color_sets],
                'Specular': [0 for _ in material_data.color_sets],
                'Reflect2': [0 for _ in material_data.color_sets],
                'Specular2': [0 for _ in material_data.color_sets],
                'XDiffuse': [0 for _ in material_data.color_sets],
                'XSpecular': [0 for _ in material_data.color_sets],
                'Tex1Name': '',
                'Tex2Name': '',
                'Tex3Name': '',
                'TexFlags': [0x00, 0x00, 0x00, 0x00],
                'TexOffset': [0.0, 0.0],
                'TexScale': [0.0, 0.0],
                'TexAngle': [0.0],
                'Alpha': 0,
                'SpecProps': [0, 0, 0],
                'Fresnel': [0, 0, 0],
                'FallOff': [0, 0]
            }
            
            if material is not None:
                material_data.materials.insert(i, material)
            
                if hasattr(material, "mox_material_properties"):
                    material_property_group = material.mox_material_properties
                
                    material_definition['MatClass'][0] = MaterialClass[material_property_group.matclass].value
                    material_definition['MatClass'][1] = MaterialSubType[material_property_group.sub_type].value
                    material_definition['MatClass'][2] = MaterialAlphaType[material_property_group.alpha_type].value
            
                    if material_property_group.matflag_preset:
                        material_definition['MatClass'][3] |= 1
                    
                    if material_property_group.matflag_standard:
                        material_definition['MatClass'][3] |= 2
                    
                    if material_property_group.matflag_dirt:
                        material_definition['MatClass'][3] |= 4
                    
                    if material_property_group.matflag_chrome:
                        material_definition['MatClass'][3] |= 8
            
                    for j in range(len(tex_property_names)):
                        texture_property = getattr(material_property_group, f"texture_{j + 1}")
                        
                        if not texture_property:
                            continue
                        
                        tex_name = f"{os.path.splitext(texture_property.name)[0]}.tga"
                    
                        material_definition[tex_property_names[j]] = tex_name
                        
                    material_definition['TexFlags'][0] = TextureTiling[material_property_group.texture_tiling_u].value & 15
                    material_definition['TexFlags'][0] |= (TextureTiling[material_property_group.texture_tiling_v].value & 15) << 4
                
                    material_definition['TexFlags'][1] = 0
                    material_definition['TexFlags'][2] = 0
                    material_definition['TexFlags'][3] = 0
                    
                    material_definition['TexOffset'] = material_property_group.texture_offset
                    material_definition['TexScale'] = material_property_group.texture_scale
                    material_definition['TexAngle'] = material_property_group.texture_angle
                    material_definition['Alpha'] = material_property_group.alpha
            
                    material_definition['SpecProps'][0] = material_property_group.spec_sharp_1
                    material_definition['SpecProps'][1] = material_property_group.spec_size_1
                    material_definition['SpecProps'][2] = material_property_group.spec_sharp_2
            
                    material_definition['Fresnel'][0] = material_property_group.fresnel_intensity
                    material_definition['Fresnel'][1] = material_property_group.fresnel_curve
                    material_definition['Fresnel'][2] = material_property_group.fresnel_level
            
                    material_definition['FallOff'][0] = material_property_group.falloff_intensity
                    material_definition['FallOff'][1] = material_property_group.falloff_curve
                    
                    for scene_color_index, scene_color in enumerate(scene.mox_material_color_list):
                        color_property_group = material_property_group.color_properties[scene_color_index]

                        for prop_name, dict_key in material_color_keys.items():
                            unpacked = getattr(color_property_group, prop_name)
                            material_definition[dict_key][scene_color_index] = pack_color(unpacked)
            
            material_data.material_definitions.insert(i, material_definition)
        
        with mox_file_path.open('wb') as mox_writer:
            mox.serialize(mox_writer)
                
        if self.write_material:
            write_dicts_to_text_file(mtl_file_path, material_data.color_sets, material_data.material_definitions)
        
        root_obj.select_set(True)
        bpy.context.view_layer.objects.active = root_obj
        
        print("ExportMox.execute() OUT")

        return {'FINISHED'}
    
def menu_func_import(self, context):
    self.layout.operator(ImportMox.bl_idname, text="Landscape Object (.mox)")
    
def menu_func_export(self, context):
    self.layout.operator(ExportMox.bl_idname, text="Landscape Object (.mox)")
    
def register():
    bpy.utils.register_class(ImportMox)
    bpy.utils.register_class(ExportMox)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(ImportMox)
    bpy.utils.unregister_class(ExportMox)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)