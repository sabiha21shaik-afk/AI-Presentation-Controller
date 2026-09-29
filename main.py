import cv2
import mediapipe as mp
import pyautogui
import pygetwindow as gw
import time


# ==========================================
# MediaPipe setup
# ==========================================

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode


options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path="hand_landmarker.task"
    ),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.2,
    min_hand_presence_confidence=0.2,
    min_tracking_confidence=0.2
)


# ==========================================
# Detect gesture
# ==========================================

def detect_gesture(hand):

    index_tip = hand[8]
    middle_tip = hand[12]
    ring_tip = hand[16]
    pinky_tip = hand[20]

    index_joint = hand[6]
    middle_joint = hand[10]
    ring_joint = hand[14]
    pinky_joint = hand[18]

    index_open = index_tip.y < index_joint.y
    middle_open = middle_tip.y < middle_joint.y
    ring_open = ring_tip.y < ring_joint.y
    pinky_open = pinky_tip.y < pinky_joint.y

    open_count = sum([
        index_open,
        middle_open,
        ring_open,
        pinky_open
    ])

    # ======================================
    # OPEN PALM
    # ======================================

    if open_count >= 3:
        return "OPEN PALM"

    # ======================================
    # TWO FINGERS
    # ======================================

    elif (
        index_open
        and middle_open
        and not ring_open
        and not pinky_open
    ):
        return "TWO FINGERS"

    # ======================================
    # ONE FINGER
    # ======================================

    elif (
        index_open
        and not middle_open
        and not ring_open
        and not pinky_open
    ):
        return "POINTING"

    # ======================================
    # FIST
    # ======================================

    elif open_count <= 1:
        return "FIST"

    else:
        return "UNKNOWN"


# ==========================================
# Find PowerPoint window
# ==========================================

def find_powerpoint():

    windows = gw.getAllWindows()

    for window in windows:

        title = window.title

        if title and "PowerPoint" in title:

            return window

    return None


# ==========================================
# Start camera
# ==========================================

with HandLandmarker.create_from_options(options) as landmarker:

    camera = cv2.VideoCapture(0)

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    start_time = time.time()

    # Gesture stability
    last_detected_gesture = ""
    stable_count = 0

    required_stable_frames = 8

    # Prevent repeated actions
    last_action_time = 0
    cooldown = 2.5

    action_locked = False

    while True:

        success, frame = camera.read()

        if not success:
            print("Could not access camera")
            break

        # Mirror camera
        frame = cv2.flip(frame, 1)

        # Convert BGR -> RGB
        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        # MediaPipe image
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        # Timestamp
        timestamp_ms = int(
            (time.time() - start_time) * 1000
        )

        # Detect hand
        result = landmarker.detect_for_video(
            mp_image,
            timestamp_ms
        )

        gesture = "NO HAND"

        # ==================================
        # Hand detected
        # ==================================

        if result.hand_landmarks:

            hand = result.hand_landmarks[0]

            gesture = detect_gesture(hand)

            # Draw landmarks
            for landmark in hand:

                x = int(
                    landmark.x * frame.shape[1]
                )

                y = int(
                    landmark.y * frame.shape[0]
                )

                cv2.circle(
                    frame,
                    (x, y),
                    5,
                    (0, 255, 0),
                    -1
                )

        # ==================================
        # Gesture stability
        # ==================================

        if gesture == last_detected_gesture:

            stable_count += 1

        else:

            last_detected_gesture = gesture
            stable_count = 1

            # Unlock when gesture changes
            action_locked = False

        # ==================================
        # PowerPoint actions
        # ==================================

        current_time = time.time()

        if (
            stable_count >= required_stable_frames
            and not action_locked
            and current_time - last_action_time >= cooldown
        ):

            # --------------------------------
            # OPEN PALM = START PRESENTATION
            # --------------------------------

            if gesture == "OPEN PALM":

                powerpoint = find_powerpoint()

                if powerpoint:

                    try:

                        powerpoint.activate()

                        time.sleep(0.5)

                        pyautogui.press("f5")

                        print("START PRESENTATION")

                    except Exception as e:

                        print("Could not start PowerPoint:", e)

                else:

                    print("PowerPoint window not found")

                last_action_time = current_time
                action_locked = True

            # --------------------------------
            # FIST = EXIT PRESENTATION
            # --------------------------------

            elif gesture == "FIST":

                powerpoint = find_powerpoint()

                if powerpoint:

                    try:

                        powerpoint.activate()

                        time.sleep(0.3)

                        pyautogui.press("esc")

                        print("EXIT PRESENTATION")

                    except Exception as e:

                        print("Could not exit PowerPoint:", e)

                last_action_time = current_time
                action_locked = True

            # --------------------------------
            # TWO FINGERS = NEXT
            # --------------------------------

            elif gesture == "TWO FINGERS":

                powerpoint = find_powerpoint()

                if powerpoint:

                    try:

                        powerpoint.activate()

                        time.sleep(0.2)

                        pyautogui.press("right")

                        print("NEXT SLIDE")

                    except Exception as e:

                        print("Could not go to next slide:", e)

                last_action_time = current_time
                action_locked = True

            # --------------------------------
            # ONE FINGER = PREVIOUS
            # --------------------------------

            elif gesture == "POINTING":

                powerpoint = find_powerpoint()

                if powerpoint:

                    try:

                        powerpoint.activate()

                        time.sleep(0.2)

                        pyautogui.press("left")

                        print("PREVIOUS SLIDE")

                    except Exception as e:

                        print("Could not go to previous slide:", e)

                last_action_time = current_time
                action_locked = True

        # ==================================
        # Display
        # ==================================

        cv2.putText(
            frame,
            gesture,
            (20, 55),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.1,
            (0, 255, 0),
            3
        )

        cv2.putText(
            frame,
            "OPEN PALM = START",
            (20, 95),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 255, 255),
            2
        )

        cv2.putText(
            frame,
            "2 FINGERS = NEXT",
            (20, 125),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 255, 255),
            2
        )

        cv2.putText(
            frame,
            "1 FINGER = PREVIOUS",
            (20, 155),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 255, 255),
            2
        )

        cv2.putText(
            frame,
            "FIST = EXIT",
            (20, 185),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 255, 255),
            2
        )

        cv2.imshow(
            "AI Presentation Controller",
            frame
        )

        # Q = quit controller
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.release()

cv2.destroyAllWindows()