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
        self.model = loader.loadModel("models/simple_env")
        self.model.reparentTo(render)
        self.model.setPos(0,0,0)
        self.dome =render.attachNewNode(ActorNode('dummy env'))
        self.model.reparentTo(self.dome)
        self.envNode = self.model.find("**/coll_ground")
        self.envNode.reparentTo(self.dome)
        self.envNode.node().setFromCollideMask(BitMask32.allOff())
        