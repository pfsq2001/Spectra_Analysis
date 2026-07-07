###### This program reads and process tabular files from Spectramax FRET, and generates an easy and friendly interface 
## Pedro Queiroz
# fev/2025
#
## library imports 

import flet as ft
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os 
import time
import math


# main function that enables the page to be created
def main(page: ft.Page):
    
    #defining page configurations 
    page.padding = ft.padding.symmetric(horizontal= 150)
    page.vertical_alignment = ft.MainAxisAlignment.END 
    
    #Defining variables for each image that is used in the program
    imagem_esquerda = ft.Image(src = "images/logo_unb.png", width=150, height=150)
    imagem_direita = ft.Image(src = "images/logo_embrapa.png", width=200)
    imagem_capes = ft.Image(src= "images/capes_fapdf_sem_fundo.png", width= 200 )
    imagem_grafico = ft.Image(src= "images/logo_ia.webp", width = 300)
    
   #positioning the images in rols for better formatation when inseached in the page
   
    linha_imagem = ft.Row(
        controls=[
            ft.Container(imagem_esquerda, alignment=ft.alignment.top_left, expand=True),
            ft.Container(imagem_direita, alignment=ft.alignment.center_right, expand=True)
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )
    linha_logo = ft.Row(
        controls=[
            ft.Container(imagem_grafico, alignment=ft.alignment.center, expand=True),
        ],
        visible= True
    )
    linha_superior = ft.Container(
        content= linha_imagem,
        margin = ft.margin.symmetric(horizontal=100),
        height= 150,
    )
    
    # Defining ROWS with the texts for better formatation
    
    linha_de_textos = ft.Row(
        controls=[
            ft.Container(imagem_capes, alignment=ft.alignment.bottom_center),
            ft.Text("Embrapa Recursos Genéticos e Biotecnologia Laboratório de Bioinformática Parque Estação Biológica, PqEB, Av. W5 Norte (final) Caixa Postal 02372 – Brasília, DF – CEP 70770-917 Fone: +55(61)3448-4741",
                size=10, 
                width=300,          
                max_lines=None,     
                overflow=ft.TextOverflow.CLIP
            ),  # First text
            ft.Text("Universidade de Brasília Departamento de Genética e Morfologia/IB Campus Darcy Ribeiro 70910-900, Brasília, DF, Brazil Fone +55(61)3107-3078Universidade de Brasília Departamento de Genética e Morfologia/IB Campus Darcy Ribeiro 70910-900, Brasília, DF, Brazil Fone +55(61)3107-3078",
                size=10, 
                width=300,           
                max_lines=None,
                overflow=ft.TextOverflow.CLIP
            ), # Second text
        
        ],
        alignment=ft.MainAxisAlignment.SPACE_EVENLY,  #positioning of the texts 
    )

    # making an container with the row inside facilitating the insertion of the texts in the page
    container_com_textos = ft.Container(
        content=linha_de_textos,
        bgcolor= ft.Colors.SURFACE_CONTAINER_HIGHEST,
        margin=ft.margin.symmetric(horizontal=200),
        alignment=ft.alignment.center,
        expand= False,
    )

    
    
    # creating lists and containers that will be used after and making then invisible while not in use
    container = ft.Container(
        visible=False,
        width=850,
        height=500,
        content=ft.Row(
            wrap=True,
            spacing=5,
            run_spacing=5,
            scroll=ft.ScrollMode.AUTO
        ),
        border=ft.border.all(1, ft.Colors.GREY_400),
        border_radius=10,
        padding=10,
        alignment=ft.alignment.center
    )
    container_resultado = ft.Container(
        width=680,
        height=390,
        content=ft.Row(
            wrap=True,
            spacing=2,
            run_spacing=2,
            scroll=ft.ScrollMode.AUTO
        ),
        border=ft.border.all(1, ft.Colors.GREY_400),
        border_radius=10,
        padding=10,
        margin= 0, 
        alignment=ft.alignment.center
    )
    container_grafico = ft.Container(
        width=600,
        height=650,
        #border=ft.border.all(1, ft.Colors.GREY_400),
        visible = False)
    confirmacao_controle= ft.Container(
        visible= False,
        alignment= ft.alignment.bottom_center,
        expand = False)
    controle_p = []
    controle_n = []
    lista_plot = []
    resultado = ft.Text(value="Estado dos botões: Nenhum")
    celulas_selecionadas = ft.Text(value= "")  
    caminho_arquivo = ''
    
    # Function that will be called when the button of the file selector be clicke
    def on_file_selected(e: ft.FilePickerResultEvent):
        global caminho_arquivo
        if e.files:
            selected_file = e.files[0].path 
            caminho_arquivo = e.files[0].path
            selected_file_label.value = f"Uploaded file path: {selected_file}"
            process_file(selected_file)
            container.visible = True
            linha_logo.visible= False
            legenda_controles.visible = True
            page.update()
    # Cria o seletor de arquivos
    file_picker = ft.FilePicker(on_result=on_file_selected)
    
    
    # variable for showing the adress from the selected file
    selected_file_label = ft.Text()

    # Button for selecting files to be uploaded 
    upload_button = ft.ElevatedButton(
        text="Upload File",
        on_click=lambda _: file_picker.pick_files(),
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        icon= ft.Icons.UPLOAD_FILE
    )
    # Container that was used for displaying the button on the page
    upload_container = ft.Container(
        content= upload_button,
        alignment= ft.alignment.top_center
    )
    confirmacao_controle.visible = True
    
    
    
    # Funcion to process CSV files
    def process_file(file_path):
        
        #uploads an table in DF format
        tabela = pd.read_csv(file_path, sep="\t", encoding='UTF-16', skiprows=2, skipfooter=3, dtype='float', decimal=',', engine="python")
        
        # Remove Temperaturo columns because it will not be used
        tabela.drop(['Temperature(¡C)'], axis='columns', inplace=True)
        
        #Replace all the NA for ) in the table than remove all the columns the are only compose by NA values
        tabela_fitted = tabela.fillna(0)
        tabela_valores = tabela.dropna(axis=1, how='all')
        
        #define a list for knowing wich one of the cells are or aren't filled 
        lista_celulas_cheias = list(tabela_valores)        
        
        # Calls the function responsable for generating the buttons 3 lines foward
        gerar_botoes(lista_celulas_cheias)



    """
    This Function is responsable for generating a 96 whells plate whith the name of wich cell and coloring the ones the are filed
    this is made using two loops one containig the letters and another one containing the nunbers in this way the buttons are generated
    in a loop and added to a list therefore to a container
    
    """
    def gerar_botoes(lista_valores):
        botoes = [
            ft.ElevatedButton(
                col=1,
                text=f"{i}{e}",
                width=50,
                height=50,
                #Ading conditions to the colors in the buttons
                bgcolor=ft.Colors.GREY if f"{i}{e}" in lista_valores else None,
                color= ft.Colors.BLACK if f"{i}{e}" in lista_valores else ft.Colors.BLUE,
                data={"count": 0},  # A counter that memorize how many clicks were executed for each button
                on_click=select, #defines wich function will be called when the button gets clicked
                disabled=(f"{i}{e}" not in lista_valores),
            )
            for i in ["A", "B", "C", "D", "E", "F", "G", "H"]
            for e in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        ]
        container.margin = ft.margin.symmetric(horizontal=60)
        container.padding=10
        container.content = ft.ResponsiveRow(botoes)
        container.update()
        

    # Função chamada quando os botões são clicados
    def select(e):
        button = e.control
        count = button.data["count"]  # Recupera o valor do contador
        count += 1  # Incrementa o contador

        # Se o contador atingir mais de 2, reseta para 0
        if count > 2:
            count = 0

        # Atualiza o estado do botão e as listas de controle conforme o contador
    
        if count == 0:
            button.bgcolor = ft.Colors.GREY
            button.color = ft.Colors.BLACK
            if button.text in controle_p:
                controle_p.remove(button.text)
            if button.text in controle_n:
                controle_n.remove(button.text)
        elif count == 1:
            button.bgcolor = ft.Colors.BLUE
            button.color = ft.Colors.WHITE
            if button.text not in controle_n:
                controle_n.append(button.text)
            if button.text in controle_p:
                controle_p.remove(button.text)
        elif count == 2:
            button.bgcolor = ft.Colors.RED
            button.color = ft.Colors.WHITE
            if button.text not in controle_p:
                controle_p.append(button.text)
            if button.text in controle_n:
                controle_n.remove(button.text)
        
            

        # Atualiza o contador do botão e seu estilo
        button.data["count"] = count
        button.update()

        atualizar_resultado()

    def atualizar_resultado():
        resultado.value = f"Controles: Positivos: {controle_p}, Negativos: {controle_n}"
        resultado.update()
    
    
    
    
    ######################################################################
    # Definindo a aćao de definir os controles na lista e fazer novos botoes
    ######################################################################
   
    #
    # FAZENDO OS NOVOS BOTOES DA SEGUNDA PAGINA
    #
    def botoes_resultado(dicionario, lista_resultado, controle_negativo, controle_positivo):

        colunas = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        linhas = ["A", "B", "C", "D", "E", "F", "G", "H"]

        # Botões seletores: ALL, números das colunas e letras das linhas
        botoes_seletores = ["ALL"] + colunas + linhas

        botoes = []

        # ----------------------------------------------------
        # Primeira linha: ALL + números das colunas
        # ----------------------------------------------------

        for texto_botao in ["ALL"] + colunas:

            cor_original = ft.Colors.GREY

            btn = ft.ElevatedButton(
                col=1,
                text=texto_botao,
                width=30,
                height=30,
                bgcolor=cor_original,
                color=ft.Colors.BLACK,
                data={
                    "count": 0,
                    "cor_original": cor_original
                },
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(),
                    bgcolor=cor_original
                ),
                disabled=False,
                on_click=celulas_plot
            )

            botoes.append(btn)

        # ----------------------------------------------------
        # Linhas da placa: A-H + poços A1-H12
        # ----------------------------------------------------

        for linha in linhas:

            # Botão seletor da linha: A, B, C...
            cor_original = ft.Colors.GREY

            btn_linha = ft.ElevatedButton(
                col=1,
                text=linha,
                width=30,
                height=30,
                bgcolor=cor_original,
                color=ft.Colors.BLACK,
                data={
                    "count": 0,
                    "cor_original": cor_original
                },
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(),
                    bgcolor=cor_original
                ),
                disabled=False,
                on_click=celulas_plot
            )

            botoes.append(btn_linha)

            # Botões dos poços: A1, A2, A3...
            for coluna in colunas:

                nome_poco = f"{linha}{coluna}"

                cor_original = (
                    ft.Colors.BLUE_100 if nome_poco in lista_resultado and dicionario.get(nome_poco) == "Negativo"
                    else ft.Colors.RED_100 if nome_poco in lista_resultado and dicionario.get(nome_poco) == "Positivo"
                    else ft.Colors.SURFACE_CONTAINER_HIGHEST if nome_poco in lista_resultado and dicionario.get(nome_poco) == "Vazio"
                    else ft.Colors.BLUE_300 if nome_poco in controle_negativo
                    else ft.Colors.RED_300 if nome_poco in controle_positivo
                    else ft.Colors.GREY
                )

                btn = ft.ElevatedButton(
                    col=1,
                    text=nome_poco,
                    width=30,
                    height=30,
                    bgcolor=cor_original,
                    color=ft.Colors.BLACK,
                    data={
                        "count": 0,
                        "cor_original": cor_original
                    },
                    style=ft.ButtonStyle(
                        shape=ft.StadiumBorder(),
                        bgcolor=cor_original
                    ),
                    disabled=(dicionario.get(nome_poco) == "Vazio"),
                    on_click=celulas_plot if dicionario.get(nome_poco) != "Vazio" else None
                )

                botoes.append(btn)

        container_resultado.content = ft.ResponsiveRow(
            botoes,
            columns=13,
            spacing= 2,
        )

        container_resultado.visible = True
        container_resultado.margin = 2
        container_resultado.padding = 2
        container_resultado.update()


    def celulas_plot(e):
        #definindo variaveis que serão utilizadas na funćão
        global dicionario

        lista_seletores = ["ALL", "COL-ROW", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "A", "B", "C", "D", "E", "F", "G", "H"]
        button = e.control
        count = button.data["count"]
        cor_original = button.data["cor_original"] 
        print(cor_original)
        #controle do botao pra saber quem de fato foi clicado :
        print(f"Botão clicado: {button.text}, Contador atualizado: {count}")
        # Botões comuns clicados
        count += 1 
        count %= 2  # Alterna entre 0 e 1
        button.data["count"] = count
        if dicionario.get(button.text) == "Negativo" and button.text not in lista_seletores:
            button.bgcolor = ft.Colors.BLUE_400 if count == 1 else cor_original 
            button.color = ft.Colors.WHITE if count == 1 else ft.Colors.BLACK
            atualizar_lista_plot(button)
        elif dicionario.get(button.text) == "Positivo" and button.text not in lista_seletores:
            button.bgcolor = ft.Colors.RED_ACCENT if count == 1 else cor_original
            button.color = ft.Colors.WHITE if count == 1 else ft.Colors.BLACK
            atualizar_lista_plot(button)
        elif button.text in controle_n:
            button.bgcolor = ft.Colors.BLUE_900 if count == 1 else cor_original 
            button.color = ft.Colors.WHITE if count == 1 else ft.Colors.BLACK
            atualizar_lista_plot(button)
        elif button.text in controle_p:
            button.bgcolor = ft.Colors.RED_900 if count == 1 else cor_original 
            button.color = ft.Colors.WHITE if count == 1 else ft.Colors.BLACK
            atualizar_lista_plot(button)

            


        # if dicionario.get(button.text) != "Vazio" and button.text not in lista_seletores:
        #     button.bgcolor = ft.Colors.RED_400 if count == 1 else cor_original
        #     atualizar_lista_plot(button)
            

        # Lida com botões "COL"
        if button.text.isdigit():
            numero = button.text
            for btn in container_resultado.content.controls:
                cor_original = btn.data["cor_original"]
                if numero == btn.text[1:]:  # Verifica se o número coincide
                    if dicionario.get(btn.text) != "Vazio" and btn.text not in lista_seletores:
                        btn.data["count"] += 1
                        btn.data["count"] %= 2  # Alterna entre 0 e 1
                        if btn.data["count"] == 1:
                            if btn.text in controle_n:
                                btn.bgcolor = ft.Colors.BLUE_900 if count == 1 else cor_original
                                btn.color = ft.Colors.WHITE if count == 1 else ft.Colors.BLACK
                                atualizar_lista_plot(btn)

                            # Depois verifica se é controle positivo
                            elif btn.text in controle_p:
                                btn.bgcolor = ft.Colors.RED_900 if count == 1 else cor_original
                                btn.color = ft.Colors.WHITE if count == 1 else ft.Colors.BLACK
                                atualizar_lista_plot(btn)

                            # Depois verifica se é uma amostra negativa
                            elif dicionario.get(btn.text) == "Negativo":
                                btn.bgcolor = ft.Colors.BLUE_400 if count == 1 else cor_original
                                btn.color = ft.Colors.WHITE if count == 1 else ft.Colors.BLACK
                                atualizar_lista_plot(btn)

                            # Depois verifica se é uma amostra positiva
                            elif dicionario.get(btn.text) == "Positivo":
                                btn.bgcolor = ft.Colors.RED_ACCENT if count == 1 else cor_original
                                btn.color = ft.Colors.WHITE if count == 1 else ft.Colors.BLACK
                                atualizar_lista_plot(btn)
                        else:
                            btn.bgcolor = btn.data["cor_original"]
                            btn.color = ft.Colors.BLACK
                        btn.update()
                        atualizar_lista_plot(btn)
        

        # Lida com botões "ROW"
        elif button.text in ["A", "B", "C", "D", "E", "F", "G", "H"]:
            letra = button.text
            
            for btn in container_resultado.content.controls:
                cor_original = btn.data["cor_original"]
                if letra in btn.text:
                    if dicionario.get(btn.text) != "Vazio" and btn.text not in lista_seletores:
                        btn.data["count"] += 1
                        btn.data["count"] %= 2  # Alterna entre 0 e 1
                        if btn.data["count"] == 1:
                            if btn.text in controle_n:
                                btn.bgcolor = ft.Colors.BLUE_900 if count == 1 else cor_original
                                btn.color = ft.Colors.WHITE if count == 1 else ft.Colors.BLACK
                                atualizar_lista_plot(btn)

                            # Depois verifica se é controle positivo
                            elif btn.text in controle_p:
                                btn.bgcolor = ft.Colors.RED_900 if count == 1 else cor_original
                                btn.color = ft.Colors.WHITE if count == 1 else ft.Colors.BLACK
                                atualizar_lista_plot(btn)

                            # Depois verifica se é uma amostra negativa
                            elif dicionario.get(btn.text) == "Negativo":
                                btn.bgcolor = ft.Colors.BLUE_400 if count == 1 else cor_original
                                btn.color = ft.Colors.WHITE if count == 1 else ft.Colors.BLACK
                                atualizar_lista_plot(btn)

                            # Depois verifica se é uma amostra positiva
                            elif dicionario.get(btn.text) == "Positivo":
                                btn.bgcolor = ft.Colors.RED_ACCENT if count == 1 else cor_original
                                btn.color = ft.Colors.WHITE if count == 1 else ft.Colors.BLACK
                                atualizar_lista_plot(btn) 
                        else:
                            btn.bgcolor = btn.data["cor_original"]
                            btn.color = ft.Colors.BLACK
                        btn.update()
                        atualizar_lista_plot(btn)
        
        #lida com a seleção de todos os botoes simultaneamente
        if button.text == "ALL":

            for btn in container_resultado.content.controls:
                cor_original = btn.data["cor_original"]
                # Ignora botões seletores como ALL, A-H e 1-12
                if btn.text not in lista_seletores:

                    # Ignora células vazias
                    if dicionario.get(btn.text) != "Vazio" and btn.text not in lista_seletores:
                            btn.data["count"] += 1
                            btn.data["count"] %= 2  # Alterna entre 0 e 1

                    # Aplica a cor conforme o novo estado
                    if btn.data["count"] == 1:
                        if btn.text in controle_n:
                            btn.bgcolor = ft.Colors.BLUE_900 if count == 1 else cor_original
                            btn.color = ft.Colors.WHITE if count == 1 else ft.Colors.BLACK
                            atualizar_lista_plot(btn)

                        # Depois verifica se é controle positivo
                        elif btn.text in controle_p:
                            btn.bgcolor = ft.Colors.RED_900 if count == 1 else cor_original
                            btn.color = ft.Colors.WHITE if count == 1 else ft.Colors.BLACK
                            atualizar_lista_plot(btn)

                        # Depois verifica se é uma amostra negativa
                        elif dicionario.get(btn.text) == "Negativo":
                            btn.bgcolor = ft.Colors.BLUE_400 if count == 1 else cor_original
                            btn.color = ft.Colors.WHITE if count == 1 else ft.Colors.BLACK
                            atualizar_lista_plot(btn)

                        # Depois verifica se é uma amostra positiva
                        elif dicionario.get(btn.text) == "Positivo":
                            btn.bgcolor = ft.Colors.RED_ACCENT if count == 1 else cor_original
                            btn.color = ft.Colors.WHITE if count == 1 else ft.Colors.BLACK
                            atualizar_lista_plot(btn) 
                    
                    else:
                        btn.bgcolor = btn.data["cor_original"]
                        btn.color = ft.Colors.BLACK
                    btn.update()

                    atualizar_lista_plot(btn)
                    btn.update()

            # button.update()
        button.update()
        atualizar_celulas_selecionadas()


    def atualizar_lista_plot(botao):
        """Atualiza a lista `lista_plot` com base no estado do botão."""
        if botao.data["count"] == 0:
            if botao.text in lista_plot:
                lista_plot.remove(botao.text)
                print(f"Removido: {botao.text}")
        elif botao.data["count"] == 1:
            if botao.text not in lista_plot:
                lista_plot.append(botao.text)
                print(f"Adicionado: {botao.text}")
        botao.update()


                
    def atualizar_celulas_selecionadas():
        celulas_selecionadas.value = f"Celulas {lista_plot}"
        celulas_selecionadas.update()        
        
    
         
    dicionario = {}


