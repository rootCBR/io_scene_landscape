
from re import A
import bpy
import struct

from enum import Enum
from abc import ABC, abstractmethod
from io import BufferedReader, BufferedWriter

class MarkerType(Enum):
    UNKNOWN = 0
    NITRO = 1                   # "Nitro"
    HEADLIGHT = 2               # "Scheinwerfer"
    REAR_AND_BRAKE_LIGHT = 3    # "Rück-/Bremslicht"
    REVERSING_LIGHT = 4         # "Rueckscheinwerfer"
    INDICATOR_LEFT = 5          # "Blinker links"
    INDICATOR_RIGHT = 6         # "Blinker rechts"
    GENERIC_LIGHT = 7           # "Leuchtendes Licht"
    BLINKING_LIGHT = 8          # "Blinklicht"
    ROTATING_LIGHT = 9          # "Drehlicht"
    TUNNEL_LIGHT = 10           # "Tunnellicht"
    MOTOR = 16                  # "Motor"
    DRONE_HOOK = 17             # "Minicar Halterung"
    WHEEL_HOOK = 20             # "Rad"
    TRAILER_HOOK = 24           # "Hänger"
    STREET_HOOK = 28            # "Straßenanschluß"
    OLD_PARTICLES = 32          # deprecated converted to ParticleEmitter
    MUZZLE_FLASH = 33           # "Mündungsfeuer"
    OLD_PARTICLES_NO_WIND = 34  # deprecated converted to ParticleEmitter
    PARTICLE_EMITTER = 35       # "Partikelemitter"
    SOUND_EMITTER = 36          # "Soundemitter"
    INVALID = 255

def to_color(color_int : int) -> ():
    r = ((color_int >> 16) & 0xFF) / 0xFF
    g = ((color_int >> 8) & 0xFF) / 0xFF
    b = ((color_int >> 0) & 0xFF) / 0xFF
    a = ((color_int >> 24) & 0xFF) / 0xFF
    
    color = (r, g, b, a)
    
    return color

def from_color(color : ()) -> int:
    
    r = color[0]
    g = color[1]
    b = color[2]
    a = color[3]
    
    color_int = 0
    color_int |= (int(r * 0xFF) & 0xFF) << 16
    color_int |= (int(g * 0xFF) & 0xFF) << 8
    color_int |= (int(b * 0xFF) & 0xFF) << 0
    color_int |= (int(a * 0xFF) & 0xFF) << 24
    
    return color_int

class MarkerParameters(ABC):
    @abstractmethod
    def deserialize(self, file : BufferedReader) -> None:
        pass
    
    @abstractmethod
    def serialize(self, file : BufferedWriter) -> None:
        pass
    
    @abstractmethod
    def from_generic(self, generic_parameters : 'GenericParameters') -> None:
        pass
    
    @abstractmethod
    def to_generic(self) -> 'GenericParameters':
        pass

class GenericParameters(MarkerParameters):
    def __init__(self):
        self.A = 0.0
        self.B = 0.0
        self.C = 0.0
        self.color = (1.0, 1.0, 1.0, 1.0)
        
    def deserialize(self, file : BufferedReader) -> None:
        read = struct.unpack('3f I', file.read(16))
        
        self.A = read[0]
        self.B = read[1]
        self.C = read[2]
        self.color = to_color(read[3])
        
        if True:
            print("")
            print("A:", self.A)
            print("B:", self.B)
            print("C:", self.C)
            print("color:", self.color)
    
    def serialize(self, file : BufferedWriter) -> None:
        file.write(struct.pack('3f I', 
            self.A,
            self.B,
            self.C,
            from_color(self.color)
        ))
    
    def from_generic(self, generic_parameters : 'GenericParameters') -> None:
        pass
    
    def to_generic(self) -> 'GenericParameters':
        pass

