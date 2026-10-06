import os
import time
import math
import urllib.request

import cv2
import mediapipe as mp
import pyautogui


# ============================================================
# 1. DOWNLOAD MEDIAPIPE HAND MODEL
# ============================================================

MODEL_PATH = "hand_landmarker.task"

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/"
    "hand_landmarker.task"
)

if not os.path.exists(MODEL_PATH):
    print("Downloading MediaPipe hand model...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("Model downloaded successfully!")


# ============================================================
# 2. PYAUTOGUI SETTINGS
# ============================================================

pyautogui.PAUSE = 0.01
pyautogui.FAILSAFE = True

screen_w, screen_h = pyautogui.size()

print("====================================")
print("      HAND MOUSE CONTROL")
print("====================================")
print("Index finger       -> Move mouse")
print("Thumb + Index      -> Click")
print("Two quick pinches   -> Double click")
print("4 fingers           -> Scroll")
print("Two hand claps     -> Screenshot")
print("Q                   -> Quit")
print("====================================")


# ============================================================
# 3. MOUSE VARIABLES
# ============================================================

prev_screen_x = screen_w // 2
prev_screen_y = screen_h // 2

# Cursor smoothing
smoothening = 4

# Pinch lock
freeze_cursor = False

# Click history
click_times = []

# Click message
message_text = ""
message_time = 0


# ============================================================
# 4. SCROLL VARIABLES
# ============================================================

scroll_mode = False

# Smooth, low-latency scrolling settings.
scroll_speed = 2.0
scroll_smoothing = 9.0
scroll_deadzone = 0.0025
scroll_max_step = 4
prev_scroll_y = None
scroll_velocity = 0.0
last_scroll_time = 0.0
scroll_delay = 0.015


# ============================================================
# 5. SCREENSHOT VARIABLES
# ============================================================

# Screenshot is triggered by TWO quick claps.
# A clap is detected when the centers of both palms come close together.
clap_distance_threshold = 0.14
clap_release_threshold = 0.20
clap_interval = 0.9
clap_count = 0
last_clap_time = 0
clap_armed = True

screenshot_cooldown = 2
last_screenshot_time = 0

screenshot_message_time = 0


# ============================================================
# 6. MEDIAPIPE TASKS SETUP
# ============================================================

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode


options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path=MODEL_PATH
    ),

    running_mode=VisionRunningMode.VIDEO,

    num_hands=2,

    min_hand_detection_confidence=0.75,
    min_hand_presence_confidence=0.75,
    min_tracking_confidence=0.75
)


# ============================================================
# 7. HAND CONNECTIONS
# ============================================================

HAND_CONNECTIONS = [

    # Thumb
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),

    # Index
    (0, 5),
    (5, 6),
    (6, 7),
    (7, 8),

    # Middle
    (5, 9),
    (9, 10),
    (10, 11),
    (11, 12),

    # Ring
    (9, 13),
    (13, 14),
    (14, 15),
    (15, 16),

    # Pinky
    (13, 17),
    (17, 18),
    (18, 19),
    (19, 20),

    # Palm
    (0, 17)
]


# ============================================================
# 8. DRAW HAND
# ============================================================

def draw_hand(frame, landmarks):

    height, width, _ = frame.shape

    points = []

    for landmark in landmarks:

        x = int(landmark.x * width)
        y = int(landmark.y * height)

        points.append((x, y))

        cv2.circle(
            frame,
            (x, y),
            5,
            (0, 255, 0),
            -1
        )

    for start, end in HAND_CONNECTIONS:

        cv2.line(
            frame,
            points[start],
            points[end],
            (255, 0, 0),
            2
        )


# ============================================================
# 9. FINGER DETECTION
# ============================================================

def get_fingers(hand_landmarks):

    # Index, middle, ring, pinky
    fingers = [

        1 if hand_landmarks[tip].y <
        hand_landmarks[tip - 2].y - 0.015

        else 0

        for tip in [8, 12, 16, 20]
    ]

    return fingers


# ============================================================
# 10. OPEN CAMERA
# ============================================================

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not cap.isOpened():

    print("ERROR: Cannot open camera.")
    print("Try changing VideoCapture(0) to VideoCapture(1).")

    exit()


# ============================================================
# 11. START MEDIAPIPE
# ============================================================

