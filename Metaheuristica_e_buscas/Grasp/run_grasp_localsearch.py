# Na sua main.py

import sys
import os
import time


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Supondo que o código acima esteja em 'grasp_kpf.py'
from Metaheuristica_e_buscas.Grasp.grasp import run_single_grasp_iteration
from Construcao.utilities import load_instances_from_directory, read_kpf_instance # Sua função para ler dados

# --- Parâmetros do GRASP e do Carrossel ---
MAX_ITERATIONS_GRASP = 50       # Quantas vezes o GRASP vai rodar
RCL_SIZE = 5                    # Tamanho da lista de candidatos aleatórios
ALPHA_CAROUSEL = 1.0            # Parâmetro alpha para a busca local
BETA_CAROUSEL = 0.3             # Parâmetro beta para a busca local

# --- Carregamento da Instância ---

target_directory = "C:/Users/gmota/Downloads/kpf_soco_instances/O/500"
all_instances_in_O_500 = load_instances_from_directory(target_directory)

if all_instances_in_O_500:
    instance_to_solve_grasp = all_instances_in_O_500[0]

    print(f"\n\n--- Preparando para resolver com Carrossel Guloso ---")
    print(f"Re-lendo arquivo: {instance_to_solve_grasp['filepath']}")
    fresh_instance_data_for_grasp = read_kpf_instance(instance_to_solve_grasp['filepath'])


    print("\n" + "="*50)
    print(f"Executando GRASP com Carrossel")
    print(f"Parâmetros: Iterações={MAX_ITERATIONS_GRASP}, RCL={RCL_SIZE}, Alpha={ALPHA_CAROUSEL}, Beta={BETA_CAROUSEL}")
    print("="*50  + "\n")

    # --- Loop Principal do GRASP (agora na main) ---
    start = time.time()

    best_grasp_solution = None
    best_grasp_objective = -sys.float_info.max

    for i in range(MAX_ITERATIONS_GRASP):
        # Executa uma única iteração de construção + busca local
        candidate_solution = run_single_grasp_iteration(
            instance_data=fresh_instance_data_for_grasp,
            rcl_size=RCL_SIZE,
            alpha=ALPHA_CAROUSEL,
            beta=BETA_CAROUSEL
        )
        
        # Compara a solução da iteração atual com a melhor já encontrada
        if candidate_solution['objective_value'] > best_grasp_objective:
            best_grasp_objective = candidate_solution['objective_value']
            best_grasp_solution = candidate_solution
            print(f"Iteração {i+1}/{MAX_ITERATIONS_GRASP}: Melhoria encontrada! Novo Melhor Objetivo = {best_grasp_objective:.2f}")

    end = time.time()
    print("\n--- GRASP finalizado! ---")

    # --- Impressão do Resultado Final ---
    if best_grasp_solution:
        print("\n--- Melhor Solução Encontrada pelo GRASP ---")
        print(f"Itens Selecionados (índices): {best_grasp_solution['selected_items_indices']}")
        print(f"Número de Itens Selecionados: {len(best_grasp_solution['selected_items_indices'])}")
        print(f"Peso Total: {best_grasp_solution['total_weight']} (Capacidade: {instance_to_solve_grasp['capacity']})")
        print(f"Lucro Total dos Itens: {best_grasp_solution['total_profit']}")
        print(f"Custo Total de Penalidades: {best_grasp_solution['total_forfeit_cost']}")
        print(f"VALOR OBJETIVO (Lucro - Penalidades): {best_grasp_solution['objective_value']:.2f}")
        print(f"Tempo decorrido: {end - start} segundos")
        print("="*50  + "\n")
    else:
        print("Nenhuma solução viável foi encontrada.")