class GenericLightParameters(MarkerParameters):
    def __init__(self):
        self.color = (1.0, 1.0, 1.0, 1.0)
        self.size = 0.0
        self.intensity = 0.0
        self.direction = 0.0
    
    def deserialize(self, file : BufferedReader) -> None:
        read = struct.unpack('I 3f', file.read(16))
        
        self.color = to_color(read[0])
        self.size = read[1]
        self.intensity = read[2]
        self.direction = read[3]
    
    def serialize(self, file : BufferedWriter) -> None:
        file.write(struct.pack('I 3f', 
            from_color(self.color),
            self.size,
            self.intensity,
            self.direction
        ))
    
    def from_generic(self, generic_parameters : GenericParameters) -> None:
        self.color = generic_parameters.color
        self.size = generic_parameters.A
        self.intensity = generic_parameters.B
        self.direction = generic_parameters.C
    
    def to_generic(self) -> GenericParameters:
        result = GenericParameters()
        result.A = self.size
        result.B = self.intensity
        result.C = self.direction
        result.color = self.color
        return result

class NitroParameters(MarkerParameters):
    def __init__(self):
        self.size_xy = 0.0
        self.size_z = 0.0
    
    def deserialize(self, file : BufferedReader) -> None:
        read = struct.unpack('2f', file.read(8))
        
        self.size_xy = read[0]
        self.size_z = read[1]
    
    def serialize(self, file : BufferedWriter) -> None:
        file.write(struct.pack('2f', 
            self.size_xy,
            self.size_z
        ))
    
    def from_generic(self, generic_parameters : GenericParameters) -> None:
        self.size_xy = generic_parameters.A
        self.size_z = generic_parameters.B
    
    def to_generic(self) -> GenericParameters:
        result = GenericParameters()
        result.A = self.size_xy
        result.B = self.size_z
        return result

class HeadlightParameters(MarkerParameters):
    def __init__(self):
        self.color = (1.0, 1.0, 1.0, 1.0)
        self.size_normal = 0.0
        self.size_flash = 0.0
        self.size_at_day = 0.0
    
    def deserialize(self, file : BufferedReader) -> None:
        read = struct.unpack('I 3f', file.read(16))
        
        self.color = to_color(read[0])
        self.size_normal = read[1]
        self.size_flash = read[2]
        self.size_at_day = read[3]
    
    def serialize(self, file : BufferedWriter) -> None:
        file.write(struct.pack('I 3f', 
            from_color(self.color),
            self.size_normal,
            self.size_flash,
            self.size_at_day
        ))
    
    def from_generic(self, generic_parameters : GenericParameters) -> None:
        self.color = generic_parameters.color
        self.size_normal = generic_parameters.A
        self.size_flash = generic_parameters.B
        self.size_at_day = generic_parameters.C
    
    def to_generic(self) -> GenericParameters:
        result = GenericParameters()
        result.A = self.size_normal
        result.B = self.size_flash
        result.C = self.size_at_day
        result.color = self.color
        return result

class RearAndBrakeLightParameters(MarkerParameters):
    def __init__(self):
        self.color = (1.0, 1.0, 1.0, 1.0)
        self.size_normal = 0.0
        self.size_braking = 0.0
    
    def deserialize(self, file : BufferedReader) -> None:
        read = struct.unpack('I 2f', file.read(12))
        
        self.color = to_color(read[0])
        self.size_normal = read[1]
        self.size_braking = read[2]
    
    def serialize(self, file : BufferedWriter) -> None:
        file.write(struct.pack('I 2f', 
            from_color(self.color),
            self.size_normal,
            self.size_braking
        ))
    
    def from_generic(self, generic_parameters : GenericParameters) -> None:
        self.color = generic_parameters.color
        self.size_normal = generic_parameters.A
        self.size_braking = generic_parameters.B
    
    def to_generic(self) -> GenericParameters:
        result = GenericParameters()
        result.A = self.size_normal
        result.B = self.size_braking
        result.color = self.color
        return result

class ReversingLightParameters(MarkerParameters):
    def __init__(self):
        self.color = (1.0, 1.0, 1.0, 1.0)
        self.size = 0.0
    
    def deserialize(self, file : BufferedReader) -> None:
        read = struct.unpack('I f', file.read(8))
        
        self.color = to_color(read[0])
        self.size = read[1]
    
    def serialize(self, file : BufferedWriter) -> None:
        file.write(struct.pack('I f', 
            from_color(self.color),
            self.size
        ))
    
    def from_generic(self, generic_parameters : GenericParameters) -> None:
        self.color = generic_parameters.color
        self.size = generic_parameters.A
    
    def to_generic(self) -> GenericParameters:
        result = GenericParameters()
        result.A = self.size
        result.color = self.color
        return result

