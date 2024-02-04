import cv2

from gaze_tracking import GazeTracking

STACK_SIZE = 25
CALIBRATE_TEXT = "Look at the dot for 4 seconds and press space"


gaze = GazeTracking()
webcam = cv2.VideoCapture(0)
width, height = int(webcam.get(3)), int(webcam.get(4))


MIN_WIDTH = int(width / 100)
MID_WIDTH = int(width / 2)
MAX_WIDTH = int(width * 98 / 100)
MIN_HEIGHT = int(2 * height / 100)
MID_HEIGHT = int(height / 2)
MAX_HEIGHT = int(height * 98 / 100)

max_coords = [0, 0, 0, 0]

horizon_ratios_stack, vertical_ratios_stack = [], []


status = "top"

while True:
    _, frame = webcam.read()

    gaze.refresh(frame)

    frame = gaze.annotated_frame()

    horizon, vertical = gaze.horizontal_ratio(), gaze.vertical_ratio()
    try:
        horizon = float("{:.5f}".format(horizon))
        vertical = float("{:.5f}".format(vertical))

        horizon_ratios_stack.append(horizon)
        vertical_ratios_stack.append(vertical)
        if len(horizon_ratios_stack) == STACK_SIZE + 1:
            horizon_ratios_stack.pop(0)
            vertical_ratios_stack.pop(0)
        no_eyes = False
    except TypeError:
        no_eyes = True

    if status != "complete":
        # Calibration
        cv2.putText(
            frame,
            CALIBRATE_TEXT,
            (int(width / 4), int(height / 2)),
            cv2.FONT_HERSHEY_DUPLEX,
            0.6,
            (217, 217, 217),
            1,
        )

        dot_poition = ()
        if status == "top":
            dot_poition = (MID_WIDTH, MIN_HEIGHT)
        elif status == "right":
            dot_poition = (MAX_WIDTH, MID_HEIGHT)
        elif status == "bottom":
            dot_poition = (MID_WIDTH, MAX_HEIGHT)
        elif status == "left":
            dot_poition = (MIN_WIDTH, MID_HEIGHT)

        cv2.putText(
            frame,
            ".",
            dot_poition,
            cv2.FONT_HERSHEY_DUPLEX,
            2,
            (199, 0, 0),
            2,
        )
    elif not (no_eyes):
        # move the cursor
        cursor_y = (
            (max_coords[0] - (sum(vertical_ratios_stack) / len(vertical_ratios_stack)))
            / (max_coords[0] - max_coords[2])
        ) * height
        cursor_y = int(
            max(
                min(cursor_y, MAX_HEIGHT),
                2*MIN_HEIGHT,
            )
        )
        cursor_x = (
            (max_coords[3] - (sum(horizon_ratios_stack) / len(horizon_ratios_stack)))
            / (max_coords[3] - max_coords[1])
        ) * width
        cursor_x = int(
            max(
                min(cursor_x, MAX_WIDTH),
                MIN_WIDTH,
            )
        )

        cv2.putText(
            frame,
            "*",
            (cursor_x, cursor_y),
            cv2.FONT_HERSHEY_DUPLEX,
            1.1,
            (199, 0, 0),
            2,
        )

    # Show the ratios
    horizon_text = f"Horizon: {horizon}"
    vertical_text = f"Vertical: {vertical}"

    cv2.putText(
        frame,
        horizon_text,
        (int(width / 10), int(height / 10)),
        cv2.FONT_HERSHEY_DUPLEX,
        1.1,
        (147, 58, 31),
        2,
    )
    cv2.putText(
        frame,
        vertical_text,
        (int(width / 10), int(height * 2 / 10)),
        cv2.FONT_HERSHEY_DUPLEX,
        1.1,
        (147, 58, 31),
        2,
    )

    """
    Show positions of pupils
    left_pupil = gaze.pupil_left_coords()
    right_pupil = gaze.pupil_right_coords()
    cv2.putText(
        frame,
        "Left pupil:  " + str(left_pupil),
        (int(width / 10), int(height * 8 / 10)),
        cv2.FONT_HERSHEY_DUPLEX,
        0.6,
        (33, 33, 33),
        1,
    )
    cv2.putText(
        frame,
        "Right pupil: " + str(right_pupil),
        (int(width / 10), int(height * 9 / 10)),
        cv2.FONT_HERSHEY_DUPLEX,
        0.6,
        (33, 33, 33),
        1,
    )"""

    # Show Frame
    cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow("window", frame)

    # Handle input from keyboard
    k = cv2.waitKey(1)

    if k == 27:
        break
    elif k == 32 and status != "complete":
        # Submit the coords
        if len(vertical_ratios_stack) == STACK_SIZE:
            if status == "top":
                max_coords[0] = sum(vertical_ratios_stack) / len(vertical_ratios_stack)
                status = "right"
            elif status == "right":
                max_coords[1] = sum(horizon_ratios_stack) / len(horizon_ratios_stack)
                status = "bottom"
            elif status == "bottom":
                max_coords[2] = sum(vertical_ratios_stack) / len(vertical_ratios_stack)
                status = "left"
            elif status == "left":
                max_coords[3] = sum(horizon_ratios_stack) / len(horizon_ratios_stack)
                status = "complete"
            vertical_ratios_stack = []
            horizon_ratios_stack = []
            CALIBRATE_TEXT = "Look at the dot for 4 seconds and press space"
        else:
            CALIBRATE_TEXT = "Wait more"

webcam.release()
cv2.destroyAllWindows()
