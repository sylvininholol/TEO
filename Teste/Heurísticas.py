import random
import sys
import collections
import itertools

from carrossel_greedy import penalty_aware_greedy_constructor, select_best_penalized_item_to_add
from utilities import calculate_solution_value

def calculate_solution_weight(solution_indices, weights):
    """Calcula o peso total de uma solução."""
    return sum(weights[i] for i in solution_indices)

def _perturbation(solution_indices, instance_data, strength=0.2):
    """
    Perturbação (Destruir e Reconstruir): Remove uma porcentagem de itens
    aleatoriamente e depois reconstrói a solução de forma gulosa.
    """
    if not solution_indices:
        return []

    num_to_remove = int(len(solution_indices) * strength)
    if num_to_remove == 0:
        num_to_remove = 1 # Garante que pelo menos um item seja removido

    # Destruir: remove 'num_to_remove' itens aleatórios
    items_to_remove = set(random.sample(solution_indices, k=min(num_to_remove, len(solution_indices))))
    perturbed_solution = [item for item in solution_indices if item not in items_to_remove]
    
    current_weight = calculate_solution_weight(perturbed_solution, instance_data['weights'])
    
    # Reconstruir: adiciona os melhores itens possíveis com o espaço disponível
    available_for_fill = set(range(instance_data['num_items'])) - set(perturbed_solution)

    while True:
        best_item_to_add = select_best_penalized_item_to_add(
            available_for_fill, perturbed_solution,
            current_weight, instance_data['capacity'],
            instance_data['profits'], instance_data['weights'], instance_data['forfeit_costs_matrix']
        )
        if best_item_to_add is not None:
            perturbed_solution.append(best_item_to_add)
            current_weight += instance_data['weights'][best_item_to_add]
            available_for_fill.remove(best_item_to_add)
        else:
            break
            
    return perturbed_solution

def _local_search_swap_1_0(current_solution_indices, instance_data):
    """
    Busca Local (Remoção 1-0): Tenta remover cada item da solução.
    Aplica a melhor melhoria (best improvement).
    Retorna (nova_solucao, melhorou_ou_nao).
    """
    num_items = instance_data['num_items']
    profits = instance_data['profits']
    weights = instance_data['weights']
    forfeit_costs_matrix = instance_data['forfeit_costs_matrix']

    best_improvement = 0
    best_move = None
    
    _, _, current_objective = calculate_solution_value(current_solution_indices, profits, forfeit_costs_matrix)

    # Tenta remover cada item
    for item_to_remove in current_solution_indices:
        neighbor_solution = [item for item in current_solution_indices if item != item_to_remove]
        _, _, neighbor_objective = calculate_solution_value(neighbor_solution, profits, forfeit_costs_matrix)
        
        improvement = neighbor_objective - current_objective
        if improvement > best_improvement:
            best_improvement = improvement
            best_move = item_to_remove

    if best_move is not None:
        final_solution = [item for item in current_solution_indices if item != best_move]
        return final_solution, True

    return current_solution_indices, False

def _local_search_swap_0_1(current_solution_indices, instance_data):
    """
    Busca Local (Adição 0-1): Tenta adicionar um item que está fora da solução.
    Aplica a melhor melhoria (best improvement).
    Retorna (nova_solucao, melhorou_ou_nao).
    """
    # ... (implementação similar ao swap 1-0, mas adicionando itens)
    num_items = instance_data['num_items']
    profits = instance_data['profits']
    weights = instance_data['weights']
    capacity = instance_data['capacity']
    forfeit_costs_matrix = instance_data['forfeit_costs_matrix']

    best_improvement = 0
    best_move = None
    
    current_weight = calculate_solution_weight(current_solution_indices, weights)
    _, _, current_objective = calculate_solution_value(current_solution_indices, profits, forfeit_costs_matrix)
    
    solution_set = set(current_solution_indices)
    
    # Tenta adicionar cada item que não está na solução
    for item_to_add in range(num_items):
        if item_to_add not in solution_set:
            if current_weight + weights[item_to_add] <= capacity:
                neighbor_solution = current_solution_indices + [item_to_add]
                _, _, neighbor_objective = calculate_solution_value(neighbor_solution, profits, forfeit_costs_matrix)
                
                improvement = neighbor_objective - current_objective
                if improvement > best_improvement:
                    best_improvement = improvement
                    best_move = item_to_add
    
    if best_move is not None:
        final_solution = current_solution_indices + [best_move]
        return final_solution, True
        
    return current_solution_indices, False

