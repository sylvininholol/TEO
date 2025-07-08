import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_grasp import penalty_aware_greedy_constructor_grasp
from local_grasp import grasp_local_search
from utilities import load_instances_from_directory, read_kpf_instance # Sua função para ler dados

# --- Parâmetros do GRASP e do Carrossel ---
MAX_ITERATIONS_GRASP = 100       # Quantas vezes o GRASP vai rodar
RCL_SIZE = 5                    # Tamanho da lista de candidatos aleatórios
ALPHA_CAROUSEL = 1.0            # Parâmetro alpha para a busca local
BETA_CAROUSEL = 0.3             # Parâmetro beta para a busca local

# --- Carregamento da Instância ---

# Mude aqui para testar outras instâncias
target_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.New Instances', 'O', '700'))
all_instances_in_O_500 = load_instances_from_directory(target_directory)

if all_instances_in_O_500:

    #Troque o valor dentro dos colchetes para alterar o arquivo acessado
    instance_to_solve_grasp = all_instances_in_O_500[1]

    print(f"\n\n--- Preparando para resolver com Carrossel Guloso ---")
    print(f"Re-lendo arquivo: {instance_to_solve_grasp['filepath']}")
    fresh_instance_data_for_grasp = read_kpf_instance(instance_to_solve_grasp['filepath'])



    print("\n" + "="*50)
    print(f"Executando a construçao do GRASP")
    print(f"Parâmetros: RCL={RCL_SIZE}")
    print("="*50  + "\n")

    start = time.time()
    grasp_builded = penalty_aware_greedy_constructor_grasp(num_items=fresh_instance_data_for_grasp['num_items'],
        capacity=fresh_instance_data_for_grasp['capacity'],
        profits=fresh_instance_data_for_grasp['profits'],
        weights=fresh_instance_data_for_grasp['weights'],
        forfeit_costs_matrix=fresh_instance_data_for_grasp['forfeit_costs_matrix'],
        rcl_size=RCL_SIZE)
    end = time.time()
    print("\n--- Contrução do GRASP finalizada! ---")

    # --- Impressão do Resultado Final ---
    if grasp_builded:
        print("\n--- Solução inicial encontrada pelo GRASP ---")
        print(f"Itens Selecionados (índices): {grasp_builded['selected_items_indices']}")
        print(f"Número de Itens Selecionados: {len(grasp_builded['selected_items_indices'])}")
        print(f"Peso Total: {grasp_builded['total_weight']} (Capacidade: {instance_to_solve_grasp['capacity']})")
        print(f"Lucro Total dos Itens: {grasp_builded['total_profit']}")
        print(f"Custo Total de Penalidades: {grasp_builded['total_forfeit_cost']}")
        print(f"VALOR OBJETIVO (Lucro - Penalidades): {grasp_builded['objective_value']:.2f}")
        print(f"Tempo decorrido: {end - start} segundos")
        print("\n" + "="*50)
    else:
        print("Nenhuma solução viável foi encontrada.")
        exit()


    print(f"Executando a busca local do GRASP")
    print(f"Parâmetros: Iterações={MAX_ITERATIONS_GRASP}, RCL={RCL_SIZE}")
    print("="*50  + "\n")

    # --- Loop Principal do GRASP (agora na main) ---
    start = time.time()

    best_grasp_solution = None
    best_grasp_objective = -sys.float_info.max

    for i in range(MAX_ITERATIONS_GRASP):
        # Executa uma única iteração de construção + busca local
        candidate_solution = grasp_local_search(
            initial_solution_indices=grasp_builded['selected_items_indices'],
            instance_data=fresh_instance_data_for_grasp,
        )
        
        # Compara a solução da iteração atual com a melhor já encontrada
        if candidate_solution['objective_value'] > best_grasp_objective:
            grasp_builded = candidate_solution
            best_grasp_objective = candidate_solution['objective_value']
            best_grasp_solution = candidate_solution
            print(f"Iteração {i+1}/{MAX_ITERATIONS_GRASP}: Melhoria encontrada! Novo Melhor Objetivo = {best_grasp_objective:.2f}")
        #else:
            #print(f"Iteração {i+1}/{MAX_ITERATIONS_GRASP}: Melhoria não encontrada! Melhor Objetivo = {best_grasp_objective:.2f}")


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
else:
    print(f"Nenhuma instância carregada do diretório '{target_directory}'. Verifique o caminho ou o conteúdo do diretório.")