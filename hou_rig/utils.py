import hou
#todo in parm to ui, if the folder doesnt exist run ui_folder from scratch currently works if the main folder doesexist
#todo touch the parm after been linked, press button to refresh it.

def ui_folder(node_to_put_the_folder, in_this_folder=[None], insert_before_parm=None, insert_after_parm=None):
    """
    creates a folder in the UI of the given node
    node_to_put_the_folder = node where we are going to create the folder
    in_this_folder = []  is expecting a tuple of strings, each string represent a folder, that its inside a
    folder example ['bla', 'ble', 'bli'] where folder bli, is inside ble, that's inside bla.
    to specify a folder name should be the last string of the tuple, example
    if the folder where you want to put the folder is call "test"   the tuple should be ["test", "name of the folder"]
    """
    tg = node_to_put_the_folder.parmTemplateGroup()
    folder_found = tg.findFolder(in_this_folder)

    if folder_found is None:
        for index, item in enumerate(in_this_folder):
            if len(in_this_folder) == 1:
                prog_list = in_this_folder[0]
            else:
                prog_list = in_this_folder[0:index + 1]
            folder_found = tg.findFolder(prog_list)

            if folder_found is not None:
                last_folder_found = folder_found
            elif folder_found is None:
                folder_parm_template = hou.FolderParmTemplate(item, item)
                try:
                    tg.appendToFolder(last_folder_found, folder_parm_template)
                except:
                    pass
                    #	tg.append(folder_parm_template)
                last_folder_found = folder_parm_template
    #todo if folder not found  create it

    if insert_before_parm is not None:
        tg.insertBefore(insert_before_parm, last_folder_found)

    if insert_after_parm is not None:
        tg.insertAfter(insert_after_parm, last_folder_found)

    node_to_put_the_folder.setParmTemplateGroup(tg)









def parm_to_ui(node_to_put_the_parm, parm_to_add, in_this_folder=None, insert_before_parm=None, insert_after_parm=None,
               join_with_next_parm=False):
    """
    put a parm in the ui
    node = is the node where the parm will be added
    parm to add is the hou.###.ParmTemplate that will be added
    in_this_folder = tuple of the folders paths example. ['bla','ble'] where ble is inside bla.
    insertBefore_parm = will put the parm_to_add before this parm.
    insertAfter_parm = will put the parm_to_add after this parm.
    BEWARE you can only have,  in the args folder, or 	insertBefore_parm, or insertAfter_parm
    """
    #todo do a dummy invisible parameter that will work as buffer for set Next parm_to_add should be a list of parm, so the join with next works
    if join_with_next_parm is True:
        parm_to_add.setJoinWithNext(1)

    tg = node_to_put_the_parm.parmTemplateGroup()
    if in_this_folder is not None:
        try:
            tg_folder = tg.findFolder(in_this_folder)
            tg.appendToFolder(tg_folder, parm_to_add)
        except:

            print "folder doesnt exist you should run a function to create the folder if doesnt exist."
            ui_folder(node_to_put_the_parm, in_this_folder=in_this_folder)
            print in_this_folder
            tg_folder = tg.findFolder(in_this_folder[-1])
            print tg_folder
            tg.appendToFolder(tg_folder, parm_to_add)
            #print tg

    elif insert_before_parm is not None:
        tg.insertBefore(insert_before_parm, parm_to_add)
    elif insert_after_parm is not None:
        tg.insertAfter(insert_after_parm, parm_to_add)
    elif in_this_folder is None or insert_before_parm is None or insert_after_parm is None:
        tg.append(parm_to_add)
    try:
        node_to_put_the_parm.setParmTemplateGroup(tg)
    except:
        if type(parm_to_add) == hou.SeparatorParmTemplate:
            pass
        else:
            print "the parm name already exist, try using another name"
            print parm_to_add
            raise StandardError()

    return node_to_put_the_parm.parm(parm_to_add.name())













