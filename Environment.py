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
        self.env=render.attachNewNode(ActorNode('dummy env'))
        self.model.reparentTo(self.env)
        self.envNode = self.model.find("**/coll_ground")
        self.envNode.reparentTo(self.env)
        self.envNode.node().setFromCollideMask(BitMask32.allOff())
        self.env.setScale(5)
        
        #bounding dome
        self.dome_model = loader.loadModel("models/dome_again")
        self.dome_model.setScale(5)
        self.domeNode = CollisionNode("dome")
        self.dome = CollisionInvSphere(0,0,0,100)
        self.domeNode.addSolid(self.dome)
        self.domeNodePath = self.env.attachNewNode(self.domeNode)
        self.domeNodePath.node().setFromCollideMask(BitMask32.allOff())
        #self.domeNodePath.show()
        
        #resorting to simple collision since .egg collision hates us
        
        self.groundNode = CollisionNode("ground")
        self.ground = CollisionPlane(Plane(Vec3(0,0,1),Point3(0,0,0)))
        self.groundNode.addSolid(self.ground)
        self.groundNodePath = self.env.attachNewNode(self.groundNode)
        self.groundNodePath.node().setFromCollideMask(BitMask32.allOff())
        #self.groundNodePath.show()
        
        
        
        
        
        