from direct.showbase.DirectObject import DirectObject  #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.task import Task
import sys, math, random
from direct.interval.IntervalGlobal import * #for compound intervals
from pandac.PandaModules import * #basic Panda modules

class Plane(DirectObject):
    def __init__(self,camera,name):
        #load model
        self.np = None
        self.camera = camera
        self.plane = render.attachNewNode(ActorNode(name))
        self.model = loader.loadModel("models/mig-3")
        self.model.reparentTo(self.plane)
        self.plane.setScale(.05)
        self.plane.setH(180)
        #self.plane.reparentTo(render)
        taskMgr.add(self.move, "moveTask")
        self.keyMap = {"left":0, "right":0, "forward":0}
        self.prevtime = 0
        self.isMoving = False   

        self.setupLights()

        #set up collision
        #tail
        self.tail_cNode = CollisionNode("tail_"+name)
        self.tail_cSphere = CollisionSphere((0,28,26),13)
        self.tail_cNode.addSolid(self.tail_cSphere)
        self.tail_cNodePath = self.plane.attachNewNode(self.tail_cNode)
        self.tail_cNodePath.show()
        #outer wing left
        self.lwouter_cNode = CollisionNode("lwouter_"+name)
        self.lwouter_cSphere = CollisionSphere((-37,-10,22),8)
        self.lwouter_cNode.addSolid(self.lwouter_cSphere)
        self.lwouter_cNodePath = self.plane.attachNewNode(self.lwouter_cNode)
        self.lwouter_cNodePath.show()
        #outer wing right
        self.rwouter_cNode = CollisionNode("rwouter_"+name)
        self.rwouter_cSphere = CollisionSphere((37,-10,22),8)
        self.rwouter_cNode.addSolid(self.rwouter_cSphere)
        self.rwouter_cNodePath = self.plane.attachNewNode(self.rwouter_cNode)
        self.rwouter_cNodePath.show()
        #inner wing left
        self.lwinner_cNode = CollisionNode("lwinner_"+name)
        self.lwinner_cSphere = CollisionSphere((-20,-10,20),11)
        self.lwinner_cNode.addSolid(self.lwinner_cSphere)
        self.lwinner_cNodePath = self.plane.attachNewNode(self.lwinner_cNode)
        self.lwinner_cNodePath.show()
        #inner wing right
        self.rwinner_cNode = CollisionNode("rwinner_"+name)
        self.rwinner_cSphere = CollisionSphere((20,-10,20),11)
        self.rwinner_cNode.addSolid(self.rwinner_cSphere)
        self.rwinner_cNodePath = self.plane.attachNewNode(self.rwinner_cNode)
        self.rwinner_cNodePath.show()
        #body three pieces
        self.bodyfront_cNode = CollisionNode("bodyfront_"+name)
        self.bodyfront_cSphere = CollisionSphere((0,-29,22),8)
        self.bodyfront_cNode.addSolid(self.bodyfront_cSphere)
        self.bodyfront_cNodePath = self.plane.attachNewNode(self.bodyfront_cNode)
        self.bodyfront_cNodePath.show()
        self.bodymid_cNode = CollisionNode("bodymid_"+name)
        self.bodymid_cSphere = CollisionSphere((0,-12,22),12)
        self.bodymid_cNode.addSolid(self.bodymid_cSphere)
        self.bodymid_cNodePath = self.plane.attachNewNode(self.bodymid_cNode)
        self.bodymid_cNodePath.show()
        self.bodyrear_cNode = CollisionNode("bodyrear_"+name)
        self.bodyrear_cSphere = CollisionSphere((0,7,24),10)
        self.bodyrear_cNode.addSolid(self.bodyrear_cSphere)
        self.bodyrear_cNodePath = self.plane.attachNewNode(self.bodyrear_cNode)
        self.bodyrear_cNodePath.show()
        
        
       
        
        
    def setKey(self,key,value):
        self.keyMap[key] = value
    
    def move(self, task):
        elapsed = task.time - self.prevtime
        self.camera.lookAt(self.plane)
        if self.keyMap["left"]:
            self.plane.setH(self.plane.getH() + elapsed * 100)
        if self.keyMap["right"]:
            self.plane.setH(self.plane.getH() - elapsed * 100)
        if self.keyMap["forward"]:
            dist = 8 * elapsed
            angle = deg2Rad(self.plane.getH())
            dx = dist * math.sin(angle)
            dy = dist * -math.cos(angle)
            self.plane.setPos(self.plane.getX() + dx, self.plane.getY() + dy, 0)
            
        # if self.keyMap["left"] or self.keyMap["right"] or self.keyMap["forward"]:
            # if self.isMoving == False:
                # self.isMoving = True
                # self.plane.loop("walk")
        # else:
            # if self.isMoving:
                # self.isMoving = False
                # self.plane.stop()
                # self.plane.pose("walk", 4)
        
        self.prevtime = task.time
        return Task.cont
        
    def setupLights(self):
    
        spotlight = Spotlight('spotlight') 
        spotlight.setColor((.5,.5,.5,1)) 
        spotlight.setLens(PerspectiveLens()) 
        spotlight.getLens().setFov(18,18)
        spotlight.setAttenuation(Vec3(1.0,0.0,0.0)) 
        spotlight.setExponent(60) 

        spotlightNP = self.plane.attachNewNode(spotlight)	
        spotlightNP.setHpr(180,0,0) 

        render.setLight(spotlightNP)
        
        