def _local_search_swap_1_1(current_solution_indices, instance_data):
    """
    Busca Local (Troca 1-1): Tenta trocar um item da solução por um de fora.
    Aplica a melhor melhoria (best improvement).
    Retorna (nova_solucao, melhorou_ou_nao).
    """
    # ... (implementação da troca)
    num_items = instance_data['num_items']
    profits = instance_data['profits']
    weights = instance_data['weights']
    capacity = instance_data['capacity']
    forfeit_costs_matrix = instance_data['forfeit_costs_matrix']

    best_improvement = 0
    best_move = (None, None) # (item_to_remove, item_to_add)
    
    current_weight = calculate_solution_weight(current_solution_indices, weights)
    _, _, current_objective = calculate_solution_value(current_solution_indices, profits, forfeit_costs_matrix)
    
    solution_set = set(current_solution_indices)

    for item_to_remove in current_solution_indices:
        temp_weight = current_weight - weights[item_to_remove]
        for item_to_add in range(num_items):
            if item_to_add not in solution_set:
                if temp_weight + weights[item_to_add] <= capacity:
                    # Cria a solução vizinha para avaliação
                    neighbor_solution = [item for item in current_solution_indices if item != item_to_remove] + [item_to_add]
                    _, _, neighbor_objective = calculate_solution_value(neighbor_solution, profits, forfeit_costs_matrix)
                    
                    improvement = neighbor_objective - current_objective
                    if improvement > best_improvement:
                        best_improvement = improvement
                        best_move = (item_to_remove, item_to_add)

    if best_move[0] is not None:
        item_out, item_in = best_move
        final_solution = [item for item in current_solution_indices if item != item_out] + [item_in]
        return final_solution, True

    return current_solution_indices, False

def _local_search_swap_2_1(current_solution_indices, instance_data):
    """
    Busca Local (Troca 2-1): Tenta remover dois itens da solução e adicionar um de fora.
    Aplica a melhor melhoria (best improvement).
    Retorna (nova_solucao, melhorou_ou_nao).
    """
    num_items = instance_data['num_items']
    profits = instance_data['profits']
    weights = instance_data['weights']
    capacity = instance_data['capacity']
    forfeit_costs_matrix = instance_data['forfeit_costs_matrix']

    best_improvement = 0
    # (item_removido_1, item_removido_2, item_adicionado)
    best_move = (None, None, None)

    # Valores base para evitar recálculos
    current_weight = calculate_solution_weight(current_solution_indices, weights)
    _, _, current_objective = calculate_solution_value(current_solution_indices, profits, forfeit_costs_matrix)
    
    solution_set = set(current_solution_indices)
    
    # Se a solução tiver menos de 2 itens, o swap 2-1 não é possível
    if len(current_solution_indices) < 2:
        return current_solution_indices, False

    # Itera sobre todas as combinações de 2 itens para remover da solução
    for item_to_remove_1, item_to_remove_2 in itertools.combinations(current_solution_indices, 2):
        
        # Calcula o peso após a remoção dos dois itens
        temp_weight = current_weight - weights[item_to_remove_1] - weights[item_to_remove_2]
        
        # Itera sobre todos os itens possíveis para adicionar
        for item_to_add in range(num_items):
            # Considera apenas itens que não estão na solução atual
            if item_to_add not in solution_set:
                
                # Verifica a restrição de capacidade
                if temp_weight + weights[item_to_add] <= capacity:
                    # Constrói a solução vizinha para avaliação
                    # Começa com os itens que não foram removidos
                    temp_solution = [item for item in current_solution_indices if item != item_to_remove_1 and item != item_to_remove_2]
                    # Adiciona o novo item
                    neighbor_solution = temp_solution + [item_to_add]
                    
                    _, _, neighbor_objective = calculate_solution_value(neighbor_solution, profits, forfeit_costs_matrix)
                    
                    improvement = neighbor_objective - current_objective
                    if improvement > best_improvement:
                        best_improvement = improvement
                        best_move = (item_to_remove_1, item_to_remove_2, item_to_add)

    # Se um movimento de melhoria foi encontrado, aplica-o
    if best_move[2] is not None:
        r1, r2, a1 = best_move
        
        # Constrói a solução final a partir do melhor movimento
        final_solution = [item for item in current_solution_indices if item != r1 and item != r2]
        final_solution.append(a1)
        
        return final_solution, True

    # Se nenhuma melhoria foi encontrada, retorna a solução original
    return current_solution_indices, False

