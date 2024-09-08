###################################################################################################################
    ## effect_functions.py ##


    ## Main file for testing effects
###################################################################################################################
from krita import *                         ## Krita

import socket                               ## for connecting to Crowd Control with TCP
import json                                 ## to parse JSON data sent from Crowd Control
from enum import Enum                       ## for all the response types
from time import sleep                      ## sleep()

from PyQt5.QtWidgets import QMainWindow     ## passed to TestEffects class from Krita
from PyQt5.QtCore import (                  ## TODO: clean up
    QObject,                                ## used in worker objects
    QThread,                                ## QThreads
    pyqtSignal                              ## signals passed from inside worker loops
)



###################################################################################################################
    ## Request types ##


    ## See https://github.com/WarpWorld/ConnectorLib.JSON/blob/main/RequestType.cs
###################################################################################################################
class RequestTypes(Enum):
    EffectTest      = 0x00
    EffectStart     = 0x01
    EffectStop      = 0x02
    GenericEvent    = 0x10
    DataRequest     = 0x20
    RpcResponse     = 0xD0
    PlayerInfo      = 0xE0
    Login           = 0xF0
    GameUpdate      = 0xFD
    KeepAlive       = 0xFF
    


###################################################################################################################
    ## Response types ##


    ## See https://github.com/WarpWorld/ConnectorLib.JSON/blob/main/ResponseType.cs
###################################################################################################################
class ResponseTypes(Enum):
    EffectRequest   = 0x00
    EffectStatus    = 0x01
    GenericEvent    = 0x10
    LoadEvent       = 0x18
    SaveEvent       = 0x19
    DataResponse    = 0x20
    RpcRequest      = 0xD0
    Login           = 0xF0
    LoginSuccess    = 0xF1
    GameUpdate      = 0xFD
    Disconnect      = 0xFE
    KeepAlive       = 0xFF
    


###################################################################################################################
    ## Effect status ##


    ## See https://github.com/WarpWorld/ConnectorLib.JSON/blob/main/EffectStatus.cs
###################################################################################################################
class EffectStatus(Enum):
    ## Effect Instance Messages ##
    Success         = 0x00  ## The effect executed successfully

    Failure         = 0x01  ## The effect failed to trigger, but is still available for use
                            ## Viewer(s) will be refunded
                            ## You probably don't want this

    Unavailable     = 0x02  ## Same as Failure but the effect is no longer available for the remainder of the game
                            ## You probably don't want this

    Retry           = 0x03  ## The effect cannot be triggered right now, try again in a few seconds
                            ## This is the "normal" failure response

    Queue           = 0x04  ## INTERNAL USE ONLY
                            ## The effect has been queued for execution after the current one ends

    Running         = 0x05  ## INTERNAL USE ONLY
                            ## The effect triggered successfully and is now active until it ends
    
    Paused          = 0x06  ## The timed effect has been paused and is now waiting
    
    Resumed         = 0x07  ## The timed effect has been resumed and is counting down again
    
    Finished        = 0x08  ## The timed effect has finished


    ## Effect Class Messages ##
    Visible         = 0x80  ## The effect should be shown in the menu
    
    NotVisible      = 0x81  ## The effect should be hidden in the menu
    
    Selectable      = 0x82  ## The effect should be selectable in the menu
    
    NotSelectable   = 0x83  ## The effect should be unselectable in the menu


    ## System Status Messages ##
    NotReady        = 0xFF  ## The processor isn't ready to start or has shut down



###################################################################################################################
    ## Class to run the rotate canvas thread ##


    ## 
###################################################################################################################
class RotateWorker(QObject):
    finished = QtCore.pyqtSignal()                  ## Create a signal for when this thread finishes
    progress = QtCore.pyqtSignal()                  ## Create a signal for when this thread does an update tick
    slot = 0                                        ## Store the output function locally. This is needed? Why?

    def __init__(self):                             ## init
        super().__init__()

    def set_progress(self, slot):                   ## Set the progress function and store it
        self.progress.connect(slot)
        self.slot = slot

    def run(self):                                  ## This is the loop itself.
        for i in range(5 * 360):                    ## Spin 5 times
            sleep(1 / 60)                           ## Delay is one 60fps frame. TODO: Is there a Krita update tick
            self.progress.emit()                    ## We looped

        self.finished.emit()                        ## The thread is done, tell the clean up functions



