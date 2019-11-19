import numpy as np
from math import inf as infinity
import itertools
import random
import time

SpelStatus = [[' ',' ',' '],
              [' ',' ',' '],
              [' ',' ',' ']]
spelers = ['X','O']

def SpelZet(state, speler, block_num):
    if state[int((block_num-1)/3)][(block_num-1)%3] is ' ':
        state[int((block_num-1)/3)][(block_num-1)%3] = speler
    else:
        block_num = int(input("De gekozen vak is al bezet, kies een andere vak: "))
        SpelZet(state, speler, block_num)
    
def copy_SpelStatus(state):
    new_state = [[' ',' ',' '],[' ',' ',' '],[' ',' ',' ']]
    for i in range(3):
        for j in range(3):
            new_state[i][j] = state[i][j]
    return new_state
    
def check_huidige_status(SpelStatus):    
    # Controleer horizontale as
    if (SpelStatus[0][0] == SpelStatus[0][1] and SpelStatus[0][1] == SpelStatus[0][2] and SpelStatus[0][0] is not ' '):
        return SpelStatus[0][0], "Klaar"
    if (SpelStatus[1][0] == SpelStatus[1][1] and SpelStatus[1][1] == SpelStatus[1][2] and SpelStatus[1][0] is not ' '):
        return SpelStatus[1][0], "Klaar"
    if (SpelStatus[2][0] == SpelStatus[2][1] and SpelStatus[2][1] == SpelStatus[2][2] and SpelStatus[2][0] is not ' '):
        return SpelStatus[2][0], "Klaar"
    
    # Controleer verticale as
    if (SpelStatus[0][0] == SpelStatus[1][0] and SpelStatus[1][0] == SpelStatus[2][0] and SpelStatus[0][0] is not ' '):
        return SpelStatus[0][0], "Klaar"
    if (SpelStatus[0][1] == SpelStatus[1][1] and SpelStatus[1][1] == SpelStatus[2][1] and SpelStatus[0][1] is not ' '):
        return SpelStatus[0][1], "Klaar"
    if (SpelStatus[0][2] == SpelStatus[1][2] and SpelStatus[1][2] == SpelStatus[2][2] and SpelStatus[0][2] is not ' '):
        return SpelStatus[0][2], "Klaar"
    
    # Controleer diagonale as
    if (SpelStatus[0][0] == SpelStatus[1][1] and SpelStatus[1][1] == SpelStatus[2][2] and SpelStatus[0][0] is not ' '):
        return SpelStatus[1][1], "Klaar"
    if (SpelStatus[2][0] == SpelStatus[1][1] and SpelStatus[1][1] == SpelStatus[0][2] and SpelStatus[2][0] is not ' '):
        return SpelStatus[1][1], "Klaar"
    
    # Controleer of het gelijkspel is
    draw_flag = 0
    for i in range(3):
        for j in range(3):
            if SpelStatus[i][j] is ' ':
                draw_flag = 1
    if draw_flag is 0:
        return None, "Gelijkspel"
    
    return None, "Niet klaar"

def print_board(SpelStatus):
    print('----------------')
    print('| ' + str(SpelStatus[0][0]) + ' || ' + str(SpelStatus[0][1]) + ' || ' + str(SpelStatus[0][2]) + ' |')
    print('----------------')
    print('| ' + str(SpelStatus[1][0]) + ' || ' + str(SpelStatus[1][1]) + ' || ' + str(SpelStatus[1][2]) + ' |')
    print('----------------')
    print('| ' + str(SpelStatus[2][0]) + ' || ' + str(SpelStatus[2][1]) + ' || ' + str(SpelStatus[2][2]) + ' |')
    print('----------------')
    
  
# Initialize status waardes
speler = ['X','O',' ']
states_dict = {}
all_possible_states = [[list(i[0:3]),list(i[3:6]),list(i[6:10])] for i in itertools.product(speler, repeat = 9)]
n_states = len(all_possible_states) # 2 spelers, 9 spaces
n_acties = 9   # 9 spaces
state_values_for_AI_O = np.full((n_states),0.0)
state_values_for_AI_X = np.full((n_states),0.0)
print("n_states = %i \nn_acties = %i"%(n_states, n_acties))

# Status waardes voor AI 'O'
for i in range(n_states):
    states_dict[i] = all_possible_states[i]
    winner, _ = check_huidige_status(states_dict[i])
    if winner == 'O':   # AI won
        state_values_for_AI_O[i] = 1
    elif winner == 'X':   # AI verloor
        state_values_for_AI_O[i] = -1
        
