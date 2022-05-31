import pandas as pd
import re
brancos = re.compile(r'\r\n|\n|\r|[ \u202F\u00A0]+$|^[ \u202F\u00A0]+')
sepExtra = re.compile(r'#$|^#')

def procDecisoes(classe, myReg, ListaErros, entCatalog, tipCatalog, legCatalog):
    # PCA -----
    if classe["Prazo de conservação administrativa"]:
        myReg['pca'] = {}
        if type(classe["Prazo de conservação administrativa"]) not in [int, float]:
            pca = brancos.sub('', classe["Prazo de conservação administrativa"])
        else:
            pca = classe["Prazo de conservação administrativa"]
        # Verifica-se se tem alguma coisa
        if pd.isna(pca):
            myReg['pca']['valores'] = "NE"
        else: 
            if type(classe["Prazo de conservação administrativa"]) not in [int, float]:
                if re.search(r'\d+', pca):
                    if re.search(r'#', str(pca)):
                        pca = sepExtra.sub('', pca)
                        valores = pca.split('#')
                        myReg['pca']['valores'] = list(map(int, valores))
                    else:
                        myReg['pca']['valores'] = pca
                else:
                    myReg['pca']['valores'] = "NE"
            else:
                myReg['pca']['valores'] = pca
    # Nota ao PCA ----------------------------
    if classe["Nota ao PCA"]:
        myReg['pca']['notas'] = brancos.sub('', classe["Nota ao PCA"])
    # ERRO: um dos dois, PCA ou Nota ao PCA, tem de ter um valor válido
    if myReg["estado"]!='H':
        if classe["Prazo de conservação administrativa"] and (myReg['pca']['valores'] == "NE") and 'notas' not in myReg['pca'].keys():
            ListaErros.append('Erro::' + myReg['codigo'] + '::PCA e Nota ao PCA não podem ser simultaneamente inválidos')
    # Forma de Contagem do PCA -----
    if 'pca' in myReg.keys():
        formaContagem = brancos.sub('', str(classe["Forma de contagem do PCA"]))
        if re.search(r'conclusão.*procedimento', formaContagem, re.I):
            myReg['pca']['formaContagem'] = 'conclusaoProcedimento'
        elif re.search(r'cessação.*vigência', formaContagem, re.I):
            myReg['pca']['formaContagem'] = 'cessacaoVigencia'
        elif re.search(r'extinção.*entidade', formaContagem, re.I):
            myReg['pca']['formaContagem'] = 'extincaoEntidade'
        elif re.search(r'extinção.*direito', formaContagem, re.I):
            myReg['pca']['formaContagem'] = 'extincaoDireito'
        elif re.search(r'início.*procedimento', formaContagem, re.I):
            myReg['pca']['formaContagem'] = 'inicioProcedimento'
        elif re.search(r'emissão.*título', formaContagem, re.I):
            myReg['pca']['formaContagem'] = 'emissaoTitulo'
        elif re.search(r'disposição.*legal', formaContagem, re.I):
            myReg['pca']['formaContagem'] = 'disposicaoLegal'
            if re.search(r'10\s+-', formaContagem):
                myReg['pca']['subFormaContagem'] = 'F01.10'
            elif re.search(r'11\s+-', formaContagem):
                myReg['pca']['subFormaContagem'] = 'F01.11'
            elif re.search(r'12\s+-', formaContagem):
                myReg['pca']['subFormaContagem'] = 'F01.12'
            elif re.search(r'1\s+-', formaContagem):
                myReg['pca']['subFormaContagem'] = 'F01.01'
            elif re.search(r'2\s+-', formaContagem):
                myReg['pca']['subFormaContagem'] = 'F01.02'
            elif re.search(r'3\s+-', formaContagem):
                myReg['pca']['subFormaContagem'] = 'F01.03'
            elif re.search(r'4\s+-', formaContagem):
                myReg['pca']['subFormaContagem'] = 'F01.04'
            elif re.search(r'5\s+-', formaContagem):
                myReg['pca']['subFormaContagem'] = 'F01.05'
            elif re.search(r'6\s+-', formaContagem):
                myReg['pca']['subFormaContagem'] = 'F01.06'
            elif re.search(r'7\s+-', formaContagem):
                myReg['pca']['subFormaContagem'] = 'F01.07'
            elif re.search(r'8\s+-', formaContagem):
                myReg['pca']['subFormaContagem'] = 'F01.08'
            elif re.search(r'9\s+-', formaContagem):
                myReg['pca']['subFormaContagem'] = 'F01.09'
            else:
                ListaErros.append('Erro::' + myReg['codigo'] + '::Não consegui extrair a subforma de contagem::' + formaContagem)
        else:
            myReg['pca']['formaContagem'] = "Desconhecida"
            ListaErros.append('Erro::' + myReg['codigo'] + '::Forma de contagem do PCA desconhecida::' + formaContagem)
    # Justificação do PCA -----
    if 'pca' in myReg.keys() and classe["Justificação PCA"]:
        just = brancos.sub('', classe["Justificação PCA"])
        just = sepExtra.sub('', just)
        myReg['pca']['justificacao'] = just.split('#')

    if classe["Dimensão qualitativa do processo"]:
        myReg["dimensao"] = classe["Dimensão qualitativa do processo"]
    if classe["Uniformização do processo"]:
        myReg["uniformizacao"] = classe["Uniformização do processo"]
            
    # DF ------------------------------------------------------
    if classe["Destino final"]:
        myReg['df'] = {}
        df = brancos.sub('', classe["Destino final"]).upper()
        # Verifica-se se tem alguma coisa
        if re.search(r'C|CP|E|NE', df):
            myReg['df']['valor'] = df
        else: 
            if myReg["estado"]!='H':
                ListaErros.append('Erro::' + myReg['codigo'] + '::Valor inválido para o DF::' + df)
    # Nota ao DF ------------------------------------------------------
    if "Nota ao DF" in classe.keys() and classe["Nota ao DF"]:
        myReg['df']['nota'] = brancos.sub('', classe["Nota ao DF"])
    # ERRO: um dos dois, DF ou Nota ao DF, tem de ter um valor válido
    if myReg["estado"]!='H' and classe["Destino final"] and (myReg['df']['valor'] == "NE") and not myReg['df']['nota']:
        ListaErros.append('Erro::' + myReg['codigo'] + '::DF e Nota ao DF não podem ser simultaneamente inválidos')
    # Justificação do DF ----------------------------------------------
    if classe["Destino final"] and classe["Justificação DF"]:
        just = brancos.sub('', classe["Justificação DF"])
        just = sepExtra.sub('', just)
        myReg['df']['justificacao'] = just.split('#')
            
    if classe["Notas"]:
        myReg["Notas"] = classe["Notas"]