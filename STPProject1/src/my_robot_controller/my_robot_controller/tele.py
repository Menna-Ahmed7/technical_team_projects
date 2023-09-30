import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
import sys
import tty
import termios
import threading
import logging


class TurtleTeleop(Node):
    def __init__(self):
        #--------initialization for the node and publisher--------#
        super().__init__("turtle_teleop")
        self.publishermotor = self.create_publisher(Float64, "motor", 10)
        self.publishersteer = self.create_publisher(Float64, "steer", 10)
        self.motor = 0.0
        self.steer = 0.0

    def teleop(self):
        maxV = 1500.0
        minV = -1500.0
        maxS = 2.0
        minS = -2.0
        msgm = Float64()
        msgs = Float64()

        #--------to get input from the user using stdin-------#
        settings = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin.fileno())
        self.get_logger().info("Use arrow keys to control the turtle. Press 'q' to quit.")

        #--------trying to control when the user inputs nothing-------#
        stop_flag = False
        # Create a threading.Event() to signal the timeout function to be called
        timeout_event = threading.Event()
        def timeout_function():
            self.get_logger().info("YOU'VE ENTERED nothing\n")

        #--------to loop waiting for the user input and break only on pressing q--------#
        while True:
            # Start the timer thread
            timer_thread = threading.Timer(1.0, timeout_function)
            timer_thread.start()
            #--------reading input from user and applying values for motor and steer based on the input--------#
            key = sys.stdin.read(1)
            if key == "" or key == "\x1b" or key == "q" or key=="Q":  # Escape key
                stop_flag = True
                break
            elif key == "w" or key == "W":
                #--------if the vehicle is moving backward, to fasten moving forward increase the speed------#
                if self.motor < 0.0: 
                    self.motor += 50.0
                self.motor += 50.0
                if self.motor > maxV:
                    self.motor = maxV
            elif key == "s" or key == "S":
                #--------if the vehicle is moving forward, to fasten moving backward increase 
                # the speed in the opposite direction------#
                if self.motor > 0.0:
                    self.motor -= 50.0
                self.motor -= 50.0
                if self.motor < minV:
                    self.motor = minV
            elif key == "a" or key == "A":
                if self.steer < 0.0:
                    self.steer = 0.0
                self.steer += 0.05
                if self.steer > maxS:
                    self.steer = maxS
            elif key == "d" or key == "D":
                if self.steer > 0.0:
                    self.steer = 0.0
                self.steer -= 0.05
                if self.steer < minS:
                    self.steer = minS
            elif key == " ":  # addition---> press space to stop the car from steering
                self.steer = 0.0

            # If the user presses a key, set the stop flag
            # and cancel the timer thread
            if key != "":
                stop_flag = True
                timer_thread.cancel()

            # If the stop flag is not set and the user has not pressed a key
            # for 1 second, signal the timeout function to be called
            #timer_thread.is_alive() will be false as the second
            #has finished and the user inputed nothing
            if not stop_flag and not timer_thread.is_alive():
                timeout_event.set()
                # Wait for the timeout event to be cleared
                timeout_event.wait()
                timeout_event.clear()
            else:
                self.get_logger().info("YOU'VE ENTERED " + key)
                msgm.data = self.motor
                msgs.data = self.steer
                self.publishermotor.publish(msgm)
                self.publishersteer.publish(msgs)

        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)


def main(args=None):
    rclpy.init(args=args)
    turtle_teleop = TurtleTeleop()
    turtle_teleop.teleop()
    rclpy.shutdown()

