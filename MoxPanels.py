import bpy

from .MarkerProperties import *
from .Markers import *
from .MoxParts import *

from mathutils import Vector
import math

part_type_enum = [
    (PartType.DISABLE.name, 'Disable', 'Description'),
    (PartType.X.name, 'X', 'Description'),
    (PartType.Y.name, 'Y', 'Description'),
    (PartType.XYZ.name, 'XYZ', 'Description'),
    (PartType.EXHAUST.name, 'Exhaust', 'Description'),
    (PartType.SUSPENSION.name, 'Suspension', 'Description'),
    (PartType.BOX.name, 'Box', 'Description')
]

marker_type_enum = [
    (MarkerType.UNKNOWN.name, 'Unknown', 'Description'),
    (MarkerType.NITRO.name, 'Nitro', 'Description'),
    (MarkerType.HEADLIGHT.name, 'Headlight', 'Description'),
    (MarkerType.REAR_AND_BRAKE_LIGHT.name, 'Rear And Brake Light', 'Description'),
    (MarkerType.REVERSING_LIGHT.name, 'Reversing Light', 'Description'),
    (MarkerType.INDICATOR_LEFT.name, 'Indicator Left', 'Description'),
    (MarkerType.INDICATOR_RIGHT.name, 'Indicator Right', 'Description'),
    (MarkerType.GENERIC_LIGHT.name, 'Generic Light', 'Description'),
    (MarkerType.BLINKING_LIGHT.name, 'Blinking Light', 'Description'),
    (MarkerType.ROTATING_LIGHT.name, 'Rotating Light', 'Description'),
    (MarkerType.TUNNEL_LIGHT.name, 'Tunnel Light', 'Description'),
    (MarkerType.MOTOR.name, 'Motor', 'Description'),
    (MarkerType.DRONE_HOOK.name, 'Drone Hook', 'Description'),
    (MarkerType.WHEEL_HOOK.name, 'Wheel Hook', 'Description'),
    (MarkerType.TRAILER_HOOK.name, 'Trailer Hook', 'Description'),
    (MarkerType.STREET_HOOK.name, 'Street Hook', 'Description'),
    (MarkerType.OLD_PARTICLES.name, 'Old Particles', 'Description'),
    (MarkerType.MUZZLE_FLASH.name, 'Muzzle Flash', 'Description'),
    (MarkerType.OLD_PARTICLES_NO_WIND.name, 'Old Particles No Wind', 'Description'),
    (MarkerType.PARTICLE_EMITTER.name, 'Particle Emitter', 'Description'),
    (MarkerType.SOUND_EMITTER.name, 'Sound Emitter', 'Description'),
    (MarkerType.INVALID.name, 'Invalid', 'Description')
]

marker_type_to_property = {
    MarkerType.UNKNOWN.name: "no_properties",
    MarkerType.NITRO.name: "nitro_properties",
    MarkerType.HEADLIGHT.name: "headlight_properties",
    MarkerType.REAR_AND_BRAKE_LIGHT.name: "rear_and_brake_light_properties",
    MarkerType.REVERSING_LIGHT.name: "reversing_light_properties",
    MarkerType.INDICATOR_LEFT.name: "blinking_light_properties",
    MarkerType.INDICATOR_RIGHT.name: "blinking_light_properties",
    MarkerType.GENERIC_LIGHT.name: "generic_light_properties",
    MarkerType.BLINKING_LIGHT.name: "blinking_light_properties",
    MarkerType.ROTATING_LIGHT.name: "rotating_light_properties",
    MarkerType.TUNNEL_LIGHT.name: "tunnel_light_properties",
    MarkerType.MOTOR.name: "no_properties",
    MarkerType.DRONE_HOOK.name: "no_properties",
    MarkerType.WHEEL_HOOK.name: "no_properties",
    MarkerType.TRAILER_HOOK.name: "no_properties",
    MarkerType.STREET_HOOK.name: "no_properties",
    MarkerType.OLD_PARTICLES.name: "particle_emitter_properties",
    MarkerType.MUZZLE_FLASH.name: "muzzle_flash_properties",
    MarkerType.OLD_PARTICLES_NO_WIND.name: "particle_emitter_properties",
    MarkerType.PARTICLE_EMITTER.name: "particle_emitter_properties",
    MarkerType.SOUND_EMITTER.name: "sound_emitter_properties",
    MarkerType.INVALID.name: "no_properties"
}

