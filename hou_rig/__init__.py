""" in houdini shelf
import hou_rig
reload(hou_rig)
hou_rig.rel_modules(hou_rig.__path__[0], "hou_rig")
#hou_rig.loadSubModules(hou_rig.__path__[0], "hou_rig")
print "\n"*5
"""

import os

def rel_modules(path, Main_Module):
	for root, dirs, filesNames in os.walk(path):
		for i in filesNames:
			if i.endswith(".py"):
				if i == "__init__.py":
					subModuleName = str(Main_Module)
				else:
					subModuleName = str(Main_Module) + "." + i.split(".")[0]
				try:
					module = __import__( subModuleName, globals(), locals(), ["*"], -1 )
					reload(module)
					print "Reloaded: " + subModuleName
				except ImportError, e:
					for arg in e.args:
						print( arg )
				except Exception, e:
					for arg in e.args:
						print( arg )
		for dirName in dirs:
			rel_modules( os.path.join( path, dirName ), ".".join( [ Main_Module, dirName ] ) )
		break