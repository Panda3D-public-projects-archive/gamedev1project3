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

from panda3d.core import Vec3
from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletBoxShape


class World(DirectObject): #subclassing here is necessary to accept events
    def __init__(self):
        #turn off mouse control, otherwise camera is not repositionable
        base.disableMouse()
        
        #physics world
        self.physWorld = BulletWorld()
        self.physWorld.setGravity(Vec3(0,0,-9.81))
        
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
        
        
    def loadModels(self):
        """loads models into the world and set's their collision bodies"""
        #basic collision setup
        base.cTrav = CollisionTraverser()
        self.cHandler = CollisionHandlerEvent()
        
        #environment
        self.env = loader.loadModel("models/environment")
        self.env.reparentTo(render)
        self.env.setScale(.25)
        self.env.setPos(-8, 42, 0)   
        
        #player 1 plane
        self.plane1 = Plane(base.camList[0])
        np = render.attachNewNode(self.plane1.node)
        np.setPos(0,0,2)
        self.physWorld.attachRigidBody(self.plane1.node)
        self.plane1.plane.reparentTo(np)
        
        #player 2 plane
        self.plane2 = Plane(base.camList[1])
        np = render.attachNewNode(self.plane2.node)
        np.setPos(1,0,2)
        self.physWorld.attachRigidBody(self.plane2.node)
        self.plane2.plane.reparentTo(np)
        
        # plane2_body=OdeBody(self.physWorld)
        # plane2_body.setPosition(self.plane2.plane.getPos(render))
        # plane2_body.setQuaternion(self.plane2.plane.getQuat(render))
        # plane2_mass = OdeMass()
        # plane2_mass.setBox(11340,1,1,1)
        # plane2_body.setMass(plane2_mass)
        
        
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
        
        
w = World()
run()
