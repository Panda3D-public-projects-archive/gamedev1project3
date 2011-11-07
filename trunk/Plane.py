from direct.showbase.DirectObject import DirectObject  #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.task import Task
import sys, math, random
from direct.interval.IntervalGlobal import * #for compound intervals
from pandac.PandaModules import * #basic Panda modules
from direct.interval.IntervalGlobal import *

class Plane(DirectObject):
    def __init__(self,camera,name):
        #load model
        self.name = name
        self.np = None
        self.camera = camera
        self.plane = render.attachNewNode(ActorNode(name))
        self.model = loader.loadModel("models/mig-3")
        self.model2 = loader.loadModel("models/panda-model")
        self.model2.setScale(.01)
        self.model2.setPos(0,-30,25)
        self.model2.setP(12)
        self.model2.setR(-3)
        self.model2.reparentTo(self.plane)
        self.model.reparentTo(self.plane)
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
       
        
    def setupCollision(self):
        #set up collision
        #tail
        self.tail_cNode = CollisionNode("tail_"+self.name)
        self.tail_cSphere = CollisionSphere((0,28,26),13)
        self.tail_cNode.addSolid(self.tail_cSphere)
        self.tail_cNodePath = self.plane.attachNewNode(self.tail_cNode)
        #self.tail_cNodePath.show()
        #outer wing left
        self.lwouter_cNode = CollisionNode("lwouter_"+self.name)
        self.lwouter_cSphere = CollisionSphere((-37,-10,22),8)
        self.lwouter_cNode.addSolid(self.lwouter_cSphere)
        self.lwouter_cNodePath = self.plane.attachNewNode(self.lwouter_cNode)
        #self.lwouter_cNodePath.show()
        #outer wing right
        self.rwouter_cNode = CollisionNode("rwouter_"+self.name)
        self.rwouter_cSphere = CollisionSphere((37,-10,22),8)
        self.rwouter_cNode.addSolid(self.rwouter_cSphere)
        self.rwouter_cNodePath = self.plane.attachNewNode(self.rwouter_cNode)
        #self.rwouter_cNodePath.show()
        #inner wing left
        self.lwinner_cNode = CollisionNode("lwinner_"+self.name)
        self.lwinner_cSphere = CollisionSphere((-20,-10,20),11)
        self.lwinner_cNode.addSolid(self.lwinner_cSphere)
        self.lwinner_cNodePath = self.plane.attachNewNode(self.lwinner_cNode)
        #self.lwinner_cNodePath.show()
        #inner wing right
        self.rwinner_cNode = CollisionNode("rwinner_"+self.name)
        self.rwinner_cSphere = CollisionSphere((20,-10,20),11)
        self.rwinner_cNode.addSolid(self.rwinner_cSphere)
        self.rwinner_cNodePath = self.plane.attachNewNode(self.rwinner_cNode)
        #self.rwinner_cNodePath.show()
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
        
        self.prevtime = task.time
        return Task.cont
        
    def shoot(self):
    #############################################################
    ## ATTENTION: if you get the error "global name 'Parabolaf' is
    ##not defined either a) pick up the latest release for fix or b)
    ##hand edit <panda location>/direct/interval/ProjectileInterval.py 
    ##and rename Parabolaf with LParabola
    #############################################################
    ############################################################
        print(self.name + " SHOOT")
        self.bullet = loader.loadModel("smiley")
        self.bullet.setScale(.5)
        self.bullet.reparentTo(render)
        self.bullet.setPos(self.plane.getX(), self.plane.getY(),self.plane.getZ()+5)
        self.trajectory = ProjectileInterval(self.bullet, startPos = Point3(self.bullet.getPos()),duration = 1, startVel = Vec3(0,10,0))
        self.trajectory.start()
        
    def setupLights(self):
        
        #Right Spotlight
        spotlight1 = Spotlight('spotlight') 
        spotlight1.setColor((.5,.5,.5,1)) 
        spotlight1.setLens(PerspectiveLens()) 
        spotlight1.getLens().setFov(15,15) 
        spotlight1.getLens().setNearFar(20,20) 
        spotlight1.setExponent(45)
        
        #Left Spotlight
        spotlight2 = Spotlight('spotlight') 
        spotlight2.setColor((.5,.5,.5,1)) 
        spotlight2.setLens(PerspectiveLens()) 
        spotlight2.getLens().setFov(15,15) 
        spotlight2.getLens().setNearFar(20,20) 
        spotlight2.setExponent(45)
        
        #Center Spotlight (Dimmer, can't be shot off)
        pointlight = PointLight('pointlight') 
        pointlight.setColor((.5,.5,.5,1))
        pointlight.setAttenuation(Point3(0,0,1))
        
        
        #Nodepath for right spotlight
        spotlightNP1 = self.plane.attachNewNode(spotlight1)
        spotlightNP1.setPos(VBase3(-30,0,20))
        spotlightNP1.setHpr(180,0,0) 
        spotlightNP1.setShaderAuto()
        spotlightNP1.setDepthOffset(1)
        
        #Nodepath for left spotlight
        spotlightNP2 = self.plane.attachNewNode(spotlight2)
        spotlightNP2.setPos(VBase3(30,0,20))
        spotlightNP2.setHpr(180,0,0) 
        spotlightNP2.setShaderAuto()
        spotlightNP2.setDepthOffset(1)
        
        #Nodepath for center spotlight
        pointlightNP = self.plane.attachNewNode(pointlight)
        pointlightNP.setPos(VBase3(0,-25,25))
        pointlightNP.setHpr(180,0,0) 
        pointlightNP.setShaderAuto()
        pointlightNP.setDepthOffset(1)

        render.setLight(spotlightNP1)
        render.setLight(spotlightNP2)
        render.setLight(pointlightNP)
        