def calculate_part_properties(obj):
    part_properties = obj.mox_part_properties
            
    mesh = obj.data
            
    mesh.update()

    min_x, min_y, min_z = math.inf, math.inf, math.inf
    max_x, max_y, max_z = -math.inf, -math.inf, -math.inf
            
    centroid = Vector((0.0, 0.0, 0.0))

    for vertex in mesh.vertices:
        co = obj.matrix_world @ vertex.co
        min_x = min(min_x, co.x)
        min_y = min(min_y, co.y)
        min_z = min(min_z, co.z)
        max_x = max(max_x, co.x)
        max_y = max(max_y, co.y)
        max_z = max(max_z, co.z)
                
        centroid += vertex.co

    min_extents = Vector((min_x, min_y, min_z))
    max_extents = Vector((max_x, max_y, max_z))
    
    dimensions = max_extents - min_extents

    dimensions_world = obj.matrix_world.to_scale() * dimensions
            
    max_dimension = max(abs(min_x), abs(min_y), abs(min_z), abs(max_x), abs(max_y), abs(max_z))
    
    centroid /= len(mesh.vertices)
            
    radius = max_dimension / 2.0 # ?

    part_properties.center = centroid
    part_properties.radius = radius

class MoxPartCalculationOperator(bpy.types.Operator):
    bl_idname = "object.mox_part_calculate"
    bl_label = "Calculate Test"
    bl_description = "Calculate the center and radius of this part"

    def execute(self, context):
        obj = context.object
        
        if obj.type == 'MESH':
            calculate_part_properties(obj)

        return {'FINISHED'}
    
