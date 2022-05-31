from itertools import islice
import pandas as pd
import json
import re

hreg = re.compile(r'[hH][aA][rR][mM][oO]?[nN]?')
ireg = re.compile(r'[iI][nN][Aa][tT]?[iI]?[vV]?')
n4 = re.compile(r'^\d{3}\.\d{1,3}\.\d{1,3}\.\d{1,4}$')
n3 = re.compile(r'^\d{3}\.\d{1,3}\.\d{1,3}$')
n2 = re.compile(r'^\d{3}\.\d{1,3}$')
n1 = re.compile(r'^\d{3}$')

brancos = re.compile(r'\r\n|\n|\r|[ \u202F\u00A0]+$|^[ \u202F\u00A0]+')
sepExtra = re.compile(r'#$|^#')

# Calcula e normaliza o estado da classe
def calcEstado(e):
    global hreg, ireg
    if e.strip() == '': 
        return 'A'
    elif hreg.search(e): 
        return 'H'
    elif ireg.search(e): 
        return 'I'
    else: 
        return 'Erro'
# --------------------------------------------------
#
# Calcula o nível da classe
def calcNivel(cod):
    res = 0
    if n4.fullmatch(cod):
        res = 4
    elif n3.fullmatch(cod):
        res = 3
    elif n2.fullmatch(cod):
        res = 2
    elif n1.fullmatch(cod):
        res = 1
    return res
# --------------------------------------------------
#
# Processa as notas de aplicação
from nanoid import generate

def procNotas(notas, codClasse, chave1=None, chave2=None):
    res = []
    if not chave1:
        chave1 = 'idNota'
    if not chave2:
        chave2 = 'nota'
    notas = brancos.sub('', notas)
    notas = sepExtra.sub('', notas)
    filtradas = notas.split('#')
    for na in filtradas:
        na = re.sub('\"', '\"', na)
        res.append({
            chave1: chave2 + '_' + codClasse + '_' + generate('1234567890abcdef', 12),
            chave2: na
        })      
    return res
# --------------------------------------------------
#
# Calcula um array de booleanos para as N3 com subdivisão
def calcSubdivisoes(df):
    indN3 = {}
    for index, row in df.iterrows():
        if row["Código"]:
            # Código -----
            codigo = re.sub(r'(\r\n|\n|\r)','', str(row["Código"]))
            # Nível -----
            nivel = calcNivel(codigo)
            if nivel == 3:
                indN3[codigo] = False
            elif nivel == 4:
                pai = re.search(r'^(\d{3}\.\d{1,3}\.\d{1,3})\.\d{1,4}$', codigo).group(1)
                indN3[pai] = True
    return indN3

