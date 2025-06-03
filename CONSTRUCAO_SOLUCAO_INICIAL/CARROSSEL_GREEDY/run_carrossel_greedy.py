import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utilities import read_kpf_instance, load_instances_from_directory
from carrossel_greedy import penalty_aware_carousel_kpf
from utilities import calculate_solution_value

target_directory = "/home/sylvino/Downloads/kpf_soco_instances/O/1000"
all_instances_in_O_500 = load_instances_from_directory(target_directory)

if all_instances_in_O_500:
    instance_to_solve_carousel = all_instances_in_O_500[0] # Ou a instância desejada
    
    # "Reinicializa o arquivo" relendo-o do disco para garantir dados frescos
    print(f"\n\n--- Preparando para resolver com Carrossel Guloso ---")
    print(f"Re-lendo arquivo: {instance_to_solve_carousel['filepath']}")
    fresh_instance_data_for_carousel = read_kpf_instance(instance_to_solve_carousel['filepath'])
    
    print(f"\n--- Resolvendo instância com Carrossel Guloso: {fresh_instance_data_for_carousel['filepath']} ---")

    # Parâmetros para o Carrossel Guloso (ajuste conforme necessário)
    ALPHA_CAROUSEL = 2.0  # Ex: 1.0 significa que o número de giros é ~tamanho da solução gulosa inicial
    BETA_CAROUSEL = 0.80   # Ex: 20% dos itens da solução gulosa formam a elite inicial

    # Testar com 1.0 e 0.2
    # Testar com 2.0 e 0.8

    carousel_solution = penalty_aware_carousel_kpf(
        fresh_instance_data_for_carousel,
        ALPHA_CAROUSEL,
        BETA_CAROUSEL,
        calculate_solution_value
    )

    print("\n--- Solução Gerada pela Heurística Carrossel Guloso ---")
    if carousel_solution and carousel_solution['objective_value'] > -float('inf'):
        print(f"Itens Selecionados (índices): {carousel_solution['selected_items_indices']}")
        print(f"Número de Itens Selecionados: {len(carousel_solution['selected_items_indices'])}")
        print(f"Peso Total: {carousel_solution['total_weight']} (Capacidade: {fresh_instance_data_for_carousel['capacity']})")
        print(f"Lucro Total dos Itens: {carousel_solution['total_profit']}")
        print(f"Custo Total de Penalidades: {carousel_solution['total_forfeit_cost']}")
        print(f"VALOR OBJETIVO (Lucro - Penalidades): {carousel_solution['objective_value']}")
        print(f"Parâmetros usados: {carousel_solution['params']}")
    else:
        print("Nenhuma solução viável foi encontrada pelo Carrossel Guloso.")