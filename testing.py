import random
import time

from GoFGame import GoFGame
import gameLogic


itr = 100
max_turns = 1000

start_time = time.time()
total_turns = 0

env = GoFGame()


players_go, current_state, currently_available_actions = env.getCurrentState()

print(len(current_state))
print(len(currently_available_actions))


"""
print(f"simulating { itr } random games")

for i in range(itr):
    env.reset()

    counter = 0
    while True:
        players_go, current_state, currently_available_actions = env.getCurrentState()
        
        # pick an action
        options = []
        for j, val in enumerate(currently_available_actions):
            if val:
                options.append(j)
        action = options[random.randrange(len(options))]

        reward, done, info = env.step(action)

        counter += 1

        if done:
            total_turns += info['num_turns']
            break

        if counter >= max_turns:
            raise Exception("Hit max turns")
            break
        
    print(f"game { i + 1 } finished")

print(f"{ itr } games, { round(itr / (time.time() - start_time) * 60) } games per min, { round(total_turns / itr) } average turns")
"""