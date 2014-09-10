import master
import hou_rig.utils

class null(master.master):
    def __init__(self, node, rig_subnet):
        print "null"
        self.node = node
        self.rig_subnet = rig_subnet
        self.limb_subnet = self.create_rig_node(self.rig_subnet)

        self.node_rename(self.node, self.limb_subnet)
        self.make_color(self.node)
        self.colorize_node(self.limb_subnet, self.color)
        self.position_node(self.node, self.limb_subnet)

        self.create_spare_parms_folder()

        working_nodes_list = self.working_nodes_list(self.node)

        self.fetch = self.create_fetch_import(self.node.parm("hook"), self.limb_subnet)

        self.null_offset = self.create_fetch_offset(self.fetch, working_nodes_list[0], node_name="chain")
        self.null_offset_chain = self.create_fetch_offset(self.null_offset, working_nodes_list[0],
                                                          node_name="chain_offset")

        self.null_offset_chain.parm("controltype").set(2)
        if self.node.parm("k_type").eval() == 1:
            self.null_offset.setDisplayFlag(0)
            self.null_offset_chain.setDisplayFlag(0)

        self.fetch_hook = self.hook_for_chain_offset(self.null_offset_chain)

        self.colorize_the_object([self.null_offset], self.color)
        self.colorize_the_object([self.null_offset_chain], self.color)

        self.ik_parms_list = self.iks_multi_parms_list(self.node)
        self.multi_ik_parents(self.null_offset_chain)

        self.promote_chains_parameters()
        self.create_bone_for_deformation(self.null_offset_chain)
        self.move_hook_and_bone_deformer()

        self.limb_subnet.layoutChildren()

    def move_hook_and_bone_deformer(self):
        if self.node.parm("k_type").eval() != 0:
            self.bone_deformer.setInput(0, self.null_effector_offset)
            self.fetch_hook.setInput(0, self.null_effector_offset)

    def promote_chains_parameters(self):
        list_of_nodes = (self.null_offset, self.null_offset_chain)
        if self.node.parm("k_type").eval() == 0:
            # for i in list_of_nodes:
            #     i.setDisplayFlag(0)

            position_folder = ["Rig Parms", self.node.name(), "Position"]
            hou_rig.utils.list_of_parms_to_promote_to_ui(list_of_nodes, [["t", "tuple", "label=Transform"],
                                                                         ["r", "tuple", "label=Rotation"],
                                                                         ["s", "tuple", "label=Scale"],
                                                                         ["p", "tuple", "label=Pivot"]],
                                                         node_to_parm=self.rig_subnet, into_this_folder=position_folder)

            aim_folder = ["Rig Parms", self.node.name(), "Aim"]

            hou_rig.utils.list_of_parms_to_promote_to_ui(list_of_nodes,
                                                         [["lookatpath", "parm", "jwnp"], ["lookup", "parm", "jwnp"],
                                                          ["pathobjpath", "parm"], ["roll", "parm"], ["pos", "parm"],
                                                          ["uparmtype", "parm"], ["pathorient", "parm"],
                                                          ["up", "tuple", "jwnp"], ["bank", "parm", "jwnp"]],
                                                         node_to_parm=self.rig_subnet, into_this_folder=aim_folder)

            misc_folder = ["Rig Parms", self.node.name(), "Misc"]
            hou_rig.utils.list_of_parms_to_promote_to_ui(list_of_nodes, [["display", "parm"], ["use_dcolor", "parm"],
                                                                         ["picking", "parm"], ["pickscript", "parm"],
                                                                         ["caching", "parm"], ["geoscale", "parm"],
                                                                         ["displayicon", "parm"],
                                                                         ["controltype", "parm"],
                                                                         ["orientation", "parm"],
                                                                         ["shadedmode", "parm"]],
                                                         node_to_parm=self.rig_subnet, into_this_folder=misc_folder)


    def create_bone_for_deformation(self, node_to_connect_the_bone):
        name = self.node.name() + "_bone_deformer"
        self.bone_deformer = node_to_connect_the_bone.parent().createNode("bone", name)
        self.bone_deformer.setNextInput(node_to_connect_the_bone)
        self.bone_deformer.setDisplayFlag(0)
        self.bone_deformer.parm("scale").set(0.1)
        self.bone_deformer.parm("tz").setExpression("ch('scale')*0.5")

    def create_hook_for_the_offset(self, parent):
        # #todo can we delete this function?
        pass
        # '''
        # this put the animatable controls where they should depending if
        # its using ik or not.
        # (will connect them before the IK, or after the blend.)
        # '''
        # if self.node.parm("k_type").eval() == 0:
        #     pass
        # elif self.node.parm("k_type").eval() > 0:
        #     self.fetch_hook.setInput(0, self.null_effector_offset)
        # return self.fetch_hook

    def iks_multi_parms_list(self, a_node):
        """
        if we leave this method as the master,  will duplicate the nodes
        putting the character placer twice, so we over ride the method
        here, saying, if the hook is the same as one of the multi ik,
        don't use it.
        """
        k_type = self.node.parm("k_type").eval()
        #if k_type == 1 or k_type == 2:
        if k_type == 1:
            multi_iks_parms = []
            for parm in a_node.parms():
                if "ik_constraint" in parm.name():
                    if parm.eval() != a_node.parm("hook").eval():
                        hook_path = parm
                        #hook_path = self.hook_path(parm)
                        multi_iks_parms.append(hook_path)
                        #multi_iks_parms.append(parm)

            return multi_iks_parms