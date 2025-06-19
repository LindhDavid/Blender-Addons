bl_info = {
    "name": "Foliage Baker",
    "version": (0,1),
    "blender": (2,91,2),
    "category": "Object",
    "location":"Where",
    "description":"what is this"
}

from typing import DefaultDict
import bpy

from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        FloatVectorProperty,
        IntProperty,
        PointerProperty,
        StringProperty,
        )

from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator

###########################################
###         Scene Properties            ###
###########################################

class FOL_scene_variables(bpy.types.PropertyGroup):
    display_channel: FloatProperty(
        default=2
    )
    output_folder: StringProperty(
        name="Folder", 
        subtype='DIR_PATH', 
        default='//'
    )
    output_name: StringProperty(
        name="Name",
        default="output"
    )
    enable_normal: BoolProperty(
        name="Enable",
        default=True
    )
    enable_properties: BoolProperty(
        name="Enable",
        default=True
    )
    enable_properties_2: BoolProperty(
        name="Enable",
        default=False
    )
    enable_albedo: BoolProperty(
        name="Enable",
        default=True
    )
    profile_albedo: EnumProperty(
        name="Profile",
        items=(
            ('Standard', "Standard", ""),
            ('AgX', "AgX",""),
            ('Filmic', "Filmic",""),
            ('Raw', "Raw","")
        ),
        description="Color Managment of albedo texture",
        default='Standard'
    )
    suffix_albedo: StringProperty(
        name="Suffix",
        default="albedo"
    )
    suffix_normal: StringProperty(
        name="Suffix",
        default="normal"
    )
    suffix_properties: StringProperty(
        name="Suffix",
        default="properties"
    )
    suffix_properties_2: StringProperty(
        name="Suffix",
        default="properties_2"
    )
    profile_normal: EnumProperty(
        name="Profile",
        items=(
            ('Standard', "Standard", ""),
            ('AgX', "AgX",""),
            ('Filmic', "Filmic",""),
            ('Raw', "Raw","")
        ),
        description="Color Managment of albedo texture",
        default='Raw'
    )
    profile_properties: EnumProperty(
        name="Profile",
        items=(
            ('Standard', "Standard", ""),
            ('AgX', "AgX",""),
            ('Filmic', "Filmic",""),
            ('Raw', "Raw","")
        ),
        description="Color Managment of albedo texture",
        default='Raw'
    )
    profile_properties_2: EnumProperty(
        name="Profile",
        items=(
            ('Standard', "Standard", ""),
            ('AgX', "AgX",""),
            ('Filmic', "Filmic",""),
            ('Raw', "Raw","")
        ),
        description="Color Managment of albedo texture",
        default='Raw'
    )
    camera_priority: EnumProperty(
        name="Priority",
        items=(
            ('texel', "Texel Dencity", ""),
            ('scale', "Camera Scale",""),
        ),
        description="Color Managment of albedo texture",
        default='texel'
    )
    camera_texel: FloatProperty(
        name = 'Texel Density',
        default = 8
    )
    camera_dimension: FloatProperty(
        name = 'Camera Dimension',
        default = 2,
        subtype='DISTANCE'
    )

    inpaint_distance: IntProperty(
        name='Inpaint',
        default = 2048,
    )
    erode_distance: IntProperty(
        name='Erode Alpha',
        default = -1,
    )

###########################################
###         Material Properties         ###
###########################################

class FOL_material_variables(bpy.types.PropertyGroup):

    def properties_types(self, context):
        return (
            ('ao', "Ambient Occlusion",""),
            ('backface', "Backface mask", ""),
            ('random', "Random Grayscale",""),
            ('roughness', "Roughness",""),
            ('height', "Height",""),
            ('v_color_red', "Vertex Color Red",""),
            ('v_color_green', "Vertex Color Green",""),
            ('v_color_blue', "Vertex Color Blue",""),
            #('mask', "Mask for Alpha",""),
            ('disable', "Disable",""),
        )
    
    mask_mode: EnumProperty(
        name="Mode",
        items=(
            ('opaque', "Opaque", ""),
            ('clip', "Alpha Clip","")
        ),
        default='opaque'
    )

    albedo_enable: BoolProperty(
        name='Create',
        default=True
    )
    albedo_alpha: BoolProperty(
        name="Use Albedo Alpha as Mask",
        default=True
    )
    albedo_mode: EnumProperty(
        name="Mode",
        items=(
            ('vertex', "Vertex Color", ""),
            ('texture', "Texture",""),
            ('solid', "Solid Color","")
        ),
        description="Type of albedo to bake",
        default='solid'
    )

    roughness_mode: EnumProperty(
        name="Mode",
        items=(
            ('vertex', "Vertex Color", ""),
            ('texture', "Texture",""),
            ('solid', "Value","")
        ),
        description="Type of albedo to bake",
        default='solid'
    )

    normal_enable: BoolProperty(
        name='Create',
        default=True
    )
    normal_mode: EnumProperty(
        name="Mode",
        items=(
            ('object', "Object Normal", ""),
            ('texture', "Texture","")
        ),
        description="Type of albedo to bake",
        default='object'
    )
    normal_type: EnumProperty(
        name="Input",
        items=(
            ('dx11', "Direct X", ""),
            ('opengl', "Open GL","")
        ),
        description="Type of albedo to bake",
        default='opengl'
    )
    normal_type_out: EnumProperty(
        name="Output",
        items=(
            ('dx11', "Direct X", ""),
            ('opengl', "Open GL","")
        ),
        default='opengl'
    )
    
    properties_1_enable: BoolProperty(
        name='Create',
        default=True
    )
    properties_1_1: EnumProperty(
        name="Red",
        items=properties_types,
        description="Type of properties to bake in red channel",
    )
    properties_1_2: EnumProperty(
        name="Green",
        items=properties_types,
        description="Type of properties to bake in green channel",

    )
    properties_1_3: EnumProperty(
        name="Blue",
        items=properties_types,
        description="Type of properties to bake in blue channel",
    )

    properties_2_enable: BoolProperty(
        name='Create',
        default=False
    )
    properties_2_1: EnumProperty(
        name="Red",
        items=properties_types,
        description="Type of properties channel to bake",
    )
    properties_2_2: EnumProperty(
        name="Green",
        items=properties_types,
        description="Type of properties channel to bake",
    )

    properties_2_3: EnumProperty(
        name="Blue",
        items=properties_types,
        description="Type of properties channel to bake",
    )