# IndicatorLeft, IndicatorRight
class BlinkingLightParameters(MarkerParameters):
    def __init__(self):
        self.color = (1.0, 1.0, 1.0, 1.0)
        self.size = 0.0
        self.time_offset = 0.0
        self.display_time = 0.0
        self.cycle_length = 0.0
    
    def deserialize(self, file : BufferedReader) -> None:
        read = struct.unpack('I 4f', file.read(20))
        
        self.color = to_color(read[0])
        self.size = read[1]
        self.time_offset = read[2]
        self.display_time = read[3]
        self.cycle_length = read[4]
    
    def serialize(self, file : BufferedWriter) -> None:
        file.write(struct.pack('I 4f', 
            from_color(self.color),
            self.size,
            self.time_offset,
            self.display_time,
            self.cycle_length
        ))
    
    def from_generic(self, generic_parameters : GenericParameters) -> None:
        self.color = generic_parameters.color
        self.size = generic_parameters.A
        self.time_offset = generic_parameters.B
        self.display_time = generic_parameters.C
    
    def to_generic(self) -> GenericParameters:
        result = GenericParameters()
        result.A = self.size
        result.B = self.time_offset
        result.C = self.display_time
        result.color = self.color
        return result

class RotatingLightParameters(MarkerParameters):
    def __init__(self):
        self.color = (1.0, 1.0, 1.0, 1.0)
        self.size = 0.0
        self.angle_offset = 0.0
        self.cycle_length = 0.0
    
    def deserialize(self, file : BufferedReader) -> None:
        read = struct.unpack('I 3f', file.read(16))
        
        self.color = to_color(read[0])
        self.size = read[1]
        self.angle_offset = read[2]
        self.cycle_length = read[3]
    
    def serialize(self, file : BufferedWriter) -> None:
        file.write(struct.pack('I 3f', 
            from_color(self.color),
            self.size,
            self.angle_offset,
            self.cycle_length
        ))
    
    def from_generic(self, generic_parameters : GenericParameters) -> None:
        self.color = generic_parameters.color
        self.size = generic_parameters.A
        self.angle_offset = generic_parameters.B
        self.cycle_length = generic_parameters.C
    
    def to_generic(self) -> GenericParameters:
        result = GenericParameters()
        result.A = self.size
        result.B = self.angle_offset
        result.C = self.cycle_length
        result.color = self.color
        return result

class TunnelLightParameters(MarkerParameters):
    def __init__(self):
        self.color = (1.0, 1.0, 1.0, 1.0)
    
    def deserialize(self, file : BufferedReader) -> None:
        read = struct.unpack('I', file.read(4))
        
        self.color = to_color(read[0])
    
    def serialize(self, file : BufferedWriter) -> None:
        file.write(struct.pack('I', 
            from_color(self.color)
        ))
    
    def from_generic(self, generic_parameters : GenericParameters) -> None:
        self.color = generic_parameters.color
    
    def to_generic(self) -> GenericParameters:
        result = GenericParameters()
        result.color = self.color
        return result

# Motor, DroneHook, WheelHook, TrailerHook, StreetHook
class NoParameters(MarkerParameters):
    def __init__(self):
        pass
    
    def deserialize(self, file : BufferedReader) -> None:
        pass
    
    def serialize(self, file : BufferedWriter) -> None:
        pass
    
    def from_generic(self, generic_parameters : GenericParameters) -> None:
        pass
    
    def to_generic(self) -> GenericParameters:
        result = GenericParameters()
        return result

