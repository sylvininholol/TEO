import sys
import os
import time

# Adiciona o diretório pai ao path para encontrar a pasta 'utilities' e outras
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Tenta fazer as importações necessárias
try:
    from build_grasp import penalty_aware_greedy_constructor_grasp
    from local_grasp import grasp_local_search
    from utilities import read_kpf_instance
except ImportError as e:
    print(f"ERRO DE IMPORTAÇÃO: {e}")
    print("Verifique se a estrutura de pastas está correta.")
    print("A estrutura esperada é que a pasta 'utilities' esteja no mesmo nível que a pasta 'GRASP'.")
    sys.exit(1)


# --- Parâmetros do GRASP ---
MAX_ITERATIONS_GRASP = 100
RCL_SIZE = 5

# --- INÍCIO DA SEÇÃO CORRIGIDA ---
# Removemos a lógica antiga e a substituímos por uma que lê o argumento da linha de comando.

# 1. Verifica se o caminho do arquivo foi passado como argumento
if len(sys.argv) < 2:
    print("Erro: Forneça o caminho para o arquivo da instância como um argumento.")
    print(f"Uso: python {sys.argv[0]} /caminho/para/arquivo.txt")
    sys.exit(1)

# 2. Pega o caminho do arquivo do argumento (sys.argv[1])
caminho_da_instancia = sys.argv[1]

# 3. Verifica se o arquivo realmente existe
if not os.path.isfile(caminho_da_instancia):
    print(f"Erro: Arquivo de instância não foi encontrado em: {caminho_da_instancia}")
    sys.exit(1)

# A lógica antiga que definia 'target_directory', 'all_instances_in_O_500',
# e 'instance_to_solve_grasp' foi completamente removida.
# --- FIM DA SEÇÃO CORRIGIDA ---


# O corpo principal do script agora usa a variável 'caminho_da_instancia'
print(f"\n\n--- Preparando para resolver com GRASP ---")
# CORREÇÃO: Usamos a variável string 'caminho_da_instancia' diretamente.
print(f"Lendo arquivo: {caminho_da_instancia}")
fresh_instance_data_for_grasp = read_kpf_instance(caminho_da_instancia)

# A verificação agora é feita sobre o resultado da leitura do arquivo
if fresh_instance_data_for_grasp:
    print("\n" + "="*50)
    print(f"Executando a construção do GRASP")
    print(f"Parâmetros: RCL={RCL_SIZE}")
    print("="*50  + "\n")

    start = time.time()
    grasp_builded = penalty_aware_greedy_constructor_grasp(
        num_items=fresh_instance_data_for_grasp['num_items'],
        capacity=fresh_instance_data_for_grasp['capacity'],
        profits=fresh_instance_data_for_grasp['profits'],
        weights=fresh_instance_data_for_grasp['weights'],
        forfeit_costs_matrix=fresh_instance_data_for_grasp['forfeit_costs_matrix'],
        rcl_size=RCL_SIZE
    )
    end = time.time()
    print("\n--- Construção do GRASP finalizada! ---")

    # --- Impressão do Resultado Final ---
    if grasp_builded and grasp_builded.get('objective_value', -float('inf')) > -float('inf'):
        print("\n--- Solução inicial encontrada pelo GRASP ---")
        print(f"Itens Selecionados (índices): {grasp_builded['selected_items_indices']}")
        print(f"Número de Itens Selecionados: {len(grasp_builded['selected_items_indices'])}")
        # CORREÇÃO: Usamos os dados lidos da instância, não a variável antiga
        print(f"Peso Total: {grasp_builded['total_weight']} (Capacidade: {fresh_instance_data_for_grasp['capacity']})")
        print(f"Lucro Total dos Itens: {grasp_builded['total_profit']}")
        print(f"Custo Total de Penalidades: {grasp_builded['total_forfeit_cost']}")
        print(f"VALOR OBJETIVO (Lucro - Penalidades): {grasp_builded['objective_value']:.2f}")
        print(f"Tempo decorrido: {end - start} segundos")
        print("\n" + "="*50)
    else:
        print("Nenhuma solução viável foi encontrada pela construção GRASP.")
        # Se a primeira etapa falhar, encerramos para não causar mais erros.
        sys.exit(0)


    print(f"Executando a busca local do GRASP")
    print(f"Parâmetros: Iterações={MAX_ITERATIONS_GRASP}, RCL={RCL_SIZE}")
    print("="*50  + "\n")

    # --- Loop Principal do GRASP ---
    start = time.time()

    best_grasp_solution = grasp_builded  # Inicia com a solução da construção
    best_grasp_objective = grasp_builded['objective_value']

    for i in range(MAX_ITERATIONS_GRASP):
        # Executa uma única iteração de construção + busca local
        candidate_solution = grasp_local_search(
            initial_solution_indices=best_grasp_solution['selected_items_indices'],
            instance_data=fresh_instance_data_for_grasp,
        )
        
        # Compara a solução da iteração atual com a melhor já encontrada
        if candidate_solution and candidate_solution['objective_value'] > best_grasp_objective:
            best_grasp_solution = candidate_solution
            best_grasp_objective = candidate_solution['objective_value']
            print(f"Iteração {i+1}/{MAX_ITERATIONS_GRASP}: Melhoria encontrada! Novo Melhor Objetivo = {best_grasp_objective:.2f}")

    end = time.time()
    print("\n--- GRASP finalizado! ---")

    # --- Impressão do Resultado Final ---
    if best_grasp_solution:
        print("\n--- Melhor Solução Encontrada pelo GRASP ---")
        print(f"Itens Selecionados (índices): {best_grasp_solution['selected_items_indices']}")
        print(f"Número de Itens Selecionados: {len(best_grasp_solution['selected_items_indices'])}")
        # CORREÇÃO: Usamos os dados lidos da instância, não a variável antiga
        print(f"Peso Total: {best_grasp_solution['total_weight']} (Capacidade: {fresh_instance_data_for_grasp['capacity']})")
        print(f"Lucro Total dos Itens: {best_grasp_solution['total_profit']}")
        print(f"Custo Total de Penalidades: {best_grasp_solution['total_forfeit_cost']}")
        print(f"VALOR OBJETIVO (Lucro - Penalidades): {best_grasp_solution['objective_value']:.2f}")
        print(f"Tempo decorrido: {end - start} segundos")
        print("="*50  + "\n")
    else:
        print("Nenhuma solução viável foi encontrada.")
else:
    print(f"Nenhuma instância carregada do arquivo '{caminho_da_instancia}'. Verifique o caminho ou o conteúdo do diretório.")