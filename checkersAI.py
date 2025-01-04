import argparse
import copy
import sys
import time

cache = {} # you can use this to implement state caching

directions = [(-1,-1),(-1,1), (1,-1),(1,1)]

class State:
    # This class is used to represent a state.
    # board : a list of lists that represents the 8*8 board
    def __init__(self, board, count = 0, turn = 'r'):

        self.board = board
        self.pieces = []
        self.width = 8
        self.height = 8
        self.move_count = count
        self.turn = turn
        self.load_pieces()

    def load_pieces(self):
        for i,line in enumerate(self.board):
            for j,piece in enumerate(line):
                if piece in ['b','B','r','R']:
                    self.pieces.append((piece,(i,j)))

    def print_pieces(self):
        print(self.pieces)

    def display(self):
        for i in self.board:
            for j in i:
                print(j, end="")
            print("")
        print("")

    
    def evaluate(self,depth):
        score = 0
        for i in self.pieces:
            piece = i[0]
            if piece == 'r'  : score += 1
            elif piece == 'R': score +=2
            elif piece == 'b': score -=1
            elif piece == 'B': score -=2
        score *= 1000
        score -= self.move_count
        return score
    def __hash__(self):
        prime = 31
        result = 1
        for row in self.board:
            for piece in row:
                result = prime * result + hash(piece)
        return hash((result,self.turn))
    def black_wins(self):
        r = 0 
        b = 0
        for i in self.pieces:
            piece = i[0]
            if piece == 'r' or piece == 'R' : r+=1
            elif piece == 'b' or piece == 'B' : b+=1
        print(r,b)
        return r == 0
    # def board_to_string():
    #     string = ""
    #     for i in len(state.board):
    #         for j in len(state.board[i]):
    #             string += j
def get_opp_char(player):
    if player in ['b', 'B']:
        return ['r', 'R']
    else:
        return ['b', 'B']

def get_next_turn(curr_turn):
    if curr_turn == 'r':
        return 'b'
    else:
        return 'r'

def read_from_file(filename):

    f = open(filename)
    lines = f.readlines()
    board = [[str(x) for x in l.rstrip()] for l in lines]
    f.close()

    return board

def avaliable_moves(state,turn):
    #list all avaliable moves for the current player.
    available = []
    jump = False
    for i, piece_tup in enumerate(state.pieces):
        pos = piece_tup[1]
        piece = piece_tup[0]

        
        pos_direction = []

        if (piece in ['r','R'] and turn=='r') or (piece in ['b','B'] and turn == 'b'):
            
            if piece == 'r':
        
                pos_direction = directions[0:2]
            elif piece == 'b':
                
                pos_direction = directions[2:4]
            elif piece in ['R','B']:
                pos_direction = directions
            lst = available_moves_helper(state,piece, pos[0],pos[1],pos_direction, True,(0,0),jump)
            if lst[1] == True:
                
                jump = True
            available.extend(lst[0])
            
    if jump:
        available = [i for i in available if not isinstance(i[1], tuple)]
        
    return available

def available_moves_helper(state, piece, y,x,directions, first,last,alr_jumped):
    
    available = []
    jump = False

    for j in directions:
        new_board = [row[:] for row in state.board]
            
        if not j[0] == -last[0] or not j[1] == -last[1]:
            curr_path = []
            new_pos = (y+j[0],x+j[1])
            #print(new_pos)
            #print('found')
            #print(state.board[new_pos[0]][new_pos[1]])
            if 0 <= new_pos[0] and new_pos[0] < state.width and 0 <= new_pos[1] and new_pos[1] < state.width: 

                #single moves
                if (state.board[new_pos[0]][new_pos[1]] == '.' and first and not alr_jumped):
                    if piece.islower() and can_promote(piece,new_pos[0],new_pos[1]):
                        new_board[new_pos[0]][new_pos[1]] = piece.upper()                    
                    else:
                        new_board[new_pos[0]][new_pos[1]] = piece
                    new_board[y][x] = '.'
                    new_state = State(new_board,state.move_count+1,piece.lower())
                    available.append((new_state,new_pos))

                #jump moves
                if (state.board[new_pos[0]][new_pos[1]] in get_opp_char(piece)):
                    
                    jump_pos = (new_pos[0]+j[0],new_pos[1]+j[1])
                    if 0 <= jump_pos[0] and jump_pos[0] < state.width and 0 <= jump_pos[1] and jump_pos[1] < state.width: 
                        if(state.board[jump_pos[0]][jump_pos[1]] == '.'):
                        
                            # #recursion
                            
                            new_board[y][x] = '.'
                            new_board[new_pos[0]][new_pos[1]] = "."
                            if piece.islower() and can_promote(piece,jump_pos[0],jump_pos[1]):
                                new_board[jump_pos[0]][jump_pos[1]] = piece.upper()
                            else:
                                new_board[jump_pos[0]][jump_pos[1]] = piece
                            new_state = State(new_board,state.move_count+1,piece.lower())
                            

                            last = j
                            jump_sequence = available_moves_helper(new_state, piece, jump_pos[0], jump_pos[1], directions, False,last,alr_jumped)[0]
                            curr_path.append(jump_pos)
                            #print(curr_path)
                            jump = True
                            # If there are more jumps, add the whole sequence, otherwise append the single jump
                            if jump_sequence:
                                for seq in jump_sequence:
                                    
                                    available.append((seq[0],curr_path + seq[1]))
                            else:
                                
                                available.append((new_state,curr_path))
        
                
    return (available,jump)
    #if it is  a jump move, then recursion with new position

