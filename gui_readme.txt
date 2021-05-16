To get the necessary libraries you need to complete these steps:
	1. if pip is installed on your computer run the command:
		pip install -r requirements.txt
	2. if pip isn't installed, install pip3 by running the command:
		sudo apt install python3-pip
	3. After pip is installed run pip3 --version on the commandline if you get a version ouptut version go back to step 1 if not try to install again.

After the libraries are installed you can start using the GUI.

Usage instructions:
	1. run the program with the command:
		python3 ui.py
	2. Hit start on the popup window and enter name,surname,phone_number hitting the okay button after every popup
	3. After the program starts simply hit the start button in the bottom left and then the GUI will start recording and randomly play a startling sound
	4. After you are done with the recording hit the stop button next to the start button. That will stop the recording and the result video will be saved as "output.avi" in the same directory.
	5. To calculate the blinks you have to hit the blink button at the bottom right. That will send the previously generated video to the blink program for the blinks to be calculated.
	6. The blink program will display the graphs and upload results to the database.

Limitations:
	1. Because the pupil code can't run without a live camera I was unable to integrate it into the GUI
	2. The database GUI is currently buggy and not working properly. But I added comments so when the database is complete the GUI can easily be updated.
	
Closing Notes:
The GUI is very neatly commented and written in a OOP manner so it's easy to change and increment over time. I also only included components and requirments of the GUI since the rest has already been provided.
	

