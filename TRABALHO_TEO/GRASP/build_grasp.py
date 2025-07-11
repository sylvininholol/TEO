import random

from utilities import _calculate_penalized_metric, calculate_solution_value, calculate_solution_weight

def penalty_aware_greedy_constructor_grasp(num_items, capacity, profits, weights,
                                           forfeit_costs_matrix, rcl_size=3):
    """
    Construtor guloso com lista restrita de candidatos (RCL) para o GRASP.
    A cada passo, escolhe aleatoriamente um dos 'rcl_size' melhores candidatos.
    
    --- MUDANÇA AQUI: Agora retorna um dicionário completo da solução. ---
    """
    solution_indices = []
    current_weight = 0
    available_items = set(range(num_items))

    while True:
        candidates = []
        current_solution_set = set(solution_indices)

        # Avalia todos os itens disponíveis
        for item_idx in sorted(list(available_items)):
            if current_weight + weights[item_idx] <= capacity:
                metric = _calculate_penalized_metric(item_idx, current_solution_set,
                                                     profits, weights, forfeit_costs_matrix)
                if metric >= 0:
                    candidates.append((metric, item_idx))

        if not candidates:
            break

        candidates.sort(key=lambda x: x[0], reverse=True)
        
        rcl = candidates[:rcl_size]

        if not rcl:
            break

        _, chosen_item = random.choice(rcl)
        
        solution_indices.append(chosen_item)
        current_weight += weights[chosen_item]
        available_items.remove(chosen_item)

    if not solution_indices:
         return {
            'selected_items_indices': [], 'total_weight': 0,
            'total_profit': 0, 'total_forfeit_cost': 0,
            'objective_value': -float('inf'), # Usar um valor muito baixo
        }

    final_weight = calculate_solution_weight(solution_indices, weights)
    final_profit, final_forfeit_cost, objective_value = calculate_solution_value(
        solution_indices,
        profits,
        forfeit_costs_matrix
    )
    
    return {
        'selected_items_indices': sorted(solution_indices),
        'total_weight': final_weight,
        'total_profit': final_profit,
        'total_forfeit_cost': final_forfeit_cost,
        'objective_value': objective_value,
    }