import pickle

import gameLogic


with open('actions.pkl','rb') as file:
    card_lookup, index_lookup = pickle.load(file)

num_actions = []  # num actions for a certain number of cards played
num_actions.append(1)
for i in range(1, 6):
    num_actions.append(len(card_lookup[i]))

card_lookup_all = [()]
index_lookup_all = {(): 0}
for i in card_lookup.keys():
    for c in card_lookup[i]:
        card_lookup_all.append(c)
counter = 1
for i in index_lookup.keys():
    for c in index_lookup[i].keys():
        index_lookup_all[c] = counter
        counter += 1


def legalHands(player_cards):
    """
    returns a list of binary values signifying whether or not a given hand is legal
    """
    
    assert len(player_cards) == 16

    hand_list = []
    for num_cards in range(6):
        if num_cards == 0:
            hand_list.append(1)
            continue

        for i in range(num_actions[num_cards]):
            action_indices = card_lookup[num_cards][i]

            if gameLogic.isLegalHand(makeHand(player_cards, action_indices)):
                hand_list.append(1)
            else:
                hand_list.append(0)

    return hand_list


def makeHand(player_cards, hand_indices):
    """
    returns a list of the cards in the hand
    """

    hand = []
    for i in hand_indices:
        hand.append(player_cards[i])
    return hand


def numCards(index):
    """
    returns the number of cards from an index
    """

    cum_sum = 0
    for n, a in enumerate(num_actions):
        cum_sum += a
        if index < cum_sum:
            return n

    return None
