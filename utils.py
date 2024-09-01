
from mathutils import Vector, Matrix

def swap_yz_axes_of_quaternion(quat):
    rotation_matrix = quat.to_matrix().to_4x4()
    
    # Swap Y and Z axes in the rotation matrix
    swapped_matrix = Matrix((
        (rotation_matrix[0][0], rotation_matrix[0][2], rotation_matrix[0][1], rotation_matrix[0][3]),
        (rotation_matrix[2][0], rotation_matrix[2][2], rotation_matrix[2][1], rotation_matrix[2][3]),
        (rotation_matrix[1][0], rotation_matrix[1][2], rotation_matrix[1][1], rotation_matrix[1][3]),
        (rotation_matrix[3][0], rotation_matrix[3][2], rotation_matrix[3][1], rotation_matrix[3][3])
    ))
    
    adjusted_quat = swapped_matrix.to_quaternion()
    
    return adjusted_quat

def decompose_and_apply_matrix(obj, matrix, scale_correction_factor=1.0):
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
    
    translation /= scale_correction_factor
    
    quaternion = swap_yz_axes_of_quaternion(matrix_quaternion)
    
    obj.location = translation
    obj.scale = scale
    
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = quaternion
    obj.rotation_mode = 'XYZ'

def compose_matrix(obj, scale_correction_factor=1.0):
    local_matrix = obj.matrix_local

    input_translation = local_matrix.to_translation()
    input_quaternion = local_matrix.to_quaternion()
    input_scale = local_matrix.to_scale()
    
    translation = input_translation.copy()
    scale = input_scale.copy()
    
    translation.x = input_translation.x
    translation.y = input_translation.z
    translation.z = input_translation.y
    
    scale.x = input_scale.x
    scale.y = input_scale.z
    scale.z = input_scale.y
    
    translation *= scale_correction_factor
    
    quaternion = swap_yz_axes_of_quaternion(input_quaternion)
    
    matrix = Matrix.LocRotScale(translation, quaternion, scale)
    
    return matrix
