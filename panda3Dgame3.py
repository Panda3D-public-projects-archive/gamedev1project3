from pandac.PandaModules import loadPrcFileData
loadPrcFileData('', 'win-size 800 640')
loadPrcFileData('', 'win-fixed-size #t')
from direct.directbase import DirectStart
from pandac.PandaModules import *    #basic Panda modules
from direct.showbase.DirectObject import DirectObject  #for event handling
from direct.actor.Actor import Actor #for animated models
from direct.interval.IntervalGlobal import *  #for compound intervals
from direct.task import Task         #for update fuctions
import sys, math, random

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
        self.setupCollisions()
        render.setShaderAuto() #you probably want to use this
        self.keyMap = {"left":0, "right":0, "forward":0}
        self.accept("escape", sys.exit)
        
        ############################################
        ## Class code - example
        # taskMgr.add(self.move, "moveTask")
        # self.prevtime = 0
        # self.isMoving = False
        # self.accept("escape", sys.exit)
        # self.accept("arrow_up", self.setKey, ["forward", 1])
        # self.accept("arrow_right", self.setKey, ["right", 1])
        # self.accept("arrow_left", self.setKey, ["left", 1])
        # self.accept("arrow_up-up", self.setKey, ["forward", 0])
        # self.accept("arrow_right-up", self.setKey, ["right", 0])
        # self.accept("arrow_left-up", self.setKey, ["left", 0])
        # self.accept("ate-smiley", self.eat)
        
        ## "mouse1" is the event when the left mouse button is clicked
        ## append "-up" for the equivalent of a pygame.KEYUP event
        #######################################################
     
    def setKey(self, key, value):
        self.keyMap[key] = value     
        
    def loadModels(self):
        """loads models into the world"""
        self.panda = Actor("models/panda-model", {"walk":"panda-walk4"})
        self.panda.setScale(.005)
        self.panda.setH(180)
        self.panda.reparentTo(render)
        self.env = loader.loadModel("models/environment")
        self.env.reparentTo(render)
        self.env.setScale(.25)
        self.env.setPos(-8, 42, 0)        
        #load models here - see panda code for examples
        
    def	setupLights(self):
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
        
        
    def setupCollisions(self):
        #instantiates a collision traverser and sets it to the default
        base.cTrav = CollisionTraverser()
        self.cHandler = CollisionHandlerEvent()
        #set pattern for event sent on collision
        # "%in" is substituted with the name of the into object
        self.cHandler.setInPattern("collide-%in")
        
        ##################################################################
        ## Class code - example
        # cSphere = CollisionSphere((0,0,0), 500) #because the panda is scaled way down
        # cNode = CollisionNode("panda")
        # cNode.addSolid(cSphere)
        # cNode.setIntoCollideMask(BitMask32.allOff()) #panda is *only* a from object
        # cNodePath = self.panda.attachNewNode(cNode)
        ##cNodePath.show()
        ##registers a from object with the traverser with a corresponding handler
        # base.cTrav.addCollider(cNodePath, self.cHandler)
        
        # for target in self.targets:
            # cSphere = CollisionSphere((0,0,0), 2)
            # cNode = CollisionNode("smiley")
            # cNode.addSolid(cSphere)
            # cNodePath = target.attachNewNode(cNode)
            ##cNodePath.show()
        

w = World()
run()

