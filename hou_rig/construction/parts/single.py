#todo verify ik outside the methods like self.toon_curve so we only verify it once.
import hou
import master
import hou_rig.utils
import hou_rig.line_maker
import hou_rig.global_variables as gv

class single(master.master):
    def __init__(self, node, rig_subnet):
        print "single"
        self.node = node
        self.rig_subnet = rig_subnet
        self.limb_subnet = self.create_rig_node(self.rig_subnet)

        self.node_rename(self.node, self.limb_subnet)
        self.make_color(self.node)
        self.colorize_node(self.limb_subnet, self.color)
        self.position_node(self.node, self.limb_subnet)

        self.create_spare_parms_folder()

        working_node_list = self.working_nodes_list(self.node)


        self.create_bones(self.node.parm("hook"), working_node_list, self.limb_subnet)
        #self.colorize_the_object(self.created_bones, self.color)

        list_of_bones_to_promote = self.created_bones[0:-1]

        hou_rig.utils.list_of_parms_to_promote_to_ui(list_of_bones_to_promote,
                                                     [["t", "tuple", "jwnp"],
                                                      ["r", "tuple", "jwnp"],
                                                      ["scale", "parm", "jwnp"]],
                                                     node_to_parm=self.rig_subnet,
                                                     into_this_folder=["Rig Parms", self.node.name(), "Bones"])

        self.create_ik()
        self.create_stretchy()
        self.ik_stretchy_knee_slide()

        if self.node.parm("toon_curve").eval() == 1:
            node_divisions = int(self.node.parm("divisions").eval())
            self.toon_curve(self.chain_list[0:-1], divisions=node_divisions)
        self.destroy_last_bone()

        hou_rig.utils.ui_folder(self.rig_subnet, in_this_folder=["Rig Parms", self.node.name(), "Viz"])
        hou_rig.utils.list_of_parms_to_promote_to_ui(list_of_bones_to_promote,
                                                     [["displaylink", "parm", "jwnp"],
                                                      ["display_type", "parm"]],
                                                     node_to_parm=self.rig_subnet,
                                                     into_this_folder=["Rig Parms", self.node.name(), "Viz"])

        gv.bone_deformers_list.append(list_of_bones_to_promote)
