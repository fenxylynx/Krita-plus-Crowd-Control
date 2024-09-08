###################################################################################################################
    ## ./__init__.py ##


    ## Import the ExtensionTemplate class, which is the base for the plugin
    ## Make an instance of it, and register it with the Krita instance
    ##
    ## Also import the TestEffects class 
    ## We will make an instance of it in the ExtensionTemplate class later
###################################################################################################################
from .extension_template import ExtensionTemplate
from .effect_functions import TestEffects

Krita.instance().addExtension(ExtensionTemplate(Krita.instance()))


