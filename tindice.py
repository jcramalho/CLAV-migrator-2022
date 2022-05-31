from itertools import islice
import pandas as pd
import json

def processSheet(sheet, nome):
    # Load one worksheet.
    fnome = nome.split("_")[0]
    ws = sheet
    data = ws.values
    cols = next(data)[1:]
    data = list(data)
    idx = [r[0] for r in data]
    data = (islice(r, 1, None) for r in data)
    df = pd.DataFrame(data, index=idx, columns=cols)

    myClasse = []
    for index, row in df.iterrows():
        myReg = {}
        if row["Código"]:
            myReg["Código"] = row["Código"]
            myReg["Termo"] = row["Termo"]
            myClasse.append(myReg)

    outFile = open("./files/"+fnome+".json", "w", encoding="utf-8")
    json.dump(myClasse, outFile, indent = 4)
    print("Termos de índice extraídos: ", len(myClasse))
    outFile.close()