# função de mosstrar erro 
    def mostrar_erro(page, mensagem):
        snackbar = ft.SnackBar(
            content=ft.Text(mensagem),
            bgcolor=ft.Colors.RED_700
        )

        page.open(snackbar)
        page.update()  

########################################################
######Função que verifica a escolha dos controles#######
########################################################
    def verificar_controles(tabela, lista_controles, nome_grupo):

        picos = {}

        for controle in lista_controles:
            pico = tabela[controle].loc[
                (tabela["Wavelength"] > 655) &
                (tabela["Wavelength"] < 665)
            ].nlargest(3).mean()

            picos[controle] = pico

        if len(picos) > 1:
            maior = max(picos.values())
            menor = min(picos.values())

            if menor == 0:
                return False, f"Erro: um dos {nome_grupo} tem valor zero."

            razao = maior / menor

            if razao >= 1.50:
                return False, (
                    f"Erro: os {nome_grupo} foram mal escolhidos. "
                    f"Um controle está {((razao - 1) * 100):.1f}% maior que outro."
                )

        return True, ""



    

    def confirmando_controles(e):
        global caminho_arquivo, dicionario

        tabela = pd.read_csv(
            caminho_arquivo,
            sep="\t",
            encoding="UTF-16",
            skiprows=2,
            skipfooter=3,
            decimal=",",
            engine="python"
        )

        # Remove a coluna de temperatura, caso exista
        tabela.drop(
            ["Temperature(¡C)"],
            axis="columns",
            inplace=True,
            errors="ignore"
        )

        # Identifica quais colunas/poços possuem dados
        tabela_valores = tabela.dropna(axis=1, how="all")
        lista_celulas_cheias = list(tabela_valores.columns)
        controles = controle_n + controle_p

        resultado = []

        if controle_n and controle_p: # verifica se clicaram nos controles

            # Calcula as médias dos controles
            tabela["media_controle_p"] = tabela.loc[:, controle_p].mean(axis=1)
            tabela["media_controle_n"] = tabela.loc[:, controle_n].mean(axis=1)


            ## Verifica seos controles estão ou não bem escolhidos
            controle_n_ok, mensagem_erro_n = verificar_controles(
                tabela,
                controle_n,
                "controles negativos"
            )

            controle_p_ok, mensagem_erro_p = verificar_controles(
                tabela,
                controle_p,
                "controles positivos"
            )

            if not controle_n_ok:
                mostrar_erro(e.page, mensagem_erro_n)
                return

            if not controle_p_ok:
                mostrar_erro(e.page, mensagem_erro_p)
                return

            # ----------------------------------------------------
            # Cálculo do limiar baseado nos controles negativos
            # ----------------------------------------------------

            picos_controle_n = []

            for cn in controle_n:
                ratio_cn = tabela[cn] / tabela["media_controle_n"]

                pico_cn = ratio_cn.loc[
                    (tabela["Wavelength"] > 655) & 
                    (tabela["Wavelength"] < 665)
                ].nlargest(3).mean()

                picos_controle_n.append(pico_cn)

            media_fold_controle_n = np.mean(picos_controle_n)
            ## Condicional para caso a pessoa escolha apenas um controle
            if len(picos_controle_n) > 1:
                desvio_padrao_controle_n = np.std(picos_controle_n, ddof=1)
            else:
                desvio_padrao_controle_n = 0
            

            limiar = media_fold_controle_n + 0.10 + desvio_padrao_controle_n

            print("Média controle negativo:", media_fold_controle_n)
            print("Desvio padrão controle negativo:", desvio_padrao_controle_n)
            print("Limiar:", limiar)

            # ----------------------------------------------------
            # Seleção das amostras
            # ----------------------------------------------------

            colunas_ignoradas = [
                *controle_n,
                *controle_p,
                "Wavelength",
                "media_controle_p",
                "media_controle_n"
            ]

            amostras = [
                coluna for coluna in tabela.columns
                if coluna not in colunas_ignoradas
            ]

            # ----------------------------------------------------
            # Classificação das amostras
            # ----------------------------------------------------

            for i in amostras:

                if i not in lista_celulas_cheias:
                    resultado.append((i, "Vazio"))
                    continue

                ratio_tratamento = tabela[i] / tabela["media_controle_n"]

                pico_tratamento = ratio_tratamento.loc[
                    (tabela["Wavelength"] > 655) & 
                    (tabela["Wavelength"] < 665)
                ].nlargest(3).mean()

                print(i, pico_tratamento)

                if pico_tratamento > limiar:
                    resultado.append((i, "Positivo"))
                else:
                    resultado.append((i, "Negativo"))
        

    #fazendo o dicionario para fazer o replace das células do data frame com os resultados:
            pos = []
            res = []
            for l in resultado:
                pos.append(l[0])
                res.append(l[1])
            dicionario = dict(zip(pos, res))

            e.page.go("/pagina2")
            botoes_resultado(dicionario, pos, controle_n, controle_p)

            print(resultado)

       
            
    ########################################################################################################################
    ##################### fazendo os botões para a proxima pagina ##########################################################
    ########################################################################################################################
    
    confirmacao = ft.ElevatedButton(
                col=1,
                text= f"Generate Results",
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                on_click= confirmando_controles
            )
    confirmacao_controle.content = confirmacao
    
    
    #funćao pra remover graficos antigos
    def remover_graficos_antigos():
        """Remove todos os gráficos gerados anteriormente."""
        
        for arquivo in os.listdir():
            if arquivo.startswith("grafico_") and arquivo.endswith(".png"):
                os.remove(arquivo)

    
    
    #funćao para gerar os gráficos 
    def grafico(e):
        remover_graficos_antigos()

        global caminho_arquivo

        plt.close("all")

        # ----------------------------------------------------
        # Verifica se existem células selecionadas
        # ----------------------------------------------------

        if not lista_plot:
            mostrar_erro(
                e.page,
                "Select at least one cell to generate the graph."
            )
            return

        # ----------------------------------------------------
        # Leitura da tabela
        # ----------------------------------------------------

        tabela = pd.read_csv(
            caminho_arquivo,
            sep="\t",
            encoding="UTF-16",
            skiprows=2,
            skipfooter=3,
            dtype="float",
            decimal=",",
            engine="python"
        )

        tabela.drop(
            ["Temperature(¡C)"],
            axis="columns",
            inplace=True,
            errors="ignore"
        )

        # Colunas completamente vazias
        colunas_vazias = tabela.columns[
            tabela.isna().all()
        ].tolist()

        # ----------------------------------------------------
        # Verifica os controles negativos
        # ----------------------------------------------------

        controles_n_validos = [
            cn for cn in controle_n
            if cn in tabela.columns
            and cn not in colunas_vazias
        ]

        if not controles_n_validos:
            mostrar_erro(
                e.page,
                "There are no valid negative controls to calculate the threshold."
            )
            return

        # Média dos controles negativos
        tabela["media_controle_n"] = tabela[
            controles_n_validos
        ].mean(axis=1)

        # ----------------------------------------------------
        # Verifica os controles positivos
        # ----------------------------------------------------

        controles_p_validos = [
            cp for cp in controle_p
        ]

        if controles_p_validos:
            tabela["media_controle_p"] = tabela[
                controles_p_validos
            ].mean(axis=1)

        # ----------------------------------------------------
        # Intervalo usado para calcular o pico
        # ----------------------------------------------------

        mascara_intervalo = (
            (tabela["Wavelength"] > 655) &
            (tabela["Wavelength"] < 665)
        )

        if mascara_intervalo.sum() == 0:
            mostrar_erro(
                e.page,
                "There are no data points between 655 and 665 nm."
            )
            return

        # ----------------------------------------------------
        # Cálculo dos picos dos controles negativos
        # ----------------------------------------------------

        picos_controle_n = []
        nomes_controle_n = []

        for cn in controles_n_validos:

            ratio_cn = (
                tabela[cn] /
                tabela["media_controle_n"]
            )

            valores_intervalo = ratio_cn.loc[
                mascara_intervalo
            ].dropna()

            if valores_intervalo.empty:
                continue

            pico_cn = valores_intervalo.nlargest(
                min(3, len(valores_intervalo))
            ).mean()

            picos_controle_n.append(pico_cn)
            nomes_controle_n.append(cn)

        if not picos_controle_n:
            mostrar_erro(
                e.page,
                "It was not possible to calculate the peaks of the negative controls."
            )
            return

        media_fold_controle_n = np.mean(
            picos_controle_n
        )

        if len(picos_controle_n) > 1:
            desvio_padrao_controle_n = np.std(
                picos_controle_n,
                ddof=1
            )
        else:
            desvio_padrao_controle_n = 0

        limiar = (
            media_fold_controle_n +
            desvio_padrao_controle_n
        ) * 1.10

        print("Picos controle negativo:", picos_controle_n)
        print("Média controle negativo:", media_fold_controle_n)
        print(
            "Desvio padrão controle negativo:",
            desvio_padrao_controle_n
        )
        print("Limiar:", limiar)

        # ----------------------------------------------------
        # Dados para o gráfico de espectros
        # ----------------------------------------------------

        tabela_grafico = tabela[
            (tabela["Wavelength"] >= 600) &
            (tabela["Wavelength"] <= 700)
        ].copy()

        colunas_controle_p = [
            coluna for coluna in lista_plot
            if coluna in controles_p_validos
        ]

        colunas_controle_n = [
            coluna for coluna in lista_plot
            if coluna in controles_n_validos
        ]

        colunas_amostras = [
            coluna for coluna in lista_plot
            if coluna in tabela.columns
            and coluna not in controle_p
            and coluna not in controle_n
            and coluna not in colunas_vazias
            and coluna not in [
                "Wavelength",
                "media_controle_n",
                "media_controle_p"
            ]
        ]

        # ----------------------------------------------------
        # Classificação das amostras e controles
        # ----------------------------------------------------

        COR_POSITIVO = "red"
        COR_NEGATIVO = "blue"
        COR_CONTROLE_POSITIVO = "red"
        COR_CONTROLE_NEGATIVO = "blue"

        classificacao_por_coluna = {}
        pico_por_coluna = {}

        def classificar_pico(valor_pico):
            if valor_pico > limiar:
                return "Positive", COR_POSITIVO
            else:
                return "Negative", COR_NEGATIVO

        # Classificação dos controles negativos
        for cn, pico_cn in zip(
            nomes_controle_n,
            picos_controle_n
        ):
            classificacao, cor = classificar_pico(
                pico_cn
            )

            classificacao_por_coluna[cn] = classificacao
            pico_por_coluna[cn] = pico_cn

        # Classificação das amostras selecionadas
        for amostra in colunas_amostras:

            ratio_tratamento = (
                tabela[amostra] /
                tabela["media_controle_n"]
            )

            valores_intervalo = ratio_tratamento.loc[
                mascara_intervalo
            ].dropna()

            if valores_intervalo.empty:
                continue

            pico_tratamento = valores_intervalo.nlargest(
                min(3, len(valores_intervalo))
            ).mean()

            classificacao, cor = classificar_pico(
                pico_tratamento
            )

            classificacao_por_coluna[amostra] = classificacao
            pico_por_coluna[amostra] = pico_tratamento

            print(
                amostra,
                pico_tratamento,
                classificacao
            )

        # Classificação dos controles positivos selecionados
        for cp in colunas_controle_p:

            ratio_cp = (
                tabela[cp] /
                tabela["media_controle_n"]
            )

            valores_intervalo = ratio_cp.loc[
                mascara_intervalo
            ].dropna()

            if valores_intervalo.empty:
                continue

            pico_cp = valores_intervalo.nlargest(
                min(3, len(valores_intervalo))
            ).mean()

            classificacao, cor = classificar_pico(
                pico_cp
            )

            classificacao_por_coluna[cp] = classificacao
            pico_por_coluna[cp] = pico_cp

        # ----------------------------------------------------
        # Criação da figura
        # ----------------------------------------------------

        fig, (ax_espectro, ax_barras) = plt.subplots(
            nrows=2,
            ncols=1,
            figsize=(9, 11),
            gridspec_kw={
                "height_ratios": [1, 0.5]
            }
        )

        # ====================================================
        # GRÁFICO 1 — ESPECTROS
        # ====================================================

        for coluna in colunas_amostras:

            classificacao = classificacao_por_coluna.get(
                coluna,
                "Negative"
            )

            if classificacao == "Positive":
                cor_linha = COR_POSITIVO
            else:
                cor_linha = COR_NEGATIVO

            ax_espectro.plot(
                tabela_grafico["Wavelength"],
                tabela_grafico[coluna],
                label=f"{coluna} - {classificacao}",
                linewidth=1,
                color=cor_linha
            )

        # ----------------------------------------------------
        # Controles positivos
        # ----------------------------------------------------

        if colunas_controle_p:

            media_p = tabela_grafico[
                colunas_controle_p
            ].mean(axis=1)

            if len(colunas_controle_p) > 1:
                desvio_p = tabela_grafico[
                    colunas_controle_p
                ].std(axis=1)
            else:
                desvio_p = pd.Series(
                    0,
                    index=tabela_grafico.index
                )

            ax_espectro.plot(
                tabela_grafico["Wavelength"],
                media_p,
                label="CP",
                linewidth=1.5,
                color=COR_CONTROLE_POSITIVO
            )

            ax_espectro.fill_between(
                tabela_grafico["Wavelength"],
                media_p - desvio_p,
                media_p + desvio_p,
                alpha=0.2,
                color=COR_POSITIVO
            )

        # ----------------------------------------------------
        # Controles negativos
        # ----------------------------------------------------

        if colunas_controle_n:

            media_n = tabela_grafico[
                colunas_controle_n
            ].mean(axis=1)

            if len(colunas_controle_n) > 1:
                desvio_n = tabela_grafico[
                    colunas_controle_n
                ].std(axis=1)
            else:
                desvio_n = pd.Series(
                    0,
                    index=tabela_grafico.index
                )

            ax_espectro.plot(
                tabela_grafico["Wavelength"],
                media_n,
                label="CN",
                linewidth=1.5,
                color=COR_CONTROLE_NEGATIVO
            )

            ax_espectro.fill_between(
                tabela_grafico["Wavelength"],
                media_n - desvio_n,
                media_n + desvio_n,
                alpha=0.2,
                color=COR_NEGATIVO
            )

        # Destaca o intervalo do cálculo dos picos
        ax_espectro.axvspan(
            655,
            665,
            alpha=0.12,
            color="grey",
            label="Peak interval"
        )

        ax_espectro.set_title(
            "Fluorescence intensity vs. wavelength"
        )

        ax_espectro.set_xlabel(
            "Wavelength (nm)",
            fontsize=12
        )

        ax_espectro.set_ylabel(
            "Fluorescence intensity (A.U.)",
            fontsize=12
        )

        ax_espectro.grid(
            True,
            alpha=0.3
        )

        handles, labels = (
            ax_espectro.get_legend_handles_labels()
        )

        if labels:
            numero_colunas_legenda = max(
                1,
                math.ceil(len(labels) / 12)
            )

            ax_espectro.legend(
                handles,
                labels,
                title="Selected cells",
                title_fontsize=10,
                fontsize=8,
                ncol=numero_colunas_legenda,
                loc="best",
                framealpha=0.8
            )

        # ====================================================
        # GRÁFICO 2 — PICOS NORMALIZADOS
        # ====================================================

        nomes_barras = []
        valores_barras = []
        cores_barras = []

        # ----------------------------------------------------
        # Controles negativos
        # ----------------------------------------------------
        for cp in colunas_controle_p:

            # if cp not in pico_por_coluna:
            #     continue

            pico_cp = pico_por_coluna[
                cp
            ]

            classificacao = classificacao_por_coluna.get(
                cp,
                "Negative"
            )

            if classificacao == "Positive":
                cor_barra = COR_POSITIVO
            else:
                cor_barra = COR_NEGATIVO

            nomes_barras.append(
                f"{cp} C+"
            )

            valores_barras.append(
                pico_cp
            )

            cores_barras.append(
                COR_CONTROLE_POSITIVO
            )
        for cn, pico_cn in zip(
            nomes_controle_n,
            picos_controle_n
        ):

            classificacao = classificacao_por_coluna.get(
                cn,
                "Negative"
            )

            if classificacao == "Positive":
                cor_barra = COR_POSITIVO
            else:
                cor_barra = COR_NEGATIVO

            nomes_barras.append(
                f"{cn} C-"
            )

            valores_barras.append(
                pico_cn
            )

            cores_barras.append(
                COR_CONTROLE_NEGATIVO
            )

        # Média dos controles negativos
        #nomes_barras.append("Média C-")
        #valores_barras.append(media_fold_controle_n)

        # classificacao_media_cn, cor_media_cn = classificar_pico(
        #     media_fold_controle_n
        # )

        # cores_barras.append(
        #     cor_media_cn
        # )

        # ----------------------------------------------------
        # Amostras selecionadas
        # ----------------------------------------------------

        for amostra in colunas_amostras:

            if amostra not in pico_por_coluna:
                continue

            pico_tratamento = pico_por_coluna[
                amostra
            ]

            classificacao = classificacao_por_coluna.get(
                amostra,
                "Negative"
            )

            if classificacao == "Positive":
                cor_barra = COR_POSITIVO
            else:
                cor_barra = COR_NEGATIVO

            nomes_barras.append(
                f"{amostra}"
            )

            valores_barras.append(
                pico_tratamento
            )

            cores_barras.append(
                cor_barra
            )

        # ----------------------------------------------------
        # Controles positivos selecionados
        # ----------------------------------------------------

        

        posicoes = np.arange(
            len(nomes_barras)
        )

        barras = ax_barras.bar(
            posicoes,
            valores_barras,
            color=cores_barras,
            edgecolor="black",
            linewidth=0.4
        )

        # Linha do limiar
        ax_barras.axhline(
            y=limiar,
            linestyle="--",
            color="black",
            linewidth=1.3,
            label=f"Threshold = {limiar:.2f}"
        )

        # Legenda das cores positivo/negativo
        from matplotlib.patches import Patch

        legenda_classificacao = [
            Patch(
                facecolor=COR_POSITIVO,
                edgecolor="black",
                label="Positive"
            ),
            Patch(
                facecolor=COR_NEGATIVO,
                edgecolor="black",
                label="Negative"
            )
        ]

        ax_barras.set_xlabel(
            "Samples",
            fontsize=12
        )

        ax_barras.set_ylabel(
            "Fold change / normalized peak",
            fontsize=12
        )

        ax_barras.set_title(
            "Sample peaks relative to the negative control"
        )

        ax_barras.set_xticks(
            posicoes
        )

        ax_barras.set_xticklabels(
            nomes_barras,
            rotation=90,
            fontsize=8
        )

        ax_barras.grid(
            True,
            axis="y",
            alpha=0.3
        )

        handles_barras, labels_barras = (
            ax_barras.get_legend_handles_labels()
        )

        ax_barras.legend(
            handles=legenda_classificacao + handles_barras,
            fontsize=9
        )

        # Valores acima das barras
        # if len(barras) <= 0:
        #
        #     deslocamento = max(valores_barras) * 0.01
        #
        #     for barra, valor in zip(
        #         barras,
        #         valores_barras
        #     ):
        #         ax_barras.text(
        #             barra.get_x() +
        #             barra.get_width() / 2,
        #             barra.get_height() + deslocamento,
        #             f"{valor:.2f}",
        #             ha="center",
        #             va="bottom",
        #             rotation=90,
        #             fontsize=7
        #         )

        # ----------------------------------------------------
        # Salva a figura
        # ----------------------------------------------------

        # fig.suptitle(
        #     "Spectral profile and peak-based classification",
        #     fontsize=15,
        #     fontweight="bold"
        # )

        fig.tight_layout(
            rect=[0, 0, 1, 0.95]
        )

        timestamp = int(time.time())
        caminho_imagem = f"grafico_{timestamp}.png"

        fig.savefig(
            caminho_imagem,
            format="png",
            dpi=72,
            bbox_inches="tight"
        )

        plt.close(fig)

        # ----------------------------------------------------
        # Mostra no Flet
        # ----------------------------------------------------

        chart = ft.Image(
            src=caminho_imagem,
            fit=ft.ImageFit.CONTAIN,
            width=900,
            height=600,
        )

        container_grafico.content = chart
        container_grafico.visible = True
        container_grafico.alignment = ft.alignment.center
        container_grafico.update()    
    remover_graficos_antigos()

        
    ####### Botão para plotar o gráfico####
    plot = ft.ElevatedButton(
                text= 'Plot cells',
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                on_click= grafico
    )
    
    
    #reinicia o app:
    
    def reiniciar_app(e):
        page.session.clear()
        page.controls.clear()  # Remove todos os componentes da tela
        main(page)  # Chama a função principal novamente
        page.update()
        page.go("/")
        
        
    legenda_controles_2 = ft.Container(
        content=ft.Column(
            [
                
                # ft.Text(
                #             "Legend",
                #             weight=ft.FontWeight.BOLD,
                #             size=14
                #         ),
                ft.Row(
                    [
                        ft.Text(
                            "Legend:",
                            weight=ft.FontWeight.BOLD,
                            size=14
                        ),
                        ft.Container(
                            width=12,
                            height=12,
                            bgcolor=ft.Colors.RED_300,
                            border_radius=50
                        ),
                        # ft.Container(
                        #     width=12,
                        #     height=12,
                        #     bgcolor=ft.Colors.RED_900,
                        #     border_radius=50
                        # ),
                        ft.Text("Positive Control;"),
                        ft.Container(
                            width=12,
                            height=12,
                            bgcolor=ft.Colors.BLUE_300,
                            border_radius=50
                        ),
                        # ft.Container(
                        #     width=12,
                        #     height=12,
                        #     bgcolor=ft.Colors.BLUE_900,
                        #     border_radius=50
                        # ),
                        ft.Text("Negative Control;"),
                        ft.Container(
                            width=12,
                            height=12,
                            bgcolor=ft.Colors.RED_100,
                            border_radius=50
                        ),
                        # ft.Container(
                        #     width=12,
                        #     height=12,
                        #     bgcolor=ft.Colors.RED_ACCENT,
                        #     border_radius=50
                        # ),
                        ft.Text("Positive Sample;"),
                        ft.Container(
                            width=12,
                            height=12,
                            bgcolor=ft.Colors.BLUE_100,
                            border_radius=50
                        ),
                        # ft.Container(
                        #     width=12,
                        #     height=12,
                        #     bgcolor=ft.Colors.BLUE_400,
                        #     border_radius=50
                        # ),
                        ft.Text("Negative Sample"),
                        
                    ],
                    spacing=8
                ),

                # ft.Row(
                #     [
                #         ft.Container(
                #             width=12,
                #             height=12,
                #             bgcolor=ft.Colors.BLUE,
                #             border_radius=50
                #         ),
                #         ft.Text("Positive control")
                #     ],
                #     spacing=8
                # ),
            ],
            spacing=8,
            tight=True
        ),
        padding=10,
        border=ft.border.all(1, ft.Colors.GREY_400),
        border_radius=10,
        width= 750,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        visible= True
    )
    legenda_controles = ft.Container(
        content=ft.Column(
            [
                
                # ft.Text(
                #             "Legend",
                #             weight=ft.FontWeight.BOLD,
                #             size=14
                #         ),
                ft.Row(
                    [
                        ft.Text(
                            "Legend",
                            weight=ft.FontWeight.BOLD,
                            size=14
                        ),
                        ft.Container(
                            width=12,
                            height=12,
                            bgcolor=ft.Colors.BLUE,
                            border_radius=50
                        ),
                        ft.Text("Negative control"),
                        ft.Container(
                            width=12,
                            height=12,
                            bgcolor=ft.Colors.RED,
                            border_radius=50
                        ),
                        ft.Text("Positive control")
                    ],
                    spacing=8
                ),

                # ft.Row(
                #     [
                #         ft.Container(
                #             width=12,
                #             height=12,
                #             bgcolor=ft.Colors.BLUE,
                #             border_radius=50
                #         ),
                #         ft.Text("Positive control")
                #     ],
                #     spacing=8
                # ),
            ],
            spacing=8,
            tight=True
        ),
        padding=10,
        border=ft.border.all(1, ft.Colors.GREY_400),
        border_radius=10,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        margin=ft.margin.symmetric(horizontal=200),
        visible= False
    )
    
    coluna_pagina_1 = ft.Column(
        [
            ft.Container(
                content=linha_superior,
                alignment=ft.alignment.top_center,
                margin=ft.margin.symmetric(horizontal=200),
             ), # imagens primeira linha
            ft.Container(
                content=ft.Text(
                    'SpectraRNA is a software program developed to interpret and analyze curves generated by spectrophotometers. This software enables the extraction of information such as curve peaks, the distance between maximum points, and emission patterns, facilitating both quantitative and qualitative analysis of samples. The software was initially developed to simplify the interpretation of diagnostic results for highly pathogenic avian influenza H5N1 (HPAI); however, its application extends to several areas of science, promoting efficient interpretation of the obtained spectral data.',
                    width=1000,  
                    max_lines=None,  
                    overflow=ft.TextOverflow.CLIP,
                    text_align=ft.TextAlign.JUSTIFY,  
                ),
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                padding=10,
                alignment=ft.alignment.top_center,  
                margin=ft.margin.symmetric(horizontal=200),
            ), # tezxto com descrićao do 
            upload_container, # LOCAL PARA ESCOLHER O ARQUIVO 
            file_picker, # POP UP DA PAGINA
            ft.Container(
                content=container,
                alignment=ft.alignment.center,
                expand=True
            ), #ONDE ESTAO OS BOTOES 
            ft.Container(
                content=legenda_controles,
                alignment=ft.alignment.bottom_center,
                expand=True
            ),
            linha_logo,
            confirmacao_controle, 
            container_com_textos,
        ],
        expand=True,
        scroll="auto",# 🔹 Expande a coluna para ocupar toda a altura da página
        alignment=ft.MainAxisAlignment.END
    )

    

    coluna_pagina_2 = ft.Column(
        [
            #ft.Text("Page 2"),
            ft.ElevatedButton(
                "Back",
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                on_click= reiniciar_app
            ),
            ft.Container(
                content = ft.Row(
                    [
                        ft.Column(
                            [
                                container_resultado,
                                legenda_controles_2,
                            ],
                            spacing=10,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        container_grafico, #o gráfico
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing = 50,
                    expand= True,
                    scroll=ft.ScrollMode.AUTO,
                ),
                alignment= ft.alignment.center,
                expand= True

            ),
            ft.Container(
                        content=plot,
                        alignment=ft.alignment.center,
                    ),

            #celulas_selecionadas, # Container com textos posicionado no final
                        
        ],
        scroll='auto',  # Habilita rolagem
        expand = True,  # Permite que a coluna ocupe todo o espaço vertical
        
    )
   
    ##### visualizaćao da pagina
    def route_change(route):
        page.views.clear()
        if page.route == "/":
            page.views.append(
                ft.View(
                    "/",
                    [
                        coluna_pagina_1,
                    ],
                )
            )
        elif page.route == "/pagina2":
            page.views.append(
                ft.View(
                    "/pagina2",
                    [
                        coluna_pagina_2,
                    ],
                )
            )
        page.update()

    # Detecta alterações na rota
    page.on_route_change = route_change

    # Define a rota inicial
    page.go(page.route)

# Inicializa o app Flet
ft.app(target=main)