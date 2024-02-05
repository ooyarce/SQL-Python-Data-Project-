import opensees.utils.tcl_input as tclin
import PyMpc.App
import PyMpc.Units as u
import csv
import importlib

from PyMpc import *
from mpc_utils_html import *
import os


def makeXObjectMetaData():
	def mka(type, name, group, descr):
		a = MpcAttributeMetaData()
		a.type = type
		a.name = name
		a.group = group
		a.description = (
			html_par(html_begin()) +
			html_par(html_boldtext(name)+'<br/>') +
			html_par(descr) +
			html_par(html_href('','')+'<br/>') +
			html_end()
		)
		return a
	at_file_name = MpcAttributeMetaData()
	at_file_name.type = MpcAttributeType.String
	at_file_name.name = '$fileName'
	at_file_name.group = 'File'
	at_file_name.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('file_name')+'<br/>') +
		html_par('Name of file to which output is sent (without extension)') +
		html_par(html_href('https://opensees.berkeley.edu/wiki/index.php/Node_Recorder','Node Recorder')+'<br/>') +
		html_end()
		)
	#at_file_name.setDefault(None)

	# -file
	at_file = MpcAttributeMetaData()
	at_file.type = MpcAttributeType.Boolean
	at_file.name = '-file'
	at_file.group = 'File'
	at_file.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('file')+'<br/>') +
		html_par(html_href('https://opensees.berkeley.edu/wiki/index.php/Node_Recorder','Node Recorder')+'<br/>') +
		html_end()
		)
	at_file.setDefault(True)

	# -xml
	at_xml = MpcAttributeMetaData()
	at_xml.type = MpcAttributeType.Boolean
	at_xml.name = '-xml'
	at_xml.group = 'File'
	at_xml.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('xml')+'<br/>') +
		html_par(html_href('https://opensees.berkeley.edu/wiki/index.php/Node_Recorder','Node Recorder')+'<br/>') +
		html_end()
		)

	# -binary
	at_binary = MpcAttributeMetaData()
	at_binary.type = MpcAttributeType.Boolean
	at_binary.name = '-binary'
	at_binary.group = 'File'
	at_binary.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('binary')+'<br/>') +
		html_par(html_href('https://opensees.berkeley.edu/wiki/index.php/Node_Recorder','Node Recorder')+'<br/>') +
		html_end()
		)

	# -extension
	at_extension = MpcAttributeMetaData()
	at_extension.type = MpcAttributeType.String
	at_extension.name = 'Extension'
	at_extension.group = 'File'
	at_extension.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('Extension')+'<br/>') +
		html_par(html_href('https://opensees.berkeley.edu/wiki/index.php/Node_Recorder','Node Recorder')+'<br/>') +
		html_end()
		)
	at_extension.setDefault('.txt')

	# -dof_X
	at_dof_X = MpcAttributeMetaData()
	at_dof_X.type = MpcAttributeType.Boolean
	at_dof_X.name = '-dof_X'
	at_dof_X.group = 'DOF'
	at_dof_X.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('DOF')+'<br/>') +
		html_par('List of dof at nodes whose response is requested.') +
		html_par(html_href('https://opensees.berkeley.edu/wiki/index.php/Node_Recorder','Node Recorder')+'<br/>') +
		html_end()
		)

	# -dof_Y
	at_dof_Y = MpcAttributeMetaData()
	at_dof_Y.type = MpcAttributeType.Boolean
	at_dof_Y.name = '-dof_Y'
	at_dof_Y.group = 'DOF'
	at_dof_Y.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('DOF')+'<br/>') +
		html_par('List of dof at nodes whose response is requested.') +
		html_par(html_href('https://opensees.berkeley.edu/wiki/index.php/Node_Recorder','Node Recorder')+'<br/>') +
		html_end()
		)

	# -dof_Z
	at_dof_Z = MpcAttributeMetaData()
	at_dof_Z.type = MpcAttributeType.Boolean
	at_dof_Z.name = '-dof_Z'
	at_dof_Z.group = 'DOF'
	at_dof_Z.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('DOF')+'<br/>') +
		html_par('List of dof at nodes whose response is requested.') +
		html_par(html_href('https://opensees.berkeley.edu/wiki/index.php/Node_Recorder','Node Recorder')+'<br/>') +
		html_end()
		)

	# nodes
	at_nodes = MpcAttributeMetaData()
	at_nodes.type = MpcAttributeType.IndexVector
	at_nodes.name = '-node'
	at_nodes.group = 'Nodes'
	at_nodes.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('node')+'<br/>') +
		html_par('Tags of nodes whose response is being recorded')+
		html_par(html_href('https://opensees.berkeley.edu/wiki/index.php/Node_Recorder','Node Recorder')+'<br/>') +
		html_end()
		)
	at_nodes.indexSource.type = MpcAttributeIndexSourceType.SelectionSet

	# -disp
	at_disp = MpcAttributeMetaData()
	at_disp.type = MpcAttributeType.Boolean
	at_disp.name = 'disp'
	at_disp.group = 'Response Type'
	at_disp.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('disp')+'<br/>') +
		html_par(html_href('https://opensees.berkeley.edu/wiki/index.php/Node_Recorder','Node Recorder')+'<br/>') +
		html_end()
		)

	# -vel
	at_vel = MpcAttributeMetaData()
	at_vel.type = MpcAttributeType.Boolean
	at_vel.name = 'vel'
	at_vel.group = 'Response Type'
	at_vel.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('vel')+'<br/>') +
		html_par(html_href('https://opensees.berkeley.edu/wiki/index.php/Node_Recorder','Node Recorder')+'<br/>') +
		html_end()
		)

	# -accel
	at_accel = MpcAttributeMetaData()
	at_accel.type = MpcAttributeType.Boolean
	at_accel.name = 'accel'
	at_accel.group = 'Response Type'
	at_accel.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('accel')+'<br/>') +
		html_par(html_href('https://opensees.berkeley.edu/wiki/index.php/Node_Recorder','Node Recorder')+'<br/>') +
		html_end()
		)

	# -incrDisp
	at_incrDisp = MpcAttributeMetaData()
	at_incrDisp.type = MpcAttributeType.Boolean
	at_incrDisp.name = 'incrDisp'
	at_incrDisp.group = 'Response Type'
	at_incrDisp.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('incrDisp')+'<br/>') +
		html_par(html_href('https://opensees.berkeley.edu/wiki/index.php/Node_Recorder','Node Recorder')+'<br/>') +
		html_end()
		)

	# -eigen
	at_eigen = MpcAttributeMetaData()
	at_eigen.type = MpcAttributeType.Boolean
	at_eigen.name = 'eigen'
	at_eigen.group = 'Response Type'
	at_eigen.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('eigen')+'<br/>') +
		html_par(html_href('https://opensees.berkeley.edu/wiki/index.php/Node_Recorder','Node Recorder')+'<br/>') +
		html_end()
		)

	# -mode
	at_mode = MpcAttributeMetaData()
	at_mode.type = MpcAttributeType.Integer
	at_mode.name = '$mode'
	at_mode.group = 'Response Type'
	at_mode.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('mode')+'<br/>') +
		html_par(html_href('https://opensees.berkeley.edu/wiki/index.php/Node_Recorder','Node Recorder')+'<br/>') +
		html_end()
		)
	at_mode.setDefault(0)

	# -reaction
	at_reaction = MpcAttributeMetaData()
	at_reaction.type = MpcAttributeType.Boolean
	at_reaction.name = 'reaction'
	at_reaction.group = 'Response Type'
	at_reaction.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('reaction')+'<br/>') +
		html_par(html_href('https://opensees.berkeley.edu/wiki/index.php/Node_Recorder','Node Recorder')+'<br/>') +
		html_end()
		)

	# -rayleighForces
	at_rayleighForces = MpcAttributeMetaData()
	at_rayleighForces.type = MpcAttributeType.Boolean
	at_rayleighForces.name = 'rayleighForces'
	at_rayleighForces.group = 'Response Type'
	at_rayleighForces.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('rayleighForces')+'<br/>') +
		html_par(html_href('https://opensees.berkeley.edu/wiki/index.php/Node_Recorder','Node Recorder')+'<br/>') +
		html_end()
		)

	# -precision
	at_precision = MpcAttributeMetaData()
	at_precision.type = MpcAttributeType.Boolean
	at_precision.name = 'precision'
	at_precision.group = 'Optional'
	at_precision.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('precision')+'<br/>') +
		html_par('Number of significant digits (default is 6).') +
		html_par(html_href('https://opensees.berkeley.edu/wiki/index.php/Node_Recorder','Node Recorder')+'<br/>') +
		html_end()
		)

	# -nSD
	at_nSD = MpcAttributeMetaData()
	at_nSD.type = MpcAttributeType.Integer
	at_nSD.name = '$nSD'
	at_nSD.group = 'Optional'
	at_nSD.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('nSD')+'<br/>') +
		html_par(html_href('https://opensees.berkeley.edu/wiki/index.php/Node_Recorder','Node Recorder')+'<br/>') +
		html_end()
		)
	at_nSD.setDefault(6)

	# -timeSeries
	at_timeSeries = MpcAttributeMetaData()
	at_timeSeries.type = MpcAttributeType.Boolean
	at_timeSeries.name = 'timeSeries'
	at_timeSeries.group = 'Optional'
	at_timeSeries.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('timeSeries')+'<br/>') +
		html_par('The tag of a previously constructed TimeSeries.') +
		html_par(html_href('https://opensees.berkeley.edu/wiki/index.php/Node_Recorder','Node Recorder')+'<br/>') +
		html_end()
		)

	# -tsTag
	at_tsTag = MpcAttributeMetaData()
	at_tsTag.type = MpcAttributeType.Index
	at_tsTag.name = '$tsTag'
	at_tsTag.group = 'Optional'
	at_tsTag.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('tsTag')+'<br/>') +
		html_par(html_href('https://opensees.berkeley.edu/wiki/index.php/Node_Recorder','Node Recorder')+'<br/>') +
		html_end()
		)
	at_tsTag.indexSource.type = MpcAttributeIndexSourceType.Definition
	at_tsTag.indexSource.addAllowedNamespace("timeSeries")

	# -time
	at_time = MpcAttributeMetaData()
	at_time.type = MpcAttributeType.Boolean
	at_time.name = '-time'
	at_time.group = 'Optional'
	at_time.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('time')+'<br/>') +
		html_par('Using this option places domain time in first entry of each data line') +
		html_par(html_href('https://opensees.berkeley.edu/wiki/index.php/Node_Recorder','Node Recorder')+'<br/>') +
		html_end()
		)

	# -CloseOnWrite
	at_CloseOnWrite = MpcAttributeMetaData()
	at_CloseOnWrite.type = MpcAttributeType.Boolean
	at_CloseOnWrite.name = '-CloseOnWrite'
	at_CloseOnWrite.group = 'Optional'
	at_CloseOnWrite.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('CloseOnWrite')+'<br/>') +
		html_par('Using this option will instruct the recorder to invoke a close on the data handler after every timestep. If this is a file it will close the file on every step and then re-open it for the next step. Note, this greatly slows the execution time, but is useful if you need to monitor the data during the analysis') +
		html_par(html_href('https://opensees.berkeley.edu/wiki/index.php/Node_Recorder','Node Recorder')+'<br/>') +
		html_end()
		)

	# -dT
	at_dT = MpcAttributeMetaData()
	at_dT.type = MpcAttributeType.Boolean
	at_dT.name = '-dT'
	at_dT.group = 'Optional'
	at_dT.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('dT')+'<br/>') +
		html_par('Using this option will instruct the recorder to invoke a close on the data handler after every timestep. If this is a file it will close the file on every step and then re-open it for the next step. Note, this greatly slows the execution time, but is useful if you need to monitor the data during the analysis') +
		html_par(html_href('https://opensees.berkeley.edu/wiki/index.php/Node_Recorder','Node Recorder')+'<br/>') +
		html_end()
		)

	# -deltaT
	at_deltaT = MpcAttributeMetaData()
	at_deltaT.type = MpcAttributeType.Real
	at_deltaT.name = '$deltaT'
	at_deltaT.group = 'Optional'
	at_deltaT.description = (
		html_par(html_begin()) +
		html_par(html_boldtext('deltaT')+'<br/>') +
		html_par('Using this option will instruct the recorder to invoke a close on the data handler after every timestep. If this is a file it will close the file on every step and then re-open it for the next step. Note, this greatly slows the execution time, but is useful if you need to monitor the data during the analysis') +
		html_par(html_href('https://opensees.berkeley.edu/wiki/index.php/Node_Recorder','Node Recorder')+'<br/>') +
		html_end()
		)
	at_deltaT.setDefault(1.0)


	xom = MpcXObjectMetaData()
	xom.name = 'AlbertisRecorder'

	#File
	xom.addAttribute(at_file_name)
	xom.addAttribute(at_file)
	xom.addAttribute(at_xml)
	xom.addAttribute(at_binary)
	xom.addAttribute(at_extension)
	#DOF
	xom.addAttribute(at_dof_X)
	xom.addAttribute(at_dof_Y)
	xom.addAttribute(at_dof_Z)
	#Nodes
	xom.addAttribute(at_nodes)
	#Recorder
	xom.addAttribute(at_disp)
	xom.addAttribute(at_vel)
	xom.addAttribute(at_accel)
	xom.addAttribute(at_incrDisp)
	xom.addAttribute(at_eigen)
	xom.addAttribute(at_mode)
	xom.setVisibilityDependency(at_eigen, at_mode)
	xom.addAttribute(at_reaction)
	xom.addAttribute(at_rayleighForces)
	#Optional
	xom.addAttribute(at_precision)
	xom.addAttribute(at_nSD)
	xom.setVisibilityDependency(at_precision, at_nSD)
	xom.addAttribute(at_time)
	xom.addAttribute(at_timeSeries)
	xom.addAttribute(at_tsTag)
	xom.setVisibilityDependency(at_timeSeries, at_tsTag)
	xom.addAttribute(at_dT)
	xom.addAttribute(at_deltaT)
	xom.setVisibilityDependency(at_dT, at_deltaT)
	xom.addAttribute(at_CloseOnWrite)
	return xom

