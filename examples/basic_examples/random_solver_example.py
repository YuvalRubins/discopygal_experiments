from discopygal.solvers_infra import Scene
from discopygal.solvers_infra.verify_paths import verify_paths
from discopygal_tools.solver_viewer import start_gui

from RandomSolver import RandomSolver

# Load scene from file
scene = Scene.from_file('basic_scene.json')

# "Solve" the scene (find paths for the robots)
solver = RandomSolver(num_landmarks=10, num_connections=10)

# Option 1 - give scene to solve (load + solve)
path_collection = solver.solve(scene)  # Returns a PathCollection object

# Option 2 - First load scene and then solve it (solves the last loaded scene)
solver.load_scene(scene)
path_collection = solver.solve()
path_collection = solver.solve()  # Solves again the loaded scene

# Print the points of the paths
for i, (robot, path) in enumerate(path_collection.paths.items()):
    print("Path for robot {}:".format(i))
    for j, point in enumerate(path.points):
        print(f'\t Point {j:2}:  ', point.location)  # point is of type PathPoint, point.location is CGALPY.Ker.Point_2
    print()

result, reason = verify_paths(scene, path_collection)
print(f"Are paths valid: {result}\t{reason}")

# Optional - Open solver_viewer with our solver and scene

# Option 1 - Use solve object we made:
print("First gui")
start_gui(scene, solver)

# Option 2 - Use solver's class type to create a new one:
print("Second gui")
start_gui(scene, RandomSolver)

# Option 3 - Use solver's class name to create a new one (must pass solver's module):
print("Third gui")
start_gui(scene, "RandomSolver", "RandomSolver.py")

# Option 4 - Passing the path to the scene json file
print("Fourth gui")
start_gui("basic_scene.json", solver)
