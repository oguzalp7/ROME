"""
Author: Oguz Alp Saglam
Date: 05/15/2021
Latest draft for ROME-Pupilometer

The program aims to detect potential anomalies in human brain measuring eye pupil sizes.
Looks up for any pupil dilations.
Keeps the measurements both in JSON file locally and in MySQL database.
Visualize the results just after the test.
Has micro-controller communication integration, but commented out. (Serial Communication)

The source code of the pupilometer is refactored in April 2021 in more object oriented programming manner.

Partnerships: Binghamton University Thomas J. Watson College of Engineering and Applied Science and Vehware Company.
"""

# importing packages
import json  # json module to keep the data in serialized format
import math  # math library both for calculations
import os  # to process file i/o
import time  # time library to add timestamps for each iteration and filename
import cv2  # Computer Vision Library
import numpy as np  # linear algebra and math library
import serial  # serial communication library to receive messages from a micro-controller
import matplotlib.pyplot as plt  # plotting tool
import mysql.connector  # database connection library


__author__ = "Oguz Alp Saglam"


def cut_eyebrows(img):  # reduce height of the ROI
    """
    The Eye Haarcascade Classifier contains eyebrows, since we are trying to achieve binary image which contains black,
    and white colors inside. So, the eyebrows may cause problem detecting the pupils.
    PARAM: image (eye frame)
    """
    try:
        height, width = img.shape[:2]  # get height and width
        eyebrow_h = int(height / 4)  # reduce 25% height
        img = img[eyebrow_h:height, 0:width]  # cut eyebrows out (15 px), remap the image
        return img  # return
    except:
        pass  # eye might not detected, but we didn't want that to interrupt the program...


def process_image(img, blob_detector, threshold=30, iter_erode=2, iter_dilate=4):
    """
    Image processing function that applied on eye frames.
    PARAMS: image (eye frame), opencv blob detector, threshold value (the one on the sliders), morphological transforms
    """
    # image processing function that algorithm runs
    gray_frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # convert to 2D gray image
    _, img = cv2.threshold(gray_frame, threshold, 255, cv2.THRESH_BINARY)  # apply binary thresholding algorithm
    img = cv2.erode(img, None, iterations=iter_erode)  # morphological transformations
    img = cv2.dilate(img, None, iterations=iter_dilate)  # morphological transformations
    img = cv2.medianBlur(img, 5)  # remove the noise
    keypoints = blob_detector.detect(img)  # keypoints return from blob detector
    n_black_pix = np.sum(img == 0)  # number of total white pixels from processed image
    return keypoints, n_black_pix, img  # return keypoints to calculate area of the blob
    # number of white pixels to compare and proportion
    # and processed image


def dict_to_json(dictionary, outfile_name):
    """
     Converts Python dictionary to JSON object and saves it to specified directory.
    PARAMS: dictionary as input, name of the file.
    """
    outfile = open(outfile_name, 'w')  # open file in write mode
    json.dump(dictionary, outfile)  # write the dictionary data into file with JSON serialization format.


def nothing(x):
    """
    Required for sliders, temporary function. It can be removed after optimization and utilization of the environment
    and the system.
    """
    pass


def area_of_circle(diameter):
    """
    Calculate the area of a circle
    PARAMS: diameter (detected blobs are returning coordinates of the blob and diameter of the blob)
    """
    radius = diameter / 2  # keypoint.size returns a diameter, we need radius so diameter/2 = radius
    area = np.power(radius, 2) * math.pi  # circle area = radius*radius*PI
    return area  # return


