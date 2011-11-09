from direct.showbase.DirectObject import DirectObject  #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.task import Task
import sys, math, random
from direct.interval.IntervalGlobal import * #for compound intervals
from pandac.PandaModules import * #basic Panda modules
from direct.interval.IntervalGlobal import *

class Environment(DirectObject):
    def __init__(self):
        #load the models and set up the corresponding collision bodies
        self.dome = loader.loadModel("models/environment")
        self.dome.reparentTo(render)
        
        