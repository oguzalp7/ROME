------------------------------------------ WINDOWS ----------------------------------------------------
Installation Steps:
1- Unzip the files
2- Go to: https://visualstudio.microsoft.com/downloads/
3- Download Community Edition (Screenshot #1)
4- During the installation screen, go head and tick "Desktop development with C++" and continue the installation. (Screenshot #2)
5- Download CMake:  https://github.com/Kitware/CMake/releases/download/v3.16.2/cmake-3.16.2-win64-x64.msi 
6- During the installation of CMake make sure to add CMake to PATH.
7- Reboot the computer.
8- Open the unzipped folder and delete everything in the directory section of the folder and type "cmd" (without the quotes). (Screenshot #3)
9- There should be a command prompt pops out, and it should be in the same directory with the project files. To verify, type "dir"(without quotes) and hit enter.
9.1- You should be seeing the list of names of the folders and files.
10- In the command prompt type "pip install -r requirements.txt". (without quotes)

Usage of Blink Project:
1- To run blink project, run(double click) "ROME-Blink" which is a shortcut that runs our scripts. (Shortcut can be moved to Desktop to make easier to run.)
2- If the user believe that enough data is collected; by pressing "q" in the keyboard, data collection can be stopped.
3- Back in the command prompt, type name and surname to save the data as json file.
4- Graphs will be plotted automatically after typing in name and surname.
5- To see next graph, just close the graph window. (Desired graph can be saved as "png" format with pressing save button on the graph pop-up)

 
Usage of Pupil Project:
1- To run pupil dilation project, run(double click) "Rome-Pupil" which is a shortcut that runs our scripts. (Shortcut can be moved to Desktop to make easier to run.)
2- Play with the trackbars to get optimized pupil detection. This part will be utilized as the systems are installed. When enough data collected, press 'q' to stop collecting data.
3- Back in the command prompt, type name and surname to save the data as json file.
4- Graphs will be plotted automatically after typing in name and surname.
5- To see next graph, just close the graph window. (Desired graph can be saved as "png" format with pressing save button on the graph pop-up)

@TODO: Include installation and usage documentation for Ubuntu or any other Linux based Operating System.