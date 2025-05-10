import tkinter
import time
import threading
import sys
import math
from math import pi as PI

import reinforcement_learning_agent
import simple_crawler
import environment

class App:
    def __init__(self, win, **kwargs):
        # default epsilon 0.5 (with sigmoid inverse the value is 0)
        self.ep = self.sigmoid_inv_round(kwargs['epsilon']) if 'epsilon' in kwargs.keys() else 0
        # default gamma and alpha 0.8 (with sigmoid inverse the value is 2)
        self.ga = self.sigmoid_inv_round(kwargs['gamma']) if 'gamma' in kwargs.keys() else 2
        self.al = self.sigmoid_inv_round(kwargs['alpha']) if 'alpha' in kwargs.keys() else 2
        self.step_count = 0

        # intervals of the sigmoid inverse values
        self.dec = -0.5
        self.inc = 0.5
        self.tick = 0.1

        self.__initGUI(win)

        self.robot = simple_crawler.SimpleCrawler(self.canvas)
        self.robot_env = environment.Environment(self.robot)

        actionFcn = lambda state: self.robot_env.get_possible_actions(state)
        self.agent = reinforcement_learning_agent.QLearningAgent(actionFcn=actionFcn, **kwargs)

        self.agent.set_epsilon(self.epsilon)
        self.agent.set_learning_rate(self.alpha)
        self.agent.set_discount(self.gamma)

        self.running = True
        self.stopped = False
        self.steps_to_skip = 0
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def __initGUI(self, win):
        self.win = win

        win.grid()

        self.setup_speed(win)
        self.setup_epsilon(win)
        self.setup_gamma(win)
        self.setup_alpha(win)

        self.canvas = tkinter.Canvas(window, height=200, width=1000)
        self.canvas.grid(row=2, columnspan=10)

    def setup_speed(self, win):
        """
        Sets up the speed button. 
        Increments and decrements by powers of 2 (doubling or halfing speeds)
        """
        self.speed_minus = tkinter.Button(win,
        text="-",command=(lambda: self.increment_speed(.5)))
        self.speed_minus.grid(row=0, column=0)

        self.speed_label = tkinter.Label(win, text='Step Delay: %.5f' % (self.tick))
        self.speed_label.grid(row=0, column=1)

        self.speed_plus = tkinter.Button(win,
        text="+",command=(lambda: self.increment_speed(2)))
        self.speed_plus.grid(row=0, column=2)

    def setup_epsilon(self, win):
        """
        Sets up the epsilon button (explore/exploit probability).
        """
        self.epsilon_minus = tkinter.Button(win,
        text="-",command=(lambda: self.increment_epsilon(self.dec)))
        self.epsilon_minus.grid(row=0, column=3)

        self.epsilon = self.sigmoid(self.ep)
        self.epsilon_label = tkinter.Label(win, text='Epsilon: %.3f' % (self.epsilon))
        self.epsilon_label.grid(row=0, column=4)

        self.epsilon_plus = tkinter.Button(win,
        text="+",command=(lambda: self.increment_epsilon(self.inc)))
        self.epsilon_plus.grid(row=0, column=5)

    def setup_gamma(self, win):
        """
        Sets up the gamma button (discount ratio).
        """
        self.gamma_minus = tkinter.Button(win,
        text="-",command=(lambda: self.increment_gamma(self.dec)))
        self.gamma_minus.grid(row=1, column=0, padx=10)

        self.gamma = self.sigmoid(self.ga)
        self.gamma_label = tkinter.Label(win, text='Discount: %.3f' % (self.gamma))
        self.gamma_label.grid(row=1, column=1)

        self.gamma_plus = tkinter.Button(win,
        text="+",command=(lambda: self.increment_gamma(self.inc)))
        self.gamma_plus.grid(row=1, column=2, padx=10)

    def setup_alpha(self, win):
        """
        Sets up the alpha button (learning rate).
        """
        self.alpha_minus = tkinter.Button(win,
        text="-",command=(lambda: self.increment_alpha(self.dec)))
        self.alpha_minus.grid(row=1, column=3, padx=10)

        self.alpha = self.sigmoid(self.al)
        self.alpha_label = tkinter.Label(win, text='Learning Rate: %.3f' % (self.alpha))
        self.alpha_label.grid(row=1, column=4)

        self.alpha_plus = tkinter.Button(win,
        text="+",command=(lambda: self.increment_alpha(self.inc)))
        self.alpha_plus.grid(row=1, column=5, padx=10)

    def increment_speed(self, inc):
        """
        Changes tick speed.
        """
        self.tick *= inc
        self.speed_label['text'] = 'Step Delay: %.5f' % (self.tick)

    def increment_epsilon(self, inc):
        """
        Changes epsilon value.
        """
        self.ep += inc
        self.epsilon = self.sigmoid(self.ep)
        self.agent.set_epsilon(self.epsilon)
        self.epsilon_label['text'] = 'Epsilon: %.3f' % (self.epsilon)

    def increment_gamma(self, inc):
        """
        Changes gamma value.
        """
        self.ga += inc
        self.gamma = self.sigmoid(self.ga)
        self.agent.set_discount(self.gamma)
        self.gamma_label['text'] = 'Discount: %.3f' % (self.gamma)

    def increment_alpha(self, inc):
        """
        Changes alpha value.
        """
        self.al += inc
        self.alpha = self.sigmoid(self.al)
        self.agent.set_learning_rate(self.alpha)
        self.alpha_label['text'] = 'Learning Rate: %.3f' % (self.alpha)

    def sigmoid(self, x):
        """
        Returns the sigmoid of a value. Result ranges 0-1.
        """
        return 1.0 / (1.0 + 2.0 ** (-x))
    
    def __round_half_int(self, x):
        """
        Round a float to the closest half integer (0.5).
        """
        return round(x * 2) / 2

    def sigmoid_inv_round(self, x):
        """
        Converts a float in between 0-1 to a rounded pre-sigmoid value by 0.5 intervals.
        """
        # if x=1, 1/0 returns error
        return self.__round_half_int(-math.log2(1 / x - 1)) if x < 1 else self.__round_half_int(-math.log2(1 / 0.998 - 1))
    
    def exit(self):
        self.running = False
        for i in range(5):
            if not self.stopped:
                time.sleep(0.1)
        try:
            self.win.destroy()
        except:
            pass
        sys.exit(0)

    def step(self):
        """
        Perform a step, consists of choosing and performing an action and observing the result.
        """
        self.step_count += 1

        state = self.robot_env.get_current_state()
        actions = self.robot_env.get_possible_actions(state)
        if len(actions) == 0.0:
            # should never reach here
            self.robot_env.reset()
            state = self.robot_env.get_current_state()
            actions = self.robot_env.get_possible_actions(state)
            print('Reset!')
        action = self.agent.get_action(state)
        if action == None:
            raise Exception('None action returned: Code Not Complete')
        nextState, reward = self.robot_env.do_action(action)
        self.agent.observe_transition(state, action, nextState, reward)

    def run(self):
        self.step_count = 0
        self.agent.start_episode()
        while True:
            min_sleep = 0.01
            tm = max(min_sleep, self.tick)
            time.sleep(tm)
            self.steps_to_skip = int(tm / self.tick) - 1

            if not self.running:
                self.stopped = True
                break
            for i in range(self.steps_to_skip):
                self.step()
            self.steps_to_skip = 0
            self.step()
        self.agent.end_episode()

    def start(self):
        self.win.mainloop()

def run(**kwargs):
    global window
    window = tkinter.Tk()
    window.title("Simple Crawler")
    window.resizable(0, 0)

    app = App(window, **kwargs)
    def update_gui():
        app.robot.draw(app.step_count, app.tick)
        window.after(10, update_gui)
    update_gui()

    window.protocol('WM_DELETE_WINDOW', app.exit)
    try:
        app.start()
    except:
        app.exit()