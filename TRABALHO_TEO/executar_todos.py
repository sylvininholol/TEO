import os
import subprocess
import sys

# --- Configuração ---

# O caminho base para a pasta '.New Instances'. 
# Este caminho parece estar correto, vamos mantê-lo.
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','TRABALHO_TEO', '.New Instances', 'O'))

# Lista dos diretórios com as instâncias a serem processadas
diretorios_de_instancias = ['800']

# --- ALTERAÇÃO 1: Definir os caminhos completos dos scripts ---
# Primeiro, definimos o caminho para a pasta raiz do seu projeto (TRABALHO_TEO)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'TRABALHO_TEO'))

# Agora, criamos a lista de scripts com o caminho completo para cada um
scripts_para_rodar = [
    os.path.join(project_root, 'GRASP', 'run_grasp.py'),    
    os.path.join(project_root, 'DVGH', 'run_dvgh.py'),
    os.path.join(project_root, 'CARROSSEL', 'run_carrossel.py'),
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
        
        if not todas_as_instancias:
            print(f"--- Nenhum arquivo encontrado no diretório: {diretorio_alvo} ---")
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

            # --- INÍCIO DA CORREÇÃO PARA WINDOWS ---
            try:
                # Executa o script capturando a saída como bytes, sem especificar codificação.
                resultado = subprocess.run(
                    [sys.executable, nome_script, caminho_completo_instancia],
                    capture_output=True,
                    check=True
                )

                # Decodifica a saída (stdout) de bytes para string de forma segura,
                # substituindo caracteres que não sejam UTF-8.
                stdout_str = resultado.stdout.decode('utf-8', errors='replace')
                stderr_str = resultado.stderr.decode('utf-8', errors='replace')

                with open(caminho_arquivo_output, 'w', encoding='utf-8') as f:
                    f.write(f"--- Resultado para {os.path.basename(nome_script)} com a instância {caminho_completo_instancia} ---\n\n")
                    f.write(stdout_str)
                    if stderr_str:
                        f.write("\n--- Erros (stderr) ---\n")
                        f.write(stderr_str)
                
                print(f" -> Sucesso! Resultado salvo em: {os.path.basename(caminho_arquivo_output)}")

            except FileNotFoundError:
                print(f"ERRO: Script '{nome_script}' não encontrado. Verifique o caminho.")
                break
            except subprocess.CalledProcessError as e:
                # Se o processo falhar, a saída de erro também é decodificada de forma segura.
                stdout_str = e.stdout.decode('utf-8', errors='replace') if e.stdout else ""
                stderr_str = e.stderr.decode('utf-8', errors='replace') if e.stderr else ""

                print(f"ERRO ao executar '{os.path.basename(nome_script)}' na instância '{nome_instancia}'.")
                print(f"   -> Output de erro salvo em: {os.path.basename(caminho_arquivo_output)}")
                with open(caminho_arquivo_output, 'w', encoding='utf-8') as f:
                    f.write(f"Ocorreu um erro ao processar a instância: {caminho_completo_instancia}\n")
                    f.write(f"Comando: {' '.join(map(str, e.cmd))}\n") 
                    f.write(f"Código de Saída: {e.returncode}\n\n")
                    f.write("--- Saída Padrão (stdout) ---\n")
                    f.write(stdout_str)
                    f.write("\n--- Saída de Erro (stderr) ---\n")
                    f.write(stderr_str)
            except Exception as e:
                print(f"Um erro inesperado ocorreu: {e}")
            # --- FIM DA CORREÇÃO PARA WINDOWS ---

    print("-" * 50 + "\n")

print("Todos os scripts foram executados e os resultados foram salvos.")