###########################################
###         Render out textures         ###
###########################################

class FOL_OT_render_channels(bpy.types.Operator):
    bl_idname = "fol.render_channels"
    bl_label = "Render all textures"

    def execute(self, context):
        scene = context.scene
        sfb = scene.foliagebaker
        fp = scene.render.filepath # get existing output path
        wm = bpy.context.window_manager
        wm.progress_begin(0, 4)
        #scene.view_settings.view_transform = 'Standard'
        # Render Albedo
        if sfb.enable_albedo:
            scene.render.filepath = fp + sfb.output_name + "_" + sfb.suffix_albedo
            bpy.ops.fol.display_channel(value_to_set=1.0)
            bpy.context.scene.view_settings.view_transform = sfb.profile_albedo
            bpy.ops.render.render(write_still=True)
            wm.progress_update(1)

        # Render Normal
        if sfb.enable_normal:
            scene.render.filepath = fp + sfb.output_name + "_" + sfb.suffix_normal
            bpy.ops.fol.display_channel(value_to_set=0.8)
            bpy.context.scene.view_settings.view_transform = sfb.profile_normal
            bpy.ops.render.render(write_still=True)
            wm.progress_update(2)

        # Render properties
        if sfb.enable_properties:
            scene.render.filepath = fp + sfb.output_name + "_" + sfb.suffix_properties
            bpy.ops.fol.display_channel(value_to_set=0.6)
            bpy.context.scene.view_settings.view_transform = sfb.profile_properties
            bpy.ops.render.render(write_still=True)
            wm.progress_update(3)

        # Render properties 2
        if sfb.enable_properties_2:
            scene.render.filepath = fp + sfb.output_name + "_" + sfb.suffix_properties_2
            bpy.ops.fol.display_channel(value_to_set=0.7)
            bpy.context.scene.view_settings.view_transform = sfb.profile_properties_2
            bpy.ops.render.render(write_still=True)
            wm.progress_update(4)

        wm.progress_end()

        scene.render.filepath = fp
        return {'FINISHED'}
    def invoke(self,context,event):
        return context.window_manager.invoke_props_dialog(self)
    def draw(self, context):
        scene = context.scene
        sfb = scene.foliagebaker
        layout = self.layout
        col = layout.column(align = True)
        col.label(text = "This will overide if exists:")
        if sfb.enable_albedo:
            col.label(text = sfb.output_name + "_" + sfb.suffix_albedo)
        if sfb.enable_normal:
            col.label(text = sfb.output_name + "_" + sfb.suffix_normal)
        if sfb.enable_properties:
            col.label(text = sfb.output_name + "_" + sfb.suffix_properties)
        if sfb.enable_properties_2:
            col.label(text = sfb.output_name + "_" + sfb.suffix_properties_2)
        col = layout.column(align = True)
        path = bpy.path.abspath(scene.render.filepath)
        col.label(text = "In folder: " + path[-30:])


###########################################
###     Display texture in viewport     ###
###########################################

