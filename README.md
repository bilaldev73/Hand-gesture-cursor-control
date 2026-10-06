# Hand Gesture Mouse Control

A Python project that turns a webcam and hand gestures into computer
mouse controls using **MediaPipe Hand Landmarker**, **OpenCV**, and
**PyAutoGUI**.

## Features

-   🖐️ **Index finger mouse movement** --- Move the index finger to
    control the mouse cursor.
-   🤏 **Pinch to click** --- Bring the thumb and index finger together
    to perform a mouse click.
-   🖱️ **Double click** --- Perform two quick pinches to trigger a
    double click.
-   ✋ **Four-finger scrolling** --- Raise four fingers and move the
    index finger vertically for smooth scrolling.
-   👏 **Two-hand clap screenshot** --- Bring both palms together twice
    quickly to capture a screenshot.
-   🎥 **Live webcam preview** --- Shows detected hand landmarks and the
    current gesture/status.
-   🎯 **Cursor smoothing** --- Smooths index-finger movement to reduce
    cursor jitter.
-   🔄 **Automatic model download** --- Downloads the MediaPipe hand
    model if it is not already present.
-   🛑 **Safe quit** --- Press `Q` to stop the application.

##  Demo
Here is a demonstration of the hand gesture mouse controller. The video is intentionally **muted** so it can be shared on GitHub without audio.

https://github.com/user-attachments/assets/1d9ba11c-f1ad-4118-9cbf-5351011d60ea


## Project Structure

``` text
hand-gesture-mouse/
│
├── main.py
├── util.py
├── hand_landmarker.task
└── README.md
```

### Files

  -----------------------------------------------------------------------
  File                                Purpose
  ----------------------------------- -----------------------------------
  `main.py`                           Main application. Handles webcam
                                      input, hand detection, gesture
                                      recognition, mouse control,
                                      scrolling, and screenshots.

  `util.py`                           Contains NumPy-based helper
                                      functions for angle and
                                      landmark-distance calculations.

  `hand_landmarker.task`              MediaPipe Hand Landmarker model
                                      used for detecting hand landmarks.

  `README.md`                         Project documentation.
  -----------------------------------------------------------------------

## Technologies Used

-   **Python 3**
-   **OpenCV (`cv2`)** --- Webcam capture, image processing, drawing,
    and display.
-   **MediaPipe** --- Hand landmark detection.
-   **PyAutoGUI** --- Mouse movement, clicks, scrolling, and
    screenshots.
-   **NumPy** --- Numerical helper functions in `util.py`.
-   **urllib** --- Downloads the MediaPipe model when required.

## Requirements

Install the required Python packages:

``` bash
pip install opencv-python mediapipe pyautogui numpy
```

> On some systems, PyAutoGUI may require additional operating-system
> permissions or packages.

## Installation

### 1. Clone or copy the project

Place these files in the same directory:

``` text
main.py
util.py
hand_landmarker.task
```

### 2. Install dependencies

``` bash
pip install opencv-python mediapipe pyautogui numpy
```

### 3. Run the application

``` bash
python main.py
```

The program uses the webcam and opens a window named:

``` text
MediaPipe Hand Mouse Control
```

## How the Gestures Work

### 1. Move the Mouse

Raise only the index finger.

``` text
☝️
```

The index-finger position is mapped to the screen dimensions. Cursor
movement is smoothed to make it more stable.

### 2. Single Click

Bring the thumb and index finger together:

``` text
🤏
```

The program checks the normalized distance between the thumb tip and
index-finger tip. When the distance becomes small enough, a mouse click
is generated.

### 3. Double Click

Perform two quick pinch gestures.

The program keeps a short click history and treats two pinches occurring
within the configured time window as a double click.

### 4. Scroll

Raise four fingers:

``` text
🖐️
```

Then move the index finger vertically.

The program calculates the change in the index-finger position and
converts it into small, smoothed mouse-wheel movements.

### 5. Take a Screenshot

Use two hands and bring the palms together twice quickly:

``` text
👏  👏
```

When two quick claps are detected, PyAutoGUI saves a screenshot using a
filename similar to:

``` text
screenshot_XXXXXXXXXX.png
```

The screenshot is saved in the current working directory.

## Gesture Summary

  Gesture                     Action
  --------------------------- --------------
  ☝️ Index finger only        Move mouse
  🤏 Thumb + index pinch      Single click
  🤏 + 🤏 Two quick pinches   Double click
  🖐️ Four fingers             Scroll
  👏 Two quick hand claps     Screenshot
  `Q`                         Quit

