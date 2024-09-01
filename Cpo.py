
import bpy
import struct
import io

from enum import Enum
from abc import ABC, abstractmethod
from io import BufferedReader, BufferedWriter

class CpoShapeData(ABC):
    @abstractmethod
    def deserialize(self, file : BufferedReader) -> None:
        pass
    
    @abstractmethod
    def serialize(self, file : BufferedWriter) -> None:
        pass
    
class CpoShapeDataSphere(CpoShapeData):
    def __init__(self):
        pass
        
    def deserialize(self, reader : BufferedReader):
        pass
    
    def serialize(self, writer : BufferedWriter):
        pass
    
class CpoShapeDataBox(CpoShapeData):
    def __init__(self):
        pass
        
    def deserialize(self, reader : BufferedReader):
        pass
    
    def serialize(self, writer : BufferedWriter):
        pass
    
class CpoShapeDataMesh(CpoShapeData):
    def __init__(self):
        self.vertices = []
        self.polygons = []
        self.position_x = 0.0
        self.position_y = 0.0
        self.position_z = 0.0
        self.matrix = []
        
    def deserialize(self, reader : BufferedReader):
        read = struct.unpack('4I', reader.read(16))
        
        number_of_vertices = read[0]
        number_of_polygons = read[1]
        size_of_polygons = read[2]
        _ = read[3]
        
        for i in range(number_of_vertices):
            vertex = CpoVertex()
            vertex.deserialize(reader)
            self.vertices.append(vertex)
            
        for i in range(number_of_polygons):
            polygon = CpoPolygon()
            polygon.deserialize(reader)
            self.polygons.append(polygon)
            
        read = struct.unpack('3f', reader.read(12))
        self.position_x = read[0]
        self.position_y = read[1]
        self.position_z = read[2]
        
        read = struct.unpack('9f', reader.read(36))
        self.matrix = [
            [ read[0],  read[1], read[2]],
            [ read[3],  read[4], read[5]],
            [ read[6],  read[7], read[8]]
        ]
    
    def serialize(self, writer : BufferedWriter):
        number_of_vertices = len(self.vertices)
        number_of_polygons = len(self.polygons)
        
        polygons_buffer = io.BytesIO()
        polygons_writer = io.BufferedWriter(polygons_buffer)
        
        for i in range(number_of_polygons):
            polygon : CpoPolygon = self.polygons[i]
            polygon.serialize(polygons_writer)
            
        polygons_writer.flush()
            
        size_of_polygons = polygons_writer.tell()
            
        writer.write(struct.pack("4I", 
            number_of_vertices, 
            number_of_polygons, 
            size_of_polygons,
            0
        ))
        
        for i in range(number_of_vertices):
            vertex : CpoVertex = self.vertices[i]
            vertex.serialize(writer)
            
        polygons_writer.seek(0)
        
        writer.write(polygons_buffer.getvalue())
        
        writer.write(struct.pack("3f", 
            self.position_x, 
            self.position_y, 
            self.position_z
        ))
        
        input_matrix = self.matrix

        matrix = [
            [ input_matrix[0][0],  input_matrix[0][1], input_matrix[0][2]],
            [ input_matrix[1][0],  input_matrix[1][1], input_matrix[1][2]],
            [ input_matrix[2][0],  input_matrix[2][1], input_matrix[2][2]]
        ]
        
        matrix_flat = [item for sublist in matrix for item in sublist]
        
        writer.write(struct.pack("9f", *matrix_flat))
    
class CpoShape:
    def __init__(self):
        self.type = 0
        self.data : CpoShapeData = None
        
    def deserialize(self, reader : BufferedReader):
        self.type = struct.unpack('I', reader.read(4))[0]
        
        if self.type == 1:
            self.data = CpoShapeDataSphere()
        elif self.type == 2:
            self.data = CpoShapeDataBox()
        elif self.type == 3:
            self.data = CpoShapeDataMesh()
        
        self.data.deserialize(reader)
    
    def serialize(self, writer : BufferedWriter):
        writer.write(struct.pack("I", self.type))
        self.data.serialize(writer)
    
class CpoVertex:
    def __init__(self):
        self.position_x = 0.0
        self.position_y = 0.0
        self.position_z = 0.0
        
    def deserialize(self, reader : BufferedReader):
        read = struct.unpack('3f', reader.read(12))
        self.position_x = read[0]
        self.position_y = read[1]
        self.position_z = read[2]
    
    def serialize(self, writer : BufferedWriter):
        writer.write(struct.pack("3f", 
            self.position_x, 
            self.position_y, 
            self.position_z
        ))
        
class CpoPolygon:
    def __init__(self):
        self.vertex_indices = []
        
    def deserialize(self, reader : BufferedReader):
        read = struct.unpack('H', reader.read(2))
        
        number_of_vertex_indices = read[0]
        
        for i in range(number_of_vertex_indices):
            read = struct.unpack('H', reader.read(2))
            
            vertex_index = read[0]
            
            self.vertex_indices.append(vertex_index)

    def serialize(self, writer : BufferedWriter):
        number_of_vertex_indices = len(self.vertex_indices)
        
        writer.write(struct.pack("H", number_of_vertex_indices))
        
        for i in range(number_of_vertex_indices):
            vertex_index = self.vertex_indices[i]
            
            writer.write(struct.pack("H", vertex_index))
    
class CpoFile:
    def __init__(self):
        self.shapes = []
        
    def deserialize(self, reader : BufferedReader):
        read = struct.unpack('4I', reader.read(16))
            
        _ = read[0]
        number_of_shapes = read[1]
        _ = read[2]
        _ = read[3]
        
        for i in range(number_of_shapes):
            shape = CpoShape()
            shape.deserialize(reader)
            self.shapes.append(shape)
    
    def serialize(self, writer : BufferedWriter):
        number_of_shapes = len(self.shapes)
        
        writer.write(struct.pack("4I", 
            0x43504f21, 
            number_of_shapes, 
            0,
            0
        ))
        
        for i in range(number_of_shapes):
            shape = self.shapes[i]
            shape.serialize(writer)