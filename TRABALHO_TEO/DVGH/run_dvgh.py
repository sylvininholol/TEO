import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utilities import load_instances_from_directory, read_kpf_instance
from dvgh import dynamic_value_greedy_heuristic_kpf

target_directory = "C:/Users/gmota/Downloads/kpf_soco_instances/O/500"
# target_directory = "/home/sylvino/Faculdade/TEO/construcao_solucao_inicial/" # Testar instância

all_instances_in_O_500 = load_instances_from_directory(target_directory)

if all_instances_in_O_500:
    instance_reference_for_dvgh = all_instances_in_O_500[0]
    
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
    else:
        print("Nenhuma solução viável foi encontrada pela DVGH.")
else:
    print(f"Nenhuma instância carregada do diretório '{target_directory}'. Verifique o caminho ou o conteúdo do diretório.")
