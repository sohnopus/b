import pygame
import random
import argparse


# define some global variables
Blauw = (0, 0, 255)
Wit = (255, 255, 255)
Zwart = (0, 0, 0)
Rood = (255, 0, 0)
Groen = (0, 255, 0)
Boord_grootte = (7,7)

class ColumnFullException(Exception):
    def __init__(eigen, waarde):
        eigen.waarde = waarde
        
    def __str__(eigen):
        return repr(eigen.waarde)   
    

class Slot():
    SIZE=80
    def __init__(eigen, rij_index, col_index, breedte, hoogte, x1, y1):
       
        eigen.inhoud = 0
        eigen.rij_index = rij_index
        eigen.col_index = col_index
        eigen.breedte = breedte
        eigen.hoogte = hoogte
        eigen.surface = pygame.Surface((breedte*2, hoogte*2))
        eigen.x_pos = x1
        eigen.y_pos = y1
        
    def get_locatie(eigen):
      
        return (eigen.rij_index, eigen.col_index)
    
    def get_position(eigen):
      
        return (eigen.x_pos, eigen.y_pos)
    
    def set_coin(eigen, coin):
     
        eigen.inhoud = coin.get_coin_type()
        
    def check_slot_fill(eigen):
       
        return (eigen.inhoud != 0)
    
    def get_inhoud(eigen):
      
        return eigen.inhoud
        
    def draw(eigen, achtergrond):
       
        pygame.draw.rect(eigen.surface, Groen, (0, 0, eigen.breedte, eigen.hoogte))
        pygame.draw.rect(eigen.surface, Wit, (1,1,eigen.breedte - 2,eigen.hoogte - 2))
        eigen.surface = eigen.surface.convert()
        achtergrond.blit(eigen.surface, (eigen.x_pos, eigen.y_pos))
    
    
