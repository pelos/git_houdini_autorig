import hou
import hou_rig.my_null
import master

class character_placer(master.master):
    def __init__(self, node, rig_subnet):
        print "character placer"
        self.node = node
        self.rig_subnet = rig_subnet
        self.limb_subnet = self.create_rig_node(self.rig_subnet)

        self.node_rename(self.node, self.limb_subnet)
        self.position_node(self.node, self.limb_subnet)

        null_ch = self.limb_subnet.createNode("null", "character_placer")
        null_ch.parm("controltype").set(1)
        null_ch.parm("geoscale").set(2)
        null_ch.parm("orientation").set(2)

        hook = hou_rig.my_null.my_null(self.limb_subnet, "hook_chain_0")
        #hook = hou_rig.my_null.my_null(self.subnet, "character_placer_hook")
        hook.setInput(0, null_ch)
        hook.setColor(hou.Color((0.15, 0.15, 0.15)))
        hook.parm("geoscale").set(1)
        hook.parm("controltype").set(3)
        hook.parm("orientation").set(2)

        self.parameters_ui()
        self.connect_parms()
        self.limb_subnet.layoutChildren()

    def parameters_ui(self):
        # opening the template group
        tg_parms = self.rig_subnet.parmTemplateGroup()
        ch_p_folder_parms = hou.FolderParmTemplate(self.node.name()+"character_placer", "character_placer")
        # creating the parms
        for i in self.limb_subnet.children():
            hou_parm_template = hou.FloatParmTemplate(i.name()+"_t", "Translate", 3, default_value=([0, 0, 0]),
                                                    min=0, max=10, min_is_strict=False, max_is_strict=False,
                                                    look=hou.parmLook.Regular,
                                                    naming_scheme=hou.parmNamingScheme.XYZW)
            ch_p_folder_parms.addParmTemplate(hou_parm_template)

            hou_parm_template = hou.FloatParmTemplate(i.name()+"_r", "Rotate", 3, default_value=([0, 0, 0]), min=0,
                                                    max=360, min_is_strict=False, max_is_strict=False,
                                                    look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.XYZW)
            ch_p_folder_parms.addParmTemplate(hou_parm_template)

            hou_parm_template = hou.FloatParmTemplate(i.name()+"_s", "Scale", 3, default_value=([1, 1, 1]), min=0,
                                                    max=10, min_is_strict=False, max_is_strict=False,
                                                    look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.XYZW)
            ch_p_folder_parms.addParmTemplate(hou_parm_template)

            hou_parm_template = hou.FloatParmTemplate(i.name()+"_p", "Pivot", 3, default_value=([0, 0, 0]), min=0,
                                                    max=10, min_is_strict=False, max_is_strict=False,
                                                    look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.XYZW)
            ch_p_folder_parms.addParmTemplate(hou_parm_template)


            hou_parm_template = hou.SeparatorParmTemplate(i.name()+"_sep")
            ch_p_folder_parms.addParmTemplate(hou_parm_template)

        #finding the folder to put the parms and closing the template
        folder_node = tg_parms.findFolder(["Rig Parms"])
        tg_parms.appendToFolder(folder_node, ch_p_folder_parms)
        self.rig_subnet.setParmTemplateGroup(tg_parms)

    def connect_parms(self):
        list_of_parms = ["t", "r", "s", "p"]
        list_of_vectors = ["x", "y", "z"]

        for i in self.limb_subnet.children():
            for j in list_of_parms:
                for z in list_of_vectors:
                    i.parm(j+z).setExpression('ch("'+i.relativePathTo(self.rig_subnet)+"/"+i.name()+"_"+j+z+'")')