def iterated_local_search_simple(instance_data, max_iter_ils=50, perturbation_strength=0.2):
    """
    ILS Simples: Usa apenas a busca local de remoção (swap 1-0).
    """
    profits = instance_data['profits']
    weights = instance_data['weights']
    forfeit_costs_matrix = instance_data['forfeit_costs_matrix']
    
    # 1. Gerar Solução Inicial (usando seu carrossel, se desejado, ou um construtor mais simples)
    #    Para o ILS, uma construção gulosa simples já é um bom ponto de partida.
    current_solution = penalty_aware_greedy_constructor(
        instance_data['num_items'], instance_data['capacity'], profits, weights, forfeit_costs_matrix
    )

    best_solution_so_far1 = current_solution
    _, _, best_objective_so_far1 = calculate_solution_value(best_solution_so_far1, profits, forfeit_costs_matrix)
    print(best_objective_so_far1)

    # 2. Aplicar Busca Local na solução inicial para encontrar o primeiro ótimo local
    current_solution, _ = _local_search_swap_1_0(current_solution, instance_data)
    
    best_solution_so_far = current_solution
    _, _, best_objective_so_far = calculate_solution_value(best_solution_so_far, profits, forfeit_costs_matrix)

    print(f"ILS Simples - Obj. Inicial: {best_objective_so_far:.2f}")

    # 3. Loop principal do ILS
    for i in range(max_iter_ils):
        # 3a. Perturbação: "Chacoalha" a solução atual para escapar do ótimo local
        perturbed_solution = _perturbation(best_solution_so_far, instance_data, strength=perturbation_strength)
        
        # 3b. Busca Local: Refina a solução perturbada
        refined_solution, _ = _local_search_swap_1_0(perturbed_solution, instance_data)
        
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


def local_search_vnd(solution_indices, instance_data):
    """
    Variable Neighborhood Descent (VND): Aplica uma sequência de buscas locais.
    Retorna para a primeira vizinhança sempre que uma melhoria é encontrada.
    """
    # Define a ordem das buscas locais a serem exploradas
    neighborhoods = [
        _local_search_swap_1_0,
        _local_search_swap_0_1,
        _local_search_swap_1_1,
        _local_search_swap_2_1,
    ]
    
    current_solution = solution_indices
    k = 0 # Índice da vizinhança atual
    while k < len(neighborhoods):
        # Explora a vizinhança k
        new_solution, improved = neighborhoods[k](current_solution, instance_data)
        
        if improved:
            current_solution = new_solution
            k = 0 # Volta para a primeira vizinhança (estratégia básica do VND)
        else:
            k += 1 # Vai para a próxima vizinhança
            
    return current_solution


def iterated_local_search_vnd(instance_data, max_iter_ils=50, perturbation_strength=0.2):
    """
    ILS com VND: Usa o VND como procedimento de busca local.
    """
    profits = instance_data['profits']
    weights = instance_data['weights']
    forfeit_costs_matrix = instance_data['forfeit_costs_matrix']
    
    # 1. Gerar Solução Inicial
    current_solution = penalty_aware_greedy_constructor(
        instance_data['num_items'], instance_data['capacity'], profits, weights, forfeit_costs_matrix
    )

    best_solution_so_far1 = current_solution
    _, _, best_objective_so_far1 = calculate_solution_value(best_solution_so_far1, profits, forfeit_costs_matrix)
    print(best_objective_so_far1)

    # 2. Aplicar VND na solução inicial para encontrar o primeiro ótimo local
    current_solution = local_search_vnd(current_solution, instance_data)
    
    best_solution_so_far = current_solution
    _, _, best_objective_so_far = calculate_solution_value(best_solution_so_far, profits, forfeit_costs_matrix)
    
    print(f"ILS com VND - Obj. Inicial: {best_objective_so_far:.2f}")

    # 3. Loop principal do ILS
    for i in range(max_iter_ils):
        # 3a. Perturbação
        perturbed_solution = _perturbation(best_solution_so_far, instance_data, strength=perturbation_strength)
        
        # 3b. Busca Local (VND)
        refined_solution = local_search_vnd(perturbed_solution, instance_data)
        
        # 3c. Critério de Aceitação
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
        'params': {'type': 'ILS_com_VND'}
    }