def can_promote(piece,y,x):
    if piece == 'r':
        if y == 0:
            return True
    if piece =='b' :
        if y == 7:
            return True
    return False


def minimax(state, depth, max_player, alpha, beta):

    # Generate a unique key for the current game state
    state_key = hash(state)  
    
    # Check if the state has already been evaluated at this depth
    if state_key in cache and cache[state_key]['depth'] >= depth:
        return cache[state_key]['evaluation'], cache[state_key]['best_move']
    


    if  depth == 0 or not avaliable_moves(state,'r') or not avaliable_moves(state,'b'):

        evaluation = state.evaluate(depth)
        
        cache[state_key] = {'evaluation': evaluation, 'best_move': state, 'depth': depth}
        return evaluation, state
    
    if max_player:
        maxEval = float('-inf')
        best_move = None
        
        moves = sorted(avaliable_moves(state, 'r'), key=lambda move: move[0].evaluate(depth), reverse=True)

        for move in moves:
            evaluation = minimax(move[0],depth-1,False,alpha,beta)[0]
            maxEval = max(maxEval,evaluation)
            alpha = max( alpha, maxEval)
            if beta <= alpha:
                break
            if maxEval == evaluation:
                best_move = move
                
        
        cache[state_key] = {'evaluation': maxEval, 'best_move': best_move, 'depth': depth}
        return maxEval, best_move
    else:
        minEval = float('inf')
        best_move = None

        moves = sorted(avaliable_moves(state, 'b'), key=lambda move: move[0].evaluate(depth))

        for move in moves:
            evaluation = minimax(move[0],depth-1,True,alpha,beta)[0]
            minEval = min(minEval,evaluation)
            beta = min( beta, minEval)
            if beta <= alpha:
                break
            if minEval == evaluation:
                best_move = move
                
        # Cache the result before returning
        cache[state_key] = {'evaluation': minEval, 'best_move': best_move, 'depth': depth}
        return minEval, best_move
    return


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputfile",
        type=str,
        required=True,
        help="The input file that contains the puzzles."
    )
    parser.add_argument(
        "--outputfile",
        type=str,
        required=True,
        help="The output file that contains the solution."
    )
    args = parser.parse_args()


    initial_board = read_from_file(args.inputfile)
    state = State(initial_board)
    turn = 'r'
    ctr = 0

    start_time = time.time()
    
    new_board = state
    
    
    #sys.stdout = open(args.outputfile, 'w')
    #state.display()
    state.display()
    while(avaliable_moves(new_board,'r') and avaliable_moves(new_board,'b')):
        maxx = False
        if turn == 'r':
            maxx = True
            moves = avaliable_moves(new_board, turn)
            print("Available Moves:")
            for i in moves:
                print(i[1])
            print("AI Suggests")
            print(minimax(new_board,10,maxx,float("-inf"),float("inf"))[1][1])
            move = int(input())
            while move < 0 or move >= len(moves):
                print("Move Invalid")
                move = int(input("Enter Move:"))
            new_board = moves[int(move)][0]
            #maxx = True

            
        else:
            maxx = False
            value,n = minimax(new_board,10,maxx,float("-inf"),float("inf"))
            new_board = n[0]
        turn = get_next_turn(turn)
        new_board.display()
        #break
    
    
    print(new_board.pieces)
    
    #sys.stdout = sys.__stdout__
    if new_board.black_wins():
        print("BLACK WINS")
    else:
        print("RED WINS")
    end_time = time.time()

    # Calculate and print the elapsed time
    elapsed_time = end_time - start_time
    print(f"Time taken: {elapsed_time:.2f} seconds")

