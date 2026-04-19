import array
import copy
import io
import math
import struct;
import sys;
import os
import numpy as np

from mathutils import Vector
from enum import Enum

from .QadMaterials import MaterialType
from .QadTexturePropertyGroupPanels import *
from .QadMaterialPanels import *
from .QadObjectPanels import *
from .QadObjectLibraryPanels import *
from .utils import *

class SmpVertex:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        
class SmpEdge:
    def __init__(self):
        self.seIndex = 0
        
class MyVtxStruct1:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.nx = 0.0
        self.ny = 0.0
        self.nz = 0.0
        self.color = 0
        self.specular = 0
        self.tu = 0.0
        self.tv = 0.0
        self.tu2 = 0.0
        self.tv2 = 0.0
        self.tmp1 = 0.0
        self.tmp2 = 0.0
        
class MyVtxStructE:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.normal = 0
        self.color = 0
        self.specular = 0
        self.tu = 0.0
        self.tv = 0.0
        self.tu2 = 0.0
        self.tv2 = 0.0
        self.tmp1 = 0.0
        self.tmp2 = 0.0
        
class MyTang1:
    def __init__(self):
        self.tx1 = 0.0
        self.ty1 = 0.0
        self.tz1 = 0.0
        self.tw1 = 0.0
        self.tx2 = 0.0
        self.ty2 = 0.0
        self.tz2 = 0.0
        self.tw2 = 0.0
    
class FaceMatItem:
    def __init__(self):
        self.fmTyp = 0
        self.fmOrigin = 0
        self.fmTypU = 0
        self.fmTexAni = 0
        self.fmDecalLayer = 0
        self.fmGeoLayer = 0
        self.fmChunk = 0
        self.fmOrigPoly = 0
        self.fmNormal = SmpVertex()
        self.fmPolySize = 0.0
        self.fmSelSave = 0
        self.fmSelected = 0
        self.fmSelectedU = 0
        #
        self.fmTextures = [0 for _ in range(4)]
        self.fmModes = [0 for _ in range(2 + 2)]
        self.fmModesEd = [0 for _ in range(2 + 2)]
        self.fmTxScale = [0 for _ in range(2 + 2)]
        self.fmTxOffsX = [0 for _ in range(2 + 2)]
        self.fmTxOffsY = [0 for _ in range(2 + 2)]
        self.fmTxAngle = [0 for _ in range(2 + 2)]
        # Variation, only scaling/offset
        self.fmTxScale2 = [0 for _ in range(2 + 2)]
        self.fmTxOffsX2 = [0 for _ in range(2 + 2)]
        self.fmTxOffsY2 = [0 for _ in range(2 + 2)]
        #
        self.fmSmoothGroup = [0 for _ in range(3)]
        self.fmBasicPoly = [0 for _ in range(3)]
        self.fmNormalsPoly = [0 for _ in range(3)]
        self.fmPoly = [SmpEdge() for _ in range(3)]
        # Nur temporaer benutzt
        self.fmTexturesU = [0 for _ in range(4)]
        self.fmAlphas = [0 for _ in range(3)]
        self.fmAlphas2 = [0 for _ in range(3)]
        self.fmGrassProps = 0
        self.fmLoadIndex = 0
        
class VertexMatItem:
    def __init__(self):
        self.viNormal = SmpVertex()
        self.viAlpha = 0
        self.viSelected = 0
        self.viSelectedU = 0
        self.viSoftSel = 0.0
        self.viSavedAlphas = [0 for _ in range(4)]
        self.viAlphaU = 0
        self.viAlpha2 = 0
        self.viAlpha2U = 0
        self.viTexFree = 0
        self.viNext = 0
        self.viNext2 = 0
        self.viGroupIds = [0 for _ in range(4)]
        
class FaceMatChunk:
    def __init__(self):
        self.fcFirstPoly = 0
        self.fcNumPolys = 0
        self.fcTextures = [0 for _ in range(4)]
        self.fcChunk = 0
        self.fcTexAni = 0
        self.fcDecalLayer = 0
        self.fcGeoLayer = 0
        self.fcTyp = 0
        self.fcSelected = 0
        self.fcTexMatrix = [0 for _ in range(8 * 2)]
        self.fcTMCRC = [0 for _ in range(2)]
        self.fcTexMod = [0 for _ in range(4 * 2)]

class QuadItem:
    def __init__(self):
        self.qiQuadX = 0
        self.qiQuadY = 0
        self.qiStartIndex = 0
        self.qiPolysNum = 0
        self.qiPolysNum2 = 0
        self.qiChunk1 = 0
        self.qiChunksNum = 0
        self.qiMidX = 0.0
        self.qiMidY = 0.0
        self.qiMidZ = 0.0
        self.qiRadius = 0.0
        self.qiObject1 = 0
        self.qiObjectsNum = 0
        self.qiLight1 = 0
        self.qiLightsNum = 0
        self.qiVxBufIndex = 0
        
class LedObject:
    def __init__(self):
        self.loObjName = ""
        self.loObjectType = 0
        self.loKickType = 0
        self.loObjWeight = 0
        self.loKickSound = ""
        self.loBounceSound = ""
        
class LedObjectPos:
    def __init__(self):
        self.lpObjName = ""
        self.lpInstanceName = ""
        self.lpObjIndex = 0
        self.lpPathFlag = 0
        self.lpXpos = 0.0
        self.lpYpos = 0.0
        self.lpZpos = 0.0
        self.lpOrientation = [0.0 for _ in range(4)]
        self.lpScale = 1.0
        self.lpObjMatrix = [0.0 for _ in range(9)]
        self.lpMeltedFlag = 0
        self.lpInShadow = 0
        self.lpPathZ = 0.0
        self.lpMinMaxSpeed = 0
        self.lpObjPacket = 0
        self.lpDecalLayer = 0
    
class LedMaterial:
    def __init__(self):
        self.lmMyName = ""
        self.lmTexName1 = ""
        self.lmTexObj1 = None
        self.lmTexObj2 = None
        self.lmUsed = False
        self.lmTexPropGroup = 0
        self.lmOptions = 0
        self.lmAvgColor = 0

class TexAniItem:
    def __init__(self):
        self.Typ = 0
        self.Mode = 0
        self.Layers = 0
        self.Speed = 0
        self.Fps = 0
        self.Step = 0
        self.Begin = 0
        self.End = 0
        self.StepU = 0
        self.StepV = 0
        self.TexScaleX = 0
        self.TexScaleY = 0
        self.TexOffsX = 0
        self.TexOffsY = 0
        
class TexPropGroup:
    def __init__(self):
        self.tpTheName = ""
        self.tpStaub = 0
        self.tpGripV = 0
        self.tpGripH = 0
        self.tpBrems = 0
        self.tpSchlupf = 0
        self.tpSpurFlag = 0
        self.tpSoundName = ""
        self.tpColliFlag = 0
        self.tpColliSound = 0
        self.tpNoShadowFlag = 0
        self.tpNoDisplayFlag = 0
        self.tpEmitter = 0
        self.tpRumbleL = 0
        self.tpRumbleH = 0

class SortEntry:
    def __init__(self):
        self.ZOffset = 0
        self.PIndex = 0

class VllHash:
    def __init__(self):
        self.vhTri = 0
        self.vhNext = 0
    
class Recursion():
    def __init__(self):
        self.initial_value = self.get()
        
    def set(self, value : int):
        sys.setrecursionlimit(value)
        
    def get(self):
        return sys.getrecursionlimit()
        
    def reset(self):
        sys.setrecursionlimit(self.initial_value)
        
class CollisionQuadItem:
    def __init__(self):
        self.graphics_quad_index = 0
        self.triangle_indices = []
        
class CollisionQuad:
    def __init__(self):
        self.items = []

