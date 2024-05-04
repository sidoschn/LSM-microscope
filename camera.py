# import napari
# import cv2

# def capture_camera():
#     # Open the camera
#     cap = cv2.VideoCapture(0)
    
#     while True:
#         # Capture frame-by-frame
#         ret, frame = cap.read()
        
#         # Convert the frame from BGR to RGB (required for Napari)
#         frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
#         # Display the frame in Napari
#         viewer.add_image(frame_rgb, name='Camera Feed', rgb=True)
        
#         # Update the Napari viewer
#         #viewer.refresh()

#         # If 'q' is pressed, exit the loop
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
    
#     # Release the camera and close the Napari viewer
#     cap.release()
#     cv2.destroyAllWindows()

# # Create a Napari viewer
# viewer = napari.Viewer()

# # Capture and display the camera feed
# capture_camera()

import matplotlib.pyplot as plt
import pco
import numpy as np


height = 100
width = 100

with pco.Camera(interface = 'USB 3.0') as cam:

    # get image width and height
    cam_settings = cam.rec.get_settings()
    #width = cam_settings["width"]
    #height = cam_settings["height"]

    # Create a figure and axis for plotting
    fig, ax = plt.subplots()

    # Initialize the plot with an empty image
    img_data = np.zeros((height,width))
    img_plot = ax.imshow(img_data)

    # while True:
    #     cam.record(mode="sequence")
    #     img, meta = cam.image()
        
    #     img_plot.set_data(img)

    #     plt.draw()
        #plt.show()
        #plt.close()