# importing libraries and modules
from scipy.spatial import distance as dist  # math library both for calculations and increase the calculation speed.
from imutils import face_utils  # helper module for dlib face AI
import imutils  # helper module for computer vision library.
import time  # to keep the time differences, time library
import dlib  # Face Landmark AI Library
import cv2  # Computer Vision Library
from playsound import playsound  # Sound module to play a specific sound in the program
from threading import Thread  # multi threading module
import random  # to play the sound in a random period, we aimed to surprise the patients
import os  # to process file i/o
import json  # json module to keep the data in serialized format
import matplotlib.pyplot as plt  # plotting tool
import mysql.connector  # database connection library

def visualize_current(dict_data, desired_seconds=5):
    """
    Visualizes the current patients data
    PARAMS: dictionary and desired number of seconds
    -In the program we used dictionaries to keep the data, because they are easy to parse, and faster than arrays
    -Number of desired seconds are basically X axis for the delay graph, it set to 5 as default.
    """
    # get the initial values of the dictionary and save them in variables.
    _name = dict_data["name"]
    _surname = dict_data["surname"]
    _phone = dict_data["phone"]
    delay = dict_data["delay"]
    total_blinks = dict_data["total_blinks"]

    # after getting the initial values, remove them to easy to iterate over desired data to plot.
    dict_data.pop("name")
    dict_data.pop("surname")
    dict_data.pop("delay")
    dict_data.pop("total_blinks")
    dict_data.pop("phone")

    # prepare X axis for delay graph
    seconds = [x for x in range(desired_seconds)]

    # prepare Y axis for delay graph
    delay_ = []  # initialize an empty list
    for i in range(desired_seconds):  # iterate number of desired seconds to match the same size with X-axis
        delay_.append(delay)  # append the same value 5 times.

    # line chart of delay between sound and the first blink
    plt.plot(seconds, delay_)  # parameters are two lists or numpy array
    plt.xlabel(f"{desired_seconds} seconds")  # label x-axis indicating what is there
    plt.ylabel("delay")  # label y-axis indicating what is there
    plt.show()  # show the plotted graph

    durations = []  # initialize an empty list
    for key in dict_data:  # after clean up the general data such as name and surname, iterate over desired data
        # append durations to the empty list that initialized 2 lines above
        durations.append(dict_data[key]["duration"])

    # prepare x-axis, which will be number of samples, number of blinks occured during the test.
    sample_len = [x for x in range(len(dict_data))]

    # scatter plot
    plt.scatter(sample_len, durations)  # parameters are two lists or numpy array
    plt.xlabel("number of samples")  # label x-axis indicating what is there
    plt.ylabel("durations")  # label y-axis indicating what is there
    plt.show()  # show the plotted graph

    # line chart
    plt.plot(sample_len, durations)  # parameters are two lists or numpy array
    plt.xlabel("number of samples")  # label x-axis indicating what is there
    plt.ylabel("durations")  # label y-axis indicating what is there
    plt.show()  # show the plotted graph

    # combination of 3 plots that we displayed above
    fig, axs = plt.subplots(3)
    axs[0].plot(seconds, delay_)  # parameters are two lists or numpy array
    axs[0].set_title("delay")  # title of the first chart
    axs[1].plot(sample_len, durations)  # parameters are two lists or numpy array
    axs[1].set_title("duration line chart")  # title of the second chart
    axs[2].scatter(sample_len, durations)  # parameters are two lists or numpy array
    axs[2].set_title("duration scatter chart")  # title of the third chart
    plt.show()  # show the plotted graph

    # since we removed 5 piece of data from dictionary, we still require delay data in outer scope
    # we'll use it to upload all the data into our database.
    return delay  # return


def json_to_dict(input_file):
    """
    Read JSON file and converts to a Python dictionary.
    PARAM: JSON file path
    Potential TODO: extention check may added to this function.
    """
    file = open(input_file, 'r')  # Open file in Read Mode
    data = json.load(file)  # load file as dictionary
    return data  # return the output


def dict_to_json(dictionary, outfile_name):
    """
    Converts Python dictionary to JSON object and saves it to specified directory.
    PARAMS: dictionary as input, name of the file.
    """
    outfile = open(outfile_name, 'w')  # open file in write mode
    json.dump(dictionary, outfile)  # write the dictionary data into file with JSON serialization format.


def timer_to_start():  # thread function for to play the sound and detecting blinks at the same time.
    """
    NO_PARAMS
    Threaded function that must be run at the same time when we start reading the camera.
    """
    time.sleep(1)  # wait for 1 seconds to camera to warm up and run almost synchronous with the camera.
    playsound('smashingSound.wav')  # play a dummy but triggering sound from the directory.


