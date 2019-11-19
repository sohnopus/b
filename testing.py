import numpy as np
from math import inf as infinity
import itertools
import random

spel_status = [[' ',' ',' '],
              [' ',' ',' '],
              [' ',' ',' ']]
spelers = ['X','O']

def SpelZet(state, speler, block_num):
    if state[int((block_num-1)/3)][(block_num-1)%3] is ' ':
        state[int((block_num-1)/3)][(block_num-1)%3] = speler
    else:
        block_num = int(input("De gekozen vak is al bezet, kies een andere vak: "))
        SpelZet(state, speler, block_num)
    
def copy_spel_status(state):
    new_state = [[' ',' ',' '],[' ',' ',' '],[' ',' ',' ']]
    for i in range(3):
        for j in range(3):
            new_state[i][j] = state[i][j]
    return new_state
    
def check_huidige_state(spel_status):    
    # Controleer horizontale as
    if (spel_status[0][0] == spel_status[0][1] and spel_status[0][1] == spel_status[0][2] and spel_status[0][0] is not ' '):
        return spel_status[0][0], "Klaar"
    if (spel_status[1][0] == spel_status[1][1] and spel_status[1][1] == spel_status[1][2] and spel_status[1][0] is not ' '):
        return spel_status[1][0], "Klaar"
    if (spel_status[2][0] == spel_status[2][1] and spel_status[2][1] == spel_status[2][2] and spel_status[2][0] is not ' '):
        return spel_status[2][0], "Klaar"
    
    # Controleer verticale as
    if (spel_status[0][0] == spel_status[1][0] and spel_status[1][0] == spel_status[2][0] and spel_status[0][0] is not ' '):
        return spel_status[0][0], "Klaar"
    if (spel_status[0][1] == spel_status[1][1] and spel_status[1][1] == spel_status[2][1] and spel_status[0][1] is not ' '):
        return spel_status[0][1], "Klaar"
    if (spel_status[0][2] == spel_status[1][2] and spel_status[1][2] == spel_status[2][2] and spel_status[0][2] is not ' '):
        return spel_status[0][2], "Klaar"
    
    # Controleer diagonale as
    if (spel_status[0][0] == spel_status[1][1] and spel_status[1][1] == spel_status[2][2] and spel_status[0][0] is not ' '):
        return spel_status[1][1], "Klaar"
    if (spel_status[2][0] == spel_status[1][1] and spel_status[1][1] == spel_status[0][2] and spel_status[2][0] is not ' '):
        return spel_status[1][1], "Klaar"
    
    # Controleer of het gelijkspel is
    draw_flag = 0
    for i in range(3):
        for j in range(3):
            if spel_status[i][j] is ' ':
                draw_flag = 1
    if draw_flag is 0:
        return None, "Gelijkspel"
    
    return None, "Niet klaar"

def print_board(spel_status):
    print('----------------')
    print('| ' + str(spel_status[0][0]) + ' || ' + str(spel_status[0][1]) + ' || ' + str(spel_status[0][2]) + ' |')
    print('----------------')
    print('| ' + str(spel_status[1][0]) + ' || ' + str(spel_status[1][1]) + ' || ' + str(spel_status[1][2]) + ' |')
    print('----------------')
    print('| ' + str(spel_status[2][0]) + ' || ' + str(spel_status[2][1]) + ' || ' + str(spel_status[2][2]) + ' |')
    print('----------------')
    
  
# Initializeer zet waardes
speler = ['X','O',' ']
states_dict = {}
alle_mogelijke_states = [[list(i[0:3]),list(i[3:6]),list(i[6:10])] for i in itertools.product(speler, repeat = 9)]
n_states = len(alle_mogelijke_states) # 2 spelers, 9 spaces
n_acties = 9   # 9 spaces
state_values_for_AI = np.full((n_states),0.0)
print("n_states = %i \nn_acties = %i"%(n_states, n_acties))

for i in range(n_states):
    states_dict[i] = alle_mogelijke_states[i]
    winnaar, _ = check_huidige_state(states_dict[i])
    if winnaar == 'O':   # AI won
        state_values_for_AI[i] = 1
    elif winnaar == 'X':   # AI verloor
        state_values_for_AI[i] = -1

def update_state_value(hdg_state_idx, next_state_idx, learning_rate):
    new_value = state_values_for_AI[hdg_state_idx] + learning_rate*(state_values_for_AI[next_state_idx]  - state_values_for_AI[hdg_state_idx])
    state_values_for_AI[hdg_state_idx] = new_value

def getBestMove(state, speler):
    '''
    Reinforcement Learning Algorithm
    '''    
    moves = []
    hdg_state_values = []
    empty_cells = []
    for i in range(3):
        for j in range(3):
            if state[i][j] is ' ':
                empty_cells.append(i*3 + (j+1))
    
    for empty_cell in empty_cells:
        moves.append(empty_cell)
        new_state = copy_spel_status(state)
        SpelZet(new_state, speler, empty_cell)
        next_state_idx = list(states_dict.keys())[list(states_dict.values()).index(new_state)]
        hdg_state_values.append(state_values_for_AI[next_state_idx])
        
    print('Mogelijke zetten = ' + str(moves))
    print('Zet waardes = ' + str(hdg_state_values))    
    best_move_idx = np.argmax(hdg_state_values)
    best_move = moves[best_move_idx]
    return best_move

# Spelen
    
#Laad de zet waardes
state_values_for_AI = np.loadtxt('Waardes_O.txt', dtype=np.float64)

play_again = 'Y'
while play_again == 'Y' or play_again == 'y':
    spel_status = [[' ',' ',' '],
              [' ',' ',' '],
              [' ',' ',' ']]
    huidige_state = "Niet klaar"
    print("\nNieuwe spel!")
    print_board(spel_status)
    speler_keuze = input("Kies wie als eerst een zet mag nemen, Jij(X) of de AI(O) ")
    winnaar = None
    
    if speler_keuze == 'X' or speler_keuze == 'x':
        huidige_speler_idx = 0
    else:
        huidige_speler_idx = 1
        
    while huidige_state == "Niet klaar":
        hdg_state_idx = list(states_dict.keys())[list(states_dict.values()).index(spel_status)]
        if huidige_speler_idx == 0: # Mens's beurt
            block_keuze = int(input("Het is jouw beurt om een zet te nemen, kies een vak:(1 to 9): "))
            SpelZet(spel_status ,spelers[huidige_speler_idx], block_keuze)
            
        else:   # AI's beurt
            block_keuze = getBestMove(spel_status, spelers[huidige_speler_idx])
            SpelZet(spel_status ,spelers[huidige_speler_idx], block_keuze)
            print("AI plays move: " + str(block_keuze))
        
        print_board(spel_status)
        winnaar, huidige_state = check_huidige_state(spel_status)
        if winnaar is not None:
            print(str(winnaar) + " won!")
        else:
            huidige_speler_idx = (huidige_speler_idx + 1)%2
        
        if huidige_state is "Gelijkspel":
            print("Gelijkspel!")
            
    play_again = input('Wil je nog een keer spelen?(Y/N) : ')
print('Tot de volgende keer :D')        
    
