import numpy as np
import cv2
from collections import deque


def callSignature():
    # Define the upper and lower boundaries for a color to be considered "Blue"
    Lower = np.array([100, 60, 60])
    Upper = np.array([140, 255, 255])

    # Define a 5x5 kernel for erosion and dilation
    kernel = np.ones((5, 5), np.uint8)

    bpoints = [deque(maxlen=512)]
    bindex = 0
    color = [(0, 0, 0)]
    colorIndex = 0

    paintWindow = np.zeros((471, 636, 3)) + 255
    paintWindow = cv2.rectangle(paintWindow, (40, 1), (140, 65), (0, 0, 0), 2)
    cv2.putText(paintWindow, "CLEAR ALL", (49, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)

    cv2.namedWindow('Paint', cv2.WINDOW_AUTOSIZE)

    # Load the video
    camera = cv2.VideoCapture(0)

    # Keep looping
    while True:
        # Grab the current paintWindow
        (grabbed, frame) = camera.read()
        frame = cv2.flip(frame, 1)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Add the coloring options to the frame
        frame = cv2.rectangle(frame, (40, 1), (140, 65), (122, 122, 122), -1)
        cv2.putText(frame, "CLEAR ALL", (49, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

        # Check to see if we have reached the end of the video
        if not grabbed:
            break

        # Determine which pixels fall within the blue boundaries and then blur the binary image
        blueMask = cv2.inRange(hsv, Lower, Upper)
        blueMask = cv2.erode(blueMask, kernel, iterations=2)
        blueMask = cv2.morphologyEx(blueMask, cv2.MORPH_OPEN, kernel)
        blueMask = cv2.dilate(blueMask, kernel, iterations=1)

        # Find contours in the image
        (cnts, _) = cv2.findContours(blueMask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        center = None

        # Check to see if any contours were found
        if len(cnts) > 0:
            # Sort the contours and find the largest one
            cnt = sorted(cnts, key=cv2.contourArea, reverse=True)[0]
            # Get the radius of the enclosing circle around the found contour
            ((x, y), radius) = cv2.minEnclosingCircle(cnt)
            # Draw the circle around the contour
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            # Get the moments to calculate the center of the contour (in this case Circle)
            M = cv2.moments(cnt)
            center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

            if center[1] <= 65:
                if 40 <= center[0] <= 140:  # Clear All
                    bpoints = [deque(maxlen=512)]
                    bindex = 0
                    paintWindow[67:, :, :] = 255
            else:
                if colorIndex == 0:
                    bpoints[bindex].appendleft(center)

                # Append the next deque when no contours are detected (object hidden/out of frame)
        else:
            bpoints.append(deque(maxlen=512))
            bindex += 1
        points = [bpoints]
        for i in range(len(points)):
            for j in range(len(points[i])):
                for k in range(1, len(points[i][j])):
                    if points[i][j][k - 1] is None or points[i][j][k] is None:
                        continue
                    cv2.line(frame, points[i][j][k - 1], points[i][j][k], color[i], 2)
                    cv2.line(paintWindow, points[i][j][k - 1], points[i][j][k], color[i], 2)

        # Show the frame and the paintWindow image
        cv2.imshow("Tracking", frame)
        cv2.imshow("Paint", paintWindow)

        # If the 'q' key is pressed, stop the loop
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Cleanup the camera and close any open windows
    camera.release()
    cv2.destroyAllWindows()
