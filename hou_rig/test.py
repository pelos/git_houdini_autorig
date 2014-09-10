# import hou
# file = "C:\Users\dk\Desktop\Flabio_Hair_System/hair_wet_002.hip"
# #hou.hipFile.load("C:\Users\dk\Desktop\Flabio_Hair_System\\flabio_demostration_V002.hip")
#
# hou.hipFile.load(file)
#
# print hou.node("obj").children()
#
# mantra_node = hou.node("/out").children()[0]
# mantra_node.parm("execute").pressButton()
#
# print file
# bla = raw_input()

#--------------------------------------------------
# check year of the movie folder
# import os
# import sys
# import re
# folder = "L:\Backup\Movies"
# j = os.listdir(folder)
# for i in j:
#     if re.search("\d{4}", i) and "1080" not in i:
#         print i
#-------------------------------
#put some files into smaller sections of folders
# import shutil
# import os
# folderr = "E:\Reter\Pic\safe\\testa"
#
# print folderr
#
# fs = os.listdir(folderr)
# limitt = 35000
# count = 0
# os.makedirs(folderr+"\\bla0")
# ftm = folderr+"\\bla0"
#
# for index, i in enumerate(fs):
#     fpath = os.path.join(folderr, i)
#     if os.path.isfile(fpath):
#         shutil.move(fpath, ftm)
#
#     if index%limitt == 0:
#         count = count+1
#         os.makedirs(folderr+"\\bla"+str(count))
#         ftm = folderr+"\\bla"+str(count)
#
#     # if count >4:
#     #     break


# remove duplicated if they have (1) in file name
# import os
# foldd = "E:\Reter\Pic\New"
# lll = os.listdir(foldd)
# print len(lll)
# print lll
# for i in lll:
#     fp = os.path.join(foldd, i)
#     print fp
#     if "(1)" in fp:
#         os.remove(fp)

# l = range(0,5000)
# g=[]
# for i in l:
#     if 1000/(i+1) == 0:
#         g.append(i)
#
# print len(g)


import os
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--path", help="path that the tool will walk down reading all the files", default=".")
parser.add_argument("-w", "--walk", help="if walk down the folder scructure", default="False")
parser.add_argument("-d", "--delete", help="will delete the duplicated file", default="False")
args = parser.parse_args()

print "Folder Path to Walk: " +args.path
print "Delete Function: "+str(args.delete)
print "walk is: "+str(args.walk)

sys.path.append("C:\Python27\Lib\site-packages\PIL")
import Image
import ImageChops

def delete_duplicated(pathh):
    space_to_free = 0
    list_files = []
    pathh = str(args.path)

    if args.walk == "False":
        for i in os.listdir(pathh):
            fp = os.path.join(pathh, i)
            if os.path.isfile(fp):
                list_files.append(fp)

    elif args.walk == "True":
        for root, dirs, files in os.walk(pathh):
            for j in files:
                fp = os.path.join(root, j)
                list_files.append(fp)

    dup = list_files
    for i in list_files:
        dup.remove(i)
        for j in list_files:
            try:
                i_space = os.path.getsize(i)
                j_space = os.path.getsize(j)
                if i_space == j_space and i != j:
                    ii = Image.open(i)
                    ji = Image.open(j)
                    chop = ImageChops.difference(ii, ji)
                    if chop.getbbox() is None:
                        print i+"\t\t<--"+str(i_space)+"-->\t\t"+j
                        space_to_free = space_to_free + i_space
                        if args.delete == "True":
                            #print "file was deleted" + j
                            os.remove(j)
            except:
                pass
    print "\namount of space liberated: " + str(space_to_free>>20) + "megs aprox"
delete_duplicated(args.path)