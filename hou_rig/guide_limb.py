#todo make a nice arrow pointing the direction and maybe orientation? of the my_null
#todo: my_null use null  instead geo and start from scratch

#todo: MOVE THE CHARACTER PLACER function inside the class, consistency
#todo make sure the character placer is the first one, looks like now is using creation order instead list order.
#todo toon_curve should lock divisions parm

#todo the bone_shape add a color, user can set the wire frame color before running the auto rig
#todo if the hook is not pick still drop the pre rig node just give a warning and don't fill the hook parms.


import hou
import hou_rig.line_maker
import hou_rig.my_null
import hou_rig.utils


""" in houdini
from hou_rig import guide_limb
guide_limb.character_placer()
"""
def character_placer():
    subnet = hou.node("/obj").createNode("subnet", "character_placer")
    subnet.setColor(hou.Color((.3, .3, .3)))
    #subnet.setSelectableInViewport(0)
    tg = subnet.parmTemplateGroup()
    folder = hou.FolderParmTemplate("folder", "Rig Parms")
    name_parm = hou.StringParmTemplate("name", "Name", 1, help="character rig to build", default_value=["Bided", ])

    c_center = hou.FloatParmTemplate("color_center", "Color Center", 3, default_value=([.75, .75, .75]), min=0, max=1,
                                     min_is_strict=False, max_is_strict=False, look=hou.parmLook.ColorSquare,
                                     naming_scheme=hou.parmNamingScheme.RGBA)

    c_right = hou.FloatParmTemplate("color_right", "Color Right", 3, default_value=([0, 0, 1]), min=0, max=1,
                                    min_is_strict=False, max_is_strict=False, look=hou.parmLook.ColorSquare,
                                    naming_scheme=hou.parmNamingScheme.RGBA)

    c_left = hou.FloatParmTemplate("color_left", "Color Left", 3, default_value=([1, 0, 0]), min=0, max=1,
                                   min_is_strict=False, max_is_strict=False, look=hou.parmLook.ColorSquare,
                                   naming_scheme=hou.parmNamingScheme.RGBA)
    rig_type = hou.StringParmTemplate("type", "type", 1, default_value=["character_placer"])

    hou_parm_template2 = hou.StringParmTemplate("position", "Position", 1, default_value=(["center"]),
                                                naming_scheme=hou.parmNamingScheme.Base1,
                                                string_type=hou.stringParmType.Regular,
                                                menu_items=([""]),
                                                menu_labels=([""]),
                                                icon_names=([]),
                                                item_generator_script="",
                                                item_generator_script_language=hou.scriptLanguage.Python,
                                                menu_type=hou.menuType.Normal)
    hou_parm_template2.hide(1)

    folder.addParmTemplate(name_parm)
    folder.addParmTemplate(c_center)
    folder.addParmTemplate(c_right)
    folder.addParmTemplate(c_left)
    folder.addParmTemplate(rig_type)
    folder.addParmTemplate(hou_parm_template2)

    tg.insertBefore((0,), folder)
    subnet.setParmTemplateGroup(tg)
    subnet.parm("type").lock(1)

    #ch_placer = subnet.createNode("null", "character_placer")
    #ch_placer.setDisplayFlag(0)
    #hook = subnet.createNode("null", "character_placer_hook")
    hook = subnet.createNode("null", "chain_1")
    #hook = subnet.createNode("null", "character_placer")
    #hook.setInput(0,ch_placer,0)
    hook.parm("controltype").set(1)
    hook.parm("orientation").set(2)
    #hook.setSelectableInViewport(0)

    subnet.layoutChildren()

"""
#in houdini shelf button put this code for each limb type
from hou_rig import guide_limb
if len(hou.selectedNodes()) == 0 or hou.selectedNodes()[0].type().nameComponents()[2 ]== "subnet":
    hou.ui.displayMessage("Make sure you are selecting a valid Hook")
else:
    limb = guide_limb.limb(hook = hou.selectedNodes()[0], limb_type = "single")
    limb.single()
"""


