from direct.showbase.DirectObject import DirectObject  #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.task import Task
import sys, math, random
from direct.interval.IntervalGlobal import * #for compound intervals
from pandac.PandaModules import * #basic Panda modules
from Bullet import *

#GLOBALS
density = 5000
bulletVelocity = -1000
baseDrag = .05
fullThrottleForce = 1.5
gravityForce = 9.81

controlFactors = {
    "throttle":1,
    "pitch":100,
    "yaw":100,
    "roll":100
}

gravity = NodePath(ForceNode("gravity"))
gravity.reparentTo(render)
gravity.node().addForce(LinearVectorForce(Vec3.down(), gravityForce))

#base.enableParticles()

class MyPlane(DirectObject):
    def __init__(self,camera,name):
        #load model
        self.name = name
        self.np = None
        self.camera = camera
        self.canFireLeft = True
        self.canFireRight = True
        
        #init physics
        self.plane = render.attachNewNode(ActorNode(name))
        self.objMass = {
            "body":600,
            "tail":100,
            "outer":75,
            "inner":75
        }
        
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
        self.prevtime = 0

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
        
        #controls
        self.controls = {
            "throttle":0,
            "pitch":0,
            "yaw":0,
            "roll":0
        }
        
        #movement
        self.throttle = 1
        self.velocity = Vec3(0, 10, 0)
        #self.forces = ForceNode("control_forces")
        #NodePath(self.forces).reparentTo(self.plane)
        
        #self.throttleForce = LinearVectorForce(0, -1, 0, fullThrottleForce)
        #self.dragForce = LinearFrictionForce(baseDrag)
        #self.controlForce = AngularVectorForce(0, 0, 0)
        
        #self.forces.addForce(self.throttleForce)
        #self.forces.addForce(self.dragForce)
        #self.forces.addForce(self.controlForce)
        
        #self.plane.node().getPhysical(0).addLinearForce(self.throttleForce)
        #self.plane.node().getPhysical(0).addLinearForce(self.dragForce)
        #self.plane.node().getPhysical(0).addAngularForce(self.controlForce)
        
        #misc
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
        
    def runControl(self, control, direction):
        self.controls[control] += (1 if direction == "up" else -1) * controlFactors[control]
        print " ".join((control, direction))
        print self.controls
        
        
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
        
        #acceleration & drag
        thrust = self.plane.getQuat().getForward() * -1
        thrust.normalize()
        thrust *= (self.throttle * fullThrottleForce)
        self.velocity += thrust
        self.velocity *= (1 - baseDrag)
        
        #Forward Movement
        #self.throttleForce.setAmplitude(self.throttle * fullThrottleForce)
        self.plane.setPos(self.velocity * elapsed + self.plane.getPos())
        
        #angle movement
        hpr = VBase3(self.controls["yaw"] * elapsed,
                     self.controls["pitch"] * elapsed,
                     self.controls["roll"] * elapsed)
        
        self.plane.setHpr(self.plane, hpr)
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
        
        