class CData():
    def __init__(self):
        self.scenario_obj = None
        self.placed_objs = []
        self.landscape_scale = 1
        
        self.OBJECTS_NUM      = 6144
        self.TEXTURES_NUM     = 4096
        self.EXTRALIGHTS_NUM  = 8192
        self.SPLINEPOINTS_NUM = 8192
        self.SPLINE_MAXLEN    = 256
        self.SPLINE_NUM       = 1536
        self.SPLINEANI_NUM    = 128
        self.ROAD_MAXLEN      = 512
        self.WAYP_MAXNUM      = 1024
        
        self.ORIGTYP_TERRAIN = 0x0000
        
        self.VxBufDrive = []
        self.VxBufDrive2 = []
        self.VxBufDriveSizes = []

        self.VxBuf1 = []
        self.VxBuf2 = []

        self.IxBuf1 = []
        self.IxBuf2 = []
        
        self.VxBuf1Size = 0
        self.Indices1Num = 0
        
        self.FacesMatInfoPtr = []
        self.VertexMatInfoPtr = []
        
        self.LedObjectsList = []
        #self.LedObjectsNum = 0
        #self.LedTreesNum = 0
        #self.LedTrxNum = 0
        self.LedObjectsTotal = 0
        
        self.LedObjectPosList = []
        self.LedObjectsSetNum = 0

        self.LedMaterialsList = []
        self.LedMaterialsNum = 0
        
        self.TexPropGroupsList = []
        self.TexPropGroupsNum = 0

        self.TexAniData = []
        self.TexData = []
        
        self.FacesTexChunksNum = 0;
        self.FacesTexChunksPtr = []

        self.FacesTexChunksNum2 = 0;
        self.FacesTexChunksPtr2 = []
        
        self.CollQuadsData = []
        self.CollQuadsDataSize = 0
        
        self.TerrainQuadList = []
        
        self.TerrainSizeX = 0
        self.TerrainSizeY = 0

        self.QuadsNum = 0
        self.QuadsNumX = 0
        self.QuadsNumY = 0
        
        self.TestTxScale = 0
        self.TestTxAngle = 0
        self.TestTxOffsetX = 0
        self.TestTxOffsetY = 0
        
        self.TestTxScale2 = 0
        self.TestTxOffsetX2 = 0
        self.TestTxOffsetY2 = 0

    def SortMaterialsByTex(self, Begin : int, SortNum : int, FacesSortList : [], ChunkCount_REF : [], Level : int):
        i = n = SortNum2 = SortBegin = 0
        Last = Code = 0
        
        if Level == 0:
            for i in range(Begin, Begin + SortNum):
                n = FacesSortList[i].PIndex
                
                if ((self.FacesMatInfoPtr[n].fmTyp >> 4) < MaterialType.mat_2L_Water.value):
                    FacesSortList[i].ZOffset = 0
                elif ((self.FacesMatInfoPtr[n].fmTyp >> 4) == MaterialType.mat_2L_Water.value):
                    FacesSortList[i].ZOffset = 1000
                else:
                    FacesSortList[i].ZOffset = self.FacesMatInfoPtr[n].fmDecalLayer + 1
                #print(f"(0) ZOffset = {FacesSortList[i].ZOffset}")
        elif Level == 1:
            for i in range(Begin, Begin + SortNum):
                n = FacesSortList[i].PIndex
                FacesSortList[i].ZOffset = ((self.FacesMatInfoPtr[n].fmTyp & 0x1f0) << (25-4)) | ((self.FacesMatInfoPtr[n].fmSelected & 1) << 24) | (self.FacesMatInfoPtr[n].fmModesEd[0] << 21) | (self.FacesMatInfoPtr[n].fmModesEd[1] << 18) | (self.FacesMatInfoPtr[n].fmTxAngle[0] << 9) | (self.FacesMatInfoPtr[n].fmTxAngle[1])
                #print(f"(1) ZOffset = {FacesSortList[i].ZOffset}")
        elif Level == 2:
            for i in range(Begin, Begin + SortNum):
                n = FacesSortList[i].PIndex
                FacesSortList[i].ZOffset = (self.FacesMatInfoPtr[n].fmTextures[0] << 16) | (self.FacesMatInfoPtr[n].fmTextures[1])
                #print(f"(2) ZOffset = {FacesSortList[i].ZOffset}")
        elif Level == 3:
            for i in range(Begin, Begin + SortNum):
                n = FacesSortList[i].PIndex
                FacesSortList[i].ZOffset = (self.FacesMatInfoPtr[n].fmTextures[2] << 16) | (self.FacesMatInfoPtr[n].fmTextures[3])
                #print(f"(3) ZOffset = {FacesSortList[i].ZOffset}")
        elif Level == 4:
            for i in range(Begin, Begin + SortNum):
                n = FacesSortList[i].PIndex
                FacesSortList[i].ZOffset = self.FacesMatInfoPtr[n].fmTexAni
                #print(f"(4) ZOffset = {FacesSortList[i].ZOffset}")
        elif Level == 5:
            for i in range(Begin, Begin + SortNum):
                n = FacesSortList[i].PIndex
                FacesSortList[i].ZOffset = (self.FacesMatInfoPtr[n].fmTxScale[0] << 24) | (self.FacesMatInfoPtr[n].fmTxScale[1] << 16) | (self.FacesMatInfoPtr[n].fmTxScale2[0] << 8) | (self.FacesMatInfoPtr[n].fmTxScale2[1])
                #print(f"(5) ZOffset = {FacesSortList[i].ZOffset}")
        elif Level == 6:
            for i in range(Begin, Begin + SortNum):
                n = FacesSortList[i].PIndex
                FacesSortList[i].ZOffset = (self.FacesMatInfoPtr[n].fmTxOffsX[0] << 24) | (self.FacesMatInfoPtr[n].fmTxOffsX[1] << 16) | (self.FacesMatInfoPtr[n].fmTxOffsX2[0] << 8) | (self.FacesMatInfoPtr[n].fmTxOffsX2[1])
                #print(f"(6) ZOffset = {FacesSortList[i].ZOffset}")
        elif Level == 7:
            for i in range(Begin, Begin + SortNum):
                n = FacesSortList[i].PIndex
                FacesSortList[i].ZOffset = (self.FacesMatInfoPtr[n].fmTxOffsY[0] << 24) | (self.FacesMatInfoPtr[n].fmTxOffsY[1] << 16) | (self.FacesMatInfoPtr[n].fmTxOffsY2[0] << 8) | (self.FacesMatInfoPtr[n].fmTxOffsY2[1])
                #print(f"(7) ZOffset = {FacesSortList[i].ZOffset}")
        elif Level == 8:
            for i in range(Begin, Begin + SortNum):
                n = FacesSortList[i].PIndex
                FacesSortList[i].ZOffset = self.FacesMatInfoPtr[n].fmGeoLayer
                #print(f"(8) ZOffset = {FacesSortList[i].ZOffset}")
        elif Level == 9:
            for i in range(Begin, Begin + SortNum):
                FacesSortList[i].ZOffset = ChunkCount_REF[0]
                #print(f"(9) ZOffset = {FacesSortList[i].ZOffset}")
            
            ChunkCount_REF[0] += 1
            
            return
        
        self.SortTheListS(FacesSortList, SortNum, Begin)
        
        # Einzelne Abschnitte weitersortieren
        SortBegin = Begin
        SortNum2 = 0
        Last = 0xffffffff
        
        for i in range(Begin, Begin + SortNum + 1):
            if i < (Begin + SortNum):
                Code = FacesSortList[i].ZOffset
            else:
                Code = 0xffffffff
                
            if ((Code != Last) or (i == (Begin + SortNum))):
                if SortNum2 > 0:
                    self.SortMaterialsByTex(SortBegin, SortNum2, FacesSortList, ChunkCount_REF, Level + 1)
                    
                Last = Code
                SortBegin = i
                SortNum2 = 0
                
            SortNum2 += 1

    def GenerateVertexRings(self):
        i = i2 = a1 = a2 = p = 0
        #
        for i in range(self.VxBuf1Size):
            self.VertexMatInfoPtr[i].viNext2 = -1
            
        for i in range(self.Indices1Num // 3):
            for i2 in range(3):
                a1 = self.FacesMatInfoPtr[i].fmBasicPoly[i2]
                a2 = self.FacesMatInfoPtr[i].fmPoly[i2].seIndex
                
                if self.VertexMatInfoPtr[a2].viNext2 < 0:
                    p = self.VertexMatInfoPtr[a1].viNext2
                    
                    if p >= 0:
                        while self.VertexMatInfoPtr[p].viNext2 != a1:
                            p = self.VertexMatInfoPtr[p].viNext2
                            
                        self.VertexMatInfoPtr[p].viNext2 = a2
                        
                    else:
                        self.VertexMatInfoPtr[a1].viNext2 = a2
                        
                    self.VertexMatInfoPtr[a2].viNext2 = a1

        for i in range(self.VxBuf1Size):
            if self.VertexMatInfoPtr[i].viNext2 < 0:
                self.VertexMatInfoPtr[i].viNext2 = i

    def ReApplyTerrainMaterials(self, SelectedOnly : int):
        FacesSortList = [SortEntry() for _ in range(self.Indices1Num // 3)]
        i = i2 = SortNum = 0
        p = a1 = a2 = 0
        ChunkCount_REF = [0]
        SortedFlag = False
        
        SortNum = self.Indices1Num // 3;
        
        if SelectedOnly == 0:
            # Flaecheninfos aktualisieren
            for i in range(SortNum):
                FacesSortList[i].PIndex = i
                
                for i2 in range(3):
                    p = self.IxBuf1[i * 3 + i2];
                
                    self.FacesMatInfoPtr[i].fmPoly[i2].seIndex = p;
                    self.FacesMatInfoPtr[i].fmPoly[i2].seTu  = self.VxBuf1[p].tu;
                    self.FacesMatInfoPtr[i].fmPoly[i2].seTv  = self.VxBuf1[p].tv;
                    self.FacesMatInfoPtr[i].fmPoly[i2].seTu2 = self.VxBuf1[p].tu2;
                    self.FacesMatInfoPtr[i].fmPoly[i2].seTv2 = self.VxBuf1[p].tv2;
                    self.FacesMatInfoPtr[i].fmPoly[i2].seNx  = self.VxBuf1[p].nx;
                    self.FacesMatInfoPtr[i].fmPoly[i2].seNy  = self.VxBuf1[p].ny;
                    self.FacesMatInfoPtr[i].fmPoly[i2].seNz  = self.VxBuf1[p].nz;
                
                    if self.FacesMatInfoPtr[i].fmTextures[0] < 0:
                        self.FacesMatInfoPtr[i].fmTextures[0] = 0
                    if self.FacesMatInfoPtr[i].fmTextures[1] < 0:
                        self.FacesMatInfoPtr[i].fmTextures[1] = 0
                    if self.FacesMatInfoPtr[i].fmTextures[2] < 0:
                        self.FacesMatInfoPtr[i].fmTextures[2] = 0
                    if self.FacesMatInfoPtr[i].fmTextures[3] < 0:
                        self.FacesMatInfoPtr[i].fmTextures[3] = 0
                        
            self.SortMaterialsByTex(0, SortNum, FacesSortList, ChunkCount_REF, 0)
            SortedFlag = True
        else:
            pass # --- TODO
        
        print(f"ChunkCount = {ChunkCount_REF[0]}")
        
        if SortedFlag:
            # Flaechen sortiert umkopieren
            Indices2Ptr = [self.IxBuf1[i] for i in range(self.Indices1Num)]
            
            for i in range(SortNum):
                self.IxBuf1[i * 3] = Indices2Ptr[FacesSortList[i].PIndex * 3]
                self.IxBuf1[i * 3 + 1] = Indices2Ptr[FacesSortList[i].PIndex * 3 + 1]
                self.IxBuf1[i * 3 + 2] = Indices2Ptr[FacesSortList[i].PIndex * 3 + 2]
            
            # Texinfos sortiert umkopieren
            MatPtr2 = [self.FacesMatInfoPtr[i] for i in range(SortNum)]
            
            for i in range(SortNum):
                self.FacesMatInfoPtr[i] = MatPtr2[FacesSortList[i].PIndex]
        
        # Anzahl Chunks ermitteln
        i2 = -1
        p = 0
        
        for i in range(SortNum):
            if FacesSortList[i].ZOffset != i2:
                p += 1
                i2 = FacesSortList[i].ZOffset
        
        self.FacesTexChunksNum = p
        self.FacesTexChunksPtr = [FaceMatChunk() for _ in range(p)]
        
        # Chunks erzeugen
        i2 = -1
        p = 0
        
        for i in range(SortNum):
            if FacesSortList[i].ZOffset != i2:
                self.FacesTexChunksPtr[p].fcFirstPoly = i
                self.FacesTexChunksPtr[p].fcNumPolys = 0
                self.FacesTexChunksPtr[p].fcTextures[0] = self.FacesMatInfoPtr[i].fmTextures[0]
                self.FacesTexChunksPtr[p].fcTextures[1] = self.FacesMatInfoPtr[i].fmTextures[1]
                self.FacesTexChunksPtr[p].fcTextures[2] = self.FacesMatInfoPtr[i].fmTextures[2]
                self.FacesTexChunksPtr[p].fcTextures[3] = self.FacesMatInfoPtr[i].fmTextures[3]
                self.FacesTexChunksPtr[p].fcDecalLayer = self.FacesMatInfoPtr[i].fmDecalLayer
                self.FacesTexChunksPtr[p].fcGeoLayer = self.FacesMatInfoPtr[i].fmGeoLayer
                self.FacesTexChunksPtr[p].fcTyp = self.FacesMatInfoPtr[i].fmTyp
                self.FacesTexChunksPtr[p].fcTexAni = self.FacesMatInfoPtr[i].fmTexAni
                self.FacesTexChunksPtr[p].fcSelected = self.FacesMatInfoPtr[i].fmSelected
                
                #if (self.FacesTexChunksPtr[p].fcSelected) and (self.EdMapPreview):
                #    Channel = (self.EdTexWhichLayer & 2) >> 1
                #    self.GenerateFaceTexMatrix(self.FacesTexChunksPtr[p], self.FacesMatInfoPtr[i], Channel, self.EdTexWhichLayer & 1)
                #    self.GenerateFaceTexMatrix(self.FacesTexChunksPtr[p], self.FacesMatInfoPtr[i], Channel ^ 1)
                #else:
                self.GenerateFaceTexMatrix(self.FacesTexChunksPtr[p], self.FacesMatInfoPtr[i], 0)
                self.GenerateFaceTexMatrix(self.FacesTexChunksPtr[p], self.FacesMatInfoPtr[i], 1)
    
                p += 1
                i2 = FacesSortList[i].ZOffset
                
            self.FacesMatInfoPtr[i].fmChunk = p - 1 # Merken, zu welchem chunk
            self.FacesTexChunksPtr[p - 1].fcNumPolys += 1
            #print(f"(A) ZOffset = {FacesSortList[i].ZOffset}")
            #print(f"(A) fmChunk = {self.FacesMatInfoPtr[i].fmChunk}")
            
        self.GenerateVertexRings()
        
    def LoadTerrainFile(self, scene, scenario_obj, placed_objs, landscape_scale : int):
        self.scenario_obj = scenario_obj
        self.placed_objs = placed_objs
        self.landscape_scale = landscape_scale
        
        self.VxBuf1 = []
        self.VxBuf2 = []
        self.IxBuf1 = []
        self.IxBuf2 = []
        
        self.VxBufDrive = [[] for _ in range(64)]
        self.VxBufDrive2 = [[] for _ in range(64)]
        self.VxBufDriveSizes = [0 for _ in range(64)]
        
        self.VertexMatInfoPtr = []
        self.FacesTexChunksPtr = []
        self.FacesMatInfoPtr = []
        
        self.LedMaterialsList = []
        self.LedMaterialsNum = 0
        
        self.TexPropGroupsList = []
        self.TexPropGroupsNum = 0
        
        self.LedObjectPosList = []
        self.LedObjectsSetNum = 0
        
        self.TexAniData = [TexAniItem() for _ in range(16)]
        
        self.TexData = []
        
        used_vertex_indices = {}
        led_material_indices = {}
        
        face_mat_chunks = []

        mesh = self.scenario_obj.data
        
        mesh.calc_loop_triangles()
        
        if bpy.app.version < (4, 1, 0):
            mesh.calc_normals_split()
    
        uv_layers = [uv_layer.name for uv_layer in mesh.uv_layers]
    
        for uv_index in range(min(len(uv_layers), 2)):
            uv_layer_name = uv_layers[uv_index]
            mesh.calc_tangents(uvmap=uv_layer_name)
            
        color_layer_blend = None
        color_layer_ambient = None

        if "Color" in mesh.vertex_colors:
            color_layer_blend = mesh.vertex_colors["Color"]
            
        if "Specular" in mesh.vertex_colors:
            color_layer_ambient = mesh.vertex_colors["Specular"]
    
        # TODO
        
        for i in range(len(placed_objs)):
            placed_obj = placed_objs[i]
            qad_object_properties : QadObjectProperties = placed_obj.qad_object_properties
            
            print(f"scene.qad_object_data_list = {scene.qad_object_data_list}")
            print(f"qad_object_properties.qad_object_dataset = {qad_object_properties.qad_object_dataset}")
            
            qad_object_data_properties : QadObjectDataProperties =  scene.qad_object_data_list[int(qad_object_properties.qad_object_dataset)]
            
            print(f"qad_object_data_properties = {qad_object_data_properties}")
            
            object_model_name = qad_object_data_properties.name
            
            print(f"object_model_name = {object_model_name}")
            
            data_index = next((i for i, item in enumerate(self.LedObjectsList) if item.loObjName == object_model_name), -1)
            
            if data_index == -1:
                data_index = len(self.LedObjectsList)
                qad_object_data = LedObject()
                qad_object_data.loObjName = object_model_name
                qad_object_data.loObjectType = qad_object_data_properties.type
                qad_object_data.loKickType = qad_object_data_properties.kick_type
                qad_object_data.loObjWeight = qad_object_data_properties.weight
                qad_object_data.loKickSound = qad_object_data_properties.kick_sound
                qad_object_data.loBounceSound = qad_object_data_properties.bounce_sound
                self.LedObjectsList.append(qad_object_data)
                
            qad_placed_object = LedObjectPos()
            qad_placed_object.lpObjName = object_model_name
            qad_placed_object.lpObjIndex = data_index
            
            matrix = placed_obj.matrix_world.to_4x4()
            
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
    
            translation *= landscape_scale
    
            quaternion_b = swap_yz_axes_of_quaternion(matrix_quaternion)
            quaternion = [quaternion_b.x, quaternion_b.y, quaternion_b.z, -quaternion_b.w]
    
            qad_placed_object.lpXpos = translation.x
            qad_placed_object.lpYpos = translation.y
            qad_placed_object.lpZpos = translation.z
            qad_placed_object.lpOrientation = quaternion
            
            if (scale.x == scale.y == scale.z):
                qad_placed_object.lpScale = scale.x
            else:
                qad_placed_object.lpScale = 1.0
            
            matrix3 = matrix.to_3x3().transposed()
            
            # TODO
            qad_placed_object.lpObjMatrix = [
                matrix3[0][0], matrix3[0][1], matrix3[0][2],
                matrix3[1][0], matrix3[1][1], matrix3[1][2],
                matrix3[2][0], matrix3[2][1], matrix3[2][2]
                ]
        
            self.LedObjectPosList.append(qad_placed_object)
            
        self.LedObjectsSetNum = len(self.LedObjectPosList)

        if self.LedObjectsSetNum < 1:
            raise Exception(f"Could not find a minimum of 1 placed object")
            
        default_texture_name = "01"
        led_default_material = LedMaterial()
        led_default_material.lmTexName1 = default_texture_name
        led_default_material.lmTexPropGroup = 0
        led_material_indices[default_texture_name] = len(self.LedMaterialsList)
        self.LedMaterialsList.append(led_default_material)
            
        for i in range(len(scenario_obj.material_slots)):
            material_slot = scenario_obj.material_slots[i]
            material = material_slot.material
            
            material_name = material.name
            
            qad_material_properties : QadMaterialProperties = material.qad_material_properties

            print(f"{i} material_name = {material_name}")
            
            material_type_name = qad_material_properties.type
            material_type = MaterialType[material_type_name].value
            
            face_mat_chunk = FaceMatItem()
            face_mat_chunk.fmTyp = material_type << 4
            
            face_mat_chunk.fmTexAni = 0
            face_mat_chunk.fmTxAngle[0] = 0
            face_mat_chunk.fmTxAngle[1] = 0
            
            face_mat_chunk.fmTxOffsX[0] = round(qad_material_properties.texture_1_offset[0])
            face_mat_chunk.fmTxOffsY[0] = round(qad_material_properties.texture_1_offset[1])
            face_mat_chunk.fmTxScale[0] = round(qad_material_properties.texture_1_scale[0] * 100.0)
            face_mat_chunk.fmTxScale[1] = round(qad_material_properties.texture_1_scale[1] * 100.0)
            face_mat_chunk.fmTxOffsX2[0] = round(qad_material_properties.texture_2_offset[0])
            face_mat_chunk.fmTxOffsY2[0] = round(qad_material_properties.texture_2_offset[1])
            face_mat_chunk.fmTxScale2[0] = round(qad_material_properties.texture_2_scale[0] * 100.0)
            face_mat_chunk.fmTxScale2[1] = round(qad_material_properties.texture_2_scale[1] * 100.0)
            
            textures = [
                qad_material_properties.texture_1, 
                qad_material_properties.texture_2, 
                qad_material_properties.texture_3, 
                qad_material_properties.texture_4
            ]
            
            bump_textures = [
                qad_material_properties.bump_texture_1, 
                qad_material_properties.bump_texture_2, 
                qad_material_properties.bump_texture_3
            ]
            
            for j in range(len(textures)):
                image = textures[j]
        
                texture_name = default_texture_name
                
                if image:
                    texture_name = os.path.splitext(image.name)[0]
                    
                if texture_name not in led_material_indices:
                    led_material_indices[texture_name] = len(self.LedMaterialsList)
                
                    texture_property_group_index = int(image.qad_texture_properties.texture_properties_group)

                    texture_property_group = bpy.context.scene.qad_texture_property_group_list[texture_property_group_index]
                    texture_property_group_name = texture_property_group.name

                    # TODO: maintain order
                    led_material = LedMaterial()
                    led_material.lmTexName1 = texture_name
                    led_material.lmTexPropGroup = texture_property_group_index
                        
                    print(f"{texture_name} -> {led_material.lmTexPropGroup}: {texture_property_group_name}")
                    
                    if (j < len(bump_textures)):
                        bump_image = bump_textures[j]
                        
                        if bump_image:
                            bump_texture_name = os.path.splitext(bump_image.name)[0]
                            led_material.lmTexObj2 = bump_texture_name
                                
                    self.LedMaterialsList.append(led_material)
            
                led_material_index = led_material_indices[texture_name]
                        
                print(f"{led_material_index} texture_name = {texture_name}")
                
                face_mat_chunk.fmTextures[j] = led_material_index
                
            face_mat_chunks.append(face_mat_chunk)

        for source_polygon in mesh.polygons:
            vertex_indices = []
            
            polygon_index = len(self.IxBuf1) // 3
            
            for source_loop_index in source_polygon.loop_indices:
                source_loop = mesh.loops[source_loop_index]
                
                source_vertex_index = source_loop.vertex_index
                
                source_vertex = mesh.vertices[source_vertex_index]
                
                u1 = 0.0
                v1 = 0.0
                u2 = 0.0
                v2 = 0.0
                
                t1 = [0.0, 0.0, 0.0, 0.0]
                t2 = [0.0, 0.0, 0.0, 0.0]
                
                for uv_index in range(min(len(uv_layers), 2)):
                    uv_layer_name = uv_layers[uv_index]
                        
                    uv_layer = mesh.uv_layers.get(uv_layer_name)
                    source_uv = uv_layer.data[source_loop_index].uv
                    
                    tangent = source_loop.tangent
                
                    tangent_x = tangent[0]
                    tangent_y = tangent[1]
                    tangent_z = tangent[2]
                    bitangent_sign = source_loop.bitangent_sign
                        
                    np_tangents = np.array([tangent_x, tangent_z, tangent_y, bitangent_sign], dtype=np.float32)
                    np_tangents_half = np_tangents.astype(np.float16)
                    
                    if uv_index == 0:
                        u1 = source_uv[0]
                        v1 = -source_uv[1] + 1.0
                            
                        t1 = np_tangents_half
                    elif uv_index == 1:
                        u2 = source_uv[0]
                        v2 = -source_uv[1] + 1.0
                            
                        t2 = np_tangents_half
                
                blend_color = 0xffffffff
                ambient_color = 0xffffffff
                
                if color_layer_blend:
                    vertex_color_blend = color_layer_blend.data[source_loop_index].color
                    
                    # TODO
                    blendR = int(srgb_to_linear(vertex_color_blend[0]) * 255)
                    blendG = int(srgb_to_linear(vertex_color_blend[1]) * 255)
                    blendB = int(srgb_to_linear(vertex_color_blend[2]) * 255)
                    blendA = int(srgb_to_linear(vertex_color_blend[3]) * 255)
                    blend_color = (blendR << 24) | (blendG << 16) | (blendB << 8) | blendA
                
                if color_layer_ambient:
                    vertex_color_ambient = color_layer_ambient.data[source_loop_index].color
                    
                    # TODO
                    ambientR = int(srgb_to_linear(vertex_color_ambient[0]) * 255)
                    ambientG = int(srgb_to_linear(vertex_color_ambient[1]) * 255)
                    ambientB = int(srgb_to_linear(vertex_color_ambient[2]) * 255)
                    ambientA = int(srgb_to_linear(vertex_color_ambient[3]) * 255)
                    ambient_color = (ambientR << 24) | (ambientG << 16) | (ambientB << 8) | ambientA
                    
                if source_vertex_index not in used_vertex_indices:
                    used_vertex_indices[source_vertex_index] = len(self.VxBuf1)
            
                    source_vertex_position_world = scenario_obj.matrix_world @ source_vertex.co
                    
                    vertex = MyVtxStruct1()
                    vertex.x = source_vertex_position_world.x * self.landscape_scale
                    vertex.y = source_vertex_position_world.z * self.landscape_scale
                    vertex.z = source_vertex_position_world.y * self.landscape_scale
                    vertex.nx = source_loop.normal.x
                    vertex.ny = source_loop.normal.z
                    vertex.nz = source_loop.normal.y
                    vertex.tu = u1
                    vertex.tv = v1
                    vertex.tu2 = u2
                    vertex.tv2 = v2
                    vertex.color = blend_color
                    vertex.specular = ambient_color
                    self.VxBuf1.append(vertex)
            
                    tangent = MyTang1()
                    tangent.tx1 = t1[0]
                    tangent.ty1 = t1[1]
                    tangent.tz1 = t1[2]
                    tangent.tw1 = t1[3]
                    tangent.tx2 = t2[0]
                    tangent.ty2 = t2[1]
                    tangent.tz2 = t2[2]
                    tangent.tw2 = t2[3]
                    self.VxBuf2.append(tangent)
            
                    # TODO
                    vertex_mat_info = VertexMatItem()
                    vertex_mat_info.viAlpha = vertex.color
                    vertex_mat_info.viAlphaU = vertex.color
                    vertex_mat_info.viAlpha2 = vertex.specular
                    vertex_mat_info.viAlpha2U = vertex.specular
                    vertex_mat_info.viSelected = 0
                    vertex_mat_info.viSelectedU = 0
                    self.VertexMatInfoPtr.append(vertex_mat_info)
            
                vertex_index = used_vertex_indices[source_vertex_index]

                vertex_indices.append(vertex_index)
                
            for i in range(3):
                self.IxBuf1.append(vertex_indices[i])

            # 3 Texturlayer
            face_mat_info = FaceMatItem()
            face_mat_info.fmTextures[0] = 0
            face_mat_info.fmTextures[1] = 1
            face_mat_info.fmTextures[2] = 2
            face_mat_info.fmTextures[3] = 3
            face_mat_info.fmTexturesU[0] = 0
            face_mat_info.fmTexturesU[1] = 1
            face_mat_info.fmTexturesU[2] = 2
            face_mat_info.fmTexturesU[3] = 3
            #
            face_mat_info.fmTyp = MaterialType.mat_4L_diff_L_1234.value << 4
            face_mat_info.fmSelected = 0
            face_mat_info.fmSelectedU = 0
            face_mat_info.fmSelSave = 0x00
            face_mat_info.fmSmoothGroup[0] = 7
            face_mat_info.fmSmoothGroup[1] = 7
            face_mat_info.fmSmoothGroup[2] = 7
            face_mat_info.fmOrigPoly = polygon_index
            face_mat_info.fmTxScale[0] = 100
            face_mat_info.fmTxScale[1] = 100
            face_mat_info.fmTxOffsX[0] = 0
            face_mat_info.fmTxOffsX[1] = 0
            face_mat_info.fmTxOffsY[0] = 0
            face_mat_info.fmTxOffsY[1] = 0
            face_mat_info.fmTxAngle[0] = 0
            face_mat_info.fmTxAngle[1] = 0
            face_mat_info.fmTxScale2[0] = 100
            face_mat_info.fmTxScale2[1] = 100
            face_mat_info.fmTxOffsX2[0] = 0
            face_mat_info.fmTxOffsX2[1] = 0
            face_mat_info.fmTxOffsY2[0] = 0
            face_mat_info.fmTxOffsY2[1] = 0
            face_mat_info.fmModes[0] = 0
            face_mat_info.fmModes[1] = 0
            face_mat_info.fmNormalsPoly[0] = vertex_indices[2]
            face_mat_info.fmNormalsPoly[1] = vertex_indices[1]
            face_mat_info.fmNormalsPoly[2] = vertex_indices[0]
            face_mat_info.fmBasicPoly[0] = vertex_indices[2]
            face_mat_info.fmBasicPoly[1] = vertex_indices[1]
            face_mat_info.fmBasicPoly[2] = vertex_indices[0]
            face_mat_info.fmPoly[0].seTu = 0
            face_mat_info.fmPoly[0].seTv = 0
            face_mat_info.fmPoly[1].seTu = 0
            face_mat_info.fmPoly[1].seTv = 0
            face_mat_info.fmPoly[2].seTu = 0
            face_mat_info.fmPoly[2].seTv = 0
            face_mat_info.fmPoly[0].seTu2 = 0
            face_mat_info.fmPoly[0].seTv2 = 0
            face_mat_info.fmPoly[1].seTu2 = 0
            face_mat_info.fmPoly[1].seTv2 = 0
            face_mat_info.fmPoly[2].seTu2 = 0
            face_mat_info.fmPoly[2].seTv2 = 0
            #
            
            material_slot_index = source_polygon.material_index
            face_mat_info.fmTyp = face_mat_chunks[material_slot_index].fmTyp
            # TODO
            face_mat_info.fmTextures[0] = face_mat_chunks[material_slot_index].fmTextures[0]
            face_mat_info.fmTextures[1] = face_mat_chunks[material_slot_index].fmTextures[1]
            face_mat_info.fmTextures[2] = face_mat_chunks[material_slot_index].fmTextures[2]
            face_mat_info.fmTextures[3] = face_mat_chunks[material_slot_index].fmTextures[3]
            face_mat_info.fmTxScale[0] = face_mat_chunks[material_slot_index].fmTxScale[0]
            face_mat_info.fmTxScale[1] = face_mat_chunks[material_slot_index].fmTxScale[1]
            face_mat_info.fmTxOffsX[0] = face_mat_chunks[material_slot_index].fmTxOffsX[0]
            face_mat_info.fmTxOffsY[0] = face_mat_chunks[material_slot_index].fmTxOffsY[0]
            face_mat_info.fmTxScale2[0] = face_mat_chunks[material_slot_index].fmTxScale2[0]
            face_mat_info.fmTxScale2[1] = face_mat_chunks[material_slot_index].fmTxScale2[1]
            face_mat_info.fmTxOffsX2[0] = face_mat_chunks[material_slot_index].fmTxOffsX2[0]
            face_mat_info.fmTxOffsY2[0] = face_mat_chunks[material_slot_index].fmTxOffsY2[0]
            self.FacesMatInfoPtr.append(face_mat_info)

        self.VxBuf1Size = len(self.VxBuf1)
        self.Indices1Num = len(self.IxBuf1)
        
        self.LedObjectsTotal = len(self.LedObjectsList)
        self.LedObjectsSetNum = len(self.LedObjectPosList)
        self.LedMaterialsNum = len(self.LedMaterialsList)
        
        for i in range(len(scene.qad_texture_property_group_list)):
            texture_property_group_properties : QadTexturePropertyGroupProperties = scene.qad_texture_property_group_list[i]
            
            texture_property_group = TexPropGroup()
            texture_property_group.tpTheName = texture_property_group_properties.name
            texture_property_group.tpStaub = texture_property_group_properties.dust
            texture_property_group.tpGripV = texture_property_group_properties.grip_front
            texture_property_group.tpGripH = texture_property_group_properties.grip_rear
            texture_property_group.tpBrems = texture_property_group_properties.brake
            texture_property_group.tpSchlupf = texture_property_group_properties.slip_mode
            texture_property_group.tpSpurFlag = (texture_property_group_properties.skidmark_type_colored & 2) | (texture_property_group_properties.skidmark_type_black & 1)
            texture_property_group.tpSoundName = texture_property_group_properties.sound
            texture_property_group.tpColliFlag = texture_property_group_properties.collision_options
            texture_property_group.tpColliSound = texture_property_group_properties.collision_sound_type
            texture_property_group.tpNoShadowFlag = not texture_property_group_properties.enable_shadow
            texture_property_group.tpNoDisplayFlag = not texture_property_group_properties.enable_render
            texture_property_group.tpEmitter = texture_property_group_properties.emitter
            texture_property_group.tpRumbleL = texture_property_group_properties.rumble_slow
            texture_property_group.tpRumbleH = texture_property_group_properties.rumble_fast
            self.TexPropGroupsList.append(texture_property_group)
            
        self.TexPropGroupsNum = len(self.TexPropGroupsList)
        
        TexData2 = [0 for _ in range(4096)]
        count = (self.LedMaterialsNum + 1) & ~1 # padding to keep 4 byte alignment
        count = max(count, 256)
        for i in range(self.LedMaterialsNum):
            TexData2[i] = self.LedMaterialsList[i].lmTexPropGroup
            #print(f"TexData2[i] = {TexData2[i]}")
        self.TexData = TexData2[:count]
        print(f"len(self.TexData) = {len(self.TexData)}")

        # FacesMatInfoPtr2 = [FaceMatItem() for _ in range(self.Indices1Num // 3)]
        
        # for i in range(self.Indices1Num // 3):
        #     #FacesMatInfoPtr2[i] = self.FacesMatInfoPtr[i]
            
        #     for ix in range(3):
        #         FacesMatInfoPtr2[i].fmAlphas[ix] = self.VxBuf1[self.IxBuf1[i * 3 + ix]].color
                
        # for i in range(self.Indices1Num // 3):
        #     for ix in range(3):
        #         self.FacesMatInfoPtr[i].fmAlphas[ix] = self.VxBuf1[self.IxBuf1[i * 3 + ix]].color # Default-Alphawerte retten
                
        # for i in range(self.Indices1Num // 3):
        #     self.FacesMatInfoPtr[i].fmSelSave = 0x00
        #     self.FacesMatInfoPtr[i].fmSelected = 0
            
        # # Texturen restaurieren
        # for i in range(self.Indices1Num // 3):
        #     ix = FacesMatInfoPtr2[i].fmOrigPoly; # --- TODO
            
        #     if ix >= 0:
        #         #self.FacesMatInfoPtr[ix] = FacesMatInfoPtr2[i]
        #         self.FacesMatInfoPtr[ix].fmSelected = 1
        
        # Alphas restaurieren
        for i in range(self.Indices1Num // 3):
            self.FacesMatInfoPtr[i].fmOrigin = self.ORIGTYP_TERRAIN # Code = Terrain
            #self.FacesMatInfoPtr[i].fmOrigPoly = i
            self.FacesMatInfoPtr[i].fmGeoLayer = 2
            
        #     for ix in range(3):
        #         self.VxBuf1[self.IxBuf1[i * 3 + ix]].color = self.FacesMatInfoPtr[i].fmAlphas[ix] # Alphas restaurieren
        
        # for i in range(self.VxBuf1Size):
        #     self.VertexMatInfoPtr[i].viAlpha = self.VxBuf1[i].color
        #     self.VertexMatInfoPtr[i].viAlphaU = self.VxBuf1[i].color
        #     self.VertexMatInfoPtr[i].viSelected = 0
        #     self.VertexMatInfoPtr[i].viSelectedU = 0

        #self.ReCreateNormals(True)
        self.ReApplyTerrainMaterials(0)
        
    def SortTheList(self, ListPtr : [], Size : int, Start : int = 0):
        EsCount = BsCount = ec = h2 = PiVal = 0
        Value1 = Value2 = h = 0
        ListPtr_INDEX = 0
        HolePtr_INDEX = 0
        PrevPtr_INDEX = 0
        
        #print(f"SortTheList() {len(ListPtr)}, {Size}, {Start}")
        
        if Size < 2:
            return
        
        EsCount = Size - 1
        BsCount = 1

        Value1 = ListPtr[ListPtr_INDEX + Start].ZOffset
        
        ListPtr_INDEX += 1
        
        while True:
            Value2 = ListPtr[ListPtr_INDEX + Start].ZOffset
            
            if Value1 > Value2:
                PiVal = ListPtr[ListPtr_INDEX + Start].PIndex
                HolePtr_INDEX = ListPtr_INDEX
                PrevPtr_INDEX = ListPtr_INDEX - 1
                ec = BsCount
                
                while True:
                    h2 = ListPtr[PrevPtr_INDEX + Start].PIndex
                    h = ListPtr[PrevPtr_INDEX + Start].ZOffset
                    PrevPtr_INDEX -= 1
                    
                    if h <= Value2:
                        break
                    
                    ListPtr[HolePtr_INDEX + Start].PIndex = h2
                    ListPtr[HolePtr_INDEX + Start].ZOffset = h
                    HolePtr_INDEX -= 1
                    
                    ec -= 1
                    
                    if ec == 0:
                        break
                
                ListPtr[HolePtr_INDEX + Start].ZOffset = Value2
                ListPtr[HolePtr_INDEX + Start].PIndex = PiVal
                Value2 = ListPtr[ListPtr_INDEX + Start].ZOffset
                
            ListPtr_INDEX += 1
            Value1 = Value2
            BsCount += 1

            EsCount -= 1
                
            if EsCount == 0:
                break
               
    def SortTheListQ(self, ListPtr : [], Size : int, Start : int = 0):
        i = i1 = i2 = 0
        Min = Max = Mid = z = 0

        #print(f"SortTheListQ() {len(ListPtr)}, {Size}, {Start}")
        
        if Size < 2:
            return
        
        if Size < 10:
            self.SortTheList(ListPtr, Size, Start)
            return
        
        # Min/Max suchen
        for i in range(Size):
            z = ListPtr[i + Start].ZOffset
            
            if i == 0:
                Min = z
                Max = z
            else:
                if z < Min:
                    Min = z
                
                if z > Max:
                    Max = z
                    
        if Min == Max: # Hier gibts nix zu sortieren
            return
        
        # Mid suchen
        Avg_ = d = d_ = 0
        
        Avg_ = (Min + Max) >> 1
        
        for i in range(Size):
            z = ListPtr[i + Start].ZOffset
            d = z - Avg_
            
            if d < 0:
                d = -d
            
            if i == 0:
                Mid = z
                d_ = d
            else:
                if d < d_:
                    Mid =  z
                    d_ = d
                    
        if Mid == Min:
            Mid = Max
            
        # Quicksort-swap
        i1 = 0
        i2 = Size - 1
        
        while i1 < i2:
            while ((i1 < i2) and (ListPtr[i1 + Start].ZOffset < Mid)):
                i1 += 1
            
            while ((i1 < i2) and (ListPtr[i2 + Start].ZOffset >= Mid)):
                i2 -= 1
                
            if i1 < i2:
                Swap = ListPtr[i1 + Start]
                ListPtr[i1 + Start] = ListPtr[i2 + Start]
                ListPtr[i2 + Start] = Swap
        
        self.SortTheListQ(ListPtr, i1, Start)
        self.SortTheListQ(ListPtr, Size - i1, i1 + Start)

    def SortTheListS(self, ListPtr : [], Size : int, Start : int = 0):
        if Size < 2:
            return
        
        Step = Size >> 1
        
        while Step > 0:
            for i in range(Step, Size):
                if ListPtr[i - Step + Start].ZOffset > ListPtr[i + Start].ZOffset:
                    j = i - Step
                    h : SortEntry = ListPtr[j + Step + Start]
                    
                    while True:
                        ListPtr[j + Step + Start] = ListPtr[j + Start]
                        j -= Step
                        if j < 0:
                            break
                        if ListPtr[j + Start].ZOffset <= h.ZOffset:
                            break
                        
                    ListPtr[j + Step + Start] = h

            Step >>= 1
            
    def GenerateFaceTexMatrix(self, TheChunk, TheFace, Channel, LayerEdit = -1):
        #Modes = TxAngle = TxScale = TxOffsX = TxOffsY = TxScale2 = TxOffsX2 = TxOffsY2 = 0
        
        # 3
        
        # START ORIG?
        # TestTxScale = self.TestTxScale
        # TestTxAngle = self.TestTxAngle
        # TestTxOffsetX = self.TestTxOffsetX
        # TestTxOffsetY = self.TestTxOffsetY
        
        # TestTxScale2 = self.TestTxScale2
        # TestTxOffsetX2 = self.TestTxOffsetX2
        # TestTxOffsetY2 = self.TestTxOffsetY2
        
        # if LayerEdit == 0:
        #     Modes = TheFace.fmModesEd[Channel]
        #     TxAngle = TestTxAngle
        #     TxScale = TestTxScale
        #     TxOffsX = TestTxOffsetX
        #     TxOffsY = TestTxOffsetY
        # else:
        #     Modes = TheFace.fmModes[Channel]
        #     TxAngle = TheFace.fmTxAngle[Channel]
        #     TxScale = TheFace.fmTxScale[Channel]
        #     TxOffsX = TheFace.fmTxOffsX[Channel]
        #     TxOffsY = TheFace.fmTxOffsY[Channel]
            
        # if LayerEdit == 1:
        #     TxScale2 = TestTxScale2
        #     TxOffsX2 = TestTxOffsetX2
        #     TxOffsY2 = TestTxOffsetY2
        # else:
        #     TxScale2 = TheFace.fmTxScale2[Channel]
        #     TxOffsX2 = TheFace.fmTxOffsX2[Channel]
        #     TxOffsY2 = TheFace.fmTxOffsY2[Channel]
            
        # Channel &= 1
        
        # Matrix = TheChunk.fcTexMatrix[Channel * 8 : Channel * 8 + 8] # --- TODO
        
        # # Texmatrix, use x/z
        # L = (TxScale - 100) / 20.0
        # L = math.exp(L + math.log(2.0)) / 480.0
        # A = TxAngle * 6.28318530718 / 360.0
        
        # if Modes == 1: # Proj X/Y
        #     # U
        #     Matrix[0] = math.cos(A) * L
        #     Matrix[1] = math.sin(A) * L
        #     Matrix[2] = 0.0
        #     Matrix[3] = TxOffsX / 256.0
        #     # V (negated)
        #     Matrix[4] = math.sin(A) * L
        #     Matrix[5] = -math.cos(A) * L
        #     Matrix[6] = 0.0
        #     Matrix[7] = -(TxOffsY / 256.0)
        # elif Modes == 2: # Proj Z/Y
        #     # U
        #     Matrix[0] = 0.0
        #     Matrix[1] = math.sin(A) * L
        #     Matrix[2] = math.cos(A) * L
        #     Matrix[3] = TxOffsX / 256.0
        #     # V (negated)
        #     Matrix[4] = 0.0
        #     Matrix[5] = -math.cos(A) * L
        #     Matrix[6] = math.sin(A) * L
        #     Matrix[7] = -(TxOffsY / 256.0)
        # else: # Proj X/Z
        #     # U
        #     Matrix[0] = math.cos(A) * L
        #     Matrix[1] = 0.0
        #     Matrix[2] = math.sin(A) * L
        #     Matrix[3] = TxOffsX / 256.0
        #     # V (negated)
        #     Matrix[4] = math.sin(A) * L
        #     Matrix[5] = 0.0
        #     Matrix[6] = -math.cos(A) * L
        #     Matrix[7] = -(TxOffsY / 256.0)
            
        # TheChunk.fcTexMatrix[Channel * 8:Channel * 8 + 8] = Matrix # --- TODO
            
        # Matrix2 = TheChunk.fcTexMod[Channel * 4 : Channel * 4 + 4] # --- TODO
        # A = (TxScale2 - 100) / 20.0
        # A = math.exp(A * math.log(2.0) / 480.0)
        # A /= L
        # Matrix2[2] = A # Aspect-ratio ?
        # Matrix2[3] = A
        # Matrix2[0] = (TxOffsX2 / 256.0 - Matrix[3] * A) % 1 # --- TODO
        # Matrix2[1] = (-TxOffsY2 / 256.0 - Matrix[7] * A) % 1 # --- TODO
        
        # TheChunk.fcTexMod[Channel * 4:Channel * 4 + 4] = Matrix2 # --- TODO
        # END ORIG?
        
        Modes = TheFace.fmModes[Channel]
        TxAngle = TheFace.fmTxAngle[Channel]
        TxScale = TheFace.fmTxScale[Channel]
        TxOffsX = TheFace.fmTxOffsX[Channel]
        TxOffsY = TheFace.fmTxOffsY[Channel]
        TxScale2 = TheFace.fmTxScale2[Channel]
        TxOffsX2 = TheFace.fmTxOffsX2[Channel]
        TxOffsY2 = TheFace.fmTxOffsY2[Channel]
        
        # Matrix = TheChunk.fcTexMatrix[Channel * 8 : Channel * 8 + 8]
        
        # # Texmatrix, use x/z
        # L = (TxScale - 100) / 20.0
        # L = math.exp(L + math.log(2.0)) / 480.0
        # A = TxAngle * 6.28318530718 / 360.0
        
        # # # (v) Proj X/Z
        # # # U
        # # Matrix[0] = math.cos(A) * L
        # # Matrix[1] = 0.0
        # # Matrix[2] = math.sin(A) * L
        # # Matrix[3] = TxOffsX / 256.0
        # # # V (negated)
        # # Matrix[4] = math.sin(A) * L
        # # Matrix[5] = 0.0
        # # Matrix[6] = -math.cos(A) * L
        # # Matrix[7] = -(TxOffsY / 256.0)
        
        # # (v) tex u1v1
        # L = -(TxScale-128.0)/128.0
        # L = math.pow(16.0,L)
        # # U
        # Matrix[0] = math.cos(A)*L
        # Matrix[1] = math.sin(A)*L
        # Matrix[2] = 0.0
        # Matrix[3] = TxOffsX / 256.0
        # # V (negated)
        # Matrix[4] = -math.sin(A)*L
        # Matrix[5] = math.cos(A)*L
        # Matrix[6] = 0.0
        # Matrix[7] = TxOffsY / 256.0
        
        # TheChunk.fcTexMatrix[Channel * 8:Channel * 8 + 8] = Matrix
            
        # Matrix2 = TheChunk.fcTexMod[Channel * 4 : Channel * 4 + 4]
        # A = (TxScale2 - 100) / 20.0
        # A = math.exp(A * math.log(2.0) / 480.0)
        # A /= L
        # Matrix2[2] = A # Aspect-ratio ?
        # Matrix2[3] = A
        # Matrix2[0] = (TxOffsX2 / 256.0 - Matrix[3] * A) % 1
        # Matrix2[1] = (-TxOffsY2 / 256.0 - Matrix[7] * A) % 1
        
        # TheChunk.fcTexMod[Channel * 4:Channel * 4 + 4] = Matrix2

        TheChunk.fcTexMod[Channel * 4:Channel * 4 + 4] = [TxOffsX, TxOffsY, TxScale / 100.0, TxScale / 100.0]
        
        # "Pruefsumme" bilden
        CheckSum = Modes
        CheckSum ^= TxAngle << 2
        CheckSum ^= TxScale << 11
        CheckSum ^= TxOffsX << 19
        CheckSum ^= TxOffsY << 24
        CheckSum ^= TxScale2
        CheckSum ^= TxOffsX2 << 8
        CheckSum ^= TxOffsY2 << 16
        TheChunk.fcTMCRC[Channel] = CheckSum
           
    def CollectVllPolys(self, Collected : [], CollNum_REF : [], Index : int, VertLinkList : []):
        Hash = Tri = 0
        i = 0
        
        if CollNum_REF[0] >= 64:
            return
        
        Hash = self.VertexMatInfoPtr[Index].viNext

        while Hash >= 0:
            Tri = VertLinkList[Hash].vhTri
            
            if self.FacesMatInfoPtr[Tri].fmSelected == 0:
                # Schon vorhanden ?
                for i in range(CollNum_REF[0]):
                    if Collected[i] == Tri:
                        Tri = -1
                        break
                    
                if Tri >= 0:
                    Collected[CollNum_REF[0]] = Tri
                    CollNum_REF[0] += 1
                    if CollNum_REF[0] >= 64:
                        break
            
            #
            Hash = VertLinkList[Hash].vhNext

    def OptiCheckKantenFree(self, Poly1 : int, List : [], VertLinkList : []):
        a = b = a_ = b_ = 0
        Collected = [0 for _ in range(64)] # --- TODO
        i = i2 = i3 = i4 = 0
        Count = 0
        
        for i2 in range(3):
            List[i2] = 0
            
            a = self.FacesMatInfoPtr[Poly1].fmPoly[i2].seIndex
            
            if i2 < 2:
                b = self.FacesMatInfoPtr[Poly1].fmPoly[i2 + 1].seIndex
            else:
                b = self.FacesMatInfoPtr[Poly1].fmPoly[0].seIndex
        
            #
            CollNum_REF = [0]
            self.CollectVllPolys(Collected, CollNum_REF, a, VertLinkList)
            
            for i3 in range(CollNum_REF[0]):
                if Collected[i3] == Poly1:
                    continue
                
                for i4 in range(3):
                    a_ = self.FacesMatInfoPtr[Collected[i3]].fmPoly[i4].seIndex
                    
                    if i4 < 2:
                        b_ = self.FacesMatInfoPtr[Collected[i3]].fmPoly[i4 + 1].seIndex
                    else:
                        b_ = self.FacesMatInfoPtr[Collected[i3]].fmPoly[0].seIndex
                        
                    if (((a == a_) and (b == b_)) or ((a == b_) and (b == a_))):
                        List[i2] += 1
                        
            if List[i2] == 0:
                Count += 1
                
        return Count

    def OptimizePolyChunk(self, Poly1 : int, PolysNum : int, CacheSize : int):
        VertLinkList = [VllHash() for _ in range(PolysNum * 3)]
        ResortList = [0 for _ in range(PolysNum)] # --- TODO
        p = hl = 0
        Prev_REF = [0]
        NewTri = 0
        Last = [0 for _ in range(3)] # --- TODO
        Collected = [0 for _ in range(64)] # --- TODO
        CollectedABC = [[0 for _ in range(64)] for _ in range(3)] # --- TODO
        CollNumABC = [0 for _ in range(3)] # --- TODO
        i = i2 = i3 = i4 = CollNum = 0
        StripSize = 0
        WindLeft = True
        StripID = 0
        
        # Alle Verweise loeschen
        VllSize = 0
        
        for i in range(PolysNum):
            for i2 in range(3):
                p = self.FacesMatInfoPtr[i + Poly1].fmPoly[i2].seIndex
                self.VertexMatInfoPtr[p].viNext = -1
                self.VertexMatInfoPtr[p].viTexFree = StripID
                self.VertexMatInfoPtr[p].viSelected = 0
                
        # Punkte Dreiecken zuweisen
        for i in range(PolysNum):
            self.FacesMatInfoPtr[i + Poly1].fmSelected = 0
            
            for i2 in range(3):
                p = self.FacesMatInfoPtr[i + Poly1].fmPoly[i2].seIndex
                self.VertexMatInfoPtr[p].viSelected += 1
                
                # Durch verkettete Liste steppen
                Prev_REF = [self.VertexMatInfoPtr[p].viNext] # --- TODO
                hl = Prev_REF[0] # --- TODO
                
                while hl >= 0:
                    Prev_REF = [VertLinkList[hl].vhNext]
                    hl = Prev_REF[0]
                
                # Neuen Eintrag anlegen
                VertLinkList[VllSize].vhTri = i + Poly1
                VertLinkList[VllSize].vhNext = -1
                
                Prev_REF[0] = VllSize
                VllSize += 1
        
        # Startdreieck aussuchen
        Current = -1
        Done = 0
        StripSize = 0
        StripID += 1
        
        # "Strips" erzeugen
        while Done < PolysNum:
            NewTri = -1
            CollNum = 0
            
            if Current >= 0:
                Collected2 = [0 for _ in range(64)]
                CollNum2_REF = [0]
                
                # Irgendwie Angrenzende sammeln
                for i in range(3):
                    self.CollectVllPolys(Collected2, CollNum2_REF, self.FacesMatInfoPtr[Current].fmPoly[i].seIndex, VertLinkList) # --- TODO
                    
                if CollNum2_REF[0] > 0:
                    a = b = a_ = b_ = 0
                    List = [0 for _ in range(3)]
                    Marked = [0 for _ in range(64)]
                    
                    #Polys filtern die an Kanten grenzen
                    for i in range(CollNum2_REF[0]):
                        Marked[i] = 0
                        
                    for i in range(3):
                        CollNumABC[i] = 0
                        
                        # Kante laden
                        a = self.FacesMatInfoPtr[Current].fmPoly[i].seIndex
                        
                        if i < 2:
                            b = self.FacesMatInfoPtr[Current].fmPoly[i + 1].seIndex
                        else:
                            b = self.FacesMatInfoPtr[Current].fmPoly[0].seIndex
                            
                        #
                        for i2 in range(CollNum2_REF[0]):
                            for i3 in range(3):
                                # Kante laden
                                a_ = self.FacesMatInfoPtr[Collected2[i2]].fmPoly[i3].seIndex
                                
                                if i3 < 2:
                                    b_ = self.FacesMatInfoPtr[Collected2[i2]].fmPoly[i3 + 1].seIndex
                                else:
                                    b_ = self.FacesMatInfoPtr[Collected2[i2]].fmPoly[0].seIndex
                                
                                #
                                if (((a == a_) and (b == b_)) or ((a == b_) and (b == a_))):
                                    Marked[i2] = 1
                                    CollectedABC[i][CollNumABC[i]] = Collected2[i2] # --- TODO

                                    CollNumABC[i] += 1
    
                                    if CollNumABC[i] >= 64: # Nur bei kaputten Dreiecken moeglich !
                                        break

                    for i in range(CollNum2_REF[0]):
                        if Marked[i] != 0:
                            Collected[CollNum] = Collected2[i]
                            CollNum += 1
                            
                    # In "Collected[]" sind jetzt alle anhaengenden Tris
                    if CollNum > 0:
                        if CollNum == 1:
                            NewTri = Collected[0]
                        else:
                            # Letzte nicht freie Kante suchen
                            if WindLeft:
                                for i in range(3):
                                    a = i - 1
                                    
                                    if a < 0:
                                        a += 3
                                    
                                    b = i
                                    
                                    if CollNumABC[b] == 0:
                                        # Vorige nicht ?
                                        if CollNumABC[a] != 0:
                                            NewTri = CollectedABC[a][0]
                            else:
                                for i in range(3):
                                    a = i + 1
                                    
                                    if a > 2:
                                        a -= 3
                                    
                                    b = i
                                    
                                    if CollNumABC[b] == 0:
                                        # Naechste nicht ?
                                        if CollNumABC[a] != 0:
                                            NewTri = CollectedABC[a][0]
                            if NewTri < 0:
                                NewTri = Collected[0]
                    else:
                        NewTri = Collected2[0]
                        StripSize = 0
                        WindLeft = not WindLeft
                        StripID += 1
                                        
            if NewTri < 0:
                List = [0 for _ in range(3)]
                List2 = [0 for _ in range(3)]
                a = b = a_ = b_ = 0
                
                StripID += 1
                # Neuen Strip beginnen
                StripSize = 0
                # Polygon an Kante suchen
                
                i4 = 0
                i3 = -1
                
                for i in range(PolysNum):
                    if self.FacesMatInfoPtr[i + Poly1].fmSelected == 0:
                        i2 = self.OptiCheckKantenFree(i + Poly1, List, VertLinkList)
                        
                        if i2 > i4:
                            i4 = i2
                            i3 = i + Poly1
                            List2[0] = List[0]
                            List2[1] = List[1]
                            List2[2] = List[2]

                            if i4 > 1:
                                break
                            
                if i3 >= 0:
                    NewTri = i3
                    
            if NewTri < 0:
                # Irgend eins nehmen, war nix zu finden (Keine freie Kante ?)
                for i in range(PolysNum):
                    if self.FacesMatInfoPtr[i + Poly1].fmSelected == 0:
                        NewTri = i + Poly1
                        break
                    
            # Dreieck speichern
            Current = NewTri
            ResortList[Done] = Current
            Done += 1
            
            for i in range(3):
                Last[i] = self.FacesMatInfoPtr[Current].fmPoly[i].seIndex
                self.VertexMatInfoPtr[Last[i]].viSelected -= 1
                
                if self.VertexMatInfoPtr[Last[i]].viTexFree != 0:
                    self.VertexMatInfoPtr[Last[i]].viTexFree = StripID
                    
            self.FacesMatInfoPtr[Current].fmSelected = 1
            
            StripSize += 1
            
            if StripSize >= 10:
                StripSize = 0
                WindLeft = not WindLeft
                StripID += 1
        
        #print(f"len(self.FacesMatInfoPtr) = {len(self.FacesMatInfoPtr)}")
        
        # Dreiecke umsortieren
            
        # V1
        # MatPtr2 = [FaceMatItem() for _ in range(PolysNum)]
        
        # for i in range(PolysNum):
        #     MatPtr2[i] = self.FacesMatInfoPtr[ResortList[i]]
            
        # for i in range(PolysNum):
        #     self.FacesMatInfoPtr[Poly1 + i] = MatPtr2[i]

        # V2
        MatPtr2 = [self.FacesMatInfoPtr[ResortList[i]] for i in range(PolysNum)] # --- TODO
        
        for i in range(PolysNum):
           self.FacesMatInfoPtr[Poly1 + i] = MatPtr2[i]
            
        # V3
        # for i in range(PolysNum):
        #     self.FacesMatInfoPtr[Poly1 + i] = self.FacesMatInfoPtr[ResortList[i]]
        
    def CopyEngineVertex(self, VbufPtr1 : MyVtxStruct1, VbufPtr2 : MyVtxStructE):
        VbufPtr2.x = VbufPtr1.x
        VbufPtr2.y = VbufPtr1.y
        VbufPtr2.z = VbufPtr1.z
        
        # Pack normal, TODO: 10Bit fuer Xbox ?
        # a = int((VbufPtr1.nx + 1.0) * 128.0)
        # b = int((VbufPtr1.ny + 1.0) * 128.0)
        # c = int((VbufPtr1.nz + 1.0) * 128.0)
        
        # TODO
        a = int(VbufPtr1.nx * 255)
        b = int(VbufPtr1.ny * 255)
        c = int(VbufPtr1.nz * 255)
        
        if a < 0:
            a = 0
        if a > 255:
            a = 255
        if b < 0:
            b = 0
        if b > 255:
            b = 255
        if c < 0:
            c = 0
        if c > 255:
            c = 255
            
        VbufPtr2.normal = (a << 16) | (b << 8) | c
        
        # Texcoords
        VbufPtr2.tu = VbufPtr1.tu
        VbufPtr2.tv = VbufPtr1.tv
        VbufPtr2.tu2 = VbufPtr1.tu2
        VbufPtr2.tv2 = VbufPtr1.tv2
        
        # Alphas and shadows
        VbufPtr2.color = VbufPtr1.color
        VbufPtr2.specular = VbufPtr1.specular #& 0x00ffffff

    def FlushVertexBuffer(self, VbIndex : int, VxPtr : [], VxPtr2 : [], Size : int):
        self.VxBufDrive[VbIndex] = copy.deepcopy(VxPtr[:Size])
        self.VxBufDrive2[VbIndex] = copy.deepcopy(VxPtr2[:Size])
        self.VxBufDriveSizes[VbIndex] = Size

    def VertexCacheOptimize(self, QuadsFlag : bool):
        i = i2 = Poly1 = PolysNum = p = 0
        
        # Jeden Chunk einzeln optimieren
        if QuadsFlag:
            for i in range(self.FacesTexChunksNum2):
                p = i * 100 // self.FacesTexChunksNum2
                
                Poly1 = self.FacesTexChunksPtr2[i].fcFirstPoly
                PolysNum = self.FacesTexChunksPtr2[i].fcNumPolys
                self.OptimizePolyChunk(Poly1, PolysNum, 18)
        else:
            for i in range(self.FacesTexChunksNum):
                p = i * 100 // self.FacesTexChunksNum
                
                Poly1 = self.FacesTexChunksPtr[i].fcFirstPoly
                PolysNum = self.FacesTexChunksPtr[i].fcNumPoly
                self.OptimizePolyChunk(Poly1, PolysNum, 18)
        
        # Indices updaten
        Indices1Ptr_INDEX = 0

        for i in range(self.Indices1Num // 3):
            for i2 in range(3):
                self.IxBuf1[Indices1Ptr_INDEX] = self.FacesMatInfoPtr[i].fmPoly[i2].seIndex
                Indices1Ptr_INDEX += 1
    
    def ResortToQuadrants(self, aQuadrantSize : float = 1024.0, aSortBorderToSingleQuad : bool = False):
        scenario_obj = self.scenario_obj
        landscape_scale = self.landscape_scale
        
        scenario_bbox_local = [Vector(corner) for corner in scenario_obj.bound_box]
        scenario_bbox_world = [scenario_obj.matrix_world @ corner for corner in scenario_bbox_local]
        
        #print(f"scenario_bbox_local: {scenario_bbox_local}")
        #print(f"scenario_bbox_world: {scenario_bbox_world}")
        
        min_x, min_y = math.inf, math.inf
        max_x, max_y = -math.inf, -math.inf

        for x, y, z in scenario_bbox_world:
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)
    
        dimensions_x = max_x * 2.0
        dimensions_y = max_y * 2.0
        print(f"dimensions_x, dimensions_y: {dimensions_x}, {dimensions_y}")
        
        self.TerrainSizeX = int((dimensions_x * landscape_scale) / 64)
        self.TerrainSizeY = int((dimensions_y * landscape_scale) / 64)
        print(f"TerrainSizeX, TerrainSizeY: {self.TerrainSizeX}, {self.TerrainSizeY}")
        
        ix = int(math.floor((dimensions_x * landscape_scale) / aQuadrantSize + 0.5))
        iy = int(math.floor((dimensions_y * landscape_scale) / aQuadrantSize + 0.5))
        print(f"ix, iy: {ix}, {iy}")
        
	    # Pruefen ob End of World vorhanden
        scenarioExtentX = math.floor((dimensions_x * landscape_scale) / 1024.0 + 0.5) * 1024.0
        scenarioExtentZ = math.floor((dimensions_y * landscape_scale) / 1024.0 + 0.5) * 1024.0
        print(f"scenarioExtentX, scenarioExtentZ: {scenarioExtentX}, {scenarioExtentZ}")
        
        HasEndQuads = False;
        
        for i in range(self.VxBuf1Size):
            if self.VxBuf1[i].x > scenarioExtentX or self.VxBuf1[i].x < -scenarioExtentX:
                HasEndQuads = True;
            
            if self.VxBuf1[i].z > scenarioExtentZ or self.VxBuf1[i].z < -scenarioExtentZ:
                HasEndQuads = True;
        
        print(f"HasEndQuads: {HasEndQuads}")
        
        if not HasEndQuads:
            aSortBorderToSingleQuad = False;
            
        if HasEndQuads and not aSortBorderToSingleQuad:
            ix += 2 # Border !
            iy += 2
            
        self.QuadsNum = ix * iy
        self.QuadsNumX = ix
        self.QuadsNumY = iy
        
        print(f"quad size: {scenarioExtentX / ix}, {scenarioExtentZ / iy}")
        
        print(f"self.QuadsNumX = {self.QuadsNumX}")
        print(f"self.QuadsNumY = {self.QuadsNumY}")
        print(f"self.QuadsNum = {self.QuadsNum}")
        
        if HasEndQuads and aSortBorderToSingleQuad:
            self.QuadsNum += 1
            
        self.TerrainQuadList = [QuadItem() for _ in range(self.QuadsNum)]
        QuadSortingList = [SortEntry() for _ in range(self.Indices1Num // 3)]

        for i in range(self.Indices1Num // 3):
            x = 0.0
            y = 0.0
            
            for i2 in range(3):
                p = self.IxBuf1[i * 3 + i2]
                x += self.VxBuf1[p].x
                y += self.VxBuf1[p].z
                
            x /= 3.0
            y /= 3.0
            
            if x < -scenarioExtentX:
                ix = -1
            elif x > scenarioExtentX:
                ix = self.QuadsNumX
            else:
                ix = math.floor((x / aQuadrantSize)) + (self.QuadsNumX >> 1)
                
            if y < -scenarioExtentZ:
                iy = -1
            elif y > scenarioExtentZ:
                iy = self.QuadsNumY
            else:
                iy = math.floor((y / aQuadrantSize)) + (self.QuadsNumY >> 1)
                
            # Als Quadrant
            
            if aSortBorderToSingleQuad:
                if (ix < 0) or (ix >= self.QuadsNumX) or (iy < 0) or (iy >= self.QuadsNumY):
                    ix = 0
                    iy = self.QuadsNumY
            else:
                if ix < 0:
                    ix = 0
                if ix >= self.QuadsNumX:
                    ix = self.QuadsNumX - 1
                if iy < 0:
                    iy = 0
                if iy >= self.QuadsNumY:
                    iy = self.QuadsNumY - 1
                    
            #print(f"ix, iy = {ix}, {iy}")

            QuadSortingList[i].PIndex = i
            QuadSortingList[i].ZOffset = (iy << 16) | ix # Quadrant-ID
            
        # Sortieren
        self.SortTheListQ(QuadSortingList, (self.Indices1Num // 3))

        # Flaechen umkopieren
        Indices2Ptr = [self.IxBuf1[i] for i in range(self.Indices1Num)]
        
        for i in range(self.Indices1Num // 3):
            self.IxBuf1[i * 3] = Indices2Ptr[QuadSortingList[i].PIndex * 3]
            self.IxBuf1[i * 3 + 1] = Indices2Ptr[QuadSortingList[i].PIndex * 3 + 1]
            self.IxBuf1[i * 3 + 2] = Indices2Ptr[QuadSortingList[i].PIndex * 3 + 2]

        # Flaecheninfos umkopieren
        MatPtr2 = [self.FacesMatInfoPtr[i] for i in range(self.Indices1Num // 3)] # --- TODO
        
        self.FacesMatInfoPtr = [MatPtr2[QuadSortingList[i].PIndex] for i in range(self.Indices1Num // 3)] # --- TODO

        # Quadranten sammeln
        LastQuad = 0x12345678
        QuadIndex = QuadX = QuadY = 0
        
        for i in range(self.Indices1Num // 3):
            if QuadSortingList[i].ZOffset != LastQuad:
                LastQuad = QuadSortingList[i].ZOffset
                QuadX = LastQuad & 0xffff
                QuadY = LastQuad >> 16
                QuadIndex = QuadX + QuadY * self.QuadsNumX
                self.TerrainQuadList[QuadIndex].qiPolysNum = 0
                self.TerrainQuadList[QuadIndex].qiPolysNum2 = 0
                self.TerrainQuadList[QuadIndex].qiStartIndex = i
                self.TerrainQuadList[QuadIndex].qiQuadX = QuadX
                self.TerrainQuadList[QuadIndex].qiQuadY = QuadY
                self.TerrainQuadList[QuadIndex].qiObject1 = -1
                self.TerrainQuadList[QuadIndex].qiObjectsNum = 0
                self.TerrainQuadList[QuadIndex].qiLight1 = -1
                self.TerrainQuadList[QuadIndex].qiLightsNum = 0
            
                #print(f"{LastQuad}, {QuadIndex} - qiQuadX, qiQuadY: {self.TerrainQuadList[QuadIndex].qiQuadX}, {self.TerrainQuadList[QuadIndex].qiQuadY}")
            
            # TODO
            self.TerrainQuadList[QuadIndex].qiPolysNum += 1
            
            if self.TerrainQuadList[QuadIndex].qiPolysNum > 0xFFFF:
                raise Exception(f"Exceeded polygon limit for quad {QuadIndex} ({QuadX} {QuadY})")
            
        # Mittelpunkte und Radien festlegen
        for i in range(self.QuadsNum):
            x = y = z = mx = my = mz = R = L = 0
            MinX = MinY = MinZ = MaxX = MaxY = MaxZ = 0.0

            First = True

            if i < self.QuadsNumX * self.QuadsNumY:
                mx = aQuadrantSize * (self.TerrainQuadList[i].qiQuadX - (self.QuadsNumX >> 1)) + 0.5 * aQuadrantSize
                mz = aQuadrantSize * (self.TerrainQuadList[i].qiQuadY - (self.QuadsNumY >> 1)) + 0.5 * aQuadrantSize
            else:
                mx = 0.0
                mz = 0.0
                
            MinX = MaxX = mx
            MinY = MaxY = 0.0
            MinZ = MaxZ = mz

            for i2 in range(self.TerrainQuadList[i].qiPolysNum):
                iy = self.TerrainQuadList[i].qiStartIndex + i2
                
                for ix in range(3):
                    p = self.IxBuf1[iy * 3 + ix]
                    x = self.VxBuf1[p].x
                    y = self.VxBuf1[p].y
                    z = self.VxBuf1[p].z
                    
                    if First:
                        First = False
                        MinX = x
                        MinY = y
                        MinZ = z
                        MaxX = x
                        MaxY = y
                        MaxZ = z
                    else:
                        if x < MinX:
                            MinX = x
                        if y < MinY:
                            MinY = y
                        if z < MinZ:
                            MinZ = z
                        if x > MaxX:
                            MaxX = x
                        if y > MaxY:
                            MaxY = y
                        if z > MaxZ:
                            MaxZ = z

            mx = (MinX + MaxX) * 0.5
            my = (MinY + MaxY) * 0.5
            mz = (MinZ + MaxZ) * 0.5
            R = 0
            
            for i2 in range(self.TerrainQuadList[i].qiPolysNum):
                iy = self.TerrainQuadList[i].qiStartIndex + i2
                
                for ix in range(3):
                    p = self.IxBuf1[iy * 3 + ix]
                    x = self.VxBuf1[p].x - mx
                    y = self.VxBuf1[p].y - my
                    z = self.VxBuf1[p].z - mz
                    L = math.sqrt(x * x + y * y + z * z)
                    
                    if (L > R):
                        R = L
            
            self.TerrainQuadList[i].qiMidX = mx
            self.TerrainQuadList[i].qiMidY = my
            self.TerrainQuadList[i].qiMidZ = mz
            self.TerrainQuadList[i].qiRadius = R

        # Fuer jeden Quadranten Polys nach Texturen sortieren
        for i in range(self.Indices1Num // 3):
            QuadSortingList[i].PIndex = i
            QuadSortingList[i].ZOffset = self.FacesMatInfoPtr[i].fmChunk
            #print(f"(B) fmChunk {self.FacesMatInfoPtr[i].fmChunk}")
            
        # Jeden Quadranten einzeln sortieren
        for i in range(self.QuadsNum):
            self.SortTheListQ(QuadSortingList, self.TerrainQuadList[i].qiPolysNum, self.TerrainQuadList[i].qiStartIndex)
            
        # Flaechen sortiert umkopieren
        Indices2Ptr = [self.IxBuf1[i] for i in range(self.Indices1Num)]
        
        for i in range(self.Indices1Num // 3):
            self.IxBuf1[i * 3] = Indices2Ptr[QuadSortingList[i].PIndex * 3]
            self.IxBuf1[i * 3 + 1] = Indices2Ptr[QuadSortingList[i].PIndex * 3 + 1]
            self.IxBuf1[i * 3 + 2] = Indices2Ptr[QuadSortingList[i].PIndex * 3 + 2]

        # Flaecheninfos umkopieren
        MatPtr2 = [self.FacesMatInfoPtr[i] for i in range(self.Indices1Num // 3)]
        self.FacesMatInfoPtr = [MatPtr2[QuadSortingList[i].PIndex] for i in range(self.Indices1Num // 3)]
        
		# Anzahl Chunks ermitteln
        LastTex = 0
        NumFound = 0
        
        for i in range(self.QuadsNum):
            LastTex = 0xffffffff
            
            if self.TerrainQuadList[i].qiPolysNum > 0:
                ix = self.TerrainQuadList[i].qiStartIndex
                iy = self.TerrainQuadList[i].qiPolysNum
                
                for i2 in range(ix, ix + iy):
                    if LastTex != QuadSortingList[i2].ZOffset:
                        LastTex = QuadSortingList[i2].ZOffset
                        NumFound += 1
                        
        # Speicher anlegen
        self.FacesTexChunksNum2 = NumFound;
        self.FacesTexChunksPtr2 = [FaceMatChunk() for _ in range(self.FacesTexChunksNum2)]

        # Fuer jeden Quadranten Chunkliste erzeugen
        NumFound = 0
        
        for i in range(self.QuadsNum):
            LastTex = 0xffffffff
            
            self.TerrainQuadList[i].qiChunk1 = NumFound
            self.TerrainQuadList[i].qiChunksNum = 0
            
            if self.TerrainQuadList[i].qiPolysNum > 0:
                ix = self.TerrainQuadList[i].qiStartIndex
                iy = self.TerrainQuadList[i].qiPolysNum
                
                for i2 in range(ix, ix + iy):
                    if LastTex != QuadSortingList[i2].ZOffset:
                        LastTex = QuadSortingList[i2].ZOffset
                        
                        p = NumFound
                        NumFound += 1
                        
                        self.TerrainQuadList[i].qiChunksNum += 1
                        self.FacesTexChunksPtr2[p].fcFirstPoly = i2
                        self.FacesTexChunksPtr2[p].fcNumPolys = 0;
                        self.FacesTexChunksPtr2[p].fcTextures[0] = self.FacesMatInfoPtr[i2].fmTextures[0]
                        self.FacesTexChunksPtr2[p].fcTextures[1] = self.FacesMatInfoPtr[i2].fmTextures[1]
                        self.FacesTexChunksPtr2[p].fcTextures[2] = self.FacesMatInfoPtr[i2].fmTextures[2]
                        self.FacesTexChunksPtr2[p].fcTextures[3] = self.FacesMatInfoPtr[i2].fmTextures[3]
                        self.FacesTexChunksPtr2[p].fcTyp = self.FacesMatInfoPtr[i2].fmTyp
                        self.FacesTexChunksPtr2[p].fcChunk = self.FacesMatInfoPtr[i2].fmChunk
                        self.FacesTexChunksPtr2[p].fcGeoLayer = self.FacesMatInfoPtr[i2].fmGeoLayer
                        self.GenerateFaceTexMatrix(self.FacesTexChunksPtr2[p], self.FacesMatInfoPtr[i2], 0)
                        self.GenerateFaceTexMatrix(self.FacesTexChunksPtr2[p], self.FacesMatInfoPtr[i2], 1)
                        
                    self.FacesTexChunksPtr2[p].fcNumPolys += 1
                    
        print(f"NumChunks: {self.FacesTexChunksNum2}")
        print(f" NumQuads: {self.QuadsNum}")

	    # Objekte Quadranten zuordnen
        if self.LedObjectsSetNum > 0:
            ObjPosBup = [LedObjectPos() for _ in range(self.LedObjectsSetNum)]
            ObjSortingList = [SortEntry() for _ in range(self.LedObjectsSetNum)]
            
            for i in range(self.LedObjectsSetNum):
                ix = math.floor((self.LedObjectPosList[i].lpXpos / 1024.0))
                iy = math.floor((self.LedObjectPosList[i].lpZpos / 1024.0))
                ix += self.QuadsNumX >> 1
                iy += self.QuadsNumY >> 1
                
                if ix < 0:
                    ix = 0
                
                if ix >= self.QuadsNumX:
                    ix = self.QuadsNumX - 1
                
                if iy >= self.QuadsNumY:
                    iy = self.QuadsNumY - 1
                    
                ObjSortingList[i].PIndex = i
                ObjSortingList[i].ZOffset = (iy << 16) | ix # Quadrant-ID
                
            # Sortieren
            self.SortTheListQ(ObjSortingList, self.LedObjectsSetNum)
            
            # Umkopieren
            for i in range(self.LedObjectsSetNum):
                ObjPosBup[i] = self.LedObjectPosList[i]
                
            for i in range(self.LedObjectsSetNum):
                self.LedObjectPosList[i] = ObjPosBup[ObjSortingList[i].PIndex]
                
            for i in range(self.LedObjectsSetNum):
                ix = ObjSortingList[i].ZOffset & 0xffff
                iy = ObjSortingList[i].ZOffset >> 16
                
                ix += iy * self.QuadsNumX
                
                if self.TerrainQuadList[ix].qiObject1 < 0:
                    self.TerrainQuadList[ix].qiObject1 = i
                
                self.TerrainQuadList[ix].qiObjectsNum += 1
    
    def ResortVertices(self):
        i = i2 = c = 0
        # Quad-statistik
        i3 = p = ix = iy = n = 0
        TempVxBuf = [MyVtxStructE() for _ in range(65536)]
        TempVxBuf2 = [MyTang1() for _ in range(65536)]
        
        t0 = 0
        t = 0
        v = 0
        TempVxPtr = TempVxBuf
        TempVxPtr2 = TempVxBuf2
        IndicesCopied = 0
        VerticesCopied = 0
        
        Indices2Ptr = []
        
        for ix in range(self.VxBuf1Size):
            self.VertexMatInfoPtr[ix].viTexFree = -1
            self.VertexMatInfoPtr[ix].viSelected = 0xff
            self.VertexMatInfoPtr[ix].viNext = 0
            
        i = 0
            
        while i < self.QuadsNum:
            self.TerrainQuadList[i].qiVxBufIndex = v
            
            # Neue Punkte zaehlen
            n = 0
            
            for i2 in range(self.TerrainQuadList[i].qiPolysNum):
                p = i2 + self.TerrainQuadList[i].qiStartIndex
                
                for i3 in range(3):
                    c = self.FacesMatInfoPtr[p].fmPoly[i3].seIndex

                    if self.VertexMatInfoPtr[c].viSelected != v:
                        self.VertexMatInfoPtr[c].viSelected = v
                        n += 1
                        
            if (t + n) >= 65536:
                print(f"Flushing Vertexbuffer {v} ({VerticesCopied} Vertices)")
                self.FlushVertexBuffer(v, TempVxPtr, TempVxPtr2, VerticesCopied)
                t = 0
                v += 1
                VerticesCopied = 0
                continue
            
            t += n
            t0 += n
        
            print(f"Quad{i}: {n}\t{t}")
            
            # Neue Punkte speichern
            for i2 in range(self.TerrainQuadList[i].qiPolysNum):
                p = i2 + self.TerrainQuadList[i].qiStartIndex
            
                indices = []

                for i3 in range(3):
                    c = self.FacesMatInfoPtr[p].fmPoly[i3].seIndex
                
                    if self.VertexMatInfoPtr[c].viTexFree != v:
                        self.VertexMatInfoPtr[c].viTexFree = v
                        self.VertexMatInfoPtr[c].viNext = VerticesCopied
                    
                        # Punkt speichern
                        self.CopyEngineVertex(self.VxBuf1[c], TempVxPtr[VerticesCopied])
                        TempVxPtr2[VerticesCopied] = self.VxBuf2[c]
                        VerticesCopied += 1
                    
                    # Index reloziert kopieren
                    indices.append(self.VertexMatInfoPtr[c].viNext) # --- TODO
                    
                for i3 in range(3):
                    Indices2Ptr.append(indices[2 - i3])
                
            #
            i += 1
        
        self.FlushVertexBuffer(v, TempVxPtr, TempVxPtr2, VerticesCopied)
        
        self.IxBuf2 = Indices2Ptr[:self.Indices1Num]

        print(f" -> {t0} Vertices used total ({self.VxBuf1Size}) +{t0 - self.VxBuf1Size} extra")
        print(f" -> Number of Vertexbuffers: {v}")
    
    def ReCreateFaceNormals(self):
        i = i2 = 0
        
        lx = ly = lz = Len = 0.0

        #TerrainNormals = [SmpVertex() for _ in range(self.Indices1Num // 3)]

        # Normalenvektoren erzeugen
        Fvx = Fvy = Fvz = Fux = Fuy = Fuz = Nvx = Nvy = Nvz = 0.0
        a = b = c = 0
        
        for i in range(self.Indices1Num // 3):
            a = self.IxBuf1[i * 3]
            b = self.IxBuf1[i * 3 + 1]
            c = self.IxBuf1[i * 3 + 2]
            
            #print(f"a = {a}")
            #print(f"b = {b}")
            #print(f"c = {c}")
            
            Nvx = self.VxBuf1[a].x
            Nvy = self.VxBuf1[a].y
            Nvz = self.VxBuf1[a].z
            Fux = self.VxBuf1[b].x
            Fuy = self.VxBuf1[b].y
            Fuz = self.VxBuf1[b].z
            Fvx = self.VxBuf1[c].x
            Fvy = self.VxBuf1[c].y
            Fvz = self.VxBuf1[c].z
            
            # Create Vectors U,V
            Fvx -= Nvx
            Fvy -= Nvy
            Fvz -= Nvz
            Fux -= Nvx
            Fuy -= Nvy
            Fuz -= Nvz
            
            # Create Normalvector
            Nvx = Fuy * Fvz - Fuz * Fvy
            Nvy = Fuz * Fvx - Fux * Fvz
            Nvz = Fux * Fvy - Fuy * Fvx
            
            # Normalize
            Len = math.sqrt(Nvx*Nvx + Nvy*Nvy + Nvz*Nvz)
            
            if	Len > 0:
                Nvx /= Len
                Nvy /= Len
                Nvz /= Len
                
            #TerrainNormals[i].X = Nvx
            #TerrainNormals[i].Y = Nvy
            #TerrainNormals[i].Z = Nvz
            
            self.FacesMatInfoPtr[i].fmNormal.X = Nvx
            self.FacesMatInfoPtr[i].fmNormal.Y = Nvy
            self.FacesMatInfoPtr[i].fmNormal.Z = Nvz
            self.FacesMatInfoPtr[i].fmPolySize = Len
    
    def BoxTriangle2D(self, BoxCenter : Vector, BoxHalfSize : Vector, Vert0 : Vector, Vert1 : Vector, Vert2 : Vector):
        v0x = v0z = v1x = v1z = v2x = v2z = e0x = e0z = e1x = e1z = e2x = e2z = fex = fez = 0.0
        p0 = p1 = p2 = _min = _max = _rad = 0.0
		
        v0x = Vert0.x - BoxCenter.x
        v0z = Vert0.z - BoxCenter.z
        v1x = Vert1.x - BoxCenter.x
        v1z = Vert1.z - BoxCenter.z
        v2x = Vert2.x - BoxCenter.x
        v2z = Vert2.z - BoxCenter.z
		
        e0x = v1x - v0x
        e0z = v1z - v0z
        e1x = v2x - v1x
        e1z = v2z - v1z
        e2x = v0x - v2x
        e2z = v0z - v2z
		
        fex = math.fabs(e0x)
        fez = math.fabs(e0z)
		
        p0  = e0x * v0z - e0z * v0x
        p2  = e0x * v2z - e0z * v2x
        _rad = fez * BoxHalfSize.x + fex * BoxHalfSize.z
		
        if (p0 <= p2):
            _min = p0
            _max = p2
        else:
            _min = p2
            _max = p0
		
        if ((_min > _rad) or (_max < -_rad)):
            return False
		
        fex = math.fabs(e1x)
        fez = math.fabs(e1z)
		
        p0  = e1x * v0z - e1z * v0x
        p2  = e1x * v2z - e1z * v2x
        _rad = fez * BoxHalfSize.x + fex * BoxHalfSize.z
		
        if (p0 <= p2):
            _min = p0
            _max = p2
        else:
            _min = p2
            _max = p0
		
        if ((_min > _rad) or (_max < -_rad)):
            return False
		
        fex = math.fabs(e2x)
        fez = math.fabs(e2z)
		
        p0  = e2x * v0z - e2z * v0x
        p1  = e2x * v1z - e2z * v1x
        _rad = fez * BoxHalfSize.x + fex * BoxHalfSize.z
		
        if (p0 <= p1):
            _min = p0
            _max = p1
        else:
            _min = p1
            _max = p0
		
        if ((_min > _rad) or (_max < -_rad)):
            return False
		
        _min = v0x
        _max = v0x
		
        if (_min > v1x):
            _min = v1x
        elif (_max < v1x):
            _max = v1x
		
        if (_min > v2x):
            _min = v2x
        elif (_max < v2x):
            _max = v2x
		
        if ((_min > BoxHalfSize.x) or (_max < -BoxHalfSize.x)):
            return False
		
        _min = v0z
        _max = v0z
		
        if (_min > v1z):
            _min = v1z
        elif (_max < v1z):
            _max = v1z
		
        if (_min > v2z):
            _min = v2z
        elif (_max < v2z):
            _max = v2z
		
        if ((_min > BoxHalfSize.z) or (_max < -BoxHalfSize.z)):
            return False
        
        return True
        
    def CreateCollisionQuads2(self):
        i = ix = iy = i2 = 0
        p = 0
        
        # Kollisionsquadranten erzeugen
        MinX = MinZ = MaxX = MaxZ = 0.0
        qx1 = qz1 = qx2 = qz2 = 0.0
        x = z = 0.0
        qi = qix = qiz = qix1 = qiz1 = qix2 = qiz2 = 0
        
        collision_quads = []
        
        test_skip = False
        
        for iy in range(self.QuadsNumY * 4):
            for ix in range(self.QuadsNumX * 4):
                # Quadrantausmasse erzeugen
                qx1 = (ix - (self.QuadsNumX << 1)) * 256
                qz1 = (iy - (self.QuadsNumY << 1)) * 256
                qx2 = qx1 + 256.0
                qz2 = qz1 + 256.0
                    
                # Zugrunde liegender Quadrant,angrenzende mitnehmen
                qix2 = qix1 = ix >> 2
                qiz2 = qiz1 = iy >> 2
                qix1 -= 1
                qiz1 -= 1
                qix2 += 1
                qiz2 += 1
                    
                if	(qix1 < 0):
                    qix1 = 0
                if	(qiz1 < 0):
                    qiz1 = 0
                if	(qix2 >= self.QuadsNumX):
                    qix2 = self.QuadsNumX - 1
                if	(qiz2 >= self.QuadsNumY):
                    qiz2 = self.QuadsNumY - 1
                        
                collision_quad = CollisionQuad()
                collision_quad.items = {}

                for qiz in range(qiz1, qiz2 + 1):
                    for qix in range(qix1, qix2 + 1):
                        qi = qix + qiz * self.QuadsNumX
                        
                        collision_quad_item = CollisionQuadItem()
                        collision_quad_item.graphics_quad_index = qi
                            
                        if test_skip:
                            continue

                        for i in range(self.TerrainQuadList[qi].qiStartIndex, self.TerrainQuadList[qi].qiStartIndex + self.TerrainQuadList[qi].qiPolysNum):
                            Typ = self.FacesMatInfoPtr[i].fmTyp >> 4

                            if self.TexPropGroupsList[self.LedMaterialsList[self.FacesMatInfoPtr[i].fmTextures[0]].lmTexPropGroup].tpColliFlag == 1 and (Typ != MaterialType.mat_2L_Water.value):
                               continue
                                
                            if (self.FacesMatInfoPtr[i].fmSelSave & (1 << 23)) != 0:
                                continue
                                
                            # Schneidet Flaeche diesen Quadranten ? TODO: Mit Clipping ganz genau pruefen...
                            verts = [Vector() for _ in range(3)]
                                
                            # MinMax erzeugen
                            for i2 in range(3):
                                p = self.IxBuf1[i * 3 + i2]
                                x = self.VxBuf1[p].x
                                z = self.VxBuf1[p].z

                                if i2 == 0:
                                    MinX = MaxX = x
                                    MinZ = MaxZ = z
                                else:
                                    if x < MinX:
                                        MinX = x
                                    if z < MinZ:
                                        MinZ = z
                                    if x > MaxX:
                                        MaxX = x
                                    if z > MaxZ:
                                        MaxZ = z
                                    
                                verts[i2].x = x
                                verts[i2].y = 0.0
                                verts[i2].z = z
                                    
                            # Ueberlappung ?
                            #if (((MinX < qx2) and (MaxX > qx1)) or ((MinX == qx2) and (MaxX == qx2))) and (((MinZ < qz2) and (MaxZ > qz1)) or ((MinZ == qz2) and (MaxZ == qz2))) and self.BoxTriangle2D(Vector((qx1 + 128.0, 0.0, qz1 + 128.0)), Vector((128.0, 1.0, 128.0)), Vector(verts[0]), Vector(verts[1]), Vector(verts[2])):
                            if (
                                (((MinX < qx2) and (MaxX > qx1)) or ((MinX == qx2) and (MaxX == qx2))) and
								(((MinZ < qz2) and (MaxZ > qz1)) or ((MinZ == qz2) and (MaxZ == qz2))) and
								self.BoxTriangle2D(Vector((qx1 + 128.0, 0.0, qz1 + 128.0)),
								Vector((128.0, 1.0, 128.0)), verts[0], verts[1], verts[2])
                            ):
                                # Ok, Flaeche mitnehmen
                                if qi not in collision_quad.items:
                                    collision_quad.items[qi] = CollisionQuadItem()
                                    collision_quad.items[qi].graphics_quad_index = qi
                                    
                                collision_quad.items[qi].triangle_indices.append(i - self.TerrainQuadList[qi].qiStartIndex)
                                
                collision_quads.append(collision_quad)
                                
                # Endekennung
                    
        number_of_collision_quads = len(collision_quads)
        
        print(f"number_of_collision_quads = {number_of_collision_quads}")
        
        size_of_header = self.QuadsNumX * self.QuadsNumY* 16 * 4
            
        print(f"size_of_header = {size_of_header}")
        
        header_buffer = bytearray()
        data_buffer = bytearray()
        
        for i in range(number_of_collision_quads):
            collision_quad : CollisionQuad = collision_quads[i]
            
            data_buffer_offset = len(data_buffer)
            
            for graphics_quad_index, collision_quad_item in collision_quad.items.items():
                
                number_of_triangles = len(collision_quad_item.triangle_indices)
            
                data_buffer.extend(struct.pack('H', number_of_triangles))
            
                if number_of_triangles > 0:
                    data_buffer.extend(struct.pack('H', graphics_quad_index))
                
                    for i2 in range(number_of_triangles):
                        data_buffer.extend(struct.pack('H', collision_quad_item.triangle_indices[i2]))
                    
            data_buffer.extend(struct.pack('H', 0))
            
            header_buffer.extend(struct.pack('I', size_of_header + data_buffer_offset))
        
        size_of_data = len(data_buffer)
        
        print(f"size_of_data = {size_of_data}")
        
        self.CollQuadsData = header_buffer + data_buffer
        self.CollQuadsDataSize = size_of_header + size_of_data
        
        print(f"CollQuadsDataSize = {self.CollQuadsDataSize}")
        print(f"len(self.CollQuadsData) = {len(self.CollQuadsData)}")
        
    def CreateCollisionQuads(self):
        # Initialize variables
        MinX = MinZ = MaxX = MaxZ = 0.0
        qx1 = qz1 = qx2 = qz2 = 0.0
        x = z = 0.0
        qi = qix = qiz = qix1 = qiz1 = qix2 = qiz2 = 0

        # Buffers for header and data
        header_buffer = bytearray()
        data_buffer = bytearray()

        # Precompute header size
        size_of_header = self.QuadsNumX * self.QuadsNumY * 16 * 4

        for iy in range(self.QuadsNumY * 4):
            for ix in range(self.QuadsNumX * 4):
                # Quadrantausmasse erzeugen
                qx1 = (ix - (self.QuadsNumX << 1)) * 256
                qz1 = (iy - (self.QuadsNumY << 1)) * 256
                qx2 = qx1 + 256.0
                qz2 = qz1 + 256.0
                    
                # Zugrunde liegender Quadrant,angrenzende mitnehmen
                qix2 = qix1 = ix >> 2
                qiz2 = qiz1 = iy >> 2
                qix1 -= 1
                qiz1 -= 1
                qix2 += 1
                qiz2 += 1
                    
                if	(qix1 < 0):
                    qix1 = 0
                if	(qiz1 < 0):
                    qiz1 = 0
                if	(qix2 >= self.QuadsNumX):
                    qix2 = self.QuadsNumX - 1
                if	(qiz2 >= self.QuadsNumY):
                    qiz2 = self.QuadsNumY - 1

                # Write offsets to header
                data_buffer_offset = len(data_buffer)
                
                for qiz in range(qiz1, qiz2 + 1):
                    for qix in range(qix1, qix2 + 1):
                        qi = qix + qiz * self.QuadsNumX
                        
                        triangles_added = False
                        
                        for i in range(self.TerrainQuadList[qi].qiStartIndex, self.TerrainQuadList[qi].qiStartIndex + self.TerrainQuadList[qi].qiPolysNum):
                            Typ = self.FacesMatInfoPtr[i].fmTyp >> 4

                            if self.TexPropGroupsList[self.LedMaterialsList[self.FacesMatInfoPtr[i].fmTextures[0]].lmTexPropGroup].tpColliFlag == 1 and (Typ != MaterialType.mat_2L_Water.value):
                               continue
                                
                            if (self.FacesMatInfoPtr[i].fmSelSave & (1 << 23)) != 0:
                                continue
                                
                            # Schneidet Flaeche diesen Quadranten ? TODO: Mit Clipping ganz genau pruefen...
                            verts = [Vector() for _ in range(3)]
                                
                            # MinMax erzeugen
                            for i2 in range(3):
                                p = self.IxBuf1[i * 3 + i2]
                                x = self.VxBuf1[p].x
                                z = self.VxBuf1[p].z

                                if i2 == 0:
                                    MinX = MaxX = x
                                    MinZ = MaxZ = z
                                else:
                                    if x < MinX:
                                        MinX = x
                                    if z < MinZ:
                                        MinZ = z
                                    if x > MaxX:
                                        MaxX = x
                                    if z > MaxZ:
                                        MaxZ = z
                                    
                                verts[i2].x = x
                                verts[i2].y = 0.0
                                verts[i2].z = z
                                    
                            # Ueberlappung ?
                            #if (((MinX < qx2) and (MaxX > qx1)) or ((MinX == qx2) and (MaxX == qx2))) and (((MinZ < qz2) and (MaxZ > qz1)) or ((MinZ == qz2) and (MaxZ == qz2))) and self.BoxTriangle2D(Vector((qx1 + 128.0, 0.0, qz1 + 128.0)), Vector((128.0, 1.0, 128.0)), Vector(verts[0]), Vector(verts[1]), Vector(verts[2])):
                            if (
                                (((MinX < qx2) and (MaxX > qx1)) or ((MinX == qx2) and (MaxX == qx2))) and
								(((MinZ < qz2) and (MaxZ > qz1)) or ((MinZ == qz2) and (MaxZ == qz2))) and
								self.BoxTriangle2D(Vector((qx1 + 128.0, 0.0, qz1 + 128.0)),
								Vector((128.0, 1.0, 128.0)), verts[0], verts[1], verts[2])
                            ):
                                # Add triangle index to data buffer
                                if not triangles_added:
                                    triangle_count_offset = len(data_buffer)
                                    data_buffer.extend(struct.pack('H', 0))  # Placeholder for triangle count
                                    data_buffer.extend(struct.pack('H', qi))  # Graphics quad index
                                    triangles_added = True
                                    
                                #print(f"{i} - {self.TerrainQuadList[qi].qiStartIndex} = {i - self.TerrainQuadList[qi].qiStartIndex}")
                                data_buffer.extend(struct.pack('H', i - self.TerrainQuadList[qi].qiStartIndex))

                        if triangles_added:
                            # Write triangle count
                            triangle_count = (len(data_buffer) - triangle_count_offset - 4) // 2
                            struct.pack_into('H', data_buffer, triangle_count_offset, triangle_count)

                # End marker
                data_buffer.extend(struct.pack('H', 0))

                # Write header entry
                header_buffer.extend(struct.pack('I', size_of_header + data_buffer_offset))

        # Finalize buffers
        size_of_data = len(data_buffer)
        self.CollQuadsData = header_buffer + data_buffer
        self.CollQuadsDataSize = size_of_header + size_of_data

        print(f"Collision quads created: Header = {len(header_buffer)} bytes, Data = {size_of_data} bytes")

    def DoExportToXbox(self, bCopyOnly : bool, bTangents : bool):
        print("Create Quads")
        self.ResortToQuadrants()
        print("Optimize for cache")
        #self.VertexCacheOptimize(True)
        print("Resort Vertices")
        self.ResortVertices()
        #self.ReCreateFaceNormals()
        print("Collisionquads")
        self.CreateCollisionQuads() # TODO
        
        print("Saving...")