# OldParticles, OldParticlesNoWind
class ParticleEmitterParameters(MarkerParameters):
    def __init__(self):
        self.type_and_options = 0
        self.color = (1.0, 1.0, 1.0, 1.0)
    
    def deserialize(self, file : BufferedReader) -> None:
        read = struct.unpack('2I', file.read(8))
        
        self.type_and_options = read[0]
        self.color = to_color(read[1])
    
    def serialize(self, file : BufferedWriter) -> None:
        file.write(struct.pack('2I', 
            self.type_and_options,
            from_color(self.color)
        ))
    
    def from_generic(self, generic_parameters : GenericParameters) -> None:
        self.color = generic_parameters.color
    
    def to_generic(self) -> GenericParameters:
        result = GenericParameters()
        result.color = self.color
        return result

class MuzzleFlashParameters(MarkerParameters):
    def __init__(self):
        self.offset = 0.0
    
    def deserialize(self, file : BufferedReader) -> None:
        read = struct.unpack('f', file.read(4))
        
        self.offset = read[0]
    
    def serialize(self, file : BufferedWriter) -> None:
        file.write(struct.pack('f', 
            self.offset
        ))
    
    def from_generic(self, generic_parameters : GenericParameters) -> None:
        self.offset = generic_parameters.A
    
    def to_generic(self) -> GenericParameters:
        result = GenericParameters()
        result.A = self.offset
        return result

class SoundEmitterParameters(MarkerParameters):
    def __init__(self):
        self.name_offset = -1
        self.reserved_1 = 0
        self.reserved_2 = 0
        self.reserved_3 = 0
    
    def deserialize(self, file : BufferedReader) -> None:
        read = struct.unpack('i 3I', file.read(16))
        
        self.name_offset = read[0]
        self.reserved_1 = read[1]
        self.reserved_2 = read[2]
        self.reserved_3 = read[3]
    
    def serialize(self, file : BufferedWriter) -> None:
        file.write(struct.pack('i 3I', 
            self.name_offset,
            self.reserved_1,
            self.reserved_2,
            self.reserved_3
        ))
    
    def from_generic(self, generic_parameters : GenericParameters) -> None:
        pass
    
    def to_generic(self) -> GenericParameters:
        pass
    
def get_marker_parameters_class(input_type):
    type = MarkerType(input_type)
    result = None
    if type == MarkerType.UNKNOWN:
        result = NoParameters
    elif type == MarkerType.INVALID:
        result = NoParameters
    elif type == MarkerType.NITRO:
        result = NitroParameters
    elif type == MarkerType.HEADLIGHT:
        result = HeadlightParameters
    elif type == MarkerType.REAR_AND_BRAKE_LIGHT:
        result = RearAndBrakeLightParameters
    elif type == MarkerType.REVERSING_LIGHT:
        result = ReversingLightParameters
    elif type == MarkerType.INDICATOR_LEFT:
        result = BlinkingLightParameters
    elif type == MarkerType.INDICATOR_RIGHT:
        result = BlinkingLightParameters
    elif type == MarkerType.GENERIC_LIGHT:
        result = GenericLightParameters
    elif type == MarkerType.BLINKING_LIGHT:
        result = BlinkingLightParameters
    elif type == MarkerType.ROTATING_LIGHT:
        result = RotatingLightParameters
    elif type == MarkerType.TUNNEL_LIGHT:
        result = TunnelLightParameters
    elif type == MarkerType.MOTOR:
        result = NoParameters
    elif type == MarkerType.DRONE_HOOK:
        result = NoParameters
    elif type == MarkerType.WHEEL_HOOK:
        result = NoParameters
    elif type == MarkerType.TRAILER_HOOK:
        result = NoParameters
    elif type == MarkerType.STREET_HOOK:
        result = NoParameters
    elif type == MarkerType.OLD_PARTICLES:
        result = ParticleEmitterParameters
    elif type == MarkerType.MUZZLE_FLASH:
        result = MuzzleFlashParameters
    elif type == MarkerType.OLD_PARTICLES_NO_WIND:
        result = ParticleEmitterParameters
    elif type == MarkerType.PARTICLE_EMITTER:
        result = ParticleEmitterParameters
    elif type == MarkerType.SOUND_EMITTER:
        result = SoundEmitterParameters
    print("result:", result)
    return result
    