def processSheet(sheet, nome):
    # Carregam-se os catálogos 
    # --------------------------------------------------
    ecatalog = open('./files/entCatalog.json')
    tcatalog = open('./files/tipCatalog.json')
    lcatalog = open('./files/legCatalog.json')
    entCatalog = json.load(ecatalog)
    tipCatalog = json.load(tcatalog)
    legCatalog = json.load(lcatalog)
    # Tipos de intervenção
    # --------------------------------------------------
    intervCatalog = ['Apreciar','Assessorar','Comunicar','Decidir','Executar','Iniciar']
    
    # Load one worksheet.
    # --------------------------------------------------
    fnome = nome.split("_")[0]
    print("# Migração da Classe  " + fnome + "----------------------")
    ws = sheet
    data = ws.values
    cols = next(data)[0:]
    data = list(data)
    idx = list(range(len(data)))
    data = (islice(r, 0, None) for r in data)
    df = pd.DataFrame(data, index=idx, columns=cols)

    myClasse = []
    ListaErros = []
    ProcHarmonizacao = []
    indN3 = calcSubdivisoes(df)

    for index, row in df.iterrows():
        myReg = {}
        if row["Código"]:
            # Código -----
            myReg["codigo"] = re.sub(r'(\r\n|\n|\r)','', str(row["Código"]))
            # Nível -----
            myReg["nivel"] = calcNivel(myReg["codigo"])
            # Estado -----
            if row["Estado"]:
                myReg["estado"] = calcEstado(row["Estado"])
                if myReg["estado"] == 'H':
                    ProcHarmonizacao.append( myReg["codigo"])
            else:
                myReg["estado"] = 'A'
            # Título -----
            if row["Título"]:
                myReg["titulo"] = brancos.sub('', row["Título"])
            else:
                if myReg["estado"] != 'H':
                    ListaErros.append('Erro::' + myReg['codigo'] + '::classe sem título')
            # Descrição -----
            myReg["descricao"] = row["Descrição"]
            # Notas de aplicação -----
            if row["Notas de aplicação"]:
                myReg["notasAp"] = procNotas(row["Notas de aplicação"], myReg["codigo"])
            # Exemplos de notas de aplicação -----
            if row["Exemplos de NA"]:
                myReg["exemplosNotasAp"] = procNotas(row["Exemplos de NA"], myReg["codigo"], 'idExemplo', 'exemplo')
            # Notas de exclusão -----
            if row["Notas de exclusão"]:
                myReg["notasEx"] = procNotas(row["Notas de exclusão"], myReg["codigo"])
            # Tipo de processo -----
            if row["Tipo de processo"]:
                myReg['tipoProc'] = brancos.sub('', row["Tipo de processo"])
                if myReg["estado"]!='H' and myReg["nivel"]==3 and myReg['tipoProc'] not in ['PC','PE']:
                    ListaErros.append('Erro::' + myReg['codigo'] + '::tipo de processo desconhecido::' + myReg['tipoProc'])
            else:
                if myReg["estado"]!='H' and myReg["nivel"]==3 and myReg['estado'] != 'H':
                    ListaErros.append('Erro::' + myReg['codigo'] + '::tipo de processo não preenchido')
            # Transversalidade -----
            if myReg["nivel"]==3 and row["Processo transversal (S/N)"]:
                myReg['procTrans'] = brancos.sub('', row["Processo transversal (S/N)"])
                if myReg["estado"]!='H' and myReg['procTrans'] not in ['S','N']:
                    ListaErros.append('Erro::' + myReg['codigo'] + '::transversalidade desconhecida::' + myReg['procTrans'])
            # Donos -----
            if row["Dono do processo"]:
                donos = brancos.sub('', row["Dono do processo"])
                donos = sepExtra.sub('', donos)
                myReg['donos'] = donos.split('#')
            # ERRO: Verificação da existência dos donos no catálogo de entidades e/ou tipologias
                for d in myReg['donos']:
                    if (d not in entCatalog) and (d not in tipCatalog):
                        ListaErros.append('Erro::' + myReg['codigo'] + '::Entidade dono não está no catálogo de entidades ou tipologias::' + d)
            # ERRO: Um processo tem que ter sempre donos
            elif myReg["nivel"]==3 and myReg['estado'] != 'H':
                ListaErros.append('Erro::' + myReg['codigo'] + '::Este processo não tem donos identificados.')
            # Participantes -----
            if row["Participante no processo"]:
                participantes = brancos.sub('', row["Participante no processo"])
                participantes = sepExtra.sub('', participantes)
                lparticipantes = participantes.split('#')
                myReg['participantes'] = []
                for p in lparticipantes:
                    myReg['participantes'].append({'id': p})
            # ERRO: Verificação da existência dos participantes no catálogo de entidades e/ou tipologias
                for part in myReg['participantes']:
                    if (part['id'] not in entCatalog) and (part['id'] not in tipCatalog):
                        ListaErros.append('Erro::' + myReg['codigo'] + '::Entidade dono não está no catálogo de entidades ou tipologias::' + part['id'])
            # ERRO: Um processo transversal tem que ter participantes
            elif myReg["nivel"] == 3 and myReg['estado'] != 'H' and myReg['procTrans'] == 'S':
                ListaErros.append('Erro::' + myReg['codigo'] + '::Este processo é transversal mas não tem participantes identificados.')   
            # Tipo de intervenção -----
            linterv = []
            if row["Tipo de intervenção do participante"]:
                interv = brancos.sub('', row["Tipo de intervenção do participante"])
                interv = re.sub(r'[ ]+','',interv)
                interv = sepExtra.sub('', interv)
                linterv = interv.split('#')
            # ERRO: Verificação da existência do tipo de intervenção no catálogo de intervenções
                for i in linterv:
                    if i not in intervCatalog:
                        ListaErros.append('Erro::' + myReg['codigo'] + '::Tipo de intervenção não está no catálogo de intervenções::' + i)
            # ERRO: Participantes e intervenções têm de ter a mesma cardinalidade
            if row["Participante no processo"] and row["Tipo de intervenção do participante"]:
                if myReg["estado"]!='H' and len(myReg['participantes']) != len(linterv):
                    ListaErros.append('Erro::' + myReg['codigo'] + '::Participantes e intervenções não têm a mesma cardinalidade')
                elif len(myReg['participantes']) == len(linterv):
                    for index, i in enumerate(linterv):
                        myReg['participantes'][index]['interv'] = i
                else:
                    ListaErros.append('Erro::' + myReg['codigo'] + '::Processo em harmonização e participantes e intervenções não têm a mesma cardinalidade, estas não foram migradas')
            # Legislação -----
            if row["Diplomas jurídico-administrativos REF"]:
                leg = brancos.sub('', row["Diplomas jurídico-administrativos REF"])
                leg = sepExtra.sub('', leg)
                myReg['legislacao'] = leg.split('#')
                nova =[]
                # Limpeza e normalização dos ids da legislação
                for l in myReg['legislacao']:
                    limpa = re.sub(r'([ \u202F\u00A0]+)|([ \u202F\u00A0]*,[ \u202F\u00A0]*)', '_', brancos.sub('', l))
                    nova.append(limpa)
                myReg['legislacao'] = nova
            # ERRO: Verificação da existência da legislação no catálogo legislativo
                for l in myReg['legislacao']:
                    if l not in legCatalog:
                        ListaErros.append('Erro::' + myReg['codigo'] + '::Legislação inexistente no catálogo legislativo::' + l)
            # Processos Relacionados -----
            if row["Código do processo relacionado"]:
                proc = brancos.sub('', row["Código do processo relacionado"])
                proc = sepExtra.sub('', proc)
                myReg['processosRelacionados'] = proc.split('#')
            # Tipo de relação entre processos -----
            if row["Tipo de relação entre processos"]:
                procRel = brancos.sub('', row["Tipo de relação entre processos"])
                procRel = sepExtra.sub('', procRel)
                myReg['proRel'] = procRel.split('#')
                # Normalização do tipo de relação
                normalizadas = []
                for rel in myReg['proRel']:
                    if re.search(r'S[íi]ntese[ ]*\(s[ií]ntetizad[oa](\s+por)?\)', rel, re.I):
                        normalizadas.append('eSintetizadoPor')
                    elif re.search(r'S[íi]ntese[ ]*\(sintetiza\)', rel, re.I):
                        normalizadas.append('eSinteseDe')
                    elif re.search(r'Complementar', rel, re.I):
                        normalizadas.append('eComplementarDe')
                    elif re.search(r'\s*Cruzad', rel, re.I):
                        normalizadas.append('eCruzadoCom')
                    elif re.search(r'\s*Suplement.?\s*de', rel, re.I):
                        normalizadas.append('eSuplementoDe')
                    elif re.search(r'\s*Suplement.?\s*para', rel, re.I):
                        normalizadas.append('eSuplementoPara')
                    elif re.search(r'Sucessão[ ]*\(suce', rel, re.I):
                        normalizadas.append('eSucessorDe')
                    elif re.search(r'\s*Sucessão\s*\(antece', rel, re.I):
                        normalizadas.append('eAntecessorDe')
                    else:
                        normalizadas.append(rel)
                        ListaErros.append('Erro::' + myReg['codigo'] + '::Relação entre processos desconhecida::' + rel)
                    myReg['proRel'] = normalizadas
            # ERRO: Processos e Relações têm de ter a mesma cardinalidade
            if row["Código do processo relacionado"] and row["Tipo de relação entre processos"]:
                if myReg["estado"]!='H' and len(myReg['processosRelacionados']) != len(myReg['proRel']):
                    ListaErros.append('Erro::' + myReg['codigo'] + '::Processos relacionados e respetivas relações não têm a mesma cardinalidade')
            # PCA -----
            if row["Prazo de conservação administrativa"] and myReg['nivel'] >= 3:
                myReg['pca'] = {}
                if type(row["Prazo de conservação administrativa"]) not in [int, float]:
                    pca = brancos.sub('', row["Prazo de conservação administrativa"])
                else:
                    pca = row["Prazo de conservação administrativa"]
                # Verifica-se se tem alguma coisa
                if pd.isna(pca):
                    myReg['pca']['valores'] = "NE"
                else: 
                    if type(row["Prazo de conservação administrativa"]) not in [int, float]:
                        if re.search(r'\d+', pca):
                            myReg['pca']['valores'] = pca
                        else:
                            myReg['pca']['valores'] = "NE"
                    else:
                        myReg['pca']['valores'] = pca
            if row["Nota ao PCA"] and myReg['nivel'] >= 3:
                myReg['pca']['notas'] = brancos.sub('', row["Nota ao PCA"])
            # ERRO: um dos dois, PCA ou Nota ao PCA, tem de ter um valor válido
            if myReg["estado"]!='H' and ((myReg['nivel'] > 3) or (myReg['nivel'] == 3 and not indN3[myReg['codigo']])):
                if row["Prazo de conservação administrativa"] and (myReg['pca']['valores'] == "NE") and 'notas' not in myReg['pca'].keys():
                    ListaErros.append('Erro::' + myReg['codigo'] + '::PCA e Nota ao PCA não podem ser simultaneamente inválidos')
            # Forma de Contagem do PCA -----
            if 'pca' in myReg.keys():
                formaContagem = brancos.sub('', str(row["Forma de contagem do PCA"]))
                if re.search(r'conclusão.*procedimento', formaContagem, re.I):
                    myReg['pca']['formaContagem'] = 'conclusaoProcedimento'
                elif re.search(r'cessação.*vigência', formaContagem, re.I):
                    myReg['pca']['formaContagem'] = 'cessacaoVigencia'
                elif re.search(r'extinção.*entidade', formaContagem, re.I):
                    myReg['pca']['formaContagem'] = 'extincaoEntidade'
                elif re.search(r'extinção.*direito', formaContagem, re.I):
                    myReg['pca']['formaContagem'] = 'extincaoDireito'
                elif re.search(r'disposição.*legal', formaContagem, re.I):
                    myReg['pca']['formaContagem'] = 'disposicaoLegal'
                elif re.search(r'início.*procedimento', formaContagem, re.I):
                    myReg['pca']['formaContagem'] = 'inicioProcedimento'
                elif re.search(r'emissão.*título', formaContagem, re.I):
                    myReg['pca']['formaContagem'] = 'emissaoTitulo'
                else:
                    myReg['pca']['formaContagem'] = "Desconhecida"
                    ListaErros.append('Erro::' + myReg['codigo'] + '::Forma de contagem do PCA desconhecida::' + formaContagem)
            # Justificação do PCA -----
            if 'pca' in myReg.keys() and row["Justificação PCA"]:
                just = brancos.sub('', row["Justificação PCA"])
                just = sepExtra.sub('', just)
                myReg['pca']['justificacao'] = just.split('#')

            if row["Dimensão qualitativa do processo"]:
                myReg["Dimensão qualitativa do processo"] = row["Dimensão qualitativa do processo"]
            if row["Uniformização do processo"]:
                myReg["Uniformização do processo"] = row["Uniformização do processo"]
            
            # DF -----
            if row["Destino final"]:
                myReg['df'] = {}
                df = brancos.sub('', row["Destino final"].strip()).upper()
                # Verifica-se se tem alguma coisa
                if re.search(r'C|CP|E|NE', df):
                    myReg['df']['valor'] = df
                else: 
                    if myReg["estado"]!='H':
                        ListaErros.append('Erro::' + myReg['codigo'] + '::Valor inválido para o DF::' + df)
            if "Nota ao DF" in row.keys() and row["Nota ao DF"]:
                myReg['df']['nota'] = brancos.sub('', row["Nota ao DF"].strip())
            # ERRO: um dos dois, DF ou Nota ao DF, tem de ter um valor válido
            if (myReg['nivel'] > 3) or (myReg['nivel'] == 3 and not indN3[myReg['codigo']]):
                if myReg["estado"]!='H' and row["Destino final"] and (myReg['df']['valor'] == "NE") and not myReg['df']['nota']:
                    ListaErros.append('Erro::' + myReg['codigo'] + '::DF e Nota ao DF não podem ser simultaneamente inválidos')
            # Justificação do DF -----
            if row["Destino final"] and row["Justificação DF"]:
                just = brancos.sub('', row["Justificação DF"])
                just = sepExtra.sub('', just)
                myReg['df']['justificacao'] = just.split('#')
            
            if row["Notas"]:
                myReg["Notas"] = row["Notas"]
            myClasse.append(myReg)

    outFile = open("./files/"+fnome+".json", "w", encoding="utf-8")
    json.dump(myClasse, outFile, indent = 4, ensure_ascii=False)
    print("Classe extraída: ", nome, " :: ", len(myClasse))
    if len(ListaErros) > 0:
        print("Erros: ")
        print('\n'.join(ListaErros))
    if len(ProcHarmonizacao) > 0:
        print("Processos em Harmonização: ")
        print('\n'.join(ProcHarmonizacao))
    outFile.close()
    print("# FIM: Migração da Classe  " + fnome + "-----------------")