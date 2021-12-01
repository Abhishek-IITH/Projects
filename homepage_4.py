from flask import Flask, request, render_template
import time
import serial
import RPi.GPIO as GPIO
import datetime
import pigpio

#PIN SETUP

ser = serial.Serial(port = '/dev/ttyAMA0',
                    baudrate = 115200,
                    parity = serial.PARITY_NONE,
                    stopbits = serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=1)
#servoPIN = 12
IN1 = 16
IN2 = 20
IN3 = 21
IN4 = 26
servoPIN = 17
speed_control1 = 13
speed_control2 = 18
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

#GPIO.setup(servoPIN, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)
GPIO.setup(speed_control1, GPIO.OUT)
GPIO.setup(speed_control2, GPIO.OUT)
s1 = GPIO.PWM(speed_control1, 490)
s2 = GPIO.PWM(speed_control2, 490)
s1.start(75)
s2.start(80)

pi = pigpio.pi()

#Speed and Yaw
max_speed = 3.0
max_turn = 180.0

#PIN SETUP END

#Bot Movement Logic
def forward(distcm):
    GPIO.output(IN1,1)
    GPIO.output(IN2,0)
    GPIO.output(IN3,1)
    GPIO.output(IN4,0)
    time.sleep(distcm)
    
def backward(distcm):
    GPIO.output(IN1,0)
    GPIO.output(IN2,1)
    GPIO.output(IN3,0)
    GPIO.output(IN4,1)
    time.sleep(distcm)
	
    
#Bot Movement Logic
def back(distcm):
    GPIO.output(IN1,1)
    GPIO.output(IN2,0)
    GPIO.output(IN3,1)
    GPIO.output(IN4,0)
    time.sleep(distcm)
    
def stop(t):
    GPIO.output(IN1,0)
    GPIO.output(IN2,0)
    GPIO.output(IN3,0)
    GPIO.output(IN4,0)
    time.sleep(t/5)

def right_turn(t):
    time.sleep(0.2)
    GPIO.output(IN1,1)
    GPIO.output(IN2,0)
    GPIO.output(IN3,0)
    GPIO.output(IN4,1)
    time.sleep(t)

def left_turn(t):
    time.sleep(0.2)
    GPIO.output(IN1,0)
    GPIO.output(IN2,1)
    GPIO.output(IN3,1)
    GPIO.output(IN4,0)
    time.sleep(t)

def set_pwm(pwm1, pwm2):
    s1.ChangeDutyCycle(pwm1)
    s2.ChangeDutyCycle(pwm2)
    
def package_delivery(t):
    pi.set_servo_pulsewidth(servoPIN, 1000)
    time.sleep(t)
    pi.set_servo_pulsewidth(servoPIN, 2200)
    time.sleep(t)
    pi.set_servo_pulsewidth(servoPIN, 1000)
    time.sleep(t)
    pi.set_servo_pulsewidth(servoPIN, 0)
    pi.stop()


app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/forward')
def ifwd():
    if 't' in request.args:  
        forward(float(request.args['t']))
    else:
        forward(1)
    stop(1)
    return 'Going Forward'
    
@app.route('/back')
def iback():
    if 't' in request.args:  
        backward(float(request.args['t']))
    else:
        back(1)
    stop(1)
    return 'Going Forward'
    


@app.route('/right')
def iright():
    t = float(request.args['t'])
    right_turn(t)
    #set_pwm(100,10)
    stop(1)
    return 'Making right turn'


@app.route('/left')
def ileft():
    t = float(request.args['t'])
    left_turn(t)
    stop(1)
    return 'Going left turn'

@app.route('/controlfwd')
def controlfwd():
    #bot = request.args['b']
    speed = float(request.args['s'])
    yaw = float(request.args['o'])
    dist = float(request.args['d'])

    pwm = (speed/max_speed)*100

    set_pwm(pwm, pwm)
    forward(dist)
    stop(1)
    return "control_fwd"    


@app.route('/controlbck')
def controlbck():
    #bot = request.args['b']
    speed = float(request.args['s'])
    yaw = float(request.args['o'])
    dist = float(request.args['d'])

    pwm = (speed/max_speed)*100

    set_pwm(pwm, pwm)
    back(dist)
    stop(1)

    return "control_bck"
    
@app.route('/drop')
def drop():
    t = float(request.args['t'])
    package_delivery(t)
    stop(0.5)
    
    return "Package Delivered"
    



if __name__ == '__main__':
    try:
        app.run(debug=True, port=8080, host='0.0.0.0')
    except:
        print('')
