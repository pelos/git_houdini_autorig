import hou
import utils

"""
##in houdini
from hou_rig import line_maker

name = "guide_curve"
centers = hou.selectedNodes()
if len(centers) <=0:
    print "Please select 3 or more nodes"
else:
    parent = centers[0]
    line_maker.create_line(parent, name, centers)
"""


def create_line(name, centers, where=None, name_of_node_to_merge="point1", basic_curve=False):
    """
    creates a line/curve from the incoming geometry, example select 2 nulls and will make a line from them.
    @param name: name of the created curve
    @param centers: a list of nodes
    @param where: where is going to place the curve
    @param name_of_node_to_merge: what the node inside the centers that will grab
    @param imp_normals: true or false if add extra stuff to the curve, (use for toon curve bones)
    @return: the created curve
    """
    level = centers[0].parent()
    if where is not None:
        level = centers[0].parent()

    curve = level.createNode("geo", name)
    curve.node("file1").destroy()
    curve.moveToGoodPosition()
    curve.setColor(hou.Color((.6, .6, 1)))
    #curve.parm("tdisplay").set(1)

    merge_node = curve.createNode("merge")

    add_all = curve.createNode("add", "add_generate_line")
    add_all.parm("stdswitcher1").set(1)
    add_all.parm("switcher1").set(1)
    add_all.setInput(0, merge_node, 0)

    convert_node = curve.createNode("convert", "convert_to_curve")
    convert_node.parm("totype").set(4)
    convert_node.setInput(0, add_all, 0)

    if basic_curve is False:
        convert_to_poly = curve.createNode("convert")
        convert_to_poly.setInput(0, convert_node, 0)

        switch_node = curve.createNode("switch")

        switch_node.setNextInput(convert_to_poly)
        switch_node.setNextInput(add_all)

        tg = curve.parmTemplateGroup()
        poly_toggle_parm = hou.ToggleParmTemplate("polywire", "polywire", 0)
        sc_toggle_parm = hou.ToggleParmTemplate("straight_curve", "Straight Curve", 0)
        sc_toggle_parm.setDefaultValue(True)
        wire_rad_parm = hou.FloatParmTemplate("wire_rad", "Wire Rad", 1)

        tg.insertBefore((0,), poly_toggle_parm)
        tg.insertBefore((0,), sc_toggle_parm)
        tg.insertBefore((0,), wire_rad_parm)

        curve.setParmTemplateGroup(tg)

        switch_node.parm("input").set(curve.parm("straight_curve"))

        wire_node = curve.createNode("polywire", "wire_view")
        curve.parm("wire_rad").set(0.05)
        wire_node.parm("radius").set(curve.parm("wire_rad"))
        wire_node.parm("div").set(6)

        wire_node.setInput(0, switch_node, 0)

        switch_poly = curve.createNode("switch", "switch_poly")
        switch_poly.setNextInput(switch_node)
        switch_poly.setNextInput(wire_node)
        switch_poly.parm("input").set(curve.parm("polywire"))

    null_out = curve.createNode("null", "OUT")
    null_out.setDisplayFlag(1)
    null_out.setRenderFlag(1)
    if basic_curve is True:
        null_out.setInput(0, convert_node)
    elif basic_curve is False:
        null_out.setInput(0, switch_poly)

    for i in centers:
        obj_merge = curve.createNode("object_merge", "object_merge_" + i.name())
        obj_merge.parm("xformtype").set(1)
        rel = obj_merge.relativePathTo(i)

        obj_merge.parm("objpath1").set(rel + "/" + name_of_node_to_merge)

        merge_node.setNextInput(obj_merge)

    # if imp_normals is True:
    #     curve_import_normals(curve)

    curve.layoutChildren()
    return curve