###################################################################################################################
    ## Class to run the read loop thread ##


    ##  
###################################################################################################################
class ReadWorker(QObject):
    finished = QtCore.pyqtSignal()                  ## Create a signal for when this thread finishes
    progress = QtCore.pyqtSignal(bytes)             ## Create a signal for when we receive data from Crowd Control
    slot = 0                                        ## Store the output function locally. This is needed? Why?
    sock = 0                                        ## Store the already created socket, so we can read from it

    def __init__(self):                             ## init
        super().__init__()

    def set_progress(self, slot):                   ## Set the progress function and store it
        self.progress.connect(slot)
        self.slot = slot

    def set_sock(self, s):                          ## Set the socket so we can access it in the loop
        self.sock = s

    def run(self):                                  ## This is the loop itself.
        while True:                                 ## Infinite read loop. We clean up. TODO: Add a proper loop.
            data = self.sock.recv(1024)             ## We got a message!
            self.progress.emit(data)                ## Tell the message function
        self.finished.emit()                        ## Tell the clean up functions that the thread is done.
        qWarning("Exiting read loop")               ## Tell ourselves too


    
###################################################################################################################
    ## Main class for testing effects ##


    ## For now it contains everything, including the network client
###################################################################################################################
class TestEffects(QMainWindow):                     ## Create a class to test effects with
    thread = QThread()                              ## One thread for the rotation. TODO: Use thread pools
    thread2 = QThread()                             ## One thread for the socket reader. TODO: Use thread pools
    worker = RotateWorker()                         ## Rotation worker class
    readWorker = ReadWorker()                       ## Socket reader worker class
    sock = 0                                        ## The socket itself
    spinFunction = 0


    def __init__(self):                                     ## init
        super().__init__()
        self.worker.set_progress(self.rotate_canvas_tick)   ## Set the spin progress function
        self.worker.moveToThread(self.thread2)              ## Move the rotation worker to it's thread
        self.thread2.started.connect(self.worker.run)       ## Set the start function
        self.worker.finished.connect(self.thread2.quit)     ## When worker is done, tell thread


    def __del__(self):                              ## Clean up important stuff if we leave scope early somehow
        self.sock.close()                           ## Probably not needed
        self.thread2.quit()
        self.thread.quit()


    
###################################################################################################################
    ## Start the canvas rotation thead ##


    ## We aren't cleaning up the worker or thread here because we might want to spin again


    ## TODO: Revisit thread creation. Use thread pools?
###################################################################################################################
    def rotate_canvas_thread(self):                                 ## Give the canvas a spin
        qWarning("Starting rotation")
        self.thread2.start()                                        ## Everything is set. Start the thread



###################################################################################################################
    ## Start the client thead and enter read loop ##


    ## TODO: Revisit thread creation. Use thread pools?
###################################################################################################################
    def start_client_socket(self):
        qWarning("Connecting...")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       ## Create the socket
        HOST = "127.0.0.1"                                                  ## Crowd Control server is on 127.0.0.1
        PORT = 2323                                                         ## Any port between 1024 - 49151
        self.sock.connect((HOST, PORT))                                     ## Connect to the Crowd Control server
        qWarning("Connected")

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)     ## Enable keepalive

        self.readWorker.moveToThread(self.thread)                           ## Move the readWorker to it's thread
        self.thread.started.connect(self.readWorker.run)                    ## Set the start function
        self.readWorker.set_sock(self.sock)                                 ## Set the socket we just made
        self.readWorker.set_progress(self.read_update)                      ## Set the output for received data

        self.readWorker.finished.connect(self.thread.quit)                  ## When worker is done, tell thread
        self.readWorker.finished.connect(self.readWorker.deleteLater)       ## Delete the worker when done
        self.thread.finished.connect(self.thread.deleteLater)               ## Delete the thread when done

        self.thread.start()                                                 ## Everything is set. Start the thread



