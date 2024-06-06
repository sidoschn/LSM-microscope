from pycromanager import Acquisition, multi_d_acquisition_events

try:
    # Check if Micro-Manager is running and ZMQ server is enabled on port 4827
    with Acquisition(directory='/', name='acquisition_name') as acq:
        # Create events for acquisition
        events = multi_d_acquisition_events(num_time_points=0)
        print(f"Acquisition events created: {events}")

        # Start the acquisition
        acq.acquire(events)
        print("Acquisition completed successfully.")

except Exception as e:
    print(f"An error occurred: {e}")