class FOL_OT_display_channel(bpy.types.Operator):
    bl_idname = "fol.display_channel"
    bl_label = "Display Channel"

    value_to_set: bpy.props.FloatProperty(
        name="Value to Set"
    )
    def list_materials(self, context):
        node_list = []
        for ob in bpy.data.objects:
            if ob.type == "MESH":
                for mat_slot in ob.material_slots:
                    if mat_slot.material:
                        if mat_slot.material.node_tree:
                            node_list.extend([x for x in mat_slot.material.node_tree.nodes if x.label=='MATERIAL_SELECTOR'])
        return node_list


    def execute(self, context):
        scene = context.scene
        sfb = scene.foliagebaker
        for i in self.list_materials(context):
            i.outputs[0].default_value = self.value_to_set

        sfb.display_channel = self.value_to_set
        #scene.view_settings.view_transform = 'Standard'
        scene.display_settings.display_device = 'sRGB'
        
        if round(self.value_to_set,2) == 1.0:
            #scene.display_settings.display_device = sfb.profile_albedo
            scene.view_settings.view_transform = sfb.profile_albedo
        elif round(self.value_to_set,2) == 0.8:
            #scene.display_settings.display_device = sfb.profile_normal
            scene.view_settings.view_transform = sfb.profile_normal
        elif round(self.value_to_set,2) == 0.6:
            #scene.display_settings.display_device = sfb.profile_properties
            scene.view_settings.view_transform = sfb.profile_properties
        elif round(self.value_to_set,2) == 0.7:
            #scene.display_settings.display_device = sfb.profile_properties_2
            scene.view_settings.view_transform = sfb.profile_properties_2
        elif round(self.value_to_set,2) == 1.1:
            #scene.display_settings.display_device = 'sRGB'
            scene.view_settings.view_transform = 'Standard'

        #bpy.context.space_data.shading.type = 'MATERIAL'

        return {'FINISHED'}



class FOL_OT_create_camera(bpy.types.Operator):
    
    bl_idname = "fol.create_camera"
    bl_label = "Setup Scene for baking"
    
    def execute(self, context):
        scene = context.scene
        rd = scene.render
        sfb = scene.foliagebaker

        camera_data = any
        camera_object = any

        for o in bpy.context.scene.objects:
            if "Bake_Camera" in o.name:
                for collection in list(o.users_collection):
                    collection.objects.unlink(o)
                if o.users == 0:
                    bpy.data.objects.remove(o)
                del o
        
        camera_data = bpy.data.cameras.new(name='Bake_Camera')
        camera_object = bpy.data.objects.new('Bake_Camera', camera_data)

        camera_data.type = 'ORTHO'
        camera_data.display_size = 0.01

        if sfb.camera_priority == 'scale':
            scale = sfb.camera_dimension
        else:
            if rd.resolution_x > rd.resolution_y:
                scale = (rd.resolution_x/100) / sfb.camera_texel
            else:
                scale = (rd.resolution_y/100) / sfb.camera_texel

        camera_data.ortho_scale = scale
        camera_object.location = (0,0,scale)

        bpy.context.scene.collection.objects.link(camera_object)

        scene.camera = camera_object


        # Create inpaint
        compositor = bpy.context.scene
        # DELETE ALL EXISTING NODES
        for x in compositor.node_tree.nodes:
            compositor.node_tree.nodes.remove( x )
        compositor.use_nodes = True

        layers = compositor.node_tree.nodes.new("CompositorNodeRLayers")
        reroute = compositor.node_tree.nodes.new("NodeReroute")
        reroute.location = (300,-250)
        reroute2 = compositor.node_tree.nodes.new("NodeReroute")
        reroute2.location = (800,-250)
        dilate = compositor.node_tree.nodes.new("CompositorNodeDilateErode")
        dilate.location = (300,-80)
        dilate.distance = sfb.erode_distance
        alpha = compositor.node_tree.nodes.new("CompositorNodeSetAlpha")
        alpha.location = (500,20)
        inpaint = compositor.node_tree.nodes.new("CompositorNodeInpaint")
        inpaint.distance = sfb.inpaint_distance
        inpaint.location = (700,20)
        out = compositor.node_tree.nodes.new("CompositorNodeComposite")
        out.location = (900,0)

        link = compositor.node_tree.links.new

        link(layers.outputs[0],alpha.inputs[0])
        link(layers.outputs[1],dilate.inputs[0])
        link(dilate.outputs[0],alpha.inputs[1])
        link(alpha.outputs[0],inpaint.inputs[0])
        link(inpaint.outputs[0],out.inputs[0])
        link(layers.outputs[1],reroute.inputs[0])
        link(reroute.outputs[0],reroute2.inputs[0])
        link(reroute2.outputs[0],out.inputs[1])


        return {'FINISHED'}


