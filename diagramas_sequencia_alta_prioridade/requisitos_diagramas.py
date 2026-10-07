"""Diagramas de sequência de projeto: colaboração entre instâncias internas."""

def call(a,b,method,result,body=()):
    return [('m',a,b,method), *body, ('r',b,a,result)]

def frame(kind,guard,body):
    return [(kind,guard),*body,('end',)]

def alt(guard,yes,other,no):
    return [('alt',guard),*yes,('else',other),*no,('end',)]

def diagram(slug,rf,participants,body):
    return (slug,rf,'',participants,body,'')

DIAGRAMAS = [
 diagram('01_gerenciar_provas','RF02',[
 ('Administrador','actor'),(':TelaProva','boundary'),(':ControladorProva','control'),
 (':RepositorioProva','entity'),('prova:Prova','entity'),('criterios:CriteriosPontuacao','entity')],
 call(0,1,'confirmarConfiguracao(dados)','exibirRetorno(retorno)',
 call(1,2,'salvarConfiguracao(dados)','retorno',
 call(2,3,'buscarPorId(dados.provaId)','prova ou nulo')+
 alt('prova == nulo',
 call(2,4,'inicializar(id, olimpiadaId, categoriaId)','prova, vinculoValido'),
 'prova != nulo',call(2,4,'verificarVinculo(olimpiadaId, categoriaId)','vinculoValido'))+
 call(2,5,'validar(dados.regras)','errosRegras')+
 call(2,4,'validarConfiguracao(dados)','errosProva')+
 alt('erros vazios e vinculo valido',
 call(2,5,'configurar(dados.regras)','criterios')+
 call(2,4,'configurar(dados, criterios)','provaAtualizada')+
 call(2,3,'salvar(provaAtualizada)','idProva'),
 'configuracao invalida',call(2,2,'montarErros(errosRegras, errosProva, vinculoValido)','retornoErro'))))),
 diagram('02_cadastrar_gabarito','RF03',[
 ('Administrador','actor'),(':TelaGabarito','boundary'),(':ControladorGabarito','control'),
 (':RepositorioProva','entity'),('prova:Prova','entity'),('gabarito:Gabarito','entity'),('questao:Questao','entity')],
 call(0,1,'confirmarCadastro(provaId, itens)','exibirRetorno(retorno)',
 call(1,2,'cadastrar(provaId, itens)','retorno',
 call(2,3,'buscarPorId(provaId)','prova ou nulo')+
 alt('prova encontrada',
 call(2,5,'preparar(provaId)','gabaritoEmEdicao')+
 frame('loop','para cada item do gabarito',
 call(2,4,'obterQuestao(item.numero)','questao')+
 call(2,6,'validarAlternativas(item.aceitas)','erros')+
 alt('alternativas validas',call(2,5,'definirResposta(item.numero, item.aceitas)','respostaDefinida'),
 'alternativas invalidas',call(2,5,'registrarPendencia(item.numero, erros)','pendencia')))+
 call(2,5,'validarCompletude(prova)','pendencias')+
 alt('sem pendencias',call(2,4,'definirGabarito(gabarito)','provaAtualizada')+
 call(2,3,'salvar(provaAtualizada)','gabaritoSalvo'),
 'com pendencias',call(2,5,'listarPendencias()','pendencias')),
 'prova nao encontrada',call(2,2,'montarErroProvaInexistente(provaId)','retornoErro'))))),
 diagram('03_importar_respostas','RF05',[
 ('Administrador','actor'),(':TelaImportacao','boundary'),(':ControladorImportacao','control'),
 (':LeitorArquivo','control'),(':ValidadorRespostas','control'),(':RepositorioProva','entity'),
 (':RepositorioRespostas','entity'),('relatorio:RelatorioImportacao','entity')],
 call(0,1,'confirmarImportacao(provaId, arquivo)','exibirResumo(relatorio)',
 call(1,2,'importar(provaId, arquivo)','relatorio ou erro',
 call(2,3,'ler(arquivo)','registros ou erroFormato')+
 alt('arquivo valido',
 call(2,5,'buscarContexto(provaId)','prova, participantes, gabarito')+
 frame('loop','para cada registro',
 call(2,4,'validar(registro, contexto)','validacao')+
 alt('validacao permite registro',call(2,6,'salvar(provaId, registro, validacao)','respostaId')+
 call(2,7,'adicionarImportado(respostaId, validacao)','itemRegistrado'),
 'inconsistencia impeditiva',call(2,7,'adicionarFalha(registro.linha, validacao)','falhaRegistrada')))+
 call(2,7,'resumir()','totais e ocorrencias'),
 'arquivo invalido',call(2,7,'adicionarFalhaArquivo(erroFormato)','relatorioErro'))))),
 diagram('04_corrigir_automaticamente','RF07',[
 ('Administrador','actor'),(':TelaCorrecao','boundary'),(':ControladorCorrecao','control'),
 (':RepositorioProva','entity'),(':RepositorioRespostas','entity'),('questao:Questao','entity'),
 ('resultado:Resultado','entity'),(':ServicoPontuacao','control'),(':RepositorioResultados','entity')],
 call(0,1,'executarCorrecao(provaId)','exibirResumo(resumo)',
 call(1,2,'corrigir(provaId)','resumo ou pendencias',
 call(2,3,'buscarComGabaritoECriterios(provaId)','prova')+
 call(2,4,'listarPorProva(provaId)','respostasPorParticipante')+
 alt('gabarito, criterios e respostas disponiveis',
 frame('loop','para cada participante',
 call(2,6,'inicializar(participanteId, provaId)','resultado')+
 frame('loop','para cada questao da prova',
 call(2,5,'avaliar(resposta, alternativasAceitas)','situacao')+
 call(2,6,'adicionarDetalhe(questao, resposta, situacao)','detalhe'))+
 call(2,7,'calcular(resultado, prova.criterios)','pontuacao',
 [('ref','RF08',7,7)])+
 call(2,8,'salvar(resultado)','resultadoId')),
 'dados insuficientes',call(2,2,'identificarPendencias(prova, respostasPorParticipante)','pendencias'))))),
 diagram('05_calcular_pontuacao','RF08',[
 (':ControladorCorrecao','control'),(':ServicoPontuacao','control'),
 ('resultado:Resultado','entity'),('detalhe:DetalheCorrecao','entity'),
 ('criterios:CriteriosPontuacao','entity')],
 call(0,1,'calcular(resultado, criterios)','pontuacao',
 call(1,2,'obterDetalhes()','detalhes')+
 call(1,2,'iniciarPontuacao()','total = 0')+
 frame('loop','para cada detalhe',
 call(1,3,'obterSituacaoEPeso()','situacao, peso')+
 call(1,4,'pontuar(situacao, peso)','pontos',
 alt('situacao == ACERTO',call(4,4,'aplicarRegraAcerto(peso)','pontos'),
 'situacao != ACERTO',
 alt('situacao == ERRO',call(4,4,'aplicarRegraErro(peso)','pontos'),
 'outra situacao',call(4,4,'aplicarRegraEspecial(situacao, peso)','pontos'))))+
 call(1,2,'acumularPontuacao(pontos)','totalParcial'))+
 call(1,2,'obterPontuacao()','pontuacao'))),
 diagram('06_consultar_correcao_individual','RF09',[
 ('Usuario','actor'),(':TelaResultado','boundary'),(':ControladorConsulta','control'),
 (':RepositorioResultados','entity'),('resultado:Resultado','entity'),
 ('detalhe:DetalheCorrecao','entity')],
 call(0,1,'consultar(provaId, participanteId)','exibirRetorno(retorno)',
 call(1,2,'consultarIndividual(provaId, participanteId)','retorno',
 call(2,3,'buscar(provaId, participanteId)','resultado ou nulo')+
 alt('resultado != nulo',
 call(2,4,'obterDetalhes()','detalhes')+
 frame('loop','para cada detalhe',
 call(2,5,'obterRespostaFornecida()','respostaFornecida')+
 call(2,5,'obterRespostasCorretas()','respostasCorretas')+
 call(2,5,'obterSituacao()','acerto, erro ou outra situacao'))+
 call(2,4,'obterAcertosErrosEPontuacao()','acertos, erros, pontuacao'),
 'resultado == nulo',call(2,2,'montarRetornoNaoEncontrado(provaId, participanteId)','retornoIndisponivel'))))),
]
