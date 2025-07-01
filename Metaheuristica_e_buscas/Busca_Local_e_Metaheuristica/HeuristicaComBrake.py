import random
import sys
import collections
import itertools

# Importe a função de cálculo original para uso inicial e final, mas não dentro dos loops
from Construcao.utilities import calculate_solution_value
# Supondo que as funções do carrossel estão no mesmo nível ou no sys.path
from carrossel_greedy import penalty_aware_greedy_constructor, select_best_penalized_item_to_add

# ----------------------------------------------------------------------------------
# NOVA FUNÇÃO HELPER PARA CÁLCULO DE PENALIDADE
# ----------------------------------------------------------------------------------
def _calculate_item_penalty_with_solution(item_idx, solution_set, forfeit_costs_matrix):
    """
    Calcula o custo de penalidade total que um item 'item_idx' teria com
    todos os itens em 'solution_set'.
    Complexidade: O(s), onde s = len(solution_set)
    """
    penalty = 0
    # Este loop garante que somamos a penalidade para cada par único {item_idx, sol_item}
    for sol_item in solution_set:
        # Para garantir que acessemos a matriz da mesma forma que calculate_solution_value,
        # podemos usar min/max ou simplesmente somar ambas as direções se a matriz for simétrica.
        # A forma mais robusta que replica a lógica de pares únicos é:
        pair_penalty = forfeit_costs_matrix[min(item_idx, sol_item)][max(item_idx, sol_item)]
        penalty += pair_penalty
    return penalty

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
        
        # Melhoria = Ganhos - Perdas
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

# A função de swap 2-1 ainda será muito custosa, mas a otimização ajuda.
# A complexidade ainda é alta, então use-a com cautela.
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
        # Precisamos adicionar a penalidade entre r1 e r2 que também foi removida
        penalty_between_r1_r2 = forfeit_costs_matrix[min(r1, r2)][max(r1, r2)]
        
        total_penalty_gain = penalty_gain_out_r1 + penalty_gain_out_r2 + penalty_between_r1_r2
        
        for item_in in range(num_items):
            if item_in not in solution_set:
                if temp_weight + weights[item_in] <= capacity:
                    # Efeito da adição de 'item_in'
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

# Em _local_search_swap_2_1_optimized

def _local_search_swap_2_1_optimized_first_improvement(current_solution_indices, instance_data):
    
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
    
    # Flag para quebrar os laços externos
    found_improvement = False 

    for r1, r2 in itertools.combinations(current_solution_indices, 2):
        temp_weight = current_weight - weights[r1] - weights[r2]
        
        # Efeito da remoção de r1 e r2
        profit_loss_out = profits[r1] + profits[r2]
        
        temp_solution_set = solution_set - {r1, r2}
        penalty_gain_out_r1 = _calculate_item_penalty_with_solution(r1, temp_solution_set, forfeit_costs_matrix)
        penalty_gain_out_r2 = _calculate_item_penalty_with_solution(r2, temp_solution_set, forfeit_costs_matrix)
        # Precisamos adicionar a penalidade entre r1 e r2 que também foi removida
        penalty_between_r1_r2 = forfeit_costs_matrix[min(r1, r2)][max(r1, r2)]
        
        total_penalty_gain = penalty_gain_out_r1 + penalty_gain_out_r2 + penalty_between_r1_r2
        
        for item_in in range(num_items):
            if item_in not in solution_set:
                if temp_weight + weights[item_in] <= capacity:
                    # Efeito da adição de 'item_in'
                    profit_gain_in = profits[item_in]
                    penalty_loss_in = _calculate_item_penalty_with_solution(item_in, temp_solution_set, forfeit_costs_matrix)
                    
                    improvement = (profit_gain_in - penalty_loss_in) + (total_penalty_gain - profit_loss_out)

                    if improvement > best_improvement:
                        # ENCONTRAMOS UMA MELHORIA, NÃO PRECISAMOS PROCURAR MAIS!
                        # Aplicamos o movimento e saímos.
                        final_solution = [item for item in current_solution_indices if item != r1 and item != r2] + [item_in]
                        return final_solution, True # Retorna imediatamente

    # Se o loop terminar sem encontrar melhoria, retorna a solução original
    return current_solution_indices, False

# ----------------------------------------------------------------------------------
# FUNÇÕES PRINCIPAIS (ILS, VND) ATUALIZADAS PARA USAR AS VERSÕES OTIMIZADAS
# ----------------------------------------------------------------------------------

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

    # 2. Aplicar Busca Local na solução inicial para encontrar o primeiro ótimo local
    current_solution, _ = _local_search_swap_1_0_optimized(current_solution, instance_data)
    
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

def local_search_vnd(solution_indices, instance_data):
    """
    Variable Neighborhood Descent (VND) que agora usa as funções otimizadas.
    """
    neighborhoods = [
        _local_search_swap_1_0_optimized,
        _local_search_swap_0_1_optimized,
        _local_search_swap_1_1_optimized,
        _local_search_swap_2_1_optimized_first_improvement,  # Considere remover esta linha para testes mais rápidos
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

def iterated_local_search_vnd(instance_data, max_iter_ils=50, perturbation_strength=0.3):
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
    
    current_solution = penalty_aware_greedy_constructor(
        instance_data['num_items'], instance_data['capacity'], profits, weights, forfeit_costs_matrix
    )

    current_solution = local_search_vnd(current_solution, instance_data)
    
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

# A função _perturbation e o ILS Simples podem ser mantidas como estavam,
# mas o ILS Simples também pode ser atualizado para usar a busca local otimizada.
# O código original para elas não foi incluído aqui para focar na otimização do VND.