class FOL_OT_create_material(bpy.types.Operator):
    bl_idname = "fol.create_material"
    bl_label = "This will overide current material"

    input_nodes = []
    def checkIfExist(self, name, mat):
        for x in mat.node_tree.nodes:
                if x.label == 'Roughness':
                    return [True, x]
        return [False,any]
    def createBackface(self, mat):
        out = mat.node_tree.nodes.new(type="ShaderNodeNewGeometry")
        outlink = out.outputs[6]
        return [out, outlink]
    def createRandom(self, mat):
        out = mat.node_tree.nodes.new(type="ShaderNodeObjectInfo")
        outlink = out.outputs[4]
        return [out, outlink]
    def createAO(self, mat):
        out = mat.node_tree.nodes.new(type="ShaderNodeAmbientOcclusion")
        outlink = out.outputs[1]
        return [out, outlink]
    def createDepth(self, context, mat, pos):
        scene = context.scene
        sfb = scene.foliagebaker

        link = mat.node_tree.links.new
        geo = mat.node_tree.nodes.new(type="ShaderNodeNewGeometry")
        geo.location = (pos[0]-400, pos[1])
        sep = mat.node_tree.nodes.new(type="ShaderNodeSeparateRGB")
        sep.location = (pos[0]-200, pos[1])
        out = mat.node_tree.nodes.new(type="ShaderNodeMath")
        out.operation = 'DIVIDE'
        out.inputs[1].default_value = sfb.camera_dimension

        link(geo.outputs[0],sep.inputs[0])
        link(sep.outputs[2],out.inputs[0])

        outlink = out.outputs[0]
        return [out, outlink] 
    
    def createRoughness(self, context, mat):
        material = context.material
        fb = material.foliagebaker
        
        if fb.roughness_mode == 'texture':
            out = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
            outlink = out.outputs[0]
        elif fb.roughness_mode == 'vertex':
            out = mat.node_tree.nodes.new(type="ShaderNodeVertexColor")
            outlink = out.outputs[1]
        else:
            out = mat.node_tree.nodes.new(type="ShaderNodeValue")
            outlink = out.outputs[0]
        out.label = 'Roughness'
        self.input_nodes.append(out)
        return [out, outlink] 
    def createFresnel(self, mat):
        out = mat.node_tree.nodes.new(type="ShaderNodeFresnel")
        outlink = out.outputs[0]
        return [out, outlink]
    def createVertexColor(self, mat, pos, color):
        vertex = mat.node_tree.nodes.new(type="ShaderNodeVertexColor")
        vertex.location = (pos[0]-200, pos[1])
        out = mat.node_tree.nodes.new(type="ShaderNodeSeparateRGB")
        mat.node_tree.links.new(vertex.outputs[0], out.inputs[0])
        if color == 'red':
            outlink = out.outputs[0]
        if color == 'green':
            outlink = out.outputs[1]
        if color == 'blue':
            outlink = out.outputs[2]
        return [out,outlink]
    def createMask(self, mat):
        out = mat.node_tree.nodes.new(type="ShaderNodeValue")
        #out.inputs[0].default_value = 1.0
        outlink = out.outputs[0]
        return [out,outlink]

    def createPropertiesChannel(self, context, mat, channel, pos):
        if channel == 'backface':
            out, outlink = self.createBackface(mat)
        elif channel == 'random':
            out, outlink = self.createRandom(mat)
        elif channel == 'ao':
            out, outlink = self.createAO(mat)
        elif channel == 'roughness':
            out, outlink = self.createRoughness(context, mat)
        elif channel == 'height':
            out, outlink = self.createDepth(context, mat, pos)
        elif channel == 'fresnel':
            out, outlink = self.createFresnel(mat)
        elif channel == 'v_color_red':
            out, outlink = self.createVertexColor(mat, pos, 'red')
        elif channel == 'v_color_green':
            out, outlink = self.createVertexColor(mat,pos, 'green')
        elif channel == 'v_color_blue':
            out, outlink = self.createVertexColor(mat, pos, 'blue')
        elif channel == 'mask':
            out, outlink = self.createMask(mat)
        else:
            return (False, False)

        out.location = pos
        return [out, outlink]
    def execute(self, context):
        material = context.material
        fb = material.foliagebaker

        scene = context.scene
        sfb = scene.foliagebaker

        mat = bpy.context.active_object.active_material
        mat.use_nodes = True

        gridSize = -200
        self.input_nodes.clear() 

        if fb.mask_mode =='clip':
            mat.blend_method = 'CLIP'
        else:
            mat.blend_method = 'OPAQUE'

        # DELETE ALL EXISTING NODES
        for x in mat.node_tree.nodes:
            mat.node_tree.nodes.remove( x )

        output_node = mat.node_tree.nodes.new("ShaderNodeOutputMaterial")
        output_node.location = (-gridSize,0)
        
        emission_node = mat.node_tree.nodes.new(type="ShaderNodeEmission")
        emission_node.location = (gridSize*2, gridSize*1)
        transparent_node = mat.node_tree.nodes.new(type="ShaderNodeBsdfTransparent")
        transparent_node.location = (gridSize*1,gridSize/2)
        mix_node = mat.node_tree.nodes.new(type="ShaderNodeMixShader")
        mix_node.location = (0,0)
        mix_node.inputs[0].default_value = 1
        mix_node_material = mat.node_tree.nodes.new(type="ShaderNodeMixShader")
        mix_node_material.location = (gridSize*1,gridSize)
        BSDF = mat.node_tree.nodes.new(type="ShaderNodeBsdfPrincipled")
        BSDF.location = (gridSize*2-100, gridSize*2)

        link = mat.node_tree.links.new
        link(emission_node.outputs[0], mix_node_material.inputs[1])
        link(BSDF.outputs[0], mix_node_material.inputs[2])
        link(transparent_node.outputs[0], mix_node.inputs[1])
        link(mix_node_material.outputs[0], mix_node.inputs[2])
        link(mix_node.outputs[0], output_node.inputs[0])


        ###         Create material selector

    
       
        select_nodes_location_x = gridSize*3
        select_nodes_location_y = 0
        value_node = mat.node_tree.nodes.new(type="ShaderNodeValue")
        value_node.location = (select_nodes_location_x + gridSize * 7,1*gridSize)
        value_node.label = "MATERIAL_SELECTOR"
        value_node.outputs[0].default_value = sfb.display_channel
        self.input_nodes.append(value_node)

        reroute = mat.node_tree.nodes.new(type="NodeReroute")
        reroute.location = (select_nodes_location_x + gridSize * 6,1*gridSize-40)

        link(value_node.outputs[0], reroute.inputs[0])
        

        # MATERIAL PREVIEW
        math = mat.node_tree.nodes.new(type="ShaderNodeMath")
        math.operation = 'DIVIDE' 
        math.inputs[1].default_value = 1.1
        math.location = (gridSize*3 + select_nodes_location_x,-gridSize)
        clamp = mat.node_tree.nodes.new(type="ShaderNodeClamp")
        clamp.location = (gridSize*2 + select_nodes_location_x,-gridSize)
        link(math.outputs[0],clamp.inputs[0])
        floor = mat.node_tree.nodes.new(type="ShaderNodeMath")
        floor.operation = 'FLOOR' 
        floor.location = (gridSize + select_nodes_location_x,-gridSize)
        link(clamp.outputs[0],floor.inputs[0])
        link(reroute.outputs[0], math.inputs[0])
        link(floor.outputs[0], mix_node_material.inputs[0])
        

        select_nodes = []
        for i in range(3):
            row = []

            
            row.append(mat.node_tree.nodes.new(type="ShaderNodeMath"))
            row[0].operation = 'DIVIDE' 
            row[0].inputs[1].default_value = 1 - (0.1 * i + 0.1)
            row[0].location = (i * gridSize + select_nodes_location_x + gridSize * 3,i*gridSize)

            link(reroute.outputs[0], row[0].inputs[0])

            row.append(mat.node_tree.nodes.new(type="ShaderNodeClamp"))
            row[1].location = (i * gridSize + select_nodes_location_x + gridSize * 2 ,i*gridSize)

            row.append(mat.node_tree.nodes.new(type="ShaderNodeMath"))
            row[2].operation = 'FLOOR' 
            row[2].location = (i * gridSize + select_nodes_location_x + gridSize * 1 ,i*gridSize)

            row.append(mat.node_tree.nodes.new(type="ShaderNodeMixRGB"))
            row[3].location = (i * gridSize + select_nodes_location_x ,i*gridSize)

            link(row[0].outputs[0], row[1].inputs[0])
            link(row[1].outputs[0], row[2].inputs[0])
            link(row[2].outputs[0], row[3].inputs[0])

            select_nodes.append(row)

            if i != 0:
                link(row[3].outputs[0], select_nodes[i-1][3].inputs[1])

        link(select_nodes[0][3].outputs[0], emission_node.inputs[0])

        
        if fb.mask_mode =='clip':
            if not fb.albedo_alpha or not fb.albedo_mode == 'texture':
                mask_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                mask_node.location = (-2500,200)
                mask_node.label = 'Mask'
                self.input_nodes.append(mask_node)
                link(mask_node.outputs[0],mix_node.inputs[0])
            
        ###         Setup Inputs and textures
        if sfb.enable_albedo:
            albedo_node = None
            if fb.albedo_mode == 'texture':
                albedo_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                if fb.albedo_alpha and fb.mask_mode =='clip':
                    link(albedo_node.outputs[1],mix_node.inputs[0])
            elif fb.albedo_mode == 'vertex':
                albedo_node = mat.node_tree.nodes.new(type="ShaderNodeVertexColor")
            else:
                albedo_node = mat.node_tree.nodes.new(type="ShaderNodeRGB")
            albedo_node.label = 'Albedo'
            self.input_nodes.append(albedo_node)
            albedo_node.location = (-2500,0)
            
            link(albedo_node.outputs[0],select_nodes[0][3].inputs[2])
            link(albedo_node.outputs[0],BSDF.inputs[0])
        
        ######      NORMAL      ######
        if sfb.enable_normal:
            normal_pos_x = gridSize*7
            normal_pos_y = gridSize*4
                        
            vec_transform_node = mat.node_tree.nodes.new(type="ShaderNodeVectorTransform")
            vec_transform_node.convert_to = 'CAMERA'
            vec_transform_node.location = (normal_pos_x+gridSize*4, normal_pos_y)
            sep_rgb_node = mat.node_tree.nodes.new(type="ShaderNodeSeparateRGB")
            sep_rgb_node.location = (normal_pos_x+gridSize*3, normal_pos_y)
            com_rgb_node = mat.node_tree.nodes.new(type="ShaderNodeCombineRGB")
            com_rgb_node.location = (normal_pos_x, normal_pos_y)
            normal_node = mat.node_tree.nodes.new(type="ShaderNodeNormalMap")
            normal_node.location = (normal_pos_x+gridSize*5, normal_pos_y)
            link(normal_node.outputs[0], vec_transform_node.inputs[0])

            if fb.normal_mode == 'texture':
                normal_texture = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                normal_texture.location = (normal_pos_x+gridSize*7, normal_pos_y)
                normal_texture.label = 'Normal Map'
                self.input_nodes.append(normal_texture)


                mix = mat.node_tree.nodes.new(type="ShaderNodeMixRGB")
                mix.location = (normal_pos_x+gridSize*6,normal_pos_y)
                geo = mat.node_tree.nodes.new(type="ShaderNodeNewGeometry")
                geo.location = (normal_pos_x+gridSize*7, normal_pos_y-gridSize-50)
                sep = mat.node_tree.nodes.new(type="ShaderNodeSeparateRGB")
                sep.location = (normal_pos_x+gridSize*9, normal_pos_y)
                com = mat.node_tree.nodes.new(type="ShaderNodeCombineRGB")
                com.location = (normal_pos_x+gridSize*7, normal_pos_y)
                com.label = 'Frontfacing'
                comInv = mat.node_tree.nodes.new(type="ShaderNodeCombineRGB")
                comInv.location = (normal_pos_x+gridSize*7, normal_pos_y+gridSize)
                comInv.label = 'Backfacing'
                mathR = mat.node_tree.nodes.new(type="ShaderNodeMath")
                mathR.location = (normal_pos_x+gridSize*8, normal_pos_y)
                mathR.operation = 'SUBTRACT' 
                mathR.inputs[0].default_value = 1
                mathG = mat.node_tree.nodes.new(type="ShaderNodeMath")
                mathG.location = (normal_pos_x+gridSize*8, normal_pos_y+gridSize)
                mathG.operation = 'SUBTRACT' 
                mathG.inputs[0].default_value = 1

                link(sep.outputs[2], com.inputs[2])
                link(sep.outputs[0], mathR.inputs[1])
                link(sep.outputs[1], mathG.inputs[1])
                link(sep.outputs[2], comInv.inputs[2])
                link(mathR.outputs[0], comInv.inputs[0])
                link(sep.outputs[0], com.inputs[0])

                if fb.normal_type == 'opengl':
                    link(mathG.outputs[0], comInv.inputs[1])
                    link(sep.outputs[1], com.inputs[1])
                else:
                    link(mathG.outputs[0], com.inputs[1])
                    link(sep.outputs[1], comInv.inputs[1])



                link(geo.outputs[6],mix.inputs[0])
                link(comInv.outputs[0],mix.inputs[2])
                link(com.outputs[0],mix.inputs[1])
                link(normal_texture.outputs[0],sep.inputs[0])
                link(mix.outputs[0],normal_node.inputs[1])
                link(normal_node.outputs[0],BSDF.inputs[20])

            normal_nodes = []
            for i in range(3):
                row = []

                row.append(mat.node_tree.nodes.new(type="ShaderNodeMath"))
                row[0].operation = 'MULTIPLY' 
                row[0].location = (normal_pos_x+gridSize*2, i * gridSize + normal_pos_y)
                

                link(sep_rgb_node.outputs[i], row[0].inputs[0])

                row.append(mat.node_tree.nodes.new(type="ShaderNodeMath"))
                row[1].operation = 'ADD' 
                row[1].location = (normal_pos_x+gridSize, i * gridSize + normal_pos_y)
                link(row[0].outputs[0], row[1].inputs[0])

                link(row[1].outputs[0], com_rgb_node.inputs[i])
                normal_nodes.append(row)
            normal_nodes[2][0].inputs[1].default_value = -0.5
            if fb.normal_type_out == 'dx11':
                normal_nodes[1][0].inputs[1].default_value = -0.5
            
            link(vec_transform_node.outputs[0], sep_rgb_node.inputs[0])
            link(com_rgb_node.outputs[0], select_nodes[1][3].inputs[2])
            

            


        ######      properties 1      ######
        if fb.properties_1_enable:
            com_rgb_node = mat.node_tree.nodes.new(type="ShaderNodeCombineRGB")
            com_rgb_node.location = (gridSize*7, gridSize*9)

            red, redlink = self.createPropertiesChannel(context, mat, fb.properties_1_1, (gridSize*8, gridSize*8))
            green, greenlink = self.createPropertiesChannel(context, mat, fb.properties_1_2, (gridSize*8, gridSize*9))   
            blue, bluelink = self.createPropertiesChannel(context, mat, fb.properties_1_3, (gridSize*8, gridSize*10))
            
            if red:
                link(redlink, com_rgb_node.inputs[0])
                if red.label == 'Roughness':
                    link(redlink, BSDF.inputs[7])
            if green:
                link(greenlink, com_rgb_node.inputs[1])
                if green.label == 'Roughness':
                    link(greenlink, BSDF.inputs[7])
            if blue:
                link(bluelink, com_rgb_node.inputs[2])
                if blue.label == 'Roughness':
                    link(bluelink, BSDF.inputs[7])

            link(com_rgb_node.outputs[0], select_nodes[-1][3].inputs[1])


        ######      properties 2      ######
        if fb.properties_2_enable:
            com_rgb_node = mat.node_tree.nodes.new(type="ShaderNodeCombineRGB")
            com_rgb_node.location = (gridSize*7, gridSize*11)

            red, redlink = self.createPropertiesChannel(context, mat, fb.properties_2_1, (gridSize*8, gridSize*11))
            green, greenlink = self.createPropertiesChannel(context, mat, fb.properties_2_2, (gridSize*8, gridSize*12))   
            blue, bluelink = self.createPropertiesChannel(context, mat, fb.properties_2_3, (gridSize*8, gridSize*13))
            
            if red:
                link(redlink, com_rgb_node.inputs[0])
                if red.label == 'Roughness':
                    link(redlink, BSDF.inputs[7])
            if green:
                link(greenlink, com_rgb_node.inputs[1])
                if green.label == 'Roughness':
                    link(greenlink, BSDF.inputs[7])
            if blue:
                link(bluelink, com_rgb_node.inputs[2])
                if blue.label == 'Roughness':
                    link(bluelink, BSDF.inputs[7])
            
            link(com_rgb_node.outputs[0], select_nodes[-1][3].inputs[2])

        frame = mat.node_tree.nodes.new(type='NodeFrame')
        frame.label = 'Inputs'
        frame.label_size = 64
        frame.use_custom_color = True
        frame.color = (0.432242, 1.000000, 0.789715)
        i = 0
        for node in self.input_nodes:
            node.location = (gridSize*18, gridSize*i*1.2)
            node.parent = frame
            i = i + 1
        
        return {'FINISHED'}
    def invoke(self,context,event):
        return context.window_manager.invoke_confirm(self, event)


