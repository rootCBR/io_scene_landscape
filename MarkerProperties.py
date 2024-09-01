import bpy

from .Markers import *

class MarkerProperties(bpy.types.PropertyGroup):
    @abstractmethod
    def set_parameters(self, parameters : MarkerParameters) -> None:
        pass
    
    def get_parameters(self) -> MarkerParameters:
        pass

class GenericProperties(MarkerProperties):
    A: bpy.props.FloatProperty(name="A", default=0.0)
    B: bpy.props.FloatProperty(name="B", default=0.0)
    C: bpy.props.FloatProperty(name="C", default=0.0)
    color: bpy.props.FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        size=4,
        default=(1.0, 1.0, 1.0, 1.0),
        min=0.0, max=1.0,
    )
    
    def draw(self, context, layout):
        layout.prop(self, "A")
        layout.prop(self, "B")
        layout.prop(self, "C")
        layout.prop(self, "color")
        
    def set_parameters(self, parameters : GenericParameters) -> None:
        self.A = parameters.A
        self.B = parameters.B
        self.C = parameters.C
        self.color = parameters.color
        
    def get_parameters(self) -> GenericParameters:
        parameters = GenericParameters()
        parameters.A = self.A
        parameters.B = self.B
        parameters.C = self.C
        parameters.color = self.color
        return parameters

class GenericLightProperties(MarkerProperties):
    color: bpy.props.FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        size=4,
        default=(1.0, 1.0, 1.0, 1.0),
        min=0.0, max=1.0,
    )
    size: bpy.props.FloatProperty(name="Size", default=0.0)
    intensity: bpy.props.FloatProperty(name="Intensity", default=0.0)
    direction: bpy.props.FloatProperty(name="Direction", default=0.0)

    def draw(self, context, layout):
        layout.prop(self, "color")
        layout.prop(self, "size")
        layout.prop(self, "intensity")
        layout.prop(self, "direction")
        
    def set_parameters(self, parameters : GenericLightParameters) -> None:
        self.color = parameters.color
        self.size = parameters.size
        self.intensity = parameters.intensity
        self.direction = parameters.direction
        
    def get_parameters(self) -> GenericLightParameters:
        parameters = GenericLightParameters()
        parameters.color = self.color
        parameters.size = self.size
        parameters.intensity = self.intensity
        parameters.direction = self.direction
        return parameters

class NitroProperties(MarkerProperties):
    size_xy: bpy.props.FloatProperty(name="Size XY", default=0.0)
    size_z: bpy.props.FloatProperty(name="Size Z", default=0.0)
    
    def draw(self, context, layout):
        layout.prop(self, "size_xy")
        layout.prop(self, "size_z")
        
    def set_parameters(self, parameters : NitroParameters) -> None:
        self.size_xy = parameters.size_xy
        self.size_z = parameters.size_z
        
    def get_parameters(self) -> NitroParameters:
        parameters = NitroParameters()
        parameters.size_xy = self.size_xy
        parameters.size_z = self.size_z
        return parameters

class HeadlightProperties(MarkerProperties):
    color: bpy.props.FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        size=4,
        default=(1.0, 1.0, 1.0, 1.0),
        min=0.0, max=1.0,
    )
    size_normal: bpy.props.FloatProperty(name="Size Normal", default=0.0)
    size_flash: bpy.props.FloatProperty(name="Size Flash", default=0.0)
    size_at_day: bpy.props.FloatProperty(name="Size At Day", default=0.0)
    
    def draw(self, context, layout):
        layout.prop(self, "color")
        layout.prop(self, "size_normal")
        layout.prop(self, "size_flash")
        layout.prop(self, "size_at_day")
        
    def set_parameters(self, parameters : HeadlightParameters) -> None:
        self.color = parameters.color
        self.size_normal = parameters.size_normal
        self.size_flash = parameters.size_flash
        self.size_at_day = parameters.size_at_day
        
    def get_parameters(self) -> HeadlightParameters:
        parameters = HeadlightParameters()
        parameters.color = self.color
        parameters.size_normal = self.size_normal
        parameters.size_flash = self.size_flash
        parameters.size_at_day = self.size_at_day
        return parameters

