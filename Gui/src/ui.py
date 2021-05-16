import tkinter as tk
import cv2
import PIL.Image, PIL.ImageTk
import time
import datetime as dt
import argparse
import playsound
from threading import Thread
import os
import blink_gui
import frontend
import random
from tkinter.simpledialog import askstring, askinteger
from tkinter.messagebox import showwarning

class App:
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source
        self.ok=False
        self.start_time = 0
        self.stop_time = 0
        self.t1 = Thread(target=self.timer_to_start)
        #create the gui window to input patient name
        self.first_name = askstring('Title', 'first name:')
        self.surname = askstring('Title', 'last name:')
        self.phone = askstring('Title', 'phone:')
        self.startle = False

        #timer
        self.timer=ElapsedTimeClock(self.window)
        # open video source (by default this will try to open the computer webcam)
        self.vid = VideoCapture(self.video_source)

        # Create a canvas that can fit the above video source size
        self.canvas = tk.Canvas(window, width = self.vid.width, height = self.vid.height)
        self.canvas.pack()

        # Button that lets the user take a snapshot
        self.btn_snapshot=tk.Button(window, text="Snapshot", command=self.snapshot)
        self.btn_snapshot.pack(side=tk.LEFT)

        #video control buttons
        self.btn_start=tk.Button(window, text='START', command=self.open_camera)
        self.btn_start.pack(side=tk.LEFT)

        #stop video button
        self.btn_stop=tk.Button(window, text='STOP', command=self.close_camera)
        self.btn_stop.pack(side=tk.LEFT)

        # quit button
        self.btn_quit=tk.Button(window, text='QUIT', command=quit)
        self.btn_quit.pack(side=tk.LEFT)

        #blink calculate button
        self.btn_calculate=tk.Button(window, text='Blink', command=self.calculate)
        self.btn_calculate.pack(side=tk.RIGHT)

        #graph button
        '''
        self.btn_graph=tk.Button(window, text='GRAPH', command=self.graph)
        self.btn_graph.pack(side=tk.RIGHT)
	'''

        #database button
        self.btn_db=tk.Button(window, text='DB', command=self.db)
        self.btn_db.pack(side=tk.RIGHT)

        #self.btn_pupil=tk.Button(window, text='PUPIL', command=self.pupil)
        #self.btn_pupil.pack(side=tk.LEFT)

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay=10
        self.update()

        self.window.mainloop()

    #startling sound
    def timer_to_start(self):  # thread function for to beeping and detecting blinks at the same time.
        """
        NO_PARAMS: It was suppose to take 2 arguments, to easy to manipulate the code
            we set the parameters that used in this function as global variables.
        Warning: This function works on the machines that have only Windows OS. It's not working on either
            Linux based OS and MacOS.
        """
        print("[INFO] sound thread begins...")
        # random wait before the startle sound
        for i in list(range(random.randint(1, 4)))[::-1]:
            print("[ATTENTION] Program starts in ", i + 1, "seconds.")
            time.sleep(i)
        '''
        while True:
            winsound.PlaySound('smashingSound.wav', winsound.SND_ASYNC)
            time.sleep(random.randint(1,5))
        '''
        playsound.playsound('smashingSound.wav')
        self.stop_time = time.time() - self.start_time

    #commented out do it being integrated into the blink code
    '''
    #function for displaying graphs
    def graph(self):
        if self.ok == False:
            g = Thread(target=plot_data.plot(self.first_name+"_"+ self.surname))
            g.daemon = True
            if once:
                g.start()
            	# print(sound_time)
                once = False
            g.join()
    '''
    #function for taking user mugshot may later be extended to add photo to database
    def snapshot(self):
        # Get a frame from the video source
        ret,frame=self.vid.get_frame()

        if ret:
            #cv2.imwrite("frame-"+time.strftime("%d-%m-%Y-%H-%M-%S")+".jpg",cv2.cvtColor(frame,cv2.COLOR_RGB2BGR))
            cv2.imwrite("snapshot"+".jpg",cv2.cvtColor(frame,cv2.COLOR_RGB2BGR))

    #start camera and thread
    def open_camera(self):
        self.ok = True
        self.timer.start()
        self.t1.daemon = True
        once = True
        if once:
            self.start_time = time.time()
            self.t1.start()
        	# print(sound_time)
            once = False

        print("camera opened => Recording")
        if self.startle == True:
            self.t1.join()
    #open the db window
    def db(self):
        if self.ok == False:
            g = Thread(target=frontend.main())
            g.daemon = True
            if once:
                g.start()
            	# print(sound_time)
                once = False
            g.join()

    #calculate the blinks from the output.avi video generated by the gui
    def calculate(self):
        #os.system('blink.py')
        camera = Thread(target=blink_gui.blink(self.first_name, self.surname, self.phone, self.stop_time))
        camera.daemon = True
        once = True
        if once:
            camera.start()
        	# print(sound_time)
            once = False
        camera.join()

    #stop recording
    def close_camera(self):
        self.ok = False
        self.timer.stop()


        print("camera closed => Not Recording")

    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()
        center_coordinates = (300, 300)
        axesLength = (120, 80)
        angle = 90
        startAngle = 0
        endAngle = 360
        # Red color in BGR
        color = (0, 0, 255)
        # Line thickness of 5 px
        thickness = 5
        # Using cv2.ellipse() method
        # Draw a ellipse with red line borders of thickness of 5 px
        frame = cv2.ellipse(frame, center_coordinates, axesLength,
               angle, startAngle, endAngle, color, thickness)
        if self.ok:
            self.vid.out.write(cv2.cvtColor(frame,cv2.COLOR_RGB2BGR))

        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tk.NW)
        self.window.after(self.delay,self.update)


class VideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Command Line Parser
        args=CommandLineParser().args


        #create videowriter

        # 1. Video Type
        VIDEO_TYPE = {
            'avi': cv2.VideoWriter_fourcc(*'XVID'),
            #'mp4': cv2.VideoWriter_fourcc(*'H264'),
            'mp4': cv2.VideoWriter_fourcc(*'XVID'),
        }

        self.fourcc=VIDEO_TYPE[args.type[0]]

        # 2. Video Dimension
        STD_DIMENSIONS =  {
            '480p': (640, 480),
            '720p': (1280, 720),
            '1080p': (1920, 1080),
            '4k': (3840, 2160),
        }
        res=STD_DIMENSIONS[args.res[0]]
        print(args.name,self.fourcc,res)
        self.out = cv2.VideoWriter(args.name[0]+'.'+args.type[0],self.fourcc,10,res)

        #set video sourec width and height
        self.vid.set(3,res[0])
        self.vid.set(4,res[1])

        # Get video source width and height
        self.width,self.height=res


    # To get frames
    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            else:
                return (ret, None)
        else:
            return (ret, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
            self.out.release()
            cv2.destroyAllWindows()


class ElapsedTimeClock:
    def __init__(self,window):
        self.T=tk.Label(window,text='00:00:00',font=('times', 20, 'bold'), bg='green')
        self.T.pack(fill=tk.BOTH, expand=1)
        self.elapsedTime=dt.datetime(1,1,1)
        self.running=0
        self.lastTime=''
        t = time.localtime()
        self.zeroTime = dt.timedelta(hours=t[3], minutes=t[4], seconds=t[5])
        # self.tick()


    def tick(self):
        # get the current local time from the PC
        self.now = dt.datetime(1, 1, 1).now()
        self.elapsedTime = self.now - self.zeroTime
        self.time2 = self.elapsedTime.strftime('%H:%M:%S')
        # if time string has changed, update it
        if self.time2 != self.lastTime:
            self.lastTime = self.time2
            self.T.config(text=self.time2)
        # calls itself every 200 milliseconds
        # to update the time display as needed
        # could use >200 ms, but display gets jerky
        self.updwin=self.T.after(100, self.tick)


    def start(self):
            if not self.running:
                self.zeroTime=dt.datetime(1, 1, 1).now()-self.elapsedTime
                self.tick()
                self.running=1

    def stop(self):
            if self.running:
                self.T.after_cancel(self.updwin)
                self.elapsedTime=dt.datetime(1, 1, 1).now()-self.zeroTime
                self.time2=self.elapsedTime
                self.running=0


class CommandLineParser:

    def __init__(self):

        # Create object of the Argument Parser
        parser=argparse.ArgumentParser(description='Script to record videos')

        # Create a group for requirement
        # for now no required arguments
        # required_arguments=parser.add_argument_group('Required command line arguments')

        # Only values is supporting for the tag --type. So nargs will be '1' to get
        parser.add_argument('--type', nargs=1, default=['avi'], type=str, help='Type of the video output: for now we have only AVI & MP4')

        # Only one values are going to accept for the tag --res. So nargs will be '1'
        parser.add_argument('--res', nargs=1, default=['480p'], type=str, help='Resolution of the video output: for now we have 480p, 720p, 1080p & 4k')

        # Only one values are going to accept for the tag --name. So nargs will be '1'
        parser.add_argument('--name', nargs=1, default=['output'], type=str, help='Enter Output video title/name')

        # Parse the arguments and get all the values in the form of namespace.
        # Here args is of namespace and values will be accessed through tag names
        self.args = parser.parse_args()



def main():
    # Create a window and pass it to the Application object
    App(tk.Tk(),'Video Recorder')
    window = tk.Tk()
    button_start = tk.Button(window, text='Start!', command=start)
    button_start.pack()  # for use with other widgets (that use grid), you must .grid() here
      # the GUI appears at this moment

main()
