import random

from util import Counter, flip_coin

class ReinforcementAgent:
    def __init__(self, actionFcn=None, num_training=100, epsilon=0.5, alpha=0.5, gamma=1):
        if actionFcn == None:
            actionFcn = lambda state: state.get_legal_actions()
        self.action_fcn = actionFcn
        self.episodes_elapsed = 0
        self.accum_train_rewards = 0.0
        self.accum_test_rewards = 0.0
        self.num_training = int(num_training)
        self.epsilon = float(epsilon)
        self.alpha = float(alpha)
        self.discount = float(gamma)

    def get_legal_actions(self, state):
        return self.action_fcn(state)
    
    def observe_transition(self, state, action, next_state, delta_rew):
        self.episode_rewards += delta_rew
        self.update(state, action, next_state, delta_rew)

    def start_episode(self):
        self.last_state = None
        self.last_action = None
        self.episode_rewards = 0.0

    def end_episode(self):
        if self.episodes_elapsed < self.num_training:
            self.accum_train_rewards += self.episode_rewards
        else:
            self.accum_test_rewards += self.episode_rewards
        
        self.episodes_elapsed += 1

        if self.episodes_elapsed >= self.num_training:
            self.alpha = 0.0
            self.epsilon = 0.0

    def is_training(self):
        return self.episodes_elapsed < self.num_training
    
    def is_testing(self):
        return not self.is_training()
    
    def set_epsilon(self, epsilon):
        self.epsilon = epsilon

    def set_learning_rate(self, alpha):
        self.alpha = alpha

    def set_discount(self, gamma):
        self.gamma = gamma

    def do_action(self, state, action):
        self.last_state = state
        self.last_action = action

class QLearningAgent(ReinforcementAgent):
    def __init__(self, **kargs):
        super.__init__(self, **kargs)
        self.q_values = Counter()

    def get_qVal(self, state, action):
        return self.q_values[(state, action)]
    
    def compute_val_from_qVal(self, state):
        max_value = None
        legal_actions = self.get_legal_actions(state)
        for a in legal_actions:
            q = self.get_qVal(state, a)
            if max_value is None or q > max_value:
                max_value = q
        return max_value if max_value is not None else 0.0
    
    def compute_action_from_qVal(self, state):
        best_action = None
        best_q = None
        legal_actions = self.get_legal_actions(state)
        for a in legal_actions:
          q = self.get_qVal(state, a)
          if best_q is None or q > best_q:
            best_q = q
            best_action = a
        return best_action
    
    def get_action(self, state):
        legalActions = self.get_legal_actions(state)
        action = None
        
        if flip_coin(self.epsilon):
          if len(legalActions) > 0:
            action = random.choice(legalActions)
        else:
          action = self.compute_action_from_qVal(state)
        return action

    def update(self, state, action, nextState, reward):
        # Q_k+1(s, a) = (1 - alpha) Q_k(s, a) + alpha [R(s, a, s') + gamma max_a'{Q(s', a')}]
        # find max_a'{Q(s', a')}
        next_actions = self.get_legal_actions(nextState)
        next_q = None
        for a in next_actions:
          exploration_fcn = self.get_qVal(nextState, a)
          if next_q is None or exploration_fcn > next_q:
            next_q = exploration_fcn
        if next_q is not None:
          new_q = (1 - self.alpha) * self.get_qVal(state, action) + self.alpha * (reward + self.discount * next_q)
        else:
          new_q = (1 - self.alpha) * self.get_qVal(state, action) + self.alpha * (reward)
        self.q_values[(state, action)] = new_q
          
    def get_policy(self, state):
        return self.compute_action_from_qVal(state)

    def get_value(self, state):
        return self.compute_val_from_qVal(state)