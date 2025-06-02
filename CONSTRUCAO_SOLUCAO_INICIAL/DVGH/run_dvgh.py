import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utilities import read_kpf_instance, load_instances_from_directory
from dvgh import dynamic_value_greedy_heuristic_kpf

# 1. Definir o caminho do diretório e carregar todas as instâncias
target_directory = "/home/sylvino/Downloads/kpf_soco_instances/O/500" # Use seu caminho real
all_instances_in_O_500 = load_instances_from_directory(target_directory)

# Verifica se alguma instância foi carregada
if all_instances_in_O_500:
    # Exemplo: Processar a primeira instância da lista
    # Você pode iterar sobre `all_instances_in_O_500` para processar cada uma.
    instance_reference_for_dvgh = all_instances_in_O_500[0]
    
    # --- Execução da DVGH com "reinicialização do arquivo" ---
    print(f"\n\n--- Preparando para resolver com DVGH ---")
    print(f"Instância original (referência): {instance_reference_for_dvgh['filepath']}")

    # "Reinicializa o arquivo" relendo-o do disco para garantir dados frescos para esta execução da DVGH
    print(f"Re-lendo arquivo para garantir dados frescos para DVGH: {instance_reference_for_dvgh['filepath']}")
    fresh_instance_data_for_dvgh = read_kpf_instance(instance_reference_for_dvgh['filepath'])
    
    print(f"\n--- Resolvendo instância com DVGH (dados frescos): {fresh_instance_data_for_dvgh['filepath']} ---")
    print(f"Número de itens: {fresh_instance_data_for_dvgh['num_items']}, Capacidade: {fresh_instance_data_for_dvgh['capacity']}")

    # Opcional: Imprimir os pares de penalidade da instância (agora usando os dados frescos)
    # print_forfeit_pairs(fresh_instance_data_for_dvgh)

    # 2. Executar a DVGH na instância com dados frescos
    dvgh_solution = dynamic_value_greedy_heuristic_kpf(fresh_instance_data_for_dvgh)

    # 3. Apresentar a solução gerada pela DVGH e suas métricas
    print("\n--- Solução Gerada pela Heurística DVGH ---")
    if dvgh_solution and dvgh_solution['objective_value'] > -float('inf'): # Verifica se uma solução válida foi retornada
        print(f"Itens Selecionados (índices): {dvgh_solution['selected_items_indices']}")
        print(f"Número de Itens Selecionados: {len(dvgh_solution['selected_items_indices'])}")
        print(f"Peso Total: {dvgh_solution['total_weight']} (Capacidade: {fresh_instance_data_for_dvgh['capacity']})")
        print(f"Lucro Total dos Itens: {dvgh_solution['total_profit']}")
        print(f"Custo Total de Penalidades: {dvgh_solution['total_forfeit_cost']}")
        print(f"VALOR OBJETIVO (Lucro - Penalidades): {dvgh_solution['objective_value']}")
    else:
        print("Nenhuma solução viável foi encontrada pela DVGH.")
else:
    print(f"Nenhuma instância carregada do diretório '{target_directory}'. Verifique o caminho ou o conteúdo do diretório.")
