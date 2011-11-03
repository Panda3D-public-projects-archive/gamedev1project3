from pandac.PandaModules import loadPrcFileData
from pandac.PandaModules import OdeWorld, OdeBody, OdeMass, Quat
loadPrcFileData('', 'win-size 800 640')
loadPrcFileData('', 'win-fixed-size #t')
from direct.directbase import DirectStart
from pandac.PandaModules import *    #basic Panda modules
from direct.showbase.DirectObject import DirectObject  #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import *  #for compound intervals
from direct.task import Task         #for update fuctions
import sys, math, random
from Plane import *


class World(DirectObject): #subclassing here is necessary to accept events
    def __init__(self):
        #turn off mouse control, otherwise camera is not repositionable
        base.disableMouse()
        
        #set up for split screen
        #first window (default window)
        wp = WindowProperties()
        wp.setTitle('player 1')
        base.win.requestProperties(wp)
        #second window
        w2 = base.openWindow()
        wp.setTitle('player 2')
        w2.requestProperties(wp)
        
        #set camera 1
        base.camList[0].setPosHpr(0,-15,7,0,-15,0)
        #set camera 2
        base.camList[1].setPosHpr(0,-15,7,0,-15,0)
        
        self.loadModels()
        self.setupLights()
        render.setShaderAuto() #you probably want to use this
        
        #input
        self.keyMap = {"left":0, "right":0, "forward":0}
        self.accept("escape", sys.exit)
        
        self.accept("arrow_up", self.plane1.setKey, ["forward", 1])
        self.accept("arrow_right", self.plane1.setKey, ["right", 1])
        self.accept("arrow_left", self.plane1.setKey, ["left", 1])
        self.accept("arrow_up-up", self.plane1.setKey, ["forward", 0])
        self.accept("arrow_right-up", self.plane1.setKey, ["right", 0])
        self.accept("arrow_left-up", self.plane1.setKey, ["left", 0])
        self.accept("w", self.plane2.setKey, ["forward", 1])
        self.accept("d", self.plane2.setKey, ["right", 1])
        self.accept("a", self.plane2.setKey, ["left", 1])
        self.accept("w-up", self.plane2.setKey, ["forward", 0])
        self.accept("d-up", self.plane2.setKey, ["right", 0])
        self.accept("a-up", self.plane2.setKey, ["left", 0])
        
        self.accept("collide-plane1", self.collisionTest)
        self.accept("collide-plane2", self.collisionTest)
        
        
        
    def loadModels(self): #collision detection also here (keep with models for organization's sake)
        """loads models into the world and set's their collision bodies"""
        #basic collision setup
        base.cTrav = CollisionTraverser()
        self.cHandler = PhysicsCollisionHandler()
        self.cHandler.setInPattern("collide-%in")
        
        #environment
        self.env = loader.loadModel("models/environment")
        self.env.reparentTo(render)
        self.env.setScale(.25)
        self.env.setPos(-8, 42, 0)   
        
        #player 1 plane
        self.plane1 = Plane(base.camList[0],"plane1")
        self.plane1.plane.setPos(5,5,5)
        base.cTrav.addCollider(self.plane1.cNodePath, self.cHandler)
        self.cHandler.addCollider(self.plane1.cNodePath, self.plane1.plane)
        
        #player 2 plane
        self.plane2 = Plane(base.camList[1], "plane2")
        self.plane2.plane.setPos(10,10,10)
        base.cTrav.addCollider(self.plane2.cNodePath, self.cHandler)
        self.cHandler.addCollider(self.plane2.cNodePath, self.plane2.plane)
        
        
        
    def setupLights(self):
        #ambient light
        self.ambientLight = AmbientLight("ambientLight")
        #four values, RGBA (alpha is largely irrelevent), value range is 0:1
        self.ambientLight.setColor((.25, .25, .25, 1))
        self.ambientLightNP = render.attachNewNode(self.ambientLight)
        #the nodepath that calls setLight is what gets illuminated by the light
        render.setLight(self.ambientLightNP)
        #call clearLight() to turn it off
        
        
        ##################################################
        ## Class code - example
        # self.keyLight = DirectionalLight("keyLight")
        # self.keyLight.setColor((.6,.6,.6, 1))
        # self.keyLightNP = render.attachNewNode(self.keyLight)
        # self.keyLightNP.setHpr(0, -26, 0)
        # render.setLight(self.keyLightNP)
        # self.fillLight = DirectionalLight("fillLight")
        # self.fillLight.setColor((.4,.4,.4, 1))
        # self.fillLightNP = render.attachNewNode(self.fillLight)
        # self.fillLightNP.setHpr(30, 0, 0)
        # render.setLight(self.fillLightNP)
        ######################################################
    
    def collisionTest(self, cEntry):
        print(cEntry.getIntoNodePath().getParent())
        
        
w = World()
run()

