import json

def classeGenTTL(c):
    fin = open('./files/' + c + '.json')
    fout = open(c + '.ttl', 'w')
    classes = json.load(fin)

    # Carregam-se os catálogos 
    # --------------------------------------------------
    ecatalog = open('./files/entCatalog.json')
    tcatalog = open('./files/tipCatalog.json')
    lcatalog = open('./files/legCatalog.json')
    entCatalog = json.load(ecatalog)
    tipCatalog = json.load(tcatalog)
    legCatalog = json.load(lcatalog)
    # Correspondência de intervenções e relações
    intervCatalog = {'Apreciar': 'temParticipanteApreciador','Assessorar': 'temParticipanteAssessor',
                    'Comunicar': 'temParticipanteComunicador','Decidir': 'temParticipanteDecisor',
                    'Executar': 'temParticipanteExecutor','Iniciar': 'temParticipanteIniciador'}
    
    for classe in classes:
        # codigo, estado, nível e título
        ttl = f"""
###  http://jcr.di.uminho.pt/m51-clav#c{ classe['codigo'] }
:c{ classe['codigo'] } rdf:type owl:NamedIndividual ;
\t:classeStatus '{ classe['estado'] }';
\trdf:type :Classe_N{classe['nivel']} ;
\t:codigo '{ classe['codigo'] }' ;
\t:titulo '{ classe['titulo'] }' ;\n"""
        # Relação hierárquica-------------------------------
        if classe['nivel'] == 1:
            ttl += "\t:pertenceLC :lc1 ;\n"
            ttl += "\t:temPai :lc1 ;\n"
        elif classe['nivel'] in [2,3,4]:
            partes = classe['codigo'].split('.')
            pai = '.'.join(partes[0:-1])
            ttl += "\t:pertenceLC :lc1 ;\n"
            ttl += "\t:temPai :c" + pai + " ;\n"
        # ------------------------------------------------
        # Descrição
        if classe["descricao"]:
            ttl += "\t:descricao '" + classe["descricao"] + "' .\n"
        # ------------------------------------------------
        # Notas de Aplicação -----------------------------
        if 'notasAp' in classe.keys():
            for n in classe['notasAp']:
                ttl += "###  http://jcr.di.uminho.pt/m51-clav#" + n['idNota'] + "\n"
                ttl += ":" + n['idNota'] + " rdf:type owl:NamedIndividual ,\n"
                ttl += "\t\t:NotaAplicacao ;\n"
                ttl += "\t:rdfs:label \"Nota de Aplicação\";\n"
                ttl += "\t:conteudo " + "\"" + n['nota'] + "\".\n\n"
                # criar as relações com das notas de aplicação com a classe
                ttl += ":c" + classe['codigo'] +" :temNotaAplicacao " + ":" + n['idNota'] + " .\n\n"
        # ------------------------------------------------
        # Exemplos de Notas de Aplicação -----------------
        if 'exemplosNotasAp' in classe.keys():
            for e in classe['exemplosNotasAp']:
                ttl += "###  http://jcr.di.uminho.pt/m51-clav#" + e['idExemplo'] + "\n"
                ttl += ":" + e['idExemplo'] + " rdf:type owl:NamedIndividual ,\n"
                ttl += "\t\t:ExemploNotaAplicacao ;\n"
                ttl += "\t:rdfs:label \"Exemplo de nota de aplicação\";\n"
                ttl += "\t:conteudo " + "\"" + e['exemplo'] + "\".\n\n"
                # criar as relações com das notas de aplicação com a classe
                ttl += ":c" + classe['codigo'] +" :temExemploNA " + ":" + e['idExemplo'] + " .\n\n"
        # ------------------------------------------------
        # Notas de Exclusão ------------------------------
        if 'notasEx' in classe.keys():
            for n in classe['notasEx']:
                ttl += "###  http://jcr.di.uminho.pt/m51-clav#" + n['idNota'] + "\n"
                ttl += ":" + n['idNota'] + " rdf:type owl:NamedIndividual ,\n"
                ttl += "\t\t:NotaExclusao ;\n"
                ttl += "\t:rdfs:label \"Nota de Exclusão\";\n"
                ttl += "\t:conteudo " + "\"" + n['nota'] + "\".\n\n"
                # criar as relações com das notas de aplicação com a classe
                ttl += ":c" + classe['codigo'] + " :temNotaExclusao " + ":" + n['idNota'] + " .\n\n"
        # ------------------------------------------------
        # Tipo de Processo -------------------------------
        if 'tipoProc' in classe.keys():
            if classe['tipoProc'] == 'PC':
                ttl += ":c" + classe['codigo'] + " :processoTipoVC :vc_processoTipo_pc .\n"
            else:
                ttl += ":c" + classe['codigo'] + " :processoTipoVC :vc_processoTipo_pe .\n"
        # ------------------------------------------------
        # Transversalidade -------------------------------
        if 'procTrans' in classe.keys():
            ttl += ":c" + classe['codigo'] + " :processoTransversal " + "\"" + classe['procTrans'] + "\" .\n"
        # ------------------------------------------------
        # Donos
        # ------------------------------------------------
        if 'donos' in classe.keys():
            for d in classe['donos']:
                if d in entCatalog:
                    prefixo = 'ent_'
                else:
                    prefixo = 'tip_'
                ttl += ":c" + classe['codigo'] + " :temDono" + " :" + prefixo + d + " .\n"
        # ------------------------------------------------
        # Participantes ----------------------------------
        # Um processo tem participantes se for transversal
        if 'procTrans' in classe.keys() and classe['procTrans'] == 'S':
            for p in classe['participantes']:
                if p['id'] in entCatalog:
                    prefixo = 'ent_'
                else:
                    prefixo = 'tip_'
                ttl += ":c" + classe['codigo'] + " :" + intervCatalog[p['interv']] + " :" + prefixo + p['id'] + " .\n"
        # ------------------------------------------------
        # Legislação -------------------------------------
        if 'legislacao' in classe.keys():
            for l in classe['legislacao']:
                if l in legCatalog:
                    ttl += ":c" + classe['codigo'] + " :temLegislacao" + " :" + l + " .\n"
        # ------------------------------------------------------------
        # Processos Relacionados -------------------------------------
        if 'processosRelacionados' in classe.keys():
            for index, p in enumerate(classe['processosRelacionados']):
                ttl += ":c" + classe['codigo'] + " :temRelProc" + " :c" + p + " .\n"
                ttl += ":c" + classe['codigo'] + " :" + classe['proRel'][index] + " :c" + p + " .\n"
        # ------------------------------------------------------------
        # PCA --------------------------------------------------------
        if 'pca' in classe.keys():
            ttl += "###  http://jcr.di.uminho.pt/m51-clav#pca_c" + classe['codigo'] + "\n"
            ttl += ":" + classe['codigo'] + " rdf:type owl:NamedIndividual ,\n"
            ttl += "\t:PCA ;\n"
            if type(classe['pca']['valores']) != list:
                ttl += "\t:pcaValor " + str(classe['pca']['valores']) + ";\n"
            else:
                for v in classe['pca']['valores']:
                    ttl += "\t:pcaValor " + str(v) + ";\n"
    


        fout.write(ttl)
    
    fin.close()
    fout.close()

classeGenTTL('400')

    