import os
import subprocess
import sys

# --- Configuração ---

# O caminho base para a pasta '.New Instances'. 
# Este caminho parece estar correto, vamos mantê-lo.
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','TRABALHO_TEO', '.New Instances', 'O'))

# Lista dos diretórios com as instâncias a serem processadas
diretorios_de_instancias = ['500', '700', '1000']

# --- ALTERAÇÃO 1: Definir os caminhos completos dos scripts ---
# Primeiro, definimos o caminho para a pasta raiz do seu projeto (TRABALHO_TEO)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'TRABALHO_TEO'))

# Agora, criamos a lista de scripts com o caminho completo para cada um
scripts_para_rodar = [
    os.path.join(project_root, 'GRASP', 'run_grasp.py'),
    os.path.join(project_root, 'CARROSSEL', 'run_carrossel.py'),
    os.path.join(project_root, 'DVGH', 'run_dvgh.py')
]
# --- FIM DA ALTERAÇÃO 1 ---

# --- Lógica Principal ---

# Garante que um diretório para salvar os outputs exista
output_dir = os.path.join(os.path.dirname(__file__), 'resultados')
os.makedirs(output_dir, exist_ok=True)

print(f"Salvando resultados em: {output_dir}\n")

# Loop para iterar sobre cada script que deve ser executado
for nome_script in scripts_para_rodar: # 'nome_script' agora é o caminho completo
    # Loop para iterar sobre cada diretório de instância (500, 700, 1000)
    for nome_diretorio in diretorios_de_instancias:
        diretorio_alvo = os.path.join(base_path, nome_diretorio)

        if not os.path.isdir(diretorio_alvo):
            print(f"AVISO: Diretório não encontrado, pulando: {diretorio_alvo}")
            continue

        try:
            todas_as_instancias = sorted(os.listdir(diretorio_alvo))
        except FileNotFoundError:
            print(f"ERRO: Não foi possível listar arquivos em: {diretorio_alvo}")
            continue

        instancias_para_processar = todas_as_instancias[:10]
        
        # Usamos os.path.basename para mostrar apenas o nome do arquivo no print
        print(f"--- Processando Diretório: {nome_diretorio} com o Script: {os.path.basename(nome_script)} ---")

        for nome_instancia in instancias_para_processar:
            caminho_completo_instancia = os.path.join(diretorio_alvo, nome_instancia)

            # --- ALTERAÇÃO 2: Corrigir o nome do arquivo de saída ---
            # Usamos os.path.basename para pegar apenas o nome do arquivo (ex: 'run_grasp.py')
            nome_base_script = os.path.basename(nome_script) 
            nome_arquivo_output = f"output_{nome_base_script.replace('.py', '')}_{nome_diretorio}_{nome_instancia}"
            caminho_arquivo_output = os.path.join(output_dir, nome_arquivo_output)
            # --- FIM DA ALTERAÇÃO 2 ---
            
            print(f"Executando para a instância: {nome_instancia}...")

            try:
                # Agora, 'nome_script' é o caminho completo e correto, então o Python o encontrará.
                resultado = subprocess.run(
                    [sys.executable, nome_script, caminho_completo_instancia],
                    capture_output=True,
                    text=True,
                    check=True,
                    encoding='utf-8'
                )

                with open(caminho_arquivo_output, 'w', encoding='utf-8') as f:
                    f.write(f"--- Resultado para {os.path.basename(nome_script)} com a instância {caminho_completo_instancia} ---\n\n")
                    f.write(resultado.stdout)
                    if resultado.stderr:
                        f.write("\n--- Erros (stderr) ---\n")
                        f.write(resultado.stderr)
                
                print(f" -> Sucesso! Resultado salvo em: {os.path.basename(caminho_arquivo_output)}")

            except FileNotFoundError:
                # Este erro é menos provável agora, mas é bom mantê-lo
                print(f"ERRO: Script '{nome_script}' não encontrado. Verifique o caminho.")
                break
            except subprocess.CalledProcessError as e:
                print(f"ERRO ao executar '{os.path.basename(nome_script)}' na instância '{nome_instancia}'.")
                print(f"   -> Output de erro salvo em: {os.path.basename(caminho_arquivo_output)}")
                with open(caminho_arquivo_output, 'w', encoding='utf-8') as f:
                    f.write(f"Ocorreu um erro ao processar a instância: {caminho_completo_instancia}\n")
                    # O comando agora é uma lista, então usamos ' '.join para imprimi-lo de forma legível
                    f.write(f"Comando: {' '.join(e.cmd)}\n") 
                    f.write(f"Código de Saída: {e.returncode}\n\n")
                    f.write("--- Saída Padrão (stdout) ---\n")
                    f.write(e.stdout)
                    f.write("\n--- Saída de Erro (stderr) ---\n")
                    f.write(e.stderr)
            except Exception as e:
                print(f"Um erro inesperado ocorreu: {e}")
    print("-" * 50 + "\n")

print("Todos os scripts foram executados e os resultados foram salvos.")