class RearAndBrakeLightProperties(MarkerProperties):
    color: bpy.props.FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        size=4,
        default=(1.0, 1.0, 1.0, 1.0),
        min=0.0, max=1.0,
    )
    size_normal: bpy.props.FloatProperty(name="Size Normal", default=0.0)
    size_braking: bpy.props.FloatProperty(name="Size Braking", default=0.0)
    
    def draw(self, context, layout):
        layout.prop(self, "color")
        layout.prop(self, "size_normal")
        layout.prop(self, "size_braking")
        
    def set_parameters(self, parameters : RearAndBrakeLightParameters) -> None:
        self.color = parameters.color
        self.size_normal = parameters.size_normal
        self.size_braking = parameters.size_braking
        
    def get_parameters(self) -> RearAndBrakeLightParameters:
        parameters = RearAndBrakeLightParameters()
        parameters.color = self.color
        parameters.size_normal = self.size_normal
        parameters.size_braking = self.size_braking
        return parameters

class ReversingLightProperties(MarkerProperties):
    color: bpy.props.FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        size=4,
        default=(1.0, 1.0, 1.0, 1.0),
        min=0.0, max=1.0,
    )
    size: bpy.props.FloatProperty(name="Size", default=0.0)
    
    def draw(self, context, layout):
        layout.prop(self, "color")
        layout.prop(self, "size")
        
    def set_parameters(self, parameters : ReversingLightParameters) -> None:
        self.color = parameters.color
        self.size = parameters.size
        
    def get_parameters(self) -> ReversingLightParameters:
        parameters = ReversingLightParameters()
        parameters.color = self.color
        parameters.size = self.size
        return parameters

# IndicatorLeft, IndicatorRight
class BlinkingLightProperties(MarkerProperties):
    color: bpy.props.FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        size=4,
        default=(1.0, 1.0, 1.0, 1.0),
        min=0.0, max=1.0,
    )
    size: bpy.props.FloatProperty(name="Size", default=0.0)
    time_offset: bpy.props.FloatProperty(name="Time Offset", default=0.0)
    display_time: bpy.props.FloatProperty(name="Display Time", default=0.0)
    cycle_length: bpy.props.FloatProperty(name="Cycle Length", default=0.0)
    
    def draw(self, context, layout):
        layout.prop(self, "color")
        layout.prop(self, "size")
        layout.prop(self, "time_offset")
        layout.prop(self, "display_time")
        layout.prop(self, "cycle_length")
        
    def set_parameters(self, parameters : BlinkingLightParameters) -> None:
        self.color = parameters.color
        self.size = parameters.size
        self.time_offset = parameters.time_offset
        self.display_time = parameters.display_time
        self.cycle_length = parameters.cycle_length
        
    def get_parameters(self) -> BlinkingLightParameters:
        parameters = BlinkingLightParameters()
        parameters.color = self.color
        parameters.size = self.size
        parameters.time_offset = self.time_offset
        parameters.display_time = self.display_time
        parameters.cycle_length = self.cycle_length
        return parameters

class RotatingLightProperties(MarkerProperties):
    color: bpy.props.FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        size=4,
        default=(1.0, 1.0, 1.0, 1.0),
        min=0.0, max=1.0,
    )
    size: bpy.props.FloatProperty(name="Size", default=0.0)
    angle_offset: bpy.props.FloatProperty(name="Angle Offset", default=0.0)
    cycle_length: bpy.props.FloatProperty(name="Cycle Length", default=0.0)
    
    def draw(self, context, layout):
        layout.prop(self, "color")
        layout.prop(self, "size")
        layout.prop(self, "angle_offset")
        layout.prop(self, "cycle_length")
        
    def set_parameters(self, parameters : RotatingLightParameters) -> None:
        self.color = parameters.color
        self.size = parameters.size
        self.angle_offset = parameters.angle_offset
        self.cycle_length = parameters.cycle_length
        
    def get_parameters(self) -> RotatingLightParameters:
        parameters = RotatingLightParameters()
        parameters.color = self.color
        parameters.size = self.size
        parameters.angle_offset = self.angle_offset
        parameters.cycle_length = self.cycle_length
        return parameters

