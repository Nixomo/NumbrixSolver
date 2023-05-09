# numbrix.py: Projeto de Inteligência Artificial 2021/2022.

# Grupo 01:
# 93747 Pedro Gomes
# 93749 Rafael Pereira

import sys
from search import Problem, Node, astar_search, breadth_first_tree_search, depth_first_tree_search, depth_first_graph_search, greedy_search, recursive_best_first_search
import copy
import time


class NumbrixState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = NumbrixState.state_id
        NumbrixState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id
        

class Board:
    """ Representação interna de um tabuleiro de Numbrix. """

    def __init__(self, n, board, filled, ant_pos):
        self.n = n
        self.board = board
        self.filled = filled
        self.ant_pos = ant_pos

    def get_number(self, row: int, col: int) -> int:
        """ Devolve o valor do quadrado em board[row][col] """
        return self.board[row][col]

    def adjacent_vertical_numbers(self, row: int, col: int):
        """ Devolve os valores imediatamente abaixo e acima, 
        respectivamente. """
        if row == 0:
            return (self.board[row + 1][col], None)
        if row == self.n - 1:
            return (None, self.board[row - 1][col])
        return (self.board[row + 1][col], self.board[row - 1][col])
    
    def adjacent_horizontal_numbers(self, row: int, col: int):
        """ Devolve os valores imediatamente à esquerda e à direita, 
        respectivamente. """
        if col == 0:
            return (None, self.board[row][col + 1])
        if col == self.n - 1:
            return (self.board[row][col - 1], None)
        return (self.board[row][col - 1], self.board[row][col + 1])
    
    def find_number(self, number: int):
        """ Devolve o tuplo com a localização do número requisitado. """

        for i in range(self.n):
            for j in range(self.n):
                if self.board[i][j] == number:
                    return (i, j)
        
        return (None, None)
    
    def is_ant_pos_adjacent(self, row: int, col: int, val: int):
        """ Procura saber se, numa dada posição vazia, dois números (anterior e posterior)
        estão presentes nas posições adjacentes. """
        
        b = self.board
        ant_pos = 0
        (a, b) = self.adjacent_horizontal_numbers(row, col)
        (c, d) = self.adjacent_vertical_numbers(row, col)   
        
        if a == val + 1 or a == val - 1:
            ant_pos += 1          
        
        if b == val + 1 or b == val - 1:
            ant_pos += 1
        
        if c == val + 1 or c == val - 1:
            ant_pos += 1
        
        if d == val + 1 or d == val - 1:
            ant_pos += 1

        if ant_pos < 2:
            return False

        return True

    def is_valid_distance(self, row: int, col: int, val: int):

        goal = 0
        for i in range(len(self.filled)):
            if (self.filled[i] == val - 1):
                if i + 1 == len(self.filled):
                    return True
                else:
                    goal = self.filled[i + 1]
                    break
        for i in range(len(self.filled)):
            if (self.filled[i] == val + 1):
                if i == 0:
                    return True
                else:
                    goal = self.filled[i - 1]
                    break
        if goal == 0:
            return True
        (x, y) = self.find_number(goal)
        distance= abs(x-row) + abs(y-col)
        diff = abs(goal - val)
        return distance <= diff


    def print_board(self):
        """ Imprime a matriz do tabuleiro """
        for line in self.board:
            print(*line, sep = "\t")
    
    @staticmethod    
    def parse_instance(filename: str):
        """ Lê o ficheiro cujo caminho é passado como argumento e retorna
        uma instância da classe Board. """
        
        f = open(filename, "r")
        n = int(f.readline())

        if n <= 0:
            raise ValueError("Invalid Dimension!")
        
        board = []
        filled = []
        ant_pos = []

        for line in f:
            numbers = line.split("\t")
            numbers = list(map(int, numbers))
            board.append(numbers)
            for num in numbers:
                if num != 0:

                    filled.append(num)
                    
                    if num == 1 and (num + 1) not in filled:
                        ant_pos.append(num + 1)
                    elif num == n*n and (num - 1) not in filled:
                        ant_pos.append(num - 1)
                    else:
                        if (num - 1) not in filled:
                            ant_pos.append(num - 1)
                        if (num + 1) not in filled:
                            ant_pos.append(num + 1)
                                        
                    if num in ant_pos:
                        ant_pos.remove(num)

        f.close()

        filled.sort()
        ant_pos.sort()
        ant_pos = list(dict.fromkeys(ant_pos))

        return Board(n, board, filled, ant_pos)


