import re
brancos = re.compile(r'\r\n|\n|\r|[ \u202F\u00A0]+$|^[ \u202F\u00A0]+')
sepExtra = re.compile(r'#$|^#')

def procContexto(classe, myReg, ListaErros, entCatalog, tipCatalog, legCatalog):
    # Tipos de intervenção
    # --------------------------------------------------
    intervCatalog = ['Apreciar','Assessorar','Comunicar','Decidir','Executar','Iniciar']
    # --------------------------------------------------
    # Tipo de processo -----
    if classe["Tipo de processo"]:
        myReg['tipoProc'] = brancos.sub('', str(classe["Tipo de processo"]))
        if myReg["estado"]!='H' and myReg['tipoProc'] not in ['PC','PE']:
            ListaErros.append('Erro::' + myReg['codigo'] + '::Tipo de processo desconhecido::' + myReg['tipoProc'])
        elif myReg["estado"]!='H' and myReg['tipoProc'] == '':
            ListaErros.append('Erro::' + myReg['codigo'] + '::tipo de processo não preenchido::' + myReg['tipoProc'])
    # Transversalidade -----
    if classe["Processo transversal (S/N)"]:
        myReg['procTrans'] = brancos.sub('', classe["Processo transversal (S/N)"])
        if myReg["estado"]!='H' and myReg['procTrans'] not in ['S','N']:
            ListaErros.append('Erro::' + myReg['codigo'] + '::transversalidade desconhecida::' + myReg['procTrans'])
    # Donos -----
    if classe["Dono do processo"]:
        donos = brancos.sub('', classe["Dono do processo"])
        donos = sepExtra.sub('', donos)
        myReg['donos'] = donos.split('#')
        # ERRO: Verificação da existência dos donos no catálogo de entidades e/ou tipologias
        for d in myReg['donos']:
            if (d not in entCatalog) and (d not in tipCatalog):
                ListaErros.append('Erro::' + myReg['codigo'] + '::Entidade dono não está no catálogo de entidades ou tipologias::' + d)
            # ERRO: Um processo tem que ter sempre donos
        if myReg['estado'] != 'H' and len(myReg['donos']) == 0:
            ListaErros.append('Erro::' + myReg['codigo'] + '::Este processo não tem donos identificados.')
    # Participantes -----
    if classe["Participante no processo"]:
        participantes = brancos.sub('', classe["Participante no processo"])
        participantes = sepExtra.sub('', participantes)
        lparticipantes = participantes.split('#')
        myReg['participantes'] = []
        for p in lparticipantes:
            myReg['participantes'].append({'id': brancos.sub('', p)})
        # ERRO: Verificação da existência dos participantes no catálogo de entidades e/ou tipologias
        for part in myReg['participantes']:
            if (part['id'] not in entCatalog) and (part['id'] not in tipCatalog):
                ListaErros.append('Erro::' + myReg['codigo'] + '::Entidade participante não está no catálogo de entidades ou tipologias::' + part['id'])
    # ERRO: Um processo transversal tem que ter participantes
    if myReg['estado'] != 'H' and myReg['procTrans'] == 'S' and len(myReg['participantes']) == 0:
        ListaErros.append('Erro::' + myReg['codigo'] + '::Este processo é transversal mas não tem participantes identificados.')   
    # Tipo de intervenção -----
    linterv = []
    if classe["Tipo de intervenção do participante"]:
        interv = brancos.sub('', classe["Tipo de intervenção do participante"])
        interv = re.sub(r'[ ]+','',interv)
        interv = sepExtra.sub('', interv)
        linterv = interv.split('#')
        # ERRO: Verificação da existência do tipo de intervenção no catálogo de intervenções
        for i in linterv:
            if i not in intervCatalog:
                ListaErros.append('Erro::' + myReg['codigo'] + '::Tipo de intervenção não está no catálogo de intervenções::' + i)
            # ERRO: Participantes e intervenções têm de ter a mesma cardinalidade
            if classe["Participante no processo"] and classe["Tipo de intervenção do participante"]:
                if myReg["estado"]!='H' and len(myReg['participantes']) != len(linterv):
                    ListaErros.append('Erro::' + myReg['codigo'] + '::Participantes e intervenções não têm a mesma cardinalidade')
                elif len(myReg['participantes']) == len(linterv):
                    for index, i in enumerate(linterv):
                        myReg['participantes'][index]['interv'] = i
                else:
                    ListaErros.append('Erro::' + myReg['codigo'] + '::Processo em harmonização e participantes e intervenções não têm a mesma cardinalidade, estas não foram migradas')
    # Legislação -----
    if classe["Diplomas jurídico-administrativos REF"]:
        leg = brancos.sub('', classe["Diplomas jurídico-administrativos REF"])
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
    if classe["Código do processo relacionado"]:
        proc = brancos.sub('', classe["Código do processo relacionado"])
        proc = sepExtra.sub('', proc)
        myReg['processosRelacionados'] = proc.split('#')
    # Tipo de relação entre processos -----
    if classe["Tipo de relação entre processos"]:
        procRel = brancos.sub('', classe["Tipo de relação entre processos"])
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
    if classe["Código do processo relacionado"] and classe["Tipo de relação entre processos"]:
        if myReg["estado"]!='H' and len(myReg['processosRelacionados']) != len(myReg['proRel']):
            ListaErros.append('Erro::' + myReg['codigo'] + '::Processos relacionados e respetivas relações não têm a mesma cardinalidade')
            