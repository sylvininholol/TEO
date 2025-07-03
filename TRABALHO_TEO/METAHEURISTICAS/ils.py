from busca_local import _local_search_swap_1_0_optimized
from utilities import calculate_solution_value, calculate_solution_weight, _perturbation

def iterated_local_search_simple(initial_solution, instance_data, max_iter_ils=50, perturbation_strength=0.2):
    """
    ILS Simples: Usa apenas a busca local de remoção (swap 1-0).
    """
    profits = instance_data['profits']
    weights = instance_data['weights']
    forfeit_costs_matrix = instance_data['forfeit_costs_matrix']
    
    # 1. Gerar Solução Inicial (usando seu carrossel, se desejado, ou um construtor mais simples)
    # A solução inicial é dada por initial_solution.
    # Para o ILS, uma construção gulosa simples já é um bom ponto de partida.

    # 2. Aplicar Busca Local na solução inicial para encontrar o primeiro ótimo local
    current_solution, _ = _local_search_swap_1_0_optimized(initial_solution['selected_items_indices'], instance_data)
    
    best_solution_so_far = current_solution
    _, _, best_objective_so_far = calculate_solution_value(best_solution_so_far, profits, forfeit_costs_matrix)

    print(f"ILS Simples - Obj. Inicial: {best_objective_so_far:.2f}")

    # 3. Loop principal do ILS
    for i in range(max_iter_ils):
        # 3a. Perturbação: "Chacoalha" a solução atual para escapar do ótimo local
        perturbed_solution = _perturbation(best_solution_so_far, instance_data, strength=perturbation_strength)
        
        # 3b. Busca Local: Refina a solução perturbada
        refined_solution, _ = _local_search_swap_1_0_optimized(perturbed_solution, instance_data)
        
        # 3c. Critério de Aceitação: Compara a nova solução com a melhor já encontrada
        _, _, refined_objective = calculate_solution_value(refined_solution, profits, forfeit_costs_matrix)
        
        if refined_objective > best_objective_so_far:
            best_solution_so_far = refined_solution
            best_objective_so_far = refined_objective
            print(f"  Iter {i+1}/{max_iter_ils}: Melhoria encontrada! Novo Obj = {best_objective_so_far:.2f}")

    # Retorna o resultado final
    final_weight = calculate_solution_weight(best_solution_so_far, weights)
    final_profit, final_forfeit, final_objective = calculate_solution_value(best_solution_so_far, profits, forfeit_costs_matrix)
    
    return {
        'selected_items_indices': sorted(best_solution_so_far),
        'total_weight': final_weight,
        'total_profit': final_profit,
        'total_forfeit_cost': final_forfeit,
        'objective_value': final_objective,
        'params': {'type': 'ILS_Simple (Swap 1-0)'}
    }