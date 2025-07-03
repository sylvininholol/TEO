from utilities import calculate_solution_value
from busca_local import (
    _local_search_swap_1_0_optimized,
    _local_search_swap_0_1_optimized,
    _local_search_swap_1_1_optimized,
    _local_search_swap_2_1_optimized,
    _local_search_swap_2_1_optimized_first_improvement,
    calculate_solution_weight
)
from build_grasp import penalty_aware_greedy_constructor_grasp


def grasp_local_search(initial_solution_indices, instance_data):
    """
    Busca local padrão do GRASP usando VND otimizado.
    """
    # Usa o VND como estratégia de busca local padrão
    neighborhoods = [
        _local_search_swap_1_0_optimized,
        _local_search_swap_0_1_optimized,
        _local_search_swap_1_1_optimized,
        #_local_search_swap_2_1_optimized,
        #_local_search_swap_2_1_optimized_first_improvement, 
    ]

    current_solution = initial_solution_indices
    k = 0
    while k < len(neighborhoods):
        new_solution, improved = neighborhoods[k](current_solution, instance_data)
        if improved:
            current_solution = new_solution
            k = 0  # volta para a primeira vizinhança
        else:
            k += 1
            #print("To rodando com o K :", k)

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
        'params': {'type': 'GRASP_LocalSearch_Standard'}
    }