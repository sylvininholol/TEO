import random
import os

def generate_kpf_instance_content(
    num_items,
    num_forfeit_pairs,
    knapsack_capacity,
    profit_range=(5, 25),
    weight_range=(1, 25),
    forfeit_cost_range=(1, 15)
):
    """
    Gera o conteúdo de um arquivo de instância para o Problema da Mochila com Penalidades (KPF).

    Args:
        num_items (int): Número de itens (nI).
        num_forfeit_pairs (int): Número de pares com penalidade (nP).
        knapsack_capacity (int): Capacidade da mochila (kS).
        profit_range (tuple): (min_profit, max_profit) para os itens.
        weight_range (tuple): (min_weight, max_weight) para os itens.
                               É garantido que os pesos serão >= 1.
        forfeit_cost_range (tuple): (min_cost, max_cost) para as penalidades.

    Returns:
        str: Uma string formatada representando o conteúdo do arquivo da instância.
             Retorna None se os parâmetros de entrada forem inválidos.
    """

    if not (isinstance(num_items, int) and num_items >= 0):
        print("Erro: Número de itens (num_items) deve ser um inteiro não-negativo.")
        return None
    if not (isinstance(num_forfeit_pairs, int) and num_forfeit_pairs >= 0):
        print("Erro: Número de pares de penalidade (num_forfeit_pairs) deve ser um inteiro não-negativo.")
        return None
    if not (isinstance(knapsack_capacity, int) and knapsack_capacity >= 0):
        print("Erro: Capacidade da mochila (knapsack_capacity) deve ser um inteiro não-negativo.")
        return None
    
    if num_items < 2 and num_forfeit_pairs > 0:
        print(f"Erro: Não é possível gerar {num_forfeit_pairs} pares de penalidade com menos de 2 itens. "
              f"Definindo num_forfeit_pairs para 0.")
        num_forfeit_pairs = 0

    profits = [random.randint(profit_range[0], profit_range[1]) for _ in range(num_items)]

    weights = [max(1, random.randint(weight_range[0], weight_range[1])) for _ in range(num_items)]

    max_possible_pairs = 0
    if num_items >= 2:
        max_possible_pairs = num_items * (num_items - 1) // 2
    
    actual_num_forfeit_pairs = min(num_forfeit_pairs, max_possible_pairs)
    if num_forfeit_pairs > max_possible_pairs:
        print(f"Aviso: O número solicitado de pares de penalidade ({num_forfeit_pairs}) excede o máximo "
              f"possível ({max_possible_pairs}) para {num_items} itens. "
              f"Limitando a {max_possible_pairs} pares.")

    generated_pairs_set = set()
    forfeit_pairs_details = []

    while len(generated_pairs_set) < actual_num_forfeit_pairs:
        id1 = random.randint(0, num_items - 1)
        id2 = random.randint(0, num_items - 1)
        
        if id1 == id2:
            continue
        
        pair = tuple(sorted((id1, id2)))
        
        if pair not in generated_pairs_set:
            generated_pairs_set.add(pair)
            cost = random.randint(forfeit_cost_range[0], forfeit_cost_range[1])
            forfeit_pairs_details.append({'id1': pair[0], 'id2': pair[1], 'cost': cost})

    output_lines = []
    
    output_lines.append(f"{num_items} {actual_num_forfeit_pairs} {knapsack_capacity}")
    
    output_lines.append(" ".join(map(str, profits)))
    
    output_lines.append(" ".join(map(str, weights)))
    
    for detail in forfeit_pairs_details:
        output_lines.append(f"1 {detail['cost']} 2")

        output_lines.append(f"{detail['id1']} {detail['id2']}")
        
    return "\n".join(output_lines)

if __name__ == "__main__":
    nI_desejado = 500
    nP_desejado = 100
    kS_desejado = 750

    conteudo_instancia = generate_kpf_instance_content(
        nI_desejado,
        nP_desejado,
        kS_desejado
    )

    if conteudo_instancia:
        print("\n--- Conteúdo da Instância Gerada ---")
        print(conteudo_instancia)
        print("-----------------------------------\n")

        nome_arquivo = f"TRABALHO_TEO/.New Instances/KPF_n{nI_desejado}_p{nP_desejado}_c{kS_desejado}.txt"
        os.makedirs("TRABALHO_TEO/.New Instances", exist_ok=True)
        try:
            with open(nome_arquivo, 'w') as f:
                f.write(conteudo_instancia)
            print(f"Instância salva em: {nome_arquivo}")
        except IOError as e:
            print(f"Erro ao salvar o arquivo {nome_arquivo}: {e}")

    conteudo_instancia_pequena = generate_kpf_instance_content(5, 7, 50)
    if conteudo_instancia_pequena:
        print("\n--- Conteúdo da Instância Pequena Gerada ---")
        print(conteudo_instancia_pequena)
        print("-----------------------------------------\n")

    conteudo_instancia_muitos_pares = generate_kpf_instance_content(4, 10, 50)
    if conteudo_instancia_muitos_pares:
        print("\n--- Conteúdo da Instância com Tentativa de Muitos Pares ---")
        print(conteudo_instancia_muitos_pares)
        print("---------------------------------------------------------\n")