class Boord():
   
    MARGIN_X = 300
    MARGIN_Y = 150
    
    def __init__(eigen, num_rijen, num_columns):
      
        eigen.container = [[Slot(i, j, Slot.SIZE, Slot.SIZE, 
                                j*Slot.SIZE + Boord.MARGIN_X, 
                                i*Slot.SIZE + Boord.MARGIN_Y) for j in range(num_columns)] for i in range(num_rijen)]
        eigen.num_rijen = num_rijen
        eigen.num_columns = num_columns
        eigen.total_slots = num_rijen * num_columns
        eigen.num_slots_filled = 0
        eigen.last_visited_nodes = []
        eigen.last_waarde = 0
        
        eigen.state = [[0 for j in range(num_columns)] for i in range(num_rijen)]
        eigen.vorige_state = None
        eigen.vorige_move = (None, None, None)
        eigen.representation = [[SlotTrackerNode() for j in range(num_columns)] for i in range(num_rijen)]
        for i in range(num_rijen):
            vorige_rij_index = i - 1
            next_rij_index = i + 1
            for j in range(num_columns):
                vorige_col_index = j - 1
                next_col_index = j + 1
                current_node = eigen.representation[i][j]
                if vorige_rij_index >= 0 and vorige_col_index >=0:
                    current_node.top_left = eigen.representation[vorige_rij_index][vorige_col_index]
                if vorige_rij_index >=0:
                    current_node.top = eigen.representation[vorige_rij_index][j]
                if vorige_rij_index >=0 and next_col_index < num_columns:
                    current_node.top_right = eigen.representation[vorige_rij_index][next_col_index]
                if vorige_col_index >= 0:
                    current_node.left = eigen.representation[i][vorige_col_index]
                    
                if next_col_index < num_columns:
                    current_node.right = eigen.representation[i][next_col_index]
                if next_rij_index < num_rijen and vorige_col_index >= 0:
                    current_node.bottom_left = eigen.representation[next_rij_index][vorige_col_index]
                    
                if next_rij_index < num_rijen:
                    current_node.bottom = eigen.representation[next_rij_index][j]
                if next_rij_index < num_rijen and next_col_index < num_columns:
                    current_node.bottom_right = eigen.representation[next_rij_index][next_col_index]    
    
    def draw(eigen, achtergrond):
     
        for i in range(eigen.num_rijen):
            for j in range(eigen.num_columns):
                eigen.container[i][j].draw(achtergrond)
                
    def get_slot(eigen, rij_index, col_index):
     
        return eigen.container[rij_index][col_index]
    
    def check_column_fill(eigen, col_num):
       
        for i in range(len(eigen.container)):
            if not eigen.container[i][col_num].check_slot_fill():
                return False
        return True
    
    def insert_coin(eigen, coin, achtergrond, game_logic):
       
        col_num = coin.get_column()
        if not eigen.check_column_fill(col_num):
            rij_index = eigen.determine_rij_to_insert(col_num)
            eigen.container[rij_index][col_num].set_coin(coin)
            if (eigen.vorige_move[0] == None):
                eigen.vorige_state = [[0 for j in range(eigen.num_columns)] for i in range(eigen.num_rijen)]
            else:
                (vorige_rij, vorige_col, waarde) = eigen.vorige_move
                eigen.vorige_state[vorige_rij][vorige_col] = waarde
            eigen.vorige_move = (rij_index, col_num, coin.get_coin_type())    
            eigen.state[rij_index][col_num] = coin.get_coin_type()
            eigen.update_slot_tracker(rij_index, col_num, coin.get_coin_type())
            eigen.num_slots_filled += 1
            eigen.last_waarde = coin.get_coin_type()
            coin.drop(achtergrond, rij_index)
            
        else:
            raise ColumnFullException('Column is already filled!')
        
        result = game_logic.check_game_over()
        
        return result
        
    def determine_rij_to_insert(eigen, col_num):
      
        for i in range(len(eigen.container)):
            if eigen.container[i][col_num].check_slot_fill():
                return (i - 1)
        
        return eigen.num_rijen - 1
                
    def get_dimensions(eigen):
      
        return (eigen.num_rijen, eigen.num_columns)
    
    def check_Boord_filled(eigen):
     
        return (eigen.total_slots == eigen.num_slots_filled)
            
    def get_representation(eigen):
    
        return eigen.representation
    
    def get_available_actions(eigen):
     
        actions = []
        for i in range(eigen.num_columns):
            if (not eigen.check_column_fill(i)):
                actions.append(i)
        return actions
    
    def get_state(eigen):
      
        result = tuple(tuple(x) for x in eigen.state)
        
        return result
    
    def get_vorige_state(eigen):
       
        result = tuple(tuple(x) for x in eigen.vorige_state)
        
        return result
    
    def get_last_filled_information(eigen):
       
        return (eigen.last_visited_nodes, eigen.last_waarde)
    
    def update_slot_tracker(eigen, i, j, coin_type):
       
        eigen.last_visited_nodes = []
        start_node = eigen.representation[i][j]
        start_node.waarde = coin_type
        eigen.traverse(start_node, coin_type, i, j, eigen.last_visited_nodes)

        for indices in eigen.last_visited_nodes:
            eigen.representation[indices[0]][indices[1]].visited = False
            
        
    def traverse(eigen, current_node, desiRood_waarde, i, j, visited_nodes):
      
        current_node.visited = True
        visited_nodes.append((i,j))
        if current_node.top_left:
            top_left_node = current_node.top_left
            if top_left_node.waarde == desiRood_waarde:
                current_node.top_left_score = top_left_node.top_left_score + 1
                if not top_left_node.visited:
                    eigen.traverse(top_left_node, desiRood_waarde, i - 1, j - 1, visited_nodes)
        if current_node.top:
            top_node = current_node.top
            if top_node.waarde == desiRood_waarde:
                current_node.top_score = top_node.top_score + 1
                if not top_node.visited:
                    eigen.traverse(top_node, desiRood_waarde, i - 1, j, visited_nodes)  
        if current_node.top_right:
            top_right_node = current_node.top_right
            if top_right_node.waarde == desiRood_waarde:
                current_node.top_right_score = top_right_node.top_right_score + 1
                if not top_right_node.visited:
                    eigen.traverse(top_right_node, desiRood_waarde, i - 1, j + 1, visited_nodes)          

        if current_node.left:
            left_node = current_node.left
            if left_node.waarde == desiRood_waarde:
                current_node.left_score = left_node.left_score + 1
                if not left_node.visited:
                    eigen.traverse(left_node, desiRood_waarde, i, j - 1, visited_nodes)    
                    
        if current_node.right:
            right_node = current_node.right
            if right_node.waarde == desiRood_waarde:
                current_node.right_score = right_node.right_score + 1
                if not right_node.visited:
                    eigen.traverse(right_node, desiRood_waarde, i, j + 1, visited_nodes)
                    
        if current_node.bottom_left:
            bottom_left_node = current_node.bottom_left
            if bottom_left_node.waarde == desiRood_waarde:
                current_node.bottom_left_score = bottom_left_node.bottom_left_score + 1
                if not bottom_left_node.visited:
                    eigen.traverse(bottom_left_node, desiRood_waarde, i + 1, j - 1, visited_nodes)
        
        if current_node.bottom:
            bottom_node = current_node.bottom
            if bottom_node.waarde == desiRood_waarde:
                current_node.bottom_score = bottom_node.bottom_score + 1
                if not bottom_node.visited:
                    eigen.traverse(bottom_node, desiRood_waarde, i + 1, j, visited_nodes)
                    
        if current_node.bottom_right:
            bottom_right_node = current_node.bottom_right
            if bottom_right_node.waarde == desiRood_waarde:
                current_node.bottom_right_score = bottom_right_node.bottom_right_score + 1
                if not bottom_right_node.visited:
                    eigen.traverse(bottom_right_node, desiRood_waarde, i + 1, j + 1, visited_nodes)
        
 