class PupilDilation(object):
    def __init__(self, port="COM4", baudrate=9600):
        """
        -Pupilometer object
        takes serial port and baudrate as parameters in constructor.
        -example specification of serial ports in Windows: COM1, COM2...
        -example specification of serial ports in Ubuntu: /dev/ttyUSB0, /dev/ttyUSB1...
        -example specification of serial ports in Debian(Raspberry Pi): /dev/ttyACM0, /dev/ttyACM1...
        -If the computer is Unix based Operating System; it can be checked from terminal 'ls /dev/tty*' during the
        plugging in the serial cable(mostly USB cables are machine end side)
        -Baudrate is related to the frequency of the sending and receiving messages from/to micro-controller or
        a machine. So it is mandatory to test it, it will affect the frame per seconds in the camera manner of the
        program. Baudrates to be tested are; 9600, 19200, 28800, 38400, 57600, 76800, 115200
        """
        self.port = port  # specify the serial bus
        self.baud = baudrate  # specify the baudrate
        cv2.namedWindow('image')  # for sliders to come up in same window with the camera feed
        cv2.createTrackbar('thr_left', 'image', 0, 255, nothing)  # create slider for threshold value (left eye)
        cv2.createTrackbar('thr_right', 'image', 0, 255, nothing)  # create slider for threshold value (right eye)
        # specify haarcascade classifiers
        self.eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        # set blob detector parameters
        self.detector_params = cv2.SimpleBlobDetector_Params()
        self.detector_params.filterByArea = True
        self.detector_params.maxArea = 1500
        self.detector = cv2.SimpleBlobDetector_create(self.detector_params)

        self.cap = cv2.VideoCapture(0)  # specify the camera that we're going to use and open it.
        time.sleep(1)  # warm up the camera a bit
        # To use the serial bus comment out this section.
        # TODO: set the baudrate closer to the camera fps frequincy. Values between 4800 and 115200 must be tested.
        # self.serial_dev = serial.Serial(self.port, self.baud, timeout=0.1)
        # TODO: add a microcontroller and comment out this section

        # Bunch of global variables inside of a class
        self.right_pupil_area = 0
        self.left_pupil_area = 0
        self.left = None
        self.right = None
        self.eyes = None
        self.eye_center = 0
        self.frame = None
        self.left_eye_keypoints = []
        self.left_eye_wp = 0
        self.left_eye_processed = None
        self.right_eye_keypoints = []
        self.right_eye_wp = 0
        self.right_eye_processed = None
        self.luminance = 0
        self.data = {"name": "", "surname": "", "phone_num": ""}  # initial dictionary

    def detect_eyes(self):
        """
        This is the method that caused us to implement the code in object oriented programming manner.
        This method kept occurred bugs when implemented in traditional programming manner.
        """
        gray_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)  # reduce to 2D gray image
        self.eyes = self.eye_cascade.detectMultiScale(gray_frame, 1.3, 5)  # detect eyes
        width = np.size(self.frame, 1)  # get frame width
        height = np.size(self.frame, 0)  # get frame height
        for (x, y, w, h) in self.eyes:
            if y > height / 2:  # to make sure that we work on the upper face
                # just in case if program detects an eye around the mouth or nose etc.
                # because it can, there is no guarantee
                pass
            self.eye_center = x + w / 2  # get the eye center
            if self.eye_center < width * 0.5:  # if eye takes its place on left then we're busy with left_eye
                self.left = self.frame[y:y + h, x:x + w]  # left eye ROI
            else:  # if eye takes position in the right hand side on the image then right eye
                self.right = self.frame[y:y + h, x:x + w]  # right eye ROI
        return self.left, self.right  # return both eyes

    def runner(self):
        """
        Pupilometer's data gathering method.
        NO PARAMS: -
        """
        index = 0  # index to be set as keys in the dictionary
        while True:  # infinite loop
            temp_dict = {"timestamp": time.time()}  # create a temporary dictionary
            ret, self.frame = self.cap.read()  # read camera frames and prepare for image processing
            # self.luminance = int(self.serial_dev.readline())
            # TODO: add a microcontroller and comment out this section
            temp_dict["luminance"] = self.luminance  # until the commented section removed, it's equal to 0.
            try:
                self.detect_eyes()  # method call
                self.left = cut_eyebrows(self.left)  # remove eyebrows
                self.right = cut_eyebrows(self.right)  # remove eyebrows
                thr_left = cv2.getTrackbarPos('thr_left', 'image')  # get threshold values from sliders
                thr_right = cv2.getTrackbarPos('thr_right', 'image')  # get threshold values from sliders
                # process image function call
                self.left_eye_keypoints, self.left_eye_wp, self.left_eye_processed = process_image(self.left,
                                                                                                   self.detector,
                                                                                                   threshold=thr_left)
                # debug on output display
                cv2.drawKeypoints(self.left, self.left_eye_keypoints, self.left, (0, 0, 255),
                                  cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
                try:
                    # keypoints are lists(arrays)
                    # since we have only 1 keypoint with correct settings
                    # the for loop only iterates 1 time.
                    for keypoint_l in self.left_eye_keypoints:
                        l1_checkpoint = self.left_pupil_area
                        self.left_pupil_area = area_of_circle(
                            keypoint_l.size)  # keypoint.size returns diameter of the blob
                        l2_checkpoint = self.left_pupil_area
                        # so we used the diameter to calculate the area of the pupil blob
                        # print statement for information about both pupil area and total number of black pixels
                        if l1_checkpoint != l2_checkpoint:
                            print("left pupil area: ", self.left_pupil_area,
                                  "total number of black pixels for left eye: ",
                                  self.left_eye_wp)
                            temp_dict["left_pupil_area"] = int(self.left_pupil_area)
                except Exception as e:
                    print(e)
                # process image function call
                self.right_eye_keypoints, self.right_eye_wp, self.right_eye_processed = process_image(self.right,
                                                                                                      self.detector,
                                                                                                      threshold=
                                                                                                      thr_right)
                # debug on output display
                cv2.drawKeypoints(self.right, self.right_eye_keypoints, self.right, (0, 0, 255),
                                  cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
                try:
                    # keypoints are lists(arrays)
                    # since we have only 1 keypoint with correct settings
                    # the for loop only iterates 1 time.
                    for keypoint_r in self.right_eye_keypoints:
                        r1_checkpoint = self.right_pupil_area
                        self.right_pupil_area = area_of_circle(keypoint_r.size)
                        # keypoint.size returns diameter of the blob
                        r2_checkpoint = self.right_pupil_area
                        # so we used the diameter to calculate the area of the pupil blob
                        # print statement for information about both pupil area and total number of white pixels
                        if r1_checkpoint != r2_checkpoint:
                            print("right pupil area: ", self.right_pupil_area,
                                  "total number of black pixels for left eye: "
                                  , self.right_eye_wp)
                            # self.data["right_pupil_size"].append(self.right_pupil_area)
                            temp_dict["right_pupil_area"] = int(self.right_pupil_area)

                except Exception as e:
                    print(e)

                # for parsing, check if temp dictionary has left and right pupil area or not.
                if "right_pupil_area" in temp_dict and "left_pupil_area" in temp_dict:
                    # if it does, add temporal dictionary to main dictionary just like a matrix.
                    self.data[str(index)] = temp_dict   # specify the index as keys but remember to convert it to str.
                    index += 1  # increment index
            except:
                pass

            cv2.imshow("image", self.frame)  # display the results
            if cv2.waitKey(15) & 0xFF == ord('q'):  # press "q" to exit
                break

    def visualize_current(self):
        """visualizes the current patients data"""
        # remove the personal information to easy to iterate over desired data to plot.
        self.data.pop("name")
        self.data.pop("surname")
        self.data.pop("phone_num")

        # initalize 2 empty lists
        left_pupils = []
        right_pupils = []
        for i in range(len(self.data)):  # iterate in data dictionary
            # convert the dictionary to list in order to visualize
            left_pupils.append(int(self.data[str(i)]["left_pupil_area"]))
            right_pupils.append(int(self.data[str(i)]["right_pupil_area"]))

        data_len = [x for x in range(len(left_pupils))]  # prepare number of samples.

        # scatter plot of left pupil size
        plt.scatter(data_len, left_pupils)  # parameters are two lists or numpy array
        plt.xlabel("number of samples")  # label x-axis indicating what is there
        plt.ylabel("left pupil size")  # label y-axis indicating what is there
        plt.show()  # show the plotted graph

        plt.plot(data_len, left_pupils)  # parameters are two lists or numpy array
        plt.xlabel("number of samples")  # label x-axis indicating what is there
        plt.ylabel("left pupil size")  # label y-axis indicating what is there
        plt.show()  # show the plotted graph

        # scatter plot of right pupil size
        plt.scatter(data_len, right_pupils)  # parameters are two lists or numpy array
        plt.xlabel("number of samples")  # label x-axis indicating what is there
        plt.ylabel("right pupil size")  # label y-axis indicating what is there
        plt.show()  # show the plotted graph

        plt.plot(data_len, right_pupils)  # parameters are two lists or numpy array
        plt.xlabel("number of samples")  # label x-axis indicating what is there
        plt.ylabel("right pupil size")  # label y-axis indicating what is there
        plt.show()  # show the plotted graph

        # combination of 2 plots that we displayed above
        fig, axs = plt.subplots(2)
        axs[0].plot(data_len, left_pupils)  # first plot
        axs[0].set_title("left pupil size")  # title
        axs[1].plot(data_len, right_pupils)  # second plot
        axs[1].set_title("right pupil size")  # title
        plt.show()  # show the plotted graph


def insert_database(sql_command, patient_data):
    """
    Connect database to insert patient data into patient table in database.
    PARAMS: sql command(INSERT), patient data: consisting a tuple of name, surname and phone number.
    """
    # specify and connect to the database.
    db = mysql.connector.connect(host="", user="", password="", database="vehware-rome")
    cursor = db.cursor(buffered=True)

    cursor.execute(sql_command, patient_data)  # execute sql command from cursor
    db.commit()  # commit changes
    cursor.close()  # close db connection


def get_patient_id(sql_command):
    """
    Connect database to get patient id which inserted before.
    Since we keep our desired data under same patient id, we require the patient id to insert desired data to db.
    PARAM: SQL command (SELECT)
    """
    # specify and connect to the database.
    db = mysql.connector.connect(host="", user="", password="", database="vehware-rome")
    cursor = db.cursor(buffered=True)

    cursor.execute(sql_command)  # execute sql command in argumant of the function.

    result = cursor.fetchone()   # query just 1 data, we don't need to fetch all.

    cursor.close()  # close db connection
    return result[0]  # return id


def insert_pupil_data(sql_command, data_itself, patient_id):
    """
    Insert desired data to database.
    PARAMS: SQL Command(INSERT), dictionary, patient id that we queried
    """
    # connect database
    db = mysql.connector.connect(host="", user="", password="", database="vehware-rome")
    cursor = db.cursor(buffered=True)

    # iterate over keys of dictionary
    for key in data_itself:
        pupil_id = patient_id  # set pupil_id to patient_id
        timestamp = data_itself[key]["timestamp"]  # parse pupil_timestamp from dictionary element
        luminance = data_itself[key]["luminance"]  # parse luminance from dictionary element
        left_pupil_area = data_itself[key]["left_pupil_area"]  # parse left pupil area from dictionary element
        right_pupil_area = data_itself[key]["right_pupil_area"]  # parse right pupil area from dictionary element
        pupil_data = (pupil_id, timestamp, right_pupil_area, left_pupil_area, luminance)  # put data into a tuple
        cursor.execute(sql_command, pupil_data)  # execute the insert sql command
        db.commit()  # commit changes at each iteration
    cursor.close()  # close the connection


def main():
    """
    Driver function
    NO PARAMS: -
    """
    cwd = os.getcwd()  # get current path
    # try to create a folder called 'Patients' to keep the data in JSON format in that folder.
    try:
        os.mkdir(f"{cwd}/Patients")  # create folder method
    except OSError as e:
        print(e)  # prints that file already exists after first time running the program.
    # insert patient first so its SQL command:
    insert_patient_sql = "INSERT INTO patient(patient_name , patient_surname, patient_phone) VALUES (%s, %s, %s)"
    try:
        pupil = PupilDilation()  # create the pupilometer object
        pupil.runner()  # call data gathering method
        # after we gather data and save it in pupilometer's data attribute,
        # we ask for personal data to add to dictionary
        patient_name = input("Name: ")
        patient_surname = input("Surname: ")
        patient_phone = input("Phone: ")

        # add personal data to dictionary
        pupil.data["name"] = patient_name
        pupil.data["surname"] = patient_surname
        pupil.data["phone_num"] = patient_phone

        # save the dictionary as JSON formatted file in Patients folder
        dict_to_json(pupil.data, f"{cwd}/Patients/{patient_name}_{patient_surname}#{time.time()}.json")

        # call visualize current patients data
        pupil.visualize_current()

        # information about the proceeding to the next phase
        print("Patient Data File Created in JSON format, adding current patient to database")

        # function call prior to the insert patient personal data to database
        insert_database(insert_patient_sql, (patient_name, patient_surname, patient_phone))

        # to get patient id, SQL Query command:
        get_patient_id_query = f"SELECT patient_id FROM patient WHERE patient_name = '{patient_name}' AND " \
                               f"patient_surname = '{patient_surname}' AND patient_phone = '{patient_phone}' "

        # get patient id function call
        patient_id = get_patient_id(get_patient_id_query)

        # insert desired data SQL command:
        insert_pupil_sql = "INSERT INTO pupil(pupil_id, pupil_timestamp, pupil_right_area, pupil_left_area," \
                           " pupil_luminance) VALUES (%s,%s,%s,%s,%s)"
        try:
            """
            If exists, remove personal data from the dictionary in order to pre-process the dictionary to easy to parse.
            """
            pupil.data.pop("name")
            pupil.data.pop("surname")
            pupil.data.pop("phone_num")
        except Exception as e:
            print(e)
            pass
        # function call to insert desired data to database.
        insert_pupil_data(insert_pupil_sql, pupil.data, patient_id)
        print("Successfully inserted to the database.")  # print information message
    except Exception as e:  # preventing interruption of program caused by the potential errors or exceptions
        print(e)
        pass


if __name__ == '__main__':
    """
    Call the driver function.
    """
    main()
