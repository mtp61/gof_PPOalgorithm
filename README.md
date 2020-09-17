# gof_PPOalgorithm

Application of proximal policy optimization algorithm to the card game Gang of Four using Tensorflow. This project is based of a similar project by Henry Charlesworth (https://github.com/henrycharlesworth/big2_PPOalgorithm) in which he uses PPO for the game Big 2, which is very similar to Gang of Four. Notably, the files ppoNetwork.py, ppoSimulation.py, and vectorGame.py, which are all critical for the implementation of the network, are all nearly identical to their versions in big2_PPOalgorithm. My knowledge of tensorflow, specifically deep reinforcement learning and PPO, is not complete enough to do a project as complex as this one on my own from scratch. 

## Client

This project includes both the network code and a python client which can connect to gof-online (https://github.com/mtp61/gof-online), my web version of Gang of Four. This makes it easy to play against the network with any combination of human and network players. Note the network requires tensorflow==1.14 to run correctly. 

## Network Structure

The structure of the network and the training procedures are almost exactly the same as those proposed by Henry Charlesworth’s big2_PPOalgorithm. See his paper (https://arxiv.org/pdf/1808.10442.pdf) for more details. The way of structuring the network to enable it to pick an action is really cool and would not have thought of it on my own. I didn’t find it necessary to alter any of the hyperparameters or the network structure. The player is given quite limited information about the game state. All it knows about previous hands is the current hand and the number of cards played by each player. More information would certainly be necessary for an optimal policy, though maybe not for super-(amautur)human play. The only significant improvement I made on the implementation by big2_PPOalgorithm was a much more efficient algorithm for computing possible moves. My algorithm balances space and time complexity to do the minimum required calculations at each step while the implementation in big2_PPOalgorithm completely recalculates the possible actions at every step.

## Training

The repo includes two models in modelParameters.zip, modelParameters/modelParameters55000 and modelParameters-winOnly/modelParameters27000. 27000 was trained using a binary reward function and is very weak, much weaker than the model trained with the standard reward function. For various technical reasons I was only able to train the network for 24 hours, and I believe that the strength would improve considerably if the network was trained for longer. 

## Performance

The most trained network (modelParameters55000) still performs at a sub-human level. The network isn’t terrible, I think it could beat players who are new to the game, but I was able to beat the network often, which given the high variance of Gang of Four shows the network is not very strong. The network occasionally makes baffling plays that no human player would ever do. Sometimes these plays seem objectively bad, with my limited knowledge of the game, but the network also discovered one new strategy that I have never before seen in the hundreds of games I’ve played. 

## Low Gang on a Low Single

The network repeatedly used a novel strategy where it would play a low Gang of Four directly after a low single. This non-intuitive strategy is one that I’ve never seen a human player use, but after more consideration it could be very strong in specific situations. A very quick explanation of why I think this strategy could be strong is that it prevents your opponents from dumping their low singles while gaining the lead with a gang that may not win later in the game. While this may seem a bit out of place, I actually find it to be the most interesting result of the entire project. The fact that a program I created was able to discover a new strategy that can improve my own game is pretty amazing. 

## Performance Relative to ISMCTS

In addition to playing the network myself, I wrote another program (https://github.com/mtp61/gof-bot-eval) than enables two agents, in this case my PPO and ISMCTS (https://github.com/mtp61/gof_ISMCTS) projects, to play each other. ISMCTS came out on top by a statistically significant margin (p = .0223, 160 effective games played, standard reward function and t-test for difference of means). These games were played with two ISMCTS agents and two PPO agents, in alternating order. 
