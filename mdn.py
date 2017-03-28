#!/usr/bin/python

# mdn template -i interface -m member -t template
# mdn templates -i interface -a member template [member template]1 ... [member template]n
# mdn idl -f [idl_file | idl_folder]
# mdn idl -l [idl_file | idl_folder]

# ToDos:
#  Deal with inheritance from EventTarget: https://developer.mozilla.org/en-US/docs/Web/API/BroadcastChannel

import os
import re
import sys

#{'Shared:Item1': text,
#  'Shared:Item2': text,
#  'SomeMethodName': {'Key':'Value'}
#}

here = os.path.dirname(os.path.realpath(__file__))
# re_token = re.compile(r"(\[\[([\w\-\_:]+)\]\])") # v1
re_token = re.compile(r"(\[\[(\w+:?[^]]+)\]\])")

def getTemplate(name):
	fileObj = open(os.path.join(here, 'templates', (name + '.frag')), 'r')
	fileCnts = fileObj.read()
	fileObj.close()
	return fileCnts

ddTemplate = getTemplate('dd')
dlTemplate = getTemplate('dl')

def CreateFile(template, member, data):
	# print("[Creating File]", template, member, data)
	tempPath = os.path.join(here, 'templates', (template + ".html"))
	outPath = os.path.join(here, "out", member.partition('()')[0] + ".html")

	tempFile = open(tempPath, 'r')
	outFile = open(outPath, 'w')

	question = "\nWhat is the value of {0} for {1}?\n"

	for line in tempFile:
		tokens = re.findall(re_token, line)
		if (tokens != None) and (len(tokens) > 0):
			for i in range(0, len(tokens)):
				# Hint: token = [[ + key + ]]
				token = tokens[i][0]
				key = tokens[i][1]
				if ('Shared:' in key):
					if (not key in data):
						q = key.partition(':')[2]
						response = raw_input(question.format(q, member))
						data.update({key: response})
					line = line.replace(token, data[key])
					# print data[key]
				elif ('yn:' in key):
					statements = key.split(';')
					ynquestion = statements[0].partition(':')[2]
					if ynquestion.startswith("'") or ynquestion.startswith('"'):
						ynquestion = ynquestion[1:-1]
					response = raw_input('\n' + ynquestion).upper()
					if response == 'N':
						line = statements[2]
					else:
						line = statements[1]
				else:
					if (not member in data):
						data[member] = {'Member': member}
					if (not key in data[member]):
						response = raw_input(question.format(key, member))
						data[member].update({key: response})
					line = line.replace(token, data[member][key])
					# print data[member][key]
		outFile.write(line)

	tempFile.close()
	outFile.close()

	return data


def CreateFilesFromArgs(args):
	data = {'Shared:Interface': args[3]}
	# CreateFile(template, member, data):
	while len(args) > 5:
		#  -i interface -a member template 
		template = args[len(args) - 1]
		args.pop()
		member = args[len(args) - 1]
		args.pop()
		data = CreateFile(template, member, data)
	return data

def CreateFilesFromData(data):
	# CreateFile(template, member, data)
	data = CreateFile('interface', data['Shared:Interface'], data)
	for key in data:
		if 'Member' in data[key]:
			if 'Property' in data[key]:
				data = CreateFile('property', key, data)
			else:
				data = CreateFile('method', key, data)

def GetNormalizedContents(contents):
	for line in contents:
		if line.startsWith('//'):
			re.sub(r'//[^\n]*', '', line)
		if line == '\n':
			re.sub(r'\n', '', line)

def GetEnum(contents):
	re_enum = re.compile(r"enum[^}]+};")
	return re.findall(re_enum, contents)

def GetInterface(contents):
	re_interface = re.compile(r"\[[^\]]+\] interface[^}]+};")
	return re.findall(re_interface, contents)

# def GetInterfaceData(idl_file):
# 	f = open(idl_file, 'r')
# 	file_contents = f.read()
# 	norm_contents = GetNormalizedContents(file_contents)
# 	inferface = GetInterface(norm_contents)

# 	re_method = re.compile(r"([^(\s]+\([^\)]+\))")

# 	for line in interface:
# 		if 'interface' in line:
# 			interface = line.strip().split(' ')[2]
# 			data = ({'Shared:Interface': interface})
# 			continue
# 		if re.match(re_method, line) != None:
# 			pieces = line.split(' ')


