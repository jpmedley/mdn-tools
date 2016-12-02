#!/usr/bin/python

# mdn template -i interface -m member -t template
# mdn templates -i interface -a template member [template member]1 ... [template member]n

# Shared:Interface

import os
import re
import sys

data = {}

def CreateFile(data):
	re_token = re.compile(r"(\[\[([\w\-\_:]+)\]\])")
	here = os.path.dirname(os.path.realpath(__file__))
	tempPath = os.path.join(here, (data['Template'] + ".html"))
	outPath = os.path.join(here, "out", (data['Member'] + ".html"))

	tempFile = open(tempPath, 'r')
	outFile = open(outPath, 'w')

	question = "What is the value of %s?\n"

	for line in tempFile:
		tokens = re.findall(re_token, line)
		if (tokens != None) and (len(tokens) > 0):
			for i in range(0, len(tokens)):
				token = tokens[i][0]
				key = tokens[i][1]
				if (not key in data):
					response = raw_input(question % key)
					data.update({key: response})
					print
				line = line.replace(token, data[key])
		outFile.write(line)

	tempFile.close()
	outFile.close()
	return data



def GetInterfaceData(idl_file):
	if ( not os.path.isfile(idl_file) ):
		raise Exception("File %s not found." % idl_file)
	f = open(idl_file, 'r')
	idl_contents = f.read()
	re_members = [r"(readonly )?(attribute )?(\w+\??)\s(\w+);$", r"\[[^\]]+\]\s(\w+\s)(\w+\(\));$"]
	re_interface = re.compile(r"(interface[^:]+:[^{]+)({[^}]+})")
	idl = re_interface.findall(idl_contents)
	if idl:
		# print idl[0][1]
		interface = idl[0][0]
		members = idl[0][1]
		# print members
		interface_name = interface.partition(' ')[2]
		data.update({'Interface': interface_name})

		temp = {}
		data.update({'Properties': []})
		data.update({'Methods': []})
		for re_member in re_members:
			rem = re.compile(re_member, re.M)
			# print rem
			member_list = rem.findall(members)
			# print member_list
			for member in member_list:
				# print("MEMBER:", member, member[1])
				if member[1] == 'attribute ':
					temp.update({'Readonly': member[0], 'Type': member[2], 'Name': member[3]})
					data['Properties'].append(temp)
					temp = {}
				else:
					temp.update({'Return': member[0], 'Name': member[1]})
					data['Methods'].append(temp)
					temp = {}
		return data



def ProcessIdl(idl_file):
	idl_data = GetInterfaceData(idl_file)
	# print data
	# START HERE: Shared items need to persist between iterations, but other items should not.
	data = {"Shared:Interface": idl_data['Interface']}
	print ("Creating file for %s." % data['Member'])
	data = CreateFile(data)
	print idl_data['Properties']
	for a_property in idl_data['Properties']:
		print '  ', a_property
		data.update({'Member': a_property['Name']})
		data.update({'Template': 'property'})
		data.update({'ReadOnly': a_property['Readonly']})
		data.update({'Return': a_property['Type']})
		print ("Creating file for %s." % data['Member'])
		data = CreateFile(data)
	print idl_data['Methods']
	for a_member in idl_data['Methods']:
		print '  ', a_member
		data.update({'Member': a_member['Name']})
		data.update({'Return': a_member['Return']})
		print ("Creating file for %s." % data['Member'])
		data = CreateFile(data)


if sys.argv[1] == 'template':
	if len(sys.argv) < 8:
		raise Exception("Wrong nubmer of arguments")
	if (sys.argv[2] != '-i') or (sys.argv[4] != '-m') or (sys.argv[6] != '-t'):
		raise Exception("Unsupported argument found. Arguments must be -i, -m and -t in that order.")
	data = {'Shared:Interface': sys.argv[3], 'Member': sys.argv[5], 'Template': sys.argv[7]}
	CreateFile(data)


elif sys.argv[1] == 'templates':
	if (sys.argv[2] != '-i') or (sys.argv[4] != '-a'):
		raise Exception("Unsupported argument found. Arguments must be -i, -m and -t in that order.")
	data = {'Interface': sys.argv[3]}
	while len(sys.argv) > 5:
		#data.update({key: response})
		for key in data.keys():
			if not "Shared:" in key:
				del data[key]
		data.update({'Member': sys.argv[len(sys.argv) - 1]})
		sys.argv.pop()
		data.update({'Template': sys.argv[len(sys.argv) - 1]})
		sys.argv.pop()
		print ("Creating file for %s." % data['Member'])
		data = CreateFile(data)

elif sys.argv[1] == 'idl':
	here = os.path.dirname(os.path.realpath(__file__))
	infile = os.path.join(here, 'in', 'Sensor.idl')
	ProcessIdl(infile)

else:
	raise Exception("Unrecognized command.")