def EAR(eye):
    """
    The function is referenced from https://www.pyimagesearch.com/2017/04/24/eye-blink-detection-opencv-python-dlib/
    Further understanding and history behind the Eye Aspect Ratio is well documented in the link 1 line above.
    """
    # compute the euclidean distances between the two sets of
    # vertical eye landmarks (x, y)-coordinates
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])

    # compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    C = dist.euclidean(eye[0], eye[3])

    # compute the eye aspect ratio
    ratio = (A + B) / (2.0 * C)

    # return the eye aspect ratio
    return ratio


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
    # open and connect database connection
    db = mysql.connector.connect(host="", user="", password="", database="vehware-rome")
    cursor = db.cursor(buffered=True)

    # execute sql command in argumant of the function.
    cursor.execute(sql_command)

    # query just 1 data, we don't need to fetch all.
    result = cursor.fetchone()

    cursor.close()  # close db connection
    return result[0]  # return the id as integer.


def insert_blink_data(sql_command, data_itself, patient_id, blink_delay):
    """
    Insert desired data to database.
    PARAMS: SQL Command(INSERT), dictionary, patient id that we queried, blink delay
    """
    # connect database
    db = mysql.connector.connect(host="", user="", password="", database="vehware-rome")
    cursor = db.cursor(buffered=True)

    # iterate over keys of dictionary
    for key in data_itself:
        blink_id = patient_id  # set blink_id to patient_id
        timestamp = data_itself[key]["timestamp"]  # parse blink_timestamp from dictionary element
        duration = data_itself[key]["duration"]  # parse blink_duration from dictionary element
        # since cursor expects tuple, add the desired data into a tuple
        pupil_data = (blink_id, timestamp, duration, blink_delay)
        cursor.execute(sql_command, pupil_data)  # execute insert command
        db.commit()  # commit changes in each iteration
    cursor.close()  # after inserting rows close the connection.