###################################################################################################################
    ## Send a message to Crowd Control ##


    ##  (Crowd Control) Messages are encoded as null terminated UTF-8 strings
    ##      https://developer.crowdcontrol.live/sdk/simpletcp/index.html#connection-methods
###################################################################################################################
    def socket_send(self, output):
        s = str(output).encode("utf-8") + "\x00".encode("utf-8")    ## Encode the output to a bytes type of UTF-8
        qWarning("Sending message to Crowd Control:")
        qWarning(str(s))
        self.sock.send(s)                                           ## Send



###################################################################################################################
    ## If the Crowd Control message is an effect request, it is send to this function ##


    ##
###################################################################################################################
    def handle_effect(self, effectJSON):
        ## Local variables
        activeView = Krita.instance().activeWindow().activeView()   ## Store the active view once to tidy things up


        ## Start a message to be filled out in this function for Crowd Control
        message = {                                             ## Start the message for Crowd Control as a dict
            "id": effectJSON['id'],                             ## The ID of the effect we are responding to
            "type": ResponseTypes.EffectRequest.value,          ## We're doing an EffectRequest
            "status": EffectStatus.Success.value                ## It was great
        }


        ## Spin the canvas ##
        if effectJSON['code'] == "spin_canvas":                 ## Spin the canvas
            self.spinFunction = self.rotate_normal              ## Set the type of spin we want
            self.rotate_canvas_thread()                         ## Do the thing
            message["duration"] = effectJSON['duration']        ## Effects with durations need the duration
                                                                ## It has to match, so just copy it

        ## Slow chaotic spin ##
        elif effectJSON['code'] == "spin_slow_chaotic":         ## Spin the canvas, slowly and chaotically
            self.spinFunction = self.rotate_slow_chaotic        ## Set the type of spin we want
            self.rotate_canvas_thread()                         ## Do the thing
            message["duration"] = effectJSON['duration']        ## Effects with durations need the duration


        ## Nudge the canvas CW ##
        elif effectJSON['code'] == "nudge_canvas_cw":           ## Nudge the canvas
            canvas = activeView.canvas()                        ## Get the active canvas
            canvas.setRotation(canvas.rotation() + 5)           ## Give it a nudge


        ## Nudge the canvas CCW ##
        elif effectJSON['code'] == "nudge_canvas_ccw":          ## Nudge the canvas
            canvas = activeView.canvas()                        ## Get the active canvas
            canvas.setRotation(canvas.rotation() - 5)           ## Give it a nudge


        ## Vertical flip ##
        elif effectJSON['code'] == "vertical_flip":             ## Vertical flip
            canvas = activeView.canvas()                        ## Get the active canvas
            canvas.setRotation(canvas.rotation() + 180)         ## fleep


        ## Horizontal flip ##
        elif effectJSON['code'] == "horizontal_flip":           ## Horizontal flip
            canvas = activeView.canvas()                        ## Get the active canvas
            canvas.setMirror(not canvas.mirror())               ## fleep


        ## Rainbow paint ##
        elif effectJSON['code'] == "rainbow_paint":             ## Rainbow paint
            allPresets = Krita.instance().resources("preset")   ## Get a list of resource presets
            for preset in allPresets:                           ## For all of them..
                if preset == "rainbow01":                       ## If "rainbow01", set it to our current brush
                    activeView.setCurrentBrushPreset(allPresets[preset]) #ugh


        ## The message should be ready to send
        message = json.dumps(message)                           ## Convert the message to JSON
        self.socket_send(message)                               ## Pass the message to our send function



###################################################################################################################
    ## These are the rotation functions ##


    ## The spinFunction variable is set to either rotate_normal or rotate_slow_chaotic, and called when
    ##      it's time to increment
    ## Right now the slow chaotic one doesn't have it's own thread, so it only spins 1/10th of the full rotation
