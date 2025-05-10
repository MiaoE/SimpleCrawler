import argparse

from game_visuals import run

if __name__ == '__main__':
    parse = True
    if parse:
        parser = argparse.ArgumentParser()
        parser.add_argument('--epsilon', help='change the initial epsilon (explore/exploit probability) value, must be in between 0-1, may result in slight deviation from the inputted value', required=False)
        parser.add_argument('--alpha', help='change the initial alpha (learning rate) value, must be between 0-1, may result in slight deviation from the inputted value', required=False)
        parser.add_argument('--gamma', help='change the initial gamma (discount rate) value, must be between 0-1, may result in slight deviation from the inputted value', required=False)

        args = parser.parse_args()

        kwargs = {}
        if args.alpha:
            alpha = float(args.alpha)
            if alpha < 0.0 or alpha > 1.0:
                raise ValueError('Argument alpha invalid')
            kwargs['alpha'] = alpha
        if args.epsilon:
            epsilon = float(args.epsilon)
            if epsilon < 0.0 or epsilon > 1.0:
                raise ValueError('Argument epsilon invalid')
            kwargs['epsilon'] = epsilon
        if args.gamma:
            gamma = float(args.gamma)
            if gamma < 0.0 or gamma > 1.0:
                raise ValueError('Argument gamma invalid')
            kwargs['gamma'] = gamma
        
        # if not kwargs:
        #     run()
        # else:
        # missing kwargs is handled in game_visuals.App, no need to handle it here
        run(**kwargs)
    else:
        run()
