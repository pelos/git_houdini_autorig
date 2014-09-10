import re
import random

import hou

import hou_rig
import hou_rig.construction.parts.flexor
import hou_rig.my_null
import hou_rig.utils
import hou_rig.my_path_cv
import hou_rig.line_maker


#todo:
'''
remove null_ik from the ik setup we dont need it any more
when the blend parm is getting smaller shrink the ik goal in one axis and when it get to 0 turn of display
if the weight from 2 to 5 are at zero don't display the offset



a null Control between chain bones??? for selection? or make the bone weird shape for selection???
what if the pre rig chains can have a shape that's been transfer to the rig. example a box shape on that place,
then the rig can grab it. for selection

geo class will create obj_merge or file,  will put a capture, paint, proximity deform,etc.. same as the autorig
will have a null with a UI folder structure that user can toggle what bones are been use to deform that mesh.
the classes have a list of all the bones created that can be use to populate the geometry class
parm on the pre rig geometry node to see if we promote geo stuff to the ui or not.


check later with a user:
parent chain_hook0 to the chain_offset, or to the fetch itself depending,  we need to see whats better option
'''
#todo promote the parms of the chain_offset
#todo chain_offset bone shape transfer, maybe an flying node some where just to hold the shape
#or a subnet inside the chain 1,  and we make a method that say if item in working nodes[0]

#todo  script to copy the position of the bones (world transform) and transfer to IK, "match IK Position"
#todo add the transformation of the subnet to the bone position so the user can position the subnet instead all the nodes inside
#todo promote chain_offset (before the first bone)
#todo only the controls wire frame parm should pick up the red right, and blue left color from the character placer.
#todo make a tendon class that use flexor. tendon will act as a semi bone

#todo not make the last bone, instead make a null at the tip

