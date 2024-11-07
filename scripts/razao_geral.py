import pandas as pd
import os
import tkinter as tk
from tkinter import messagebox, filedialog
from connection import connect_database
import queries
from openpyxl import Workbook

# Conectando ao banco de dados
conexão = connect_database()

# Função para encerrar o programa
def fechar_aplicacao():
    bloco_ações.quit()
    bloco_ações.destroy()
    exit()

# Escolher o caminho do arquivo para salvamento
def escolher_caminho_arquivo():
    tk.Tk().withdraw()  # Oculta a janela principal do tkinter
    caminho_arquivo = filedialog.askdirectory(title="Escolha o local de salvamento do arquivo")
    return caminho_arquivo

# Função para realizar a consulta com os parâmetros fornecidos
def realizar_consulta():

    try:
        início = entrada_inicio.get()
        fim = entrada_fim.get()
        identif_cliente = entrada_cliente.get()

        if ',' not in identif_cliente and not identif_cliente.isnumeric():
            
            identif_cliente = '%' + identif_cliente + '%'

            cursor_cliente = conexão.cursor()
            try:
                cursor_cliente.execute(queries.obter_cliente, (identif_cliente))
                resultados = cursor_cliente.fetchall()
                print(resultados)
                
                colunasResultados = [colRes[0] for colRes in cursor_cliente.description]
                códigosObtidos = pd.DataFrame.from_records(resultados, columns=colunasResultados)
                cliente = [f'{codigo}' for codigo in list(códigosObtidos['codi_emp'])]

                adicionaVariáveis = ', '.join('?' for código in cliente)

            except Exception as erroBusca:
                messagebox.showinfo("Erro", f"{str(erroBusca)}")
            finally:
                cursor_cliente.close()
        else:
            cliente = entrada_cliente.get()

        numConta = entrada_numConta.get()  # Obtendo o número da conta (opcional)

        # Verifica se a conta está preenchida
        if numConta == "":
            tipoConta = str(entrada_tipoConta.get()) + '%'  # Obtendo o tipo de conta
            parâmetros = (*cliente, início, fim, tipoConta, *cliente, início, fim, tipoConta)
            consulta = queries.razão_geral.replace("IN (?)", f"IN ({adicionaVariáveis})")
        else:
            parâmetros = (*cliente, início, fim, numConta, *cliente, início, fim, numConta)
            consulta = queries.razão_básico.replace("IN (?)", f"IN ({adicionaVariáveis})")

        # Consulta de saldo
        cursorSaldo = conexão.cursor()

        try:
            if numConta == "":
                consulta_saldo = queries.obter_saldo_tipoconta.replace("IN (?)", f"IN ({adicionaVariáveis})")
                cursorSaldo.execute(consulta_saldo, (*cliente, início, tipoConta, *cliente, início, tipoConta))
            else:
                consulta_saldo = queries.obter_saldo.replace("IN (?)", f"IN ({adicionaVariáveis})")
                cursorSaldo.execute(consulta_saldo, (*cliente, início, numConta, *cliente, início, numConta))

            linhaSaldo = cursorSaldo.fetchone()
            if linhaSaldo:
                saldo = linhaSaldo[0]
                if saldo == None:
                    saldo = 0
                    print(saldo)
                else:
                    print("Saldo não obtido")

        except Exception as error:
            print(str(error))
        finally:
            cursorSaldo.close()

        # Consulta ao Banco
        cursor = conexão.cursor()
        cursor.execute(consulta, parâmetros)

        linhas = cursor.fetchall()
        colunas = [coluna[0] for coluna in cursor.description]

        dataFrame = pd.DataFrame.from_records(linhas, columns=colunas)

        if not dataFrame.empty:
            débito = dataFrame["VALOR"][dataFrame["VALOR"] > 0].sum()
            crédito = dataFrame["VALOR"][dataFrame["VALOR"] < 0].sum()
            saldoAtual = saldo - (débito - crédito)
            print(dataFrame)
            print(f'SALDO ANTERIOR: {saldo}')
            print(f'DÉBITO: {débito}')
            print(f'CRÉDITO: {crédito}')
            print(f'SALDO ATUAL: {saldoAtual}')

            # Exporta os dados se necessário
            exportar_dados(dataFrame, débito, crédito, saldo, saldoAtual)
        else:
            messagebox.showinfo("Info", "Nenhum dado encontrado.")

    except Exception as erroConsulta:
        print(str(erroConsulta))
        messagebox.showerror("Erro", f"Erro ao executar a consulta: {str(erroConsulta)}")
    finally:
        cursor.close()

