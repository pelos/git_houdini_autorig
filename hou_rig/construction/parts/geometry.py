#todo put a subdivision node somewhere
#promote a folder for the geometry and the subdivide
#the geometry that is been brought to geo node should be lock

import hou
import master
import hou_rig.utils

class geometry(master.master):
    def __init__(self, node, rig_subnet):
        print "geo"
        self.node = node
        self.rig_subnet = rig_subnet

        self.limb_subnet = self.create_rig_node(self.rig_subnet)
        self.limb_subnet.setName(self.node.name())

        self.populate_geo(self.limb_subnet)
        self.position_node(self.node, self.limb_subnet)

        #self.create_spare_parms_folder()

    def populate_geo_back_up(self, parent_node):
        return
        geo = parent_node.createNode("geo", "geo_"+self.node.name())
        file_node = geo.node("file1")

        if self.node.parm("import_geometry").eval() == "geometry/the_autorig/will/use.bgeo":
            path_script = hou_rig.utils.__file__
            path_script = path_script.split("\\")[0:-2]
            path_script = "\\".join(path_script)
            path_script = path_script + "\\extras\\toon_character.bgeo"
            geometry_file = path_script

        else:
            geometry_file = self.node.parm("import_geometry").eval()

        file_node.parm("file").set(geometry_file)

        group_name = "right_side_group"
        mirror_group_name = "mirror_group"
        prim_grp = geo.createNode("group", "right_side_group")
        prim_grp.parm("crname").set(group_name)
        prim_grp.parm("entity").set(0)
        prim_grp.parm("filter").setExpression("$TX < 0")
        prim_grp.setNextInput(file_node)

        mirror_grp = geo.createNode("group", "mirror_group")
        mirror_grp.parm("cnvfromtype").set(0)
        mirror_grp.parm("cnvtotype").set(1)
        mirror_grp.parm("convertg").set(group_name)
        mirror_grp.parm("cnvtname").set(mirror_group_name)
        mirror_grp.setNextInput(prim_grp)

        #HERE SHOULD BE A LIST OF THE DEFORMERS CREATED BY OTHER CLASSES
        #here should be the list of deformers for the extra regions
        list_of_deformers = "../../deformers_list_goes_here"

        capture = geo.createNode("capture", "capture_bones")
        capture.parm("extraregions").set(list_of_deformers)
        capture.parm("usecaptpose").set(1)
        capture.setNextInput(mirror_grp)

        capture_prox = geo.createNode("captureproximity", "captureproximity_bones")
        capture_prox.parm("extraregions").set(list_of_deformers)
        capture_prox.setNextInput(mirror_grp)

        switch_captures = geo.createNode("switch", "switch_capture_type")
        switch_captures.setNextInput(capture)
        switch_captures.setNextInput(capture_prox)

        viz = geo.createNode("visibility", "visibility_hide_right_side")
        viz.parm("group").set(group_name)
        viz.setNextInput(switch_captures)

        paint_cap = geo.createNode("capturelayerpaint", "capturelayerpaint_weights")
        paint_cap.setNextInput(viz)

        pre_deform = geo.createNode("deform", "pre_deform")
        pre_deform.setNextInput(paint_cap)

        mirror_w = geo.createNode("capturemirror", "mirror_capture_weights")
        mirror_w.parm("group").set(mirror_group_name)
        mirror_w.parm("from").set("left_bones/cregion 0")
        mirror_w.parm("to").set("right_bones/cregion 0")
        mirror_w.setNextInput(paint_cap)

        null_lock = geo.createNode("null", "null_Lock")
        null_lock.setNextInput(mirror_w)

        subnet_blend = geo.createNode("subnet", "subnet_blendshapes")
        subnet_blend.setNextInput(null_lock)
        subnet_blend.bypass(1)

        null_import_blends = subnet_blend.createNode("null", "import_Blend_shapes_objs_from_a_folder")
        hou_parm_template = hou.ButtonParmTemplate("import_blendshapes", "Import Blend Shapes")
        hou_parm_template.setScriptCallback('import hou_rig.construction.parts.geometry; hou_rig.construction.parts.geometry.run_import_morphs()')
        hou_parm_template.setScriptCallbackLanguage(hou.scriptLanguage.Python)

        hou_rig.utils.parm_to_ui(null_import_blends, hou_parm_template, insert_before_parm=[0, ])

        null_import_blends_tg = null_import_blends.parmTemplateGroup()
        copy_parm_template = null_import_blends_tg.find("copyinput")
        null_import_blends_tg.hide(copy_parm_template, True)
        cacheinput_parm_template = null_import_blends_tg.find("cacheinput")
        null_import_blends_tg.hide(cacheinput_parm_template, True)
        null_import_blends.setParmTemplateGroup(null_import_blends_tg)

        null_import_blends.setNextInput(subnet_blend.indirectInputs()[0])

        blend = subnet_blend.createNode("blendshapes", "blendshapes_from_houdini")
        blend.parm("blend1").set(1)
        button_promote_parms_to_ui(blend)

        blend.setNextInput(null_import_blends)

        subnet_out = subnet_blend.createNode("null", "Out")
        subnet_out.setNextInput(blend)
        subnet_out.setDisplayFlag(1)
        subnet_out.setRenderFlag(1)

        subnet_blend.layoutChildren()

        deform = geo.createNode("deform", "deform")
        deform.setNextInput(subnet_blend)

        del_groups = geo.createNode("group", "delete_deform_groups")
        del_groups.parm("crname").set("delete_deform_groups")
        del_groups.parm("destroyname").set(group_name+" "+mirror_group_name+" 3d_hidden_primitives	2d_visible_primitives")
        del_groups.setNextInput(deform)

        corrective_subnet = geo.createNode("subnet", "subnet_corrective_deformations")
        corrective_subnet.setNextInput(del_groups)

        sticky = corrective_subnet.createStickyNote("sticky1")
        sticky.setText("here should be all the corrections, this subnet should be an editable node in the OTL")

        null_out = geo.createNode("null", "OUT")
        null_out.setNextInput(corrective_subnet)
        null_out.setDisplayFlag(1)
        null_out.setRenderFlag(1)

        #rop_out = geo.createNode("rop_geometry", "rop_out_skin")
        #rop_out.setNextInput(null_out)

        geo.layoutChildren()





    def populate_geo(self, parent_node, do_muscle=True):
        #promote a folder for the geometry and the subdivide
        #the geometry that is been brought to geo node should be lock
        #togle to turn on and off visibility of the geometry
        #promte rendering settings
        #todo color the node of the node that are related to bones
        #bone_color = hou.Color([0.4, 1.0, 1.0])
        muscle_color = hou.Color([0.667, 0.0, 0.0])



        geo = parent_node.createNode("geo", "geo_"+self.node.name())
        file_node = geo.node("file1")

        if self.node.parm("import_geometry").eval() == "geometry/the_autorig/will/use.bgeo":
            path_script = hou_rig.utils.__file__
            path_script = path_script.split("\\")[0:-2]
            path_script = "\\".join(path_script)
            path_script = path_script + "\\extras\\toon_character.bgeo"
            geometry_file = path_script

        else:
            geometry_file = self.node.parm("import_geometry").eval()

        file_node.parm("file").set(geometry_file)

        group_name = "right_side_group"
        mirror_group_name = "mirror_group"
        prim_grp = geo.createNode("group", "right_side_group")
        prim_grp.parm("crname").set(group_name)
        prim_grp.parm("entity").set(0)
        prim_grp.parm("groupop").set(2)
        prim_grp.parm("filter").setExpression("$TX < 0")
        prim_grp.setNextInput(file_node)

        mirror_grp = geo.createNode("group", "mirror_group")
        mirror_grp.parm("cnvfromtype").set(0)
        mirror_grp.parm("cnvtotype").set(1)
        mirror_grp.parm("convertg").set(group_name)
        mirror_grp.parm("cnvtname").set(mirror_group_name)
        mirror_grp.setNextInput(prim_grp)

        #HERE SHOULD BE A LIST OF THE DEFORMERS CREATED BY OTHER CLASSES
        #here should be the list of deformers for the extra regions
        list_of_deformers = "../../deformers_list_goes_here"

        capture = geo.createNode("capture", "capture_bones")
        capture.parm("extraregions").set(list_of_deformers)
        capture.parm("usecaptpose").set(1)
        capture.setNextInput(mirror_grp)

        capture_prox = geo.createNode("captureproximity", "captureproximity_bones")
        capture_prox.parm("extraregions").set(list_of_deformers)
        capture_prox.setNextInput(mirror_grp)

        switch_captures = geo.createNode("switch", "switch_capture_type")
        switch_captures.setNextInput(capture)
        switch_captures.setNextInput(capture_prox)

        viz = geo.createNode("visibility", "visibility_hide_right_side")
        viz.parm("group").set(group_name)
        viz.setNextInput(switch_captures)

        cap_paint_weight_bone_node = geo.createNode("capturelayerpaint", "capturelayerpaint_weights_bones")
        cap_paint_weight_bone_node.setNextInput(viz)

        # pre_deform = geo.createNode("deform", "pre_deform")
        # pre_deform.setNextInput(cap_paint_weight_bone_node)

        if do_muscle is True:
            capture_meta_node = geo.createNode("capturemeta", "capture_muscles")
            #here goes the list of muscles from the global variables
            #make sure we make the string with relative paths.
            capture_meta_node.parm("captobjects").set("")
            capture_meta_node.parm("captframe").setExpression("$F")
            capture_meta_node.parm("destroyweights").set(0)
            capture_meta_node.parm("visualize").set(1)
            capture_meta_node.setInput(0, cap_paint_weight_bone_node)
            capture_meta_node.setColor(muscle_color)

            cap_paint_weight_muscle_node = geo.createNode("capturelayerpaint", "capturelayerpaint_weights_muscles")
            cap_paint_weight_muscle_node.parm("capturetype").set(1)
            # here goes the list of muscles from the global variables.
            cap_paint_weight_muscle_node.parm("cregion").set("")
            cap_paint_weight_muscle_node.setInput(0, capture_meta_node)
            cap_paint_weight_muscle_node.setColor(muscle_color)

            slide_mode_inflation_node = geo.createNode("slidemodifierpaint", "slidemodifierpaint_inflate_muscle")
            slide_mode_inflation_node.parm("paintattrib").set(1)
            slide_mode_inflation_node.setInput(0, cap_paint_weight_muscle_node)
            slide_mode_inflation_node.setColor(muscle_color)

            slide_mode_slide_node = geo.createNode("slidemodifierpaint", "slidemodifierpaint_slide_muscle")
            slide_mode_slide_node.parm("paintattrib").set(0)
            slide_mode_slide_node.setInput(0, slide_mode_inflation_node)
            slide_mode_slide_node.setColor(muscle_color)

            attrib_mirror_node = geo.createNode("attribmirror", "attribmirror_inflate_slide_muscle")
            attrib_mirror_node.parm("grouptype").set(1)
            #attrib_mirror_node.parm("group").set("mirror_group")
            #attrib_mirror_node.parm("usegroupas").set(0)
            attrib_mirror_node.parm("attribname").set("inflatemodifier slideModifier")
            attrib_mirror_node.setInput(0, slide_mode_slide_node)
            attrib_mirror_node.setColor(muscle_color)

        mirror_w = geo.createNode("capturemirror", "mirror_capture_weights")
        mirror_w.parm("group").set(mirror_group_name)
        mirror_w.parm("from").set("left_bones/cregion 0")
        mirror_w.parm("to").set("right_bones/cregion 0")
        if do_muscle is True:
            mirror_w.setNextInput(attrib_mirror_node)
        else:
            mirror_w.setNextInput(cap_paint_weight_bone_node)

        null_lock = geo.createNode("null", "null_Lock")
        null_lock.setNextInput(mirror_w)

        subnet_blend = geo.createNode("subnet", "subnet_blendshapes")
        subnet_blend.setNextInput(null_lock)
        subnet_blend.bypass(1)

        null_import_blends = subnet_blend.createNode("null", "import_Blend_shapes_objs_from_a_folder")
        hou_parm_template = hou.ButtonParmTemplate("import_blendshapes", "Import Blend Shapes")
        hou_parm_template.setScriptCallback('import hou_rig.construction.parts.geometry; hou_rig.construction.parts.geometry.run_import_morphs()')
        hou_parm_template.setScriptCallbackLanguage(hou.scriptLanguage.Python)

        hou_rig.utils.parm_to_ui(null_import_blends, hou_parm_template, insert_before_parm=[0, ])

        null_import_blends_tg = null_import_blends.parmTemplateGroup()
        copy_parm_template = null_import_blends_tg.find("copyinput")
        null_import_blends_tg.hide(copy_parm_template, True)
        cacheinput_parm_template = null_import_blends_tg.find("cacheinput")
        null_import_blends_tg.hide(cacheinput_parm_template, True)
        null_import_blends.setParmTemplateGroup(null_import_blends_tg)

        null_import_blends.setNextInput(subnet_blend.indirectInputs()[0])

        blend = subnet_blend.createNode("blendshapes", "blendshapes_from_houdini")
        blend.parm("blend1").set(1)
        button_promote_parms_to_ui(blend)

        blend.setNextInput(null_import_blends)

        subnet_out = subnet_blend.createNode("null", "Out")
        subnet_out.setNextInput(blend)
        subnet_out.setDisplayFlag(1)
        subnet_out.setRenderFlag(1)

        subnet_blend.layoutChildren()

        deform_node = geo.createNode("deform", "deform")
        deform_node.setNextInput(subnet_blend)

        if do_muscle is True:
            deform_muscle_node = geo.createNode("deformmuscle", "deform_muscle")
            deform_muscle_node.setInput(0, deform_node)
            deform_muscle_node.parm("doinflate").set(1)
            deform_muscle_node.parm("pointstoinflate").set(1)
            #here should be the list of the deformers from the global variables
            #deform_muscle_node.parm("musclestoinflate").set("")
            deform_muscle_node.parm("doslide").set(1)
            deform_muscle_node.parm("slide").set(1)
            deform_muscle_node.setColor(muscle_color)

        del_groups = geo.createNode("group", "delete_deform_groups")
        del_groups.parm("crname").set("delete_deform_groups")
        #del_groups.parm("destroyname").set(group_name+" "+mirror_group_name+" 3d_hidden_primitives 2d_visible_primitives")

        if do_muscle is True:
            del_groups.setNextInput(deform_muscle_node)
        else:
            del_groups.setNextInput(deform_node)

        corrective_subnet = geo.createNode("subnet", "subnet_corrective_deformations")
        corrective_subnet.setNextInput(del_groups)

        sticky = corrective_subnet.createStickyNote("sticky1")
        sticky.setText("here should be all the corrections, this subnet should be an editable node in the OTL")

        null_out = geo.createNode("null", "OUT")
        null_out.setNextInput(corrective_subnet)
        null_out.setDisplayFlag(1)
        null_out.setRenderFlag(1)

        #rop_out = geo.createNode("rop_geometry", "rop_out_skin")
        #rop_out.setNextInput(null_out)

        geo.layoutChildren()


