from itertools import islice
import pandas as pd
import json

import re
brancos = re.compile(r'\r\n|\n|\r|[ \u202F\u00A0]+$|^[ \u202F\u00A0]+')
sepExtra = re.compile(r'#$|^#')

def processSheet(sheet, nome):
    print("# Migração do Catálogo de Entidades ----------------------")
    # Load one worksheet.
    fnome = nome.split("_")[0]
    ws = sheet
    data = ws.values
    cols = next(data)[0:]
    data = list(data)
    idx = list(range(len(data)))
    data = (islice(r, 0, None) for r in data)
    df = pd.DataFrame(data, index=idx, columns=cols)
    
    entCatalog = []
    myEntidade = []
    for index, row in df.iterrows():
        myReg = {}
        if row["Sigla"]:
            myReg["sigla"] = brancos.sub('', str(row["Sigla"]))
            entCatalog.append(myReg["sigla"])
            if row["Estado"]:
               myReg["estado"] = brancos.sub('', str(row["Estado"]))
            if row["ID SIOE"]:
                myReg["sioe"] = brancos.sub('', str(row["ID SIOE"]))
            if row["Designação"]:
                myReg["designacao"] = brancos.sub('', str(row["Designação"]))
            if row["Tipologia de Entidade"]:
                tipologias = brancos.sub('', str(row["Tipologia de Entidade"]))
                tipologias = sepExtra.sub('', tipologias)
                myReg['tipologias'] = tipologias.split('#')
            if row["Internacional"]:
                myReg["internacional"] = brancos.sub('', str(row["Internacional"]))
            if row["Data de criação"] and (not pd.isnull(row["Data de criação"])):
                myReg["dataCriacao"] = str(row["Data de criação"].isoformat())
            if row["Data de extinção"] and (not pd.isnull(row["Data de extinção"])):
                myReg["dataExtincao"] = str(row["Data de extinção"].isoformat())
            
            myEntidade.append(myReg)

    outFile = open("./files/ent.json", "w", encoding="utf-8")
    json.dump(myEntidade, outFile, indent = 4, ensure_ascii=False)
    print("Entidades extraídas: ", len(myEntidade))
    outFile.close()
    catalog = open("./files/entCatalog.json", "w", encoding="utf-8")
    json.dump(entCatalog, catalog, indent = 4, ensure_ascii=False)
    print("Catálogo de entidades criado.")
    print("# FIM: Migração do Catálogo de Entidades -----------------")