##############################################
###      DRAW GUI for material editor      ###
##############################################

class NODE_EDITOR_PT_foliage_baker(bpy.types.Panel):
    """Creates a Panel in the 3D viewport"""
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Foliage Baker"
    bl_label = "Materials"

    @classmethod
    def poll(self, context):
        return context.area.ui_type == "ShaderNodeTree"   

    def draw(self, context):
        layout = self.layout
        material = context.material
        scene = context.scene
        sfb = scene.foliagebaker
        try:
            fb = material.foliagebaker
            
            create = layout.column()
            create.operator_context = 'INVOKE_DEFAULT'
            create.operator("fol.create_material", text="Update Material")

            layout.separator()

            box = layout.box()
            box.label(text="Alpha")
            box.prop(fb, "mask_mode")

            
            box = layout.box()
            title = box.row()
            title.label(text="Albedo")
            title.prop(fb, 'albedo_enable')
            if fb.albedo_enable:
                box.prop(fb, "albedo_mode")
                if fb.albedo_mode == 'texture' and fb.mask_mode == 'clip':
                    box.prop(fb,"albedo_alpha")
                
          
            
            box = layout.box()
            title = box.row()
            title.label(text="Normal")
            title.prop(fb, 'normal_enable')    
            if fb.normal_enable:
                box.prop(fb, "normal_mode")
                box.label(text='Normal Type:')
                if fb.normal_mode == 'texture':
                    box.prop(fb,'normal_type')
                box.prop(fb,'normal_type_out')
                    
                


            box = layout.box()
            title = box.row()
            title.label(text="Properties 1")   
            title.prop(fb, 'properties_1_enable')     
            if fb.properties_1_enable:
                box.prop(fb, "properties_1_1")
                box.prop(fb, "properties_1_2")
                box.prop(fb, "properties_1_3")
            

            box = layout.box()
            title = box.row()
            title.label(text="Properties 2")   
            title.prop(fb, 'properties_2_enable')     
            if fb.properties_2_enable:    
                box.prop(fb, "properties_2_1")
                box.prop(fb, "properties_2_2")
                box.prop(fb, "properties_2_3")

            
            if fb.properties_1_1 == "roughness" and sfb.enable_properties or fb.properties_1_2 == "roughness" and sfb.enable_properties or fb.properties_1_3 == "roughness" and sfb.enable_properties or fb.properties_2_1 == "roughness" and sfb.enable_properties_2 or fb.properties_2_2 == "roughness" and sfb.enable_properties_2 or fb.properties_2_3 == "roughness" and sfb.enable_properties_2 :
                box = layout.box()
                box.label(text="Roughness")
                box.prop(fb, "roughness_mode")
                
        except:
            pass