## Configuration

Several values in `main.py` can be adjusted to change responsiveness.

### Cursor smoothing

``` python
smoothening = 4
```

A larger value generally produces smoother but slower cursor movement.

### Scroll settings

``` python
scroll_speed = 2.0
scroll_smoothing = 9.0
scroll_deadzone = 0.0025
scroll_max_step = 4
scroll_delay = 0.015
```

These control scrolling speed, smoothing, dead-zone filtering, maximum
wheel movement, and scroll frequency.

### Pinch click threshold

``` python
if distance < 0.045:
```

Lower or increase this threshold depending on how easily you want a
pinch to register as a click.

### Screenshot/clap settings

``` python
clap_distance_threshold = 0.14
clap_release_threshold = 0.20
clap_interval = 0.9
screenshot_cooldown = 2
```

These values control how close the hands must be, how far they must
separate before another clap can be detected, the allowed time between
claps, and the screenshot cooldown.

## Camera Settings

The application currently uses the default camera:

``` python
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
```

The requested camera resolution is:

``` text
640 × 480
```

and the target frame rate is:

``` text
30 FPS
```

If the default camera cannot be opened, the program suggests trying
camera index `1` instead of `0`.

## MediaPipe Configuration

The application uses MediaPipe's Hand Landmarker in video mode and
supports up to two hands.

Important settings include:

``` python
num_hands=2
min_hand_detection_confidence=0.75
min_hand_presence_confidence=0.75
min_tracking_confidence=0.75
```

The model file is expected at:

``` text
hand_landmarker.task
```

If it is missing, `main.py` attempts to download the model
automatically.

## Safety Feature

PyAutoGUI's failsafe is enabled:

``` python
pyautogui.FAILSAFE = True
```

This allows PyAutoGUI's normal failsafe behavior to remain active.

When experimenting with mouse automation, keep an easy way to stop the
program available.

## Troubleshooting

### Camera does not open

Try changing:

``` python
cv2.VideoCapture(0, cv2.CAP_DSHOW)
```

to:

``` python
cv2.VideoCapture(1, cv2.CAP_DSHOW)
```

Also check that another application is not using the webcam.

### MediaPipe model error

Make sure `hand_landmarker.task` is in the same working directory as
`main.py`.

If the file is missing, the program contains logic to download it
automatically.

### Cursor is too shaky

Increase:

``` python
smoothening = 4
```

For example:

``` python
smoothening = 6
```

### Clicking happens too easily

Reduce the pinch threshold:

``` python
if distance < 0.045:
```

For example:

``` python
if distance < 0.035:
```

### Scrolling is too fast

Reduce:

``` python
scroll_speed = 2.0
```

or reduce:

``` python
scroll_max_step = 4
```

### PyAutoGUI permissions

On some operating systems, applications that control the mouse or
capture the screen may need accessibility, input-monitoring, or
screen-recording permissions.

## Important Notes

-   Good lighting improves hand detection.
-   Keep the hand clearly visible to the webcam.
-   Avoid excessive background clutter.
-   Cursor control works best when the hand is within a comfortable
    distance from the camera.
-   Gesture thresholds may need adjustment for different cameras,
    lighting conditions, and hand positions.
-   The current application processes the webcam at a reduced
    `320 × 240` resolution for MediaPipe detection while displaying the
    original `640 × 480` frame.

## Current Implementation Notes

`main.py` contains the active application logic. The imported modules
include OpenCV, MediaPipe, PyAutoGUI, and standard Python modules.

`util.py` currently contains NumPy helper functions for angle and
distance calculations, but the main application does not currently
import or call these helper functions. They can be integrated later if
additional gesture calculations are added.

## Future Improvements

Possible improvements include:

-   Add left-click and right-click gestures separately.
-   Add drag-and-drop gestures.
-   Add configurable gesture sensitivity through a settings file.
-   Add a calibration screen for different camera positions.
-   Add FPS display and performance monitoring.
-   Improve finger detection for different hand orientations.
-   Add gesture-based volume control.
-   Add gesture-based media controls.
-   Add a graphical settings interface.
-   Refactor utility functions into reusable gesture-detection modules.

## License

This project is provided as a personal/educational project. Add an
appropriate open-source license such as MIT if you plan to publish and
distribute the project.

## Credits

Built with:

-   MediaPipe
-   OpenCV
-   PyAutoGUI
-   NumPy
