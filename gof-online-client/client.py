import socketio
import copy
import json
import tensorflow as tf
import joblib
import numpy as np

import sys
sys.path.append('..')

from network import NN_INPUT_SIZE, ACTIONS_SIZE
from ppoNetwork import PPONetwork, PPOModel
from GoFGame import GoFGame
from cards import CARDS_UNIQUE
import enumerateOptions


# constants
PARAMS_PATH = "../modelParameters/"
PARAMS_NAME = "modelParameters0"

USERNAME_DEFAULT = "ppo_bot"
GAME_NAME_DEFAULT = "test"

URL = "http://localhost:3331/"

PRINT_MESSAGES = False

entCoef = 0.01
valCoef = 0.5
maxGradNorm = 0.5


class Client:
    def main(self):        
        # args
        self.username = USERNAME_DEFAULT
        self.game_name = GAME_NAME_DEFAULT

        # connect to the server
        self.sio = socketio.Client()
        self.sio.connect(URL + self.game_name)

        # connect to game and ready up
        self.sio.emit('game_connection', (self.game_name, self.username))
        self.sendMessage("!ready")

        # make the network and model
        sess = tf.Session()
        self.network = PPONetwork(sess, NN_INPUT_SIZE, ACTIONS_SIZE, self.username)
        self.model = PPOModel(sess, self.network, NN_INPUT_SIZE, ACTIONS_SIZE, entCoef, valCoef, maxGradNorm)
        tf.global_variables_initializer().run(session=sess)
        params = joblib.load(PARAMS_PATH + PARAMS_NAME)
        self.network.loadParams(params)
        print(f"\nNetwork { PARAMS_NAME } loaded")

        # setup variables
        self.old_game_state = None

        # process new game states
        @self.sio.on('game_state')
        def onGameState(game_state):
            # parse messages
            for message in game_state['messages']:
                u = message['username']
                m = message['message']

                if PRINT_MESSAGES:
                    print(message)

                if u == "Server":  # server message
                    if len(m) >= 13 and m[:13] == "Game starting":  # check for starting new game
                        self.old_game_state = None
                        self.original_hand = None
                        print(f"Game starting, hand: { self.original_hand }")

            # if game active
            if game_state['active']:
                # if new game state
                if json.dumps(game_state) != json.dumps(self.old_game_state):
                    # if we dont have original hand
                    if self.original_hand == None:
                        self.original_hand = []
                        self.original_card_count = {}
                        for card in game_state['player_cards'][self.username]:
                            card_num = self.cardToNum(card)
                            if card_num not in self.original_card_count.keys():
                                self.original_card_count[card_num] = 0
                            self.original_card_count[card_num] += 1
                            self.original_hand.append(card_num)
                        self.cards_played = {}
                        for card in CARDS_UNIQUE:
                            self.cards_played[card] = 0
                    
                    # if new cards
                    if self.old_game_state == None or json.dumps(game_state['current_hand']) != json.dumps(self.old_game_state['current_hand']):
                        # update cards played
                        for card in game_state['current_hand']:
                            self.cards_played[self.cardToNum(card)] += 1

                    # update old game state
                    self.old_game_state = copy.deepcopy(game_state)

                # check if we have an action todo add timer to not double respond
                if game_state['to_play'] == self.username:
                    # make the nn input
                    # make the hand with the correct representation
                    card_count = {}
                    for card_num in self.original_hand:
                        if card_num not in card_count.keys():
                            card_count[card_num] = 0
                    for card in game_state['player_cards'][self.username]:
                        card_count[self.cardToNum(card)] += 1
                    hand = self.original_hand[:]
                    for card in self.original_card_count.keys():
                        if card in card_count.keys():
                            num_missing = self.original_card_count[card] - card_count[card]
                        else:
                            num_missing = self.original_card_count[card]
                        for _ in range(num_missing):
                            hand[hand.index(card)] = 0
                    
                    # make the gofGame that will give us the nn inputs
                    gofGame = GoFGame()
                    gofGame.player_to_act = 1
                    gofGame.player_cards[1] = hand
                    gofGame.cards_played = self.cards_played

                    current_hand = []
                    for card in game_state['current_hand']:
                        current_hand.append(self.cardToNum(card))
                    gofGame.current_hand = current_hand
                    
                    # give the other players the correct number of cards
                    current_player_index = game_state['players'].index(self.username)
                    for p in range(3):
                        current_player_index = (current_player_index + 1) % 4
                        name = game_state['players'][current_player_index]
                        num_cards = game_state['num_cards'][name]
                        player_cards = [10, 11, 12, 13, 20, 21, 22, 30, 31, 32, 40, 41, 42, 50, 51, 52][:num_cards]
                        for _ in range(16 - num_cards):
                            player_cards.append(0)
                        assert len(player_cards) == 16
                        gofGame.player_cards[p + 2] = player_cards

                    gofGame.initializeActions()
                    go, state, actions = gofGame.getCurrentState()

                    # print info
                    num_actions = 0
                    for val in actions[0]:
                        if val == 0:
                            num_actions += 1
                    print(f"bot hand: { str(hand)[1:-1] }, { num_actions } possible actions")
                    print_tuples = []
                    for i, val in enumerate(actions[0]):
                        if val == 0:
                            card_indices = enumerateOptions.card_lookup_all[i]
                            cards = []
                            for index in card_indices:
                                cards.append(hand[index])
                            print_tuples.append((str(cards)[1:-1], round(np.exp(-self.model.neglogp(state, actions, np.array([i])))[0], 4)))
                    print_tuples.sort(key=lambda t:-t[1])  # sort print tuples by probability
                    for t in print_tuples:  # print
                        print(f"  { t[0] } -- " + str(t[1]))
                    
                    # get the nn output
                    a, v, nlp = self.network.step(state, actions)
                    action = []
                    for i in enumerateOptions.card_lookup_all[a[0]]:
                        action.append(hand[i])
                    print(f"chose action { a[0] }: { str(action)[1:-1] }, p=" + str(round(np.exp(-nlp)[0], 4)))
                    
                    
                    #print(round(np.exp(-nlp)[0], 4))
                    #print(np.round(np.exp(-nlp)[0], 4))
                    
                    
                    # send message to server
                    action_message = "!play "
                    for card in action:
                        action_message += self.numToCardStr(card) + " "
                    action_message = action_message[:-1]
                    self.sendMessage(action_message)
                    print()

        
    def numToCardStr(self, num):
        card_str = str(num // 10)
        if num % 10 == 0:
            card_str += 'g'
        elif num % 10 == 1:
            card_str += 'y'
        elif num % 10 == 2:
            card_str += 'r'
        elif num % 10 == 3:
            card_str += 'm'
        return card_str

    
    def cardToNum(self, card):  # converts a card json object to the single number used by the engine
        card_num = 10 * int(card['value'])
        if card['color'] == 'y':
            card_num += 1
        elif card['color'] == 'r':
            card_num += 2
        elif card['color'] == 'm':
            card_num += 3
        return card_num


    def sendMessage(self, message):
        self.sio.emit('chat-message', (self.game_name, self.username, message))
    

if __name__ == '__main__':
    # instantiate the client class
    client = Client()

    # run the main method
    client.main()