##############################################
###         DRAW GUI for 3D View           ###
##############################################

class VIEW3D_PT_foliage_baker(bpy.types.Panel):
    """Creates a Panel in the 3D viewport"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Foliage Baker"
    bl_label = "Settings"
    
    def list_materials(self, context):
        mat_list_per_object = []
        for ob in context.scene.objects:
            if ob.type in ("MESH", "CURVE", "SURFACE", "FONT", "GPENCIL"):
                if ob.data.materials:
                    mat_list_per_object.append(ob.data.materials.items())
        # Flatten the list and return a set (unique)
        return set([i[0] for i in sum(mat_list_per_object, [])])

    def draw(self, context):


        layout = self.layout
        
        scene = context.scene
        sfb = scene.foliagebaker

        rd = scene.render
        
        box = layout.box()
        box.prop(rd, "filepath")
        box.prop(sfb, "output_name")

        box = layout.box()
        box.label(text='Render Settings')
        box.prop(rd, "filter_size")
        box.prop(scene.eevee, "taa_render_samples")
        box.prop(rd, "film_transparent", text="Transparent")
        box.prop(scene.eevee, "use_gtao")

        box = layout.box()
        row = box.row()
        row.label(text='Albedo')
        row.prop(sfb,"enable_albedo")
        if sfb.enable_albedo:
            box.prop(sfb, "profile_albedo")
            box.prop(sfb, "suffix_albedo")

        box = layout.box()
        row = box.row()
        row.label(text='Normal')
        row.prop(sfb,"enable_normal")
        if sfb.enable_normal:
            box.prop(sfb, "profile_normal")
            box.prop(sfb, "suffix_normal")
            

        box = layout.box()
        row = box.row()
        row.label(text='Properties Map 1')
        row.prop(sfb,"enable_properties")
        if sfb.enable_properties:
            box.prop(sfb, "profile_properties")
            box.prop(sfb, "suffix_properties")
        
        box = layout.box()
        row = box.row()
        row.label(text='Properties Map 2')
        row.prop(sfb,"enable_properties_2")
        if sfb.enable_properties_2:
            box.prop(sfb, "profile_properties_2")
            box.prop(sfb, "suffix_properties_2")

        

        

##############################################
###     DRAW GUI for 3D View Camera        ###
##############################################

class VIEW3D_PT_foliage_baker_camera(bpy.types.Panel):
    """Creates a Panel in the 3D viewport"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Foliage Baker"
    bl_label = "Camera"

    def draw(self, context):
        layout = self.layout
        
        scene = context.scene
        sfb = scene.foliagebaker
        rd = scene.render
        
        cam_create = layout.column()
        cam_create.scale_y = 2
        cam_create.operator('fol.create_camera', text='Uppdate Camera')


        col = layout.column(align=True)
        col.prop(rd, "resolution_x", text="Resolution X")
        col.prop(rd, "resolution_y", text="Resolution Y")
        col.prop(rd, "resolution_percentage", text="Scale")

        box = layout.box()
        box.prop(sfb,'camera_priority')
        if sfb.camera_priority == 'scale':
            box.prop(sfb, "camera_dimension")
            if rd.resolution_x > rd.resolution_y:
                texel = (rd.resolution_x/100) / sfb.camera_dimension
            else:
                texel = (rd.resolution_y/100) / sfb.camera_dimension
            box.label(text = 'Texel Density: {}'.format(round(texel,2)))
        else:
            box.prop(sfb, "camera_texel")
            if rd.resolution_x > rd.resolution_y:
                scale = (rd.resolution_x/100) / sfb.camera_texel
            else:
                scale = (rd.resolution_y/100) / sfb.camera_texel
            box.label(text = 'Camera Scale: {}m'.format(round(scale,2)))

        box = layout.box()
        col = box.column(align=True)
        col.label(text='Dilate output')
        col.prop(sfb, "inpaint_distance")
        col.prop(sfb, "erode_distance")

