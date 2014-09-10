import hou
import single


#class leg(single.single, object):
class arm(single.single):
	def __init__(self, node, rig_subnet):
		self.node = node
		self.rig_subnet = rig_subnet

		# calling class single nit method
		super(arm, self).__init__(self.node, self.rig_subnet)
		#print "hello"




