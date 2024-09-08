###################################################################################################################
    ## Base class for the plugin ##


    ## It is mostly imports and creating the TestEffects class
    ## It also creates the menu item "Effects test", which starts the client and begins listening


    ## TODO: Add a proper docker window with a connect button, and status read outs
###################################################################################################################
from krita import *                                         ## Krita

from PyQt5.QtWidgets import QWidget, QAction                ## For the menu element and click action
from PyQt5.Qt import PYQT_VERSION_STR                       ## So we can print out the PyQT version

from .effect_functions import TestEffects                   ## Our TestEffects class



###################################################################################################################
    ## This is the main class for the extension ##

    ## See https://scripting.krita.org/lessons/plugins-extensions
###################################################################################################################
class ExtensionTemplate(Extension):
    def __init__(self, parent):
        super().__init__(parent)



    ## Called once Krita.instance() exists so we can do plugin setup
    def setup(self):
        pass



    ## Called by the menu element click   
    def StartTest(self):
        qWarning("Krita version:\t\t" + Application.version())      ## Krita version
        qWarning("Python version:\t\t" + sys.version)               ## Python version
        qWarning("PyQT version:\t\t" + PYQT_VERSION_STR)            ## PyQT version

        effects = TestEffects()                                     ## Create our test class
        effects.start_client_socket()                               ## Start the client, connect to Crowd Control



    ## Called by Krita.instance() after setup()
    ## Do UI stuff here
    def createActions(self, window):
        action = window.createAction("", "Effects test")            ## Create the menu element
        action.triggered.connect(self.StartTest)                    ## Connect it to the StartTest() function


