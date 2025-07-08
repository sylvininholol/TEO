from busca_local import (
    _local_search_swap_0_1_optimized,
    _local_search_swap_1_0_optimized,
    _local_search_swap_1_1_optimized,
    _local_search_swap_2_1_optimized,
    _local_search_swap_2_1_optimized_first_improvement,
)
from utilities import calculate_solution_value, calculate_solution_weight

def vnd(solution_indices, instance_data):
    """
    Variable Neighborhood Descent (VND) que agora usa as funções otimizadas.
    """
    neighborhoods = [
        _local_search_swap_1_0_optimized,
        _local_search_swap_0_1_optimized,
        _local_search_swap_1_1_optimized,
        #_local_search_swap_2_1_optimized,
        # _local_search_swap_2_1_optimized_first_improvement,
    ]
    
    current_solution = solution_indices
    k = 0
    while k < len(neighborhoods):
        new_solution, improved = neighborhoods[k](current_solution, instance_data)
        
        if improved:
            current_solution = new_solution
            k = 0
        else:
            k += 1
            #print(f"Vizinhança: ", {k})

    # Calcula os valores finais da solução
    final_weight = calculate_solution_weight(current_solution, instance_data['weights'])
    final_profit, final_forfeit_cost, objective_value = calculate_solution_value(
        current_solution,
        instance_data['profits'],
        instance_data['forfeit_costs_matrix']
    )

    return {
        'selected_items_indices': sorted(current_solution),
        'total_weight': final_weight,
        'total_profit': final_profit,
        'total_forfeit_cost': final_forfeit_cost,
        'objective_value': objective_value,
        'params': {'type': 'VND'}
    }