with HandLandmarker.create_from_options(options) as landmarker:

    timestamp_ms = 0
    start_time = time.perf_counter()

    while True:

        # ====================================================
        # READ CAMERA
        # ====================================================

        success, frame = cap.read()

        if not success:

            print("ERROR: Cannot read camera.")
            break


        # ====================================================
        # MIRROR CAMERA
        # ====================================================

        frame = cv2.flip(frame, 1)


        # ====================================================
        # BGR -> RGB
        # ====================================================

        process_frame = cv2.resize(
            frame, (320, 240), interpolation=cv2.INTER_AREA
        )

        rgb_frame = cv2.cvtColor(
            process_frame,
            cv2.COLOR_BGR2RGB
        )


        # ====================================================
        # MEDIAPIPE IMAGE
        # ====================================================

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )


        # ====================================================
        # TIMESTAMP
        # ====================================================

        timestamp_ms = int((time.perf_counter() - start_time) * 1000)


        # ====================================================
        # DETECT HAND
        # ====================================================

        result = landmarker.detect_for_video(
            mp_image,
            timestamp_ms
        )


        # ====================================================
        # HAND DETECTED
        # ====================================================

        if result.hand_landmarks:

            for hand_landmarks in result.hand_landmarks:

                # ------------------------------------------------
                # DRAW HAND
                # ------------------------------------------------

                draw_hand(
                    frame,
                    hand_landmarks
                )


                # ------------------------------------------------
                # LANDMARKS
                # ------------------------------------------------

                thumb_tip = hand_landmarks[4]
                index_tip = hand_landmarks[8]
                middle_tip = hand_landmarks[12]
                ring_tip = hand_landmarks[16]
                pinky_tip = hand_landmarks[20]


                # ------------------------------------------------
                # FINGERS
                # ------------------------------------------------

                fingers = get_fingers(
                    hand_landmarks
                )

                finger_count = sum(fingers)


                # =================================================
                # THUMB + INDEX DISTANCE
                # =================================================

                distance = math.hypot(

                    thumb_tip.x - index_tip.x,

                    thumb_tip.y - index_tip.y
                )


                # =================================================
                # SCROLL MODE
                #
                # 4 fingers up
                # =================================================

                if sum(fingers) == 4:

                    scroll_mode = True

                else:

                    scroll_mode = False


                # =================================================
                # SCREENSHOT MODE
                #
                # TWO QUICK HAND CLAPS = SCREENSHOT
                # =================================================

                current_time = time.time()

                if len(result.hand_landmarks) >= 2:
                    hand1 = result.hand_landmarks[0]
                    hand2 = result.hand_landmarks[1]

                    # Palm centers using wrist + MCP landmarks.
                    palm1_x = sum(hand1[i].x for i in [0, 5, 9, 13, 17]) / 5
                    palm1_y = sum(hand1[i].y for i in [0, 5, 9, 13, 17]) / 5

                    palm2_x = sum(hand2[i].x for i in [0, 5, 9, 13, 17]) / 5
                    palm2_y = sum(hand2[i].y for i in [0, 5, 9, 13, 17]) / 5

                    clap_distance = math.hypot(
                        palm1_x - palm2_x,
                        palm1_y - palm2_y
                    )

                    # Hands must separate before another clap can be counted.
                    if clap_distance > clap_release_threshold:
                        clap_armed = True

                    # Count a clap when the two hands come together.
                    if clap_distance < clap_distance_threshold and clap_armed:
                        clap_armed = False

                        # Reset if the previous clap was too long ago.
                        if current_time - last_clap_time > clap_interval:
                            clap_count = 0

                        clap_count += 1
                        last_clap_time = current_time

                        print(f"Clap detected: {clap_count}/2")

                        # Two quick claps -> screenshot.
                        if clap_count >= 2:
                            if current_time - last_screenshot_time > screenshot_cooldown:
                                filename = f"screenshot_{int(current_time)}.png"

                                pyautogui.screenshot(filename)

                                print(f"Screenshot saved: {filename}")

                                last_screenshot_time = current_time
                                screenshot_message_time = current_time

                            clap_count = 0

                    # Show clap status.
                    cv2.putText(
                        frame,
                        f"Claps: {clap_count}/2",
                        (10, 130),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (255, 255, 0),
                        2
                    )

                    if time.time() - screenshot_message_time < 1:
                        cv2.putText(
                            frame,
                            "Screenshot Taken!",
                            (10, 170),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (255, 255, 0),
                            2
                        )

                # =================================================
                # SCROLL ACTIONS
                # =================================================

                if scroll_mode:
                    current_time = time.perf_counter()

                    if prev_scroll_y is None:
                        prev_scroll_y = index_tip.y
                        scroll_velocity = 0.0

                    # Smooth the tracked finger position first.
                    raw_delta = prev_scroll_y - index_tip.y
                    if abs(raw_delta) < scroll_deadzone:
                        raw_delta = 0.0

                    smoothed_delta = raw_delta / scroll_smoothing
                    scroll_velocity = (
                        scroll_velocity * 0.70
                        + smoothed_delta * 0.30
                    )

                    if (
                        abs(scroll_velocity) > 0.00045
                        and current_time - last_scroll_time >= scroll_delay
                    ):
                        # Convert normalized hand movement to small wheel steps.
                        amount = int(scroll_velocity * 180 * scroll_speed)

                        if amount == 0:
                            amount = 1 if scroll_velocity > 0 else -1

                        amount = max(
                            -scroll_max_step,
                            min(scroll_max_step, amount)
                        )

                        pyautogui.scroll(amount)
                        last_scroll_time = current_time

                    # Update previous position without jumping.
                    prev_scroll_y += (
                        index_tip.y - prev_scroll_y
                    ) / scroll_smoothing

                    if scroll_velocity > 0.00045:
                        cv2.putText(
                            frame,
                            "Smooth Scroll Up",
                            (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (0, 255, 0),
                            2
                        )
                    elif scroll_velocity < -0.00045:
                        cv2.putText(
                            frame,
                            "Smooth Scroll Down",
                            (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (0, 0, 255),
                            2
                        )

                else:
                    # Reset scrolling immediately when 4-finger mode ends.
                    prev_scroll_y = None
                    scroll_velocity = 0.0


                # =================================================
                # CLICK DETECTION
                # =================================================

                if not scroll_mode:

                    if distance < 0.045:

                        if not freeze_cursor:

                            freeze_cursor = True

                            current_time = time.time()

                            click_times.append(
                                current_time
                            )


                            # -------------------------------------
                            # Keep recent clicks only
                            # -------------------------------------

                            click_times = [

                                t for t in click_times

                                if current_time - t < 0.4
                            ]


                            # -------------------------------------
                            # DOUBLE CLICK
                            # -------------------------------------

                            if (
                                len(click_times) >= 2
                                and
                                click_times[-1]
                                -
                                click_times[-2]
                                < 0.4
                            ):

                                pyautogui.doubleClick()

                                message_text = (
                                    "Double Click"
                                )

                                message_time = (
                                    time.time()
                                )

                                click_times = []


                            # -------------------------------------
                            # SINGLE CLICK
                            # -------------------------------------

                            else:

                                pyautogui.click()

                                message_text = (
                                    "Single Click"
                                )

                                message_time = (
                                    time.time()
                                )


                    # ---------------------------------------------
                    # RELEASE PINCH
                    # ---------------------------------------------

                    else:

                        if freeze_cursor:

                            time.sleep(0)

                        freeze_cursor = False


                # =================================================
                # SMOOTH MOUSE MOVEMENT
                # =================================================

                if (
                    fingers[0] == 1
                    and fingers[1] == 0
                    and fingers[2] == 0
                    and fingers[3] == 0
                    and not scroll_mode
                    and distance >= 0.045
                ):

                    if not freeze_cursor:

                        # -----------------------------------------
                        # Target position
                        # -----------------------------------------

                        screen_x = int(
                            index_tip.x * screen_w
                        )

                        screen_y = int(
                            index_tip.y * screen_h
                        )


                        # -----------------------------------------
                        # Smooth cursor
                        # -----------------------------------------

                        current_x = (
                            prev_screen_x
                            +
                            (
                                screen_x
                                - prev_screen_x
                            )
                            / smoothening
                        )

                        current_y = (
                            prev_screen_y
                            +
                            (
                                screen_y
                                - prev_screen_y
                            )
                            / smoothening
                        )


                        # -----------------------------------------
                        # Move cursor
                        # -----------------------------------------

                        pyautogui.moveTo(
                            int(current_x),
                            int(current_y),
                            duration=0.01
                        )


                        # -----------------------------------------
                        # Save position
                        # -----------------------------------------

                        prev_screen_x = current_x
                        prev_screen_y = current_y


                    cv2.putText(
                        frame,
                        "MOUSE CONTROL",
                        (10, 170),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2
                    )


                # =================================================
                # FINGER COUNT
                # =================================================

                cv2.putText(
                    frame,
                    f"Fingers: {finger_count}",
                    (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2
                )


                # =================================================
                # PINCH DISTANCE
                # =================================================

                cv2.putText(
                    frame,
                    f"Distance: {distance:.3f}",
                    (10, 210),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )


                # =================================================
                # CLICK MESSAGE
                # =================================================

                if (
                    message_text
                    and
                    time.time() - message_time < 0.7
                ):

                    cv2.putText(
                        frame,
                        message_text,
                        (10, 250),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 255),
                        2
                    )


        # ====================================================
        # NO HAND
        # ====================================================

        else:

            freeze_cursor = False
            scroll_mode = False
            clap_armed = True

            prev_scroll_y = None
            scroll_velocity = 0.0

            cv2.putText(
                frame,
                "No hand detected",
                (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )


        # ====================================================
        # SHOW CAMERA
        # ====================================================

        cv2.imshow(
            "MediaPipe Hand Mouse Control",
            frame
        )


        # ====================================================
        # QUIT
        # ====================================================

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break


# ============================================================
# 12. CLEAN UP
# ==============================================q============

cap.release()
cv2.destroyAllWindows()

print("Hand mouse control stopped.")
