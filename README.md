# AI Presentation Controller

An AI-powered gesture-based presentation controller that allows users to control PowerPoint slides using hand gestures through a webcam.

Instead of using a keyboard or mouse during a presentation, the presenter can use simple hand gestures to start the presentation, navigate between slides, and exit the presentation.

## Features

- Real-time hand detection using a webcam
- Hand landmark tracking using MediaPipe
- Gesture recognition using Python
- PowerPoint control using PyAutoGUI
- Gesture stability detection to reduce accidental actions
- Cooldown mechanism to prevent repeated slide changes

## Gesture Controls

| Gesture | Action |
|---|---|
| 🖐️ Open Palm | Start Presentation |
| ✌️ Two Fingers | Next Slide |
| ☝️ One Finger | Previous Slide |
| ✊ Closed Fist | Exit Presentation |

## How It Works

The system follows this pipeline:

Webcam  
↓  
OpenCV  
↓  
MediaPipe Hand Landmarker  
↓  
21 Hand Landmarks  
↓  
Gesture Recognition  
↓  
PyAutoGUI  
↓  
PowerPoint

The webcam captures the presenter's hand movements.

MediaPipe detects the hand and identifies its landmarks.

The Python program analyzes the positions of the fingers and determines the gesture.

The recognized gesture is converted into a keyboard command that controls PowerPoint.

## Technologies Used

- Python 3.12
- OpenCV
- MediaPipe
- PyAutoGUI
- PyGetWindow
- PowerPoint
- VS Code

## Project Structure

```text
AI-Presentation-Controller/
│
├── main.py
├── gesture_controller.py
├── hand_tracker.py
├── test_camera.py
├── hand_landmarker.task
├── requirements.txt
├── .gitignore
└── README.md