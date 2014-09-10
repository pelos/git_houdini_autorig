#reason of this class is because pathcv in houdini doesnt let you change the scale of the vizualization

import hou
import hou_rig.utils


class My_path_cv(object):
    def __init__(self, where=hou.node("/obj"), name="null_cv"):
        self.where = where
        self.name = name
        self.path_cv = self.create_path_null(where=self.where)

    def create_path_null(self, where=hou.node("/obj")):
        path_cv = where.createNode("null", self.name)
        p1 = path_cv.node("point1")

        at_it = path_cv.createNode("attribcreate", "attribcreate_initial_twist")
        at_it.parm("name1").set("initial_twist")
        #hou_rig.utils.promote_parm_to_ui() didn't work because attribute create its Always tuple 4 parm length
        initial_twist_pt = hou.FloatParmTemplate("initialtwist", "Initial Twist", 1, default_value=([0]), min=0, max=10)
        hou_rig.utils.parm_to_ui(path_cv, initial_twist_pt, in_this_folder=["Misc"])
        at_it.parm("value1v1").setExpression('ch("../initialtwist")')

        at_it.setInput(0, p1)

        at_twist = path_cv.createNode("attribcreate", "attribcreate_twist")
        at_twist.parm("name1").set("twist")
        at_twist.parm("value1v1").setExpression("ch('../rz')")
        at_twist.setFirstInput(at_it)

        pn = path_cv.createNode("point", "point_normal")
        pn.parm("donml").set("on")
        pn.parmTuple("n").deleteAllKeyframes()
        pn.parmTuple("n").set([0, 1, 0])
        pn.setInput(0, at_twist)

        null_out = path_cv.createNode("null", "Out")
        null_out.setNextInput(pn)
        null_out.setRenderFlag(1)

        path_cv.layoutChildren()
        return path_cv