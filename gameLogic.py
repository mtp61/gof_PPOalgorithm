
def isLegalHand(hand):
    """
    hand must be sorted

    returns 1 if hand is legal, 0 otherwise
    """
    
    # make sure there are no null cards in hand
    for card in hand:
        if card == 0:
            return False

    if len(hand) == 1:
        return True
    elif len(hand) == 2:
        if getValue(hand[0]) == getValue(hand[1]) and hand[1] != 112:
            return True
    elif len(hand) == 3:
        if getValue(hand[0]) == getValue(hand[1]) == getValue(hand[2]) and hand[2] != 112:
            return True
    elif len(hand) == 4:
        if getValue(hand[0]) == getValue(hand[1]) == getValue(hand[2]) == getValue(hand[3]):
            return True
    elif len(hand) == 5:
        # check straight
        is_straight = True
        for i in range(1, 5):
            if getValue(hand[i]) != getValue(hand[0]) + i:
                is_straight = False
                break
        if is_straight and getValue(hand[4]) != 11:
            return True

        # check flush
        hand_color = getColor(hand[4])
        is_flush = True
        for card in hand[:-1]:
            if getColor(card) != hand_color:
                is_flush = False
                break
        if is_flush and getValue(hand[4]) != 11:
            return True

        # check full house
        if getValue(hand[0]) == getValue(hand[1]) and getValue(hand[3]) == getValue(hand[4]) \
        and (getValue(hand[1]) == getValue(hand[2]) or getValue(hand[2]) == getValue(hand[3])) \
        and hand[4] != 112:
            return True

    return False


def getScore(hand):
    """
    returns the hand score
    """

    hand_size = len(hand)
    if hand_size == 0:
        return 0
    elif hand_size == 1:
        return hand[0]
    elif hand_size == 2:
        return 100 * getValue(hand[1]) + 10 * getColor(hand[1]) + getColor(hand[0])
    elif hand_size == 3:
        return 1000 * getValue(hand[2]) + 100 * getColor(hand[2]) + 10 * getColor(hand[1]) + getColor(hand[0])
    elif hand_size == 4:
        return getValue(hand[0]) + 100000000
    elif hand_size == 5:
        # straight
        is_straight = True
        for i in range(1, 5):
            if getValue(hand[i]) != getValue(hand[0]) + i:
                is_straight = False
                break
        
        # flush
        hand_color = getColor(hand[4])
        is_flush = True
        for card in hand[:4]:
            if getColor(card) != hand_color:
                is_flush = False
                break
        
        if is_straight and is_flush:
            return hand[4] + 90000000
        elif is_straight:
            score = 100000 * getValue(hand[4])
            ten_power = 10000
            for card in hand[::-1]:
                score += ten_power * getColor(card)
                ten_power /= 10
            return score
        elif is_flush:
            score = 100000 * getColor(hand[4]) + 2000000
            ten_power = 10000
            for card in hand[::-1]:
                score += ten_power * getValue(card)
                ten_power /= 10
            return score

        # must be a full house
        if getValue(hand[1]) == getValue(hand[2]):  # 3 is first 3
            score = 1000000 * getValue(hand[0]) + 100000 * getValue(hand[4]) + 3000000
            ten_power = 10000
            for card in hand[2::-1]:
                score += ten_power * getColor(card)
                ten_power /= 10
            for card in hand[4:2:-1]:
                score += ten_power * getColor(card)
                ten_power /= 10
        else:  # 3 is last 3
            score = 1000000 * getValue(hand[4]) + 100000 * getValue(hand[0]) + 3000000
            ten_power = 10000
            for card in hand[::-1]:
                score += ten_power * getColor(card)
                ten_power /= 10
        return score

    return -1


def getValue(card):
    return card // 10


def getColor(card):
    return card % 10
