import numpy as np
import random
from typing import Dict, List, Union

def get_index_array(obj):
    """Return the index, array pair corresponding to <obj> which
    is either an index or an array."""

    if isinstance(obj, (int, float)): # obj is an index
        return obj, get_array(obj)

    # obj is an array
    return get_index(obj), obj

def get_array(n: int):
    """Get the numpy array corresponding to index <n>."""

    arr = np.zeros((3, 3), dtype=int)

    for i in range(8, -1, -1):
        col_index = i % 3
        row_index = (i - col_index) // 3
        arr[row_index, col_index] = n // 3**i - 1
        n = n - 3**i *(n // 3**i)

    return arr


def get_index(arr):
    """Get the index corresponding to the numpy array <arr>."""
    n = 0

    for i in range(9):
        col_index = i % 3
        row_index = (i - col_index) // 3
        n += (arr[row_index, col_index] + 1) * 3**i

    return n


def get_result(arr):
    """Return 1 for winning, -1 for losing, 0 for not finished, 2 for a draw."""
    # Rows
    for i in range(3):
        s = np.sum(arr[i,:])
        if s == 3:
            return 1
        if s == -3:
            return -1

    # Columns
    for i in range(3):
        s = np.sum(arr[:,i])
        if s == 3:
            return 1
        if s == -3:
            return -1

    # Diagonals
    s = arr[0,0] + arr[1,1] + arr[2,2]
    if s == 3:
        return 1
    if s == -3:
        return -1

    s = arr[0,2] + arr[1,1] + arr[2,0]
    if s == 3:
        return 1
    if s == -3:
        return -1

    # Check if finished or a draw
    if 0 in arr:
        return 0

    return 2


def get_prob_winning(res):
    """Convert the result of get_result to a probability of winning."""
    if res == 1:
        return 1
    if res == -1:
        return 0
    if res == 2:
        return 0
    return 0.5


class Game:

    def __init__(self, player0, player1):
        self.board = np.zeros((3,3), dtype = int)
        self.players = [player0, player1]
        self.turn = 0

    def take_turn(self):
        index, self.board, b = self.players[self.turn].make_move(self.board)
        self.turn = 1 - self.turn
        return index, b, get_prob_winning(get_result(self.board))

    def play_game(self, verbose = False):
        player_0_states = []
        exploratory_states = []
        if verbose:
            print(self.board)

        res = None

        while res != 0 and res != 1:
            index, b, res, = self.take_turn()
            if verbose:
                print(self.board, index, b)
            if self.turn == 1:
                player_0_states.append(get_index(self.board))
            if b:
                exploratory_states.append(get_index(self.board))

        return res, player_0_states, exploratory_states


class RandomPlayer():
    def __init__(self, val = -1):
        self.val = val

    def make_move(self,arr):
        """Make a move and return the resultant board."""
        valid_r = []
        valid_c = []
        for r in range(3):
            for c in range(3):
                if arr[r,c] == 0:
                    valid_r.append(r)
                    valid_c.append(c)

        rand = random.randint(0, len(valid_r) - 1)
        r = valid_r[rand]
        c = valid_c[rand]

        cpy = arr.copy()
        cpy[r,c] = self.val
        i, arr = get_index_array(cpy)
        return i, arr, None

class SpecialPlayer():
    def make_move(self,arr):
        """Make a move and return the resultant board."""
        for r in range(3):
            for c in range(3):
                if arr[r,c] == 0:
                    cpy = arr.copy()
                    cpy[r,c] = -1
                    i, arr = get_index_array(cpy)
                    return i, arr, None

class LearnerPlayer:

    def __init__(self):
        self.value_function = {}

    def make_move(self, arr, prob = 0.05):
        """Make a move and return the resultant board."""
        r = random.random()
        if r < prob:
            player = RandomPlayer(1)
            i, arr, b = player.make_move(arr)
            return i, arr, True

        best_r = []
        best_c = []
        best_prob = 0
        for r in range(3):
            for c in range(3):
                if arr[r,c] == 0:
                    cpy = arr.copy()
                    cpy[r,c] = 1
                    ind = get_index(cpy)
                    if ind not in self.value_function:
                        self.value_function[ind] = get_prob_winning(get_result(cpy))
                    prob = self.value_function[ind]
                    if prob == best_prob:
                        best_r.append(r)
                        best_c.append(c)
                    if prob > best_prob:
                        best_r = [r]
                        best_c = [c]
                        best_prob = prob

        rand = random.randint(0, len(best_r) - 1)
        r = best_r[rand]
        c = best_c[rand]

        cpy = arr.copy()
        cpy[r,c] = 1

        i, arr = get_index_array(cpy)
        return i, arr, False

    def update(self, lst, exploratory_states, alpha = 0.1):
        #print(lst)
        #print(exploratory_states)
        #print(self.value_function)
        lst = lst[::-1]
        for i in range(1, len(lst)):
            if lst[i - 1] not in self.value_function:
                self.value_function[lst[i - 1]] = get_prob_winning(get_result(get_array(lst[i - 1])))
            if lst[i] not in self.value_function:
                self.value_function[lst[i]] = get_prob_winning(get_result(get_array(lst[i])))
            if lst[i - 1] not in exploratory_states:
                self.value_function[lst[i]] += alpha *(self.value_function[lst[i - 1]] - self.value_function[lst[i]])
        #print(self.value_function)
    


if __name__ == "__main__":
    player0 = LearnerPlayer()
    n = 50000
    s = 0
    alpha = 0.1
    player1 = RandomPlayer()
    for i in range(n):
        if i % 1000:
            alpha * 0.9

        g = Game(player0, player1)
        r, l, e = g.play_game()
        s += r
        player0.update(l, e, alpha)

    print(s/n)

    s = 0
    player1 = SpecialPlayer()
    alpha = 0.1
    for i in range(n):
        if i % 1000:
            alpha * 0.9

        g = Game(player0, player1)
        r, l, e = g.play_game()
        s += r
        #player0.update(l, e, alpha)

    print(s/n)
