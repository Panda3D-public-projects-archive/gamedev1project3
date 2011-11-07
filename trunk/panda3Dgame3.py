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
        
        #collision stuff
        self.accept("collide-tail_plane1", self.collisionTest)
        self.accept("collide-bodyfront_plane1", self.collisionTest)
        self.accept("collide-bodymid_plane1", self.collisionTest)
        self.accept("collide-bodyrear_plane1", self.collisionTest)
        self.accept("collide-lwouter_plane1", self.collisionTest)
        self.accept("collide-rwouter_plane1", self.collisionTest)
        self.accept("collide-lwinner_plane1", self.collisionTest)
        self.accept("collide-rwinner_plane1", self.collisionTest)
        self.accept("collide-tail_plane2", self.collisionTest)
        self.accept("collide-bodyfront_plane2", self.collisionTest)
        self.accept("collide-bodymid_plane2", self.collisionTest)
        self.accept("collide-bodyrear_plane2", self.collisionTest)
        self.accept("collide-lwouter_plane2", self.collisionTest)
        self.accept("collide-rwouter_plane2", self.collisionTest)
        self.accept("collide-lwinner_plane2", self.collisionTest)
        self.accept("collide-rwinner_plane2", self.collisionTest)
        
        #projectile/guns stuff
        self.accept("q",self.plane2.shoot)
        self.accept("/", self.plane1.shoot)
        
        
        
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
        self.plane1.plane.setPos(5,0,0)
        #add pieces for collisions
        #tail
        base.cTrav.addCollider(self.plane1.tail_cNodePath, self.cHandler)
        self.cHandler.addCollider(self.plane1.tail_cNodePath, self.plane1.plane)
        #outer wing left
        base.cTrav.addCollider(self.plane1.lwouter_cNodePath, self.cHandler)
        self.cHandler.addCollider(self.plane1.lwouter_cNodePath, self.plane1.plane)
        #outer wing right
        base.cTrav.addCollider(self.plane1.rwouter_cNodePath, self.cHandler)
        self.cHandler.addCollider(self.plane1.rwouter_cNodePath, self.plane1.plane)
        #inner wing left
        base.cTrav.addCollider(self.plane1.lwinner_cNodePath, self.cHandler)
        self.cHandler.addCollider(self.plane1.lwinner_cNodePath, self.plane1.plane)
        #inner wing right
        base.cTrav.addCollider(self.plane1.rwinner_cNodePath, self.cHandler)
        self.cHandler.addCollider(self.plane1.rwinner_cNodePath, self.plane1.plane)
        #body three pieces
        base.cTrav.addCollider(self.plane1.bodyfront_cNodePath, self.cHandler)
        self.cHandler.addCollider(self.plane1.bodyfront_cNodePath, self.plane1.plane)
        base.cTrav.addCollider(self.plane1.bodymid_cNodePath, self.cHandler)
        self.cHandler.addCollider(self.plane1.bodymid_cNodePath, self.plane1.plane)
        base.cTrav.addCollider(self.plane1.bodyrear_cNodePath, self.cHandler)
        self.cHandler.addCollider(self.plane1.bodyrear_cNodePath, self.plane1.plane)
        
        #player 2 plane
        self.plane2 = Plane(base.camList[1], "plane2")
        self.plane2.plane.setPos(23,6,0)
        #add pieces for collisions
        #tail
        base.cTrav.addCollider(self.plane2.tail_cNodePath, self.cHandler)
        self.cHandler.addCollider(self.plane2.tail_cNodePath, self.plane2.plane)
         #outer wing left
        base.cTrav.addCollider(self.plane2.lwouter_cNodePath, self.cHandler)
        self.cHandler.addCollider(self.plane2.lwouter_cNodePath, self.plane2.plane)
        #outer wing right
        base.cTrav.addCollider(self.plane2.rwouter_cNodePath, self.cHandler)
        self.cHandler.addCollider(self.plane2.rwouter_cNodePath, self.plane2.plane)
        #inner wing left
        base.cTrav.addCollider(self.plane2.lwinner_cNodePath, self.cHandler)
        self.cHandler.addCollider(self.plane2.lwinner_cNodePath, self.plane2.plane)
        #inner wing right
        base.cTrav.addCollider(self.plane2.rwinner_cNodePath, self.cHandler)
        self.cHandler.addCollider(self.plane2.rwinner_cNodePath, self.plane2.plane)
        #body three pieces
        base.cTrav.addCollider(self.plane2.bodyfront_cNodePath, self.cHandler)
        self.cHandler.addCollider(self.plane2.bodyfront_cNodePath, self.plane2.plane)
        base.cTrav.addCollider(self.plane2.bodymid_cNodePath, self.cHandler)
        self.cHandler.addCollider(self.plane2.bodymid_cNodePath, self.plane2.plane)
        base.cTrav.addCollider(self.plane2.bodyrear_cNodePath, self.cHandler)
        self.cHandler.addCollider(self.plane2.bodyrear_cNodePath, self.plane2.plane)
        
        
        
    def setupLights(self):
        #ambient light
        self.ambientLight = AmbientLight("ambientLight")
        #four values, RGBA (alpha is largely irrelevent), value range is 0:1
        self.ambientLight.setColor((.25, .25, .25, 1))
        self.ambientLightNP = render.attachNewNode(self.ambientLight)
        #the nodepath that calls setLight is what gets illuminated by the light
        render.setLight(self.ambientLightNP)
        #call clearLight() to turn it off
        
        render.setShaderAuto()
        
        
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
        if cEntry.getIntoNodePath().getParent() != cEntry.getFromNodePath().getParent():
            #print(str(cEntry.getIntoNodePath()) + " " + str(cEntry.getFromNodePath()))
            
            #plane 1 body
            if str(cEntry.getIntoNodePath())=="render/plane1/bodyfront_plane1" or str(cEntry.getIntoNodePath())=="render/plane1/bodymid_plane1" or str(cEntry.getIntoNodePath())=="render/plane1/bodyrear_plane1":
                self.plane1.body_hp-=1
                print("plane1 body hp = " + str(self.plane1.body_hp))
                #check for game over
                if(self.plane1.body_hp<=0):
                    print("plane1 dead!")
                    #remove whole plane
                    cEntry.getIntoNodePath().getParent().remove()
                
            #plane 2 body
            elif str(cEntry.getIntoNodePath()) == "render/plane2/bodyfront_plane2" or str(cEntry.getIntoNodePath())== "render/plane2/bodymid_plane2" or str(cEntry.getIntoNodePath())== "render/plane2/bodyrear_plane2":
                self.plane2.body_hp-=1
                print("plane2 body hp = " + str(self.plane2.body_hp))
                #check for game over
                if(self.plane2.body_hp<=0):
                    print("plane2 dead!")
                    #remove whole plane
                    cEntry.getIntoNodePath().getParent().remove()
                
            #plane 1 tail
            elif str(cEntry.getIntoNodePath()) == "render/plane1/tail_plane1":
                self.plane1.tail_hp-=1
                print("plane1 tail hp = " + str(self.plane1.tail_hp))
                if(self.plane1.tail_hp<=0):
                    print("plane1 lost tail!")
                    cEntry.getIntoNodePath().remove() #remove cnode
                    self.plane1.has_tail=False
                    
            #plane2 tail
            elif str(cEntry.getIntoNodePath()) =="render/plane2/tail_plane2":
                self.plane2.tail_hp-=1
                print("plane2 tail hp = " + str(self.plane2.tail_hp))
                if(self.plane2.tail_hp<=0):
                    print("plane2 lost tail!")
                    cEntry.getIntoNodePath().remove() # remove cnode
                    self.plane2.has_tail = False
                    
            #plane1 left outer wing
            elif str(cEntry.getIntoNodePath()) == "render/plane1/lwouter_plane1":
                self.plane1.lwo_hp-=1
                print("plane1 left outer wing hp = " + str(self.plane1.lwo_hp))
                if(self.plane1.lwo_hp<=0):
                    print("plane1 lost lwo!")
                    cEntry.getIntoNodePath().remove() #remove cnode
                    self.plane1.has_lwo= False 
                    
            #plane2 left outer wing
            elif str(cEntry.getIntoNodePath()) =="render/plane2/lwouter_plane2":
                self.plane2.lwo_hp-=1
                print("plane2 left outer wing hp = " + str(self.plane2.lwo_hp))
                if(self.plane2.lwo_hp<=0):
                    print("plane2 lost lwo!")
                    cEntry.getIntoNodePath().remove() #remove cnode
                    self.plane2.has_lwo = False
                      
            #plane1 right outer wing
            elif str(cEntry.getIntoNodePath()) =="render/plane1/rwouter_plane1":
                self.plane1.rwo_hp-=1
                print("plane1 right outer wing hp = " + str(self.plane1.rwo_hp))
                if(self.plane1.rwo_hp<=0):
                    print("plane1 lost rwo!")
                    cEntry.getIntoNodePath().remove() #remove cnode
                    self.plane1.has_rwo = False
                    
            #plane2 right outer wing
            elif str(cEntry.getIntoNodePath()) == "render/plane2/rwouter_plane2":
                self.plane2.rwo_hp-=1
                print("plane2 right outer wing hp = " + str(self.plane2.rwo_hp))
                if(self.plane2.rwo_hp<=0):
                    print("plane2 lost rwo!")
                    cEntry.getIntoNodePath().remove() #remove cnode
                    self.plane2.has_rwo=False
                    
            #plane1 left inner wing
            elif str(cEntry.getIntoNodePath()) == "render/plane1/lwinner_plane1":
                self.plane1.lwi_hp -=1
                print("plane1 left inner wing hp = " + str(self.plane1.lwi_hp))
                if(self.plane1.lwi_hp<=0):
                    print("plane1 lost lwi!")
                    cEntry.getIntoNodePath().remove() #remove cnode
                    self.plane1.has_lwi=False
                    #remove lwo too if it still exists
                    if(self.plane1.has_lwo):
                        self.plane1.lwouter_cNodePath.remove() 
                        self.plane1.has_lwo=False
                        print("and lwo!")
                    
            #plane 2 left inner wing
            elif str(cEntry.getIntoNodePath()) == "render/plane2/lwinner_plane2":
                self.plane2.lwi_hp-=1
                print("plane2 left inner wing hp = " + str(self.plane1.lwi_hp))
                if(self.plane2.lwi_hp<=0):
                    print("plane2 lost lwi!")
                    cEntry.getIntoNodePath().remove() #remove cnode
                    self.plane2.has_lwi=False
                    #remove lwo too if it still exists
                    if(self.plane2.has_lwo):
                        self.plane2.lwouter_cNodePath.remove()
                        self.plane2.has_lwo=False
                        print("and lwo!")
                    
            #plane 1 right inner wing
            elif str(cEntry.getIntoNodePath()) == "render/plane1/rwinner_plane1":
                self.plane1.rwi_hp-=1
                print("plane1 right inner wing hp = " + str(self.plane1.rwi_hp))
                if(self.plane1.rwi_hp<=0):
                    print("plane1 lost rwi!")
                    cEntry.getIntoNodePath().remove() #remove cnode
                    self.plane1.has_rwi=False
                    #remove rwo too if it still exists
                    if(self.plane1.has_rwo):
                        self.plane1.rwouter_cNodePath.remove()
                        self.plane1.has_rwo=False
                        print("and rwo!")
                    
            #plane 2 right inner wing
            elif str(cEntry.getIntoNodePath()) == "render/plane2/rwinner_plane2":
                self.plane2.rwi_hp-=1
                print("plane2 right inner wing hp = " + str(self.plane2.rwi_hp))
                if(self.plane2.rwi_hp<=0):
                    print("plane2 lost rwi!")
                    cEntry.getIntoNodePath().remove()
                    self.plane2.has_rwi=False
                    #remove rwo too if it still exists
                    if(self.plane2.has_rwo):
                        self.plane2.rwouter_cNodePath.remove()
                        self.plane2.has_rwo=False
                        print("and rwo!")
            else:
                "what the f$%k did I hit!?!"
                
                
                
            
        
        
w = World()
run()

