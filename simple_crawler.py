import math
from math import pi as PI

class SimpleCrawler:
    def __init__(self, canvas):
        self.canvas = canvas
        self.vel_avg = 0
        self.last_step = 0

        self.width = canvas.winfo_reqwidth()
        self.height = canvas.winfo_reqheight()
        self.ground_height = 40
        self.groundY = self.height - self.ground_height

        self.ground = canvas.create_rectangle(0, self.groundY, self.width, self.height, fill='blue')

        self.arm_angle = self.old_arm_degree = 0.0
        self.hand_angle = self.old_hand_degree = -PI / 6

        self.max_arm_angle = PI / 6
        self.min_arm_angle = -PI / 6

        self.max_hand_angle = 0
        self.min_hand_angle = -(5.0 / 6.0) * PI

        self.robot_width = 80
        self.robot_height = 40
        self.position = (20, self.groundY)
        self.robot_body = canvas.create_polygon(0,0,0,0,0,0,0,0, fill='green')

        self.arm_length = 60
        self.robot_arm = canvas.create_line(0,0,0,0, fill='orange', width=5)

        self.hand_length = 40
        self.robot_hand = canvas.create_line(0,0,0,0, fill='red', width=3)

        self.positions = [0,0]

    def __get_cos_and_sin(self, angle):
        return math.cos(angle), math.sin(angle)
    
    def __displacement(self):
        pass

    def set_angles(self, arm, hand):
        self.arm_angle = arm
        self.hand_angle = hand

    def get_angles(self):
        return self.arm_angle, self.hand_angle
    
    def get_position(self):
        return self.position
    
    def move_arm(self, new_arm_angle):
        pass

    def move_hand(self, new_hand_angle):
        pass

    def get_arm_minmax_angle(self):
        return self.min_arm_angle, self.max_arm_angle
    
    def get_hand_minmax_angle(self):
        return self.min_hand_angle, self.max_hand_angle
    
    def get_rotation_angle(self):
        arm_cos, arm_sin = self.__get_cos_and_sin(self.arm_angle)
        hand_cos, hand_sin = self.__get_cos_and_sin(self.hand_angle)
        x = self.arm_length * arm_cos + self.hand_length * hand_cos + self.robot_width
        y = self.arm_length * arm_sin + self.hand_length * hand_sin + self.robot_height
        if y < 0:
            return math.atan(-y / x)
        return 0.0

    def draw(self):
        x1, y1 = self.getRobotPosition()
        x1 = x1 % self.totWidth

        ## Check Lower Still on the ground
        if y1 != self.groundY:
            raise Exception('Flying Robot!!')

        rotationAngle = self.getRotationAngle()
        cosRot, sinRot = self.__getCosAndSin(rotationAngle)

        x2 = x1 + self.robotWidth * cosRot
        y2 = y1 - self.robotWidth * sinRot

        x3 = x1 - self.robotHeight * sinRot
        y3 = y1 - self.robotHeight * cosRot

        x4 = x3 + cosRot*self.robotWidth
        y4 = y3 - sinRot*self.robotWidth

        self.canvas.coords(self.robotBody,x1,y1,x2,y2,x4,y4,x3,y3)

        armCos, armSin = self.__getCosAndSin(rotationAngle+self.armAngle)
        xArm = x4 + self.armLength * armCos
        yArm = y4 - self.armLength * armSin

        self.canvas.coords(self.robotArm,x4,y4,xArm,yArm)

        handCos, handSin = self.__getCosAndSin(self.handAngle+rotationAngle)
        xHand = xArm + self.handLength * handCos
        yHand = yArm - self.handLength * handSin

        self.canvas.coords(self.robotHand,xArm,yArm,xHand,yHand)


        # Position and Velocity Sign Post
#        time = len(self.positions) + 0.5 * sum(self.angleSums)
#        velocity = (self.positions[-1]-self.positions[0]) / time
#        if len(self.positions) == 1: return
        steps = (stepCount - self.lastStep)
        if steps==0:return
 #       pos = self.positions[-1]
#        velocity = (pos - self.lastPos) / steps
  #      g = .9 ** (10 * stepDelay)
#        g = .99 ** steps
#        self.velAvg = g * self.velAvg + (1 - g) * velocity
 #       g = .999 ** steps
 #       self.velAvg2 = g * self.velAvg2 + (1 - g) * velocity
        pos = self.positions[-1]
        velocity = pos - self.positions[-2]
        vel2 = (pos - self.positions[0]) / len(self.positions)
        self.velAvg = .9 * self.velAvg + .1 * vel2
        velMsg = '100-step Avg Velocity: %.2f' % self.velAvg
#        velMsg2 = '1000-step Avg Velocity: %.2f' % self.velAvg2
        velocityMsg = 'Velocity: %.2f' % velocity
        positionMsg = 'Position: %2.f' % pos
        stepMsg = 'Step: %d' % stepCount
        if 'vel_msg' in dir(self):
            self.canvas.delete(self.vel_msg)
            self.canvas.delete(self.pos_msg)
            self.canvas.delete(self.step_msg)
            self.canvas.delete(self.velavg_msg)
 #           self.canvas.delete(self.velavg2_msg)
 #       self.velavg2_msg = self.canvas.create_text(850,190,text=velMsg2)
        self.velavg_msg = self.canvas.create_text(650,190,text=velMsg)
        self.vel_msg = self.canvas.create_text(450,190,text=velocityMsg)
        self.pos_msg = self.canvas.create_text(250,190,text=positionMsg)
        self.step_msg = self.canvas.create_text(50,190,text=stepMsg)
#        self.lastPos = pos
        self.lastStep = stepCount
#        self.lastVel = velocity