##############################################
###     DRAW GUI for 3D View Preview        ###
##############################################

class VIEW3D_PT_foliage_baker_preview(bpy.types.Panel):
    """Creates a Panel in the 3D viewport"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Foliage Baker"
    bl_label = "Preview"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        sfb = scene.foliagebaker
        render_layout = layout.column()
        render_layout.scale_y =2 
        render_layout.operator_context = 'INVOKE_DEFAULT'
        render_layout.operator('fol.render_channels')
        grid = layout.grid_flow(columns=2)
        grid.prop(sfb,"enable_albedo", text="Albedo")
        grid.prop(sfb,"enable_normal", text="Normal")
        grid.prop(sfb,"enable_properties", text="Properties 1")
        grid.prop(sfb,"enable_properties_2", text="Properties 2")
        layout.separator()
        col = layout.column(align=True)
        channel = round(sfb.display_channel,2)
        disp_val = col.operator("fol.display_channel", text ='Preview BSDF', depress = channel==1.1)
        disp_val.value_to_set = 1.1
        if sfb.enable_albedo:
            disp_val = col.operator("fol.display_channel", text ='Preview Albedo', depress = channel==1.0)
            disp_val.value_to_set = 1.0
        if sfb.enable_normal:
            disp_val = col.operator("fol.display_channel", text ='Preview Normal', depress = channel==0.8)
            disp_val.value_to_set = 0.8
        if sfb.enable_properties:
            disp_val = col.operator("fol.display_channel", text ='Preview Properties 1', depress = channel==0.6)
            disp_val.value_to_set = 0.6
        if sfb.enable_properties_2:
            disp_val = col.operator("fol.display_channel", text ='Preview Properties 2', depress = channel==0.7)
            disp_val.value_to_set = 0.7
      

classes = [
    FOL_material_variables,
    FOL_scene_variables,
    VIEW3D_PT_foliage_baker_preview,
    VIEW3D_PT_foliage_baker, 
    VIEW3D_PT_foliage_baker_camera,
    NODE_EDITOR_PT_foliage_baker,
    FOL_OT_create_material,
    FOL_OT_display_channel,
    FOL_OT_create_camera,
    FOL_OT_render_channels,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.foliagebaker = PointerProperty(type = FOL_scene_variables)
    bpy.types.Material.foliagebaker = PointerProperty(type = FOL_material_variables)
   

   

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.foliagebaker
    del bpy.types.Material.foliagebaker
    #33870