class MoxPartProperties(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(name="_Enabled")
    type: bpy.props.EnumProperty(
        name="Type",
        description="Description",
        items=part_type_enum
    )
    enable_deformation: bpy.props.BoolProperty(name="Enable Deformation", default=True)
    enable_detachment: bpy.props.BoolProperty(name="Enable Detachment", default=True)
    enable_animation: bpy.props.BoolProperty(name="Enable Animation", default=True)
    swing_min: bpy.props.FloatVectorProperty(name='Min Swing', subtype='XYZ')
    swing_max: bpy.props.FloatVectorProperty(name='Max Swing', subtype='XYZ')
    center: bpy.props.FloatVectorProperty(name='Center', subtype='XYZ')
    radius: bpy.props.FloatProperty(name="Radius", default=0.5)
    
    def draw(self, context, layout):
        layout.label(text="Part")
        layout.prop(self, "type")
        layout.prop(self, "enable_deformation")
        layout.prop(self, "enable_detachment")
        layout.prop(self, "enable_animation")
        layout.prop(self, "swing_min")
        layout.prop(self, "swing_max")
        layout.prop(self, "center")
        layout.prop(self, "radius")
        layout.operator("object.mox_part_calculate", text="Calculate")
    
class MoxMarkerProperties(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(name="_Enabled")
    type: bpy.props.EnumProperty(
        name="Type",
        description="Description",
        items=marker_type_enum
    )
    part: bpy.props.PointerProperty(name="Part", type=bpy.types.Object)
    generic_properties: bpy.props.PointerProperty(type=GenericProperties)
    generic_light_properties: bpy.props.PointerProperty(type=GenericLightProperties)
    nitro_properties: bpy.props.PointerProperty(type=NitroProperties)
    headlight_properties: bpy.props.PointerProperty(type=HeadlightProperties)
    rear_and_brake_light_properties: bpy.props.PointerProperty(type=RearAndBrakeLightProperties)
    reversing_light_properties: bpy.props.PointerProperty(type=ReversingLightProperties)
    blinking_light_properties: bpy.props.PointerProperty(type=BlinkingLightProperties)
    rotating_light_properties: bpy.props.PointerProperty(type=RotatingLightProperties)
    tunnel_light_properties: bpy.props.PointerProperty(type=TunnelLightProperties)
    no_properties: bpy.props.PointerProperty(type=NoProperties)
    particle_emitter_properties: bpy.props.PointerProperty(type=ParticleEmitterProperties)
    muzzle_flash_properties: bpy.props.PointerProperty(type=MuzzleFlashProperties)
    sound_emitter_properties: bpy.props.PointerProperty(type=SoundEmitterProperties)
    
    def draw(self, context, layout):
        layout.label(text="Marker")
        layout.prop(self, "type")
        layout.prop(self, "part")
        
        type_name = self.type
        prop = None
        
        if type_name == MarkerType.UNKNOWN.name:
            prop = self.no_properties
        elif type_name == MarkerType.NITRO.name:
            prop = self.nitro_properties
        elif type_name == MarkerType.HEADLIGHT.name:
            prop = self.headlight_properties
        elif type_name == MarkerType.REAR_AND_BRAKE_LIGHT.name:
            prop = self.rear_and_brake_light_properties
        elif type_name == MarkerType.REVERSING_LIGHT.name:
            prop = self.reversing_light_properties
        elif type_name == MarkerType.INDICATOR_LEFT.name:
            prop = self.blinking_light_properties
        elif type_name == MarkerType.INDICATOR_RIGHT.name:
            prop = self.blinking_light_properties
        elif type_name == MarkerType.GENERIC_LIGHT.name:
            prop = self.generic_light_properties
        elif type_name == MarkerType.BLINKING_LIGHT.name:
            prop = self.blinking_light_properties
        elif type_name == MarkerType.ROTATING_LIGHT.name:
            prop = self.rotating_light_properties
        elif type_name == MarkerType.TUNNEL_LIGHT.name:
            prop = self.tunnel_light_properties
        elif type_name == MarkerType.MOTOR.name:
            prop = self.no_properties
        elif type_name == MarkerType.DRONE_HOOK.name:
            prop = self.no_properties
        elif type_name == MarkerType.WHEEL_HOOK.name:
            prop = self.no_properties
        elif type_name == MarkerType.TRAILER_HOOK.name:
            prop = self.no_properties
        elif type_name == MarkerType.STREET_HOOK.name:
            prop = self.no_properties
        elif type_name == MarkerType.OLD_PARTICLES.name:
            prop = self.particle_emitter_properties
        elif type_name == MarkerType.MUZZLE_FLASH.name:
            prop = self.muzzle_flash_properties
        elif type_name == MarkerType.OLD_PARTICLES_NO_WIND.name:
            prop = self.particle_emitter_properties
        elif type_name == MarkerType.PARTICLE_EMITTER.name:
            prop = self.particle_emitter_properties
        elif type_name == MarkerType.SOUND_EMITTER.name:
            prop = self.sound_emitter_properties
        elif type_name == MarkerType.INVALID.name:
            prop = self.no_properties
            
        prop.draw(context, layout)
    
class OBJECT_PT_mox(bpy.types.Panel):
    bl_label = "MOX"
    bl_idname = "OBJECT_PT_mox"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        if obj.type == 'MESH':
            if hasattr(obj, "mox_part_properties"):
                obj.mox_part_properties.draw(context, layout)
        elif obj.type == 'EMPTY':
            if hasattr(obj, "mox_marker_properties"):
                obj.mox_marker_properties.draw(context, layout)

def register():
    register_marker_parameter_properties()
    bpy.utils.register_class(MoxPartCalculationOperator)
    bpy.utils.register_class(MoxPartProperties)
    bpy.utils.register_class(MoxMarkerProperties)
    bpy.types.Object.mox_part_properties = bpy.props.PointerProperty(type=MoxPartProperties)
    bpy.types.Object.mox_marker_properties = bpy.props.PointerProperty(type=MoxMarkerProperties)
    bpy.utils.register_class(OBJECT_PT_mox)

def unregister():
    unregister_marker_parameter_properties()
    del bpy.types.Object.mox_part_properties
    del bpy.types.Object.mox_marker_properties
    bpy.utils.unregister_class(MoxPartCalculationOperator)
    bpy.utils.unregister_class(MoxPartProperties)
    bpy.utils.unregister_class(MoxMarkerProperties)
    bpy.utils.unregister_class(OBJECT_PT_mox)
    
if __name__ == "__main__":
    register()