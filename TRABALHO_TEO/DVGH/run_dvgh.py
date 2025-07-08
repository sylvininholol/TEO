import sys
import os
import time

# Adiciona o diretório pai ao path para encontrar a pasta 'utilities' e 'METAHEURISTICAS'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Tenta fazer as importações necessárias
try:
    from utilities import read_kpf_instance
    from dvgh import dynamic_value_greedy_heuristic_kpf
    from METAHEURISTICAS.ils import iterated_local_search_simple
    from METAHEURISTICAS.vnd import vnd
    from METAHEURISTICAS.ils_vnd import iterated_local_search_vnd
except ImportError as e:
    print(f"ERRO DE IMPORTAÇÃO: {e}")
    print("Verifique se a estrutura de pastas está correta.")
    print("A estrutura esperada é que as pastas 'utilities' e 'METAHEURISTICAS' estejam no mesmo nível que a pasta 'DVGH'.")
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
# e 'instance_reference_for_dvgh' foi completamente removida.
# --- FIM DA SEÇÃO CORRIGIDA ---

# O corpo principal do script agora usa a variável 'caminho_da_instancia'
print(f"\n\n--- Preparando para resolver com DVGH ---")
# CORREÇÃO: Usamos a variável string 'caminho_da_instancia' diretamente.
print(f"Instância (referência): {caminho_da_instancia}")
print(f"Lendo arquivo para garantir dados frescos para DVGH: {caminho_da_instancia}")
fresh_instance_data_for_dvgh = read_kpf_instance(caminho_da_instancia)

# A verificação agora é feita sobre o resultado da leitura do arquivo
if fresh_instance_data_for_dvgh:
    # CORREÇÃO: Removemos a referência a ['filepath'], pois a variável já é o caminho.
    print(f"\n--- Resolvendo instância com DVGH (dados frescos): {caminho_da_instancia} ---")
    print(f"Número de itens: {fresh_instance_data_for_dvgh['num_items']}, Capacidade: {fresh_instance_data_for_dvgh['capacity']}, Número de pares com penalidade: {fresh_instance_data_for_dvgh['num_forfeits']}")

    start = time.time()
    dvgh_solution = dynamic_value_greedy_heuristic_kpf(fresh_instance_data_for_dvgh)
    end = time.time()

    print("\n--- Solução Gerada pela Heurística DVGH ---")
    # Adicionada verificação para evitar erro caso a construção falhe
    if dvgh_solution and dvgh_solution.get('objective_value', -float('inf')) > -float('inf'):
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
        print("\n" + "="*50)
        # Se a primeira etapa falhar, encerramos para não causar mais erros.
        sys.exit(0)

    
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
    print(f"Nenhuma instância carregada do arquivo '{caminho_da_instancia}'. Verifique o caminho ou o conteúdo do diretório.")