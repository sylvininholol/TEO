import collections
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Construcao.utilities import calculate_solution_value

def _calculate_penalized_metric(item_idx, current_solution_set,
                                 profits, weights, forfeit_costs_matrix):
    """
    Calcula a métrica (lucro_penalizado / peso) para um item,
    considerando penalidades com a solução atual.
    """
    if item_idx < 0 or item_idx >= len(profits):
        return -sys.float_info.max

    penalized_profit = profits[item_idx]
    for sol_item_idx in current_solution_set:
        if sol_item_idx < 0 or sol_item_idx >= len(profits): continue
        penalized_profit -= forfeit_costs_matrix[item_idx][sol_item_idx]

    if weights[item_idx] <= 0:
        if penalized_profit > 0 and weights[item_idx] == 0:
            return sys.float_info.max
        elif penalized_profit == 0 and weights[item_idx] == 0: # Neutro se lucro líquido for 0 e peso 0
             return 0.0
        else: # Peso negativo ou zero com lucro líquido não positivo
            return -sys.float_info.max
    return penalized_profit / weights[item_idx]

def select_best_penalized_item_to_add(available_items_set,
                                      current_solution_list, # Lista para manter a ordem se necessário, ou set
                                      current_weight, capacity,
                                      profits, weights, forfeit_costs_matrix):
    """
    Seleciona o melhor item individual para adicionar a current_solution_list,
    usando a métrica penalizada. Retorna o item_idx ou None.
    """
    best_item_idx = None
    best_metric = -sys.float_info.max # Não adiciona se a melhor métrica for < 0

    current_solution_set = set(current_solution_list)
    
    # Ordena para determinismo no desempate
    sorted_available_items = sorted(list(available_items_set))

    for item_idx in sorted_available_items:
        if item_idx in current_solution_set: # Já está na solução
            continue
        if current_weight + weights[item_idx] <= capacity:
            metric = _calculate_penalized_metric(item_idx, current_solution_set,
                                                 profits, weights, forfeit_costs_matrix)
            if metric > best_metric:
                best_metric = metric
                best_item_idx = item_idx
    
    # Adiciona apenas se a melhor métrica for não negativa
    if best_item_idx is not None and best_metric >= 0:
        return best_item_idx
    return None

def penalty_aware_greedy_constructor(num_items, capacity, profits, weights, forfeit_costs_matrix,
                                     items_to_ignore=None):
    """
    Constrói uma solução completa a partir do zero, de forma gulosa e consciente de penalidades.
    Retorna uma lista de índices de itens.
    items_to_ignore: um set de itens que não devem ser considerados.
    """
    solution_indices = []
    solution_set = set()
    current_weight = 0
    
    if items_to_ignore is None:
        items_to_ignore = set()

    available_items = set(range(num_items)) - items_to_ignore

    while True:
        best_item_to_add = select_best_penalized_item_to_add(
            available_items, solution_indices, current_weight, capacity,
            profits, weights, forfeit_costs_matrix
        )
        if best_item_to_add is not None:
            solution_indices.append(best_item_to_add)
            solution_set.add(best_item_to_add)
            current_weight += weights[best_item_to_add]
            available_items.remove(best_item_to_add)
        else:
            break
    return solution_indices

def penalty_aware_greedy_construction(instance_data):
    """
    Executa apenas a heurística de construção gulosa consciente de penalidades
    e retorna a solução formatada.
    """
    num_items = instance_data['num_items']
    profits = instance_data['profits']
    weights = instance_data['weights']
    capacity = instance_data['capacity']
    forfeit_costs_matrix = instance_data['forfeit_costs_matrix']

    # 1. Construir a solução usando apenas a heurística construtiva
    solution_indices = penalty_aware_greedy_constructor(
        num_items, capacity, profits, weights, forfeit_costs_matrix
    )
    
    # 2. Calcular os resultados finais
    # (Supondo a existência da função calculate_solution_value)
    final_profit, final_forfeit_cost, objective_value = calculate_solution_value(
        solution_indices, profits, forfeit_costs_matrix
    )
    
    total_weight = sum(weights[i] for i in solution_indices)
    
    # 3. Retornar o dicionário de resultados no mesmo formato do original
    return {
        'selected_items_indices': sorted(solution_indices),
        'total_weight': total_weight,
        'total_profit': final_profit,
        'total_forfeit_cost': final_forfeit_cost,
        'objective_value': objective_value,
        'params': {'type': 'penalty_aware_greedy_construction'}
    }

