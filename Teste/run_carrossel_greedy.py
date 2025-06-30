import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utilities import read_kpf_instance, load_instances_from_directory
from carrossel_greedy import penalty_aware_greedy_construction, carousel_local_search
from Teste.Heurísticas import iterated_local_search_simple, iterated_local_search_vnd

target_directory = "C:/Users/gmota/Downloads/kpf_soco_instances/O/500"
all_instances_in_O_500 = load_instances_from_directory(target_directory)

if all_instances_in_O_500:
    instance_to_solve_carousel = all_instances_in_O_500[0]

    print(f"\n\n--- Preparando para resolver com Carrossel Guloso ---")
    print(f"Re-lendo arquivo: {instance_to_solve_carousel['filepath']}")
    fresh_instance_data_for_carousel = read_kpf_instance(instance_to_solve_carousel['filepath'])
    
    print(f"\n--- Resolvendo instância com Carrossel Guloso: {fresh_instance_data_for_carousel['filepath']} ---")

    start = time.time()
    carousel_solution = penalty_aware_greedy_construction(fresh_instance_data_for_carousel)
    end = time.time()

    
    # --- Impressão dos Resultados Finais ---
    print("\n--- Solução Gerada pela Heurística Carrossel Guloso ---")
    if carousel_solution and carousel_solution['objective_value'] > -float('inf'):
        print(f"Parâmetros usados: {carousel_solution['params']['type']}")
        print(f"Itens Selecionados (índices): {carousel_solution['selected_items_indices']}")
        print(f"Número de Itens Selecionados: {len(carousel_solution['selected_items_indices'])}")
        print(f"Peso Total: {carousel_solution['total_weight']} (Capacidade: {fresh_instance_data_for_carousel['capacity']})")
        print(f"Lucro Total dos Itens: {carousel_solution['total_profit']}")
        print(f"Custo Total de Penalidades: {carousel_solution['total_forfeit_cost']}")
        print(f"VALOR OBJETIVO (Lucro - Penalidades): {carousel_solution['objective_value']}")
        print(f"Tempo decorrido: {end - start} segundos")
        print("\n" + "="*50)
    else:
        print("Nenhuma solução viável foi encontrada pelo Carrossel Guloso.")
        print("\n" + "="*50)

    
    ALPHA_CAROUSEL = 2.0  # Ex: 1.0 significa que o número de giros é o tamanho da solução gulosa inicial
    BETA_CAROUSEL = 0.8   # Ex: 20% dos itens da solução gulosa formam a elite inicial
    # Testar com 1.0 e 0.2
    # Testar com 2.0 e 0.8

    start = time.time()
    final_solution_dict  = carousel_local_search(carousel_solution['selected_items_indices'], fresh_instance_data_for_carousel, ALPHA_CAROUSEL, BETA_CAROUSEL)
    end = time.time()

    # --- Impressão dos Resultados Finais ---
    print("\n--- Resultado Final Após Busca Local ---")
    print(f"Tipo de Heurística: {final_solution_dict['params']['type']}")
    print(f"Parâmetros (alpha, beta): ({final_solution_dict['params']['alpha']}, {final_solution_dict['params']['beta']})")
    print(f"Itens Selecionados (índices): {final_solution_dict['selected_items_indices']}")
    print(f"Número de Itens Selecionados: {len(carousel_solution['selected_items_indices'])}")
    print(f"Peso Total: {final_solution_dict['total_weight']} (Capacidade: {fresh_instance_data_for_carousel['capacity']})")
    print(f"Lucro Total dos Itens: {final_solution_dict['total_profit']:.2f}")
    print(f"Custo Total de Penalidades: {final_solution_dict['total_forfeit_cost']:.2f}")
    print(f"VALOR OBJETIVO (Lucro - Penalidades): {final_solution_dict['objective_value']:.2f}")
    print(f"Tempo decorrido: {end - start} segundos")
    print("\n" + "="*50)

    
    # ------------------------------------------------------------------------------------------------------------------------------------------------
    start = time.time()
    print("Executando ILS Simples (apenas com swap 1-0)")
    print("="*50)
    result_simple = iterated_local_search_simple(fresh_instance_data_for_carousel, max_iter_ils=50, perturbation_strength=0.3)
    end = time.time()

    # --- Impressão dos Resultados Finais ---
    print("\n--- Resultado Final (ILS Simples) ---")
    print(f"Itens Selecionados: {result_simple['selected_items_indices']}")
    print(f"Valor Objetivo: {result_simple['objective_value']:.2f}")
    print(f"  (Lucro: {result_simple['total_profit']:.2f} - Penalidade: {result_simple['total_forfeit_cost']:.2f})")
    print(f"Peso Total: {result_simple['total_weight']} (Capacidade: {fresh_instance_data_for_carousel['capacity']})")
    print(f"Tempo decorrido: {end - start} segundos")
    print("\n" + "="*50)
    

    # ------------------------------------------------------------------------------------------------------------------------------------------------
    start = time.time()
    print("Executando ILS com VND (swaps 1-0, 0-1)")
    print("="*50)
    result_vnd = iterated_local_search_vnd(fresh_instance_data_for_carousel, max_iter_ils=50, perturbation_strength=0.3)
    end = time.time()

    # --- Impressão dos Resultados Finais ---
    print("\n--- Resultado Final (ILS com VND) ---")
    print(f"Itens Selecionados: {result_vnd['selected_items_indices']}")
    print(f"Valor Objetivo: {result_vnd['objective_value']:.2f}")
    print(f"  (Lucro: {result_vnd['total_profit']:.2f} - Penalidade: {result_vnd['total_forfeit_cost']:.2f})")
    print(f"Peso Total: {result_vnd['total_weight']} (Capacidade: {fresh_instance_data_for_carousel['capacity']})")
    print(f"Tempo decorrido: {end - start} segundos")
    print("\n" + "="*50)
    