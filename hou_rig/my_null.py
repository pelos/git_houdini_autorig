import hou


def my_null(parent, name):
    null = parent.createNode("geo", name)

    #creating the nodes inside for display
    null.node("file1").destroy()
    control = null.createNode("control")
    control.parm("scale").set(.1)
    trans = null.createNode("xform", "xform")
    #trans.parm("sy").set(.2)
    trans.setNextInput(control)
    trans.setDisplayFlag(1)
    trans.setRenderFlag(1)

    null_out = null.createNode("null", "Out")
    null_out.setNextInput(trans)
    null_out.setDisplayFlag(1)
    null_out.setRenderFlag(1)

    p1 = null.createNode("add", "point1")
    p1.parm("usept0").set(1)

    #creating the attributes at upper level
    tg = null.parmTemplateGroup()

    cd = hou.FloatParmTemplate("color", "Color", 3, default_value=([1, 1, 1]), min=0, max=10, min_is_strict=False,
                               max_is_strict=False, look=hou.parmLook.ColorSquare,
                               naming_scheme=hou.parmNamingScheme.RGBA)
    tg.appendToFolder("Misc", cd)
    sc = hou.FloatParmTemplate("geoscale", "Scale", 1, default_value=([1]), min=0, max=10, min_is_strict=False,
                               max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
    tg.appendToFolder("Misc", sc)
    display_icon = hou.MenuParmTemplate("displayicon", "Display", menu_items=(["icon", "axis", "iconandaxis"]),
                                        menu_labels=(["Icon", "Axis", "Icon and Axis"]), default_value=0,
                                        icon_names=([]), item_generator_script="",
                                        item_generator_script_language=hou.scriptLanguage.Python,
                                        menu_type=hou.menuType.Normal)
    tg.appendToFolder("Misc", display_icon)
    ct = hou.MenuParmTemplate("controltype", "Control Type",
                              menu_items=(
                              ["null", "circles", "box", "planes", "nullandcircles", "nullandbox", "nullandplanes",
                               "custom"]),
                              menu_labels=(["Null", "Circles", "Box", "Planes", "Null and Circles", "Null and Box",
                                            "Null and Planes", "Custom"]),
                              default_value=2,
                              icon_names=([]), item_generator_script="",
                              item_generator_script_language=hou.scriptLanguage.Python,
                              menu_type=hou.menuType.Normal)
    tg.appendToFolder("Misc", ct)
    ori = hou.MenuParmTemplate("orientation", "Orientation", menu_items=(["xyz", "x", "y", "z", "xy", "xz", "yz"]),
                               menu_labels=(
                               ["All planes", "YZ plane", "ZX plane", "XY plane", "YZ, ZX planes", "YZ, XY planes",
                                "ZX, XY planes"]), default_value=0, icon_names=([]), item_generator_script="",
                               item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    tg.appendToFolder("Misc", ori)
    sm = hou.ToggleParmTemplate("shadedmode", "Shaded Mode", default_value=False)
    tg.appendToFolder("Misc", sm)
    null.setParmTemplateGroup(tg)

    #linking the parms
    control.parm("colorr").set(null.parm("colorr"))
    control.parm("colorg").set(null.parm("colorg"))
    control.parm("colorb").set(null.parm("colorb"))

    control.parm("scale").set(null.parm("geoscale"))

    control.parm("displayicon").set(null.parm("displayicon"))

    control.parm("controltype").set(null.parm("controltype"))

    control.parm("orientation").set(null.parm("orientation"))

    control.parm("shadedmode").set(null.parm("shadedmode"))

    null.layoutChildren()
    return null