class master(object):
    def __init__(self, node, rig_subnet):
        """
        node is the subnet where we get all the information that we are going to use to create the rig
        """
        self.node = node
        """
        rig_subnet is the Subnet where we put all the bones and geo etc..
        """
        self.rig_subnet = rig_subnet

    def create_rig_node(self, rig_subnet):
        """
        a subnet that holds the chains parts ik etc... for the rig limb inside the self.rig_subnet
        """
        limb_subnet = rig_subnet.createNode("subnet")
        return limb_subnet

    def node_rename(self, node_with_info, a_node_to_check=None):
        """
        checks the rig position, and put l_ or r_  or c_  on the name of the created rig limb node
        """
        main_name = node_with_info.name()
        rig_position = node_with_info.parm("position").eval()
        name = rig_position + "_" + main_name
        if a_node_to_check is not None:
            a_node_to_check.setName(name)
        return name

    def make_color(self, a_node_to_check):
        """
        set self.color depending if its right left or center in the rig.
        """
        rig_position = a_node_to_check.parm("position").eval()
        #right side
        if rig_position == "right":
            self.color = hou.Color((0.467, 0.0, 0.0))
        # center side
        elif rig_position == "center":
            self.color = hou.Color((0.36, 0.36, 0.36))
        # left side
        elif rig_position == "left":
            self.color = hou.Color((0.1, 0.2, 0.5))

    def colorize_node(self, node_to_put_the_color, a_color):
        """
        put a color to a given node
        node_to_put_the_color = is the node that we want to colorize
        a_color = is the hou.Color that we are going to set
        """
        node_to_put_the_color.setColor(a_color)

    def position_node(self, a_node_to_check, node_to_put_the_position):
        """
        a_node_to_check = is the node that will fetch the position from
        node_to_put_the_position =  is the node that will set the position
        """
        rig_position = a_node_to_check.position()
        node_to_put_the_position.setPosition(rig_position)

    def create_spare_parms_folder(self):
        """
        creates a folder in the UI where we are going to place the rest of the parameters of the autorig.
        """
        #todo make sure the name the first letter is cap and no underscore for nice presentation. (watch out for other
        # function looking for that folder, leave the same name, just change the label.)
        hou_rig.utils.ui_folder(self.rig_subnet, ["Rig Parms", self.node.name()])
        #utils.utilities.ui_folder(self.rig_subnet, ["Rig Parms", self.node.name()])

    def name_hook(self, string_name, prefix=""):
        hook_name = string_name
        #hook_name = node_parm.eval().split("/")[-1]
        hook_digits = re.findall('\d+', hook_name)
        hook_digits_int = int(hook_digits[0])
        hook_digits_int -= 1
        hook_digits_str = str(hook_digits_int)
        hook_name = prefix + re.sub("\d+", hook_digits_str, hook_name)
        return hook_name

    def create_fetch_import(self, node_parm, where):
        """
        fetch the hook path and use that and set it on the node.
        @node: the node to read the parameters from
        @returns: a fetch node with the information pointing to the corresponding hook
        """
        # hook_name = node_parm.eval().split("/")[-1]
        # hook_digits = re.findall('\d+', hook_name)
        # hook_digits_int = int(hook_digits[0])
        # hook_digits_int -= 1
        # hook_digits_str = str(hook_digits_int)
        # hook_name = "hook_" + re.sub("\d+", hook_digits_str, hook_name)

        fetch = where.createNode("fetch")
        fetch.setDisplayFlag(0)
        fetch.parm("useinputoffetched").set(1)
        fetch.parm("fetchsubnet").set(1)
        fetch.setColor(hou.Color((0.867, 0.0, 0.0)))

        hook_path = self.hook_path(node_parm)
        fetch.parm("fetchobjpath").set(hook_path)
        return fetch

    def hook_for_chain_offset(self, a_node_to_connect_to=False):
        """
        null offset for a node
        a_node_to_connect = the input of the created null
        """
        parent = a_node_to_connect_to.parent()
        hook_for_chain_offset = parent.createNode("null", "hook_chain_0")
        hook_for_chain_offset.setInput(0, a_node_to_connect_to)
        hook_for_chain_offset.parm("keeppos").set(1)
        hook_for_chain_offset.setDisplayFlag(0)
        hook_for_chain_offset.setColor(hou.Color((0.0, 0.0, 0.0)))
        return hook_for_chain_offset

    def create_fetch_offset(self, connect_to=False, get_transform_from=False, node_name="chain_offset", set_vizualisation=False):
        """
        creates a null to work as an offset and it move it in another node world transform
        connect_to = input of the created null
        get_transform_from = null where we fetching the world transform
        """
        null_offset = self.limb_subnet.createNode("null")
        if get_transform_from is not False:
            #print get_transform_from.path(), get_transform_from.worldTransform()
            null_offset.setWorldTransform(get_transform_from.worldTransform())
            # null_offset.parm("tx").set(get_transform_from.worldTransform().extractTranslates()[0])
            # null_offset.parm("ty").set(get_transform_from.worldTransform().extractTranslates()[1])
            # null_offset.parm("tz").set(get_transform_from.worldTransform().extractTranslates()[2])

        null_offset.parm("keeppos").set(1)

        if connect_to is not False:
            null_offset.setInput(0, connect_to)

        null_offset.parm("geoscale").set(0.1)
        null_offset.parm("controltype").set(1)
        null_offset.parm("pre_xform").set(0)
        null_offset.parm("pre_xform").pressButton()
        null_offset.parm("tdisplay").set(1)
        null_offset.setName(node_name, unique_name=False)
        return null_offset


        # null_offset = self.limb_subnet.createNode("null" )
        # if get_transform_from is not False:
        #     null_offset.setWorldTransform(get_transform_from.worldTransform())
        #
        # null_offset.parm("keeppos").set(1)
        #
        # if connect_to is not False:
        #     null_offset.setInput(0, connect_to)
        #
        # null_offset.parm("geoscale").set(0.1)
        # null_offset.parm("controltype").set(1)
        # null_offset.parm("pre_xform").set(0)
        # null_offset.parm("pre_xform").pressButton()
        # null_offset.parm("tdisplay").set(1)
        # null_offset.setName(node_name)
        # return null_offset












    def working_nodes_list(self, node):
        """
        generate a list of nodes that we can work later one
        this list comes from the guide nulls inside the pre rig
        node = the node that contains the information with the guide curves, pre rig subnet
        """
        #todo mark the node with a hidden parameter that we can use to check if its a valid node to use.
        #self.limb_subnet = rig_subnet.createNode("subnet", node.name() )
        working_nodes_list = []
        for i in node.children():
            #if its not guide_ from the guide_curve
            # if "guide_" not in i.name():
            #     if i.type().nameComponents()[2] != "fetch":
            #         working_nodes_list.append(i)
            if "chain_" in i.name():
                if i.type().nameComponents()[2] == "geo":
                    working_nodes_list.append(i)

        working_nodes_list.sort(key=hou.Node.name)
        return working_nodes_list



    def create_bones(self, node, working_nodes_list, where):
        """
        create a bone chain from the nulls inside a pre rig subnet
        node = the node that contains the information with the guide curves, pre rig subnet
        working_nodes_list = is the list of null guides of the pre rig
        """
        self.list_for_hooks = []
        self.fetch = self.create_fetch_import(node, where)
        name_node = self.node.parm("hook").eval().split("/")[-1]
        name_node = self.name_hook(name_node, prefix="fetch_hook_")
        #name_node = self.name_hook(name_node, prefix="hook_")
        self.fetch.setName(name_node)


        self.list_for_hooks.append(self.fetch)

        self.null_offset = self.create_fetch_offset(self.fetch, working_nodes_list[0])

        self.fetch_hook = self.hook_for_chain_offset(self.null_offset)

        self.created_bones = []

        for index, null in enumerate(working_nodes_list):
            bone = self.limb_subnet.createNode("bone", "bone_" + null.name())
            bone.setColor(hou.Color((1.0, 0.8, 0.0)))
            # we don't need bone_wire_frame_color because we are using the shape to bone method.
            #we keep it for consistency
            self.bone_wire_frame_color(bone)
            self.randomize_a_color(bone.parmTuple("dcolor"))

            hook = self.limb_subnet.createNode("null", "hook_" + null.name())
            hook.setColor(hou.Color((0.0, 0.0, 0.0)))

            self.list_for_hooks.append(hook)

            bone.setSelectableInViewport(0)
            self.created_bones.append(bone)

            #transform the bones to the pre_rig position
            bone.parm("keeppos").set(1)
            null_world_transform = null.worldTransform()
            null_transform = null_world_transform.extractTranslates()
            bone.setWorldTransform(null_world_transform)

            # try to position to bone to the same location of the null
            try:
                #getting the length of the bone
                null_next = working_nodes_list[index + 1]
                null_next_transform = null_next.worldTransform().extractTranslates()

                bone.parm("lookup").set("quat")
                bone.parm("lookatpath").set(null_next.path())
                #bone.parm("lookup").set("off")
                bone.parm("length").set(null_transform.distanceTo(null_next_transform))

                #getting the rotation of the bone
                bone_after_aim = bone.worldTransform()
                bone.parm("lookatpath").set("")
                bone.setWorldTransform(bone_after_aim)

                bone.parm("pre_xform").set(0)
                bone.parm("pre_xform").pressButton()

                hook.setInput(0, bone)
                bone_length = bone.parm("length").eval()
                hook.parm("tz").set(bone_length * -1)
                hook.parm("geoscale").set(.01)
                hook.setDisplayFlag(0)
                hook.parm("keeppos").set(1)
                hook.parm("pre_xform").set(0)
                hook.parm("pre_xform").pressButton()


            except:
                pass



            if index == 0:
                bone.setNextInput(self.null_offset)
            else:
                bone.setNextInput(bone_temp)
            bone_temp = bone


            # if index == 0:
            #     bone.setNextInput(self.null_offset)
            #     # try to parent to the previews bone of the chain
            # try:
            #     bone.setNextInput(bone_temp)
            # except:
            #     pass
            # bone_temp = bone





            #transfer shape bones from prerig to rig.
            try:
                new_bone_shape_subnet = self.transfer_bone_shape_to(null.node("subnet_bone_shape"), bone)
                self.connect_bone_shape_to_bone_link(new_bone_shape_subnet, bone.node("bonelink"))
            except:
                pass
            self.limb_subnet.layoutChildren()
        self.chain_list = [self.null_offset] + self.created_bones

    def colorize_the_object(self, list_of_nodes, color):
        """
        change the color of the object display to view in the viewport
        list_of_nodes = list of nodes that we want to colorize
        color = the color that will be set on the item
        """
        for i in list_of_nodes:
            if i.type().nameComponents()[2] == "bone":
                i.node("bonelink").parm("uselinkcolor").set(1)
                i.node("bonelink").parmTuple("linkcolor").set(color.rgb())
            elif i.type().nameComponents()[2] == "null" or i.type().nameComponents()[2] == "geo":
                i.parm("use_dcolor").set(1)
                i.parmTuple("dcolor").set(color.rgb())

    def create_ik(self):
        #setting up for doing the IK
        k_type = self.node.parm("k_type").eval()
        if k_type == 0:
            pass
        elif k_type == 1 or k_type == 2:
        #----------------parms for the UI
        #todo remove all the jiberish and use the hou.utils to replace all this chunk of parm templates
            self.tg_parms = self.rig_subnet.parmTemplateGroup()

            self.ik_folder_parms = hou.FolderParmTemplate(self.node.name() + "ik", "IK")

            blend_value = hou.FloatParmTemplate(self.node.name() + "blend", "FK_IK Blend", 1, default_value=([1]),
                                                min=0, max=1, min_is_strict=True, max_is_strict=True)
            #blend_value.setJoinWithNext(True)
            self.ik_folder_parms.addParmTemplate(blend_value)

            #self.ik_folder_parms = hou.FolderParmTemplate(self.node.name()+"ik", "IK")
            ik_twist_parm = hou.FloatParmTemplate(self.node.name() + "iktwist", "IK Twist", 1, default_value=([0]),
                                                  min=-180, max=180, min_is_strict=False, max_is_strict=False,
                                                  look=hou.parmLook.Angle, naming_scheme=hou.parmNamingScheme.Base1)
            self.ik_folder_parms.addParmTemplate(ik_twist_parm)

            ik_dampening_parm = hou.FloatParmTemplate(self.node.name() + "ikdampen", "IK Dampening", 1,
                                                      default_value=([0]), min=0, max=1, min_is_strict=True,
                                                      max_is_strict=True, look=hou.parmLook.Regular,
                                                      naming_scheme=hou.parmNamingScheme.Base1)
            self.ik_folder_parms.addParmTemplate(ik_dampening_parm)

            ik_resolotuion_parm = hou.FloatParmTemplate(self.node.name() + "threshold", "Tracking Threshold Factor", 1,
                                                        default_value=([0.001]), min=0, max=1, min_is_strict=True,
                                                        max_is_strict=True, look=hou.parmLook.Regular,
                                                        naming_scheme=hou.parmNamingScheme.Base1)
            self.ik_folder_parms.addParmTemplate(ik_resolotuion_parm)

            # here append all the parms for the IK
            self.folder_node = self.tg_parms.findFolder(["Rig Parms", self.node.name()])
            self.tg_parms.appendToFolder(self.folder_node, self.ik_folder_parms)

            self.rig_subnet.setParmTemplateGroup(self.tg_parms)
            #----------------------------------------------------------------
            self.ik_root = self.created_bones[0]
            self.ik_end = self.created_bones[-2]
            self.chop = self.limb_subnet.createNode("chopnet", "chopnet_" + self.node.name())

            self.ik_parms_list = self.iks_multi_parms_list(self.node)
            for index, b in enumerate(self.ik_parms_list):
                if "character_placer" in b.eval():
                    ch_placer_parm = self.ik_parms_list.pop(index)

            fetch_ik = self.limb_subnet.createNode("fetch", "fetch_" + self.node.name())
            fetch_ik.setDisplayFlag(0)

            fetch_ik.parm("fetchobjpath").set(self.hook_path(ch_placer_parm))
            fetch_ik.parm("useinputoffetched").set(1)
            fetch_ik.parm("fetchsubnet").set(1)
            fetch_ik.setColor(hou.Color((0.867, 0.0, 0.0)))

            self.null_main_effector = self.limb_subnet.createNode("null", "null_ik_offset")
            self.null_main_effector.setNextInput(self.ik_end)
            self.null_main_effector.parm("keeppos").set(1)
            self.null_main_effector.setInput(0, None)
            self.null_main_effector.parm("tz").set(self.ik_end.parm("length").eval() * -1)
            self.null_main_effector.parm("controltype").set(1)
            self.null_main_effector.parm("orientation").set(3)
            self.null_main_effector.parm("pre_xform").set(0)
            self.null_main_effector.parm("pre_xform").pressButton()
            self.null_main_effector.setDisplayFlag(0)
            self.null_main_effector.setInput(0, fetch_ik)

            self.ik_chop = self.chop.createNode("inversekin", "inversekin_" + self.node.name())
            self.ik_chop.parm("solvertype").set(2)
            self.ik_chop.parm("bonerootpath").set(self.ik_chop.relativePathTo(self.ik_root))
            self.ik_chop.parm("boneendpath").set(self.ik_chop.relativePathTo(self.ik_end))

            #instead calling the method again why dont we just call self.null_effector_offset since we all ready
            # runned to method
            self.null_effector = self.multi_ik_parents(self.null_main_effector)
            self.ik_chop.parm("endaffectorpath").set(self.ik_chop.relativePathTo(self.null_effector))

            self.ik_chop.parm("blend").setExpression(
                'ch("' + self.ik_chop.relativePathTo(self.rig_subnet) + "/" + self.node.name() + 'blend")')

            self.ik_chop.parm("iktwist").setExpression(
                'ch("' + self.ik_chop.relativePathTo(self.rig_subnet) + "/" + self.node.name() + 'iktwist")')

            self.ik_chop.parm("ikdampen").setExpression(
                'ch("' + self.ik_chop.relativePathTo(self.rig_subnet) + "/" + self.node.name() + 'ikdampen")')

            self.ik_chop.parm("threshold").setExpression(
                'ch("' + self.ik_chop.relativePathTo(self.rig_subnet) + "/" + self.node.name() + 'threshold")')

            self.null_out = self.chop.createNode("null", "Out")
            self.null_out.setNextInput(self.ik_chop)

            for j in self.created_bones:
                if j != self.created_bones[-1]:
                    j.parm("solver").set(j.relativePathTo(self.null_out))
                    j.parmTuple("R").set([0, 0, 0])

            if k_type == 2:
                # todo maybe the fetch have to be the root of the chain and not the tip, that way can work as upvector.
                fetch_ch = self.limb_subnet.createNode("fetch", "fetch_ik_hook")
                fetch_ch.parm("fetchobjpath").set(self.hook_path(self.node.parm("ik_twist_parent")))

                fetch_ch.parm("useinputoffetched").set(1)
                fetch_ch.parm("fetchsubnet").set(1)
                fetch_ch.setDisplayFlag(0)

                self.null_twist = self.limb_subnet.createNode("null", "null_ik_twist")
                self.null_twist.parm("controltype").set(1)
                self.null_twist.parm("geoscale").set(0.1)
                self.null_twist.setWorldTransform(self.ik_root.worldTransform())
                self.null_twist.parm("pre_xform").set(0)
                self.null_twist.parm("pre_xform").pressButton()

                self.null_twist.parm("tz").set(self.ik_root.parm("length").eval() * -1)
                self.null_twist.parm("pre_xform").set(0)
                self.null_twist.parm("pre_xform").pressButton()
                self.null_twist.parm("keeppos").set(1)
                self.null_twist.setInput(0, fetch_ch)

                hou_rig.utils.list_of_parms_to_promote_to_ui([self.null_twist],
                                                             [["t", "tuple", "jwnp"], ["r", "tuple", "jwnp"]],
                                                             node_to_parm=self.rig_subnet,
                                                             into_this_folder=["Rig Parms", self.node.name(),
                                                                               "IK Goals", "Twist"])

                self.ik_chop.parm("twistaffectorpath").set(self.ik_chop.relativePathTo(self.null_twist))

        self.limb_subnet.layoutChildren()

    def hook_path(self, node_parm):
        #todo what if the chain is pointing to itself at the last chain?
        #todo  we need to offset the hook so it actually grab the one it needs.
        """
        will convert the parameter string from pre rig into autorig path.
        node_parm = the parameter we want to convert from pre rig to auto rig
        return a string with a path
        @node_parm: the houdini parameter
        """
        # if its for the multi ik setup
        if "ik_constraint" in node_parm.name():
            tt = node_parm.node().path()
            tt = hou.node(tt)
            tt = tt.node(node_parm.eval())
            position = tt.parent().parm("position").eval()
            position = position + "_"
        # if its for the hooks
        else:
            tt = node_parm.node().path()
            tt = hou.node(tt)
            position = node_parm.node().node(tt.parm("hook").eval()).parent().parm("position").eval()
            position = position + "_"

        hook_path = node_parm.eval()
        hook_path_split = hook_path.split("/")

        hook_path_last_index = hook_path_split.pop()
        digits = re.findall('\d+', hook_path_last_index)
        digits_int = int(digits[0])
        digits_int -= 1
        digits_str = str(digits_int)
        replace_last_index = "hook_" + re.sub("\d+", "", hook_path_last_index) + digits_str

        if len(hook_path_split) == 0:
            #if the node is child of the node in question.
            hook_path_split = hook_path
            hook_path = "../" + replace_last_index
            print "Becarefull:  you might get a recursive parenting problem"
            #hook_path = "../"+hook_path+"/"+replace_last_index
        else:
            hook_path_split[1] = position + hook_path_split[1]
            hook_path = "/".join(hook_path_split)
            hook_path = "../" + hook_path + "/" + replace_last_index

        return hook_path

    def iks_multi_parms_list(self, a_node):
        """
        a_node = the node that contains the information with the guide curves, pre rig subnet
        #return a list of strings where the ik goals lives
        """
        k_type = self.node.parm("k_type").eval()
        if k_type == 1 or k_type == 2:
            multi_iks_parms = []
            #for index, parm in enumerate(a_node.parms()):
            for parm in a_node.parms():
                if "ik_constraint" in parm.name():
                    #we dont do this like the null that way a goal can be parented to its same chain.
                    #and we can do position ik instead rotation. (verify this)
                    #if parm.eval() != a_node.parm("hook").eval():

                    #use this next 3 lines if we need to fix the path of the multi paths
                    hook_path = parm
                    #hook_path = self.hook_path(parm)
                    multi_iks_parms.append(hook_path)
                    #multi_iks_parms.append(parm)
            return multi_iks_parms

    def multi_ik_parents(self, null_ik):
        #todo make access a variable in the method instead instead using the self.ik_parm_list
        """
        will fetch the pre rig nodes of the ik goals
        and create corresponding goals for the IK chain
        null_ik = the main null IK that the chain follows
        return the null effects, the end of the chain so it can use for other purposes.
        """
        k_type = self.node.parm("k_type").eval()
        if k_type == 1 or k_type == 2:

            if len(self.ik_parms_list) > 0:
                self.blend_node = self.limb_subnet.createNode("blend", "blend_IK")
                self.blend_node.parm("blendw1").set(1)
                self.blend_node.parm("blendw2").set(0)
                self.blend_node.parm("blendw3").set(0)
                self.blend_node.parm("blendw4").set(0)
                self.blend_node.setDisplayFlag(0)
                self.blend_node.setColor(hou.Color((0.4, 0.2, 0.6)))
                self.blend_node.setNextInput(null_ik)

                blent_type = self.blend_node.parm("shortrotblend")
                hou_rig.utils.promote_parm_to_ui(blent_type, self.rig_subnet,
                                                 in_this_folder=["Rig Parms", self.node.name(), "Multi Goals"],
                                                 #parm_label=self.node.name()+"Rotation Blending")
                                                 parm_label="Rotation Blending",
                                                 parm_name=self.node.name() + "_shortrotblen")

            for index, i in enumerate(self.ik_parms_list):
                name = i.eval().split("/")
                if len(name) == 1:
                    #means the parm is relative inside the same subnet
                    name = name[0]
                    last_name = self.limb_subnet.name()
                else:
                    #means the parm is pointing out side to another subnet
                    name = name[-2]
                    last_name = name[-1]

                #todo check the name is right on the child creation.
                fetch_ik = self.limb_subnet.createNode("fetch", "fetch_" + name + "_" + last_name)
                fetch_ik.setDisplayFlag(0)

                ik_hook = self.hook_path(i)

                fetch_ik.parm("fetchobjpath").set(ik_hook)
                fetch_ik.parm("useinputoffetched").set(1)
                fetch_ik.parm("fetchsubnet").set(1)

                null = hou_rig.my_null.my_null(self.limb_subnet, name + "_" + last_name + "_offset")
                null.setNextInput(fetch_ik)
                null.setDisplayFlag(0)
                self.blend_node.setNextInput(null)

            #promoting the blend parameters
            max_range = len(self.ik_parms_list) + 2
            if len(self.ik_parms_list) >= 1:
                for index in range(1, max_range):
                    blend_parm = self.blend_node.parm("blendw" + str(index))
                    hou_rig.utils.promote_parm_to_ui(blend_parm, self.rig_subnet,
                                                     in_this_folder=["Rig Parms", self.node.name(), "Multi Goals"],
                                                     #parm_label=self.node.name()+"_blendw"+str(index))
                                                     parm_label="Weight " + str(index), maximum=1)

                    blend_mask = self.blend_node.parm("blendm" + str(index))
                    hou_rig.utils.promote_parm_to_ui(blend_mask, self.rig_subnet,
                                                     in_this_folder=["Rig Parms", self.node.name(), "Multi Goals"],
                                                     #parm_label=self.node.name()+"_blendm"+str(index))
                                                     parm_label="Mask " + str(index))

            list_of_nulls_effectors = []
            self.null_effector = hou_rig.my_null.my_null(self.limb_subnet, "ik_effector")
            self.null_effector.parm("geoscale").set(0.15)

            if len(self.ik_parms_list) > 0:
                self.null_effector.setNextInput(self.blend_node)
            else:
                self.null_effector.setNextInput(self.null_main_effector)

            list_of_nulls_effectors.append(self.null_effector)

            self.null_effector_offset = hou_rig.my_null.my_null(self.limb_subnet, "ik_effector_offset")
            self.null_effector_offset.parm("geoscale").set(0.1)
            self.null_effector_offset.parm("controltype").set(1)
            list_of_nulls_effectors.append(self.null_effector_offset)

            position_folder = ["Rig Parms", self.node.name(), "IK Goals", "Position"]
            hou_rig.utils.list_of_parms_to_promote_to_ui(list_of_nulls_effectors,
                                                         [["t", "tuple"], ["r", "tuple"], ["s", "tuple"],
                                                          ["p", "tuple"]], node_to_parm=self.rig_subnet,
                                                         into_this_folder=position_folder)

            aim_folder = ["Rig Parms", self.node.name(), "IK Goals", "Aim"]
            hou_rig.utils.list_of_parms_to_promote_to_ui(list_of_nulls_effectors,
                                                         [["lookatpath", "parm", "jwnp"], ["lookup", "parm", "jwnp"],
                                                          ["pathobjpath", "parm"], ["roll", "parm"], ["pos", "parm"],
                                                          ["uparmtype", "parm"], ["pathorient", "parm"],
                                                          ["up", "tuple", "jwnp"], ["bank", "parm", "jwnp"]],
                                                         node_to_parm=self.rig_subnet, into_this_folder=aim_folder)

            misc_folder = ["Rig Parms", self.node.name(), "IK Goals", "Misc"]
            hou_rig.utils.list_of_parms_to_promote_to_ui(list_of_nulls_effectors,
                                                         [["display", "parm"], ["use_dcolor", "parm"],
                                                          ["picking", "parm"], ["pickscript", "parm"],
                                                          ["caching", "parm"], ["geoscale", "parm"],
                                                          ["displayicon", "parm"], ["controltype", "parm"],
                                                          ["orientation", "parm"], ["shadedmode", "parm"]],
                                                         node_to_parm=self.rig_subnet, into_this_folder=misc_folder)

            self.null_effector_offset.setNextInput(self.null_effector)
            self.limb_subnet.layoutChildren
            return self.null_effector_offset

    def create_stretchy(self):
        k_type = self.node.parm("k_type").eval()
        stretchy = self.node.parm("stretchy").eval()
        if k_type == 1 or k_type == 2:
            if stretchy == 1:
                #todo instead creating the UI and then connect use the Utils.
                #Making the parms in the rig subnet to link later
                tg_parms = self.rig_subnet.parmTemplateGroup()
                ik_folder_parms = hou.FolderParmTemplate(self.node.name() + "stretchy", "Stretchy")

                min_value = hou.FloatParmTemplate(self.node.name() + "min", "min", 1, default_value=([1]), min=0,
                                                  max=10, min_is_strict=True)
                min_value.setJoinWithNext(True)
                ik_folder_parms.addParmTemplate(min_value)

                max_value = hou.FloatParmTemplate(self.node.name() + "max", "max", 1, default_value=([5]), min=1,
                                                  max=10)
                ik_folder_parms.addParmTemplate(max_value)

                # here append all the parms regarding the IK
                folder = tg_parms.findFolder(["Rig Parms", self.node.name()])

                tg_parms.appendToFolder(folder, ik_folder_parms)
                self.rig_subnet.setParmTemplateGroup(tg_parms)
                #---------------------------------------------------------------
                total_len_chop = self.chop.createNode("math", "math_total_length")
                total_len_chop.parm("chopop").set(1)

                stretch_ratio = self.chop.createNode("math", "math_stretch_ratio")

                self.clamped_ratio = self.chop.createNode("limit", "limit_clamped_ratio")
                self.clamped_ratio.parm("type").set(1)

                # we dont need them since we all ready created the parm on the UI with the value
                #self.clamped_ratio.parm("min").set(1)
                #Promote Max Some Where
                #self.clamped_ratio.parm("max").set(5)
                self.clamped_ratio.setNextInput(stretch_ratio)

                self.clamped_ratio.parm("min").setExpression(
                    'ch("' + self.clamped_ratio.relativePathTo(self.rig_subnet) + "/" + self.node.name() + 'min")')

                self.clamped_ratio.parm("max").setExpression(
                    'ch("' + self.clamped_ratio.relativePathTo(self.rig_subnet) + "/" + self.node.name() + 'max")')

                self.chop_list_created_nodes = []
                self.chop_list_streatch_bone = []
                self.chop_list_null_out = []
                for index, r in enumerate(self.created_bones[0:-1]):
                    cons_original_length = self.chop.createNode("constant", "constant_" + r.name())
                    bone_name = r.name()
                    cons_original_length.parm("name0").set(bone_name)
                    bone_len = r.parm("length").eval()
                    cons_original_length.parm("value0").set(bone_len)

                    self.chop_list_created_nodes.append(cons_original_length)
                    total_len_chop.setNextInput(cons_original_length)

                    stretch_bone = self.chop.createNode("math", "math_stretch" + r.name())
                    stretch_bone.parm("chopop").set(3)
                    stretch_bone.setNextInput(self.clamped_ratio)
                    stretch_bone.setNextInput(cons_original_length)
                    self.chop_list_streatch_bone.append(stretch_bone)

                    null_out = self.chop.createNode("null", "OUT_" + r.name())
                    self.chop_list_null_out.append(null_out)
                    null_out.setNextInput(stretch_bone)

                    r.parm("length").setExpression("chop('" + r.relativePathTo(null_out) + "/length')")
                    #---------------------------------------------------------------
                #calculating the current length of all the bones
                self.top_length = self.chop.createNode("object", "object_start_obj")
                self.top_length.parm("targetpath").set(self.top_length.relativePathTo(self.null_offset))
                self.top_length.setColor(hou.Color((.7, .5, .1)))

                self.tip_length = self.chop.createNode("object", "object_end_obj")
                self.tip_length.parm("targetpath").set(self.tip_length.relativePathTo(self.null_effector))
                self.tip_length.setColor(hou.Color((.7, .5, .1)))

                obj_measure = self.chop.createNode("object", "object_start_to_end_vector")
                obj_measure.setInput(0, self.top_length, 0)
                obj_measure.setInput(1, self.tip_length, 0)

                vector = self.chop.createNode("vector", "vector_current_len")
                vector.setInput(0, obj_measure, 0)

                stretch_ratio.setNextInput(vector)
                stretch_ratio.setNextInput(total_len_chop)
                stretch_ratio.parm("chopop").set(4)

                self.chop.layoutChildren()

    def ik_stretchy_knee_slide(self):
        #we need to count the bones or the nulls in pre rig.
        #if they are 2 regular leg
        #if they are 3 dog leg
        #else, regular single chain.

        k_type = self.node.parm("k_type").eval()
        stretchy = self.node.parm("stretchy").eval()
        ik_slide = self.node.parm("ik_slide").eval()

        #if set ik or ik with effect
        if k_type == 1 or k_type == 2:
            #if we are using stretchy AND ik _slide
            if stretchy == 1 and ik_slide == 1:
                # we just check that if we only have one chan,  still be able to work properly
                if len(self.node.children()) > 4:
                    self.first_ik_bone = self.chop_list_created_nodes[0]
                    self.second_ik_bone = self.chop_list_created_nodes[1]
                    self.first_ik_bone.setColor(hou.Color((0.5, 0.5, 0.8)))
                    self.second_ik_bone.setColor(hou.Color((0.5, 0.5, 0.7)))

                    self.first_ik_stretch = self.chop_list_streatch_bone[0]
                    self.second_ik_stretch = self.chop_list_streatch_bone[1]
                    self.first_ik_stretch.setColor(hou.Color((0.5, 0.2, 0.8)))
                    self.second_ik_stretch.setColor(hou.Color((0.5, 0.2, 0.7)))

                    self.first_null_out = self.chop_list_null_out[0]
                    self.second_null_out = self.chop_list_null_out[1]
                    self.first_null_out.setColor(hou.Color((0.5, 0.2, 0.8)))
                    self.second_null_out.setColor(hou.Color((0.5, 0.2, 0.8)))

                    # Putting the parameters in the UI
                    tg_parms_stretchy = self.rig_subnet.parmTemplateGroup()

                    ik_folder_parms = tg_parms_stretchy.findFolder(["Rig Parms", self.node.name(), "Stretchy"])
                    knee_slice_value = hou.FloatParmTemplate(self.node.name() + "knee_slice", "Knee Slice", 1,
                                                             default_value=([0]), min=-1, max=1)

                    tg_parms_stretchy.appendToFolder(ik_folder_parms, knee_slice_value)
                    self.rig_subnet.setParmTemplateGroup(tg_parms_stretchy)

                    # creating the additional nodes for knee sliding
                    knee_slide = self.chop.createNode("constant", "constant_knee_slide")
                    knee_slide.parm("name0").set("kneeSlice")
                    knee_slide.parm("value0").setExpression(
                        'ch("' + knee_slide.relativePathTo(self.rig_subnet) + '/' + self.node.name() + 'knee_slice")')

                    value1 = self.chop.createNode("constant", "constant_value_of_one")
                    value1.parm("name0").set("value1")
                    value1.parm("value0").set(1)

                    up_low_ratio = self.chop.createNode("math", "math_up_low_ratio")
                    up_low_ratio.parm("chopop").set(4)
                    up_low_ratio.setNextInput(self.first_ik_bone)
                    up_low_ratio.setNextInput(self.second_ik_bone)

                    fixed_low_slide = self.chop.createNode("math", "math_fixed_low_slide")
                    fixed_low_slide.setNextInput(knee_slide)
                    fixed_low_slide.setNextInput(up_low_ratio)
                    fixed_low_slide.parm("chopop").set(3)

                    up_slide = self.chop.createNode("math", "math_up_slide")
                    up_slide.setNextInput(value1)
                    up_slide.setNextInput(knee_slide)
                    up_slide.parm("chopop").set(2)

                    low_slide = self.chop.createNode("math", "math_low_slide")
                    low_slide.setNextInput(value1)
                    low_slide.setNextInput(fixed_low_slide)
                    low_slide.parm("chopop").set(1)

                    up_with_slide = self.chop.createNode("math", "math_up_with_slide")
                    up_with_slide.setNextInput(self.clamped_ratio)
                    up_with_slide.setNextInput(up_slide)
                    up_with_slide.parm("chopop").set(3)

                    low_with_slide = self.chop.createNode("math", "math_low_with_slide")
                    low_with_slide.setNextInput(self.clamped_ratio)
                    low_with_slide.setNextInput(low_slide)
                    low_with_slide.parm("chopop").set(3)

                    self.first_ik_stretch.setInput(0, None)
                    self.first_ik_stretch.setInput(0, up_with_slide)
                    self.first_ik_stretch.setInput(1, self.first_ik_bone)

                    self.second_ik_stretch.setInput(0, None)
                    self.second_ik_stretch.setInput(0, low_with_slide)
                    self.second_ik_stretch.setInput(1, self.second_ik_bone)

                    self.knee_lock()
                    self.chop.layoutChildren()
                else:
                    print "we were not able to create IK_slide for " + self.node.name() + " since its only one chain"
                    print "you might reconsider the settings, or add additional chains \n"

    def knee_lock(self):
        k_type = self.node.parm("k_type").eval()
        stretchy = self.node.parm("stretchy").eval()
        if k_type == 2 and stretchy == 1:
            tg_parms_stretchy = self.rig_subnet.parmTemplateGroup()
            ik_folder_parms = tg_parms_stretchy.findFolder(["Rig Parms", self.node.name(), "Stretchy"])
            knee_lock = hou.FloatParmTemplate(self.node.name() + "knee_lock", "Knee Lock", 1, default_value=([0]),
                                              min=0, max=1)
            tg_parms_stretchy.appendToFolder(ik_folder_parms, knee_lock)

            ik_folder_parms = tg_parms_stretchy.findFolder(["Rig Parms", self.node.name(), "Stretchy"])
            upper_extra_length = hou.FloatParmTemplate(self.node.name() + "upper_extra_length", "Upper Extra Length", 1,
                                                       default_value=([1]), min=0, max=10)
            tg_parms_stretchy.appendToFolder(ik_folder_parms, upper_extra_length)

            ik_folder_parms = tg_parms_stretchy.findFolder(["Rig Parms", self.node.name(), "Stretchy"])
            lower_extra_length = hou.FloatParmTemplate(self.node.name() + "lower_extra_length", "Lower Extra Length", 1,
                                                       default_value=([1]), min=0, max=10)
            tg_parms_stretchy.appendToFolder(ik_folder_parms, lower_extra_length)

            self.rig_subnet.setParmTemplateGroup(tg_parms_stretchy)

            twist_obj = self.chop.createNode("object", "object_twist_obj")
            twist_obj.parm("targetpath").set(twist_obj.relativePathTo(self.null_twist))

            constant_knee_lock = self.chop.createNode("constant", "constant_knee_lock")
            constant_knee_lock.parm("name0").set("knee_lock1")
            constant_knee_lock.parm("value0").setExpression(
                'ch("' + constant_knee_lock.relativePathTo(self.rig_subnet) + '/' + self.node.name() + 'knee_lock")')

            constant_knee_lock.parm("name1").set("knee_lock2")
            constant_knee_lock.parm("value1").setExpression(
                'ch("' + constant_knee_lock.relativePathTo(self.rig_subnet) + '/' + self.node.name() + 'knee_lock")')
            #-----------------------------------------------------------------------------
            start_to_twist_vec = self.chop.createNode("object", "object_start_to_twist_vec")
            start_to_twist_vec.setInput(0, twist_obj)
            start_to_twist_vec.setInput(1, self.top_length)

            start_to_twist_len = self.chop.createNode("vector", "vector_start_to_twist_len")
            start_to_twist_len.setInput(0, start_to_twist_vec)

            twist_to_end_vec = self.chop.createNode("object", "object_twist_to_end_vec")
            twist_to_end_vec.setInput(0, twist_obj)
            twist_to_end_vec.setInput(1, self.tip_length)

            twist_to_end_len = self.chop.createNode("vector", "vector_twist_to_end_len")
            twist_to_end_len.setInput(0, twist_to_end_vec)
            #------------------------------------------------------------------------
            up_blend = self.chop.createNode("blend", "blend_up_blend")
            up_blend.setNextInput(constant_knee_lock)
            up_blend.setNextInput(self.first_ik_stretch)
            up_blend.setNextInput(start_to_twist_len)
            up_blend.setColor(hou.Color((.2, .7, .9)))

            low_blend = self.chop.createNode("blend", "blend_low_blend")
            low_blend.setNextInput(constant_knee_lock)
            low_blend.setNextInput(self.second_ik_stretch)
            low_blend.setNextInput(twist_to_end_len)
            low_blend.setColor(hou.Color((.2, .7, .9)))

            #SWITCH THE ORDER THAT THEY ARE INPUT INTO THE MATH NODE, SINCE WE NEED TO OUTPUT THE LENGTH CHANNEL!
            up_extra = self.chop.createNode("constant", "constant_up_extra")
            up_extra.parm("name0").set("up_extra")
            up_extra.parm("value0").setExpression('ch("' + constant_knee_lock.relativePathTo(
                self.rig_subnet) + '/' + self.node.name() + 'upper_extra_length")')

            up_extra_fix = self.chop.createNode("math", "math_up_extra_fix")
            up_extra_fix.parm("chopop").set(3)

            up_extra_fix.setNextInput(up_blend)
            up_extra_fix.setNextInput(up_extra)
            self.first_null_out.setInput(0, up_extra_fix)

            low_extra = self.chop.createNode("constant", "constant_up_extra")
            low_extra.parm("name0").set("low_extra")
            low_extra.parm("value0").setExpression('ch("' + constant_knee_lock.relativePathTo(
                self.rig_subnet) + '/' + self.node.name() + 'lower_extra_length")')

            low_extra_fix = self.chop.createNode("math", "math_low_extra_fix")
            low_extra_fix.parm("chopop").set(3)

            low_extra_fix.setNextInput(low_blend)
            low_extra_fix.setNextInput(low_extra)
            self.second_null_out.setInput(0, low_extra_fix)

    def toon_curve(self, list_of_nodes, promote_shape_parms=True, promote_cvs=True, divisions=8):
        """
        from a list of nodes will create the necessary null_cvs and create a curve with bscale attributes to drive a
        chain of bone that follow the curve
        @param list_of_nodes: list of node that will generate the curve
        @return:created_toon_nodes, toon_curve
        """
        parent = list_of_nodes[0].parent()
        self.toon_subnet = parent.createNode("subnet", "subnet_toon_curve")
        created_toon_nodes = []
        #created_toon_nodes_bias = []
        # in case we need this lists
        created_toon_nodes_bias_center = []
        created_toon_nodes_bias_lower = []
        created_toon_nodes_bias_upper = []

        created_toon_nodes_order_for_promotion = []

        for i in list_of_nodes:
            fetch = self.toon_subnet.createNode("fetch", "fetch_" + i.name())
            fetch.parm("fetchobjpath").set(fetch.relativePathTo(i))
            fetch.parm("useinputoffetched").set(1)
            fetch.parm("fetchsubnet").set(1)
            fetch.setDisplayFlag(0)

            ccv = hou_rig.my_path_cv.My_path_cv(self.toon_subnet, i.name() + "_c_cv")
            ccv = ccv.path_cv
            ccv.setInput(0, fetch)
            lcv = hou_rig.my_path_cv.My_path_cv(self.toon_subnet, i.name() + "_l_cv")
            lcv = lcv.path_cv
            lcv.setInput(0, ccv)
            ucv = hou_rig.my_path_cv.My_path_cv(self.toon_subnet, i.name() + "_u_cv")
            ucv = ucv.path_cv
            ucv.setInput(0, ccv)

            if i.type().nameComponents()[2] == "bone":
                bone_length = i.parm("length").eval()
                ccv.parm("tz").set(bone_length * -1)
                ccv.parm("pre_xform").set("clean")
                ccv.parm("pre_xform").pressButton()

            created_toon_nodes.append(lcv)
            created_toon_nodes.append(ccv)
            created_toon_nodes.append(ucv)

            # created_toon_nodes_bias.append(lcv)
            # created_toon_nodes_bias.append(ucv)

            created_toon_nodes_bias_center.append(ccv)
            created_toon_nodes_bias_lower.append(lcv)
            created_toon_nodes_bias_upper.append(ucv)

            # ordering the list for promote the parameters
            created_toon_nodes_order_for_promotion.append(ccv)
            created_toon_nodes_order_for_promotion.append(lcv)
            created_toon_nodes_order_for_promotion.append(ucv)

        toon_curve = hou_rig.line_maker.create_line("toon_curve", created_toon_nodes, self.toon_subnet, "Out", basic_curve=True)
        toon_curve.setDisplayFlag(0)

        for j in created_toon_nodes:
            #looping ALL THE nodes in the list
            j.parm("geoscale").set(0.05)
            j.parm("controltype").set(2)
            j.parmTuple("dcolor").set([0.25, 0.35, 0.65])

        for z in created_toon_nodes_bias_lower:
            #looping just the lcv and ucv nodes
            z.parm("geoscale").set(0.04)
            z.parm("controltype").set(1)
            z.parm("orientation").set(3)
            z.parmTuple("dcolor").set([0.15, 0.25, 0.15])

        for z in created_toon_nodes_bias_upper:
            #looping just the lcv and ucv nodes
            z.parm("geoscale").set(0.04)
            z.parm("controltype").set(1)
            z.parm("orientation").set(2)
            z.parmTuple("dcolor").set([0.15, 0.25, 0.15])

        flex = hou_rig.construction.parts.flexor.flexor(toon_curve)
        flex_chain = flex.run_toon_curves(toon_curve, divisions, "toon_bone_", where=self.toon_subnet)

        self.toon_subnet.layoutChildren()


        if promote_shape_parms is True:
            flex.promote_shape_parms(flex.import_curve,
                                     self.rig_subnet,
                                     folder=["Rig Parms", self.node.name(), "T Curve", "Shapes"],
                                     name=self.node.name()+"test")



        #---------------------------------------------------------------------
        if promote_cvs is True:
            parm_toggle = hou.ToggleParmTemplate(self.node.name()+"_display_cvs", "Display CVs", default_value=False)

            hou_rig.utils.ui_folder(self.rig_subnet, in_this_folder=["Rig Parms", self.node.name(), "T Curve", "CVs"])
            promoted_parm_toggle = hou_rig.utils.parm_to_ui(self.rig_subnet, parm_toggle, in_this_folder=["Rig Parms", self.node.name(), "T Curve", "CVs"])
            hou_rig.utils.togle_display_nodes(promoted_parm_toggle, created_toon_nodes_order_for_promotion)

            bones_toggle = hou.ToggleParmTemplate(self.node.name()+"_display_bones", "Display Bones", default_value=False)
            promoted_bones_toggle = hou_rig.utils.parm_to_ui(self.rig_subnet, bones_toggle, in_this_folder=["Rig Parms", self.node.name(), "T Curve", "CVs"])
            hou_rig.utils.togle_display_nodes(promoted_bones_toggle, flex_chain[0])

            #-------------------------------------------------------------------------
            import re
            for z in created_toon_nodes_order_for_promotion:
                if z in created_toon_nodes_bias_center:
                    hou_rig.utils.promote_parm_to_ui(z.parmTuple("t"), self.rig_subnet, in_this_folder=["Rig Parms", self.node.name(), "T Curve", "CVs"], parm_label= re.sub('_', ' ', z.name().title()+" T"),  parm_name= self.node.name()+z.name()+"t")
                    hou_rig.utils.promote_parm_to_ui(z.parmTuple("r"), self.rig_subnet, in_this_folder=["Rig Parms", self.node.name(), "T Curve", "CVs"], parm_label= re.sub('_', ' ', z.name().title()+" R"),  parm_name= self.node.name()+z.name()+"r")
                    hou_rig.utils.promote_parm_to_ui(z.parmTuple("s"), self.rig_subnet, in_this_folder=["Rig Parms", self.node.name(), "T Curve", "CVs"], parm_label= re.sub('_', ' ', z.name().title()+" S"),  parm_name= self.node.name()+z.name()+"s")

                if z in created_toon_nodes_bias_lower+created_toon_nodes_bias_upper:
                    hou_rig.utils.promote_parm_to_ui(z.parmTuple("t"), self.rig_subnet, in_this_folder=["Rig Parms", self.node.name(), "T Curve", "CVs"], parm_label= re.sub('_', ' ', z.name().title()+" T"),  parm_name= self.node.name()+z.name()+"t")
        return created_toon_nodes, toon_curve









    def transfer_bone_shape_to(self, bone_shape_subnet, where, lock=True):
        if lock is True:
            for i in bone_shape_subnet.children():
                if i.isRenderFlagSet() is True:
                    locked_node = i
                    locked_node.setHardLocked(1)
        hou.copyNodesTo([bone_shape_subnet], where)

        if lock is True:
            locked_node.setHardLocked(0)

        return where.node(bone_shape_subnet.name())


    def connect_bone_shape_to_bone_link(self, a_node, node_to_connect, promote_parm_before="displaylink"):
        """
        connect a bone_shape_subnet to the bone link to be able to switch different shapes.
        @param a_node: the subnet that will connect
        @param node_to_connect: the node that we want to use to connect
        @return:
        """
        #todo if parent type its a null use display if its a bone use displaylink


        parent = node_to_connect.parent()
        #zero out the rotation of the mesh against the bone
        xform_zero = parent.createNode("xform", "xform_zero_out_shape")
        xform_zero.setInput(0, a_node)
        xform_zero.bypass(1)
        null_blank = parent.createNode("null", "null_no_display")

        merge = parent.createNode("merge")
        merge.setNextInput(xform_zero)
        merge.setNextInput(node_to_connect)

        sw_node = parent.createNode("switch", "switch_display")
        sw_node.setNextInput(xform_zero)
        sw_node.setNextInput(node_to_connect)
        sw_node.setNextInput(merge)

        #displaylink parm setJoinsWIth next, might be a bug in houdini
        tg = parent.parmTemplateGroup()
        display_link_parm = tg.find(promote_parm_before)
        display_link_parm.setJoinWithNext(1)
        tg.replace(promote_parm_before, display_link_parm)
        parent.setParmTemplateGroup(tg)

        display_link_parm_template = hou.MenuParmTemplate("display_type", "Display Type",
                                                          menu_items=(["0", "1", "2"]),
                                                          menu_labels=(["Custom","Bone Link","Custom + Bone Line"]),
                                                          default_value=2,
                                                          icon_names=([])   )
        hou_rig.utils.parm_to_ui(parent, display_link_parm_template, insert_after_parm=promote_parm_before)
        sw_node.parm("input").set(parent.parm("display_type"))

        cd_node = parent.createNode("color", "colorize_node")
        cd_node.setInput(0, sw_node)


        cd_node.parm("colorr").set(cd_node.parent().parm("dcolorr"))
        cd_node.parm("colorg").set(cd_node.parent().parm("dcolorg"))
        cd_node.parm("colorb").set(cd_node.parent().parm("dcolorb"))

        sw_final = parent.createNode("switch", "switch_display")
        sw_final.setNextInput(null_blank)
        sw_final.setNextInput(cd_node)
        sw_final.parm("input").set(parent.parm(promote_parm_before))

        try:
            a_node.node("Out").setNextInput(sw_final)
        except:
            pass

        null_out = parent.createNode("null", "Out")
        null_out.setInput(0, sw_final)

        null_out.setDisplayFlag(1)
        null_out.setRenderFlag(1)

        xform_zero.parm("rx").set(-90)

        parent.layoutChildren()

    def bone_wire_frame_color(self, bone):
        bone_link = bone.node("bonelink")

        bone_link.parm("uselinkcolor").set(1)
        bone_link.parm("linkcolorr").set(bone.parm("dcolorr"))
        bone_link.parm("linkcolorg").set(bone.parm("dcolorg"))
        bone_link.parm("linkcolorb").set(bone.parm("dcolorb"))

    def randomize_a_color(self, color_parameter_tuple):
        for index, i in enumerate(color_parameter_tuple):
            color_parameter_tuple[index].set(random.random())

    def destroy_last_bone(self):
        """
        destroy the last bone of the chain because we only needed to point the anti last bone to it
        same for the hooks
        @return:
        """
        #todo see if we can make a list of hooks from [0:-1] so we dont extra create one
        self.list_for_hooks[-1].destroy()
        self.created_bones[-1].destroy()