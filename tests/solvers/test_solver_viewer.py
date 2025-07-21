import sys
import json
import time
import threading
import pyautogui
import faulthandler
from PyQt5.QtWidgets import QApplication, QLineEdit, QTextEdit

from discopygal.solvers_infra import Scene
from discopygal.solvers.prm.prm import PRM
# from examples.basic_examples.RandomSolver import RandomSolver
from discopygal_tools.solver_viewer.solver_viewer_main import SolverViewerGUI

BASIC_SCENE = "examples/basic_examples/basic_scene.json"
faulthandler.disable()

class GUITester:
    def __init__(self, gui=None, app=None, solve_success_string='', **kwargs):
        self.app = app
        self.gui = gui
        self.did_import_solver_file = kwargs.get('solver_file') is not None
        self.solve_success_string = solve_success_string

    def set_gui(self, gui):
        self.gui = gui

    def wait_for_end_playing(self):
        time.sleep(1)
        while self.gui.is_queue_playing():
            time.sleep(0.5)

    def trigger_action(self, action_name, wait_time=1):
        self.gui.__getattribute__("action" + action_name).trigger()
        time.sleep(wait_time)

    def get_window_gui(self, gui_window_title):
        for gui_window in self.app.allWindows():
            if gui_window.title() == gui_window_title:
                return gui_window

    def get_widget_text(self, widget_name):
        widget = self.gui.__getattribute__(widget_name)
        if isinstance(widget, QLineEdit):
            return widget.text()
        if isinstance(widget, QTextEdit):
            return widget.toPlainText()

    @staticmethod
    def press_on_window(key, window_name=None):
        if window_name is not None:
            window = pyautogui.getWindowsWithTitle(window_name)[0]
            window.activate()
        pyautogui.press(key)

    def tester_thread(self, testing_function):
        try:
            testing_function(self)
        finally:
            self.gui.mainWindow.close()

    def basic_check_gui(self):
        print("Starting test")
        time.sleep(3)
        # from IPython import embed; embed()
        if self.did_import_solver_file:
            self.press_on_window("Enter", "Import solvers")
        assert self.gui.scene_path == self.get_widget_text("scenePathEdit")
        assert self.gui.solver.__class__.__name__ == self.get_widget_text("solverName")
        self.trigger_action("Solve", 4)
        if self.solve_success_string:
            assert self.solve_success_string in self.get_widget_text("textEdit")
        self.trigger_action("Verify")
        self.press_on_window("Enter", "Verify Paths")
        self.trigger_action("ShowGraph", 2)
        self.trigger_action("ShowGraph")
        self.trigger_action("ShowPaths")
        self.trigger_action("Grid")
        self.trigger_action("ShowBoundingBox")
        self.trigger_action("Grid")
        self.trigger_action("ShowBoundingBox")
        self.trigger_action("Play")
        self.trigger_action("Play")
        self.trigger_action("Play")
        self.trigger_action("Stop")
        self.trigger_action("Play")
        self.wait_for_end_playing()
        self.trigger_action("Clear")
        assert '' == self.get_widget_text("scenePathEdit")

def solver_viewer_test_case(testing_function, **kwargs):
    app = QApplication(sys.argv)
    gui_tester = GUITester(**kwargs)
    t = threading.Thread(target=GUITester.tester_thread, args=(gui_tester, testing_function))
    t.start()
    gui = SolverViewerGUI(kwargs.get("scene"), kwargs.get("solver"), kwargs.get("solver_file"))
    gui_tester.set_gui(gui)
    app.exec_()
    t.join()
    print("done")


def solver_viewer_basic_test(solve_success_string='Successfully found a path', **kwargs):
    solver_viewer_test_case(GUITester.basic_check_gui,
                            solve_success_string=solve_success_string,
                            **kwargs)

def test_solver_viewer_1():
    solver_viewer_basic_test(scene=BASIC_SCENE, solver="PRM")

def test_solver_viewer_2():
    solver_viewer_basic_test(scene=BASIC_SCENE, solver=PRM)

def test_solver_viewer_3():
    solver_viewer_basic_test(scene=BASIC_SCENE, solver=PRM(100, 20))

def test_solver_viewer_4():
    scene = Scene.from_file(BASIC_SCENE)
    solver_viewer_basic_test(scene=scene, solver=PRM)

def test_solver_viewer_random_solver():
    solver_viewer_basic_test(scene=BASIC_SCENE,
                             solver="RandomSolver",
                             solver_file="examples/basic_examples/RandomSolver.py",
                             solve_success_string="")

if __name__ == "__main__":
    test_solver_viewer_random_solver()
