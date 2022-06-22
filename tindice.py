from itertools import islice
import pandas as pd
import json
import re

brancos = re.compile(r'\r\n|\n|\r|[ \u202F\u00A0]+$|^[ \u202F\u00A0]+')

def processSheet(sheet, nome):
    # Load one worksheet.
    fnome = nome.split("_")[0]
    ws = sheet
    data = ws.values
    cols = next(data)[0:]
    data = list(data)
    idx = list(range(len(data)))
    data = (islice(r, 0, None) for r in data)
    df = pd.DataFrame(data, index=idx, columns=cols)

    myClasse = []
    for index,row in df.iterrows():
        myReg = {}
        if row["Código"]:
            myReg["codigo"] = brancos.sub('', str(row["Código"]))
            myReg["termo"] = brancos.sub('', str(row["Termo"]))
            myClasse.append(myReg)

    outFile = open("./files/"+fnome+".json", "w", encoding="utf-8")
    json.dump(myClasse, outFile, indent = 4, ensure_ascii=False)
    print("Termos de índice extraídos: ", len(myClasse))
    outFile.close()