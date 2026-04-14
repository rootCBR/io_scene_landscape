
from enum import Enum

class MaterialClass(Enum):
	Default = 0
	
class MaterialSubType(Enum):
	NoTexture = 0
	Textured = 1
	TexturedSpec = 2
	Overlay = 3
	OverlaySpec = 4
	OverlayMul = 5
	ParallaxRL = 6
	ParallaxSW = 7
	
class MaterialAlphaType(Enum):
	Disabled = 0
	Normal = 1
	Premul = 2
	Additive = 3
	ColorKey = 4
	
class TextureTiling(Enum):
	Clip = 0
	Wrap = 1
	Mirror = 2