def button_promote_parms_to_ui(node_to_put_the_button):
    hou_parm_template = hou.ButtonParmTemplate("promote_blendshapes", "Promote Blend Shapes")
    hou_parm_template.setScriptCallback('import hou_rig.construction.parts.geometry; hou_rig.construction.parts.geometry.promote_blendshapes_to_ui();')
    hou_parm_template.setScriptCallbackLanguage(hou.scriptLanguage.Python)
    hou_rig.utils.parm_to_ui(node_to_put_the_button, hou_parm_template, insert_before_parm=[0, ])


def promote_blendshapes_to_ui():
    """
    this function is call by the button in the blend node,
    this will promote the blend shapes to the upper level
    """
    main_otl = hou.pwd().parent().parent().parent().parent()
    hou_rig.utils.ui_folder(main_otl, ["Rig Parms", hou.pwd().parent().parent().name(), hou.pwd().name()])
    hou.pwd().parm("updatechannels").pressButton()

    for i in hou.pwd().parms():
        try:
            if i.name().startswith("blend") and "0" not in i.name():
                hou_rig.utils.promote_parm_to_ui(i, main_otl, ["Rig Parms", hou.pwd().parent().parent().name(),	hou.pwd().name()], parm_name=i.alias())
        except:
            continue
    hou.pwd().parent().bypass(0)

