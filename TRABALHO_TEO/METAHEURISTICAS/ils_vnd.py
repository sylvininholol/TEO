from busca_local import (
    _local_search_swap_0_1_optimized, 
    _local_search_swap_1_0_optimized, 
    _local_search_swap_1_1_optimized,
    _local_search_swap_2_1_optimized,
    _local_search_swap_2_1_optimized_first_improvement,
    
)
from utilities import calculate_solution_value,_perturbation, calculate_solution_weight

def local_search_vnd(solution_indices, instance_data):
    """
    Variable Neighborhood Descent (VND) que agora usa as funções otimizadas.
    """
    neighborhoods = [
        _local_search_swap_1_0_optimized,
        _local_search_swap_0_1_optimized,
        _local_search_swap_1_1_optimized,
        _local_search_swap_2_1_optimized,
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
            
    return current_solution

def iterated_local_search_vnd(initial_solution, instance_data, max_iter_ils=50, perturbation_strength=0.3):
    """
    ILS com VND que agora usa o VND otimizado.
    """
    
    profits = instance_data['profits']
    weights = instance_data['weights']
    forfeit_costs_matrix = instance_data['forfeit_costs_matrix']
    
    #Busca local
    current_solution = local_search_vnd(initial_solution['selected_items_indices'], instance_data)
    
    best_solution_so_far = current_solution
    _, _, best_objective_so_far = calculate_solution_value(best_solution_so_far, profits, forfeit_costs_matrix)
    
    print(f"ILS com VND - Obj. Inicial: {best_objective_so_far:.2f}")

    for i in range(max_iter_ils):
        perturbed_solution = _perturbation(best_solution_so_far, instance_data, strength=perturbation_strength)
        
        refined_solution = local_search_vnd(perturbed_solution, instance_data)
        
        _, _, refined_objective = calculate_solution_value(refined_solution, profits, forfeit_costs_matrix)
        
        if refined_objective > best_objective_so_far:
            best_solution_so_far = refined_solution
            best_objective_so_far = refined_objective
            print(f"   Iter {i+1}/{max_iter_ils}: Melhoria encontrada! Novo Obj = {best_objective_so_far:.2f}")

    final_weight = calculate_solution_weight(best_solution_so_far, weights)
    final_profit, final_forfeit, final_objective = calculate_solution_value(best_solution_so_far, profits, forfeit_costs_matrix)

    return {
        'selected_items_indices': sorted(best_solution_so_far),
        'total_weight': final_weight,
        'total_profit': final_profit,
        'total_forfeit_cost': final_forfeit,
        'objective_value': final_objective,
        'params': {'type': 'ILS_com_VND (Otimizado)'}
    }