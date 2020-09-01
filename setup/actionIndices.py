import numpy as np
import pickle


def writeI(num, i, cardLookup, indexLookup):
    counter = 0
    for c in i:
        cardLookup[num].append(c)
        indexLookup[num][c] = counter
        counter += 1


cardLookup = {}
indexLookup = {}
for i in range(1, 6):
    cardLookup[i] = []
    indexLookup[i] = {}

# 1s
i = []
for c1 in range(0, 16):
    i.append((c1,))
writeI(1, i, cardLookup, indexLookup)
print(f"1 - { len(i) }")

# 2s
i = []
for c1 in range(0, 16):
    for c2 in range(c1 + 1, c1 + 6):
        if c2 > 15:
            continue

        c = (c1, c2)
        if c not in i:
            i.append(c)
i.append((0, 6))
writeI(2, i, cardLookup, indexLookup)
print(f"2 - { len(i) }")

# 3s
i = []
for c1 in range(0, 16):
    for c2 in range(c1 + 1, c1 + 6):
        for c3 in range(c2 + 1, c1 + 6):
            if c3 > 15:
                continue

            c = (c1, c2, c3)
            if c not in i:
                i.append(c)
i.append((0, 1, 6))
i.append((0, 2, 6))
i.append((0, 3, 6))
i.append((0, 4, 6))
i.append((0, 5, 6))
writeI(3, i, cardLookup, indexLookup)
print(f"3 - { len(i) }")

# 4s
i = []
for c1 in range(0, 16):
    for c2 in range(c1 + 1, c1 + 6):
        for c3 in range(c2 + 1, c1 + 6):
            for c4 in range(c3 + 1, c1 + 6):
                if c4 > 15:
                    continue

                c = (c1, c2, c3, c4)
                if c not in i:
                    i.append(c)
c1 = 0
c4 = 6
for c2 in range(1, 5):
    for c3 in range(c2 + 1, 6):
        c = (c1, c2, c3, c4)
        if c not in i:
            i.append(c)
writeI(4, i, cardLookup, indexLookup)
print(f"4 - { len(i) }")

# 5s
i = []
for c1 in range(0, 16):
    for c2 in range(c1 + 1, 16):
        for c3 in range(c2 + 1, 16):
            for c4 in range(c3 + 1, 16):
                for c5 in range(c4 + 1, 16):
                    c = (c1, c2, c3, c4, c5)
                    if c not in i:
                        i.append(c)
writeI(5, i, cardLookup, indexLookup)
print(f"5 - { len(i) }")

# save
with open('actions.pkl', 'wb') as file:
    pickle.dump((
        cardLookup, indexLookup
    ), file)
