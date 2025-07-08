import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utilities import read_kpf_instance, load_instances_from_directory
from build_carrosel import penalty_aware_greedy_construction
from local_carrossel import carousel_local_search
from METAHEURISTICAS.ils import iterated_local_search_simple
from METAHEURISTICAS.vnd import vnd
from METAHEURISTICAS.ils_vnd import iterated_local_search_vnd
#from HeuristicaComBrake import iterated_local_search_simple,iterated_local_search_vnd

target_directory = "C:/Users/gmota/Downloads/kpf_soco_instances/O/500"
all_instances_in_O_500 = load_instances_from_directory(target_directory)

if all_instances_in_O_500:
    instance_to_solve_carousel = all_instances_in_O_500[9]

    print(f"\n\n--- Preparando para resolver com Carrossel Guloso ---")
    print(f"Re-lendo arquivo: {instance_to_solve_carousel['filepath']}")
    fresh_instance_data_for_carousel = read_kpf_instance(instance_to_solve_carousel['filepath'])

    start = time.time()
    print("\n" + "="*50)
    print("Executando a Construção do Carrossel Guloso")
    print("="*50)
    carousel_solution = penalty_aware_greedy_construction(fresh_instance_data_for_carousel)
    end = time.time()

    
    # --- Impressão dos Resultados Finais ---
    print("\n--- Solução Gerada pela Construção do Carrossel Guloso ---")
    if carousel_solution and carousel_solution['objective_value'] > -float('inf'):
        print(f"Parâmetros usados: {carousel_solution['params']['type']}")
        print(f"Itens Selecionados (índices): {carousel_solution['selected_items_indices']}")
        print(f"Número de Itens Selecionados: {len(carousel_solution['selected_items_indices'])}")
        print(f"Peso Total: {carousel_solution['total_weight']} (Capacidade: {fresh_instance_data_for_carousel['capacity']})")
        print(f"Lucro Total dos Itens: {carousel_solution['total_profit']}")
        print(f"Custo Total de Penalidades: {carousel_solution['total_forfeit_cost']}")
        print(f"VALOR OBJETIVO (Lucro - Penalidades): {carousel_solution['objective_value']:.2f}")
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
    print("Executando a Busca Local do Carrossel Guloso")
    print("="*50)
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
    print("Executando o ILS Simples (apenas com swap 1-0)")
    print("="*50)
    result_simple = iterated_local_search_simple(carousel_solution, fresh_instance_data_for_carousel, max_iter_ils=100, perturbation_strength=0.3)
    end = time.time()

    # --- Impressão dos Resultados Finais ---
    print("\n--- Resultado Final (ILS Simples) ---")
    print(f"Itens Selecionados (índices): {result_simple['selected_items_indices']}")
    print(f"Número de Itens Selecionados: {len(result_simple['selected_items_indices'])}")
    print(f"Peso Total: {result_simple['total_weight']} (Capacidade: {fresh_instance_data_for_carousel['capacity']})")
    print(f"Lucro Total dos Itens: {result_simple['total_profit']:.2f}")
    print(f"Custo Total de Penalidades: {result_simple['total_forfeit_cost']:.2f}")
    print(f"VALOR OBJETIVO (Lucro - Penalidades): {result_simple['objective_value']:.2f}")
    print(f"Tempo decorrido: {end - start} segundos")
    print("\n" + "="*50)
    
# ------------------------------------------------------------------------------------------------------------------------------------------------
    start = time.time()
    print("Executando o VND (swaps 1-0, 0-1, 1-1, 2-1)")
    print("="*50)
    result_vnd = vnd(carousel_solution['selected_items_indices'], fresh_instance_data_for_carousel)
    end = time.time()

    # --- Impressão dos Resultados Finais ---
    print("\n--- Resultado Final (VND) ---")
    print(f"Itens Selecionados (índices): {result_vnd['selected_items_indices']}")
    print(f"Número de Itens Selecionados: {len(result_vnd['selected_items_indices'])}")
    print(f"Peso Total: {result_vnd['total_weight']} (Capacidade: {fresh_instance_data_for_carousel['capacity']})")
    print(f"Lucro Total dos Itens: {result_vnd['total_profit']:.2f}")
    print(f"Custo Total de Penalidades: {result_vnd['total_forfeit_cost']:.2f}")
    print(f"VALOR OBJETIVO (Lucro - Penalidades): {result_vnd['objective_value']:.2f}")
    print(f"Tempo decorrido: {end - start} segundos")
    print("\n" + "="*50)

    # ------------------------------------------------------------------------------------------------------------------------------------------------
    start = time.time()
    print("Executando o ILS com VND (swaps 1-0, 0-1, 1-1, 2-1)")
    print("="*50)
    result_ils_vnd = iterated_local_search_vnd(carousel_solution, fresh_instance_data_for_carousel, max_iter_ils=100, perturbation_strength=0.3)
    end = time.time()

    # --- Impressão dos Resultados Finais ---
    print("\n--- Resultado Final (ILS com VND) ---")
    print(f"Itens Selecionados (índices): {result_ils_vnd['selected_items_indices']}")
    print(f"Número de Itens Selecionados: {len(result_ils_vnd['selected_items_indices'])}")
    print(f"Peso Total: {result_ils_vnd['total_weight']} (Capacidade: {fresh_instance_data_for_carousel['capacity']})")
    print(f"Lucro Total dos Itens: {result_ils_vnd['total_profit']:.2f}")
    print(f"Custo Total de Penalidades: {result_ils_vnd['total_forfeit_cost']:.2f}")
    print(f"VALOR OBJETIVO (Lucro - Penalidades): {result_ils_vnd['objective_value']:.2f}")
    print(f"Tempo decorrido: {end - start} segundos")
    print("\n" + "="*50)
else:
    print(f"Nenhuma instância carregada do diretório '{target_directory}'. Verifique o caminho ou o conteúdo do diretório.")