# Status waardes voor AI 'X'       
for i in range(n_states):
    winner, _ = check_huidige_status(states_dict[i])
    if winner == 'O':   # AI verloor
        state_values_for_AI_X[i] = -1
    elif winner == 'X':   # AI won
        state_values_for_AI_X[i] = 1

def update_state_value_O(curr_state_idx, next_state_idx, learning_rate):
    new_value = state_values_for_AI_O[curr_state_idx] + learning_rate*(state_values_for_AI_O[next_state_idx]  - state_values_for_AI_O[curr_state_idx])
    state_values_for_AI_O[curr_state_idx] = new_value
    
def update_state_value_X(curr_state_idx, next_state_idx, learning_rate):
    new_value = state_values_for_AI_X[curr_state_idx] + learning_rate*(state_values_for_AI_X[next_state_idx]  - state_values_for_AI_X[curr_state_idx])
    state_values_for_AI_X[curr_state_idx] = new_value

def getBestMove(state, speler, nieuwsgierigheid):
    '''
    Reinforcement Learning Algorithm
    '''    
    moves = []
    curr_state_values = []
    empty_cells = []
    for i in range(3):
        for j in range(3):
            if state[i][j] is ' ':
                empty_cells.append(i*3 + (j+1))
    
    for empty_cell in empty_cells:
        moves.append(empty_cell)
        new_state = copy_SpelStatus(state)
        SpelZet(new_state, speler, empty_cell)
        next_state_idx = list(states_dict.keys())[list(states_dict.values()).index(new_state)]
        if speler == 'X':
            curr_state_values.append(state_values_for_AI_X[next_state_idx])
        else:
            curr_state_values.append(state_values_for_AI_O[next_state_idx])
        
    print('Mogelijke zetten = ' + str(moves))
    print('Zet waardes = ' + str(curr_state_values))    
    best_move_idx = np.argmax(curr_state_values)
    
    if np.random.uniform(0,1) <= nieuwsgierigheid:       # Exploratie
        best_move = random.choice(empty_cells)
        print('Agent heeft gekozen om te exploreren! Kiest actie = ' + str(best_move))
        nieuwsgierigheid *= 0.99
    else:   #Exploitatie
        best_move = moves[best_move_idx]
        print('Agent heeft gekozen om te exploiteren! Kiest actie = ' + str(best_move))
    return best_move

# Spel

#Laad de state waardes
state_values_for_AI_X = np.loadtxt('Waardes_X.txt', dtype=np.float64)
state_values_for_AI_O = np.loadtxt('Waardes_O.txt', dtype=np.float64)

learning_rate = 0.3
nieuwsgierigheid = 0.3
num_iteraties = 10
for iteratie in range(num_iteraties):
    SpelStatus = [[' ',' ',' '],
              [' ',' ',' '],
              [' ',' ',' ']]
    huidige_status = "Niet klaar"
    print("\niteratie " + str(iteratie) + "!")
    print_board(SpelStatus)
    winner = None
    current_speler_idx = random.choice([0,1])
        
    while huidige_status == "Niet klaar":
        curr_state_idx = list(states_dict.keys())[list(states_dict.values()).index(SpelStatus)]
        if current_speler_idx == 0:     # AI_X's beurt
            print("\nAI X's beurt!")         
            block_choice = getBestMove(SpelStatus, spelers[current_speler_idx], nieuwsgierigheid)
            SpelZet(SpelStatus ,spelers[current_speler_idx], block_choice)
            new_state_idx = list(states_dict.keys())[list(states_dict.values()).index(SpelStatus)]
            
        else:       # AI_O's beurt
            print("\nAI O's beurt!")   
            block_choice = getBestMove(SpelStatus, spelers[current_speler_idx], nieuwsgierigheid)
            SpelZet(SpelStatus ,spelers[current_speler_idx], block_choice)
            new_state_idx = list(states_dict.keys())[list(states_dict.values()).index(SpelStatus)]
        
        print_board(SpelStatus)
        #print('State value = ' + str(state_values_for_AI[new_state_idx]))
        update_state_value_O(curr_state_idx, new_state_idx, learning_rate)
        update_state_value_X(curr_state_idx, new_state_idx, learning_rate)
        winner, huidige_status = check_huidige_status(SpelStatus)
        if winner is not None:
            print(str(winner) + " Gewonnen!")
        else:
            current_speler_idx = (current_speler_idx + 1)%2
        
        if huidige_status is "Gelijkspel":
            print("Gelijkspel!")
            
        #time.sleep(1)
print('Training Compleet!')    

# Sla waardes op voor volgend gebruik
np.savetxt('Waardes_X.txt', state_values_for_AI_X, fmt = '%.6f')
np.savetxt('Waardes_O.txt', state_values_for_AI_O, fmt = '%.6f')
