import sys
import os
# Dynamic Value Greedy Heuristic
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utilities import calculate_solution_value

def dynamic_value_greedy_heuristic_kpf(instance_data):
    """
    Implementa a Heurística Gulosa com Avaliação Dinâmica de Penalidades (DVGH)
    para o Problema da Mochila com Penalidades (KPF).

    Args:
        instance_data (dict): Dicionário com os dados da instância.

    Returns:
        dict: Um dicionário contendo a solução encontrada:
            'selected_items_indices' (list): Lista dos índices dos itens selecionados.
            'total_weight' (int): Peso total dos itens selecionados.
            'total_profit' (int): Lucro total dos itens selecionados.
            'total_forfeit_cost' (int): Custo total das penalidades incorridas.
            'objective_value' (int): Valor da função objetivo (lucro - penalidades).
    """
    num_items = instance_data['num_items']
    profits = instance_data['profits']
    weights = instance_data['weights']
    capacity = instance_data['capacity']
    forfeit_costs_matrix = instance_data['forfeit_costs_matrix']

    current_solution_indices = []
    current_weight = 0
    
    # Inicialmente, todos os itens são candidatos (usamos uma cópia para poder remover)
    candidate_item_indices = list(range(num_items)) 

    while True:
        best_item_to_add_idx = -1 
        max_evaluation_metric = -sys.float_info.max # Métrica do melhor item a ser adicionado

        for item_idx in candidate_item_indices:
            item_profit_val = profits[item_idx]
            item_weight_val = weights[item_idx]

            if current_weight + item_weight_val <= capacity:
                # Calcula o custo adicional de penalidades se este item for adicionado
                additional_forfeit_if_added = 0
                for selected_idx_in_solution in current_solution_indices:
                    additional_forfeit_if_added += forfeit_costs_matrix[item_idx][selected_idx_in_solution]
                
                # Lucro líquido imediato ao adicionar este item
                net_gain = item_profit_val - additional_forfeit_if_added
                
                current_metric = 0.0
                if item_weight_val > 0:
                    current_metric = net_gain / item_weight_val
                else: # item_weight_val == 0
                    if net_gain > 0:
                        current_metric = sys.float_info.max # Muito desejável
                    elif net_gain == 0:
                        current_metric = 0.0 # Neutro
                    else: # net_gain < 0
                        current_metric = -sys.float_info.max # Muito indesejável
                
                if current_metric > max_evaluation_metric:
                    max_evaluation_metric = current_metric
                    best_item_to_add_idx = item_idx
        
        # Condição de parada:
        # - Nenhum item foi selecionado (best_item_to_add_idx permaneceu -1),
        #   ou seja, ou não há mais candidatos, ou nenhum candidato cabe.
        # - A melhor métrica encontrada não é estritamente positiva.
        #   Adicionar um item apenas se ele trouxer um "ganho por unidade de peso" positivo.
        if best_item_to_add_idx != -1 and max_evaluation_metric > 0:
            current_solution_indices.append(best_item_to_add_idx)
            current_weight += weights[best_item_to_add_idx]
            candidate_item_indices.remove(best_item_to_add_idx) # Remove para não considerar novamente
        else:
            break # Termina a construção
            
    # Calcula os valores finais da solução construída
    if not current_solution_indices: # Nenhuma solução construída
        return {
            'selected_items_indices': [], 'total_weight': 0,
            'total_profit': 0, 'total_forfeit_cost': 0,
            'objective_value': -float('inf') # Ou 0, dependendo da preferência para solução vazia
        }

    total_profit, total_forfeit_cost, objective_value = calculate_solution_value(
        current_solution_indices, profits, forfeit_costs_matrix
    )
    
    return {
        'selected_items_indices': sorted(current_solution_indices), # Retorna ordenado para consistência
        'total_weight': current_weight,
        'total_profit': total_profit,
        'total_forfeit_cost': total_forfeit_cost,
        'objective_value': objective_value
    }