def carousel_local_search(initial_solution_indices, instance_data, alpha, beta):
    """
    Aplica a busca local do tipo Carrossel sobre uma solução inicial fornecida.
    
    Args:
        initial_solution_indices (list): A solução inicial a ser melhorada.
        instance_data (dict): Dicionário contendo os dados do problema.
        alpha (float): Parâmetro que define o número de iterações do carrossel.
        beta (float): Parâmetro que define o tamanho do conjunto elite.

    Returns:
        dict: A solução final encontrada, no mesmo formato de dicionário.
    """
    # 1. Desempacotar dados da instância
    num_items = instance_data['num_items']
    profits = instance_data['profits']
    weights = instance_data['weights']
    capacity = instance_data['capacity']
    forfeit_costs_matrix = instance_data['forfeit_costs_matrix']

    # Se a solução inicial for vazia, não há o que fazer.
    if not initial_solution_indices:
        final_profit, final_forfeit, objective = calculate_solution_value(
            [], profits, forfeit_costs_matrix
        )
        return {
            'selected_items_indices': [], 'total_weight': 0,
            'total_profit': final_profit, 'total_forfeit_cost': final_forfeit,
            'objective_value': objective,
            'params': {'alpha': alpha, 'beta': beta, 'type': 'carousel_on_empty_initial'}
        }

    # 2. Formação do Conjunto Elite (S_prime)
    t = len(initial_solution_indices)
    elite_size = int(round(beta * t))
    if elite_size == 0 and t > 0:
        elite_size = 1

    # O conjunto elite (S_prime) é composto pelos primeiros 'elite_size' itens da solução inicial
    S_prime_deque = collections.deque(initial_solution_indices[:elite_size])
    current_prime_weight = sum(weights[i] for i in S_prime_deque)
    
    # Itens disponíveis para o carrossel são todos que não estão na elite inicial
    items_available_for_carousel = set(range(num_items)) - set(S_prime_deque)

    # 3. Loop do Carrossel
    num_iterations = int(round(alpha * t)) 

    for _ in range(num_iterations):
        if not S_prime_deque:
            break
        
        # Remove o item mais antigo da elite
        item_removed = S_prime_deque.popleft()
        current_prime_weight -= weights[item_removed]
        items_available_for_carousel.add(item_removed) # Devolve para o pool de disponíveis

        # Seleciona o melhor novo item para adicionar à elite
        item_to_add_to_prime = select_best_penalized_item_to_add(
            items_available_for_carousel, list(S_prime_deque),
            current_prime_weight, capacity,
            profits, weights, forfeit_costs_matrix
        )

        if item_to_add_to_prime is not None:
            S_prime_deque.append(item_to_add_to_prime)
            current_prime_weight += weights[item_to_add_to_prime]
            items_available_for_carousel.remove(item_to_add_to_prime)

    # 4. Fase de Preenchimento Final (S_double_prime)
    # Pega a elite resultante do carrossel e tenta preencher a capacidade restante
    
    final_solution_list = list(S_prime_deque)
    final_weight = current_prime_weight
    available_for_fill_set = items_available_for_carousel.copy()

    while True:
        best_item_for_fill = select_best_penalized_item_to_add(
            available_for_fill_set, final_solution_list,
            final_weight, capacity,
            profits, weights, forfeit_costs_matrix
        )
        if best_item_for_fill is not None:
            final_solution_list.append(best_item_for_fill)
            final_weight += weights[best_item_for_fill]
            available_for_fill_set.remove(best_item_for_fill)
        else:
            break
            
    final_solution_indices = sorted(final_solution_list)

    # 5. Retornar a solução final no formato de dicionário
    final_profit, final_forfeit_cost, objective_value = calculate_solution_value(
        final_solution_indices, profits, forfeit_costs_matrix
    )

    return {
        'selected_items_indices': final_solution_indices,
        'total_weight': final_weight,
        'total_profit': final_profit,
        'total_forfeit_cost': final_forfeit_cost,
        'objective_value': objective_value,
        'params': {'alpha': alpha, 'beta': beta, 'type': 'penalty_aware_carousel'}
    }