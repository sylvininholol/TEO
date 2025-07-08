import collections

from utilities import calculate_solution_value
from build_carrosel import select_best_penalized_item_to_add

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

    S_prime_deque = collections.deque(initial_solution_indices[:elite_size])
    current_prime_weight = sum(weights[i] for i in S_prime_deque)
    
    items_available_for_carousel = set(range(num_items)) - set(S_prime_deque)

    num_iterations = int(round(alpha * t)) 

    for _ in range(num_iterations):
        if not S_prime_deque:
            break
        
        item_removed = S_prime_deque.popleft()
        current_prime_weight -= weights[item_removed]
        items_available_for_carousel.add(item_removed) 

        item_to_add_to_prime = select_best_penalized_item_to_add(
            items_available_for_carousel, list(S_prime_deque),
            current_prime_weight, capacity,
            profits, weights, forfeit_costs_matrix
        )

        if item_to_add_to_prime is not None:
            S_prime_deque.append(item_to_add_to_prime)
            current_prime_weight += weights[item_to_add_to_prime]
            items_available_for_carousel.remove(item_to_add_to_prime)
    
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