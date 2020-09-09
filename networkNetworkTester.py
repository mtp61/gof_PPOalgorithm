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
TRIALS = 1000

entCoef = 0.01
valCoef = 0.5
maxGradNorm = 0.5

PARAMS_PATH_DEFAULT = "modelParameters-old/modelParameters31500"


# get params name from argv
if len(argv) == 1:
    params_path1 = PARAMS_PATH_DEFAULT
    params_path2 = PARAMS_PATH_DEFAULT
else:
    params_path1 = argv[1]
    params_path2 = argv[2]

# load network
sess = tf.Session()

network1 = PPONetwork(sess, NN_INPUT_SIZE, ACTIONS_SIZE, "network_name1")
network2 = PPONetwork(sess, NN_INPUT_SIZE, ACTIONS_SIZE, "network_name2")

tf.global_variables_initializer().run(session=sess)

params1 = joblib.load(params_path1)
params2 = joblib.load(params_path2)

network1.loadParams(params1)
network2.loadParams(params2)

print(f"\nNetworks { params_path1 }, { params_path2 } loaded")

# make a game
game = GoFGame()

# setup the random number generator
random.seed(time.time())

# main loop
print(f"running { TRIALS } trials")
network1_reward = []
network2_reward = []
for i in range(TRIALS):
    game.reset()  # reset the game

    # randomly assign the networks
    nums = [1, 2, 3, 4]
    random.shuffle(nums)
    network1_players = nums[:2]

    while True:
        players_go, current_state, currently_available_actions = game.getCurrentState()

        if players_go in network1_players:  # network1 is up
            a, v, nlp = network1.step(current_state, currently_available_actions)
        else:  #  network2 is up
            a, v, nlp = network2.step(current_state, currently_available_actions)

        reward, done, info = game.step(a[0])

        if done:  # game is done
            # assign rewards
            for j in range(4):
                if j + 1 in network1_players:
                    network1_reward.append(reward[j])
                else:
                    network2_reward.append(reward[j])

            print(f"game { i + 1 } complete")

            break
        
# print info
def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return m, m-h, m+h

mean1, low1, high1 = mean_confidence_interval(network1_reward)
mean2, low2, high2 = mean_confidence_interval(network2_reward)

print(f"mean, 95% confidence intervals")
print(f"{ params_path1 } reward: { round(mean1, 4) }, [{ round(low1, 4) } - { round(high1, 4) }]")
print(f"{ params_path2 } reward: { round(mean2, 4) }, [{ round(low2, 4) } - { round(high2, 4) }]")
