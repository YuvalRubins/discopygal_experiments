import pytest
from dataclasses import dataclass

from discopygal.solvers.staggered_grid import StaggeredGrid, dRRTStaggeredGrid, StaggeredGridMinPath
from .test_solvers import check_solved_scene

@dataclass
class MinPathScene():
    scene_path: str
    delta: int = 0.03
    eps: int = 9999
    result_dist_ratio: int = 1.02

    def get_scene_path(self):
        return 'examples/scenes/' + self.scene_path + '.json'

    def __str__(self) -> str:
        return f"{self.scene_path}-d={self.delta}-e={self.eps}"


MIN_PATH_SCENES = [MinPathScene("two_free_discs_symmetric"),
                   MinPathScene("two_free_discs2"),
                   MinPathScene("two_free_discs3"),
                   MinPathScene("two_free_discs4", result_dist_ratio=3.5, delta=0.02),
                   MinPathScene("two_free_discs5"),
                   MinPathScene("two_free_discs6", result_dist_ratio=1.025),
                   MinPathScene("two_free_discs", result_dist_ratio=1.5)]

@pytest.mark.parametrize("scenario", MIN_PATH_SCENES, ids=[str(s) for s in MIN_PATH_SCENES])
@pytest.mark.skip
def test_min_staggered_grid(scenario: MinPathScene):
    solver = StaggeredGridMinPath.init_solver(bounding_margin_width_factor=2, delta=scenario.delta, eps=scenario.eps)
    paths = check_solved_scene(solver, scenario.get_scene_path())
    max_robot = max(solver.scene.robots, key=lambda r: paths.paths[r].calculate_length(solver.metric))
    max_robot_index = solver.scene.robots.index(max_robot)
    assert paths.paths[max_robot].calculate_length(solver.metric) / solver.metric.dist(max_robot.start, max_robot.end) < scenario.result_dist_ratio
    reference_solver = StaggeredGrid.init_default_solver()
    reference_paths = check_solved_scene(reference_solver, scenario.get_scene_path())
    assert float(reference_paths.paths[reference_solver.scene.robots[max_robot_index]].calculate_length(solver.metric)) >= \
           float(paths.paths[max_robot].calculate_length(solver.metric))