from gpiozero import AngularServo 
from time import sleep

servo = AngularServo(18, min_pulse_width=0.001, max_pulse_width=0.0023)

start_point = (0, 90)
end_point = (10, -90)

m = (start_point[1] - end_point[1]) / (start_point[0]-end_point[0])
n = start_point[1] - m * start_point[0]
equation = lambda x: max(min(m * x + n, 50), -20)

#times = [x for x in range(0, 11, 1)] 
servo.angle = 50.0
sleep(0.5)
servo.angle = 0.0
sleep(0.5)
servo.angle = -36.0
sleep(0.5)
servo.angle = 0.0
sleep(0.5)
servo.angle = 36.0

