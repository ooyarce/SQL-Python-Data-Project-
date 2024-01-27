# ==================================================================================
# IMPORT LIBRARIES
# ==================================================================================
# Objects
from pathlib import Path

# ==================================================================================
# SECONDARY CLASSES
# ==================================================================================
class ModelInfo:
    """
    This class is used to check the model info and extract specific data from the model.
    This data is used in the class SeismicSimulation to perform the analysis and upload
    the results to the database.

    Attributes
    ----------
    path : str
        Path to the 'PartitionsInfo' subfolder.
    folder_accel : str
        Path to the 'PartitionsInfo/accel' subfolder.
    folder_coords : str
        Path to the 'PartitionsInfo/coords' subfolder.
    folder_disp : str
        Path to the 'PartitionsInfo/disp' subfolder.
    folder_info : str
        Path to the 'PartitionsInfo/info' subfolder.
    folder_reaction : str
        Path to the 'PartitionsInfo/reaction' subfolder.

    Methods
    -------
    give_accelerations()
        Returns the accelerations of the model.
    give_coords_info()
        Returns the coordinates of the model.
    give_displacements()
        Returns the displacements of the model.
    give_model_info()
        Returns the info of the model.
    give_reactions()
        Returns the reactions of the model.
    """

    def __init__(self, sim_type:int = 1, verbose:bool=True):
        # Set the path to the 'PartitionsInfo' subfolder
        self.verbose = verbose
        current_path = Path(__file__).parent
        self.path = Path(__file__).parent / "PartitionsInfo"
        # Check if the 'PartitionsInfo' subfolder exists
        if not self.path.exists():
            raise Exception("The PartitionsInfo folder does not exist!\n"
                            "Current path = {}".format(current_path))
        if self.verbose:
            # Call the methods to initialize the data
            print("---------------------------------------------|")
            print("------- CHECKING NODES IN PARTITIONS --------|")
            print("---------------------------------------------|")
        self.accelerations, self.acce_nodes  = self.give_accelerations()
        self.displacements, self.displ_nodes = self.give_displacements()
        self.reactions, self.reaction_nodes  = self.give_reactions() if sim_type==1 else (None, None)

        if self.verbose:
            print('\n---------------------------------------------|')
            print('------------- INITIALIZING DATA -------------|')
            print('---------------------------------------------|')
        self.glob_nnodes, self.glob_nelements, self.npartitions = self.give_model_info()

        self.coordinates,\
        self.drift_nodes,\
        self.stories_nodes,\
        self.stories,\
        self.subs,\
        self.heights = self.give_coords_info()

    def give_accelerations(self):
        # check nodes
        folder_name = "accel"
        files_accel = self.path / folder_name
        files = [open(file, "r") for file in files_accel.iterdir() if file.is_file()]

        # create dictionary
        accelerations = {}
        for file in range(len(files)):
            nodes = [[(num) for num in line.split("\n")]
                     for line in files[file]]
            file_id = (str(files[file]).split("/")[-1].split("-")[1].split(" ")
                       [0].split(".")[0])
            accelerations[f"Partition {file_id}"] = {}
            for nodei in range(len(nodes)):
                accelerations[f"Partition {file_id}"][f"Node {nodei}"] = nodes[
                    nodei][0]

        # create list with nodes sorted
        acce_nodes = []
        for values in accelerations.values():
            for node in values.values():
                acce_nodes.append(int(node))
        acce_nodes.sort()
        listed = set(acce_nodes)

        if len(acce_nodes) == len(listed):
            if self.verbose:
                print("Accelerations: No nodes repeated")
        else:
            raise Exception("WARNING: NODES REPEATED")
        return accelerations, acce_nodes

    def give_displacements(self):
        # check nodes
        folder_name = "disp"
        files_disp = self.path / folder_name
        files = [open(file, "r") for file in files_disp.iterdir() if file.is_file()]

        # create dictionary
        displacements = {}
        for file in range(len(files)):
            nodes = [[(num) for num in line.split("\n")]
                     for line in files[file]]
            file_id = (str(files[file]).split("/")[-1].split("-")[1].split(" ")
                       [0].split(".")[0])
            displacements[f"Partition {file_id}"] = {}
            for nodei in range(len(nodes)):
                displacements[f"Partition {file_id}"][f"Node {nodei}"] = nodes[nodei][0]

        # create list with nodes sorted
        displ_nodes = []

        for values in displacements.values():
            for node in values.values():
                displ_nodes.append(int(node))
        displ_nodes.sort()
        listed = set(displ_nodes)

        if len(displ_nodes) == len(listed):
            if self.verbose:
                print("Displacements: No nodes repeated")
        else:
            raise Exception("WARNING: NODES REPEATED")

        return displacements, displ_nodes

    def give_reactions(self):
        # check nodes
        folder_name = "reaction"
        files_reaction = self.path / folder_name
        files = [open(file, "r") for file in files_reaction.iterdir() if file.is_file()]

        # create dictionary
        reactions = {}
        for file in range(len(files)):
            nodes = [[(num) for num in line.split("\n")]
                     for line in files[file]]
            file_id = (str(files[file]).split("/")[-1].split("-")[1].split(" ")
                       [0].split(".")[0])
            reactions[f"Partition {file_id}"] = {}
            for nodei in range(len(nodes)):
                reactions[f"Partition {file_id}"][f"Node {nodei}"] = nodes[nodei][0]

        # create list with nodes sorted
        reaction_nodes = []
        for values in reactions.values():
            for node in values.values():
                reaction_nodes.append(int(node))

        reaction_nodes.sort()
        listed = set(reaction_nodes)
        if len(reaction_nodes) == len(listed):
            if self.verbose:
                print("Reactions:     No nodes repeated ")
        else:
            raise Exception("WARNING: NODES REPEATED")
        return reactions, reaction_nodes

    def give_coords_info(self):
        # check nodes
        folder_name = "coords"
        files_coords = self.path / folder_name
        files = [open(file, "r") for file in files_coords.iterdir()if file.is_file()]

        # create dictionary
        coordinates = {}
        for file in range(len(files)):
            nodes = [[(num) for num in line.split("\n")] for line in files[file]]

            for nodei in range(1, len(nodes)):
                node_id = nodes[nodei][0].split(" ")[0]
                coord_x = round(float(nodes[nodei][0].split(" ")[1]), 1)
                coord_y = round(float(nodes[nodei][0].split(" ")[2]), 1)
                coord_z = round(float(nodes[nodei][0].split(" ")[3]), 1)
                coordinates[f"Node {node_id}"] = {}
                coordinates[f"Node {node_id}"] = {}
                coordinates[f"Node {node_id}"] = {}
                coordinates[f"Node {node_id}"]["coord x"] = float(f"{coord_x:.1f}")
                coordinates[f"Node {node_id}"]["coord y"] = float(f"{coord_y:.1f}")
                coordinates[f"Node {node_id}"]["coord z"] = float(f"{coord_z:.1f}")

        # sort every node per level
        sorted_nodes = sorted(coordinates.items(), key=lambda x: (x[1]["coord x"], x[1]["coord y"], x[1]["coord z"]))
        # create dictionary with specific nodes per corner to calculate directly the drift
        drift_nodes = {"corner1": [],"corner2": [],"corner3": [],"corner4": []}

        # calculate subs, stories, and fill drift nodes with heights
        height = 0
        id_corner = 1
        subs = []
        stories = 0
        for tuple_i in sorted_nodes:
            z = tuple_i[1]["coord z"]
            # print(z)
            node = tuple_i[0]
            if z < 0 and z != height:
                subs.append(z)
                continue
            elif z == height and z < 0:
                continue
            elif z == height and z >= 0:
                continue
            elif z > height:
                height = z
                drift_nodes[f"corner{id_corner}"].append(f"{node}|{z}")
                stories += 1
                continue
            height = 0.0
            id_corner += 1

        subs = sorted(set(subs))
        subs = len(subs)
        stories = int(stories / 4)
        # list of heigths
        heights = []
        for data in range(len(drift_nodes["corner1"]) - 1):
            current_height = float(
                drift_nodes["corner1"][data + 1].split("|")[1]) - float(
                    drift_nodes["corner1"][data].split("|")[1])
            heights.append(current_height)

        # create dict with nodes per story
        sort_by_story = sorted(coordinates.items() ,key=lambda x: (x[1]["coord z"], x[1]["coord x"], x[1]["coord y"]))
        stories_nodes = {}
        counter = 0
        for i in range(stories + subs + 1):
            i -= subs
            if i < 0:
                counter += 4
                continue
            stories_nodes[f"Level {i}"] = {}
            node1 = sort_by_story[counter][0]
            node2 = sort_by_story[counter + 1][0]
            node3 = sort_by_story[counter + 2][0]
            node4 = sort_by_story[counter + 3][0]
            # print(node1,node2,node3,node4)
            stories_nodes[f"Level {i}"][node1] = sort_by_story[counter][1]
            stories_nodes[f"Level {i}"][node2] = sort_by_story[counter + 1][1]
            stories_nodes[f"Level {i}"][node3] = sort_by_story[counter + 2][1]
            stories_nodes[f"Level {i}"][node4] = sort_by_story[counter + 3][1]
            counter += 4
        heights.insert(0, (coordinates[list(stories_nodes["Level 1"])[0]]["coord z"] - coordinates[list(stories_nodes["Level 0"])[0]]["coord z"]))
        return coordinates, drift_nodes, stories_nodes, stories, subs, heights

    def give_model_info(self):
        # read file
        folder_name = "info"
        files_coords = self.path / folder_name
        file = open(files_coords / 'model_info.csv', "r")
        # get number of nodes and number of elements
        info = [[row for row in line.split(" ")] for line in file]
        nnodes = int(info[0][4])
        nelements = int(info[1][4])
        npartitions = int(info[2][4])
        file.close()
        return nnodes, nelements, npartitions









