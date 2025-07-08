import itertools

from utilities import _calculate_item_penalty_with_solution, calculate_solution_weight
# ----------------------------------------------------------------------------------
# FUNÇÕES DE BUSCA LOCAL OTIMIZADAS COM CÁLCULO DELTA
# ----------------------------------------------------------------------------------

def _local_search_swap_1_0_optimized(current_solution_indices, instance_data):
    """
    Busca Local (Remoção 1-0) OTIMIZADA com cálculo delta.
    Complexidade: O(s^2), uma melhoria de O(s^3).
    """
    profits = instance_data['profits']
    forfeit_costs_matrix = instance_data['forfeit_costs_matrix']
    
    best_improvement = 1e-9  # Usar um pequeno epsilon para evitar trocas de valor zero
    best_item_to_remove = None
    
    solution_set = set(current_solution_indices)

    for item_to_remove in current_solution_indices:
        # Delta de lucro: negativo, pois estamos perdendo o item
        profit_loss = profits[item_to_remove]
        
        # Delta de penalidade: positivo, pois estamos removendo as penalidades
        # que 'item_to_remove' causava com o resto da solução.
        temp_solution_set = solution_set - {item_to_remove}
        penalty_gain = _calculate_item_penalty_with_solution(item_to_remove, temp_solution_set, forfeit_costs_matrix)
        
        improvement = penalty_gain - profit_loss
        
        if improvement > best_improvement:
            best_improvement = improvement
            best_item_to_remove = item_to_remove

    if best_item_to_remove is not None:
        final_solution = [item for item in current_solution_indices if item != best_item_to_remove]
        return final_solution, True

    return current_solution_indices, False

def _local_search_swap_0_1_optimized(current_solution_indices, instance_data):
    """
    Busca Local (Adição 0-1) OTIMIZADA com cálculo delta.
    Complexidade: O((n-s)*s), uma melhoria de O((n-s)*s^2).
    """
    num_items = instance_data['num_items']
    profits = instance_data['profits']
    weights = instance_data['weights']
    capacity = instance_data['capacity']
    forfeit_costs_matrix = instance_data['forfeit_costs_matrix']

    best_improvement = 1e-9
    best_item_to_add = None
    
    current_weight = calculate_solution_weight(current_solution_indices, weights)
    solution_set = set(current_solution_indices)
    
    for item_to_add in range(num_items):
        if item_to_add not in solution_set:
            if current_weight + weights[item_to_add] <= capacity:
                # Delta de lucro: positivo
                profit_gain = profits[item_to_add]
                
                # Delta de penalidade: negativo, pois estamos adicionando novas penalidades
                penalty_loss = _calculate_item_penalty_with_solution(item_to_add, solution_set, forfeit_costs_matrix)
                
                improvement = profit_gain - penalty_loss
                
                if improvement > best_improvement:
                    best_improvement = improvement
                    best_item_to_add = item_to_add
    
    if best_item_to_add is not None:
        final_solution = current_solution_indices + [best_item_to_add]
        return final_solution, True
        
    return current_solution_indices, False

def _local_search_swap_1_1_optimized(current_solution_indices, instance_data):
    """
    Busca Local (Troca 1-1) OTIMIZADA com cálculo delta.
    Complexidade: O(s*(n-s)*s), uma melhoria de O(s^3*(n-s)).
    """
    num_items = instance_data['num_items']
    profits = instance_data['profits']
    weights = instance_data['weights']
    capacity = instance_data['capacity']
    forfeit_costs_matrix = instance_data['forfeit_costs_matrix']

    best_improvement = 1e-9
    best_move = (None, None)  # (item_out, item_in)
    
    current_weight = calculate_solution_weight(current_solution_indices, weights)
    solution_set = set(current_solution_indices)

    for item_out in current_solution_indices:
        temp_weight = current_weight - weights[item_out]
        
        # Efeito da remoção de 'item_out'
        profit_loss_out = profits[item_out]
        temp_solution_set = solution_set - {item_out}
        penalty_gain_out = _calculate_item_penalty_with_solution(item_out, temp_solution_set, forfeit_costs_matrix)
        
        for item_in in range(num_items):
            if item_in not in solution_set:
                if temp_weight + weights[item_in] <= capacity:
                    # Efeito da adição de 'item_in' na solução temporária
                    profit_gain_in = profits[item_in]
                    penalty_loss_in = _calculate_item_penalty_with_solution(item_in, temp_solution_set, forfeit_costs_matrix)
                    
                    # Melhoria total = (Ganhos - Perdas) da adição + (Ganhos - Perdas) da remoção
                    improvement = (profit_gain_in - penalty_loss_in) + (penalty_gain_out - profit_loss_out)

                    if improvement > best_improvement:
                        best_improvement = improvement
                        best_move = (item_out, item_in)

    if best_move[0] is not None:
        item_out, item_in = best_move
        final_solution = [item for item in current_solution_indices if item != item_out] + [item_in]
        return final_solution, True

    return current_solution_indices, False

