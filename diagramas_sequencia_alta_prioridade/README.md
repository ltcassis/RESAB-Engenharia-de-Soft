# Diagramas de sequência de projeto — alta prioridade

As versões com fundo branco estão em [versao_clara/](versao_clara/), nos formatos PNG, SVG e PlantUML. Elas mantêm o conteúdo e as dimensões das versões escuras. Para regenerar apenas a versão clara, execute `python gerar_diagramas.py --tema claro`. Sem esse argumento, o gerador produz o tema escuro na pasta principal.

Os seis diagramas representam a colaboração entre objetos internos para realizar RF02, RF03, RF05, RF07, RF08 e RF09, conforme a tabela de requisitos fornecida. O cabeçalho de cada imagem contém apenas o RF, sem subtítulo, legenda ou observação de rodapé.

## Arquivos

| RF | Caso de uso | PNG | SVG | PlantUML |
|---|---|---|---|---|
| RF02 | Gerenciar provas | [PNG](01_gerenciar_provas.png) | [SVG](01_gerenciar_provas.svg) | [Fonte](01_gerenciar_provas.puml) |
| RF03 | Cadastrar gabarito oficial | [PNG](02_cadastrar_gabarito.png) | [SVG](02_cadastrar_gabarito.svg) | [Fonte](02_cadastrar_gabarito.puml) |
| RF05 | Importar respostas | [PNG](03_importar_respostas.png) | [SVG](03_importar_respostas.svg) | [Fonte](03_importar_respostas.puml) |
| RF07 | Corrigir gabarito automaticamente | [PNG](04_corrigir_automaticamente.png) | [SVG](04_corrigir_automaticamente.svg) | [Fonte](04_corrigir_automaticamente.puml) |
| RF08 | Calcular pontuação | [PNG](05_calcular_pontuacao.png) | [SVG](05_calcular_pontuacao.svg) | [Fonte](05_calcular_pontuacao.puml) |
| RF09 | Consultar correção individual | [PNG](06_consultar_correcao_individual.png) | [SVG](06_consultar_correcao_individual.svg) | [Fonte](06_consultar_correcao_individual.puml) |

## Modelo de projeto

As linhas de vida usam instâncias, como `prova:Prova`, ou instâncias anônimas, como `:ControladorProva`. As mensagens especificam operações com argumentos e retornos. Os controladores coordenam a execução, entidades realizam operações de domínio e repositórios recuperam e persistem objetos. Os repositórios foram agrupados visualmente no papel de acesso aos dados; não impõem uma tecnologia de armazenamento.

- RF02: TelaProva, ControladorProva, RepositorioProva, Prova e CriteriosPontuacao colaboram para recuperar, validar e salvar a configuração vinculada à olimpíada e à categoria.
- RF03: ControladorGabarito consulta Prova/Questao, monta Gabarito, valida as respostas e a completude e persiste a prova com seu gabarito.
- RF05: ControladorImportacao delega a leitura a LeitorArquivo, a validação de apoio do RF06 a ValidadorRespostas, a persistência a RepositorioRespostas e a composição de ocorrências a RelatorioImportacao.
- RF07: ControladorCorrecao carrega dados dos repositórios, solicita avaliação a Questao, compõe Resultado, chama ServicoPontuacao e salva os resultados.
- RF08: ServicoPontuacao percorre DetalheCorrecao, delega as regras a CriteriosPontuacao e acumula os pontos em Resultado. É chamado internamente pelo RF07 para cada participante.
- RF09: ControladorConsulta recupera Resultado, consulta seus detalhes e reúne respostas fornecidas, respostas corretas, situações, acertos, erros e pontuação.

`alt` contém condições de caminhos alternativos; `loop` delimita repetições. Barras de ativação duram da chamada até o retorno, com ativações aninhadas para chamadas internas. Setas contínuas com ponta preenchida representam chamadas síncronas; setas tracejadas representam retornos. O fragmento `ref RF08` localiza o detalhamento do serviço de pontuação.

As entidades que recebem `inicializar()`/`preparar()` são tratadas como instâncias já alocadas, obtidas por injeção, carregamento ou fábrica fora do trecho representado. No laço de participantes, `resultado:Resultado` representa a instância correspondente à iteração, e não um mesmo resultado compartilhado por todos.

## Relação com a implementação

Esta é uma proposta de projeto orientado a objetos para atender aos requisitos. As classes e assinaturas detalhadas não são um inventário das classes existentes no programa Python. O código atual concentra várias responsabilidades em CorretorProvas; implementar essa separação exigiria uma refatoração específica da aplicação.

RF01, RF04, RF06, RF10 e RF11 continuam classificados como prioridade média. RF06 aparece como apoio à importação. A modelagem não fixa valores dos pesos, descontos ou regras de situações especiais: esses detalhes pertencem à configuração dos critérios. As rotinas de validação e tratamento de erros são decisões de projeto propostas para realizar os requisitos.

## Edição

O modelo compartilhado fica em `requisitos_diagramas.py`. O gerador `gerar_diagramas.py` produz PNG, SVG e PlantUML a partir das mesmas chamadas e retornos e verifica o balanceamento das chamadas e dos fragmentos. Requer Python, Pillow e fontes Arial do Windows.

Os arquivos PlantUML também podem ser editados separadamente. Uma nova execução do gerador substitui essas edições diretas. Os SVGs permitem ampliar os diagramas mais largos sem perda de definição.

O código da aplicação e os diagramas originais permanecem preservados.
