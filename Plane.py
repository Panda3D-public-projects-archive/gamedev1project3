from direct.showbase.DirectObject import DirectObject  #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.task import Task
import sys, math, random
from direct.interval.IntervalGlobal import * #for compound intervals
from pandac.PandaModules import * #basic Panda modules
from Bullet import *

#GLOBALS
bulletVelocity = -1000
baseDrag = .1
fullThrottleForce = 100

def maxVelocity():
    #return (1-baseDrag) * fullThrottleForce / baseDrag
    return 100

gravityForce = Vec3(0, 0, -30)

liftPower = (1, -1) #lift and angle

#rate of change, per second, of the various controls
controlFactors = {
    "throttle":1, #scales from 0 to 1
    
    #these scale from -Limit to Limit (see controlLimits, below)
    "pitch":200,
    "yaw":100,
    "roll":200
}

controlLimits = {
    "pitch":70,
    "yaw":30,
    "roll":50
}

class MyPlane(DirectObject):
    def __init__(self,camera,name):
        #load model
        self.name = name
        self.np = None
        self.camera = camera
        self.canFireLeft = True
        self.canFireRight = True
        self.fireRight = False #false for left side, true for right
        
        #init physics
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
            
        #self.model2 = loader.loadModel("models/panda-model")
        #self.model2.setScale(.008)
        #self.model2.setPos(0,40,-3)
        #self.model2.reparentTo(self.plane)
        #self.model.reparentTo(self.plane)
        
        #self.model_panda = loader.loadModel("models/panda-model")
        #self.model_panda.setScale(.008)
        #self.model_panda.setPos(5,0,0)
        #self.model_panda.reparentTo(self.plane)
        
        self.left_gun = self.plane.attachNewNode('left_gun')
        self.left_gun.setPos(14,-22,-5)
        self.right_gun = self.plane.attachNewNode('right_gun')
        self.right_gun.setPos(-14,-22,-5)
        self.plane.setScale(.05)
        self.plane.setH(180)
        
        #self.plane.reparentTo(render)
        taskMgr.add(self.move, "moveTask")
        self.prevtime = 0

        #hp levels for each piece of the plane
        self.body_hp= 50 #make it hard to blow up the body without making the player crash to the ground
        self.lwo_hp=1
        self.rwo_hp=1
        self.lwi_hp=2
        self.rwi_hp=2
        self.tail_hp=1

        #booleans for inventory of remaining plane parts
        #don't need to include body because obviously if body is lost then you are dead
        self.has_tail=True
        self.has_lwo=True
        self.has_lwi=True
        self.has_rwo=True
        self.has_rwi=True
        
        #controls
        self.resetControls()
        
        #movement
        self.throttle = .5
        self.velocity = Vec3(0, 0, 0)
        self.rotation = Vec3(0, 0, 0) #the current rotational velocity
        
        #misc
        self.setupCollision()
        self.setupLights()
        
        #camera on tail
        self.camera.reparentTo(self.plane)
        self.camera.setPos(0,120,30)
        self.camera.setH(180)
        self.camera.setP(-10)
        
    def resetControls(self):
        self.controls = {
            "throttle":0,
            "pitch":0,
            "yaw":0,
            "roll":0
        }
        
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
        
        self.accept("backspace", self.resetControls)
        
    def runControl(self, control, direction):
        self.controls[control] += (1 if direction == "up" else -1) * controlFactors[control]
        #print " ".join((control, direction))
        #print self.controls
        
        
    def mapKeys(self, forwardKey, backwardKey, control):
        self.accept(forwardKey, self.runControl, [control, "up"])
        self.accept(forwardKey + "-up", self.runControl, [control, "down"])
        self.accept(backwardKey, self.runControl, [control, "down"])
        self.accept(backwardKey + "-up", self.runControl, [control, "up"])
        
    def move(self, task):
        elapsed = task.time - self.prevtime
        #update controls
        
        #THROTTLE
        #throttle takes 1 full second to go from full to stop
        self.throttle += self.controls["throttle"] * elapsed
        if self.throttle > 1:
            self.throttle = 1
        if self.throttle < 0:
            self.throttle = 0
            
        for (i, axis) in enumerate(["yaw", "pitch", "roll"]):
            self.rotation.addToCell(i, self.controls[axis] * elapsed * max(self.velocity.length()/maxVelocity(), 1))
            if self.rotation.getCell(i) > controlLimits[axis]:
                self.rotation.setCell(i, controlLimits[axis])
            elif self.rotation.getCell(i) < -controlLimits[axis]:
                self.rotation.setCell(i, -controlLimits[axis])
                
            elif self.controls[axis] == 0 and self.rotation.getCell(i) > 0:
                self.rotation.addToCell(i, -controlFactors[axis] * elapsed * max(self.velocity.length()/maxVelocity(), 1))
                if self.rotation.getCell(i) < 0:
                    self.rotation.setCell(i, 0)
            elif self.controls[axis] == 0 and self.rotation.getCell(i) < 0:
                self.rotation.addToCell(i, controlFactors[axis] * elapsed * max(self.velocity.length()/maxVelocity(), 1))
                if self.rotation.getCell(i) > 0:
                    self.rotation.setCell(i, 0)
                
        
        #acceleration
        thrust = self.plane.getQuat().getForward() * -1
        thrust.normalize()
        thrust *= ((self.throttle**2) * fullThrottleForce) #x^2 used here for more expressive throttling
        self.velocity += thrust * elapsed
        
        #lift from wings
        #determine wing normal vector
        normal = self.plane.getQuat().getUp()
        #project velocity
        normal = self.velocity.project(normal)
        #length of this vector determines lift/drag
        normal = normal.length()
        self.velocity += liftPower[0] * elapsed * normal
        self.rotation.addY(liftPower[1] * elapsed * normal)
        
        #air drag
        self.velocity *= (1 - baseDrag)
        
        #gravity
        self.velocity += gravityForce * elapsed
        
        #Forward Movement
        #self.throttleForce.setAmplitude(self.throttle * fullThrottleForce)
        self.plane.setPos(self.velocity * elapsed + self.plane.getPos())
        
        #angle movement
        self.plane.setHpr(self.plane, self.rotation * elapsed)
        self.prevtime = task.time            
        
        return Task.cont
        
    def setupLights(self):        
        self.spotlight1 = Spotlight('spotlight1') 
        self.spotlight1.setColor((.6,.6,.6,1)) 
        self.spotlight1.setLens(PerspectiveLens()) 
        self.spotlight1.getLens().setFov(11,11) 
        self.spotlight1.getLens().setNearFar(2,2) 
        self.spotlight1.setExponent(5)
        
        self.spotlight2 = Spotlight('spotlight2') 
        self.spotlight2.setColor((.6,.6,.6,1)) 
        self.spotlight2.setLens(PerspectiveLens()) 
        self.spotlight2.getLens().setFov(11,11) 
        self.spotlight2.getLens().setNearFar(2,2) 
        self.spotlight2.setExponent(5)
        
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
        
        