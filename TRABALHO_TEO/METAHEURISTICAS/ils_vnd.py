from utilities import calculate_solution_value,_perturbation, calculate_solution_weight
from METAHEURISTICAS.vnd import vnd

def iterated_local_search_vnd(initial_solution, instance_data, max_iter_ils=50, perturbation_strength=0.3):
    """
    ILS com VND que agora usa o VND otimizado.
    """
    # A função de perturbação continua a mesma, pois já era construtiva
    # e não recalculava a solução inteira repetidamente.
    # ... (A função _perturbation não precisa de mudanças)
    
    # Restante do código do ILS com VND permanece o mesmo,
    # apenas se beneficia da velocidade do novo `local_search_vnd`.
    
    profits = instance_data['profits']
    weights = instance_data['weights']
    forfeit_costs_matrix = instance_data['forfeit_costs_matrix']
    
    #Busca local
    current_solution = vnd(initial_solution['selected_items_indices'], instance_data)
    
    best_solution_so_far = current_solution
    _, _, best_objective_so_far = calculate_solution_value(best_solution_so_far['selected_items_indices'], profits, forfeit_costs_matrix)
    
    print(f"ILS com VND - Obj. Inicial: {best_objective_so_far:.2f}")

    for i in range(max_iter_ils):
        perturbed_solution = _perturbation(best_solution_so_far['selected_items_indices'], instance_data, strength=perturbation_strength)
        
        refined_solution = vnd(perturbed_solution, instance_data)
        
        _, _, refined_objective = calculate_solution_value(refined_solution['selected_items_indices'], profits, forfeit_costs_matrix)
        
        if refined_objective > best_objective_so_far:
            best_solution_so_far = refined_solution
            best_objective_so_far = refined_objective
            print(f"   Iter {i+1}/{max_iter_ils}: Melhoria encontrada! Novo Obj = {best_objective_so_far:.2f}")

    final_weight = calculate_solution_weight(best_solution_so_far['selected_items_indices'], weights)
    final_profit, final_forfeit, final_objective = calculate_solution_value(best_solution_so_far['selected_items_indices'], profits, forfeit_costs_matrix)
    items_indices = best_solution_so_far['selected_items_indices']

    return {
        'selected_items_indices': sorted(items_indices),
        'total_weight': final_weight,
        'total_profit': final_profit,
        'total_forfeit_cost': final_forfeit,
        'objective_value': final_objective,
        'params': {'type': 'ILS_com_VND (Otimizado)'}
    }