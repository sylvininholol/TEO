import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utilities import load_instances_from_directory, read_kpf_instance
from dvgh import dynamic_value_greedy_heuristic_kpf
from METAHEURISTICAS.ils import iterated_local_search_simple
from METAHEURISTICAS.vnd import vnd
from METAHEURISTICAS.ils_vnd import iterated_local_search_vnd

target_directory = "C:/Users/gmota/Downloads/kpf_soco_instances/O/700"
# target_directory = "/home/sylvino/Faculdade/TEO/construcao_solucao_inicial/" # Testar instância

all_instances_in_O_500 = load_instances_from_directory(target_directory)

if all_instances_in_O_500:
    instance_reference_for_dvgh = all_instances_in_O_500[7]
    
    print(f"\n\n--- Preparando para resolver com DVGH ---")
    print(f"Instância original (referência): {instance_reference_for_dvgh['filepath']}")

    print(f"Re-lendo arquivo para garantir dados frescos para DVGH: {instance_reference_for_dvgh['filepath']}")
    fresh_instance_data_for_dvgh = read_kpf_instance(instance_reference_for_dvgh['filepath'])
    
    print(f"\n--- Resolvendo instância com DVGH (dados frescos): {fresh_instance_data_for_dvgh['filepath']} ---")
    print(f"Número de itens: {fresh_instance_data_for_dvgh['num_items']}, Capacidade: {fresh_instance_data_for_dvgh['capacity']}, Número de pares com penalidade: {fresh_instance_data_for_dvgh['num_forfeits']}")

    # print_forfeit_pairs(fresh_instance_data_for_dvgh)

    start = time.time()
    dvgh_solution = dynamic_value_greedy_heuristic_kpf(fresh_instance_data_for_dvgh)
    end = time.time()

    print("\n--- Solução Gerada pela Heurística DVGH ---")
    if dvgh_solution and dvgh_solution['objective_value'] > -float('inf'): # Verifica se uma solução válida foi retornada
        print(f"Itens Selecionados (índices): {dvgh_solution['selected_items_indices']}")
        print(f"Número de Itens Selecionados: {len(dvgh_solution['selected_items_indices'])}")
        print(f"Peso Total: {dvgh_solution['total_weight']} (Capacidade: {fresh_instance_data_for_dvgh['capacity']})")
        print(f"Lucro Total dos Itens: {dvgh_solution['total_profit']}")
        print(f"Custo Total de Penalidades: {dvgh_solution['total_forfeit_cost']}")
        print(f"VALOR OBJETIVO (Lucro - Penalidades): {dvgh_solution['objective_value']}")
        print(f"Tempo decorrido: {end - start} segundos")
        print("\n" + "="*50)
    else:
        print("Nenhuma solução viável foi encontrada pela DVGH.")

    
    # ------------------------------------------------------------------------------------------------------------------------------------------------
    start = time.time()
    print("Executando ILS Simples (apenas com swap 1-0)")
    print("="*50)
    result_simple = iterated_local_search_simple(dvgh_solution, fresh_instance_data_for_dvgh, max_iter_ils=100, perturbation_strength=0.3)
    end = time.time()

    # --- Impressão dos Resultados Finais ---
    print("\n--- Resultado Final (ILS Simples) ---")
    print(f"Itens Selecionados (índices): {result_simple['selected_items_indices']}")
    print(f"Número de Itens Selecionados: {len(result_simple['selected_items_indices'])}")
    print(f"Peso Total: {result_simple['total_weight']} (Capacidade: {fresh_instance_data_for_dvgh['capacity']})")
    print(f"Lucro Total dos Itens: {result_simple['total_profit']:.2f}")
    print(f"Custo Total de Penalidades: {result_simple['total_forfeit_cost']:.2f}")
    print(f"VALOR OBJETIVO (Lucro - Penalidades): {result_simple['objective_value']:.2f}")
    print(f"Tempo decorrido: {end - start} segundos")
    print("\n" + "="*50)


    # ------------------------------------------------------------------------------------------------------------------------------------------------
    start = time.time()
    print("Executando o VND (swaps 1-0, 0-1, 1-1, 2-1)")
    print("="*50)
    result_vnd = vnd(dvgh_solution['selected_items_indices'], fresh_instance_data_for_dvgh)
    end = time.time()

    # --- Impressão dos Resultados Finais ---
    print("\n--- Resultado Final (VND) ---")
    print(f"Itens Selecionados (índices): {result_vnd['selected_items_indices']}")
    print(f"Número de Itens Selecionados: {len(result_vnd['selected_items_indices'])}")
    print(f"Peso Total: {result_vnd['total_weight']} (Capacidade: {fresh_instance_data_for_dvgh['capacity']})")
    print(f"Lucro Total dos Itens: {result_vnd['total_profit']:.2f}")
    print(f"Custo Total de Penalidades: {result_vnd['total_forfeit_cost']:.2f}")
    print(f"VALOR OBJETIVO (Lucro - Penalidades): {result_vnd['objective_value']:.2f}")
    print(f"Tempo decorrido: {end - start} segundos")
    print("\n" + "="*50)
    

    # ------------------------------------------------------------------------------------------------------------------------------------------------
    start = time.time()
    print("Executando ILS com VND (swaps 1-0, 0-1, 1-1, 2-1)")
    print("="*50)
    result_ils_vnd = iterated_local_search_vnd(dvgh_solution, fresh_instance_data_for_dvgh, max_iter_ils=100, perturbation_strength=0.3)
    end = time.time()

    # --- Impressão dos Resultados Finais ---
    print("\n--- Resultado Final (ILS com VND) ---")
    print(f"Itens Selecionados (índices): {result_ils_vnd['selected_items_indices']}")
    print(f"Número de Itens Selecionados: {len(result_ils_vnd['selected_items_indices'])}")
    print(f"Peso Total: {result_ils_vnd['total_weight']} (Capacidade: {fresh_instance_data_for_dvgh['capacity']})")
    print(f"Lucro Total dos Itens: {result_ils_vnd['total_profit']:.2f}")
    print(f"Custo Total de Penalidades: {result_ils_vnd['total_forfeit_cost']:.2f}")
    print(f"VALOR OBJETIVO (Lucro - Penalidades): {result_ils_vnd['objective_value']:.2f}")
    print(f"Tempo decorrido: {end - start} segundos")
    print("\n" + "="*50)    
else:
    print(f"Nenhuma instância carregada do diretório '{target_directory}'. Verifique o caminho ou o conteúdo do diretório.")
