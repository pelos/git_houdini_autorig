#todo who's the rest anchor?  the parent null or the actual bone for sliding the skin?
#todo promote parameters
#todo stretch and squash the muscle

import master
import hou
import hou_rig.utils
import hou_rig.global_variables as gv

class muscle(master.master):
    def __init__(self, node, rig_subnet):
        print "muscle"
        self.node = node
        self.rig_subnet = rig_subnet

        self.limb_subnet = self.create_rig_node(self.rig_subnet)

        self.node_rename(self.node, self.limb_subnet)
        self.make_color(self.node)
        self.colorize_node(self.limb_subnet, self.color)
        self.position_node(self.node, self.limb_subnet)

        #todo put all this into smaller functions
        copy_self_node = hou.copyNodesTo([self.node], self.node.parent())
        copy_self_node = copy_self_node[0]

        copy_self_node.node("fetch_parent").destroy()
        copy_self_node.node("fetch_parent1").destroy()

        hou.copyNodesTo(copy_self_node.children(), self.limb_subnet)
        copy_self_node.destroy()

        # creating the nodes into variables--------------------------------------------------------------
        fetch = self.create_fetch_import(self.node.parm("hook"), self.limb_subnet)
        fetch_upper = self.create_fetch_import(self.node.parm("hook_upper"), self.limb_subnet)
        list_of_fetchers = [fetch, fetch_upper]

        self.o_position = self.limb_subnet.node("origin_position")
        self.i_position = self.limb_subnet.node("insertion_position")
        self.center_offset = self.limb_subnet.node("center_offset")
        self.muscle_node = self.limb_subnet.node("muscle")
        self.chop_muscle = self.limb_subnet.node("chopnet_muscle")
        self.jiggle_switch_node = self.chop_muscle.node("switch_jiggle_effect")
        self.jiggle_node = self.chop_muscle.node("jiggle_center_muscle")


        list_of_positioners = [self.o_position, self.i_position]

        for index, i in enumerate(list_of_positioners):
            # i.parm("keeppos").set(0)
            i.setInput(0, list_of_fetchers[index])
            # i.parm("keeppos").set(1)

        self.limb_subnet.layoutChildren()

        muscle_node = self.limb_subnet.node("muscle")
        muscle_node.parm("tdisplay").set(1)
        try:
            muscle_node_position = muscle_node.position()
            chop_node = self.limb_subnet.node("chopnet_muscle")
            chop_node.setPosition([muscle_node_position[0], (muscle_node_position[1]-.5)])
        except:
            pass

        self.muscle_view()
        self.promote_parms(self.rig_subnet, ["Rig Parms", self.node.name()])
        self.promote_viz_positioners()

        gv.muscle_deformers_list.append(muscle_node)


    def muscle_view(self):
        self.muscle_sop = self.muscle_node.node("muscle")
        del_sop = self.muscle_node.createNode("delete")
        del_sop.parm("group").set("muscle")
        del_sop.setName("delete_muscle_metaballs")
        del_sop.setInput(0, self.muscle_sop)
        self.switch_sop = self.muscle_node.createNode("switch", "switch_viz")
        self.switch_sop.setNextInput(del_sop)
        self.switch_sop.setNextInput(self.muscle_sop)
        self.switch_sop.parm("input").set(1)
        null_out = self.muscle_node.createNode("null", "Out_Viz")
        null_out.setInput(0, self.switch_sop)
        null_out.setDisplayFlag(1)
        null_out.setColor(hou.Color((0.1, 0.1, 0.1)))
        self.muscle_sop.setRenderFlag(1)
        self.muscle_node.layoutChildren()

    def promote_parms(self, node_to_put, folder_to_put_in=[]):
        #origin insertion center positional nodes.
        hou_rig.utils.ui_folder(node_to_put, folder_to_put_in)
        nodes_trans_to_promote = [self.o_position, self.i_position, self.center_offset]
        hou_rig.utils.list_of_parms_to_promote_to_ui(nodes_trans_to_promote,
                                                     [["t", "tuple", "jwnp"],
                                                      ["r", "tuple", "jwnp"],
                                                      ["scale", "parm", "jwnp"]],
                                                     node_to_parm=node_to_put,
                                                     into_this_folder=folder_to_put_in+["Muscle Trans"])

        hou_rig.utils.ui_folder(node_to_put, folder_to_put_in+["Muscle"])

        hou_rig.utils.promote_parm_to_ui(self.muscle_node.parm("display"), self.rig_subnet, in_this_folder=folder_to_put_in+["Muscle"],parm_name=self.node.name()+"_display")
        hou_rig.utils.promote_parm_to_ui(self.switch_sop.parm("input"), self.rig_subnet, in_this_folder=folder_to_put_in+["Muscle"], minimum=0, maximum=1, parm_name=self.node.name()+"input", parm_label="View Metaball")


        # hou_rig.utils.list_of_parms_to_promote_to_ui([self.muscle_node],
        #                                              [["display", "parm", "jwnp"]],
        #                                              node_to_parm=node_to_put,
        #                                              into_this_folder=folder_to_put_in + ["Muscle"],separator_line=False)
        # hou_rig.utils.list_of_parms_to_promote_to_ui([self.switch_sop],
        #                                              [["input", "parm", "label=Display Metaball"]],
        #                                              node_to_parm=node_to_put,
        #                                              into_this_folder=folder_to_put_in + ["Muscle"])










        hou_rig.utils.list_of_parms_to_promote_to_ui([self.muscle_node],
                                                     [
                                                      #["positionbias", "parm", "jwnp"],
                                                      ["musclescale", "tuple", "jwnp"],
                                                      ["primspersegment", "parm", "jwnp"]],
                                                     node_to_parm=node_to_put,
                                                     into_this_folder=folder_to_put_in + ["Muscle"])
        #muscle node parms
        for i in range(1, 6):
            hou_rig.utils.list_of_parms_to_promote_to_ui([self.muscle_node],
                                                         [["control"+str(i)+"scale", "tuple", "label=scale "+str(i)]],
                                                         node_to_parm=node_to_put,
                                                         into_this_folder=folder_to_put_in + ["Muscle"])
            if 1 < i < 5:
                hou_rig.utils.list_of_parms_to_promote_to_ui([self.muscle_node],
                                                             [["control" + str(i) + "position", "parm", "label=Position "+str(i)]],
                                                             node_to_parm=node_to_put,
                                                             into_this_folder=folder_to_put_in + ["Muscle"])
        # jiggle parameters
        hou_rig.utils.ui_folder(node_to_put, folder_to_put_in+["Jiggle"])
        # hou_rig.utils.list_of_parms_to_promote_to_ui([self.jiggle_switch_node],
        #                                              [["index", "parm", "jwnp", "label=Jiggle On"]],
        #                                              node_to_parm=node_to_put,
        #                                              into_this_folder=folder_to_put_in + ["Jiggle"])
        hou_rig.utils.promote_parm_to_ui(self.jiggle_switch_node.parm("index"),
                                         node_to_put,
                                         in_this_folder=folder_to_put_in + ["Jiggle"],
                                         minimum=0,
                                         maximum=1,
                                         parm_label="Jiggle On")

        hou_rig.utils.list_of_parms_to_promote_to_ui([self.jiggle_node],
                                                     [["stiff", "parm"],
                                                      ["damp", "parm"],
                                                      ["limit", "parm"],
                                                      ["flex", "parm"],
                                                      ["mult", "tuple"]],
                                                     node_to_parm=node_to_put,
                                                     into_this_folder=folder_to_put_in + ["Jiggle"])


        #todo promote the jiggle and all the info to another tab.

    def promote_viz_positioners(self):
        list_of_positioners = [self.o_position, self.center_offset, self.i_position]
        for i in list_of_positioners:
            i.parm("tdisplay").set(1)

            label = i.name().split("_")
            label = label[0].title()
            label = label + " Display"
            hou_rig.utils.promote_parm_to_ui(i.parm("display"),
                                             self.rig_subnet,
                                             in_this_folder=["Rig Parms", self.node.name(), "viz"],
                                             parm_label=label,
                                             parm_name= i.name()+"display")

        # hou_rig.utils.list_of_parms_to_promote_to_ui(list_of_positioners,
        #                                              [["display", "parm"]],
        #                                              node_to_parm=self.rig_subnet,
        #                                              into_this_folder=["Rig Parms", self.node.name(), "viz"])


























