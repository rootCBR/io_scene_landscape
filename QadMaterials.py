
from enum import Enum

class MaterialType(Enum):
	mat_4L_diff_L_1234                = 0
	mat_1L_diff                       = 1
	mat_1L_refl                       = 2
	mat_1L_metal                      = 3
	mat_1L_spec                       = 4
	mat_1L_diff_illum                 = 5
	mat_2L_diff_diff_L_12             = 6
	mat_2L_diff_diff_L_13             = 7
	mat_2L_refl_diff_L_12             = 8
	mat_2L_refl_diff_L_13             = 9
	mat_2L_metal_diff_L_12            = 10
	mat_2L_spec_spec_L_12             = 11
	mat_2L_spec_diff_L_13             = 12
	mat_2L_refl_diff_win_L_12         = 13
	mat_3L_diff_diff_diff             = 14
	mat_3L_refl_diff_diff             = 15
	mat_3L_refl_refl_diff             = 16
	mat_3L_spec_spec_diff             = 17
	mat_3L_spec_diff_diff             = 18
	mat_2L_diff_diff_L_12_ColKey_L_1  = 19
	mat_2L_refl_diff_L_12_ColKey_L_12 = 20
	mat_2L_Water                      = 21
	mat_1L_diff_Decal_and_spec_mask   = 22
	mat_1L_diff_Decal_and_win_mask    = 23
	mat_1L_refl_Decal_and_spec_mask   = 24
	mat_1L_refl_Decal_and_win_mask    = 25
	mat_1L_diff_Decal_and_illum_mask  = 26
	mat_1L_refl_Decal_and_illum_mask  = 27