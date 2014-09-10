import hou

import master
import hou_rig.line_maker
import hou_rig.utils
import hou_rig.my_path_cv
import hou_rig.construction.parts.flexor
import hou_rig.global_variables as gv

#todo the UI should be same as single,  inside  t curve folder and promote the s and s of the curve.
#todo promote the carve
#todo the hooks should fetch the position of the bones so when they are carve down, they will follow correctly

class spine(master.master):
    def __init__(self, node, rig_subnet):
        print "spine"
        self.node = node
        self.rig_subnet = rig_subnet
        self.limb_subnet = self.create_rig_node(self.rig_subnet)

        self.node_rename(self.node, self.limb_subnet)
        self.make_color(self.node)
        self.colorize_node(self.limb_subnet, self.color)
        self.position_node(self.node, self.limb_subnet)

        working_nodes_list = self.working_nodes_list(self.node)

        # creating the fetchers----------------------------------------------------------------
        fetch = self.create_fetch_import(self.node.parm("hook"), self.limb_subnet)
        fetch_upper = self.create_fetch_import(self.node.parm("hook_upper"), self.limb_subnet)
        list_of_fetchers = [fetch, fetch_upper]

        #generating the first curve to use as template for position the real nodes
        self.created_nodes = self.create_spine_curve(working_nodes_list)
        spinal_curve = self.generate_curve("spinal_curve", self.created_nodes, basic_curve=True)

        # creating and position of cvs--------------------------
        list_of_cvs = self.create_spine_cvs(spinal_curve, amount_nulls=4)
        self.nodes_to_follow_a_path(list_of_cvs, spinal_curve)
        self.bake_node_wtransform(list_of_cvs)
        hou_rig.utils.change_display_look(list_of_cvs, geo_scale=0.05, control_type=2)

        # creating and position of end controllers--------------------------------
        list_of_end_controllers= self.create_spine_cvs(spinal_curve, amount_nulls=2, name_of_nulls="spine_ends_control_")
        self.nodes_to_follow_a_path(list_of_end_controllers, spinal_curve)
        self.bake_node_wtransform(list_of_end_controllers)

        hou_rig.utils.change_display_look(list_of_end_controllers, geo_scale=0.5, control_type=1, orientation=3)

        spine_curve = self.generate_curve("spine_curve", list_of_cvs, basic_curve=True, name_of_node_to_merge="Out")
        spine_curve.setDisplayFlag(0)


        self.clean_subnet([spinal_curve]+self.created_nodes)

        #connecting the chain of nodes------------------------------------------------------
        self.connect_cvs_to_ends(list_of_cvs, list_of_end_controllers, list_of_fetchers)
        ##### bone_curve = hou_rig.construction.parts.master.master(self.node, self.rig_subnet)
        ##### bone_curve = bone_curve.toon_curve(working_nodes_list, divisions=spine_segments)

        bone_curve_flex = hou_rig.construction.parts.flexor.flexor(spine_curve)
        spine_segments = self.node.parm("divisions").eval() - 2
        list_of_bones = bone_curve_flex.run_toon_curves(spine_curve, spine_segments, name_of_bones="spine_core")
        bone_curve_flex.import_curve.node("resample1").parm("segs").set(spine_segments)

        hook_list = self.create_and_conect_hook_nodes(self.limb_subnet, [list_of_bones[1], list_of_bones[2]])

        # #arrenging the layout--------------------------------------------
        self.limb_subnet.layoutChildren()

        new_bone_shape_subnet = self.transfer_bone_shape_to(working_nodes_list[0].node("subnet_bone_shape"), list_of_end_controllers[0],lock=False)
        self.connect_bone_shape_to_bone_link(new_bone_shape_subnet, list_of_end_controllers[0].node("control1"), promote_parm_before="display")


        #todo create the interface should be their own method
        #creating the interface of the UI------------------------
        self.create_spare_parms_folder()
        hou_rig.utils.list_of_parms_to_promote_to_ui(list_of_end_controllers[::-1],
                                                     [["t", "tuple", "jwnp"],
                                                      ["r", "tuple", "jwnp"],
                                                      ["scale", "parm", "jwnp"]],
                                                     node_to_parm=self.rig_subnet,
                                                     into_this_folder=["Rig Parms", self.node.name(), "Controllers"])
        list_of_cvs.reverse()
        hou_rig.utils.list_of_parms_to_promote_to_ui([list_of_cvs[0]], [["t", "tuple", "jwnp"], ["r", "tuple", "jwnp"],
                                                                        ["scale", "parm", "jwnp"]],
                                                     node_to_parm=self.rig_subnet,
                                                     into_this_folder=["Rig Parms", self.node.name(), "CVs"])
        hou_rig.utils.list_of_parms_to_promote_to_ui([list_of_cvs[1]], [["t", "tuple", "jwnp"], ["r", "tuple", "jwnp"]],
                                                     node_to_parm=self.rig_subnet,
                                                     into_this_folder=["Rig Parms", self.node.name(), "CVs"])
        hou_rig.utils.list_of_parms_to_promote_to_ui([list_of_cvs[3]], [["t", "tuple", "jwnp"], ["r", "tuple", "jwnp"],
                                                                        ["scale", "parm", "jwnp"]],
                                                     node_to_parm=self.rig_subnet,
                                                     into_this_folder=["Rig Parms", self.node.name(), "CVs"])
        hou_rig.utils.list_of_parms_to_promote_to_ui([list_of_cvs[2]], [["t", "tuple", "jwnp"], ["r", "tuple",
                                                                                                 "jwnp"]],
                                                     node_to_parm=self.rig_subnet,
                                                     into_this_folder=["Rig Parms", self.node.name(), "CVs"])

        gv.bone_deformers_list.append(list_of_bones)




    def generate_curve(self, name, centers, where=None, name_of_node_to_merge="point1", imp_normals=False,
                       basic_curve=False):
        """
        creates a curve from the upper and lower spine chains.
        @param name: name of the curve
        @param centers: list of nodes to use to create the curve.
        @param where: where are putting the curve node
        @param name_of_node_to_merge: whats the node that is looking for to grab the point
        @param imp_normals: import the normals of not.
        """
        curve = hou_rig.line_maker.create_line(name, centers, where, name_of_node_to_merge, basic_curve)
        return curve



    def create_and_conect_hook_nodes(self, where, list_of_nodes):
        created_hooks = []
        for index, i in enumerate(list_of_nodes):
            fetch_node = where.createNode("fetch", "fetch_bone"+str(index))

            fetch_node.parm("fetchobjpath").set(fetch_node.relativePathTo(i) )
            fetch_node.parm("useinputoffetched").set(1)
            fetch_node.parm("fetchsubnet").set(1)
            fetch_node.setDisplayFlag(0)

            hook = where.createNode("null")
            hook.parm("keeppos").set(1)
            hook.setColor(hou.Color((0.0, 0.0, 0.0)))
            hook.setInput(0, fetch_node)
            hook.setName("hook_chain_"+str(index))
            hook.setDisplayFlag(0)

            created_hooks.append(hook)

        hou_rig.utils.change_display_look(created_hooks, geo_scale=.1)
        return created_hooks



    # def create_hook_nodes(self, working_node_list):
    #     """
    #     creates hook fetch nodes grabbing the information of the pre rig and bringing it to the limb
    #     @param working_node_list: the list of all the nodes in the pre rig limb
    #     @return: created_hooks  its  list with the fetch nodes that we just created.
    #     """
    #     created_hooks = []
    #     for index, null in enumerate(working_node_list):
    #         #name = null.name()
    #         #name_string = ''.join([i for i in name if not i.isdigit()])
    #         hook = self.limb_subnet.createNode("null")
    #         hook.parm("keeppos").set(1)
    #         hook.setColor(hou.Color((0.0, 0.0, 0.0)))
    #         hook.setInput(0, working_node_list[index])
    #         #hook.setDisplayFlag(0)
    #         hook.setName("hook_chain_"+str(index))
    #         hook.setDisplayFlag(0)
    #
    #         created_hooks.append(hook)
    #
    #     hou_rig.utils.change_display_look(created_hooks, geo_scale=.1)
    #     return created_hooks

    def create_spine_curve(self, working_nodes_list):
        """
        creates the necessary nodes to create a spine
        @param working_nodes_list: list of nodes to with
        @return: list of nodes created
        """
        created_nodes = []
        for index, null in enumerate(working_nodes_list):
            spine_bone = self.limb_subnet.createNode("null", "spine_" + null.name())
            spine_bone.setColor(hou.Color((1.0, 0.8, 0.0)))

            spine_bone.setSelectableInViewport(0)
            created_nodes.append(spine_bone)

            #transform the bones to the pre_rig position
            spine_bone.parm("keeppos").set(1)
            null_world_transform = null.worldTransform()
            #null_transform = null_world_transform.extractTranslates()
            spine_bone.setWorldTransform(null_world_transform)
        return created_nodes

    def create_spine_cvs(self, curve, amount_nulls=4, name_of_nulls="path_cv", where=None):
        """
        for a given curve create # nulls across it.
        @param curve: the curve that the nulls will follow.
        @amount_nulls: the number of nulls that will be created.
        @return: list of nulls
        """
        list_of_cvs = []
        if where is not None:
            where = where
        else:
            where = curve.parent()

        for i in range(amount_nulls):
            spine_cv = hou_rig.my_path_cv.My_path_cv(self.limb_subnet, name_of_nulls+str(i))
            list_of_cvs.append(spine_cv.path_cv)

        return list_of_cvs

    def nodes_to_follow_a_path(self, list_of_nodes, curve_to_follow):
        """
        will place the nodes along the cord of a curve evenly
        @param list_of_nodes: the nodes that will be place along the curve
        @param curve_to_follow: the curve that will drive the position of the nodes
        @return:list_of_nodes on its new position
        """
        amount_of_nodes = float(len(list_of_nodes))
        for index, i in enumerate(list_of_nodes):
            pos_along_curve = float(index)/(amount_of_nodes-1)
            i.parm("pathobjpath").set(i.relativePathTo(curve_to_follow))
            i.parm("pos").set(pos_along_curve)
            i.parmTuple("up").set([0, 1, 1])

        return list_of_nodes

    def bake_node_wtransform(self, list_of_nodes):
        for i in list_of_nodes:
            wt = i.worldTransform()
            i.parm("pathobjpath").set("")
            i.setWorldTransform(wt)
            i.parm("keeppos").set(1)
            i.parm("pre_xform").set(0)
            i.parm("pre_xform").pressButton()

    def clean_subnet(self, list_of_nodes):
        """
        destroy the nodes in the list
        @param list_of_nodes: list of nodes
        @return:
        """
        for i in list_of_nodes:
            i.destroy()

    def connect_cvs_to_ends(self, list_of_cvs, list_of_ends, list_of_fetchers):
        for index, i in enumerate(list_of_ends):
            if index == 0:
                i.setInput(0, list_of_fetchers[0])
                list_of_cvs[0].setInput(0, i)
                list_of_cvs[1].setInput(0, list_of_cvs[0])

            if index == len(list_of_ends)-1:
                i.setInput(0, list_of_fetchers[-1])

                list_of_cvs[3].setInput(0, i)
                list_of_cvs[2].setInput(0, list_of_cvs[3])