###################################################################################################################
    def rotate_normal(self):                                                ## Normal fast
        canvas = Krita.instance().activeWindow().activeView().canvas()      ## Get the canvas
        canvas.setRotation(canvas.rotation() + 1)                           ## Increment the rotation



    def rotate_slow_chaotic(self):                                          ## Slow chaotic
        canvas = Krita.instance().activeWindow().activeView().canvas()      ## Get the canvas
        canvas.setRotation(canvas.rotation() + 0.1)                         ## Increment the rotation



    @pyqtSlot()                                                             ## The decorator will wrap our slot
                                                                            ##      in the appropriate PyQT code
    def rotate_canvas_tick(self):                                           ## It's time to increment our spin
        self.spinFunction()                                                 ## Call the set spin function



###################################################################################################################
    ## This function is sent data directly from recv() ##


    ##  The random last entry that appears sometimes is future proofing from the Crowd Control team
    ##      see screen shot


    ##  The return value (of recv) is a bytes object representing the data received
    ##      https://docs.python.org/3/library/socket.html#socket.socket.recv
    ##
    ##  (Crowd Control) Messages are encoded as null terminated UTF-8 strings
    ##      https://developer.crowdcontrol.live/sdk/simpletcp/index.html#connection-methods
    ##  
    ##  Refer to ConnectorLib.JSON for handling messages
    ##      https://github.com/WarpWorld/ConnectorLib.JSON


    ##  TODO: A proper TCP data parse is needed to handle the potential of multiple messages
###################################################################################################################
    @pyqtSlot(bytes)                                    ## The decorator will wrap our slot function in the
                                                        ##      appropriate PyQT code
    def read_update(self, data):
        qWarning("\nReceived:")
        qWarning(str(data))

        qWarning("Casting to string:")
        dataString = data.decode("utf-8")               ## Decode with UTF-8
        dataString = dataString.split("\x00", 1)[0]     ## Remove null terminator + all after it. TODO: parse all
        qWarning(dataString)

        qWarning("Casting to JSON:")
        dataJSON = json.loads(dataString)               ## Convert to JSON
        qWarning("id\t-\t" + str(dataJSON['id']))       ## Show us what we made
        qWarning("type\t-\t" + str(dataJSON['type']))



        if dataJSON['type'] == RequestTypes.EffectStart.value:      ## Crowd Control is requesting an effect start
            qWarning("type\t-\t" + "EffectStart")
            self.handle_effect(dataJSON)                            ## Send effect requests to handle_effect()



        elif dataJSON['type'] == RequestTypes.GameUpdate.value:     ## Crowd Control is requesting a game update
            qWarning("type\t-\t" + "GameUpdate")                    ## this will constantly send

            message = {                                             ## Create the message as a dictionary
                "id": dataJSON['id'],                               ## Set the message id that we're reply to
                "type": ResponseTypes.GameUpdate.value,             ## The type of response we're sending
                "state": 1                                          ## We are ready. TODO: Add enum of GameUpdates
            }
            message = json.dumps(message)                           ## Convert it to JSON
            self.socket_send(message)                               ## Send our reply to Crowd Control
      


        elif dataJSON['type'] == RequestTypes.EffectStop.value:     ## TODO: ??
            qWarning("type\t-\t" + "EffectStop")
        elif dataJSON['type'] == RequestTypes.GenericEvent.value:
            qWarning("type\t-\t" + "GenericEvent")
        elif dataJSON['type'] == RequestTypes.DataRequest.value:
            qWarning("type\t-\t" + "DataRequest")
        elif dataJSON['type'] == RequestTypes.RpcResponse.value:
            qWarning("type\t-\t" + "RpcResponse")
        elif dataJSON['type'] == RequestTypes.PlayerInfo.value:
            qWarning("type\t-\t" + "PlayerInfo")
        elif dataJSON['type'] == RequestTypes.Login.value:
            qWarning("type\t-\t" + "Login")
        elif dataJSON['type'] == RequestTypes.EffectTest.value:
            qWarning("type\t-\t" + "EffectTest")
        elif dataJSON['type'] == RequestTypes.KeepAlive.value:
            qWarning("type\t-\t" + "KeepAlive")


