import random
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utilities import calculate_solution_value

def grasp_kpf_construction(profits, weights, capacity, forfeit_costs_matrix, alpha):
    """
    Fase de construção de uma solução para o KPF usando uma abordagem GRASP.

    Args:
        profits (list): Lista de lucros dos itens.
        weights (list): Lista de pesos dos itens.
        capacity (int): Capacidade da mochila.
        forfeit_costs_matrix (list of lists): Matriz de custos de penalidade.
        alpha (float): Parâmetro do GRASP para controlar o tamanho da RCL (0 < alpha <= 1).

    Returns:
        tuple: (solution_indices, total_weight, total_profit, total_forfeit_cost, objective_value)
               Retorna uma tupla vazia se nenhuma solução viável for construída.
    """
    num_items = len(profits)
    current_solution_indices = []
    current_weight = 0
    
    # Itens disponíveis para seleção (índices)
    available_items = list(range(num_items))
    random.shuffle(available_items) # Embaralha para quebrar empates iniciais na métrica

    while True:
        candidates_for_rcl = []
        for item_idx in available_items:
            if current_weight + weights[item_idx] <= capacity:
                # Métrica gulosa: lucro/peso. Lidar com peso 0.
                if weights[item_idx] > 0:
                    metric = profits[item_idx] / weights[item_idx]
                elif profits[item_idx] > 0: # Peso 0, lucro positivo
                    metric = sys.float_info.max # Altamente desejável
                else: # Peso 0, lucro não positivo
                    metric = -sys.float_info.max
                candidates_for_rcl.append({'id': item_idx, 'metric': metric})
        
        if not candidates_for_rcl:
            break # Nenhum item restante cabe ou não há itens

        # Ordena candidatos pela métrica (decrescente)
        candidates_for_rcl.sort(key=lambda x: x['metric'], reverse=True)
        
        # Constrói a RCL
        # min_metric_val = candidates_for_rcl[-1]['metric'] # Métrica do pior candidato
        # max_metric_val = candidates_for_rcl[0]['metric'] # Métrica do melhor candidato
        # threshold = max_metric_val - alpha * (max_metric_val - min_metric_val)
        # rcl = [cand for cand in candidates_for_rcl if cand['metric'] >= threshold]
        
        # Alternativa mais comum para RCL: pegar uma fração dos melhores
        rcl_size = max(1, int(len(candidates_for_rcl) * alpha))
        rcl = candidates_for_rcl[:rcl_size]

        if not rcl: # Segurança, não deve acontecer se candidates_for_rcl não estiver vazio
            break

        # Seleciona aleatoriamente um item da RCL
        chosen_candidate = random.choice(rcl)
        chosen_item_idx = chosen_candidate['id']
        
        # Adiciona o item à solução
        current_solution_indices.append(chosen_item_idx)
        current_weight += weights[chosen_item_idx]
        available_items.remove(chosen_item_idx) # Remove da lista de disponíveis

    # Após construir a solução, calcula seus valores finais
    if not current_solution_indices:
        return [], 0, 0, 0, -float('inf')

    total_profit, total_forfeit_cost, objective_value = calculate_solution_value(
        current_solution_indices, profits, forfeit_costs_matrix
    )
    
    return sorted(current_solution_indices), current_weight, total_profit, total_forfeit_cost, objective_value


def run_grasp_kpf(instance_data, alpha=0.3, max_iter=50):
    """
    Executa o GRASP completo (múltiplas construções) para uma instância do KPF.

    Args:
        instance_data (dict): Dados da instância.
        alpha (float): Parâmetro alfa para a fase de construção.
        max_iter (int): Número de iterações do GRASP (construções).

    Returns:
        dict: Detalhes da melhor solução encontrada, incluindo:
              'selected_items_indices', 'total_weight', 'total_profit',
              'total_forfeit_cost', 'objective_value', 'iterations_run'.
    """
    best_solution = {
        'selected_items_indices': [],
        'total_weight': 0,
        'total_profit': 0,
        'total_forfeit_cost': 0,
        'objective_value': -float('inf'),
        'iterations_run': max_iter
    }

    profits = instance_data['profits']
    weights = instance_data['weights']
    capacity = instance_data['capacity']
    forfeit_costs_matrix = instance_data['forfeit_costs_matrix']

    for _ in range(max_iter):
        (sol_indices, weight, profit, forfeit, obj_val) = grasp_kpf_construction(
            profits, weights, capacity, forfeit_costs_matrix, alpha
        )
        
        if obj_val > best_solution['objective_value']:
            best_solution['selected_items_indices'] = sol_indices
            best_solution['total_weight'] = weight
            best_solution['total_profit'] = profit
            best_solution['total_forfeit_cost'] = forfeit
            best_solution['objective_value'] = obj_val
            
    return best_solution