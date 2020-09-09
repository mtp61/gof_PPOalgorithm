import tensorflow as tf
import joblib
import numpy as np
import random
import time
import scipy.stats
from sys import argv

from network import NN_INPUT_SIZE, ACTIONS_SIZE
from GoFGame import GoFGame
from ppoNetwork import PPONetwork, PPOModel


# constants
TRIALS = 250

entCoef = 0.01
valCoef = 0.5
maxGradNorm = 0.5

PARAMS_NAME_DEFAULT = "modelParameters18000"


# get params name from argv
if len(argv) == 1:
    params_name = PARAMS_NAME_DEFAULT
else:
    params_name = "modelParameters" + argv[1]

# load network
sess = tf.Session()

network = PPONetwork(sess, NN_INPUT_SIZE, ACTIONS_SIZE, "network_name")
model = PPOModel(sess, network, NN_INPUT_SIZE, ACTIONS_SIZE, entCoef, valCoef, maxGradNorm)

tf.global_variables_initializer().run(session=sess)

params = joblib.load("modelParameters/" + params_name)
#print(params[0][0][0:5])
network.loadParams(params)

print(f"\nNetwork { params_name } loaded")

# make a game
game = GoFGame()

# setup the random number generator
random.seed(time.time())

# main loop
print(f"running { TRIALS } trials")
network_reward = []
random_reward = []
for i in range(TRIALS):
    game.reset()  # reset the game

    # randomly assign the random net and the player net
    nums = [1, 2, 3, 4]
    random.shuffle(nums)
    random_players = nums[:2]

    while True:
        players_go, current_state, currently_available_actions = game.getCurrentState()

        if players_go in random_players:  # random player is up
            possible_actions = []
            for n, v in enumerate(currently_available_actions[0]):
                if v == 0:  # this means the action is available
                    possible_actions.append(n)
            action = possible_actions[random.randrange(len(possible_actions))]
        else:  # network is up
            a, v, nlp = network.step(current_state, currently_available_actions)
            action = a[0]

        reward, done, info = game.step(action)

        if done:  # game is done
            # assign rewards
            for j in range(4):
                if j + 1 in random_players:
                    random_reward.append(reward[j])
                else:
                    network_reward.append(reward[j])

            print(f"game { i + 1 } complete")

            break
        
# print info
def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return m, m-h, m+h

n_mean, n_low, n_high = mean_confidence_interval(network_reward)
r_mean, r_low, r_high = mean_confidence_interval(random_reward)

print(f"\nNetwork { params_name }")
print(f"mean, 95% confidence intervals")
print(f"network reward: { round(n_mean, 4) }, [{ round(n_low, 4) } - { round(n_high, 4) }]")
#print(f"random reward: { round(r_mean, 2) }, [{ round(r_low, 2) } - { round(r_high, 2) }]")
