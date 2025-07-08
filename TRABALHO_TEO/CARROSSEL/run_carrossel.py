import sys
import os
import time

# Adiciona o diretório pai ao path para encontrar a pasta 'utilities' e 'METAHEURISTICAS'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Tenta fazer as importações necessárias
try:
    from utilities import read_kpf_instance
    from build_carrosel import penalty_aware_greedy_construction
    from local_carrossel import carousel_local_search
    from METAHEURISTICAS.ils import iterated_local_search_simple
    from METAHEURISTICAS.vnd import vnd
    from METAHEURISTICAS.ils_vnd import iterated_local_search_vnd
except ImportError as e:
    print(f"ERRO DE IMPORTAÇÃO: {e}")
    print("Verifique se a estrutura de pastas está correta.")
    print("A estrutura esperada é que as pastas 'utilities' e 'METAHEURISTICAS' estejam no mesmo nível que a pasta 'CARROSSEL'.")
    sys.exit(1)

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
# e 'instance_to_solve_carousel' foi completamente removida.
# Agora, usamos a variável 'caminho_da_instancia' diretamente.
# --- FIM DA SEÇÃO CORRIGIDA ---

# O corpo principal do script agora usa a variável 'caminho_da_instancia'
print(f"\n\n--- Preparando para resolver com Carrossel Guloso ---")
# CORREÇÃO: Usamos a variável string 'caminho_da_instancia' diretamente.
print(f"Lendo arquivo: {caminho_da_instancia}")
fresh_instance_data_for_carousel = read_kpf_instance(caminho_da_instancia)


# A verificação agora é feita sobre o resultado da leitura do arquivo
if fresh_instance_data_for_carousel:
    start = time.time()
    print("\n" + "="*50)
    print("Executando a Construção do Carrossel Guloso")
    print("="*50)
    carousel_solution = penalty_aware_greedy_construction(fresh_instance_data_for_carousel)
    end = time.time()

    # --- Impressão dos Resultados Finais ---
    print("\n--- Solução Gerada pela Construção do Carrossel Guloso ---")
    # Adicionada verificação para evitar erro caso a construção falhe
    if carousel_solution and carousel_solution.get('objective_value', -float('inf')) > -float('inf'):
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
        # Se a primeira etapa falhar, encerramos para não causar mais erros.
        sys.exit(0)

    
    ALPHA_CAROUSEL = 2.0
    BETA_CAROUSEL = 0.8

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
    print(f"Número de Itens Selecionados: {len(final_solution_dict['selected_items_indices'])}") # Corrigido para usar a solução mais recente
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
    print(f"Nenhuma instância carregada do arquivo '{caminho_da_instancia}'. Verifique o caminho ou o conteúdo do arquivo.")