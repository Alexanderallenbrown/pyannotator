#!/usr/bin/env python
from Tkinter import *
import tkFileDialog
import cv2
import os
from numpy import *
import sys
 
def select_image():
    # grab a reference to the image panels
    global panelA, panelB
 
    # open a file chooser dialog and allow the user to select an input
    # image
    path = tkFileDialog.askopenfilename()


class Window(Frame):


    def __init__(self, master=None):
        print sys.version
        print cv2.__version__
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
        self.shot=[]

        self.path = ''
        self.directory = ''
        self.posdir = ''
        self.negdir = ''
        self.framedir = ''
        self.vidfilename = ''
        self.vidfileext = ''
        self.numFishstr = "1"
        self.numFish = int(self.numFishstr)
        self.framenum=0
        self.trialnum=0

        self.font                   = cv2.FONT_HERSHEY_SIMPLEX
        self.blc = (10,50)
        self.fontScale              = 0.5
        self.fontColor              = (0,0,255)
        self.lineType               = 2

        self.init_window()
        self.fps = 30
        self.frameskips = '1'
        self.frameskip = 1
        self.classlabel = 'archerfish'

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
        self.vidfilename = os.path.split(self.path)[1]
        self.vidfileext = self.vidfilename[-4:]
        self.vidfilename = self.vidfilename[0:-4]
        
        print self.vidfilename
        self.directory = self.path[0:-4]+'/'
        self.posdir = self.directory+'pos/'
        self.negdir = self.directory+'neg/'
        self.framedir = self.directory+'frame/'
        print self.directory
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        if not os.path.exists(self.posdir):
            os.makedirs(self.posdir)
        if not os.path.exists(self.negdir):
            os.makedirs(self.negdir)
        if not os.path.exists(self.framedir):
            os.makedirs(self.framedir)
        self.trackfile = open(self.directory+self.vidfilename+'_track.txt','wb')
        self.annotfile = open(self.framedir+self.vidfilename+'_annotations.csv','wb')
        self.annotfile.write('Filename,   Annotation tag,  Upper left corner X, Upper left corner Y, Lower right corner X,   Lower right corner Y,    Occluded,    Origin file, Origin frame number\r\n')
        

    def checkbb(self,ulx,uly,lrx,lry):
        #check if any of the corner points of this bounding box are inside any of the bounding boxes we have
        #if this is a good box, return True.
        #pull out all xy points for this query box
        points = [[ulx,uly],[lrx,uly],[ulx,lry],[lrx,lry]]
        check = True #start with the assumption that this box is AOK.
        for ind in range(0,self.numFish):
            for corn in range(0,4):
                cornx,corny = points[corn][0],points[corn][1]
                if ((cornx>self.boxUL[ind][0])and(cornx<self.boxLR[ind][0])):
                    if ((corny>self.boxUL[ind][1])and(corny<self.boxLR[ind][1])):
                        check = False
                        print "found ya"
        return check






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
        #vidlength = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
        vidlength = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
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
            self.shot.append(False)
        self.frameskip = int(self.inputskip.get())
        # self.fps    = cap.get(cv2.cv.CV_CAP_PROP_FPS)
        self.fps    = cap.get(cv2.CAP_PROP_FPS)
        while(not done):
            self.fishCount = 1
            ret, frame = cap.read()
            height,width,depth = frame.shape
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
                self.shot[ind] = False


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
                        if key==ord('t'):
                            self.trialnum+=1
                        if key==ord('s'):
                            self.shot[self.fishCount-1]= not self.shot[self.fishCount-1]

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

                        cv2.putText(frame,'trial: '+str(self.trialnum)+' (t to increment)',(10,150),self.font,self.fontScale,self.fontColor,self.lineType)
                        cv2.putText(frame,'this fish shot now: '+str(self.shot[self.fishCount-1])+'(s to toggle)',(10,175),self.font,self.fontScale,self.fontColor,self.lineType)
                        #print self.boxUL
                        for ind in range(0,self.numFish):
                            if ((self.boxUL[ind][0]!=None) and (self.boxLR[ind][0]!=None)):
                                cv2.rectangle(frame,tuple(self.boxUL[ind]),tuple(self.boxLR[ind]),(0,255,0),2)
                        cv2.imshow('frame',frame)
                        key = cv2.waitKey(10)
                    self.fishCount+=1

                print('writing for frame '+str(self.framenum))
                #now all fish have been tracked. Time to store things
                #first write to the track file
                timenow = 1.0*self.framenum/self.fps
                self.trackfile.write(str(timenow)+'\t')
                self.trackfile.write(str(self.framenum)+'\t')
                #write trial number to file
                self.trackfile.write(str(self.trialnum)+'\t')
                #now loop through all fish and write x,y,x,y,etc
                for ind in range(0,self.numFish):
                    self.trackfile.write(str(self.centers[ind][0])+'\t'+str(self.centers[ind][1])+'\t')
                    self.trackfile.write(str(self.shot[ind])+'\t')
                self.trackfile.write('\r\n')

                #now save the full original frame write the annotations file for the frame
                framefilename = self.vidfilename+'_'+str(self.framenum)+'.jpg'
                cv2.imwrite(self.framedir+framefilename, frame_orig)
                #format for annotation file:
                #Filename   Annotation tag  Upper left corner X Upper left corner Y Lower right corner X    Lower right corner Y    Occluded    Origin file Origin frame number
                #there should be numFish annotations per frame!! ALWAYS!!
                for ind in range(0,self.numFish):
                    self.annotfile.write(framefilename+',')
                    self.annotfile.write(self.classlabel+',')
                    self.annotfile.write(str(self.boxUL[ind][0])+',')
                    self.annotfile.write(str(self.boxUL[ind][1])+',')
                    self.annotfile.write(str(self.boxLR[ind][0])+',')
                    self.annotfile.write(str(self.boxLR[ind][1])+',')
                    self.annotfile.write(str(int(self.occluded[ind]))+',')
                    self.annotfile.write(self.vidfilename+self.vidfileext+',')
                    self.annotfile.write(str(self.framenum)+'\r\n')

                #finally, save the basic pos/neg images for each fish.
                for ind in range(0,self.numFish):
                    poscrop = frame_orig[self.centers[ind][1]-self.boxH[ind]/2:self.centers[ind][1]+self.boxH[ind]/2,self.centers[ind][0]-self.boxW[ind]/2:self.centers[ind][0]+self.boxH[ind]/2,:]
                    posfilename = self.posdir+self.vidfilename+'_'+str(self.framenum)+'_'+str(ind)+'.jpg'
                    cv2.imwrite(posfilename,poscrop)
                #now that all positive crops have been saved, let's automatically generate the same number of negatives
                #this should save 4 negatives for each fish, but won't save all if there is a problem
                negfilename = self.negdir+self.vidfilename+'_'+str(self.framenum)
                for ind in range(0,self.numFish):
                    #try a negative to the right of this fish
                    ulx,uly = self.centers[ind][0]+self.boxW[ind]/2,self.centers[ind][1]-self.boxH[ind]/2
                    lrx,lry = self.centers[ind][0]+3*self.boxW[ind]/2,self.centers[ind][1]+self.boxH[ind]/2
                    #now make sure this is in bounds
                    if ((ulx>0)and(lrx)<width):
                        if ((uly>0)and(lry<height)):
                            #now check to see if this overlaps with a fish
                            if(self.checkbb(ulx,uly,lrx,lry)):
                                neg = frame_orig[uly:lry,ulx:lrx,:]
                                cv2.imwrite(negfilename+'_'+str(ind)+'_r.jpg',neg)
                                #print('wrote right neg')

                    #try a negative to the left of this fish
                    ulx,uly = self.centers[ind][0]-3*self.boxW[ind]/2,self.centers[ind][1]-self.boxH[ind]/2
                    lrx,lry = self.centers[ind][0]-self.boxW[ind]/2,self.centers[ind][1]+self.boxH[ind]/2
                    
                    if ((ulx>0)and(lrx)<width):
                        if ((uly>0)and(lry<height)):
                            #now check to see if this overlaps with a fish
                            if(self.checkbb(ulx,uly,lrx,lry)):
                                neg = frame_orig[uly:lry,ulx:lrx,:]
                                cv2.imwrite(negfilename+'_'+str(ind)+'_l.jpg',neg)
                                #print('wrote left neg')

                    #try a negative above this fish
                    ulx,uly = self.centers[ind][0]-self.boxW[ind]/2,self.centers[ind][1]-3*self.boxH[ind]/2
                    lrx,lry = self.centers[ind][0]+self.boxW[ind]/2,self.centers[ind][1]-self.boxH[ind]/2

                    if ((ulx>0)and(lrx)<width):
                        if ((uly>0)and(lry<height)):
                            #now check to see if this overlaps with a fish
                            if(self.checkbb(ulx,uly,lrx,lry)):
                                neg = frame_orig[uly:lry,ulx:lrx,:]
                                cv2.imwrite(negfilename+'_'+str(ind)+'_u.jpg',neg)
                                #print('wrote up neg')

                    #try a negative below this fish
                    ulx,uly = self.centers[ind][0]-self.boxW[ind]/2,self.centers[ind][1]+self.boxH[ind]/2
                    lrx,lry = self.centers[ind][0]+self.boxW[ind]/2,self.centers[ind][1]+3*self.boxH[ind]/2
                    
                    if ((ulx>0)and(lrx)<width):
                        if ((uly>0)and(lry<height)):
                            #now check to see if this overlaps with a fish
                            if(self.checkbb(ulx,uly,lrx,lry)):
                                neg = frame_orig[uly:lry,ulx:lrx,:]
                                cv2.imwrite(negfilename+'_'+str(ind)+'_d.jpg',neg)
                                #print('wrote down neg')

                #now check to see if capture is open
                if not cap.isOpened():
                    done = True
                    print("closing")

                #handle quit key
                if key == ord('q'):
                    done = True
                    print("closing")
            
        self.annotfile.close()
        self.trackfile.close()
        cap.release()
        cv2.destroyWindow('frame')
        cv2.waitKey(1)
        print("closed")

root = Tk()
#size of the window
root.geometry("200x150")
app = Window(root)
root.mainloop()