# Função para exportar os dados
def exportar_dados(dataFrame, débito, crédito, saldo, saldoAtual):
    exportar = messagebox.askyesno("Exportar", "Consulta efetuada com sucesso. Deseja exportar/salvar os dados?")
    if exportar:
        # Janela para escolher o formato do arquivo e o nome do arquivo
        janela_export = tk.Toplevel(bloco_ações)
        janela_export.title("Opções de Exportação")

        # Seleção do formato do arquivo
        tk.Label(janela_export, text="Formato do arquivo:").grid(row=0, column=0, padx=10, pady=5)
        var_formatoArquivo = tk.StringVar(value="Selecionar")
        tk.OptionMenu(janela_export, var_formatoArquivo, "excel", "csv").grid(row=0, column=1, padx=10, pady=5)

        # Entrada para o nome do arquivo
        tk.Label(janela_export, text="Nome do arquivo:").grid(row=1, column=0, padx=10, pady=5)
        entrada_nomeArquivo = tk.Entry(janela_export)
        entrada_nomeArquivo.grid(row=1, column=1, padx=10, pady=5)

        # Função interna para salvar o arquivo
        def salvar_arquivo():
            formatoArquivo = var_formatoArquivo.get()
            nomeArquivo = entrada_nomeArquivo.get()

            if nomeArquivo == "":
                messagebox.showerror("Erro", "Nome do arquivo não pode ser vazio.")
                return

            caminhoExport = escolher_caminho_arquivo()
            if formatoArquivo == "excel":
                nomeArquivo += ".xlsx"
                caminhoCompExport = os.path.join(caminhoExport, nomeArquivo)

                novaPasta = Workbook()
                planilha = novaPasta.active

                planilha.append(dataFrame.columns.tolist())
                for linha in dataFrame.itertuples(index=False, name=None):
                    planilha.append(linha)

                planilha['H1'] = 'SALDO ANTERIOR'
                planilha['H2'] = 'DÉBITO'
                planilha['H3'] = 'CRÉDITO'
                planilha['H4'] = 'SALDO ATUAL'
                planilha['I1'] = saldo
                planilha['I2'] = débito
                planilha['I3'] = crédito
                planilha['I4'] = saldoAtual

                novaPasta.save(caminhoCompExport)
                messagebox.showinfo("Sucesso", f"Arquivo salvo em:\n'{caminhoCompExport}'")
                janela_export.destroy()

            elif formatoArquivo == "csv":
                nomeArquivo += ".csv"
                caminhoCompExport = os.path.join(caminhoExport, nomeArquivo)
                dataFrame.to_csv(caminhoCompExport, index=False)
                messagebox.showinfo("Sucesso", f"Arquivo salvo em:\n'{caminhoCompExport}'")
                janela_export.destroy()

            else:
                messagebox.showerror("Erro", "Formato inválido. Escolha 'excel' ou 'csv'.")

        # Botão para confirmar a exportação
        botao_salvar = tk.Button(janela_export, text="Salvar", command=salvar_arquivo)
        botao_salvar.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
    else:
        messagebox.showinfo("Cancelado", "Exportação cancelada.")


# Criação da interface gráfica
if conexão:

    bloco_ações = tk.Tk()
    bloco_ações.title("Consulta de Razão")

    # Para encerrar
    bloco_ações.protocol("WM_DELETE_WINDOW", fechar_aplicacao)

    # Entradas para as datas
    tk.Label(bloco_ações, text="Data inicial (YYYYMMDD):").grid(row=0, column=0, padx=10, pady=5)
    entrada_inicio = tk.Entry(bloco_ações)
    entrada_inicio.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(bloco_ações, text="Data final (YYYYMMDD):").grid(row=1, column=0, padx=10, pady=5)
    entrada_fim = tk.Entry(bloco_ações)
    entrada_fim.grid(row=1, column=1, padx=10, pady=5)

    # Entrada para o nome ou código do cliente
    tk.Label(bloco_ações, text="Cliente (código ou nome/razão social):").grid(row=3, column=0, padx=10, pady=5)
    entrada_cliente = tk.Entry(bloco_ações)
    entrada_cliente.grid(row=3, column=1, padx=10, pady=5)

    # Entrada para o número da conta
    tk.Label(bloco_ações, text="Número da conta(vazio e selecionar o tipo de conta abaixo, caso queira extrair por tipo de conta):").grid(row=4, column=0, padx=10, pady=5)
    entrada_numConta = tk.Entry(bloco_ações)
    entrada_numConta.grid(row=4, column=1, padx=10, pady=5)

    # Seleção do tipo de conta
    tk.Label(bloco_ações, text="Tipo de conta(1(ATIVO)/2(PASSIVO)/3(RESULTADO)):").grid(row=5, column=0, padx=10, pady=5)
    entrada_tipoConta = tk.IntVar(value="Selecionar")
    tipoContaMenu = tk.OptionMenu(bloco_ações, entrada_tipoConta, "1", "2", "3")
    tipoContaMenu.grid(row=5, column=1, padx=10, pady=5)

    # Botão para realizar a consulta
    botao_consultar = tk.Button(bloco_ações, text="Consultar", command=realizar_consulta)
    botao_consultar.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

    bloco_ações.mainloop()
else:
    messagebox.showinfo("Erro", "Falha ao conectar ao banco de dados.")
    print("Falha ao conectar ao banco de dados.")
