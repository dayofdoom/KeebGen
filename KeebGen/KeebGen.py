import adsk.core
import adsk.fusion
import traceback
from .Modules import KLE
from .Modules import Switches
from .Modules import Layers
from .Modules import Config


def main():
    keys = KLE.get_keys()
    Layers.full_case(keys)
    if Config.INSERT_SWITCHES:
        Switches.place_switches(keys)


def run(context):
    """This function will be called by fusion as the "main" method."""
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        main()
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
