import random
import numpy as np
import math

from cards import CARDS, CARDS_UNIQUE
import gameLogic
import enumerateOptions
import network


class GoFGame():
    def __init__(self):
        self.reset()

    
    def reset(self):
        """
        resets game state
        """

        # get shuffeded cards
        deck = CARDS[:]  # make a copy
        random.shuffle(deck)

        # set up the game state
        self.current_hand = []
        self.player_cards = {}
        for i in range(1,5):  # deal and sort cards
            self.player_cards[i] = deck[16 * (i - 1) : 16 * i]
            self.player_cards[i].sort()
        self.num_passes = 0
        self.player_to_act = 1
        
        # set up action vars
        self.initializeActions()

        # info vars
        self.num_turns = 0

        # vars for making the nn inputs
        self.cards_played = {}
        for card in CARDS_UNIQUE:
            self.cards_played[card] = 0


    def convertAvailableActions(self, availAcs):
        """
        convert from (1,0,0,1,1...) to (0, -math.inf, -math.inf, 0,0...) etc
        """
        
        availAcs[np.nonzero(availAcs==0)] = -math.inf
        availAcs[np.nonzero(availAcs==1)] = 0
        return availAcs


    def getCurrentState(self):
        """
        returns players_go, current_state, currently_available_actions
        """
        
        return self.player_to_act, self.fillNNInput(), self.convertAvailableActions(self.availableActions())


    def getGameState(self):
        """
        human readable (non nn input) version of getCurrentState()
        """

        return self.player_to_act, self.player_cards[self.player_to_act], self.availableActions()


    def step(self, action):
        """
        returns reward, done, info
        """
        
        # update the game
        # remove cards from players hand
        hand = []
        for card_index in enumerateOptions.card_lookup_all[action]:
            hand.append(self.player_cards[self.player_to_act][card_index])
            self.player_cards[self.player_to_act][card_index] = 0

        # update cards played
        for card in hand:
            self.cards_played[card] += 1
            
        # update current hand
        if action != 0:
            self.current_hand = hand
            self.num_passes = 0
        else:
            if self.num_passes == 2 or len(self.current_hand) == 0:
                self.num_passes = 0
                self.current_hand = []
            else:
                self.num_passes += 1

        # update player to act
        self.player_to_act = self.nextPlayer(self.player_to_act)
        self.num_turns += 1

        # check if game over
        if not self.gameOver():
            reward = 0
            done = False
            info = None
        else:
            reward = self.getReward()
            done = True
            info = {
                'num_turns': self.num_turns
            }

            self.reset()

        #print(f"{ self.lastPlayer(self.player_to_act) } played { hand }, score { gameLogic.getScore(hand) }")

        return reward, done, info


    def availableActions(self):
        """
        returns an array of the available options for the current player
        """

        self.updateActions()
        
        actions = []
        for _ in range(sum(enumerateOptions.num_actions)):
            actions.append(0)

        # get number of cards for next player
        num_c = 0
        for card in self.player_cards[self.nextPlayer(self.player_to_act)]:
            if card != 0:
                num_c != 1
        
        # check if we need to play the highest single
        current_hand_len = len(self.current_hand)
        if num_c == 1:
			# get highest single			
            for c, card in enumerate(self.player_cards[self.player_to_act][::-1]):
                if card != 0:
                    highest_single = card
                    highest_single_index = 15 - c
                    break
            
            if current_hand_len == 1:
                if highest_single > self.current_hand[0]:
                    # can only play highest single and gangs no passing
                    actions[highest_single_index + 1] = 1
                    possible_play_cards = [4]
                else:
                    # can only pass or gang
                    possible_play_cards = [0, 4]
            elif current_hand_len == 0:
                # can only play highest single if playing a single
                actions[highest_single_index + 1] = 1
                possible_play_cards = [0, 2, 3, 4, 5]
            else:
                possible_play_cards = [0, 4, current_hand_len]
        else:
            if current_hand_len == 0:
                possible_play_cards = [0, 1, 2, 3, 4, 5]
            elif current_hand_len == 4:
                possible_play_cards = [0, 4]
            else:
                possible_play_cards = [0, 4, current_hand_len]
        
        # go thru actions and make sure score is high enough
        current_hand_score = gameLogic.getScore(self.current_hand)
        for num_cards in possible_play_cards:
            if num_cards == 0:
                # add passing to actions
                actions[0] = 1
            else:
                offset = sum(enumerateOptions.num_actions[:num_cards])
                for i, val in enumerate(self.player_actions[self.player_to_act][offset:offset + enumerateOptions.num_actions[num_cards]]):
                    if val:
                        # see if the score is high enough
                        hand = []
                        for card_index in enumerateOptions.card_lookup[num_cards][i]:
                            hand.append(self.player_cards[self.player_to_act][card_index])
                        if gameLogic.getScore(hand) > current_hand_score:
                            actions[offset + i] = 1
        
        '''
        c = 0
        for a in actions:
            if a:
                c += 1
        print(f"  { c } possible actions")
        '''

        return actions     


    def updateActions(self):
        """
        update the actions for the current player
        """

        for i, val in enumerate(self.player_actions[self.player_to_act]):
            if val:
                hand_indices = enumerateOptions.card_lookup_all[i]
                for card_index in hand_indices:
                    if self.player_cards[self.player_to_act][card_index] == 0:
                        self.player_actions[self.player_to_act][i] = 0
                        break


    def fillNNInput(self):
        """
        returns the input array for the network for the current player
        """

        # create input array
        nn_input = np.zeros(network.NN_INPUT_SIZE)

        # fill card in hand
        for n, card in enumerate(self.player_cards[self.player_to_act]):
            card_value = gameLogic.getValue(card)
            card_color = gameLogic.getColor(card)
            
            offset = n * network.EACH_CARD_SIZE
            nn_input[offset + card_value] = 1
            if card_value != 0:
                nn_input[offset + 12 + card_color] = 1

        # fill for each opponent
        current_player = self.player_to_act
        for n in range(3):
            current_player = self.nextPlayer(current_player)
            num_cards = 0
            for card in self.player_cards[current_player]:
                if card != 0:
                    num_cards += 1
            
            offset = network.CARD_SIZE + n * network.EACH_PLAYER_SIZE
            nn_input[offset + num_cards - 1] = 1

        # fill previous hand info
        # control/num passes
        offset = network.CARD_SIZE + network.PLAYER_SIZE
        ch_len = len(self.current_hand)
        if ch_len == 0:
            nn_input[offset] = 1
        if self.num_passes == 1:
            nn_input[offset + 1] = 1
        elif self.num_passes == 2:
            nn_input[offset + 2] = 1
        elif self.num_passes == 3:
            nn_input[offset + 3] = 1
        if ch_len != 0:
            offset = network.CARD_SIZE + network.PLAYER_SIZE + 4
            
            # highest card val
            high_card_val = gameLogic.getValue(self.current_hand[-1])
            # highest card color
            high_card_color = gameLogic.getColor(self.current_hand[-1])
            
            nn_input[offset + high_card_val - 1] = 1
            nn_input[offset + 11 + high_card_color] = 1

            offset += 11 + 4

            if ch_len < 5:  # not 5 card
                hand_type = ch_len - 1
            else:  # 5 card hand
                is_straight = True
                start_value = gameLogic.getValue(self.current_hand[0])
                for n, card in enumerate(self.current_hand[1:]):
                    if gameLogic.getValue(card) != start_value + n + 1:
                        is_straight = False
                        break
                if is_straight and gameLogic.getValue(self.current_hand[-1]) == 11:
                    is_straight = False

                is_flush = True
                hand_color = gameLogic.getColor(self.current_hand[-1])
                for card in self.current_hand[:-1]:
                    if gameLogic.getColor(card) != handColor:
                        is_flush = False
                        break
                if is_flush and gameLogic.getValue(self.current_hand[-1]) == 11:
                    is_flush = False
                
                if is_straight and is_flush:  # straight flush
                    hand_type = 7
                elif is_straight:  # straight
                    hand_type = 4
                elif is_flush:  # flush
                    hand_type = 5
                else:  # full house
                    hand_type = 6

            nn_input[offset + hand_type] = 1

        # fill cards played
        # 10s
        for color in [0, 1, 2]:
            offset = network.CARD_SIZE + network.PLAYER_SIZE + network.CURRENT_HAND_SIZE + 2 * color
            card = 100 + color
            if self.cards_played[card] >= 1:
                nn_input[offset] = 1
                if self.cards_played[card] == 2:
                    nn_input[offset + 1] = 1
        # 11s
        for color in [0, 1, 2]:
            offset = network.CARD_SIZE + network.PLAYER_SIZE + network.CURRENT_HAND_SIZE + 6 + color
            card = 110 + color
            if self.cards_played[card] == 1:
                nn_input[offset] = 1

        return nn_input


    def gameOver(self):
        """
        returns a boolean value based on whether or not the game is over
        """

        # probably don't need to look at all players, just the last player

        for i in range(1, 5):
            has_cards = False
            for card in self.player_cards[i]:
                if card != 0:
                    has_cards = True
                    break
            if not has_cards:
                return True
        return False


    def initializeActions(self):
        """
        initializes the actions for each player
        """

        self.player_actions = {}
        for i in range(1, 5):
            self.player_actions[i] = enumerateOptions.legalHands(self.player_cards[i])
    

    def getReward(self):
        reward = {}
        for i in range(1, 5):
            c = 0
            for card in self.player_cards[i]:
                if card != 0:
                    c += 1
            reward[i] = c
        return reward


    def nextPlayer(self, p):
        return p % 4 + 1


    def lastPlayer(self, p):
        return (p - 2) % 4 + 1


if __name__ == "__main__":  # run tests
    gofGame = GoFGame()
    pa = gofGame.player_actions[1]
    pc = gofGame.player_cards[1]
    print(pc)

    for c, v in enumerate(pa):
        if v:
            print(enumerateOptions.makeHand(pc, enumerateOptions.card_lookup_all[c]))