class TunnelLightProperties(MarkerProperties):
    color: bpy.props.FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        size=4,
        default=(1.0, 1.0, 1.0, 1.0),
        min=0.0, max=1.0,
    )
    
    def draw(self, context, layout):
        layout.prop(self, "color")
        
    def set_parameters(self, parameters : TunnelLightParameters) -> None:
        self.color = parameters.color
        
    def get_parameters(self) -> TunnelLightParameters:
        parameters = TunnelLightParameters()
        parameters.color = self.color
        return parameters

# Motor, DroneHook, WheelHook, TrailerHook, StreetHook
class NoProperties(MarkerProperties):
    def draw(self, context, layout):
        pass
    
    def set_parameters(self, parameters : NoParameters) -> None:
        pass
        
    def get_parameters(self) -> NoParameters:
        parameters = NoParameters()
        return parameters

# OldParticles, OldParticlesNoWind
class ParticleEmitterProperties(MarkerProperties):
    type_and_options: bpy.props.IntProperty(name="Type And Options", default=0)
    color: bpy.props.FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        size=4,
        default=(1.0, 1.0, 1.0, 1.0),
        min=0.0, max=1.0,
    )
    
    def draw(self, context, layout):
        layout.prop(self, "type_and_options")
        layout.prop(self, "color")
        
    def set_parameters(self, parameters : ParticleEmitterParameters) -> None:
        self.type_and_options = parameters.type_and_options
        self.color = parameters.color
        
    def get_parameters(self) -> ParticleEmitterParameters:
        parameters = ParticleEmitterParameters()
        parameters.type_and_options = self.type_and_options
        parameters.color = self.color
        return parameters

class MuzzleFlashProperties(MarkerProperties):
    offset: bpy.props.FloatProperty(name="Offset", default=0.0)
    
    def draw(self, context, layout):
        layout.prop(self, "offset")
        
    def set_parameters(self, parameters : MuzzleFlashParameters) -> None:
        self.offset = parameters.offset
        
    def get_parameters(self) -> MuzzleFlashParameters:
        parameters = MuzzleFlashParameters()
        parameters.offset = self.offset
        return parameters

class SoundEmitterProperties(MarkerProperties):
    name_offset: bpy.props.IntProperty(name="Name Offset", default=-1)
    reserved_1: bpy.props.IntProperty(name="Reserved 1", default=0)
    reserved_2: bpy.props.IntProperty(name="Reserved 2", default=0)
    reserved_3: bpy.props.IntProperty(name="Reserved 3", default=0)
    
    def draw(self, context, layout):
        layout.prop(self, "name_offset")
        layout.prop(self, "reserved_1")
        layout.prop(self, "reserved_2")
        layout.prop(self, "reserved_3")
        
    def set_parameters(self, parameters : SoundEmitterParameters) -> None:
        self.name_offset = parameters.name_offset
        self.reserved_1 = parameters.reserved_1
        self.reserved_2 = parameters.reserved_2
        self.reserved_3 = parameters.reserved_3
        
    def get_parameters(self) -> SoundEmitterParameters:
        parameters = SoundEmitterParameters()
        parameters.name_offset = self.name_offset
        parameters.reserved_1 = self.reserved_1
        parameters.reserved_2 = self.reserved_2
        parameters.reserved_3 = self.reserved_3
        return parameters
    
