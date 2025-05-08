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
    
    def __displacement(self, old_arm_deg, old_hand_deg, arm_deg, hand_deg):
        old_arm_cos, old_arm_sin = self.__get_cos_and_sin(old_arm_deg)
        arm_cos, arm_sin = self.__get_cos_and_sin(arm_deg)
        old_hand_cos, old_hand_sin = self.__get_cos_and_sin(old_hand_deg)
        hand_cos, hand_sin = self.__get_cos_and_sin(hand_deg)

        x_old = self.arm_length * old_arm_cos + self.hand_length * old_hand_cos + self.robot_width
        y_old = self.arm_length * old_arm_sin + self.hand_length * old_hand_sin + self.robot_height

        x = self.arm_length * arm_cos + self.hand_length * hand_cos + self.robot_width
        y = self.arm_length * arm_sin + self.hand_length * hand_sin + self.robot_height

        if y < 0:
            if y_old <= 0:
                return math.sqrt(x_old*x_old + y_old*y_old) - math.sqrt(x*x + y*y)
            return (x_old - y_old*(x-x_old) / (y - y_old)) - math.sqrt(x*x + y*y)
        else:
            if y_old  >= 0:
                return 0.0
            return -(x - y * (x_old-x)/(y_old-y)) + math.sqrt(x_old*x_old + y_old*y_old)

    def set_angles(self, arm, hand):
        self.arm_angle = arm
        self.hand_angle = hand

    def get_angles(self):
        return self.arm_angle, self.hand_angle
    
    def get_position(self):
        return self.position
    
    def move_arm(self, new_arm_angle):
        if new_arm_angle > self.max_arm_angle:
            raise Exception('Crawling Robot: Arm Raised too high. Careful!')
        if new_arm_angle < self.min_arm_angle:
            raise Exception('Crawling Robot: Arm Raised too low. Careful!')
        disp = self.__displacement(self.arm_angle, self.hand_angle, new_arm_angle, self.hand_angle)
        self.position = (self.position[0]+disp, self.position[1])
        self.arm_angle = new_arm_angle

        self.positions.append(self.get_position()[0])
        if len(self.positions) > 100:
            self.positions.pop(0)

    def move_hand(self, new_hand_angle):
        if new_hand_angle > self.max_hand_angle:
            raise Exception('Crawling Robot: Hand Raised too high. Careful!')
        if new_hand_angle < self.min_hand_angle:
            raise Exception('Crawling Robot: Hand Raised too low. Careful!')
        disp = self.__displacement(self.arm_angle, self.hand_angle, self.arm_angle, new_hand_angle)
        self.position = (self.position[0]+disp, self.position[1])
        self.hand_angle = new_hand_angle

        self.positions.append(self.get_position()[0])
        if len(self.positions) > 100:
            self.positions.pop(0)

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

    def draw(self, step_count, step_delay):
        x1, y1 = self.get_position()
        x1 = x1 % self.width

        ## Check Lower Still on the ground
        if y1 != self.groundY:
            raise Exception('Flying Robot!!')

        rotation_angle = self.get_rotation_angle()
        cos_rotation, sin_rotation = self.__get_cos_and_sin(rotation_angle)

        x2 = x1 + self.robot_width * cos_rotation
        y2 = y1 - self.robot_width * sin_rotation

        x3 = x1 - self.robot_height * sin_rotation
        y3 = y1 - self.robot_height * cos_rotation

        x4 = x3 + cos_rotation * self.robot_width
        y4 = y3 - sin_rotation * self.robot_width

        self.canvas.coords(self.robot_body,x1,y1,x2,y2,x4,y4,x3,y3)

        arm_cos, arm_sin = self.__get_cos_and_sin(rotation_angle+self.arm_angle)
        xArm = x4 + self.arm_length * arm_cos
        yArm = y4 - self.arm_length * arm_sin

        self.canvas.coords(self.robot_arm,x4,y4,xArm,yArm)

        hand_cos, hand_sin = self.__get_cos_and_sin(rotation_angle+self.hand_angle)
        xHand = xArm + self.hand_length * hand_cos
        yHand = yArm - self.hand_length * hand_sin

        self.canvas.coords(self.robot_hand,xArm,yArm,xHand,yHand)

        steps = step_count - self.last_step
        if steps == 0: return

        pos = self.positions[-1]
        velocity = pos - self.positions[-2]
        vel2 = (pos - self.positions[0]) / len(self.positions)
        self.vel_avg = .9 * self.vel_avg + .1 * vel2
        vel_msg = '100-step Avg Velocity: %.2f' % self.vel_avg
        velocity_msg = 'Velocity: %.2f' % velocity
        position_msg = 'Position: %2.f' % pos
        step_msg = 'Step: %d' % step_count
        if 'vel_msg' in dir(self):
            self.canvas.delete(self.vel_msg)
            self.canvas.delete(self.pos_msg)
            self.canvas.delete(self.step_msg)
            self.canvas.delete(self.velavg_msg)
        self.velavg_msg = self.canvas.create_text(650,190,text=vel_msg)
        self.vel_msg = self.canvas.create_text(450,190,text=velocity_msg)
        self.pos_msg = self.canvas.create_text(250,190,text=position_msg)
        self.step_msg = self.canvas.create_text(50,190,text=step_msg)
        self.lastStep = step_count