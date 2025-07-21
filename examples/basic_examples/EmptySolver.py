from discopygal.solvers_infra.Solver import Solver


class EmptySolver(Solver):
    def _solve(self):
        self.log("Solving...")
        return None

    # Not really need this
    def load_scene(self, scene):
        super().load_scene(scene)

    @classmethod
    def get_arguments(cls):
        return {}
