# Python-course-assignment

This script was written to perform an experimental test on a robot (Ambrogio 🤖❤️) we built for the Cajal Advanced Neuroscience Training Porgramme. A face recognition function that plays through a web-streaming camera gives the input to Ambrogio to turn his back and run away whenever he meets human faces! The first part of the task (camera stream and face recognition) is written in python. Then, a serial port comunication is established, where an Arduino runs a .ino file to complete the second part of the task (moving the wheels to run away:) The second part of the task, written in Arduino, is not shown here, but can be found at the following link: https://github.com/NoBlackBoxes/LastBlackBox/blob/master/course/bootcamp/day_2/resources/arduino/servo_test/servo_test.ino. The audio connection through the ears of the robot is also initialized in this script, but it doesn't generate any output for the current task.

The script was modified and implemented from several scripts in the following github repositories and open web resources:
https://github.com/NoBlackBoxes/LastBlackBox/tree/master/course , https://github.com/NoBlackBoxes/LastBlackBox/tree/master/course/bootcamp/day_5/resources , https://picamera.readthedocs.io/en/release-1.13/recipes2.html

The script is intended to work on the RaspberryPi mounted on our robot, that is serially connected to an Arduino. In my repository, the "Face_recognition_run_and_spin.py" is the script that I remotely run on the RasperryPi of Ambrogio and that smoothly works. For the sake of the assignement, I also created a jupyter notebook "Face_recognition_run_and_spin_notebook.ipynb" where I documented with extensive comments all the steps of the script (comments you can't find in the .py file). However, the jupyter notebook cannot run without errors given that is not talking with its hardware. I would suggest to use my jupyter notebook for correction and feedbacks, and then I will be happy to organize a demonstration running the .py on Ambrogio RasperryPi, to display the output. In the meantime, I uploaded also a .mp4 file as a demonstration :)

Brief script description (better documented in the jypyter notebook):
1) In the first part of the script all the needed libraries for live streaming image and audio processing are downloaded. Then, a serial port communication between the RaspberryPi and the Arduino is established.
2) The audio connection to my robot's audio hardware is initialized through PyAudio
3) The camera streaming is activated through a connection between the videocamera of my robot and a web broswer page that will live-straem what the robot camera sees in real-time.
4) Multiple image processing steps follow, in order to put the image in the right shape to be detected by a face recognition algorithm
5) A pre-trained face-recognition algorithm outputs the detected face. The output is then sent through the serial communication to the Arduino as input to make the arduino script run and the robot's wheels move.