def blink(name,surname,phone,stop):
    cwd = os.getcwd()  # get current path
    # try to create a folder called "Patient" if doesn't exists.
    try:
        os.mkdir("Patients")  # create folder method
    except OSError as e:
        print(e)  # prints that file already exists after first time running the program.

    # initialize the dictionary with initial items, no desired data
    patient_dict = {"name": "", "surname": "", "phone": "", "delay": 0, "total_blinks": 0}

    global timer  # global variable that will be used in threaded timer function.
    duration_start = 0  # to keep track of blink duration
    duration_end = 0  # to keep track of blink duration
    EYE_AR_THRESH = 0.3  # Eye Aspect Ratio Threshold
    # if calculated ear is lower than this threshold, it means blink occurred
    EYE_AR_CONSEC_FRAMES = 3  # the number of consecutive frames the eye must be below the threshold

    # initialize the frame counters and the total number of blinks
    COUNTER = 0
    TOTAL = 0

    once = True  # at this stage we wanted to sound the beeping just for once
    idx = 0  # data index to be set as key to the dictionary.

    print("[INFO] loading facial landmark predictor...")
    detector = dlib.get_frontal_face_detector()  # load dlib face detector (HOG + Linear SVM)
    predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')  # load pre-trained AI model

    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]  # use helper module to get left eye point id's.
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]  # use helper module to get right eye point id's.

    print("[INFO] starting video stream thread...")
    cap = cv2.VideoCapture("output.avi")  # output of the gui
    fileStream = True
    time.sleep(stop)
    sound_time_ms = time.time()
    while True:
        ret, frame = cap.read()  # read camera payload for image processing.
        if frame is None:
            break
        frame = imutils.resize(frame, width=450)  # with using helper module resize current frame's width to 450 pixels
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # convert current frame to grayscale(reduce to 2D image)
        rects = detector(gray, 0)  # detector expects grayscale image as parameter to find faces in rectangles
        for rect in rects:

            # determine the facial landmarks for the face region, then
            # convert the facial landmark (x, y)-coordinates to a NumPy array
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            # extract the left and right eye coordinates, then use the
            # coordinates to compute the eye aspect ratio for both eyes
            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]
            leftEAR = EAR(leftEye)
            rightEAR = EAR(rightEye)

            # average the eye aspect ratio together for both eyes
            ear = (leftEAR + rightEAR) / 2.0

            # debug on the camera indicating that detection of left and right eyes
            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, (255, 0, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (255, 0, 0), 1)

            if ear < EYE_AR_THRESH:
                """
                Blink occurred here, but we use number of ear consecutive frame to filter the blinks except the first blink
                because, we also aimed to find delay between the very first blink and the startle sound.
                """
                duration_start = time.time()  # get blink_duration starting timestamp
                blink_time = time.time()  # get blink timestamp for calculating delay
                delay_ms = blink_time - sound_time_ms  # calculate delay
                COUNTER += 1  # increment counter by one

                if sound_time_ms != 0:  # if sound_time is not in initial value, than it should be right value
                    print("blink delay after sound is ", delay_ms, " seconds")  # information line
                    patient_dict["delay"] = delay_ms  # append the delay to the dictionary.
                sound_time_ms = 0  # set sound_time to 0.

            # otherwise, the eye aspect ratio is not below the blink threshold
            else:
                # if the eyes were closed for a sufficient number of frames
                # then increment the total number of blinks
                checkpoint = TOTAL
                if COUNTER >= EYE_AR_CONSEC_FRAMES:
                    TOTAL += 1
                    duration_end = time.time()  # end of the blink timestamp
                next_checkpoint = TOTAL
                # find relative duration for each blink that we counted.
                blink_duration = float(int(round(duration_start * COUNTER - duration_end) / 100000000) / 100)
                COUNTER = 0  # reset the eye frame counter
                # to prevent skews in the plot, duration threshold set to 3 seconds.
                if duration_start != 0.0 and checkpoint != next_checkpoint and blink_duration < 3:
                    print(TOTAL, "th blink duration is: ", blink_duration, " seconds")  # information line
                    patient_dict[str(idx)] = {"timestamp": time.time(), "duration": blink_duration}  # append to dictionary
                duration_start = 0  # reset duration start timestamp

            # debugging on display window.
            cv2.putText(frame, "Blinks: {}".format(TOTAL), (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            idx += 1  # increment index for dictionary.

        patient_dict["total_blinks"] = TOTAL  # add total blinks that we counted during the process.

        #cv2.imshow("Frame", frame)  # display the processed camera feed output.
        if cv2.waitKey(1) & 0xFF == ord('q'):  # press "q" to stop gathering data.
            break

    # do a bit of cleanup
    cap.release()
    cv2.destroyAllWindows()

    # POST PROCESSING
    # get patient's personal data to insert to database
    patient_name = name  # TODO: fill up the form from gui
    patient_surname = surname  # TODO: fill up the form from gui
    patient_phone = phone

    # add the personal data to patient's data dictionary
    patient_dict["name"] = patient_name
    patient_dict["surname"] = patient_surname
    patient_dict["phone"] = patient_phone

    # write the dictionary to JSON file
    dict_to_json(patient_dict, f"{cwd}/Patients/{patient_name}_{patient_surname}#{time.time()}.json")
    print(patient_dict)  # for debugging purposes, print the dictionary

    delay = visualize_current(patient_dict)  # visualize the current patient's data, also returns delay

    # insert patient first so its SQL command:
    insert_patient_sql = "INSERT INTO patient(patient_name , patient_surname, patient_phone) VALUES (%s, %s, %s)"
    # function call prior to the insert patient personal data to database
    insert_database(insert_patient_sql, (patient_name, patient_surname, patient_phone))
    # to get patient id, SQL Query command:
    get_patient_id_query = f"SELECT patient_id FROM patient WHERE patient_name = '{patient_name}' AND " \
                                   f"patient_surname = '{patient_surname}' AND patient_phone = '{patient_phone}' "
    # get patient id function call
    patient_id = get_patient_id(get_patient_id_query)
    # insert desired data SQL command:
    insert_pupil_sql = "INSERT INTO blink(blink_id, blink_timestamp, blink_duration, blink_delay) VALUES (%s,%s,%s,%s)"
    try:
        """
        Since we also remove mostly personal data of the dictionary in visualize_current function,
        try - catch block added incase of visualize_current function call may be removed.
        """
        _name = patient_dict["name"]
        _surname = patient_dict["surname"]
        _phone = patient_dict["phone"]
        delay = patient_dict["delay"]
        total_blinks = patient_dict["total_blinks"]
        patient_dict.pop("name")
        patient_dict.pop("surname")
        patient_dict.pop("delay")
        patient_dict.pop("total_blinks")
    except Exception as e:
        print(e, " dictionary don't have these items...")
        pass

    # function call to insert desired data to database.
    insert_blink_data(insert_pupil_sql, patient_dict, patient_id, delay)
    print("Successfully added to database.")
