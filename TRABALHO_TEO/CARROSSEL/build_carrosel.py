import sys

from utilities import calculate_solution_value, select_best_penalized_item_to_add

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

    solution_indices = penalty_aware_greedy_constructor(
        num_items, capacity, profits, weights, forfeit_costs_matrix
    )
    
    final_profit, final_forfeit_cost, objective_value = calculate_solution_value(
        solution_indices, profits, forfeit_costs_matrix
    )
    
    total_weight = sum(weights[i] for i in solution_indices)
    
    return {
        'selected_items_indices': sorted(solution_indices),
        'total_weight': total_weight,
        'total_profit': final_profit,
        'total_forfeit_cost': final_forfeit_cost,
        'objective_value': objective_value,
        'params': {'type': 'penalty_aware_greedy_construction'}
    }