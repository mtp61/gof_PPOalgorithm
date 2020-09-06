import socketio
import copy
import json
import tensorflow as tf
import joblib

from network import NN_INPUT_SIZE, ACTIONS_SIZE
from ppoNetwork import PPONetwork


# constants
PARAMS_PATH = "../modelParameters/"
PARAMS_NAME = "modelParameters0.pkl"

USERNAME_DEFAULT = "ppo_bot"
GAME_NAME_DEFAULT = "test"

URL = "http://localhost:3331/"


class Client:
    def main(self):
        self.username = USERNAME_DEFAULT
        self.game_name = GAME_NAME_DEFAULT

        # connect to the server
        self.sio = socketio.Client()
        self.sio.connect(URL + self.game_name)

        # connect to game and ready up
        self.sio.emit('game_connection', (self.game_name, self.username))
        self.sendMessage("!ready")

        # make the network
        sess = tf.Session()
        self.network = PPONetwork(sess, NN_INPUT_SIZE, ACTIONS_SIZE, self.username)
        tf.global_variables_initializer().run(session=sess)
        params = joblib.load(PARAMS_PATH + PARAMS_NAME)
        self.network.loadParams(params)

        # setup variables
        self.old_game_state = None

        # process new game states
        @self.sio.on('game_state')
        def onGameState(game_state):
            # parse messages
            for message in game_state['messages']:
                u = message['username']
                m = message['message']

                if u == "Server":  # server message
                    if len(m) >= 13 and m[:13] == "Game starting":  # check for starting new game
                        print('Game starting')
                        self.old_game_state = None

            # if game active
            if game_state['active']:
                # if new game state
                if json.dumps(game_state) != json.dumps(self.old_game_state):
                    # if new cards
                    if self.old_game_state == None or json.dumps(game_state['current_hand']) != json.dumps(self.old_game_state['current_hand']):
                        pass

                    # update old game state
                    self.old_game_state = copy.deepcopy(game_state)

                # check if we have an action todo add timer to not double respond
                if game_state['to_play'] == self.username:
                    # make the nn input
                    #hand = game_state['player_cards'][self.username]
                    
                    # get the nn output

                    # send message to server

                    pass

                    

        
                        
    

    
    
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
