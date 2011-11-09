from direct.showbase.DirectObject import DirectObject  #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.task import Task
import sys, math, random
from direct.interval.IntervalGlobal import * #for compound intervals
from pandac.PandaModules import * #basic Panda modules
from direct.interval.IntervalGlobal import *
from Bullet import *

density = 5000
bulletVelocity = -1000

class PlanePart(DirectObject):
    def __init__(self, name, hp, model, parent, sphereData):
        self.hp = hp
        self.max_hp = hp
        
        #collision model
        collision = CollisionSphere(*sphereData)
        self.collisionNode = CollisionNode(name + "_collision")
        self.collisionNode.addSolid(collision)
        self.collisionNode.reparentTo(parent)

class MyPlane(DirectObject):
    def __init__(self,camera,name):
        #load model
        self.name = name
        self.np = None
        self.camera = camera
        self.plane = render.attachNewNode(ActorNode(name))
        #self.model = loader.loadModel("models/mig-3")
        if self.name =="plane1":
            self.model_body = loader.loadModel("models/body_w")
            self.model_body.reparentTo(self.plane)
            self.model_tail = loader.loadModel("models/tail_w")
            self.model_tail.reparentTo(self.plane)
            self.model_rwo=loader.loadModel("models/right_tip_w")
            self.model_rwo.reparentTo(self.plane)
            self.model_lwo=loader.loadModel("models/left_tip_w")
            self.model_lwo.reparentTo(self.plane)
            self.model_rwi=loader.loadModel("models/right_wing_w")
            self.model_rwi.reparentTo(self.plane)
            self.model_lwi=loader.loadModel("models/left_wing_w")
            self.model_lwi.reparentTo(self.plane)
        else:
            self.model_body = loader.loadModel("models/body")
            self.model_body.reparentTo(self.plane)
            self.model_tail = loader.loadModel("models/tail")
            self.model_tail.reparentTo(self.plane)
            self.model_rwo=loader.loadModel("models/right_tip")
            self.model_rwo.reparentTo(self.plane)
            self.model_lwo=loader.loadModel("models/left_tip")
            self.model_lwo.reparentTo(self.plane)
            self.model_rwi=loader.loadModel("models/right_wing")
            self.model_rwi.reparentTo(self.plane)
            self.model_lwi=loader.loadModel("models/left_wing")
            self.model_lwi.reparentTo(self.plane)
            
        self.model2 = loader.loadModel("models/panda-model")
        self.model2.setScale(.008)
        self.model2.setPos(0,40,-3)
        self.model2.reparentTo(self.plane)
        #self.model.reparentTo(self.plane)
        self.plane.setScale(.05)
        self.plane.setH(180)
        #self.plane.reparentTo(render)
        taskMgr.add(self.move, "moveTask")
        self.keyMap = {"left":0, "right":0, "forward":0}
        self.prevtime = 0
        self.isMoving = False  

        #hp levels for each piece of the plane
        self.body_hp= 50 #make it hard to blow up the body without making the player crash to the ground
        self.lwo_hp=5
        self.rwo_hp=5
        self.lwi_hp=10
        self.rwi_hp=10
        self.tail_hp=12

        #booleans for inventory of remaining plane parts
        #don't need to include body because obviously if body is lost then you are dead
        self.has_tail=True
        self.has_lwo=True
        self.has_lwi=True
        self.has_rwo=True
        self.has_rwi=True
            
        self.setupCollision()
        self.setupLights()
        
        #camera on tail
        self.camera.reparentTo(self.plane)
        self.camera.setPos(0,120,30)
        self.camera.setH(180)
        self.camera.setP(-10)
        
        #bullet list
        self.bullets = []
       
        
    def setupCollision(self):
        #set up collision
        #tail
        self.tail_cNode = CollisionNode("tail_"+self.name)
        self.tail_cSphere = CollisionSphere((0,28,26),13)
        self.tail_cNode.addSolid(self.tail_cSphere)
        self.tail_cNodePath = self.plane.attachNewNode(self.tail_cNode)
        #self.tail_cNodePath.show()
        #outer wing right
        self.rwouter_cNode = CollisionNode("rwouter_"+self.name)
        self.rwouter_cSphere = CollisionSphere((-37,-10,22),8)
        self.rwouter_cNode.addSolid(self.rwouter_cSphere)
        self.rwouter_cNodePath = self.plane.attachNewNode(self.rwouter_cNode)
        #self.rwouter_cNodePath.show()
        #outer wing left
        self.lwouter_cNode = CollisionNode("lwouter_"+self.name)
        self.lwouter_cSphere = CollisionSphere((37,-10,22),8)
        self.lwouter_cNode.addSolid(self.lwouter_cSphere)
        self.lwouter_cNodePath = self.plane.attachNewNode(self.lwouter_cNode)
        #self.lwouter_cNodePath.show()
        #inner wing right
        self.rwinner_cNode = CollisionNode("rwinner_"+self.name)
        self.rwinner_cSphere = CollisionSphere((-20,-10,20),11)
        self.rwinner_cNode.addSolid(self.rwinner_cSphere)
        self.rwinner_cNodePath = self.plane.attachNewNode(self.rwinner_cNode)
        #self.rwinner_cNodePath.show()
        #inner wing left
        self.lwinner_cNode = CollisionNode("lwinner_"+self.name)
        self.lwinner_cSphere = CollisionSphere((20,-10,20),11)
        self.lwinner_cNode.addSolid(self.lwinner_cSphere)
        self.lwinner_cNodePath = self.plane.attachNewNode(self.lwinner_cNode)
        #self.lwinner_cNodePath.show()
        #body three pieces
        self.bodyfront_cNode = CollisionNode("bodyfront_"+self.name)
        self.bodyfront_cSphere = CollisionSphere((0,-29,22),8)
        self.bodyfront_cNode.addSolid(self.bodyfront_cSphere)
        self.bodyfront_cNodePath = self.plane.attachNewNode(self.bodyfront_cNode)
        #self.bodyfront_cNodePath.show()
        self.bodymid_cNode = CollisionNode("bodymid_"+self.name)
        self.bodymid_cSphere = CollisionSphere((0,-12,22),12)
        self.bodymid_cNode.addSolid(self.bodymid_cSphere)
        self.bodymid_cNodePath = self.plane.attachNewNode(self.bodymid_cNode)
        #self.bodymid_cNodePath.show()
        self.bodyrear_cNode = CollisionNode("bodyrear_"+self.name)
        self.bodyrear_cSphere = CollisionSphere((0,7,24),10)
        self.bodyrear_cNode.addSolid(self.bodyrear_cSphere)
        self.bodyrear_cNodePath = self.plane.attachNewNode(self.bodyrear_cNode)
        #self.bodyrear_cNodePath.show()
    
    def setKey(self,key,value):
        self.keyMap[key] = value
    
    def move(self, task):
        elapsed = task.time - self.prevtime
        #self.camera.lookAt(self.plane)
        if self.keyMap["left"]:
            self.plane.setH(self.plane.getH() + elapsed * 100)
        if self.keyMap["right"]:
            self.plane.setH(self.plane.getH() - elapsed * 100)
        if self.keyMap["forward"]:
            dist = 8 * elapsed
            angle = deg2Rad(self.plane.getH())
            dx = dist * math.sin(angle)
            dy = dist * -math.cos(angle)
            self.plane.setPos(self.plane.getX() + dx, self.plane.getY() + dy, self.plane.getZ())
        
        self.prevtime = task.time
        return Task.cont

        
    def setupLights(self):
        
        
        self.spotlight1 = Spotlight('spotlight1') 
        self.spotlight1.setColor((.6,.6,.6,1)) 
        self.spotlight1.setLens(PerspectiveLens()) 
        self.spotlight1.getLens().setFov(15,15) 
        self.spotlight1.getLens().setNearFar(20,20) 
        self.spotlight1.setExponent(45)
        
        self.spotlight2 = Spotlight('spotlight2') 
        self.spotlight2.setColor((.6,.6,.6,1)) 
        self.spotlight2.setLens(PerspectiveLens()) 
        self.spotlight2.getLens().setFov(15,15) 
        self.spotlight2.getLens().setNearFar(20,20) 
        self.spotlight2.setExponent(45)
        
        self.pointlight = PointLight('pointlight')
        self.pointlight.setColor((.15,.15,.15,1))
        

        
        self.spotlightNP1 = self.plane.attachNewNode(self.spotlight1)
        self.spotlightNP1.setPos(VBase3(-33,0,20))
        self.spotlightNP1.setHpr(175,0,0) 
        self.spotlightNP1.setShaderAuto()
        self.spotlightNP1.setDepthOffset(1)
        
        self.spotlightNP2 = self.plane.attachNewNode(self.spotlight2)
        self.spotlightNP2.setPos(VBase3(33,0,20))
        self.spotlightNP2.setHpr(185,0,0) 
        self.spotlightNP2.setShaderAuto()
        self.spotlightNP2.setDepthOffset(1)       
        
        self.pointlightNP = self.plane.attachNewNode(self.pointlight)
        self.pointlightNP.setPos(VBase3(0,0,20))
        self.pointlightNP.setHpr(180,0,0)
        self.pointlightNP.setShaderAuto()
        self.pointlightNP.setDepthOffset(1)
        

        render.setLight(self.spotlightNP1)
        render.setLight(self.spotlightNP2)
        render.setLight(self.pointlightNP)
        
        