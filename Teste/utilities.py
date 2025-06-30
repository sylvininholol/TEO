import os

def read_kpf_instance(filepath):
    """
    Lê um arquivo de instância do Problema da Mochila com Penalidades (KPF).

    Args:
        filepath (str): O caminho para o arquivo da instância.

    Returns:
        dict: Um dicionário contendo os dados da instância:
            'num_items' (int): Número de itens (nI).
            'num_forfeits' (int): Número de pares com penalidade (nP).
            'capacity' (int): Capacidade da mochila (kS).
            'profits' (list): Lista de lucros dos itens.
            'weights' (list): Lista de pesos dos itens.
            'forfeit_costs_matrix' (list of lists): Matriz de custos de penalidade (nI x nI).
            'filepath': Caminho do arquivo lido.
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Linha 1: nI, nP, kS
    nI, nP, kS = map(int, lines[0].strip().split())

    # Linha 2: lucros dos itens
    item_profits = list(map(int, lines[1].strip().split()))

    # Linha 3: pesos dos itens
    item_weights = list(map(int, lines[2].strip().split()))

    # Matriz de custos de penalidade (inicializada com zeros)
    forfeit_costs_matrix = [[0] * nI for _ in range(nI)]

    line_idx = 3
    for _ in range(nP):
        # Linha: nA_i fC_i nI_i (e.g., "1 100 2")
        # nA_i é sempre 1, nI_i é sempre 2, conforme a descrição do README.
        parts = lines[line_idx].strip().split()
        fC_i = int(parts[1])  # Custo da penalidade
        line_idx += 1

        # Linha: id_0_0 id_0_1 (e.g., "item_idx1 item_idx2")
        # Os IDs são 0-indexed.
        id1, id2 = map(int, lines[line_idx].strip().split())
        line_idx += 1

        # Armazena o custo da penalidade na matriz
        # A penalidade fC_i aplica-se se ambos id1 e id2 estiverem na solução.
        forfeit_costs_matrix[id1][id2] = fC_i
        forfeit_costs_matrix[id2][id1] = fC_i # A matriz é simétrica

    return {
        'num_items': nI,
        'num_forfeits': nP,
        'capacity': kS,
        'profits': item_profits,
        'weights': item_weights,
        'forfeit_costs_matrix': forfeit_costs_matrix,
        'filepath': filepath
    }

def load_instances_from_directory(directory_path):
    """
    Carrega todas as instâncias de um diretório especificado.

    Args:
        directory_path (str): O caminho para o diretório contendo os arquivos de instância.

    Returns:
        list: Uma lista de dicionários, onde cada dicionário representa uma instância lida.
    """
    instances = []
    if not os.path.isdir(directory_path):
        print(f"Erro: Diretório não encontrado em '{directory_path}'")
        return instances

    print(f"Lendo instâncias do diretório: {directory_path}")
    for filename in os.listdir(directory_path):
        # Você pode adicionar um filtro aqui se houver outros tipos de arquivo no diretório
        # Por exemplo, if filename.endswith(".dat"):
        filepath = os.path.join(directory_path, filename)
        if os.path.isfile(filepath):
            try:
                instance_data = read_kpf_instance(filepath)
                instances.append(instance_data)
                print(f"  Lida instância: {filename}")
            except Exception as e:
                print(f"  Erro ao ler o arquivo {filename}: {e}")
    return instances

def print_forfeit_pairs(instance_data):
    """
    Imprime os pares de itens que têm um custo de penalidade associado.

    Args:
        instance_data (dict): Dicionário com os dados da instância,
                               contendo 'num_items' e 'forfeit_costs_matrix'.
    """
    num_items = instance_data['num_items']
    forfeit_costs_matrix = instance_data['forfeit_costs_matrix']
    
    print("\n--- Conjuntos de Penalidade (Pares e Custos) ---")
    found_penalties = False
    # Iteramos pela matriz triangular superior para evitar duplicatas (já que a matriz é simétrica)
    # e para evitar pares de um item com ele mesmo (que não devem ter penalidade).
    for i in range(num_items):
        for j in range(i + 1, num_items): # Começa de i + 1 para pegar apenas pares (i, j) onde i < j
            cost = forfeit_costs_matrix[i][j]
            if cost > 0:
                print(f"  Item {i}, Item {j} = {cost}")
                found_penalties = True
    
    if not found_penalties:
        print("  Nenhum par com penalidade encontrado nesta instância.")

def calculate_solution_value(solution_indices, profits, forfeit_costs_matrix):
    """Calcula o lucro total, custo de penalidade e valor objetivo de uma solução."""
    current_profit = sum(profits[i] for i in solution_indices)
    
    current_forfeit_cost = 0
    # Itera sobre pares únicos na solução para somar penalidades
    for i in range(len(solution_indices)):
        for j in range(i + 1, len(solution_indices)):
            idx1 = solution_indices[i]
            idx2 = solution_indices[j]
            current_forfeit_cost += forfeit_costs_matrix[idx1][idx2]
            
    objective_value = current_profit - current_forfeit_cost
    return current_profit, current_forfeit_cost, objective_value