def promote_parm_to_ui(parm_to_add, node_to_put_the_parm, in_this_folder=None, insert_before_parm=None,
                       insert_after_parm=None, parm_name=None, parm_label=None, ch_link=True, join_with_next_parm=False,
                       minimum=None, maximum=None):
    """
    parm_to_add = is the parameter from the ui that we want to promote
    node_to_put_the_parm = the node where we want to send the parameter
    in_this_folder = will put it in that folder tuple of folders ["bla", "ble"]
    insertBefore_parm =  will put the created parameter before this parm
    insertAfter_parm =  will put the created parameter after this parm
        in case the parms all ready exist or the user want another name
    parm_name = the internal name fo the parm
    parm_label = how the name is display in the ui
    ch_link = channel link,  will create the link reference between promoted parm and original parm.
    join_with_next_parm if put the parm in the same line or not.
    """
    try:
        parm_to_add_template = parm_to_add.parmTemplate()
    except:
        print "make sure you are passing a parameter, and not a node or a class"
    #print type(parm_to_add_template), parm_to_add_template.name()

    if type(parm_to_add) == hou.Parm:
        if type(parm_to_add_template) == hou.RampParmTemplate:
            # if the parameter is a ramp
            ramp_parm_values = parm_to_add.evalAsRamp()
            ori_name = parm_to_add.name()
            ori_label = parm_to_add.description()
            parm_to_add_template = hou.RampParmTemplate(ori_name, ori_label, hou.rampParmType.Float,show_controls=False)
        elif type(parm_to_add_template) == hou.StringParmTemplate:
            parm_to_add_template.setDefaultValue(parm_to_add.evalAsString())

        else:
            try:
                parm_to_add_template.setDefaultValue([parm_to_add.eval()])
            except:
                parm_to_add_template.setDefaultValue(parm_to_add.eval())

    elif type(parm_to_add) == hou.ParmTuple:
        parm_to_add_template.setDefaultValue(parm_to_add.eval())

    if join_with_next_parm is True:
        parm_to_add_template.setJoinWithNext(True)
    if parm_name is not None:
        parm_to_add_template.setName(parm_name)
    if parm_label is not None:
        parm_to_add_template.setLabel(parm_label)
    if minimum is not None:
        parm_to_add_template.setMinValue(minimum)
    if maximum is not None:
        parm_to_add_template.setMaxValue(maximum)

    if in_this_folder is not None:
        ui_folder(node_to_put_the_parm, in_this_folder)

    parm_to_ui(node_to_put_the_parm, parm_to_add_template, in_this_folder=in_this_folder, insert_before_parm=insert_before_parm, insert_after_parm=insert_after_parm)

    # here we link the parameter
    if ch_link is True:
        if type(parm_to_add) == hou.Parm:
            # if the parameter is a ramp
            if type(parm_to_add_template) == hou.RampParmTemplate:
                tg = node_to_put_the_parm.parmTemplateGroup()
                parm_found = tg.find(parm_to_add_template.name() )
                rel_path = node_to_put_the_parm.relativePathTo(parm_to_add.node())
                parm_found.setScriptCallback("hou.pwd().node('%s').parm('%s').set(hou.pwd().parm('%s').evalAsRamp())" % ( rel_path, parm_to_add_template.name(), parm_to_add_template.name() ) )
                parm_found.setScriptCallbackLanguage(hou.scriptLanguage.Python)
                tg.replace(parm_to_add_template.name(), parm_found)
                node_to_put_the_parm.setParmTemplateGroup(tg)
                if parm_name is None:
                    node_to_put_the_parm.parm(ori_name).set(ramp_parm_values)
                if parm_name is not None:
                    node_to_put_the_parm.parm(parm_name).set(ramp_parm_values)
            else:
                parm_to_add.set(node_to_put_the_parm.parm( parm_to_add_template.name()))
            parm_to_add.pressButton()

        elif type(parm_to_add) == hou.ParmTuple:
            parm_to_add_length = parm_to_add_template.numComponents()
            if parm_to_add_length > 1:
                if str(parm_to_add.parmTemplate().namingScheme()) == "parmNamingScheme.XYZW":
                    cord = ["x", "y", "z", "w"]
                    for i in range(0, parm_to_add_length):
                        parm_to_add[i].set(node_to_put_the_parm.parm(parm_to_add_template.name() + cord[i]))
                else:
                    for i in range(0, parm_to_add_length):
                        parm_name = parm_to_add_template.name()+str(i+1)
                        parm_to_add[i].set(node_to_put_the_parm.parm(parm_name) )

            for i in range(0, parm_to_add_length):
                parm_to_add[i].pressButton()















def hide_folder_or_parm_from_ui(node_to_hide_the_parm, hide_this=[]):
    """
    node_to_hide_the_parm = is the node that we are going to hide the parameter
    hide_this=[]  = is the folder or parm that we want to hide form the UI use brackets for folders, strings for parms.
    """
    tg = node_to_hide_the_parm.parmTemplateGroup()
    #if its parm
    try:
        parm_template = tg.find(hide_this)
        parm_template.hide(True)
        tg.replace(hide_this, parm_template)
    # if its folder
    except:
        tg.hideFolder(hide_this, True)
    node_to_hide_the_parm.setParmTemplateGroup(tg)