class limb():
    def __init__(self, hook="../find_hook", second_hook="../find_hook", limb_type="single"):
        """
        grab the information of the hook and the type from the shelf tool
        @param hook: whos the parent
        @param limb_type: what class to build
        @return: a subnet
        """
        self.limb_type = limb_type
        self.hook = hook
        self.second_hook = second_hook

        self.g_node = hou.node("/obj").createNode("subnet", "guide_" + self.limb_type)

    def put_ui_in_node(self, node_to_put_ui,
                    hook_script=False,
                    hook_upper=False,
                    hook_upper_script=False,
                    default_type="single",
                    kinematic_parm=True,
                    kinematics_labels = ["No Kinematics", "IK", "IK_With Effector"],
                    stretchy_parm=True,
                    ik_slide_parm =True,
                    curve_toon_parm=True,
                    division_parm=True,
                    division_default=8,
                    ik_goal_label_warning=True,
                    ik_goals_parm=True,
                    ik_twist_parm=True,
                    position_parm=True,
                    position_default="left"):
        """

        @param node_to_put_ui:
        @param default_type:
        @param kinematic_parm:
        @param kinematics_labels:
        @param stretchy_parm:
        @param ik_slide_parm:
        @param curve_toon_parm:
        @param division_parm:
        @param ik_goal_label_warning:
        @param ik_goals_parm:
        @param ik_twist_parm:
        @param position_parm:
        @return:
        """
        template_group = node_to_put_ui.parmTemplateGroup()

        # Code for parameter template Make  RIG_PARMS FOLDER
        hou_parm_template = hou.FolderParmTemplate("folder", "Rig Parms", folder_type=hou.folderType.Tabs, default_value=0, ends_tab_group=False)
        hou_parm_template.setTags({"visibletabs": "111"})

        # Code for parameter template HOOK
        hou_parm_template2 = hou.StringParmTemplate("hook", "Hook", 1, default_value=(["parent"]),
                                                    naming_scheme=hou.parmNamingScheme.Base1,
                                                    string_type=hou.stringParmType.NodeReference,
                                                    menu_items=([]),
                                                    menu_labels=([]),
                                                    icon_names=([]),
                                                    item_generator_script="",
                                                    item_generator_script_language=hou.scriptLanguage.Python,
                                                    menu_type=hou.menuType.Normal)
        if hook_script is not False:
            hou_parm_template2.setTags({"script_callback":hook_script, "script_callback_language":"python"})

        #hou_parm_template2.setTags({"oprelative": "."})
        hou_parm_template.addParmTemplate(hou_parm_template2)

        # if we need a second Hook such as Spine or muscle....
        #todo fix second hook that use this method.
        if hook_upper is True:
            hou_parm_template2 = hou.StringParmTemplate("hook_upper", "Hook Upper", 1, default_value=(["parent"]),
                                                        naming_scheme=hou.parmNamingScheme.Base1,
                                                        string_type=hou.stringParmType.NodeReference,
                                                        menu_items=([]),
                                                        menu_labels=([]),
                                                        icon_names=([]),
                                                        item_generator_script="",
                                                        item_generator_script_language=hou.scriptLanguage.Python,
                                                        menu_type=hou.menuType.Normal)
            if hook_upper_script is not False:
                hou_parm_template2.setTags({"script_callback":hook_script, "script_callback_language":"python"})

            hou_parm_template.addParmTemplate(hou_parm_template2)




























        # Code for parameter template TYPE OF CLASS!!!
        hou_parm_template2 = hou.StringParmTemplate("type", "type", 1, default_value=([default_type]),
                                                    naming_scheme=hou.parmNamingScheme.Base1,
                                                    string_type=hou.stringParmType.Regular,
                                                    menu_items=(["single","spine","leg","arm","foot","dog_leg",
                                                                 "null", "flexor", "muscle"]),
                                                    menu_labels=(["single","spine","leg","arm","foot","dog_leg",
                                                                  "null", "flexor", "muscle"]),
                                                    icon_names=([]), item_generator_script="",
                                                    item_generator_script_language=hou.scriptLanguage.Python,
                                                    menu_type=hou.menuType.Normal)
        hou_parm_template2.setJoinWithNext(1)
        hou_parm_template.addParmTemplate(hou_parm_template2)

        if position_parm is True:
            hou_parm_template2 = hou.StringParmTemplate("position", "Position", 1, default_value=([position_default]),
                                                       naming_scheme=hou.parmNamingScheme.Base1,
                                                       string_type=hou.stringParmType.Regular,
                                                       menu_items=(["left", "center", "right"]),
                                                       menu_labels=(["left", "center", "right"]),
                                                       icon_names=([]),
                                                       item_generator_script="",
                                                       item_generator_script_language=hou.scriptLanguage.Python,
                                                       menu_type=hou.menuType.Normal)
            hou_parm_template.addParmTemplate(hou_parm_template2)

        # Code for parameter template KINEMATIC TYPE
        if kinematic_parm is True:
            menu_items_names = range(0, len(kinematics_labels))
            menu_items_names = map(str, menu_items_names)
            hou_parm_template2 = hou.MenuParmTemplate("k_type", "Kinematic Type",
                                                      menu_items=menu_items_names,
                                                      menu_labels=kinematics_labels,
                                                      default_value=0, icon_names=([]), item_generator_script="",
                                                      item_generator_script_language=hou.scriptLanguage.Python,
                                                      menu_type=hou.menuType.Normal)

            hou_parm_template2.setJoinWithNext(True)
            hou_parm_template.addParmTemplate(hou_parm_template2)

        # Code for parameter template STRETCHY TOGGLE
        if stretchy_parm is True:
            hou_parm_template2 = hou.ToggleParmTemplate("stretchy", "stretchy", default_value=True)
            hou_parm_template2.setConditional( hou.parmCondType.DisableWhen, "{ k_type == 0 }")
            hou_parm_template2.setJoinWithNext(True)
            hou_parm_template.addParmTemplate(hou_parm_template2)

        # Code for parameter template IK SLIDE
        if ik_slide_parm is True:
            hou_parm_template2 = hou.ToggleParmTemplate("ik_slide", "IK_slide", default_value=True)
            hou_parm_template2.setConditional( hou.parmCondType.DisableWhen, "{ k_type == 0 }")
            hou_parm_template2.setJoinWithNext(True)
            hou_parm_template.addParmTemplate(hou_parm_template2)


        # Code for parameter template TOON CURVE to put a curve along that drive  a chain of bones
        if curve_toon_parm is True:
            hou_parm_template2 = hou.ToggleParmTemplate("toon_curve", "toon_curve", default_value=True)
            #hou_parm_template2.setConditional( hou.parmCondType.DisableWhen, "{ k_type == 0 }")
            hou_parm_template2.setJoinWithNext(True)
            hou_parm_template.addParmTemplate(hou_parm_template2)


        # Code for parameter template how many bones on the curve
        if division_parm is True:
            hou_parm_template2 = hou.IntParmTemplate("divisions", "Divisions", 1, default_value=([division_default]),
                                                     min=0, max=10,
                                                     min_is_strict=False, max_is_strict=False,
                                                     naming_scheme=hou.parmNamingScheme.Base1)
            hou_parm_template.addParmTemplate(hou_parm_template2)

        # Code for parameter template just a label warning the user to use relative paths.
        if ik_goal_label_warning is True:
            hou_parm_template2 = hou.LabelParmTemplate("ik_warning", "ik_warning",
                                                    column_labels=(["IK Constraints must be in relative path."]))
            hou_parm_template2.hideLabel(True)
            hou_parm_template.addParmTemplate(hou_parm_template2)

        # Code for parameter template  THE IK GOAL PARENTS BLENDS
        if ik_goals_parm is True:
            hou_parm_template2 = hou.FolderParmTemplate("ik_cons_folder", "Ik Constraint",
                                                        folder_type=hou.folderType.MultiparmBlock,
                                                        default_value=1,
                                                        ends_tab_group=False)

            # Code for parameter template  PARENT BLENDS

            hou_parm_template3 = hou.StringParmTemplate("ik_constraint#", "Ik Constraint", 1, default_value=(["../character_placer/chain_1"]), naming_scheme=hou.parmNamingScheme.Base1,
                                                        string_type=hou.stringParmType.NodeReference, menu_items=([]),
                                                        menu_labels=([]), icon_names=([]), item_generator_script="",
                                                        item_generator_script_language=hou.scriptLanguage.Python,
                                                        menu_type=hou.menuType.Normal)
            hou_parm_template3.setConditional( hou.parmCondType.DisableWhen, "{ k_type == 0 }")
            hou_parm_template3.setTags({"opfilter": "!!OBJ!!", "oprelative": "."})

            #hou_parm_template3 = hou.StringParmTemplate("ik_constraint#", "Ik Constraint", 1,
            #											default_value=(["root_chain"]),
            #											naming_scheme=hou.parmNamingScheme.Base1,
            #											string_type=hou.stringParmType.NodeReferenceList,
            #											menu_items=([]),
            #											menu_labels=([]),
            #											icon_names=([]), item_generator_script="",
            #											item_generator_script_language=hou.scriptLanguage.Python,
            #											menu_type=hou.menuType.Normal)
            #hou_parm_template3.setConditional( hou.parmCondType.DisableWhen, "{ k_type == 0 }")
            #hou_parm_template3.setTags({"opfilter": "!!OBJ!!", "oprelative": "/"})
            #hou_parm_template3.setTags({"oprelative": "/"})

            hou_parm_template2.addParmTemplate(hou_parm_template3)
            hou_parm_template.addParmTemplate(hou_parm_template2)

        if ik_twist_parm is True:
            hou_parm_template2 = hou.StringParmTemplate("ik_twist_parent", "Ik Twist Parent", 1,
                                                        default_value=([""]),
                                                        #default_value=(["`chsop('hook')`"]),
                                                        naming_scheme = hou.parmNamingScheme.Base1,
                                                        string_type = hou.stringParmType.NodeReference,
                                                        menu_type = hou.menuType.Normal)
            hou_parm_template2.setConditional(hou.parmCondType.HideWhen, "{ k_type != 2 }")
            hou_parm_template2.setTags({"oprelative": "."})
            hou_parm_template.addParmTemplate(hou_parm_template2)

        # Code for parameter template POSITION  RIGHT LEFT CENTER
        #Code SETTING DOWN THE PARMS in THE UI
        template_group.insertBefore((0,), hou_parm_template)
        node_to_put_ui.setParmTemplateGroup(template_group)
        try:
            node_to_put_ui.parm("ik_constraint1").lock(1)
        except:
            pass

    def null(self):
        """ IN HOUDINI
        from hou_rig import guide_limb
        if len(hou.selectedNodes()) == 0 or hou.selectedNodes()[0].type().nameComponents()[2 ]== "subnet":
            hou.ui.displayMessage("Make sure you are selecting a valid Hook")
        else:
            limb = guide_limb.limb(hook = hou.selectedNodes()[0], limb_type = "single")
            limb.single()
        """
        self.g_node.setPosition([self.hook.parent().position()[0], self.hook.parent().position()[1]-1])
        self.g_node.setColor(hou.Color((0.55, 0.15, 0.15)))
        self.put_ui_in_node(self.g_node, default_type="null",
                            kinematic_parm=True,
                            kinematics_labels=["No Kinematics", "Multi Parents"],
                            stretchy_parm=False,
                            ik_slide_parm =False,
                            curve_toon_parm=False,
                            division_parm=False,
                            ik_goals_parm=True,
                            position_parm=True)
        self.g_node.parm("ik_constraint1").lock(0)
        self.g_node.parm("ik_constraint1").set("")

        self.hooking_a_node(self.g_node, "hook",hook_to=self.hook, lock=1, selectableInViewport=0)
        #self.hooking_a_node(self.g_node)

        # creating the nulls
        attachment = hou_rig.my_null.my_null(self.g_node, "chain_1")
        attachment.node("xform").parm("sx").set(0.5)

        attachment.parm("geoscale").set(.08)
        #self.hooking(do_line=False)

        fetch_node = self.create_fetch_node(self.g_node)
        list_for_guide = [fetch_node, attachment]

        self.parent_a_chain(list_for_guide)
        #curve = hou_rig.line_maker.create_line(self.limb_type+"_guide_curve", list_for_guide)
        #curve = self.make_guide_curve(self.limb_type+"_guide_curve", list_for_guide)
        #curve.setSelectableInViewport(0)
        #curve.parm("straight_curve").set(0)
        self.g_node.layoutChildren()

    def single(self):
        self.g_node.setPosition([self.hook.parent().position()[0], self.hook.parent().position()[1]-1])
        self.g_node.setColor(hou.Color((0.55, 0.15, 0.15)))
        self.put_ui_in_node(self.g_node, default_type="single")

        self.hooking_a_node(self.g_node, "hook",hook_to=self.hook, lock=1, selectableInViewport=0)
        fetch_node = self.create_fetch_node(self.g_node)

        # creating the nulls
        attachment = hou_rig.my_null.my_null(self.g_node, "chain_1")
        tip = hou_rig.my_null.my_null(self.g_node, "chain_2")

        list_for_guide = [attachment, tip]
        for i in list_for_guide:
            if i == attachment:
                i.parm("geoscale").set(.08)
            else:
                i.parm("geoscale").set(.1)
            #i.parm("keeppos").set(1)
            i.setInput(0, fetch_node)
            i.node("xform").parm("sx").set(0.15)
            i.parm("lookatpath").set('../chain_`opdigits(".")+1`')
            i.parm("lookup").set("off")
            bone_subnet = self.subnet_shape(i, i.node("Out"))
            self.bone_shape(bone_subnet)

        #position of the next nulls in world space
        tip.parm("tx").set(attachment.parm("tx").eval())
        tip.parm("ty").set(attachment.parm("ty").eval() + 0.25)
        tip.parm("tz").set(attachment.parm("tz").eval())

        self.make_guide_curve(self.limb_type+"_guide_curve", list_for_guide)
        self.g_node.layoutChildren()



    def geometry(self):
        """
        in houdini:
        from hou_rig import guide_limb
        geo = guide_limb.limb(limb_type="geometry")
        geo.geometry()
        """
        hou_rig.utils.ui_folder(self.g_node, in_this_folder=["Rig Parms"], insert_before_parm=(0,))
        rig_type = hou.StringParmTemplate("type", "type", 1, default_value=["geometry"])
        hou_rig.utils.parm_to_ui(self.g_node, rig_type, in_this_folder=["Rig Parms"])
        self.g_node.parm("type").lock(1)

        geometry_parm = hou.StringParmTemplate("import_geometry", "Geometry", 1,
                                                    default_value=(["geometry/the_autorig/will/use.bgeo"]),
                                                    naming_scheme=hou.parmNamingScheme.Base1,
                                                    string_type=hou.stringParmType.FileReference,
                                                    menu_items=([]), menu_labels=([]), icon_names=([]),
                                                    item_generator_script="",
                                                    item_generator_script_language=hou.scriptLanguage.Python,
                                                    menu_type=hou.menuType.StringReplace)
        geometry_parm.setHelp(
            'this can be fill later on inside the rig,'
            'this is the geometry that the rig will try to bring to the autorig.')
        hou_rig.utils.parm_to_ui(self.g_node, geometry_parm, in_this_folder=["Rig Parms"])

        self.g_node.setColor(hou.Color((0.8, 0.6, 0.25)))

    def flexor(self):
        self.g_node.setColor(hou.Color((0.1, 0.55, 0.5)))
        print "flexor"
        self.put_ui_in_node(self.g_node,
                    default_type="flexor",
                    kinematic_parm=False,
                    kinematics_labels = ["No Kinematics", "IK", "IK_With Effector"],
                    stretchy_parm=False,
                    ik_slide_parm =False,
                    curve_toon_parm=True,
                    division_parm=True,
                    ik_goal_label_warning=True,
                    ik_goals_parm=True,
                    position_parm=True)

        self.hooking_a_node(self.g_node, hook_to=self.hook)
        fetch_node = self.create_fetch_node(self.g_node)

        attachment = self.g_node.createNode("pathcv", "chain_1")
        attachment.parm("rx").set(90)
        attachment.parm("scale").set(0)

        tip = self.g_node.createNode("pathcv", "chain_2")
        tip.parm("ty").set(1)
        tip.parm("rx").set(90)
        tip.parm("scale").set(0)

        # attachment = hou_rig.my_null.my_null(self.g_node, "chain_1")
        # attachment.node("xform").parm("sx").set(0.5)
        # tip = hou_rig.my_null.my_null(self.g_node, "chain_2")
        # tip.node("xform").parm("sx").set(0.5)

        list_for_guide = [attachment, tip]
        for i in list_for_guide:
            i.setInput(0, fetch_node)
        #list_for_guide = [fetch_node, attachment, tip]
        #self.parent_a_chain(list_for_guide)

        curve = hou_rig.line_maker.create_line(self.limb_type+"_guide_curve", list_for_guide)
        #curve = self.make_guide_curve(self.limb_type+"_guide_curve", list_for_guide)
        curve.setSelectableInViewport(0)
        curve.parm("straight_curve").set(0)
        self.g_node.layoutChildren()

    def spine(self):
        self.g_node.setPosition([self.hook.parent().position()[0], self.hook.parent().position()[1]-1])
        self.g_node.setColor(hou.Color((0.1, 0.25, 0.5)))
        self.put_ui_in_node(self.g_node, default_type="spine",
                            kinematic_parm=False,
                            ik_slide_parm=False,
                            curve_toon_parm=False,
                            ik_goal_label_warning=False,
                            ik_goals_parm=False,
                            ik_twist_parm=False,
                            position_default="center",
                            division_default=7)

        self.hooking_a_node(self.g_node, "hook", hook_to=self.hook, lock=1, selectableInViewport=0)

        hook_upper_template=hou.StringParmTemplate("hook_upper", "Hook Upper", 1, default_value=(["parent"]),
                                                    naming_scheme=hou.parmNamingScheme.Base1,
                                                    string_type=hou.stringParmType.NodeReference)

        hou_rig.utils.parm_to_ui(self.g_node, hook_upper_template, insert_after_parm="hook")

        #try to set this if we selected 2 nodes for the 2 hooks, excpet don't do anything
        try:
            self.hooking_a_node(self.g_node, "hook_upper", hook_to=self.second_hook, lock=1, selectableInViewport=0)
            we_selected_two_nodes = True
        except:
            pass


        fetch_node = self.create_fetch_node(self.g_node)
        attachment = hou_rig.my_null.my_null(self.g_node, "chain_1")
        attachment.setInput(0, fetch_node)

        second_fetch_node = self.create_fetch_node(self.g_node, parm_to_grab="hook_upper")
        tip = hou_rig.my_null.my_null(self.g_node, "chain_2")
        tip.setInput(0, second_fetch_node)

        list_for_guide = [attachment, tip]
        for i in list_for_guide:
            if i == attachment:
                i.parm("geoscale").set(.08)
                i.node("xform").parm("sx").set(0.5)
            else:
                i.parm("geoscale").set(.1)
                i.parm("keeppos").set(1)
                i.parm("controltype").set(1)

            #i.setInput(0, fetch_node)
            i.parm("lookatpath").set('../chain_`opdigits(".")+1`')
            i.parm("lookup").set("off")


        #position of the nulls in world space
        # if we_selected_two_nodes is not True:
        #     tip.parm("tx").set( attachment.parm("tx").eval() )
        #     tip.parm("ty").set( attachment.parm("ty").eval() + 0.25 )
        #     tip.parm("tz").set( attachment.parm("tz").eval() )

        self.make_guide_curve(self.limb_type+"_guide_curve", list_for_guide)

        self.subnet_shape(attachment, attachment.node("Out"))
        self.subnet_shape(tip, tip.node("Out"))
        self.g_node.layoutChildren()











        # if self.limb_type == "leg" or self.limb_type == "arm":
        #     print "creation"
        #     #creation of the nulls as point position for the bones
        #     attachment = hou_rig.my_null.my_null(self.g_node, "chain_1")
        #     bow = hou_rig.my_null.my_null(self.g_node, "chain_2")
        #     tip = hou_rig.my_null.my_null(self.g_node, "chain_3")
        #
        #     list_for_guide = [attachment, bow, tip]
        #
        #     #position of the nulls
        #     if self.limb_type == "leg":
        #         print "creation leg"
        #         self.put_ui_in_node(self.g_node, default_type="leg")
        #         self.g_node.setColor(hou.Color((.25,.25,.5)))
        #         bow.parm("tx").set( attachment.parm("tx").eval() )
        #         bow.parm("ty").set( attachment.parm("ty").eval() - 0.3 )
        #         bow.parm("tz").set( attachment.parm("tz").eval() + 0.15 )
        #
        #         tip.parm("tx").set( bow.parm("tx").eval() )
        #         tip.parm("ty").set( bow.parm("ty").eval() - 0 )
        #         tip.parm("tz").set( bow.parm("tz").eval() - 0.2 )
        #
        #     elif self.limb_type == "arm":
        #         print "creation arm"
        #         self.put_ui_in_node(self.g_node, default_type="arm")
        #         self.g_node.setColor(hou.Color((.5,.25,.25)))
        #         bow.parm("tx").set( attachment.parm("tx").eval() + 0.3)
        #         bow.parm("ty").set( attachment.parm("ty").eval()  )
        #         bow.parm("tz").set( attachment.parm("tz").eval() - 0.05)
        #
        #         tip.parm("tx").set( bow.parm("tx").eval() + 0)
        #         tip.parm("ty").set( bow.parm("ty").eval()  )
        #         tip.parm("tz").set( bow.parm("tz").eval() + 0.1)
        #
        #     for i in list_for_guide:
        #         if i == attachment:
        #             i.parm("geoscale").set(.05)
        #         else:
        #             #setting the size of the null view
        #             i.parm("geoscale").set(.1)
        #             #setting the shape of the null view
        #             #i.parm("controltype").set(1)
        #             #i.parm("keeppos").set(1)
        #
        # if self.limb_type == "foot":
        #     #the Foot method should check if the parent subnet and the hook to the multi IK list and set it up as
        #     # default
        #
        #
        #     self.g_node.setColor(hou.Color((0.5, 0.25, 0.85)))
        #     attachment = hou_rig.my_null.my_null(self.g_node, "attachment")
        #     bow = hou_rig.my_null.my_null(self.g_node, "bow")
        #     tip = hou_rig.my_null.my_null(self.g_node, "tip")
        #     toe = hou_rig.my_null.my_null(self.g_node, "toe")
        #     heel = hou_rig.my_null.my_null(self.g_node, "heel")
        #
        #     list_for_guide = [attachment, bow, tip, toe, heel]
        #
        #     for i in list_for_guide:
        #         if i == attachment:
        #             i.parm("geoscale").set(0.05)
        #         else:
        #         #setting the size of the null view
        #             i.parm("geoscale").set(0.1)
        #         #setting the shape of the null view
        #         #i.parm("controltype").set(1)
        #         #i.parm("keeppos").set(1)
        #
        #     bow.parm("tx").set( attachment.parm("tx").eval() )
        #     bow.parm("ty").set( attachment.parm("ty").eval() - 0.1 )
        #     bow.parm("tz").set( attachment.parm("tz").eval() + 0.1 )
        #
        #     tip.parm("tx").set( bow.parm("tx").eval() )
        #     tip.parm("ty").set( bow.parm("ty").eval() - 0.1 )
        #     tip.parm("tz").set( bow.parm("tz").eval() + 0.1 )
        #
        #     toe.parm("tx").set( tip.parm("tx").eval() )
        #     toe.parm("ty").set( tip.parm("ty").eval() - 0.05)
        #     toe.parm("tz").set( tip.parm("tz").eval() + 0.05 )
        #
        #     heel.parm("tx").set(tip.parm("tx").eval() )
        #     heel.parm("ty").set( 0 ) #tip.parm("ty").eval()  )
        #     heel.parm("tz").set( tip.parm("tz").eval() - 0.75 )

    def muscle(self):
        #todo make sure the center and center_offset always alaing (rotation) be the average of the origin
        #position and insertion position, this helps when scaling the muscle un even. and also in the animation
        #dont flip
        #todo remove the try, just DO IT.
        #todo remove the try's on the hooks now that's been handle in the shelf.

        """
        in houdini:
        from hou_rig import guide_limb
        selected_nodes = hou.selectedNodes()
        print  len(selected_nodes)

        if len(selected_nodes) == 2:
            limb = guide_limb.limb(hook = selected_nodes[0], second_hook =selected_nodes[1], limb_type = "muscle")
        elif len(selected_nodes) ==1:
            limb = guide_limb.limb(hook = selected_nodes[0], second_hook =selected_nodes[0], limb_type = "muscle")
        elif len(selected_nodes) == 0:
            limb = guide_limb.limb(limb_type = "muscle")

        elif len(selected_nodes) >2:
            hou.ui.displayMessage("you selected more items than needed, select 0 or 2")

        limb.muscle()
        """
        try:
            self.g_node.setPosition([self.hook.parent().position()[0], self.hook.parent().position()[1] - 1])
            self.g_node.setPosition([self.second_hook.parent().position()[0], self.second_hook.parent().position()[1] - 1])
        except:
            pass
        self.g_node.setColor(hou.Color((0.31, 0.55, 0.5)))
        self.put_ui_in_node(self.g_node, default_type="muscle",
                            kinematic_parm=False,
                            ik_slide_parm=False,
                            curve_toon_parm=False,
                            ik_goal_label_warning=False,
                            ik_goals_parm=False,
                            ik_twist_parm=False,
                            position_default="left",
                            division_default=7, stretchy_parm=False, division_parm=False,
                            hook_script='hou.pwd().parm("rest_muscle").pressButton()',
                            hook_upper=True,
                            hook_upper_script='hou.pwd().parm("rest_muscle").pressButton()')

        # when people click this button will capture the position of the origin and insertion nulls to the chop
        rest_muscle_button = hou.ButtonParmTemplate("rest_muscle", "Rest Muscle Position")
        rest_muscle_button.setScriptCallbackLanguage(hou.scriptLanguage.Python)
        # rest_muscle_button.setTags(
        #     {"script_callback": 'origin_rest_node = hou.pwd().node("chopnet_muscle").node("channel_origin_rest")\n'
        #                         'insertion_rest_node = hou.pwd().node("chopnet_muscle").node("channel_insertion_rest")\n'
        #
        #                         'obj_origin_node = hou.pwd().node("chopnet_muscle").node("object_origin")\n'
        #                         'obj_insertion_node = hou.pwd().node("chopnet_muscle").node("object_insertion")\n'
        #
        #                         'origin_rest_node.parm("value0x").set(obj_origin_node.track("tx").eval())\n'
        #                         'origin_rest_node.parm("value0y").set(obj_origin_node.track("ty").eval())\n'
        #                         'origin_rest_node.parm("value0z").set(obj_origin_node.track("tz").eval())\n'
        #                         'insertion_rest_node.parm("value0x").set(obj_insertion_node.track("tx").eval())\n'
        #                         'insertion_rest_node.parm("value0y").set(obj_insertion_node.track("ty").eval())\n'
        #                         'insertion_rest_node.parm("value0z").set(obj_insertion_node.track("tz").eval())\n'
        #                         '#print "hello"\n'
        #                         , "script_callback_language":"python"})

        hou_rig.utils.parm_to_ui(self.g_node, rest_muscle_button, ["Rig Parms"])

        #we try this if we have a node selection for hooks if not, just pass and drop the node
        try:
            self.hooking_a_node(self.g_node, "hook", hook_to=self.hook,  lock=1, selectableInViewport=0)
        except:
            pass

        #we try this if we have a node selection for hooks if not, just pass and drop the node
        try:
            self.hooking_a_node(self.g_node, "hook_upper",hook_to=self.second_hook, lock=1, selectableInViewport=0)
        except:
            pass
        self.g_node.parm("type").lock(1)

        origin_fetch_node = self.create_fetch_node(self.g_node)
        origin_position_node = self.g_node.createNode("null", "origin_position")
        origin_position_node.setInput(0, origin_fetch_node)
        origin = self.g_node.createNode("null", "origin")
        origin.setInput(0, origin_position_node)
        origin.setDisplayFlag(0)
        origin.setSelectableInViewport(0)
        #origin_position_node.parm("keeppos").set(1)

        insertion_fetch_node = self.create_fetch_node(self.g_node, parm_to_grab="hook_upper")
        insertion_position_node = self.g_node.createNode("null", "insertion_position")
        insertion_position_node.setInput(0, insertion_fetch_node)
        insertion = hou_rig.my_null.my_null(self.g_node, "insertion")
        insertion.setInput(0, insertion_position_node)
        insertion.setDisplayFlag(0)
        insertion.setSelectableInViewport(0)
        insertion.parm("ry").set(180)
        #insertion_position_node.parm("keeppos").set(1)

        origin.parm("lookatpath").set(origin.relativePathTo(insertion_position_node))
        origin.parm("lookup").set("quat")
        insertion.parm("lookatpath").set(insertion.relativePathTo(origin_position_node))
        insertion.parm("lookup").set("quat")


        center_null = self.g_node.createNode("null", "center")
        center_null.parm("lookatpath").set(center_null.relativePathTo(insertion))
        center_null.setDisplayFlag(0)
        center_null.setSelectableInViewport(0)

        #chop network-------------------------------
        chop_network = self.g_node.createNode("chopnet", "chopnet_muscle")

        obj_origin_node = chop_network.createNode("object", "object_origin")
        obj_origin_node.parm("targetpath").set(obj_origin_node.relativePathTo(origin))
        obj_origin_node.parm("range").set(0)

        obj_insertion_node = chop_network.createNode("object", "object_insertion")
        obj_insertion_node.parm("targetpath").set(obj_insertion_node.relativePathTo(insertion))
        obj_insertion_node.parm("range").set(0)

        math_node = chop_network.createNode("math", "math_average_position")
        math_node.setNextInput(obj_origin_node)
        math_node.setNextInput(obj_insertion_node)
        math_node.parm("chopop").set(5)

        jiggle_node = chop_network.createNode("jiggle", "jiggle_center_muscle")
        jiggle_node.setInput(0, math_node)

        switch_node = chop_network.createNode("switch", "switch_jiggle_effect")
        switch_node.setNextInput(math_node)
        switch_node.setNextInput(jiggle_node)

        export_node = chop_network.createNode("export", "export_Out")
        export_node.setNextInput(switch_node)
        export_node.parm("nodepath").set(export_node.relativePathTo(center_null))
        export_node.parm("path").set("t*")

        export_node.setDisplayFlag(1)
        export_node.setExportFlag(1)


        """
        #controling squash and stretch---------------------
        # origin_rest_node = chop_network.createNode("channel", "channel_origin_rest")
        # insertion_rest_node = chop_network.createNode("channel", "channel_insertion_rest")
        # rest_nodes = [origin_rest_node, insertion_rest_node]
        #
        # for i in rest_nodes:
        #     i.parm("name0").set("t")
        #     i.parm("size0").set(3)
        #
        # distance_rest_node = chop_network.createNode("object", "object_distance_rest")
        # distance_rest_node.parm("compute").set(4)
        # distance_rest_node.setInput(0, origin_rest_node)
        # distance_rest_node.setInput(1, insertion_rest_node)
        #
        # objects_distance_node = chop_network.createNode("object", "objects_animated_distance")
        # objects_distance_node.parm("compute").set(4)
        # objects_distance_node.setInput(0, obj_origin_node)
        # objects_distance_node.setInput(1, obj_insertion_node)
        #
        #
        # # VOP sop to calculate how much the muscle should stretch and squash
        # vopsop_muscle_ss = chop_network.createNode("vopchop", "vopchop_muscle_SS")
        # vopsop_muscle_ss.setInput(0, distance_rest_node)
        # vopsop_muscle_ss.setInput(1, objects_distance_node)

        #inside the vopsop to squash and stretch -------------------------------------------------------------------
        # parm_anim_distance = vopsop_muscle_ss.createNode("parameter", "parm_animation_distance")
        # parm_anim_distance.parm("parmname").set("animation_distance")
        # parm_anim_distance.parm("parmlabel").set("Animation Distance")
        # vopsop_muscle_ss.parm("animation_distance").setExpression("ic(0,0,0)")
        #
        # parm_rest_distance = vopsop_muscle_ss.createNode("parameter", "parm_rest_distance")
        # parm_rest_distance.parm("parmname").set("rest_distance")
        # parm_rest_distance.parm("parmlabel").set("Rest Distance")
        # vopsop_muscle_ss.parm("rest_distance").setExpression("ic(1,0,0)")
        #
        # cons_node = vopsop_muscle_ss.createNode("constant", "constant_by_1")
        # cons_node.parm("floatdef").set(1)
        #
        # div_node = vopsop_muscle_ss.createNode("divide", "divide")
        # div_node.setInput(0, parm_anim_distance, 0)
        # div_node.setInput(1, cons_node, 0)
        #
        # mult_node = vopsop_muscle_ss.createNode("multiply", "multiply")
        # mult_node.setInput(0, div_node, 0)
        # mult_node.setInput(1, parm_rest_distance, 0)
        #
        # outputs = vopsop_muscle_ss.node("output1")
        # outputs.setInput(0, mult_node, 0)

        #end of vopsop-----------------------------------------------------------------
        #start of second try
        # parm_anim_distance = vopsop_muscle_ss.createNode("parameter", "parm_animation_distance")
        # parm_anim_distance.parm("parmname").set("animation_distance")
        # parm_anim_distance.parm("parmlabel").set("Animation Distance")
        # vopsop_muscle_ss.parm("animation_distance").setExpression('chopci(opinputpath(".", 1), 0, $F)')
        #
        # parm_rest_distance = vopsop_muscle_ss.createNode("parameter", "parm_rest_distance")
        # parm_rest_distance.parm("parmname").set("rest_distance")
        # parm_rest_distance.parm("parmlabel").set("Rest Distance")
        # vopsop_muscle_ss.parm("rest_distance").setExpression("ic(1,0,0)")
        #
        # div_node = vopsop_muscle_ss.createNode("divide", "divide")
        # div_node.setInput(0, parm_rest_distance, 0)
        # div_node.setInput(1, parm_anim_distance, 0)
        # #----------
        # parm_stretch = vopsop_muscle_ss.createNode("parameter", "stretch_mult")
        # parm_stretch.parm("parmname").set("stretch_mult")
        # parm_stretch.parm("parmlabel").set("Stretch Mult")
        # parm_stretch.parm("floatdef").set(1)
        # parm_stretch.parmTuple("rangeflt").set([0, 1])
        #
        # parm_squash = vopsop_muscle_ss.createNode("parameter", "squash_mult")
        # parm_squash.parm("parmname").set("squash_mult")
        # parm_squash.parm("parmlabel").set("Squash Mult")
        # parm_squash.parm("floatdef").set(1)
        # parm_squash.parmTuple("rangeflt").set([1, 10])
        #
        # fit_node = vopsop_muscle_ss.createNode("fit", "fit_distances")
        # fit_node.setInput(0, div_node, 0)
        # fit_node.setInput(1, parm_stretch, 0)
        # fit_node.setInput(2, parm_squash, 0)
        # fit_node.setInput(3, parm_stretch, 0)
        # fit_node.setInput(4, parm_squash, 0)
        #
        # mult_node = vopsop_muscle_ss.createNode("multiply")
        # mult_node.setInput(0, div_node, 0)
        # mult_node.setInput(1, fit_node, 0)
        #
        # output_node = vopsop_muscle_ss.node("output1")
        # output_node.setInput(0, mult_node, 0)
        # #end of second try---------------------------------------------------------------------
        # vopsop_muscle_ss.layoutChildren()
        #
        # #end vopsops--------------------------------------------------------
        # chan_muscle_scale_default_node = chop_network.createNode("channel", "channel_muscle_scale_default")
        # chan_muscle_scale_default_node.parm("name0").set("musclescale")
        # chan_muscle_scale_default_node.parm("size0").set(3)
        # chan_muscle_scale_default_node.parm("value0x").setExpression('ch("../../muscle/musclescalex")')
        # chan_muscle_scale_default_node.parm("value0y").setExpression('ch("../../muscle/musclescaley")')
        # chan_muscle_scale_default_node.parm("value0z").setExpression('ch("../../muscle/musclescalez")')
        #
        # math_muscle_by_default_node = chop_network.createNode("math")
        # math_muscle_by_default_node.parm("chopop").set(3)
        # math_muscle_by_default_node.setNextInput(chan_muscle_scale_default_node)
        # math_muscle_by_default_node.setNextInput(vopsop_muscle_ss)
        #
        # export_muscle_scale = chop_network.createNode("export", "export_muscle_scale_SS")
        # export_muscle_scale.setInput(0, math_muscle_by_default_node)
        # export_muscle_scale.parm("nodepath").set("../../muscle/muscle")
        # export_muscle_scale.parm("path").set("musclescale*")
        #
        # export_muscle_scale.setExportFlag(1)
        """


        chop_network.layoutChildren()
        # finish chop network--------------------------------



        center_offset_node = self.g_node.createNode("null", "center_offset")
        center_offset_node.setInput(0, center_null)

        muscle_node = self.g_node.createNode("muscle", "muscle")
        muscle_node.parmTuple("musclescale").set([0.1, 0.1, 0.1])
        muscle_node.setColor(hou.Color((0.667, 0.0, 0.0)))

        list_for_guide = [origin, center_offset_node, insertion]
        for i in list_for_guide:
            i.parm("geoscale").set(.1)
            i.parm("keeppos").set(1)
            i.parm("controltype").set(1)

            muscle_node.setNextInput(i)
        for j in [origin_position_node, insertion_position_node]:
            j.parm("geoscale").set(.155)
            j.parm("keeppos").set(1)
            j.parm("controltype").set(1)



        self.g_node.layoutChildren()
        self.g_node.parm("rest_muscle").pressButton()














    def hooking(self, do_line=True, parm_h="hook"):
        """
        will set a relative path from a limb to their hook
        and will create a fetch node
        and will connect all of them one after the other
        at the end will create a line that connect all of them to see in the view port
        do_line = will create a line that visualize the connection between limbs
        """
        self.hooking_a_node(self.g_node, parm_h, lock=1, selectableInViewport=0)
        fetch_node = self.create_fetch_node(self.g_node)
        self.list_for_guide.insert(0, fetch_node)
        self.parent_a_chain(self.list_for_guide)
        if do_line is True:
        #Generate a curve line to see it on the view port
            self.make_guide_curve(self.limb_type+"_guide_curve", self.list_for_guide)

    def hooking_a_node(self, a_node, parm_name,hook_to="self.hook", lock=0, selectableInViewport=0):
        """
        find and set the hook parameter
        @param a_node: node to get the chain from:
        @param parm_name the string of the parameter name
        @return: hook path
        """
        a_node.parm(parm_name).set(self.g_node.relativePathTo(hook_to))
        a_node.parm("type").lock(lock)
        a_node.setSelectableInViewport(selectableInViewport)

    def create_fetch_node(self, a_node, parm_to_grab="hook"):
        """
        create a fetch node inside the subnet
        @param a_node: node where to put the fetch
        @return: the fetch node
        """
        fetch_node = a_node.createNode("fetch", "fetch_parent")
        fetch_node.setDisplayFlag(0)

        #fetch_node.parm("fetchobjpath").set("`chsop('../hook')`")
        fetch_node.parm("fetchobjpath").set("`chsop('../%s')`"%(parm_to_grab))
        fetch_node.parm("useinputoffetched").set(1)
        fetch_node.parm("fetchsubnet").set(1)
        return fetch_node

    def parent_a_chain(self, list_of_nodes):
        for index, i in enumerate(list_of_nodes):
            i.setPosition([0, index*-1])
            try:
                i.setNextInput(i_temp)
            except:
                pass
            i_temp = i

    def make_guide_curve(self, name, list_of_nodes, where=None):
        curve = hou_rig.line_maker.create_line(name, list_of_nodes, where)
        curve.setSelectableInViewport(0)
        return curve




    def subnet_shape(self, parent, merge_with=None):
        #todo arg locked,   will lock the renderflaged node before copy and unlocked after wards
        bone_subnet = parent.createNode("subnet", "subnet_bone_shape")
        if merge_with is not None:
            merge_bone_shape = parent.createNode("merge")

            merge_bone_shape.setNextInput(merge_with)
            merge_bone_shape.setNextInput(bone_subnet)

            null_shape_out = parent.createNode("null", "Out_Shape_Bone")
            null_shape_out.setInput(0, merge_bone_shape)

            null_shape_out.setDisplayFlag(1)
            null_shape_out.setRenderFlag(1)

            null_out = bone_subnet.createNode("null", "Out")
            null_out.setColor(hou.Color((0.2, 0.3, 0.5)))

            null_out.setDisplayFlag(1)
            null_out.setRenderFlag(1)

            parent.layoutChildren()
        return bone_subnet




    def bone_shape(self, bone_subnet):
        """
        creates a subnet with node to represent the shape of a bone
        @bone_subnet: where we construct all the nodes
        @return: subnet
        """
        ob_helper1 = bone_subnet.createNode("object_merge", "object_merge_helper1")
        ob_helper1.parm("xformtype").set(1)
        ob_helper1.parm("objpath1").set("../../point1")

        ob_helper2 = bone_subnet.createNode("object_merge", "object_merge_helper2")
        ob_helper2.parm("xformtype").set(1)
        ob_helper2.parm("objpath1").set('../../../chain_`opdigits("../..")+1`/point1')

        add_first = bone_subnet.createNode("add", "add_first")
        add_first.parm("usept0").set(1)
        add_first.parm("pt0x").setExpression('point("../object_merge_helper1", 0, "P" , 0)')
        add_first.parm("pt0y").setExpression('point("../object_merge_helper1", 0, "P" , 1)')
        add_first.parm("pt0z").setExpression('point("../object_merge_helper1", 0, "P" , 2)')

        add_second = bone_subnet.createNode("add", "add_second")
        add_second.parm("usept0").set(1)
        add_second.parm("pt0x").setExpression('point("../object_merge_helper2", 0, "P" , 0)')
        add_second.parm("pt0y").setExpression('point("../object_merge_helper2", 0, "P" , 1)')
        add_second.parm("pt0z").setExpression('point("../object_merge_helper2", 0, "P" , 2)')

        merge_objs = bone_subnet.createNode("merge")
        merge_objs.setNextInput(add_first)
        merge_objs.setNextInput(add_second)

        add_node = bone_subnet.createNode("add")
        add_node.setInput(0, merge_objs)
        add_node.parm("switcher1").set(1)

        pw_node = bone_subnet.createNode("polywire")
        pw_node.setInput(0, add_node)

        pw_node.parm("radius").set(0.1)
        pw_node.parm("div").set(6)

        null_any_geo_here = bone_subnet.createNode("null", "any_geometry_you_want_to_create")

        sw_node = bone_subnet.createNode("switch", "switch_shape")
        sw_node.setNextInput(pw_node)
        sw_node.setNextInput(null_any_geo_here)

        color_node = bone_subnet.createNode("color", "color_from_bone")
        color_node.setInput(0, sw_node)

        null_no_outputs = bone_subnet.createNode("null", "No_outputs_from_this_chain")

        switch_no_outputs = bone_subnet.createNode("switch", "switch_no_outputs")
        switch_no_outputs.setNextInput(null_no_outputs)
        switch_no_outputs.setNextInput(color_node)
        switch_no_outputs.parm("input").set(1)

        try:
            null_out = bone_subnet.node("Out")
            null_out.setColor(hou.Color((0.2, 0.3, 0.5)))
            null_out.setInput(0, switch_no_outputs)

            null_out.setDisplayFlag(1)
            null_out.setRenderFlag(1)
        except:
            pass
        bone_subnet.layoutChildren()


        return bone_subnet