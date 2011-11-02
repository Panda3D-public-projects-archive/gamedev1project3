from direct.showbase.DirectObject import DirectObject  #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.task import Task
import sys, math, random
from direct.interval.IntervalGlobal import * #for compound intervals
from pandac.PandaModules import * #basic Panda modules
   
class Plane(DirectObject):
    def __init__(self,camera):
        #load model
        self.camera = camera
        self.plane = Actor("models/panda-model", {"walk":"panda-walk4"})
        self.plane.setScale(.005)
        self.plane.setH(180)
        self.plane.reparentTo(render)
        taskMgr.add(self.move, "moveTask")
        self.keyMap = {"left":0, "right":0, "forward":0}
        self.prevtime = 0
        self.isMoving = False   

        self.setupLights()
        
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
            
        if self.keyMap["left"] or self.keyMap["right"] or self.keyMap["forward"]:
            if self.isMoving == False:
                self.isMoving = True
                self.plane.loop("walk")
        else:
            if self.isMoving:
                self.isMoving = False
                self.plane.stop()
                self.plane.pose("walk", 4)
        
        self.prevtime = task.time
        return Task.cont
        
    def setupLights(self):
    
        spotlight = Spotlight('spotlight') 
        spotlight.setColor((.5,.5,.5,1)) 
        spotlight.setLens(PerspectiveLens()) 
        spotlight.getLens().setFov(12,12)
        spotlight.setAttenuation(Vec3(1.0,0.0,0.0)) 
        spotlight.setExponent(60) 

        spotlightNP = self.plane.attachNewNode(spotlight)	
        spotlightNP.setHpr(180,0,0) 

        render.setLight(spotlightNP)