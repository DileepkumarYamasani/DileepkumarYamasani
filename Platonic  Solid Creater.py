import maya.cmds as cmds

# Function to create the Window 
def CreateWindow():
	Window = cmds.window(title='Platonic Solids', width=400,height=400)
	cmds.columnLayout(adjustableColumn = True)
	cmds.separator(height = 20)	
		
# Lists the types of platonic solids 
	ListofPlatonics = cmds.optionMenu( "ListofPlatonics", label='         List of Platonic Solids:' )
	cmds.menuItem( label='Cube' )
	cmds.menuItem( label='Tetrahedron' )
	cmds.menuItem( label='Octahedron' )
	cmds.menuItem( label='Dodecahedron' )
	cmds.menuItem( label='Icosahedron' )
	Instance = cmds.intFieldGrp("instance", label= "Number of Instances : ")
	cmds.separator(height = 100)
	
# Creates the button to create platonic solids
	button = cmds.button(label='Create', command = CreatePolygon )
	
# Display new window
	cmds.showWindow()
	
# Funtion for the butoon press 
def CreatePolygon(*args):
	Selection = cmds.optionMenu("ListofPlatonics", query =True, value=True)
	value = cmds.intFieldGrp("instance",query= True, value=True)
		
# Creation Of CUBE	
	if Selection == "Cube":
		for i in range(value[0]):
			CreateCube = cmds.polyCube( name = 'Cube' )
# Creation Of Dodecahedron 		
	elif Selection == "Dodecahedron":
		
		
		
		
		
		
		
		for i in range(value[0]):
			CreateDodecahedron = cmds.polyPlatonicSolid( name='dodecahedron', st=0)
# Creation Of CUBE Icosahedron			
	elif Selection == "Icosahedron":
		for i in range(value[0]):
			CreateIcosahedron = cmds.polyPlatonicSolid( name='icosahedron', st=1 )
# Creation Of CUBE Octahedron			
	elif Selection == "Octahedron":
		for i in range(value[0]):
			CreateOctahedron = cmds.polyPlatonicSolid( name='octahedron', st=2)
# Creation Of CUBE Tetrahedron				
	elif Selection == "Tetrahedron":
		for i in range(value[0]):
			CreateTetrahedron = cmds.polyPlatonicSolid( name='tetrahedron', st=3 )
# If Nothing Is Selected			
	else:
		Create = "DO NOTHING "		
	
CreateWindow()
