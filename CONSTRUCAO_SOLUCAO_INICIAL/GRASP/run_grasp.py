import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utilities import load_instances_from_directory
from grasp import run_grasp_kpf
# --- Início do Script Principal ---

# 1. Definir o caminho do diretório e carregar instâncias

target_directory = "/home/sylvino/Downloads/kpf_soco_instances/O/500"
all_instances_in_O_500 = load_instances_from_directory(target_directory)

if all_instances_in_O_500:
    # Seleciona a primeira instância carregada para o exemplo
    # Você pode iterar sobre 'all_instances_in_O_500' para processar todas
    instance_to_solve = all_instances_in_O_500[0] 
    
    print(f"\n--- Resolvendo instância: {instance_to_solve['filepath']} ---")
    print(f"Número de itens: {instance_to_solve['num_items']}, Capacidade: {instance_to_solve['capacity']}")

    # 2. Executar o GRASP na instância selecionada
    # Parâmetros do GRASP (podem ser ajustados)
    ALPHA_GRASP = 0.3  # Entre 0 e 1. Mais próximo de 0 = mais guloso; Mais próximo de 1 = mais aleatório.
    MAX_ITER_GRASP = 50 # Número de construções GRASP

    # Opcional: Imprimir os pares de penalidade da instância (agora usando os dados frescos)
    # print_forfeit_pairs(instance_to_solve)

    best_grasp_solution = run_grasp_kpf(instance_to_solve, alpha=ALPHA_GRASP, max_iter=MAX_ITER_GRASP)

    # 3. Apresentar a solução inicial gerada pelo GRASP e suas métricas
    print("\n--- Melhor Solução Inicial Gerada pelo GRASP ---")
    if best_grasp_solution and best_grasp_solution['objective_value'] > -float('inf'):
        print(f"Itens Selecionados (índices): {best_grasp_solution['selected_items_indices']}")
        print(f"Número de Itens Selecionados: {len(best_grasp_solution['selected_items_indices'])}")
        print(f"Peso Total: {best_grasp_solution['total_weight']} (Capacidade: {instance_to_solve['capacity']})")
        print(f"Lucro Total dos Itens: {best_grasp_solution['total_profit']}")
        print(f"Custo Total de Penalidades: {best_grasp_solution['total_forfeit_cost']}")
        print(f"VALOR OBJETIVO (Lucro - Penalidades): {best_grasp_solution['objective_value']}")
        print(f"Iterações GRASP executadas: {best_grasp_solution['iterations_run']}")
    else:
        print("Nenhuma solução viável foi encontrada pelo GRASP.")
else:
    print(f"Nenhuma instância carregada do diretório {target_directory}. Verifique o caminho.")

# Itens Selecionados: A lista dos índices dos itens que compõem a solução. Isso define a própria solução.
# Ex: [0, 5, 12, 23, ...]
# Peso Total: A soma dos pesos dos itens selecionados. Crucial para verificar a viabilidade (deve ser ≤ capacidade da mochila).
# Lucro Total dos Itens: A soma dos lucros dos itens selecionados (antes de subtrair as penalidades).
# Custo Total de Penalidades: A soma das penalidades incorridas devido aos pares de itens selecionados que possuem uma taxa de penalidade associada.
# Valor da Função Objetivo: Esta é a métrica principal que o GRASP (e qualquer heurística de otimização para este problema) tenta maximizar. É calculada como: Lucro Total dos Itens - Custo Total de Penalidades.