# grasp_kpf.py (ou o nome que preferir)

import random
import sys
import os


from Metaheuristica_e_buscas.Busca_Local_e_Metaheuristica.carrossel_greedy import _calculate_penalized_metric
from Construcao.utilities import calculate_solution_value
from Metaheuristica_e_buscas.Busca_Local_e_Metaheuristica.Heuristicas import (
    _local_search_swap_1_0_optimized,
    _local_search_swap_0_1_optimized,
    _local_search_swap_1_1_optimized,
    _local_search_swap_2_1_optimized,
    calculate_solution_weight
)

def penalty_aware_greedy_constructor_grasp(num_items, capacity, profits, weights,
                                           forfeit_costs_matrix, rcl_size=3):
    """
    Construtor guloso com lista restrita de candidatos (RCL) para o GRASP.
    A cada passo, escolhe aleatoriamente um dos 'rcl_size' melhores candidatos.
    Retorna uma lista de índices de itens.
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
                # Considera apenas candidatos com contribuição não-negativa
                if metric >= 0:
                    candidates.append((metric, item_idx))

        # Se não há mais candidatos viáveis, encerra a construção
        if not candidates:
            break

        # Ordena os candidatos pela métrica (melhor para o pior)
        candidates.sort(key=lambda x: x[0], reverse=True)
        
        # Define a Lista de Candidatos Restrita (RCL)
        rcl = candidates[:rcl_size]

        # Se a RCL estiver vazia (nenhum candidato bom), encerra
        if not rcl:
            break

        # Escolhe aleatoriamente um candidato da RCL
        _, chosen_item = random.choice(rcl)
        
        # Adiciona o item escolhido à solução
        solution_indices.append(chosen_item)
        current_weight += weights[chosen_item]
        available_items.remove(chosen_item)

    return solution_indices


def run_single_grasp_iteration(instance_data, rcl_size, alpha, beta):
    """
    Executa UMA iteração completa do GRASP:
    1. Fase de Construção: Cria uma solução gulosa-randomizada.
    2. Fase de Busca Local: Refina a solução construída com o Carrossel.
    
    Args:
        instance_data (dict): Dicionário com os dados do problema.
        rcl_size (int): Tamanho da lista de candidatos restrita para a construção.
        alpha (float): Parâmetro alpha para o carousel_local_search.
        beta (float): Parâmetro beta para o carousel_local_search.

    Returns:
        dict: O dicionário da solução refinada encontrado nesta iteração.
    """
    # --- 1. FASE DE CONSTRUÇÃO ---
    # Cria uma solução inicial usando o construtor GRASP (com aleatoriedade)
    constructed_solution = penalty_aware_greedy_constructor_grasp(
        num_items=instance_data['num_items'],
        capacity=instance_data['capacity'],
        profits=instance_data['profits'],
        weights=instance_data['weights'],
        forfeit_costs_matrix=instance_data['forfeit_costs_matrix'],
        rcl_size=rcl_size
    )
    
    # Se a construção não gerar solução, retorna um resultado vazio
    if not constructed_solution:
        return {
            'selected_items_indices': [], 'total_weight': 0,
            'total_profit': 0, 'total_forfeit_cost': 0,
            'objective_value': -sys.float_info.max,
            'params': {}
        }

    # --- 2. FASE DE BUSCA LOCAL ---
    refined_solution_dict = grasp_local_search(
        initial_solution_indices=constructed_solution,
        instance_data=instance_data
    )
        
    return refined_solution_dict

def grasp_local_search(initial_solution_indices, instance_data):
    """
    Busca local padrão do GRASP usando VND otimizado.

    Args:
        initial_solution_indices (list): Solução construída pela fase GRASP.
        instance_data (dict): Dados do problema.

    Returns:
        dict: Solução refinada no formato completo com lucros, penalidades e objetivo.
    """
    # Usa o VND como estratégia de busca local padrão
    neighborhoods = [
        _local_search_swap_1_0_optimized,
        # _local_search_swap_0_1_optimized,
        # _local_search_swap_1_1_optimized,
        # _local_search_swap_2_1_optimized, 
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