def run_import_morphs():
    """
    creates a folder in the UI subnet
    """
    import_morphs(hou.ui.selectFile(title="Select the folder", file_type=hou.fileType.Directory), hou.pwd().parent(),
                hou.pwd(), out_connection=hou.pwd().parent().node("blendshapes_from_houdini"))


def import_morphs(a_path, a_node, connection, out_connection=None):
    """
    a_path = its a folder path where the .objs exists
    a_node = a node where the blendshape nodes and the files will be created
    a_node_to_connect = is the node that the blends will connect to
    out_connection = if this variable is given the blendshapes node will connect to this
    """

    import os
    categories = []
    b_master_exist = False
    list_of_files = os.listdir(a_path)
    if a_node.node("blendshapes_master"):
        b_master = a_node.node("blendshapes_master")
        b_master_exist = True
    else:
        b_master = a_node.createNode("blendshapes", "blendshapes_master")
        b_master.setColor(hou.Color((0.35, 0.55, 0.65)))
        b_master.setInput(0, connection)

    if os.path.isdir(a_path):
        for i in list_of_files:
            if i.endswith(".obj"):
                categories.append(i.split("_")[0])

    categories_list = list(set(categories))
    for z in categories_list:
        if a_node.node("blend_"+z):
            blend_cat = a_node.node("blend_"+z)
        else:
            blend_cat = a_node.createNode("blendshapes", "blend_"+z)
            button_promote_parms_to_ui(blend_cat)
            blend_cat.setColor(hou.Color((0.25, 0.35, 0.45)))
            blend_cat.setNextInput(connection)

        for index,  j in enumerate(list_of_files):
            if a_node.node(j.split(".")[0]):
                pass
            else:
                if j.startswith(z):
                    file_cat = a_node.createNode("file", j.split(".")[0])
                    blend_cat.setNextInput(file_cat)
                    file_cat.parm("file").set(a_path+"/"+j)
                    file_cat.cook(force=True)
                    file_cat.setHardLocked(1)

                blend_cat.parm("updatechannels").pressButton()
                if b_master_exist == False:
                    b_master.setNextInput(blend_cat)
                elif b_master_exist == True:
                    pass

    if out_connection is not None:
        if b_master_exist == False:
            out_connection.setNextInput(b_master)
        elif b_master_exist == True:
            pass

    b_master.parm("updatechannels").pressButton()
    for w in b_master.parms():
        if w.name().startswith("blend"):
            w.set(1)
    a_node.layoutChildren()
    a_node.bypass(0)