def register_marker_parameter_properties():
    bpy.utils.register_class(GenericProperties)
    bpy.utils.register_class(GenericLightProperties)
    bpy.utils.register_class(NitroProperties)
    bpy.utils.register_class(HeadlightProperties)
    bpy.utils.register_class(RearAndBrakeLightProperties)
    bpy.utils.register_class(ReversingLightProperties)
    bpy.utils.register_class(BlinkingLightProperties)
    bpy.utils.register_class(RotatingLightProperties)
    bpy.utils.register_class(TunnelLightProperties)
    bpy.utils.register_class(NoProperties)
    bpy.utils.register_class(ParticleEmitterProperties)
    bpy.utils.register_class(MuzzleFlashProperties)
    bpy.utils.register_class(SoundEmitterProperties)
    bpy.types.Object.marker_generic_properties = bpy.props.PointerProperty(type=GenericProperties)
    bpy.types.Object.marker_generic_light_properties = bpy.props.PointerProperty(type=GenericLightProperties)
    bpy.types.Object.marker_nitro_properties = bpy.props.PointerProperty(type=NitroProperties)
    bpy.types.Object.marker_headlight_properties = bpy.props.PointerProperty(type=HeadlightProperties)
    bpy.types.Object.marker_rear_and_brake_light_properties = bpy.props.PointerProperty(type=RearAndBrakeLightProperties)
    bpy.types.Object.marker_reversing_light_properties = bpy.props.PointerProperty(type=ReversingLightProperties)
    bpy.types.Object.marker_blinking_light_properties = bpy.props.PointerProperty(type=BlinkingLightProperties)
    bpy.types.Object.marker_rotating_light_properties = bpy.props.PointerProperty(type=RotatingLightProperties)
    bpy.types.Object.marker_tunnel_light_properties = bpy.props.PointerProperty(type=TunnelLightProperties)
    bpy.types.Object.marker_no_properties = bpy.props.PointerProperty(type=NoProperties)
    bpy.types.Object.marker_particle_emitter_properties = bpy.props.PointerProperty(type=ParticleEmitterProperties)
    bpy.types.Object.marker_muzzle_flash_properties = bpy.props.PointerProperty(type=MuzzleFlashProperties)
    bpy.types.Object.marker_sound_emitter_properties = bpy.props.PointerProperty(type=SoundEmitterProperties)

def unregister_marker_parameter_properties():
    del bpy.types.Object.marker_generic_properties
    del bpy.types.Object.marker_generic_light_properties
    del bpy.types.Object.marker_nitro_properties
    del bpy.types.Object.marker_headlight_properties
    del bpy.types.Object.marker_rear_and_brake_light_properties
    del bpy.types.Object.marker_reversing_light_properties
    del bpy.types.Object.marker_blinking_light_properties
    del bpy.types.Object.marker_rotating_light_properties
    del bpy.types.Object.marker_tunnel_light_properties
    del bpy.types.Object.marker_no_properties
    del bpy.types.Object.marker_particle_emitter_properties
    del bpy.types.Object.marker_muzzle_flash_properties
    del bpy.types.Object.marker_sound_emitter_properties
    bpy.utils.unregister_class(GenericProperties)
    bpy.utils.unregister_class(GenericLightProperties)
    bpy.utils.unregister_class(NitroProperties)
    bpy.utils.unregister_class(HeadlightProperties)
    bpy.utils.unregister_class(RearAndBrakeLightProperties)
    bpy.utils.unregister_class(ReversingLightProperties)
    bpy.utils.unregister_class(BlinkingLightProperties)
    bpy.utils.unregister_class(RotatingLightProperties)
    bpy.utils.unregister_class(TunnelLightProperties)
    bpy.utils.unregister_class(NoProperties)
    bpy.utils.unregister_class(ParticleEmitterProperties)
    bpy.utils.unregister_class(MuzzleFlashProperties)
    bpy.utils.unregister_class(SoundEmitterProperties)
    
if __name__ == "__main__":
    register_marker_parameter_properties()