def _local_search_swap_2_1_optimized(current_solution_indices, instance_data):
    """
    Busca Local (Troca 2-1) OTIMIZADA com cálculo delta.
    Complexidade: O(s^2*(n-s)*s), uma melhoria de O(s^4*(n-s)).
    """
    num_items = instance_data['num_items']
    profits = instance_data['profits']
    weights = instance_data['weights']
    capacity = instance_data['capacity']
    forfeit_costs_matrix = instance_data['forfeit_costs_matrix']

    if len(current_solution_indices) < 2:
        return current_solution_indices, False

    best_improvement = 1e-9
    best_move = (None, None, None) # (item_removido_1, item_removido_2, item_adicionado)

    current_weight = calculate_solution_weight(current_solution_indices, weights)
    solution_set = set(current_solution_indices)
    
    for r1, r2 in itertools.combinations(current_solution_indices, 2):
        temp_weight = current_weight - weights[r1] - weights[r2]
        
        # Efeito da remoção de r1 e r2
        profit_loss_out = profits[r1] + profits[r2]
        
        temp_solution_set = solution_set - {r1, r2}
        penalty_gain_out_r1 = _calculate_item_penalty_with_solution(r1, temp_solution_set, forfeit_costs_matrix)
        penalty_gain_out_r2 = _calculate_item_penalty_with_solution(r2, temp_solution_set, forfeit_costs_matrix)
        penalty_between_r1_r2 = forfeit_costs_matrix[min(r1, r2)][max(r1, r2)]
        
        total_penalty_gain = penalty_gain_out_r1 + penalty_gain_out_r2 + penalty_between_r1_r2
        
        for item_in in range(num_items):
            if item_in not in solution_set:
                if temp_weight + weights[item_in] <= capacity:
                    profit_gain_in = profits[item_in]
                    penalty_loss_in = _calculate_item_penalty_with_solution(item_in, temp_solution_set, forfeit_costs_matrix)
                    
                    improvement = (profit_gain_in - penalty_loss_in) + (total_penalty_gain - profit_loss_out)

                    if improvement > best_improvement:
                        best_improvement = improvement
                        best_move = (r1, r2, item_in)

    if best_move[2] is not None:
        r1, r2, a1 = best_move
        final_solution = [item for item in current_solution_indices if item != r1 and item != r2] + [a1]
        return final_solution, True

    return current_solution_indices, False

def _local_search_swap_2_1_optimized_first_improvement(current_solution_indices, instance_data):
    
    num_items = instance_data['num_items']
    profits = instance_data['profits']
    weights = instance_data['weights']
    capacity = instance_data['capacity']
    forfeit_costs_matrix = instance_data['forfeit_costs_matrix']

    if len(current_solution_indices) < 2:
        return current_solution_indices, False

    best_improvement = 1e-9
    best_move = (None, None, None)

    current_weight = calculate_solution_weight(current_solution_indices, weights)
    solution_set = set(current_solution_indices)
    
    # Flag para quebrar os laços externos
    found_improvement = False 

    for r1, r2 in itertools.combinations(current_solution_indices, 2):
        temp_weight = current_weight - weights[r1] - weights[r2]
        
        # Efeito da remoção de r1 e r2
        profit_loss_out = profits[r1] + profits[r2]
        
        temp_solution_set = solution_set - {r1, r2}
        penalty_gain_out_r1 = _calculate_item_penalty_with_solution(r1, temp_solution_set, forfeit_costs_matrix)
        penalty_gain_out_r2 = _calculate_item_penalty_with_solution(r2, temp_solution_set, forfeit_costs_matrix)
        penalty_between_r1_r2 = forfeit_costs_matrix[min(r1, r2)][max(r1, r2)]
        
        total_penalty_gain = penalty_gain_out_r1 + penalty_gain_out_r2 + penalty_between_r1_r2
        
        for item_in in range(num_items):
            if item_in not in solution_set:
                if temp_weight + weights[item_in] <= capacity:
                    profit_gain_in = profits[item_in]
                    penalty_loss_in = _calculate_item_penalty_with_solution(item_in, temp_solution_set, forfeit_costs_matrix)
                    
                    improvement = (profit_gain_in - penalty_loss_in) + (total_penalty_gain - profit_loss_out)

                    if improvement > best_improvement:
                        final_solution = [item for item in current_solution_indices if item != r1 and item != r2] + [item_in]
                        return final_solution, True

    return current_solution_indices, False