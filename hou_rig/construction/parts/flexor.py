import hou
import random
import hou_rig.utils

#todo different ways to generate the curve, points selected in the view port, we can use the for eyebrows for example.
#todo the bone length after been divided by the total amount of bones, should be multiply with a extra parm ratio
#todo set_bone_deform as argument, maybe we don't want to squash and stretch example eyebrows

# make a kind otl,  obj merge the curve inside the subnet and prep the curve there. and construct all inside the subnet
#then we can make a def to promote all the stuff of that subnet

class flexor(object):
    """
    for a given curve will create a chain of bones that follow that curve.
    """
    def __init__(self, a_curve):
        self.curve = a_curve

    def run_toon_curves(self, curve, bone_num=8, name_of_bones="chain_bone", where=None, viz=True):
        """
        run the necessary functions to get bones following a curve.
        @param curve: the curve that will work as back bone of the chain bones
        @param bone_num: how many bones will be created
        @param name_of_bones: if will serve to name each bone on the chain
        @param where: where are we creating the subnet, if any use the parent of the curve.
        @param name: name of system,  un use at the moment
        @param viz: if we want to create a chain of sphere to viz the stretch and squash of the system
        @return: a list of bones and the ik root
        """
        self.curve_subnet = self.curve_bones_subnet(curve, where=where)
        self.import_curve = self.bring_curve(curve, self.curve_subnet)
        self.prepare_curve(self.import_curve)

        list_chain = self.creating_bones_curve(self.import_curve, bone_num, name_of_bones, where=self.curve_subnet)
        ik_node = self.bones_follow_ik_curve(self.import_curve, list_chain[0], where=self.curve_subnet)


        self.set_bones_ik_solver(list_chain[0], ik_node)
        self.set_bone_length_parm(list_chain[0], self.import_curve)

        wt = self.set_bone_deform_region(list_chain[0], self.import_curve, name=name_of_bones, where=self.curve_subnet)
        merge_node = self.curve_world_position(self.import_curve, where=self.curve_subnet)

        self.point_att_to_parm(merge_node, list_chain[1].parm("tx"), attribute="P", point_num=0, vector=0)
        self.point_att_to_parm(merge_node, list_chain[1].parm("ty"), attribute="P", point_num=0, vector=1)
        self.point_att_to_parm(merge_node, list_chain[1].parm("tz"), attribute="P", point_num=0, vector=2)

        if viz is True:
            #viz_list = self.vizualize_stretch_and_squash(list_chain[0])
            n_out = self.vizualize_curve_stretch_and_squash(self.import_curve.node("OUT"))

        self.randomize_color_bone(list_chain[0])
        self.curve_subnet.layoutChildren()
        return list_chain

    def bring_curve(self, curve, where):
        """
        will objmerge the curve to somewhere else so we can use it as a separete part of code.
        that way we do not modify the original curve
        @param curve: the curve that we will be working with
        @param where: where are we copying the curve
        @return: the new curve object
        """
        imported_curve = where.createNode("geo", "import_"+curve.name() )
        imported_curve.node("file1").destroy()
        imp_obj_merge =imported_curve.createNode("object_merge")
        imp_obj_merge.parm("xformtype").set(1)
        imp_obj_merge.parm("objpath1").set(imp_obj_merge.relativePathTo(curve))
        imported_curve.parm("vm_renderable").set(0)
        imported_curve.parm("picking").set(0)

        return imported_curve

    def prepare_curve(self, curve):
        #todo we can remove the constants to add 1 and subtract 1
        """
        for a given curve will add extra nodes to use stretch and squash an attribute
        @param curve: the curve that will add the nodes
        @return:
        """
        for i in curve.children():
            if i.isRenderFlagSet() is True:
                null_out = i

        resample = curve.createNode("resample")
        resample.parm("last").set(1)
        resample.parm("length").set(0)
        resample.parm("dosegs").set(1)
        resample.parm("segs").set(15)
        resample.parm("dolength").set(0)
        # try:
        #     utils.promote_parm_to_ui(resample.parm("segs"), curve, insert_after_parm="wire_rad")
        # except:
        #     utils.promote_parm_to_ui(resample.parm("segs"), curve, insert_before_parm="stdswitcher5")
        resample.setInput(0, null_out)

        time_shift = curve.createNode("timeshift", "timeshift_rest")
        time_shift.parm("frame").setExpression("$FSTART")
        time_shift.setInput(0, resample)

        vopsop = curve.createNode("vopsop", "vopsop_streatch_and_squash")
        vopsop.setInput(0, resample)
        vopsop.setInput(1, time_shift)
        globals = vopsop.node("global1")

        itf = vopsop.createNode("inttofloat")
        itf.setInput(0, globals, 8)

        div = vopsop.createNode("divide")
        div.setInput(0, itf, 0)
        div.setInput(1, globals, 11)

        #-----------------------------
        ramp_stre = vopsop.createNode("rampparm", "ramp_stretch")
        ramp_stre.parm("parmname").set("stretch_ramp")
        ramp_stre.parm("parmlabel").set("Stretch Ramp")
        ramp_stre.parm("rampshowcontrolsdefault").set(0)
        ramp_stre.parm("ramptype").set(1)
        ramp_stre.parm("rampbasisdefault").set("catmull-rom")
        basis = hou.rampBasis.CatmullRom
        ramp_default = hou.Ramp((basis, basis, basis), (0, 0.5, 1), (0, 1, 0))
        vopsop.parm("stretch_ramp").set(ramp_default)

        ramp_stre.setInput(0, div, 0)

        stre_mult_parm = vopsop.createNode("parameter")
        stre_mult_parm.parm("parmname").set("stretch_ramp_mult")
        stre_mult_parm.parm("parmlabel").set("Stretch Ramp Mult")
        stre_mult_parm.parm("floatdef").set(1)
        stre_mult_parm.parmTuple("rangeflt").set([0, 10])

        stre_mult_parm.parm("joinnext").set(1)

        stre_mult = vopsop.createNode("multiply")
        stre_mult.setInput(0, ramp_stre)
        stre_mult.setInput(1, stre_mult_parm)

        stre_clamp_parm = vopsop.createNode("parameter")
        stre_clamp_parm.parm("parmname").set("stretch_cap")
        stre_clamp_parm.parm("parmlabel").set("Stretch Cap")
        stre_clamp_parm.parm("floatdef").set(20)
        stre_clamp_parm.parmTuple("rangeflt").set([0, 20])

        stre_clamp = vopsop.createNode("clamp", "clamp_cap_ramp")
        stre_clamp.setInput(0, stre_mult, 0)
        stre_clamp.setInput(2, stre_clamp_parm, 0)
        #-------------------------------------
        ramp_squa = vopsop.createNode("rampparm", "ramp_squash")
        ramp_squa.parm("parmname").set("squash_ramp")
        ramp_squa.parm("parmlabel").set("Squash Ramp")
        ramp_squa.parm("rampshowcontrolsdefault").set(0)
        ramp_squa.parm("ramptype").set(1)
        ramp_squa.parm("ramptype").set(1)
        ramp_squa.parm("rampbasisdefault").set("catmull-rom")
        vopsop.parm("squash_ramp").set(ramp_default)
        ramp_squa.setInput(0, div, 0)

        squa_mult_parm = vopsop.createNode("parameter")
        squa_mult_parm.parm("parmname").set("squash_ramp_mult")
        squa_mult_parm.parm("parmlabel").set("Squash Ramp Mult")
        squa_mult_parm.parm("floatdef").set(1)
        squa_mult_parm.parm("floatdef").set(1)
        squa_mult_parm.parmTuple("rangeflt").set([0, 10])
        squa_mult_parm.parm("joinnext").set(1)

        squa_mult = vopsop.createNode("multiply")
        squa_mult.setInput(0, ramp_squa)
        squa_mult.setInput(1, squa_mult_parm)

        squa_clamp_parm = vopsop.createNode("parameter")
        squa_clamp_parm.parm("parmname").set("squash_cap")
        squa_clamp_parm.parm("parmlabel").set("Squash Cap")
        squa_clamp_parm.parm("floatdef").set(2)
        squa_clamp_parm.parmTuple("rangeflt").set([0, 20])

        squa_clamp = vopsop.createNode("clamp", "clamp_cap_ramp")
        squa_clamp.setInput(0, squa_mult, 0)
        squa_clamp.setInput(2, squa_clamp_parm, 0)
        #---------------------------------------
        ori_len_parm = vopsop.createNode("parameter")
        ori_len_parm.parm("parmname").set("original_curve_len")
        ori_len_parm.parm("parmlabel").set("Original Curve Length")
        ori_len_parm.parm("floatdef").set(0)
        ori_len_parm.parm("joinnext").set(1)
        vopsop.parm("original_curve_len").setExpression('arclen(opinputpath(".",1),0,0,1)')

        current_len_parm = vopsop.createNode("parameter")
        current_len_parm.parm("parmname").set("current_curve_len")
        current_len_parm.parm("parmlabel").set("Current Curve Length")
        current_len_parm.parm("floatdef").set(0)
        vopsop.parm("current_curve_len").setExpression('arclen(opinputpath(".",0),0,0,1)')

        divi_len = vopsop.createNode("divide")
        divi_len.setInput(0, ori_len_parm, 0)
        divi_len.setInput(1, current_len_parm, 0)

        cons = vopsop.createNode("addconst")
        cons.parm("addconst").set(-1)
        cons.setInput(0, divi_len, 0)

        compare = vopsop.createNode("compare")
        compare.setInput(0, ori_len_parm)
        compare.setInput(1, current_len_parm)
        compare.parm("cmp").set("gt")

        two_ways = vopsop.createNode("twoway")
        two_ways.parm("condtype").set(0)
        two_ways.setInput(0, compare, 0)
        two_ways.setInput(1, squa_clamp, 0)
        two_ways.setInput(2, stre_clamp, 0)

        mult_cons_two = vopsop.createNode("multiply")
        mult_cons_two.setInput(0, cons, 0)
        mult_cons_two.setInput(1, two_ways, 0)

        cons_one = vopsop.createNode("addconst")
        cons_one.parm("addconst").set(1)
        cons_one.setInput(0, mult_cons_two, 0)

        bind_export = vopsop.createNode("bind")
        bind_export.parm("parmname").set("bscale")
        bind_export.parm("useasparmdefiner").set(1)
        bind_export.parm("exportparm").set(2)
        bind_export.setInput(0, cons_one)

        vopsop.layoutChildren()
        #after we get the original length of the curve delete the connection so we dont depend on the timeshift.
        vopsop.parm("original_curve_len").deleteAllKeyframes()
        #-----------------------------------------

        pw = curve.createNode("pointwrangle", "pointwrangle_make_local_variable")
        pw.parm("snippet").set("f@bscale = @bscale; addvariablename('bscale', 'BSCALE');")
        pw.setInput(0, vopsop)

        carve_node = curve.createNode("carve")
        carve_node.setInput(0,pw)
        carve_node.parm("firstu").set(0)
        carve_node.parm("secondu").set(1)
        carve_node.parm("domainu2").set(1)
        carve_node.bypass(1)

        null_out = curve.createNode("null", "OUT")
        null_out.setInput(0, carve_node)
        null_out.setDisplayFlag(1)
        null_out.setRenderFlag(1)

        curve.layoutChildren()
        return curve

    def vizualize_curve_stretch_and_squash(self, node_to_connect):
        parent = node_to_connect.parent()

        pw_node = parent.createNode("polywire")
        pw_node.parm("radius").setExpression('point(opinputpath(".", 0), $PT, "bscale", 0)*.075')
        pw_node.parm("div").set(6)

        n_out = parent.createNode("null", "OUT_viz")
        switch_node = parent.createNode("switch")

        pw_node.setInput(0, node_to_connect)
        switch_node.setInput(0, node_to_connect)
        switch_node.setInput(1, pw_node)

        n_out.setInput(0, switch_node)
        n_out.setDisplayFlag(1)
        n_out.setRenderFlag(1)

        parent.layoutChildren()
        return n_out

    def promote_shape_parms(self, curve, node_to_promote_parms, folder=["Transform"], name=""):
        """
        will promote the attributes of the curve to a given node, into a given  ui folder
        @param curve: the curve node that we will use
        @param node_to_promote_parms: whats the node where are we going to put all the parameters
        @param folder: in what folder tuple are we going to implement the promoted parameters
        @param name: name of the parameter, (important so doesnt clash with other limbs)
        @return:
        """

        hou_rig.utils.promote_parm_to_ui(curve.node("vopsop_streatch_and_squash").parm("stretch_ramp"),
                                         node_to_promote_parms,
                                         in_this_folder=folder,
                                         parm_name=name+"_stretch_ramp")

        hou_rig.utils.promote_parm_to_ui(curve.node("vopsop_streatch_and_squash").parm("stretch_ramp_mult"),
                                         node_to_promote_parms,
                                         in_this_folder=folder,
                                         join_with_next_parm=True,
                                         parm_name=name+"_stretch_ramp_mult")

        hou_rig.utils.promote_parm_to_ui(curve.node("vopsop_streatch_and_squash").parm("stretch_cap"),
                                         node_to_promote_parms,
                                         in_this_folder=folder,
                                         parm_name=name+"_stretch_cap")
        # #-----------------------------------------------------------------------------------------------
        hou_rig.utils.promote_parm_to_ui(curve.node("vopsop_streatch_and_squash").parm("squash_ramp"),
                                         node_to_promote_parms,
                                         in_this_folder=folder,
                                         parm_name=name+"_squash_ramp")

        hou_rig.utils.promote_parm_to_ui(curve.node("vopsop_streatch_and_squash").parm("squash_ramp_mult"),
                                         node_to_promote_parms,
                                         in_this_folder=folder,
                                         join_with_next_parm=True,
                                         parm_name=name+"_squash_ramp_mult")

        hou_rig.utils.promote_parm_to_ui(curve.node("vopsop_streatch_and_squash").parm("squash_cap"),
                                         node_to_promote_parms,
                                         in_this_folder=folder,
                                         parm_name=name+"_squash_cap")

        dcurve_toggle = hou.ToggleParmTemplate(name+"_display_curve", "Display Curve", default_value=False)
        promoted_dcurve_toggle = hou_rig.utils.parm_to_ui(node_to_promote_parms, dcurve_toggle, in_this_folder=folder)
        hou_rig.utils.togle_display_nodes(promoted_dcurve_toggle, [curve])

        if curve.node("OUT_viz"):
            sq_curve_toggle = hou.ToggleParmTemplate(name+"_display_stretch_and_squash", "Display Stretch and Squash", default_value=False)
            promoted_sq_curve_toggle = hou_rig.utils.parm_to_ui(node_to_promote_parms, sq_curve_toggle, in_this_folder=folder)
            curve.node("switch1").parm("input").set(promoted_sq_curve_toggle)

    def point_att_to_parm(self, node_with_att, parm, attribute="P", point_num=0, vector=0):
        """
        transfer the attribute of a node to a parameter
        @param node_with_att: whos the node that we want to check
        @param parm: whats the parameter we want to override
        @param attribute: the attribute that we want to extract
        @param point_num: the number of the point we are looking at, can be 0, 1 or $PT
        @param vector: the vector we want to get 0=x, 1=y, 2=z
        @return:
        """
        #we might be able to remove the arg node_with_att since we can take it from parm.node()
        parm.setExpression("point('"+parm.node().relativePathTo(node_with_att)+"'"+","+str(point_num)+","+"'"+attribute+"'"+","+str(vector)+")")

    def curve_bones_subnet(self, curve, where=None, name=None):
        """
        create a subnet where the created nodes will be created
        @param curve: the curve that will be use
        @param where: if we want to put this subnet somewhere else.
        @return: the subnet
        """
        if where is None:
            where = curve.parent()
        if name is not None:
            curve_subnet = where.createNode("subnet", name)
        elif name is None:
            curve_subnet = where.createNode("subnet", curve.name()+"_flexor")
        curve_subnet.setPosition([curve.position()[0], curve.position()[1]-1])

        return curve_subnet

    def fetch_parent(self, where, parent):
        #we don't use this any more since we are not using the fetch
        #deprecated on favor of using the root with a point expression.
        return
        fetch = where.createNode("fetch", "fetch_"+parent.name())
        fetch.parm("fetchobjpath").set(fetch.relativePathTo(parent))
        fetch.parm("useinputoffetched").set(1)
        fetch.parm("fetchsubnet").set(1)
        fetch.setDisplayFlag(0)
        return fetch

    def creating_bones_curve(self, curve, bone_num, name_of_bones="chain_bone", where=None, set_tip=True):
        """
        generate a chain of
        curve: the curve that will be populated with bones
        int@bone_num: how many bones will be created.
        str@name_of_bones: names that the bones
        tuple@color: tuple of color,[0.2,0.5,0.35] colorize the created bone nodes.

        returns, the created list of bones, the ik_root
        """
        mp = curve.position()
        if where is None:
            where = curve.parent()

        ik_root = where.createNode("null", name_of_bones+"_root")
        ik_root.setPosition([mp[0]+1, mp[1]-1])
        ik_root.setDisplayFlag(0)
        mp = [ik_root.position()[0], ik_root.position()[1]-1]

        #list_chain = [ik_root]
        list_chain = []

        for i in range(0, bone_num):
            bone = where.createNode("bone", name_of_bones+"_"+str(i))
            bone.setPosition([mp[0], mp[1]-i])
            list_chain.append(bone)
            if i == 0:
                bone.setInput(0, ik_root)
            else:
                bone.setInput(0, prev_bone)
            prev_bone = bone

        if set_tip is True:
            tip = self.creating_tip_of_chain(list_chain[-1])
            #list_chain.append(tip)
        return list_chain, ik_root, tip

    def creating_tip_of_chain(self, node_to_connect_the_tip):
        parent = node_to_connect_the_tip.parent()
        tip = parent.createNode("null", node_to_connect_the_tip.name())
        tip.setInput(0, node_to_connect_the_tip)
        rel_path = tip.relativePathTo(node_to_connect_the_tip)
        rel_path = "ch('"+rel_path+"/length')"
        tip.parm("tz").setExpression(rel_path+"*-1")

        # tip.parm("geoscale").setExpression(rel_path)
        # tip.parm("geoscale").pressButton()
        #tip.parm("geoscale").deleteAllKeyframes()

        tip.parm("geoscale").set(0.1)
        tip.parm("controltype").set(1)
        tip.setDisplayFlag(0)

        return tip

    def bones_follow_ik_curve(self, curve, chain=[], root_bone=None, end_bone=None, where=None):
        """
        will create a series of bones in a chain that follows the path of a curve
        @param curve: the curve that the bones will follow
        @param chain: the chain of bones that will follow
        @param root_bone: the root where they will start to follow the curve
        @param end_bone:  the end bone where they will follow the curve
        # we might not want all the bones to follow the curve
        @param where:  where are we creating the chop network
        @return: the ik chopsolver
        """
        if where is None:
            where = curve.parent()

        chop = where.createNode("chopnet", "ik_chopnet")
        chop.setPosition([curve.position()[0]-1.5, curve.position()[1]-1.5])
        ik = chop.createNode("inversekin", "inversekin_ik_chopnet")
        ik.parm("solvertype").set(4)
        ik.parm("curvepath").set(ik.relativePathTo(curve)+"/OUT")

        if root_bone is not None:
            ik.parm("bonerootpath").set(ik.relativePathTo(root_bone))
        else:
            for n in chain:
                if n.type().nameComponents()[2] == "bone":
                    ik.parm("bonerootpath").set(ik.relativePathTo(n))
                    break
                else:
                    continue

        if end_bone is None:
            end_bone = chain[-1]
        ik.parm("boneendpath").set(ik.relativePathTo(end_bone))

        return ik

    def set_bones_ik_solver(self, chain, solver_node):
        """
        put the ik_solver chop into the parameter of the bones
        """
        for i in chain:
            try:
                i.parm("solver").set(i.relativePathTo(solver_node))
            except:
                pass

    def set_bone_length_parm(self, chain, curve):
        """
        set the length of the bones to stretch according the the curve.
        """
        amount_of_bones = len(chain)
        for i in chain:

            i.parm("length").setExpression('arclen("%s",0,0,1)/%s' % (i.relativePathTo(curve)+"/OUT", amount_of_bones))

    def curve_world_position(self, curve, name=None, where=None):
        if name is None:
            name = curve.name()

        if where is None:
            where = curve.parent()

        if where.node(name+"_world_transform"):
            wt = where.node(name+"_world_transform")
        else:
            wt = where.createNode("geo", name+"_world_transform")
            wt.setDisplayFlag(0)
            wt.node("file1").destroy()

        merge = wt.createNode("object_merge", name)
        merge.parm("xformtype").set(1)
        merge.parm("objpath1").set(merge.relativePathTo(curve)+"/OUT")

        return merge

    def set_bone_deform_region(self, chain, curve, name=None, where=None):
        """
        creates a geometry that just brings the bones as point, to use as helper to get the
        bone position in world space
        where = what level inside houdini the object world transform helper will be created
        chain = list of bones that will get the parm
        name the name of the world transform helper

        returns wt geometry node.
        """
        if name is None:
            name = curve.name()

        if where is None:
            where = curve.parent()

        wt = where.createNode("geo", name+"world_transform")
        wt.node("file1").destroy()
        wt.setPosition([curve.position()[0]-1.5, curve.position()[1]-1])
        wt.setDisplayFlag(0)
        merge_nodes=[]
        for i in chain:
            if i.type().nameComponents()[2]== "bone":
                merge = wt.createNode("object_merge", i.name())
                merge.parm("xformtype").set(1)
                merge.parm("objpath1").set(merge.relativePathTo(i))
                merge_nodes.append(merge)

        for i, j in zip(chain, merge_nodes):
            rel_path = i.relativePathTo(curve)
            wt_rel_path = i.relativePathTo(j)

            i.parm("crscalex").setExpression('point("%s",nearpoint("%s", point("%s", 0, "P", 0), point("%s", 0, "P", 1), point("%s", 0, "P", 2) ), "bscale", 0)'%(rel_path, rel_path, wt_rel_path, wt_rel_path, wt_rel_path))
            i.parm("crscaley").setExpression('point("%s",nearpoint("%s", point("%s", 0, "P", 0), point("%s", 0, "P", 1), point("%s", 0, "P", 2) ), "bscale", 0)'%(rel_path, rel_path, wt_rel_path, wt_rel_path, wt_rel_path))

        wt.layoutChildren()
        return wt

    def randomize_color_bone(self, chain):
        """
        do to a chain of nodes will randomize the wire frame color
        """
        for i in chain:
            i.parm("dcolorr").set(random.random())
            i.parm("dcolorg").set(random.random())
            i.parm("dcolorb").set(random.random())

    def vizualize_stretch_and_squash(self, chain, where=None):
        """
        for a given chain of bones, visualize the amount of stretch and squash
        @param chain: chain of bones
        @return: a chain of visualizers spheres
        """

        # if where is not None:
        #     parent = where
        # else:
        #     parent = chain[0].parent()
        #
        # viz_subnet = parent.createNode("subnet")
        # viz_subnet.setName("subnet_viz_chain")
        # viz_subnet.parm("tdisplay").set(1)
        # viz_subnet.parm("display").set(0)
        # vizer_list = []
        # for i in chain:
        #     fetcher = viz_subnet.createNode("fetch", "fetch_"+i.name())
        #     fetcher.setColor(hou.Color((1.0, 0.4, 0.0)))
        #     fetcher.parm("useinputoffetched").set(1)
        #     fetcher.parm("fetchsubnet").set(1)
        #     fetcher.parm("fetchobjpath").set(fetcher.relativePathTo(i))
        #     fetcher.setDisplayFlag(0)
        #
        #     vizer = viz_subnet.createNode("geo", "visualize_"+i.name())
        #     vizer.node("file1").destroy()
        #     vizer.createNode("sphere")
        #
        #     vizer.parm("scale").set(i.parm("crscalex") )
        #     vizer.parm("sx").set(0.025)
        #     vizer.parm("sy").set(0.025)
        #     vizer.parm("sz").set(0.025)
        #
        #     vizer.setInput(0, fetcher)
        #     vizer_list.append(vizer)
        # viz_subnet.layoutChildren()
        #
        # return vizer_list
