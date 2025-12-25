import cv2
import numpy as np

# Create a blank image (500x500 pixels, 3 color channels)
image = np.zeros((500, 500, 3), dtype="uint8")

# Define the start and end points
start_point = (0, 250)
end_point = (500, 250)

# Define the line color (Blue in BGR)
color = (255, 0, 0)

# Define the line thickness
thickness = 5

# Draw the line
cv2.line(image, start_point, end_point, color, thickness)

# Display the image
cv2.imshow("Line", image)
cv2.waitKey(0)
cv2.destroyAllWindows()