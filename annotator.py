from Tkinter import *
import tkFileDialog
import cv2
import os
from numpy import *
 
def select_image():
    # grab a reference to the image panels
    global panelA, panelB
 
    # open a file chooser dialog and allow the user to select an input
    # image
    path = tkFileDialog.askopenfilename()


class Window(Frame):


    def __init__(self, master=None):
        Frame.__init__(self, master)                 
        self.master = master
        
        self.drawing = False
        self.dragmode = True
        self.occluded = []
        #where are the fish tho
        self.centers = []
        self.boxUL = []
        self.boxLR = []
        self.boxW = []
        self.boxH = []
        self.fishCount = 1

        self.path = ''
        self.directory = ''
        self.numFishstr = "1"
        self.numFish = int(self.numFishstr)
        self.framenum=0

        self.font                   = cv2.FONT_HERSHEY_SIMPLEX
        self.blc = (10,50)
        self.fontScale              = 0.5
        self.fontColor              = (0,0,255)
        self.lineType               = 2

        self.init_window()
        self.fps = 30
        self.frameskips = '1'
        self.frameskip = 1

    #Creation of init_window
    def init_window(self):

        # changing the title of our master widget      
        self.master.title("GUI")

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)

        # creating a button instance
        quitButton = Button(self, text="Pick Video File",command=self.pickfile)
        # placing the button on my window
        quitButton.place(x=0, y=0)

        trackButton = Button(self,text="Begin Tracking",command = self.track)
        trackButton.place(x=0,y=30)

        #label and box for number of fish
        labelText=StringVar()
        labelText.set("# Fish")
        labelnumfish=Label(self, textvariable=labelText, height=1)
        labelnumfish.pack(side="left")

        self.numFish=StringVar(None)
        self.inputnumfish=Entry(self,textvariable=self.numFishstr,width=3)
        self.inputnumfish.pack(side="left")

        #label and box for frame skips
        skiplabelText=StringVar()
        skiplabelText.set("frame skips")
        labelskip=Label(self, textvariable=skiplabelText, height=1)
        labelskip.pack(side="left")

        self.frameskips=StringVar(None)
        self.inputskip=Entry(self,textvariable=self.frameskips,width=3)
        self.inputskip.pack(side="left")
        

    def pickfile(self):
        self.path = tkFileDialog.askopenfilename()


    def update_location(self,event,x,y,flags,param):
        if event==cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            if not self.dragmode:
                #this represents just a click
                self.centers[self.fishCount-1] = [x,y]
                self.boxUL[self.fishCount-1] = [self.centers[self.fishCount-1][0]-self.boxW[self.fishCount-1]/2,self.centers[self.fishCount-1][1]-self.boxH[self.fishCount-1]/2]
                self.boxLR[self.fishCount-1] = [self.centers[self.fishCount-1][0]+self.boxW[self.fishCount-1]/2,self.centers[self.fishCount-1][1]+self.boxH[self.fishCount-1]/2]
            else:
                self.boxUL[self.fishCount-1] = [x,y]

        elif event==cv2.EVENT_LBUTTONUP:
            self.drawing=False
            if self.dragmode:
                self.boxH[self.fishCount-1]=abs(self.boxUL[self.fishCount-1][1]-self.boxLR[self.fishCount-1][1])
                self.boxW[self.fishCount-1]=abs(self.boxUL[self.fishCount-1][0]-self.boxLR[self.fishCount-1][0])
                self.centers[self.fishCount-1] = [(self.boxUL[self.fishCount-1][0]+self.boxLR[self.fishCount-1][0])/2,(self.boxUL[self.fishCount-1][1]+self.boxLR[self.fishCount-1][1])/2]
        elif event==cv2.EVENT_MOUSEMOVE:
            if self.drawing==True:
                if self.dragmode:
                    self.boxLR[self.fishCount-1] = [x,y]
                else:
                    self.centers[self.fishCount-1]=[x,y]
                    self.boxUL[self.fishCount-1] = [self.centers[self.fishCount-1][0]-self.boxW[self.fishCount-1]/2,self.centers[self.fishCount-1][1]-self.boxH[self.fishCount-1]/2]
                    self.boxLR[self.fishCount-1] = [self.centers[self.fishCount-1][0]+self.boxW[self.fishCount-1]/2,self.centers[self.fishCount-1][1]+self.boxH[self.fishCount-1]/2]

    def track(self):
        done = False
        #load the capture
        cap = cv2.VideoCapture(self.path)
        #how long is the video
        vidlength = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
        #how many fish? from GUI
        self.numFish = int(self.inputnumfish.get())
        #initialize arrays 
        cv2.namedWindow('frame')
        cv2.setMouseCallback('frame',self.update_location)
        for ind in range(0,self.numFish):
            self.centers.append([None,None])#this will be x,y
            self.boxLR.append([None,None])
            self.boxUL.append([None,None])
            self.boxH.append(None)
            self.boxW.append(None)
            self.occluded.append(False)
        self.frameskip = int(self.inputskip.get())
        self.fps    = cap.get(cv2.cv.CV_CAP_PROP_FPS)
        while(not done):
            self.fishCount = 1
            ret, frame = cap.read()
            if frame is not None:
                self.framenum+=1
                frame_orig = frame.copy()
            else:
                done=True
                print("closing")

            # here are some keys
            # space is 32
            # n is 110
            
            #reset all "occluded" vars to false
            for ind in range(0,self.numFish):
                self.occluded[ind]=False

            if (self.framenum%self.frameskip) ==0:
                #wait for a key press
                for n in range(0,self.numFish):
                    key = ''
                    while (key!=32 and done==False):
                        if key==ord('q'):
                            done=True
                        if key==ord('m'):
                            self.dragmode = not self.dragmode
                        if key==ord('o'):
                            self.occluded[self.fishCount-1]= not self.occluded[self.fishCount-1]

                        frame = frame_orig.copy()
                        cv2.putText(frame,'select Fish '+str(self.fishCount)+', press space to advance', self.blc, self.font, self.fontScale,self.fontColor,self.lineType)
                        cv2.putText(frame,'frame '+str(self.framenum)+' of '+str(vidlength),(10,75), self.font, self.fontScale,self.fontColor,self.lineType)
                        if self.occluded[self.fishCount-1]==False:
                            cv2.putText(frame,'fish not occluded (o to mark)',(10,125), self.font, self.fontScale,self.fontColor,self.lineType)
                        else:
                            cv2.putText(frame,'fish is occluded (o to unmark)',(10,125), self.font, self.fontScale,self.fontColor,self.lineType)
                        
                        if self.dragmode:
                            cv2.putText(frame,'drag mode (m to change)',(10,100),self.font,self.fontScale,self.fontColor,self.lineType)
                        else:
                            cv2.putText(frame,'click mode (m to change)',(10,100),self.font,self.fontScale,self.fontColor,self.lineType)
                        #print self.boxUL
                        for ind in range(0,self.numFish):
                            if ((self.boxUL[ind][0]!=None) and (self.boxLR[ind][0]!=None)):
                                cv2.rectangle(frame,tuple(self.boxUL[ind]),tuple(self.boxLR[ind]),(0,255,0),2)
                        cv2.imshow('frame',frame)
                        key = cv2.waitKey(10)
                    self.fishCount+=1

                if not cap.isOpened():
                    done = True
                    print("closing")


                if key & 0xFF == ord('q'):
                    done = True
                    print("closing")
            

        cap.release()
        cv2.destroyWindow('frame')
        cv2.waitKey(1)
        print("closed")

root = Tk()
#size of the window
root.geometry("200x150")
app = Window(root)
root.mainloop()