def GetInterfaceData_(idl_file):
	f = open(idl_file, 'r')
	idl_contents = f.read()
	# re_int_object = re.compile(r"(\[[^\]]+\][^{]+\{[^}]+\})")
	re_int_object = re.compile(r"((?:\[[^\]]+\])?[^{]+\{[^}]+\})")
	# ToDo: Partial interfaces shouldn't get an interface page.
	# ToDo: Interface should get its properties, methods, and event handlers from the IDL instead of prompting.
	re_int_name = re.compile(r"interface +([^\s]+)(?:[\s:]+([^\s{]+))?")
	re_mem_patterns = [r"(?:\[[^\s]+\]\s)?((?:readonly\s)?(?:attribute\s)(?:unrestricted\s)?)(\w+\??)\s(\w+);?$", r"\[[^\]]+\]\s(\w+\s)(\w+\([\w\s]*\));$"]
	# Adding this to the above breaks the looping: , r"(?:\[[^\]]+\]\s)?(Promise<\w+>)\s(\w+)\(\);$"
	idl = re_int_object.findall(idl_contents)[0]
	# print idl
	if idl:
		interface_header = re_int_name.findall(idl)
		print interface_header
		interface_name = interface_header[0][0]
		# print interface_name
		data = ({'Shared:Interface': interface_name})
		for mem_pattern in re_mem_patterns:
			re_mem_object = re.compile(mem_pattern, re.M)
			member_list = re_mem_object.findall(idl)
			print member_list
			for member in member_list:
				print member[2]
				if 'attribute' in member[0]:
					print("MEMBER: " +member[2])
					data[member[2]] = {'Member': member[2]}
					readonly = ''
					if 'readonly' in member[0]:
						readonly = 'read-only'
					data[member[2]].update({'Readonly': readonly, 'Type': 'Property', 'Return': member[2]})
				elif member[0] == '':
					continue
				else:
					data[member[1]] = {'Member': member[1]}
					data[member[1]].update({'Return': member[0], 'Type': 'Method'})
		return data


def ProcessIdl(idl_file):
	data = GetInterfaceData(idl_file)
	print("[DATA]", data)
	data = CreateFilesFromData(data)
	return data



def ProcessIdlDirectory(idl_dir):
	for f in os.listdir(idl_dir):
		if f.endswith('.idl'):
			print f
	# return data

def ListIdl(idl_file):
	data = GetInterfaceData(idl_file)
	print("[DATA]", data)
	return

def listIdlDirectory(idl_dir):
	for f in os.listdir(idl_dir):
		if f.endswith('.idl'):
			print f
	return


if sys.argv[1] == 'template':
	if len(sys.argv) < 8:
		raise Exception("Wrong nubmer of arguments")
	if (sys.argv[2] != '-i') or (sys.argv[4] != '-m') or (sys.argv[6] != '-t'):
		raise Exception("Unsupported argument found. Arguments must be -i, -m and -t in that order.")
	CreateFile(sys.argv[7], sys.argv[5], {'Shared:Interface': sys.argv[3]})

elif sys.argv[1] == 'templates':
	if (sys.argv[2] != '-i') or (sys.argv[4] != '-a'):
		raise Exception("Unsupported argument found. Arguments must be -i, and -a in that order.")
	CreateFilesFromArgs(sys.argv)

elif sys.argv[1] == 'idl':
	idl_input = os.path.join(here, sys.argv[3])
	is_valid_file = os.path.isfile(idl_input) or False
	is_valid_dir = os.path.isdir(idl_input) or False
	if (is_valid_file == is_valid_dir):
		raise Exception("The idl command requries a valid file or directory")
	if (sys.argv[2] != '-f') and (sys.argv[2] != '-l'):
		raise Exception("The idl command requires either a -f or -l argument.")
	if (sys.argv[2] == '-f'):
		if (is_valid_file):
			ProcessIdl(idl_input)
		elif (is_valid_dir):
			ProcessIdlDirectory(idl_input)
	if (sys.argv[2] == '-l'):
		if (is_valid_file):
			ListIdl(idl_input)
		elif (is_valid_dir):
			ListIdlDirectory(idl_input)

elif sys.argv[1] == 'help':
	print "./mdn.py template -i interface -m member -t template"
	print "./mdn.py templates -i interface -a member template [member template]1 ... [member template]n"
	print "./mdn.py idl [-f | -l] [idl_file | idl_foloder]"

else:
	raise Exception("Unrecognized command.")


