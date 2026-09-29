import cv2
import mediapipe as mp
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

    # Lower values = easier for MediaPipe to detect
    min_hand_detection_confidence=0.2,
    min_hand_presence_confidence=0.2,
    min_tracking_confidence=0.2
)


# ==========================================
# Gesture detection
# ==========================================

def detect_gesture(hand):

    # Finger tips
    index_tip = hand[8]
    middle_tip = hand[12]
    ring_tip = hand[16]
    pinky_tip = hand[20]

    # Finger joints
    index_joint = hand[6]
    middle_joint = hand[10]
    ring_joint = hand[14]
    pinky_joint = hand[18]

    # Check whether fingers are extended
    index_open = index_tip.y < index_joint.y
    middle_open = middle_tip.y < middle_joint.y
    ring_open = ring_tip.y < ring_joint.y
    pinky_open = pinky_tip.y < pinky_joint.y

    # Count open fingers
    open_count = sum([
        index_open,
        middle_open,
        ring_open,
        pinky_open
    ])

    # Four fingers open
    if open_count >= 3:
        return "OPEN PALM"

    # Only index finger open
    elif (
        index_open
        and not middle_open
        and not ring_open
        and not pinky_open
    ):
        return "POINTING"

    # Index + middle open
    elif (
        index_open
        and middle_open
        and not ring_open
        and not pinky_open
    ):
        return "TWO FINGERS"

    # One or zero fingers
    elif open_count <= 1:
        return "FIST"

    else:
        return "UNKNOWN"


# ==========================================
# Start MediaPipe
# ==========================================

with HandLandmarker.create_from_options(options) as landmarker:

    camera = cv2.VideoCapture(0)

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    start_time = time.time()

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

        # Create MediaPipe image
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        # Timestamp must continuously increase
        timestamp_ms = int(
            (time.time() - start_time) * 1000
        )

        # Detect and track hand
        result = landmarker.detect_for_video(
            mp_image,
            timestamp_ms
        )

        gesture = "NO HAND"

        # ==========================================
        # Hand detected
        # ==========================================

        if result.hand_landmarks:

            hand = result.hand_landmarks[0]

            gesture = detect_gesture(hand)

            # Draw all 21 landmarks
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
                    6,
                    (0, 255, 0),
                    -1
                )

        # ==========================================
        # Display gesture
        # ==========================================

        cv2.putText(
            frame,
            gesture,
            (20, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 255, 0),
            3
        )

        cv2.imshow(
            "AI Presentation Controller",
            frame
        )

        # Press Q to exit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.release()

cv2.destroyAllWindows()