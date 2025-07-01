import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utilities import read_kpf_instance, load_instances_from_directory
from carrossel_greedy import penalty_aware_carousel_kpf
from utilities import calculate_solution_value

target_directory = "C:/Users/gmota/Downloads/kpf_soco_instances/O/500"
all_instances_in_O_500 = load_instances_from_directory(target_directory)

if all_instances_in_O_500:
    instance_to_solve_carousel = all_instances_in_O_500[0]

    print(f"\n\n--- Preparando para resolver com Carrossel Guloso ---")
    print(f"Re-lendo arquivo: {instance_to_solve_carousel['filepath']}")
    fresh_instance_data_for_carousel = read_kpf_instance(instance_to_solve_carousel['filepath'])
    
    print(f"\n--- Resolvendo instância com Carrossel Guloso: {fresh_instance_data_for_carousel['filepath']} ---")

    ALPHA_CAROUSEL = 2.0  # Ex: 1.0 significa que o número de giros é o tamanho da solução gulosa inicial
    BETA_CAROUSEL = 0.8   # Ex: 20% dos itens da solução gulosa formam a elite inicial

    # Testar com 1.0 e 0.2
    # Testar com 2.0 e 0.8

    start = time.time()
    carousel_solution = penalty_aware_carousel_kpf(
        fresh_instance_data_for_carousel,
        ALPHA_CAROUSEL,
        BETA_CAROUSEL,
        calculate_solution_value
    )
    end = time.time()

    print("\n--- Solução Gerada pela Heurística Carrossel Guloso ---")
    if carousel_solution and carousel_solution['objective_value'] > -float('inf'):
        print(f"Itens Selecionados (índices): {carousel_solution['selected_items_indices']}")
        print(f"Número de Itens Selecionados: {len(carousel_solution['selected_items_indices'])}")
        print(f"Peso Total: {carousel_solution['total_weight']} (Capacidade: {fresh_instance_data_for_carousel['capacity']})")
        print(f"Lucro Total dos Itens: {carousel_solution['total_profit']}")
        print(f"Custo Total de Penalidades: {carousel_solution['total_forfeit_cost']}")
        print(f"VALOR OBJETIVO (Lucro - Penalidades): {carousel_solution['objective_value']}")
        print(f"Parâmetros usados: {carousel_solution['params']}")
        print(f"Tempo decorrido: {end - start} segundos")
    else:
        print("Nenhuma solução viável foi encontrada pelo Carrossel Guloso.")