class GameView(object):


    def __init__(eigen, breedte=640, hoogte=400, fps=30):
      
        pygame.init()
        pygame.display.set_caption("Druk op ESC om te stoppen")
        eigen.breedte = breedte
        eigen.hoogte = hoogte
        eigen.scherm = pygame.display.set_mode((eigen.breedte, eigen.hoogte), pygame.DOUBLEBUF)
        eigen.achtergrond = pygame.Surface(eigen.scherm.get_size()).convert()
        eigen.clock = pygame.time.Clock()
        eigen.fps = fps
        eigen.playtime = 0.0
        eigen.font = pygame.font.SysFont('mono', 20, bold=True)
        eigen.getraindeComputer = None
        eigen.win_list = [0,0]
        
    def initialize_game_variables(eigen, game_mode):
       
        eigen.game_Boord = Boord(Boord_grootte[0], Boord_grootte[1])
        (eigen.Boord_rijen, eigen.Boord_cols) = eigen.game_Boord.get_dimensions()
        eigen.game_logic = GameLogic(eigen.game_Boord)
        first_coin_type = random.randint(1,2)
        second_coin_type = 2 if first_coin_type == 1 else 1 
        
        if game_mode == "single":
            eigen.p1 = MenselijkeSpeler(first_coin_type)
            if (eigen.getraindeComputer == None):
                eigen.p2 = ComputerSpeler(second_coin_type, "qlearner")
                eigen.getraindeComputer = eigen.p2
            else:
                eigen.getraindeComputer.set_coin_type(second_coin_type)
                eigen.p2 = eigen.getraindeComputer
        elif game_mode == "two_Speler":
            eigen.p1 = MenselijkeSpeler(first_coin_type)
            eigen.p2 = MenselijkeSpeler(second_coin_type)
        else:
            eigen.getraindeComputer = None
            eigen.win_list = [0,0]
            eigen.p1 = ComputerSpeler(first_coin_type, "qlearner")
            eigen.p2 = ComputerSpeler(second_coin_type, "qlearner")
        
    
    def main_menu(eigen, iterations=20):
      
        main_menu = True
        play_game = False
        eigen.achtergrond.fill(Wit)
        eigen.draw_menu()
        
        while main_menu:            
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if eigen.rect1.collidepoint(pos):
                        play_game = True
                        main_menu = False
                        game_mode = "two_Speler"
                        
                    elif eigen.rect2.collidepoint(pos):
                        play_game = True
                        main_menu = False
                        game_mode = "single"
                        
                    elif eigen.rect3.collidepoint(pos):
                        play_game = True
                        main_menu = False
                        game_mode = "train"
                        
                    elif eigen.rect4.collidepoint(pos):
                        main_menu = False
                            
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        main_menu = False

                               
            milliseconds = eigen.clock.tick(eigen.fps)
            eigen.playtime += milliseconds / 1000.0
            pygame.display.flip()
            eigen.scherm.blit(eigen.achtergrond, (0, 0))            
            
        if not play_game:
            pygame.quit()
            
        elif game_mode == "train":
            eigen.run(game_mode, iterations)
        
        else:
            eigen.run(game_mode)


    def run(eigen, game_mode, iterations=1):
      
        while (iterations > 0):
            eigen.initialize_game_variables(game_mode)
            eigen.achtergrond.fill(Zwart)
            eigen.game_Boord.draw(eigen.achtergrond)
            game_over = False
            turn_ended = False
            uninitialized = True
            current_type = random.randint(1,2)
            if game_mode == "single":
                Menselijke_turn = (eigen.p1.get_coin_type() == current_type)
                
            elif game_mode == "two_Speler":
                Menselijke_turn = True
                
            else:
                Menselijke_turn = False
                
            p1_turn = (eigen.p1.get_coin_type() == current_type)
                
            (first_slot_X, first_slot_Y) = eigen.game_Boord.get_slot(0,0).get_position()
            coin = Coin(current_type)
            game_over_scherm = False
            while not game_over:
                         
                if uninitialized:
                    coin = Coin(current_type)
                    coin.set_position(first_slot_X, first_slot_Y - Slot.SIZE)
                    coin.set_column(0)
                    uninitialized = False
                    coin_inserted = False
                                   
                coin.draw(eigen.achtergrond)
                
                current_Speler = eigen.p1 if p1_turn else eigen.p2
                
                if not Menselijke_turn:
                    game_over = current_Speler.complete_move(coin, eigen.game_Boord, eigen.game_logic, eigen.achtergrond)
                    coin_inserted = True
                    uninitialized = True
                    
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        game_over = True
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            game_over = True
                        if event.key == pygame.K_RIGHT and Menselijke_turn:
                            if (coin.get_column() + 1 < eigen.Boord_cols):
                                coin.move_right(eigen.achtergrond)
                            
                        elif event.key == pygame.K_LEFT and Menselijke_turn:
                            if (coin.get_column() - 1 >= 0):
                                coin.move_left(eigen.achtergrond)
                            
                        elif event.key == pygame.K_RETURN and Menselijke_turn and not coin_inserted:
                            try:
                                game_over = eigen.game_Boord.insert_coin(coin, eigen.achtergrond, eigen.game_logic)
                                current_Speler.complete_move()
                                uninitialized = True
                                coin_inserted = True
                                
                            except ColumnFullException as e:
                                pass
                
                if game_over:
                    winnaar = eigen.game_logic.determine_winnaar_name()
                    winnaar_waarde = eigen.game_logic.get_winnaar()
                    if (winnaar_waarde > 0 and game_mode == "train"):
                        eigen.win_list[winnaar_waarde - 1] += 1
                    game_over_scherm = True
                    
                if coin_inserted:
                    if game_mode == "single":
                        Menselijke_turn = not Menselijke_turn
                    current_type = 1 if current_type == 2 else 2 
                    p1_turn = not p1_turn
                         
    
                milliseconds = eigen.clock.tick(eigen.fps)
                eigen.playtime += milliseconds / 1000.0
                pygame.display.flip()
                eigen.scherm.blit(eigen.achtergrond, (0, 0))
                
            iterations -= 1
            
        if game_mode == "train":
            index = eigen.win_list.index(max(eigen.win_list))
            eigen.getraindeComputer = eigen.p1 if index == 0 else eigen.p2
            eigen.main_menu()
        
        else:
            eigen.game_over_view(winnaar)
        
    def draw_menu(eigen):
    
        font = pygame.font.SysFont('mono', 60, bold=True)
        eigen.title_surface = font.render('CONNECT 4', True, Zwart)
        fw, fh = font.size('CONNECT 4')
        eigen.achtergrond.blit(eigen.title_surface, ((eigen.breedte - fw) // 2, 150))
        two_Speler_text = '2 Speler Modus'
        computer_Speler_text = 'vs Computer'
        train_text = 'Train Computer'
        quit_text = 'Sluit af'
        font = pygame.font.SysFont('mono', 40, bold=True)
        
        eigen.play_surface = font.render(two_Speler_text, True, Zwart)
        fw, fh = font.size(two_Speler_text)     
        eigen.rect1 = eigen.play_surface.get_rect(topleft=((eigen.breedte - fw) // 2, 300))
        eigen.achtergrond.blit(eigen.play_surface, ((eigen.breedte - fw) // 2, 300) )
        
        computer_play_surface = font.render(computer_Speler_text, True, Zwart)
        fw, fh = font.size(computer_Speler_text)     
        eigen.rect2 = computer_play_surface.get_rect(topleft=((eigen.breedte - fw) // 2, 350))
        eigen.achtergrond.blit(computer_play_surface, ((eigen.breedte - fw) // 2, 350) )    
        
        eigen.train_surface = font.render(train_text, True, Zwart)
        fw, fh = font.size(train_text)        
        eigen.rect3 = eigen.train_surface.get_rect(topleft=((eigen.breedte - fw) // 2, 400))
        eigen.achtergrond.blit(eigen.train_surface, ((eigen.breedte - fw) // 2, 400) )        
        
        eigen.quit_surface = font.render(quit_text, True, Zwart)
        fw, fh = font.size(quit_text)        
        eigen.rect4 = eigen.quit_surface.get_rect(topleft=((eigen.breedte - fw) // 2, 450))
        eigen.achtergrond.blit(eigen.quit_surface, ((eigen.breedte - fw) // 2, 450) )   
        
    def game_over_view(eigen, winnaar):
       
        game_over_scherm = True
        main_menu = False
        eigen.achtergrond.fill(Wit)
        eigen.draw_game_over(winnaar)
        
        while game_over_scherm:            
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if eigen.rect1.collidepoint(pygame.mouse.get_pos()):
                        main_menu = True
                        game_over_scherm = False
                        
                    elif eigen.rect2.collidepoint(pygame.mouse.get_pos()):
                        game_over_scherm = False
                            
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_over_scherm = False

                               
            milliseconds = eigen.clock.tick(eigen.fps)
            eigen.playtime += milliseconds / 1000.0
            pygame.display.flip()
            eigen.scherm.blit(eigen.achtergrond, (0, 0))            
            
        if not main_menu:
            pygame.quit()
            
        else:
            eigen.main_menu()        
        
    
    def draw_game_over(eigen, winnaar):
       
        font = pygame.font.SysFont('mono', 60, bold=True)
        game_over_text = 'GAME OVER'
        eigen.title_surface = font.render(game_over_text, True, Groen)
        fw, fh = font.size(game_over_text)
        eigen.achtergrond.blit(eigen.title_surface, ((eigen.breedte - fw) // 2, 150))
        play_again_text = 'Terug naar hoofdmenu'
        quit_text = 'Sluit af'
        if winnaar != 'Gelijkspel':
            winnaar_text = winnaar + " wint!"
        else:
            winnaar_text = "Het was een " + winnaar + "!"
        font = pygame.font.SysFont('mono', 40, bold=True)
        winnaar_surface = font.render(winnaar_text, True, Zwart)
        fw, fh = font.size(winnaar_text)
        eigen.achtergrond.blit(winnaar_surface, ((eigen.breedte - fw) // 2, 300) )
        
        font = pygame.font.SysFont('mono', 40, bold=False)
        eigen.play_surface = font.render(play_again_text, True, (0,  0, 0))       
        fw, fh = font.size(play_again_text)     
        eigen.rect1 = eigen.play_surface.get_rect(topleft=((eigen.breedte - fw) // 2, 360))
        eigen.achtergrond.blit(eigen.play_surface, ((eigen.breedte - fw) // 2, 360) )
        
        eigen.quit_surface = font.render(quit_text, True, (0,  0, 0))
        fw, fh = font.size(quit_text)        
        eigen.rect2 = eigen.quit_surface.get_rect(topleft=((eigen.breedte - fw) // 2, 410))
        eigen.achtergrond.blit(eigen.quit_surface, ((eigen.breedte - fw) // 2, 410) ) 
        
    
class Speler():
    
    def __init__(eigen, coin_type):
       
        eigen.coin_type = coin_type
        
    def complete_move(eigen):
        
        pass
    
    def get_coin_type(eigen):
        
        return eigen.coin_type
    
    def set_coin_type(eigen, coin_type):
      
        eigen.coin_type = coin_type
    
    
class MenselijkeSpeler(Speler):
    
    def __init__(eigen, coin_type):
      
        Speler.__init__(eigen, coin_type)
        
        
class ComputerSpeler(Speler):
    
    def __init__(eigen, coin_type, Speler_type):
     
        if (Speler_type == "random"):
            eigen.Speler = RandomSpeler(coin_type)
        else:
            eigen.Speler = QLearningSpeler(coin_type)
        
    def complete_move(eigen, coin, Boord, game_logic, achtergrond):
      
        actions = Boord.get_available_actions()
        state = Boord.get_state()
        chosen_action = eigen.choose_action(state, actions)
        coin.move_right(achtergrond, chosen_action)
        coin.set_column(chosen_action)
        game_over = Boord.insert_coin(coin, achtergrond, game_logic)
        eigen.Speler.learn(Boord, actions, chosen_action, game_over, game_logic)
        
        return game_over
    
    def get_coin_type(eigen):
       
        return eigen.Speler.get_coin_type()
    
    def choose_action(eigen, state, actions):
       
        return eigen.Speler.choose_action(state, actions)
    
    
class RandomSpeler(Speler):
    
    def __init__(eigen, coin_type):
      
        Speler.__init__(eigen, coin_type)
        
    def choose_action(eigen, state, actions):
      
        return random.choice(actions)
                
    def learn(eigen, Boord, action, game_over, game_logic):
     
        pass
    
    
class QLearningSpeler(Speler):
  
    
    def __init__(eigen, coin_type, epsilon=0.2, alpha=0.3, gamma=0.9):
       
        Speler.__init__(eigen, coin_type)
        eigen.q = {}
        eigen.epsilon = epsilon # e-greedy chance of random exploration
        eigen.alpha = alpha # learning rate
        eigen.gamma = gamma # discount factor for future rewards 
        
    def getQ(eigen, state, action):
   
        # encourage exploration; "optimistic" 1.0 initial waardes
        if eigen.q.get((state, action)) is None:
            eigen.q[(state, action)] = 1.0
        return eigen.q.get((state, action))    
        
    def choose_action(eigen, state, actions):
 
        current_state = state

        if random.random() < eigen.epsilon: # explore!
            chosen_action = random.choice(actions)
            return chosen_action

        qs = [eigen.getQ(current_state, a) for a in actions]
        maxQ = max(qs)

        if qs.count(maxQ) > 1:
            # more than 1 best option; choose among them randomly
            best_options = [i for i in range(len(actions)) if qs[i] == maxQ]
            i = random.choice(best_options)
        else:
            i = qs.index(maxQ)

        return actions[i]
    
    def learn(eigen, Boord, actions, chosen_action, game_over, game_logic):
        reward = 0
        if (game_over):
            win_waarde = game_logic.get_winnaar()
            if win_waarde == 0:
                reward = 0.5
            elif win_waarde == eigen.coin_type:
                reward = 1
            else:
                reward = -2
        vorige_state = Boord.get_vorige_state()
        vorige = eigen.getQ(vorige_state, chosen_action)
        result_state = Boord.get_state()
        maxqnew = max([eigen.getQ(result_state, a) for a in actions])
        eigen.q[(vorige_state, chosen_action)] = vorige + eigen.alpha * ((reward + eigen.gamma*maxqnew) - vorige)    
        
    
    

class Coin():
    
    RADIUS = 30
    
    def __init__(eigen, coin_type):
       
        eigen.coin_type = coin_type
        eigen.surface = pygame.Surface((Slot.SIZE - 3, Slot.SIZE - 3))
        if (eigen.coin_type == 1):
            eigen.color = Blauw
        else:
            eigen.color = Rood
    
    def set_position(eigen, x1, y1):
       
        eigen.x_pos = x1
        eigen.y_pos = y1
        
    def set_column(eigen, col):
        
        eigen.col = col
        
    def get_column(eigen):

        return eigen.col
    
    def set_rij(eigen, rij):
      
        eigen.rij = rij
        
    def get_rij(eigen):
      
        return eigen.rij
    
    def move_right(eigen, achtergrond, step=1):
     
        eigen.set_column(eigen.col + 1)
        eigen.surface.fill((0,0,0))
        achtergrond.blit(eigen.surface, (eigen.x_pos, eigen.y_pos))
        eigen.set_position(eigen.x_pos + step * Slot.SIZE, eigen.y_pos)
        eigen.draw(achtergrond)
            
    def move_left(eigen, achtergrond):
      
        eigen.set_column(eigen.col - 1)
        eigen.surface.fill((0,0,0))
        achtergrond.blit(eigen.surface, (eigen.x_pos, eigen.y_pos))
        eigen.set_position(eigen.x_pos - Slot.SIZE, eigen.y_pos)
        eigen.draw(achtergrond)  
            
    def drop(eigen, achtergrond, rij_num):
      
        eigen.set_rij(rij_num)
        eigen.surface.fill((0,0,0))
        achtergrond.blit(eigen.surface, (eigen.x_pos, eigen.y_pos))
        eigen.set_position(eigen.x_pos, eigen.y_pos + ((eigen.rij + 1) * Slot.SIZE))
        eigen.surface.fill((255,255,255))
        achtergrond.blit(eigen.surface, (eigen.x_pos, eigen.y_pos))
        eigen.draw(achtergrond) 
            
    def get_coin_type(eigen):
        
        return eigen.coin_type
    
    def draw(eigen, achtergrond):
        
        pygame.draw.circle(eigen.surface, eigen.color, (Slot.SIZE // 2, Slot.SIZE // 2), Coin.RADIUS)
        eigen.surface = eigen.surface.convert()
        achtergrond.blit(eigen.surface, (eigen.x_pos, eigen.y_pos))    
        
        
        
class GameLogic():
   
    WIN_SEQUENCE_LENGTH = 4
    
    def __init__(eigen, Boord):
        
        eigen.Boord = Boord
        (num_rijen, num_columns) = eigen.Boord.get_dimensions()
        eigen.Boord_rijen = num_rijen
        eigen.Boord_cols = num_columns
        eigen.winnaar_waarde = 0
    
    def check_game_over(eigen):
      
        (last_visited_nodes, Speler_waarde) = eigen.Boord.get_last_filled_information()
        representation = eigen.Boord.get_representation()        
        Speler_won = eigen.search_win(last_visited_nodes, representation)
        if Speler_won:
            eigen.winnaar_waarde = Speler_waarde
            
        return ( Speler_won or eigen.Boord.check_Boord_filled() )
        
        
    
    def search_win(eigen, last_visited_nodes, representation):
        
        for indices in last_visited_nodes:
            current_node = representation[indices[0]][indices[1]]
            if ( current_node.top_left_score == GameLogic.WIN_SEQUENCE_LENGTH or 
                 current_node.top_score == GameLogic.WIN_SEQUENCE_LENGTH or
                 current_node.top_right_score == GameLogic.WIN_SEQUENCE_LENGTH or
                 current_node.left_score == GameLogic.WIN_SEQUENCE_LENGTH or
                 current_node.right_score == GameLogic.WIN_SEQUENCE_LENGTH or
                 current_node.bottom_left_score == GameLogic.WIN_SEQUENCE_LENGTH or
                 current_node.bottom_score == GameLogic.WIN_SEQUENCE_LENGTH or
                 current_node.bottom_right_score == GameLogic.WIN_SEQUENCE_LENGTH ):
                return True
            
        return False
    
    def determine_winnaar_name(eigen):
        
        if (eigen.winnaar_waarde == 1):
            return "Blauw"
        elif (eigen.winnaar_waarde == 2):
            return "Rood"
        else:
            return "TIE"
        
    def get_winnaar(eigen):
       
        return eigen.winnaar_waarde
    
    
class SlotTrackerNode():
    
    
    def __init__(eigen):
       
        eigen.top_left = None
        eigen.top_right = None
        eigen.top = None
        eigen.left = None
        eigen.right = None
        eigen.bottom_left = None
        eigen.bottom = None
        eigen.bottom_right = None       
        eigen.top_left_score = 1
        eigen.top_right_score = 1
        eigen.top_score = 1
        eigen.left_score = 1
        eigen.right_score = 1
        eigen.bottom_left_score = 1
        eigen.bottom_score = 1
        eigen.bottom_right_score = 1
        eigen.waarde = 0
        eigen.visited = False

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('iterations', nargs='?', default=50, action="store", help="Store the number of iterations to train AI")
    args = parser.parse_args()

    GameView(1200, 760).main_menu(int(args.iterations))