def list_of_parms_to_promote_to_ui(list_of_nodes, list_of_desire_parms, node_to_parm=None, into_this_folder=[],
                                   separator_line=True):
    """
    @param list_of_nodes: list of the nodes that you want to loop
    @param list_of_desire_parms: list of the parameters of the nodes that you want to promote
    @param node_to_parm:  what the node where you want to promote this parameters
    @param into_this_folder: whats the folder where you want to put them
    @param separator_line:  will create a line after each node,   True or False
    @return:
    @example:
            hou_rig.utils.list_of_parms_to_promote_to_ui(nodes_trans_to_promote,
                                                     [["t", "tuple", "jwnp"],
                                                      ["r", "tuple", "jwnp"],
                                                      ["scale", "parm", "jwnp","label=this_is_label"]],
                                                     node_to_parm=node_to_put,
                                                     into_this_folder=folder_to_put_in+["Muscle Trans"])
    """
    #todo put a label in front of the separator_line with the name of the node
    for i in list_of_nodes:
        for j in list_of_desire_parms:
            if j[1] == "parm":
                parm = i.parm(j[0])
            elif j[1] == "tuple":
                parm = i.parmTuple(j[0])
            jwnp = False
            for itn in j:
                if itn == "jwnp":
                    # print itn
                    jwnp = True
                if "label" in str(itn):
                    label = itn.split("=")[1]
                else:
                    label = False

            if label is False:
                promote_parm_to_ui(parm,
                                   node_to_parm,
                                   in_this_folder=into_this_folder,
                                   parm_name=i.parent().name() + "_" + i.name() + "_" + j[0],
                                   ch_link=True,
                                   join_with_next_parm=jwnp)

            else:
                promote_parm_to_ui(parm,
                                   node_to_parm,
                                   in_this_folder=into_this_folder,
                                   parm_name=i.parent().name() + "_" + i.name() + "_" + j[0],
                                   parm_label=label,
                                   ch_link=True,
                                   join_with_next_parm=jwnp)

        if separator_line is True:
            loop = 0
            while True:
                try:
                    separator_parm = hou.SeparatorParmTemplate(
                        i.parent().name() + "_" + i.name() + "separator" + str(loop))
                    parm_to_ui(node_to_parm, separator_parm, in_this_folder=into_this_folder)
                    break
                except:
                    loop += 1





def togle_display_nodes(a_parameter, list_of_nodes):
    """
    will code into a parameter that turn on and off the display of a list of nodes.
    @param toggle_parameter: the parameter that will drive the script
    @param list_of_nodes: list of nodes that will be turn on and off with the parm
    @return:
    """

    for i in list_of_nodes:
        i.parm("tdisplay").set(1)
        i.parm("display").set(a_parameter)

#     rel_paths_to_nodes = []
#     parent = a_parameter.node()
#     for i in list_of_nodes:
#         rel_paths_to_nodes.append(parent.relativePathTo(i))
#
#     script = """rel_paths_to_nodes = %s
# if hou.pwd().parm('%s').eval() == 0:
#     for j in rel_paths_to_nodes:
#         hou.pwd().node(j).setDisplayFlag(0)
#
# elif hou.pwd().parm('%s').eval() == 1:
#     for j in rel_paths_to_nodes:
#         hou.pwd().node(j).setDisplayFlag(1)
#     """ % (rel_paths_to_nodes, a_parameter.name(), a_parameter.name())
#
#     parameter_template = a_parameter.parmTemplate()
#     parameter_template.setScriptCallbackLanguage(hou.scriptLanguage.Python)
#     parameter_template.setScriptCallback(script)
#     tg = parent.parmTemplateGroup()
#     tg.replace(a_parameter.name(), parameter_template)
#     parent.setParmTemplateGroup(tg)

def change_display_look(list_of_nodes, color=[0, 0.75, 0], viewport_selectable=True, geo_scale=1,
                        display_icon=0, control_type=0, orientation=0, shaded=False, keep_position=1):
    """
    change the display type of a null
    @param list_of_nodes: a list of the nodes to modify the display
    @return:
    """
    for i in list_of_nodes:
        try:
            i.parm("dcolorr").set(color[0])
            i.parm("dcolorr").set(color[1])
            i.parm("dcolorr").set(color[2])

            i.parm("picking").set(viewport_selectable)
            i.parm("geoscale").set(geo_scale)
            i.parm("displayicon").set(display_icon)
            i.parm("controltype").set(control_type)
            i.parm("orientation").set(orientation)
            i.parm("shadedmode").set(shaded)
        except:
            print "some parms dont exist"
            pass