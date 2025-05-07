#Created by EMILIA STEVENS
#GitHub: https://github.com/EmiliaStevens
#LinkedIn: https://www.linkedin.com/in/emilia-stevens-344b26354/
#Artstation: https://www.artstation.com/emilia_stevens

import hou
import os

dict_target_node_types = {
    "file": "file",
    "alembic": "fileName",
    "cop2plane": "copfile",  # Only if usecoppath == 0
    # filecache is handled separately
}

# Path to the $HIP folder of the Houdini file
hip_path = os.path.normcase(os.path.normpath(hou.getenv("HIP"))).lower()



def get_nodes():

    list_all_nodes_on_geo_level = hou.node("/obj").allSubChildren()
    list_correct_target_nodes = []

    #Going over all nodes in the Houdini file on geo level
    for node in list_all_nodes_on_geo_level:
        node_type = node.type().name()

        #Special handling for filecache::2.0
        if node_type == "filecache::2.0":
            load_parm = node.parm("loadfromdisk")
            if load_parm and load_parm.eval():
                list_correct_target_nodes.append(node)


        elif node_type in dict_target_node_types:
            #Skip cop2plane if it uses a COP path instead of a file
            if node_type == "cop2plane":
                use_coppath = node.parm("usecoppath")
                if use_coppath and use_coppath.eval() == 1:
                    continue  # skip if using COP input

            list_correct_target_nodes.append(node)

    get_file_path_for_nodes(list_correct_target_nodes)

def get_file_path_for_nodes(list_nodes):
    #Empty dictionary they will include node (key) and file path (value)
    dict_paths = dict()

    #Going over all nodes in the node list and getting their filepath based on the node type
    for node in list_nodes:
        node_type = node.type().name()

        parm_name = None
        parm_name = dict_target_node_types.get(node_type)

        #If the node type is in the target node types
        if not parm_name:
            continue  # no valid parm to check

        parm = node.parm(parm_name)
        if parm:
            file_path = parm.eval()

            if file_path != "":
                dict_paths.update({node:file_path.lower()})


    compare_paths(dict_paths)

def compare_paths(dict_paths):
    list_nodes_with_external_paths = []

    for node, file_path in dict_paths.items():

        # Normalize and make paths case-insensitive (especially on Windows)
        norm_file_path = os.path.normcase(os.path.normpath(file_path))

        try:
            # This will raise ValueError if file_path is on a different drive than hip_path
            if os.path.commonpath([hip_path, norm_file_path]) == hip_path:
                continue
            else:
                list_nodes_with_external_paths.append(node)

        except ValueError:
            # Happens if they're on different drives, e.g., C: vs D:
            list_nodes_with_external_paths.append(node)

    colour_external_nodes_red(list_nodes_with_external_paths)

def colour_external_nodes_red(list_nodes_with_external_paths):

    print("Nodes with external file paths:")
    #Go over all external file path nodes and make them red
    for node in list_nodes_with_external_paths:

        node.setColor(hou.Color((1.0, 0.0, 0.0)))  # RGB values from 0.0 to 1.0
        print(node.name())

get_nodes()