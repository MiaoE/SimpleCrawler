from simple_crawler import SimpleCrawler

class Environment:

    def __init__(self, simple_robot: SimpleCrawler):
        self.robot = simple_robot
        # state: (arm_angle, hand_angle) in bucket numbers, not degree measurements
        self.state = None

        self.n_arm_states = 9
        self.n_hand_states = 13

        min_arm_angle, max_arm_angle = self.robot.get_arm_minmax_angle()
        min_hand_angle, max_hand_angle = self.robot.get_hand_minmax_angle()
        arm_inc = (max_arm_angle - min_arm_angle) / (self.n_arm_states - 1)
        hand_inc = (max_hand_angle - min_hand_angle) / (self.n_hand_states - 1)

        self.arm_buckets = [min_arm_angle + (arm_inc * i) for i in range(self.n_arm_states)]
        self.hand_buckets = [min_hand_angle + (hand_inc * i) for i in range(self.n_hand_states)]

        self.reset()

    def get_current_state(self):
        return self.state
    
    def get_possible_actions(self, state):
        actions = list()
        current_arm, current_hand = state
        if current_arm > 0: actions.append('arm-down')
        if current_arm < self.n_arm_states - 1: actions.append('arm-up')
        if current_hand > 0: actions.append('hand-down')
        if current_hand < self.n_hand_states - 1: actions.append('hand-up')
        return actions
    
    def do_action(self, action):
        next_state, reward = None, None

        oldX, oldY = self.robot.get_position()

        arm, hand = self.state
        
        if action == 'arm-down':
            new_arm = self.arm_buckets[arm - 1]
            self.robot.move_arm(new_arm)
            next_state = (arm - 1, hand)
        if action == 'arm-up':
            new_arm = self.arm_buckets[arm + 1]
            self.robot.move_arm(new_arm)
            next_state = (arm + 1, hand)
        
        if action == 'hand-down':
            new_hand = self.hand_buckets[hand - 1]
            self.robot.move_hand(new_hand)
            next_state = (arm, hand - 1)
        if action == 'hand-up':
            new_hand = self.hand_buckets[hand + 1]
            self.robot.move_hand(new_hand)
            next_state = (arm, hand + 1)

        newX, newY = self.robot.get_position()
        reward = newX - oldX

        self.state = next_state
        return next_state, reward
    
    def reset(self):
        arm_state = self.n_arm_states // 2
        hand_state = self.n_hand_states // 2
        self.state = (arm_state, hand_state)
        self.robot.set_angles(self.arm_buckets[arm_state], self.hand_buckets[hand_state])
        self.robot.positions = [20, self.robot.get_position()[0]]