def extract_tags(pinfo, domain, tag, xobj):
	for elem in domain.elements:
		for node in elem.nodes:
			if node.id not in tag:
				tag.append(node.id)
	tag.sort()
"""
def extract_eletags(pinfo, domain, tag, xobj):
	for elem in domain.elements:
		if elem.id not in tag:
			tag.append(elem.id)
	tag.sort()
"""
def writeTcl(pinfo):
    #-----------------------------------------------------------|
	#----------------------GLOBAL PARAMS------------------------|
	#-----------------------------------------------------------|
	xobj = pinfo.analysis_step.XObject
	def geta(name):
		a = xobj.getAttribute(name)
		if(a is None):
			raise Exception('Error: cannot find "{}" attribute'.format(name))
		return a

	doc = PyMpc.App.caeDocument()
	if(doc is None):
		raise Exception('null cae document')

	ClassName = xobj.name
	if pinfo.currentDescription != ClassName:
		pinfo.out_file.write('\n{}# {} {}\n'.format(pinfo.indent, xobj.Xnamespace, ClassName))
		pinfo.currentDescription = ClassName




	#-----------------------------------------------------------|
	#------------------FILE CONFIGURATION-----------------------S|
	#-----------------------------------------------------------|
	# File name
	file_name_at = xobj.getAttribute('$fileName')
	if(file_name_at is None):
		raise Exception('Error: cannot find "file" attribute')
	file_name = file_name_at.string

	# Extension definition
	at_extension = xobj.getAttribute('Extension')
	if(at_extension is None):
		raise Exception('Error: cannot find "Extension" attribute')
	extension = at_extension.string

	if '.' not in extension:
		raise Exception('Extension not valid')

	# File type definition
	file_type = ''
	at_file_type = xobj.getAttribute('-file')

	if(at_file_type is None):
		raise Exception('Error: cannot find "-file" attribute')
	file_type += '-file' if at_file_type.boolean else ''
	only_type = at_file_type.boolean

	at_file_type = xobj.getAttribute('-xml')
	if(at_file_type is None):
		raise Exception('Error: cannot find "-xml" attribute')

	file_type += '-xml' if at_file_type.boolean else ''
	if only_type and at_file_type.boolean:
		raise Exception('Only one type of file can be selected')
	else:
		only_type = at_file_type.boolean or only_type

	at_file_type = xobj.getAttribute('-binary')
	if(at_file_type is None):
		raise Exception('Error: cannot find "-binary" attribute')
	file_type += '-binary' if at_file_type.boolean else ''
	if only_type and at_file_type.boolean:
		raise Exception('Only one type of file can be selected')




	#-----------------------------------------------------------|
	#---------------------------NODES---------------------------|
	#-----------------------------------------------------------|

	# Get nodes
	nodes_at = xobj.getAttribute('-node')
	if(nodes_at is None):
		raise Exception('Error: cannot find "nodes" attribute')
	SelectionSets = nodes_at.indexVector

	# Get node tags
	nodes_tags = []
	ele_tags = []
	for selection_set_id in SelectionSets:
		if not selection_set_id in doc.selectionSets:
			continue
		selection_set = doc.selectionSets[selection_set_id]

		for geometry_id, geometry_subset in selection_set.geometries.items():
			mesh_of_geom = doc.mesh.meshedGeometries[geometry_id]

			for domain_id in geometry_subset.vertices:
				domain = mesh_of_geom.vertices[domain_id]
				if domain.id not in nodes_tags:
					nodes_tags.append(domain.id)
			nodes_tags.sort()
			for domain_id in geometry_subset.edges:
				domain = mesh_of_geom.edges[domain_id]
				extract_tags(pinfo, domain, nodes_tags, xobj)
				#extract_eletags(pinfo, domain, nodes_tags, xobj)

			for domain_id in geometry_subset.faces:
				domain = mesh_of_geom.faces[domain_id]
				extract_tags(pinfo, domain, ele_tags, xobj)
				#extract_eletags(pinfo, domain, ele_tags, xobj)
			"""
			for domain_id in geometry_subset.solids:
				domain = mesh_of_geom.solids[domain_id]
				extract_tags(pinfo, domain, nodes_tags, xobj)
			"""
		for interaction_id in selection_set.interactions:
			domain = doc.mesh.meshedInteractions[interaction_id]
			extract_tags(pinfo, domain, nodes_tags, xobj)

	# Defining responses types
	respType = ''
	def_respTypes = [' disp',' vel',' accel',' incrDisp','eigen',' reaction',' rayleighForces']

	for resp_str in def_respTypes:
		if resp_str == 'eigen':
			eigen_at = xobj.getAttribute('eigen')
			mode_at = xobj.getAttribute('$mode')
			if eigen_at is None:
				raise Exception('Error: cannot find "{}" attribute'.format(resp_str))
			respType += ' eigen {}'.format(mode_at.integer) if eigen_at.boolean else ''
		else:
			response = xobj.getAttribute(resp_str[1:])
			if response is None:
				raise Exception('Error: cannot find "{}" attribute'.format(resp_str))
			respType += resp_str if response.boolean else ''

	if respType == '':
		raise Exception('Response Type cannot be empty')

	# Defining DOFs
	dofs = ''
	def_dofs = {'-dof_X':' 1','-dof_Y':' 2','-dof_Z':' 3'}
	for dof_str in def_dofs:
		dof_at = xobj.getAttribute(dof_str)
		if dof_at is None:
			raise Exception('Error: cannot find "{}" attribute'.format(dof_str))
		dofs += def_dofs[dof_str] if dof_at.boolean else ''
	if dofs == '':
		raise Exception('DOF cannot be empty')

	# Optionals 1
	sopt = ''
	at_time = xobj.getAttribute('-time')
	if(at_time is None):
		raise Exception('Error: cannot find "-time" attribute')
	sopt += ' -time ' if at_time.boolean else ''

	# Optionals 2
	at_precision = xobj.getAttribute('precision')
	at_nSD = xobj.getAttribute('$nSD')
	if(at_precision is None):
		raise Exception('Error: cannot find "precision" attribute')
	sopt += ' -precision {}'.format(at_nSD.integer) if at_precision.boolean else ''

	#Write TCL
	str_tcl = ''
	node_str = ''
	nodes_number = len(doc.mesh.nodes)
	ele_number = len(doc.mesh.elements)
	partitions = pinfo.process_count





	#-----------------------------------------------------------|
	#------------------WRITE RECORDER---------------------------|
	#-----------------------------------------------------------|
	# Create 'Results' folders
	path = os.path.abspath(pinfo.out_dir)

	# Create folder for Partitions Info files and check model
	os.makedirs(f'{path}/PartitionsInfo/info', exist_ok=True)
	with open(f'{path}\\PartitionsInfo\\info\\model_info.csv', 'w') as info_file:
		info_file.write(f'Number of nodes = {nodes_number}\n')
		info_file.write(f'Number of elements = {ele_number}\n')
		info_file.write(f'Number of partitions = {partitions}\n')

	# Parallel computing
	if pinfo.process_count > 1:
		process_block_count = 0
		for process_id in range(pinfo.process_count):
			first_done = False
			#Check if directories exist and create them if not
			os.makedirs(f'{path}/PartitionsInfo/coords', exist_ok=True)
			os.makedirs(f'{path}/PartitionsInfo/{respType[1:]}', exist_ok=True)

			#Add coordinate info
			if respType == ' disp':
				os.makedirs(f'{path}/Displacements', exist_ok=True)
				with open(f'{path}/PartitionsInfo/coords/coords_{process_id}.csv','w') as coords_file:
					coords_file.write('Node ID, X, Y, Z \n')
					for node_id in nodes_tags:
						if doc.mesh.partitionData.nodePartition(node_id) != process_id:
							continue
						nodex = doc.mesh.nodes[node_id].x
						nodey = doc.mesh.nodes[node_id].y
						nodez = doc.mesh.nodes[node_id].z
						coords_file.write("{} {} {} {} \n".format(node_id, nodex,nodey,nodez))
			elif respType == ' accel': os.makedirs(f'{path}/Accelerations', exist_ok=True)
			elif respType == ' reaction': os.makedirs(f'{path}/Reactions', exist_ok=True)

			#Add info about accelerations, displacements and reactions
			with open(f'{path}/PartitionsInfo/{respType[1:]}/{respType[1:]}_nodes_part-{process_id}.csv','w') as results_file:
				for node_id in nodes_tags:
					#In short, this line of code ensures that only nodes belonging to the current process running in parallel are processed.
					if doc.mesh.partitionData.nodePartition(node_id) != process_id:
						continue
					results_file.write(f'{node_id}\n')

					#This lines are about getting the output
					if not first_done:
						if process_block_count == 0:
							str_tcl += '\n{}{}{}{}\n'.format(pinfo.indent, 'if {$STKO_VAR_process_id == ', process_id, '} {')
						else:
							str_tcl += '{}{}{}{}\n'.format(pinfo.indent, ' elseif {$STKO_VAR_process_id == ', process_id, '} {')
						first_done = True
					str_tcl += '{}{}recorder Node {} "{}-node_{}-part_$STKO_VAR_process_id{}" -node {}{} -dof{}{}\n'.format(pinfo.indent, pinfo.tabIndent,file_type,file_name, node_id,extension, node_id , sopt,dofs, respType)
					if first_done:
						process_block_count += 1
				if process_block_count > 0 and first_done:
					str_tcl += '{}{}'.format(pinfo.indent, '}')

 	#TODO: this is not well implement
	# Secuencial computing
	else:
		os.makedirs(f'{path}/coords', exist_ok=True)
		os.makedirs(f'{path}/{respType[1:]}', exist_ok=True)
		if respType == ' disp':
				with open(f'{path}/coords/coords.csv','w') as coords_file:
					coords_file.write('Node ID, X, Y, Z \n')
					for node_id in nodes_tags:
						nodex = doc.mesh.nodes[node_id].x
						nodey = doc.mesh.nodes[node_id].y
						nodez = doc.mesh.nodes[node_id].z
						coords_file.write("{} {} {} {} \n".format(node_id, nodex,nodey,nodez))

		with open(f'{path}/{respType[1:]}/{respType[1:]}_nodes.csv','w') as results_file:
			for node_id in nodes_tags:
				results_file.write(f'{node_id}\n')
				node_str += f' {node_id}'
				str_tcl += '{}recorder Node {} "{}{}" -node {}{} -dof{}{}'.format(pinfo.indent,file_type,file_name,extension, node_str , sopt,dofs, respType,'\n')
	str_tcl += '{}{}'.format(pinfo.indent,'\n')
	pinfo.out_file.write(str_tcl)



