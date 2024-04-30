import napari
import cv2

def capture_camera():
    # Open the default camera (usually the webcam)
    cap = cv2.VideoCapture(0)
    
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        
        # Convert the frame from BGR to RGB (required for Napari)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Display the frame in Napari
        viewer.add_image(frame_rgb, name='Camera Feed', rgb=True)
        
        # Update the Napari viewer
        viewer.refresh()

        # If 'q' is pressed, exit the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release the camera and close the Napari viewer
    cap.release()
    cv2.destroyAllWindows()

# Create a Napari viewer
viewer = napari.Viewer()

# Capture and display the camera feed
capture_camera()