import hou
import master



class leg(master.master):
	def __init__(self, node, rig_subnet):
		self.node = node
		self.rig_subnet = rig_subnet

		# calling class single init method
		#super(leg, self).__init__(self.node, self.rig_subnet)

		self.create_spare_parms()
		self.create_bones(self.node, self.rig_subnet)
		self.create_ik()
		self.create_stretche_leg()
		self.ik_stretchy_knee_slide()
		self.destroy_last_bone()



#here we need to overright the ik stretchy knee to work on 2 bones
# and later on work with 3 bones as a dog leg