def button_promote_parms_to_ui(node_to_put_the_button):
    hou_parm_template = hou.ButtonParmTemplate("promote_blendshapes", "Promote Blend Shapes")
    hou_parm_template.setScriptCallback('import hou_rig.construction.parts.geometry; hou_rig.construction.parts.geometry.promote_blendshapes_to_ui();')
    hou_parm_template.setScriptCallbackLanguage(hou.scriptLanguage.Python)
    hou_rig.utils.parm_to_ui(node_to_put_the_button, hou_parm_template, insert_before_parm=[0, ])


def promote_blendshapes_to_ui():
    """
    this function is call by the button in the blend node,
    this will promote the blend shapes to the upper level
    """
    main_otl = hou.pwd().parent().parent().parent().parent()
    hou_rig.utils.ui_folder(main_otl, ["Rig Parms", hou.pwd().parent().parent().name(), hou.pwd().name()])
    hou.pwd().parm("updatechannels").pressButton()

    for i in hou.pwd().parms():
        try:
            if i.name().startswith("blend") and "0" not in i.name():
                hou_rig.utils.promote_parm_to_ui(i, main_otl, ["Rig Parms", hou.pwd().parent().parent().name(),	hou.pwd().name()], parm_name=i.alias())
        except:
            continue
    hou.pwd().parent().bypass(0)

