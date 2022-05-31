from itertools import islice
import pandas as pd
import json

import re
brancos = re.compile(r'\r\n|\n|\r|[ \u202F\u00A0]+$|^[ \u202F\u00A0]+')
sepExtra = re.compile(r'#$|^#')

def processSheet(sheet, nome):
    print("# Migração do Catálogo Legislativo ---------------------------")
    # Carregam-se os catálogos de entidades e tipologias
    # --------------------------------------------------
    ecatalog = open('./files/entCatalog.json')
    tcatalog = open('./files/tipCatalog.json')
    entCatalog = json.load(ecatalog)
    tipCatalog = json.load(tcatalog)
    # Load one worksheet.
    fnome = nome.split("_")[0]
    ws = sheet
    data = ws.values
    cols = next(data)[0:]
    data = list(data)
    idx = list(range(len(data)))
    data = (islice(r, 0, None) for r in data)
    df = pd.DataFrame(data, index=idx, columns=cols)

    ListaErros = []
    legCatalog = []
    myLeg = []
    for index, row in df.iterrows():
        myReg = {}
        if row["Tipo"] and str(row["Tipo"]) != 'NaT':
            # Tipo: ------------------------------------------------------
            myReg["tipo"] = brancos.sub('', str(row["Tipo"]))
            # Número: ----------------------------------------------------
            if row["Número"]:
                myReg["numero"] = brancos.sub('', str(row["Número"]))
                myReg["numero"] = re.sub(r'[ \u202F\u00A0]+', '_', myReg["numero"])
            # Entidades:--------------------------------------------------
            filtradas = []
            if row["Entidade"]:
                entidades = brancos.sub('', str(row["Entidade"])).split(',') 
                filtradas = list(filter(lambda e: e != '' and e != 'NaT', entidades))
                if len(filtradas)> 0:
                    myReg["entidade"] = []
                    for e in filtradas:
                        myReg["entidade"].append(brancos.sub('', e))
            if len(filtradas)> 0:
            # Cálculo do id/código da legislação: tipo + entidades + numero -------------------------
                legCod = re.sub(r'[ ]+', '_', myReg["tipo"]) + '_' + '_'.join(myReg["entidade"]) + '_' + myReg["numero"]
            # ERRO: Verificação da existência das entidades no catálogo de entidades e/ou tipologias
                for e in myReg['entidade']:
                    if (e not in entCatalog) and (e not in tipCatalog):
                        ListaErros.append('Erro::' + legCod + '::Entidade não está no catálogo de entidades ou tipologias::' + e)
            else:
                legCod = re.sub(r'[ \u202F\u00A0]+', '_', myReg["tipo"]) + '_' + myReg["numero"]
            # ERRO: Legislação duplicada ---------------------------------
            myReg['codigo'] = legCod
            if legCod not in legCatalog:
                legCatalog.append(legCod)
            else:
                ListaErros.append('Erro::' + legCod + '::Legislação duplicada.')
            # Estado: ----------------------------------------------------
            if row['Estado'] and str(row['Estado']).strip() != "":
                myReg["estado"] = 'R'
            else:
                myReg["estado"] = 'A'
            # Data:-------------------------------------------------------
            if row["Data"] and (not pd.isnull(row["Data"])):
                myReg["data"] = row["Data"].isoformat()[:10]
            # Sumário:----------------------------------------------------
            if row["Sumário"]:
                myReg["sumario"] = brancos.sub('', str(row["Sumário"]))
            # Fonte:------------------------------------------------------
            if row["Fonte"]:
                myReg["fonte"] = brancos.sub('', str(row["Fonte"])).strip()
            # Link:-------------------------------------------------------
            if row["Link"]:
                myReg["link"] = brancos.sub('', str(row["Link"])).strip()
            
            myLeg.append(myReg)

    outFile = open("./files/"+fnome+".json", "w", encoding="utf-8")
    json.dump(myLeg, outFile, indent = 4, ensure_ascii=False)
    print("Documentos legislativos extraídos: ", len(myLeg))
    outFile.close()
    catalog = open("./files/legCatalog.json", "w", encoding="utf-8")
    json.dump(legCatalog, catalog, indent = 4, ensure_ascii=False)
    print("Catálogo de legislação criado.")
    if len(ListaErros) > 0:
        print("Erros: ")
        print('\n'.join(ListaErros))
    print("# FIM: Migração do Catálogo Legislativo ----------------------")