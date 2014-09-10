""" in houdini
from hou_rig.construction.builder import build_stuff
build_stuff()
"""
#todo ask if we want to make it otl and save it to the hip file and close it after is done to test it.
#todo add a progress bar with pyqt
#todo each class should have a property type where is chain, muscle etc... for post loop

import sys
import hou
import hou_rig.utils
import hou_rig.construction.parts.geometry
import hou_rig.global_variables as gv

#from hou_rig import utils
#from hou_rig.construction.parts import arm, leg, single, spine, flexor, null, character_placer
class build_stuff():
    """
    loop all the classes and construct the rig part base on that.
    """
    def __init__(self):
        #order them  that the character placer is the first one.
        list_of_node_to_build = hou.selectedNodes()
        if len(list_of_node_to_build) == 1 and "pre_rig" in list_of_node_to_build[0].name():
            list_of_node_to_build[0].extractAndDelete()
            list_of_node_to_build = hou.selectedNodes()

        #converting the selected node tuple into a list
        list_of_node_to_build = list(list_of_node_to_build)

        #todo WHY DOESNT ACCOMMODATE THE CLASSES IN ORDER!!! FIRST CHARACTER PLACER, THEN the rest and finally geometry
        #extracting character_placer
        #extracting_geometry
        character_placer_list = []
        geometry_nodes_list = []
        muscle_nodes_list = []
        amount_of_nodes_to_build = len(list_of_node_to_build)
        for index, i in enumerate(list_of_node_to_build):
            if i.parm("type").eval() == "character_placer":
                ch_placer = list_of_node_to_build.pop(index)
                character_placer_list.append(ch_placer)

            if i.parm("type").eval() == "geometry":
                geo = list_of_node_to_build.pop(index)
                geometry_nodes_list.append(geo)
            if i.parm("type").eval() == "muscle":
                geo = list_of_node_to_build.pop(index)
                muscle_nodes_list.append(geo)


        #putting it at the front of the list
        #list_of_node_to_build.insert(0, ch_placer)
        list_of_node_to_build = character_placer_list + list_of_node_to_build + geometry_nodes_list + muscle_nodes_list
        #list_of_node_to_build = list_of_node_to_build + geometry_nodes_list
        #putting it at the back of the list
        #list_of_node_to_build.append(ch_placer)

        lvl = ch_placer.parent()
        name = ch_placer.parm("name").eval()

        """
        for index, i in enumerate(list_of_node_to_build):
            for j in i.parms():
                if j.name() == "name":
                    #means this is character_placer
                    lvl = i.parent()
                    name = j.eval()
                    #we take out the character placer form the list
                    ch_placer = list_of_node_to_build.pop(index)
        # we added back to the list at the end.
        list_of_node_to_build.append(ch_placer)
        #list_of_node_to_build.insert(1,ch_placer)
        """

        pre_rig = list_of_node_to_build[0].parent().collapseIntoSubnet(list_of_node_to_build, "pre_rig_"+name)
        pre_rig.setDisplayFlag(0)
        pre_rig.setSelectableInViewport(0)
        list_of_node_to_build = pre_rig.children()


        #todo do we create the rig subnet in this module or in the init of each class? is we do in each class is more independent
        # create the Master subnet where all the rig parts will be created
        rig_subnet = lvl.createNode("subnet", name)
        pre_rig_position = pre_rig.position()
        rig_subnet.setPosition([pre_rig_position[0], pre_rig_position[1]-1])

        #hidden the subnet folder
        hou_rig.utils.ui_folder(rig_subnet, in_this_folder=["Rig Parms"], insert_before_parm=(0,))
        hou_rig.utils.hide_folder_or_parm_from_ui(rig_subnet, hide_this=["Subnet"])
        hou_rig.utils.hide_folder_or_parm_from_ui(rig_subnet, hide_this=["Transform"])

        print "[" +" "*amount_of_nodes_to_build+"]"
        list_of_classes = []
        for index, i in enumerate(list_of_node_to_build):
            rig_type = i.parm("type").eval()

            var = __import__("hou_rig.construction.parts."+rig_type, globals(), locals(), ["*"], -1)
            g = getattr(var, rig_type)
            class_type = g(i, rig_subnet)
            list_of_classes.append(class_type)

            am_spaces = index+1.0
            rest_space = (amount_of_nodes_to_build-index)-1.0
            percentage = am_spaces/amount_of_nodes_to_build
            print "[" +"."*int(am_spaces)+" "*int(rest_space)+"]" + " %"+str(percentage)
            sys.stdout.flush()


            # sys.stdout.write(str(index))
            # sys.stdout.write( '\r Working ----> %d ' % index )
            # sys.stdout.flush()
            # sys.stdout.write(".")
            # sys.stdout.flush()


        #todo maybe a method to loop the geometry classes and populate the deformers
        for i in list_of_classes:
            print i.rig_subnet

        # print "bone deformers: "
        # print gv.bone_deformers_list
        # print "muscle deformers: "
        # print gv.muscle_deformers_list