def run_import_morphs():
    """
    creates a folder in the UI subnet
    """
    import_morphs(hou.ui.selectFile(title="Select the folder", file_type=hou.fileType.Directory), hou.pwd().parent(),
                hou.pwd(), out_connection=hou.pwd().parent().node("blendshapes_from_houdini"))


def import_morphs(a_path, a_node, connection, out_connection=None):
    """
    a_path = its a folder path where the .objs exists
    a_node = a node where the blendshape nodes and the files will be created
    a_node_to_connect = is the node that the blends will connect to
    out_connection = if this variable is given the blendshapes node will connect to this
    """

    import os
    categories = []
    b_master_exist = False
    list_of_files = os.listdir(a_path)
    if a_node.node("blendshapes_master"):
        b_master = a_node.node("blendshapes_master")
        b_master_exist = True
    else:
        b_master = a_node.createNode("blendshapes", "blendshapes_master")
        b_master.setColor(hou.Color((0.35, 0.55, 0.65)))
        b_master.setInput(0, connection)

    if os.path.isdir(a_path):
        for i in list_of_files:
            if i.endswith(".obj"):
                categories.append(i.split("_")[0])

    categories_list = list(set(categories))
    for z in categories_list:
        if a_node.node("blend_"+z):
            blend_cat = a_node.node("blend_"+z)
        else:
            blend_cat = a_node.createNode("blendshapes", "blend_"+z)
            button_promote_parms_to_ui(blend_cat)
            blend_cat.setColor(hou.Color((0.25, 0.35, 0.45)))
            blend_cat.setNextInput(connection)

        for index,  j in enumerate(list_of_files):
            if a_node.node(j.split(".")[0]):
                pass
            else:
                if j.startswith(z):
                    file_cat = a_node.createNode("file", j.split(".")[0])
                    blend_cat.setNextInput(file_cat)
                    file_cat.parm("file").set(a_path+"/"+j)
                    file_cat.cook(force=True)
                    file_cat.setHardLocked(1)

                blend_cat.parm("updatechannels").pressButton()
                if b_master_exist == False:
                    b_master.setNextInput(blend_cat)
                elif b_master_exist == True:
                    pass

    if out_connection is not None:
        if b_master_exist == False:
            out_connection.setNextInput(b_master)
        elif b_master_exist == True:
            pass

    b_master.parm("updatechannels").pressButton()
    for w in b_master.parms():
        if w.name().startswith("blend"):
            w.set(1)
    a_node.layoutChildren()
    a_node.bypass(0)