class Numbrix(Problem):
    def __init__(self, board: Board):
        """ O construtor especifica o estado inicial. """
        self.initial = board

    def actions(self, state: NumbrixState):
        """ Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento. """
        actions_list = []
        actions_dict = {}

        n = state.board.n
        b = state.board.board
        filled_list = state.board.filled
        ap = state.board.ant_pos
        minimo = [1,2,3,4]
        for k in ap:
            for i in range(n):
                for j in range(n):
                    (a, b) = state.board.adjacent_horizontal_numbers(i, j)
                    (c, d) = state.board.adjacent_vertical_numbers(i, j)                            
                    if state.board.get_number(i, j) == 0 and (a != 0 or b != 0 or c != 0 or d != 0):
                        if (k - 1) in filled_list and (k + 1) in filled_list:
                            if state.board.is_ant_pos_adjacent(i, j, k):
                                actions_list.append((i, j, k))                                                            
                        elif (((a != None and a != 0) and (a == k - 1 or a == k + 1)) or 
                            ((b != None and b != 0) and (b == k - 1 or b == k + 1)) or 
                            ((c != None and c != 0) and (c == k - 1 or c == k + 1)) or 
                            ((d != None and d != 0) and (d == k - 1 or d == k + 1))):
                            if state.board.is_valid_distance(i, j, k):
                                actions_list.append((i, j, k))
            
            actions_dict[k] = copy.copy(actions_list)
            
            if (len(actions_dict[k]) < len(minimo) and len(actions_dict[k]) > 0):
                minimo = actions_dict[k]
            
            if len(minimo) == 1:
                return minimo
            
            #print("Lista de acoes com k:", k, actions_list)
            actions_list.clear()
            #print(actions_dict[k])

        if minimo == [1,2,3,4]:
            return []
        #print(min)
        return minimo

    def result(self, state: NumbrixState, action):
        """ Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de 
        self.actions(state). """
        actions_list = self.actions(state)

        #print("\nBoard Inicial:", state.id)
        #print("\nFilled: ", state.board.filled, "\nProximos: ", state.board.ant_pos, sep = " ")
        #print("\nTenho a lista de acoes ", actions_list, sep = " ")
        #print("Vou aplicar a acao ", action, sep = " ")

        if action not in actions_list:
            return state

        (row, col, val) = action

        newBoard = copy.deepcopy(state.board)
        newState = NumbrixState(newBoard)

        newState.board.board[row][col] = val
        newState.board.filled.append(val)
        newState.board.filled.sort()

        if val == 1 and not ((val + 1) in newState.board.ant_pos) and not ((val + 1) in newState.board.filled):
            newState.board.ant_pos.append(val + 1)

        elif val == newState.board.n*newState.board.n and not ((val - 1) in newState.board.ant_pos) and not ((val - 1) in newState.board.filled):
            newState.board.ant_pos.append(val - 1)
    
        elif val != 1 and val != newState.board.n*newState.board.n:
            if (val + 1) not in newState.board.ant_pos and (val + 1) not in newState.board.filled:
                newState.board.ant_pos.append(val + 1)
            if (val - 1) not in newState.board.ant_pos and (val - 1) not in newState.board.filled:
                newState.board.ant_pos.append(val - 1)
                
        for i in newState.board.ant_pos:
            if (i == val):
                newState.board.ant_pos.remove(i)
        
        newState.board.ant_pos.sort()

        #print("Novo board:", newState.id, action)
        #if newState.id == 1:
        #    print(newState.board.filled)
        #newState.board.print_board()
        #print("\nFilled: ", newState.board.filled, "\nProximos: ", newState.board.ant_pos, sep = " ")

        return newState
    

    def goal_test(self, state: NumbrixState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro 
        estão preenchidas com uma sequência de números adjacentes."""
        
        n = state.board.n
        f = state.board.filled
        ap = state.board.ant_pos

        if len(f) != n*n and len(ap) != 0:
            return False

        val = 1
        (row, col) = state.board.find_number(val)

        if (row == None and col == None):
            return False
            
        for val in range(1, n*n):
            (esquerda, direita) = state.board.adjacent_horizontal_numbers(row, col)
            (baixo, cima) = state.board.adjacent_vertical_numbers(row, col)
            if row == 0:
                if col == 0:
                    if not (direita == val + 1 or baixo == val + 1):
                        return False
                elif col == n - 1:
                    if not (esquerda == val + 1 or baixo == val + 1):
                        return False
                else:
                    if not (esquerda == val + 1 or direita == val + 1 or baixo == val + 1):
                        return False
                    
            elif row == n - 1:
                if col == 0:
                    if not (direita == val + 1 or cima == val + 1):
                        return False
                elif col == n - 1:
                    if not (esquerda == val + 1 or cima == val + 1):
                        return False
                else:
                    if not (esquerda == val + 1 or direita == val + 1 or cima == val + 1):
                        return False         

            else:
                if not (esquerda == val + 1 or direita == val + 1 or cima == val + 1 or baixo == val + 1):
                    return False

            (row, col) = state.board.find_number(val + 1)        
        return True    

    def h(self, node: Node):
        """ Função heuristica utilizada para a procura A*. """
        return 
    

if __name__ == "__main__":
    # Ler o ficheiro de input de sys.argv[1],
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    # Imprimir para o standard output no formato indicado.
    start_time = time.time()
    board = Board.parse_instance(sys.argv[1])
    s0 = NumbrixState(board)
    problem = Numbrix(s0)
    goal_node = depth_first_graph_search(problem)
    #goal_node = breadth_first_tree_search(problem)
    #print("Estado final: \n")
    goal_node.state.board.print_board()
    end_time = time.time()
    duration = end_time - start_time
    print('Execution time:', duration, 'seconds')
    print("Is goal?", problem.goal_test(goal_node.state))
    #print("Solution:\n", goal_node.state.board.to_string(), sep="")