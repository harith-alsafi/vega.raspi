from picamera2 import Picamera2

picam2 = Picamera2()
config = picam2.create_still_configuration()
picam2.configure(config)

picam2.start()

picam2.capture_array()
picam2.capture_file("demo.jpg")
picam2.stop()