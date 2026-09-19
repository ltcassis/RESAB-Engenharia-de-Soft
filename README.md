# Avaliador de Gabaritos de Olimpíadas de Matemática

Sistema de terminal em Python para cadastrar provas objetivas de olimpíadas de
matemática, importar participantes e respostas, realizar correções e gerar
classificações e estatísticas. Não exige bibliotecas externas.

O sistema avalia questões objetivas com alternativas de `A` a `E`. Ele não
resolve as questões matemáticas: compara as respostas dos participantes com o
gabarito oficial cadastrado pela organização da olimpíada.

## Executar

Abra a pasta no VS Code e, no terminal, execute:

```bash
python main.py
```

## Testes automáticos

Para conferir as validações e o fluxo completo, execute:

```bash
python -m unittest discover -s testes -v
```

## Fluxo recomendado

1. Acesse `1. Olimpíadas, provas e questões` e cadastre ou selecione uma prova.
2. Gerencie as questões nesse módulo ou acesse `3. Gabarito oficial` para
   cadastrar o gabarito manualmente ou importar TXT.
3. Acesse `2. Participantes` e cadastre ou importe os participantes.
4. Acesse `4. Respostas e correção` e registre ou importe as respostas.
5. Execute a correção.
6. Consulte a classificação, os relatórios e o histórico.

## Persistência

Cada prova possui uma pasta própria dentro de `dados/provas/ID_DA_PROVA`.
O sistema mantém nela:

- `gabarito.txt`;
- `participantes.txt`;
- `respostas.txt`;
- `inconsistencias.txt`;
- `resultados.csv`;
- `historico.txt`.

Cada correção também cria, na subpasta `historico`, uma cópia dos resultados e
do gabarito usado. Assim, uma execução antiga pode ser consultada mesmo depois
de o gabarito ser alterado.

Por isso, os dados permanecem disponíveis depois que o programa é fechado.

## Formatos para importação

Os arquivos usam ponto e vírgula (`;`) entre as colunas.

### Gabarito

```text
numero;respostas_aceitas;peso;dificuldade;anulada
1;A;1.0;FACIL;NAO
2;A|B;2.0;DIFICIL;NAO
3;C;1.0;MEDIA;SIM
```

`A|B` significa que as alternativas A e B são aceitas. A dificuldade deve ser
`FACIL`, `MEDIA` ou `DIFICIL`.

### Participantes

```text
id;nome;categoria
A001;Ana Souza;Nível 1
A002;Bruno Lima;Nível 1
```

O ID identifica o participante e não pode se repetir.

### Respostas

```text
participante_id;respostas
A001;A,B,C,D,A
A002;B,B,C,D,A
```

Use `-` quando uma questão não tiver resposta. A quantidade de alternativas
deve ser igual à quantidade de questões do gabarito.

## Regras implementadas

- pesos diferentes;
- questões anuladas;
- mais de uma alternativa aceita;
- validação de respostas inválidas e IDs inexistentes;
- correção e pontuação automáticas;
- classificação por pontuação;
- filtro da classificação por categoria/nível;
- resultado individual;
- exportação em CSV;
- média e aproveitamento geral;
- taxa de acerto por questão;
- índice de discriminação simplificado;
- histórico detalhado com cópias de resultados e regras;
- confirmação antes do reprocessamento.

O índice de discriminação compara a proporção de acertos do grupo superior com
a do grupo inferior, usando aproximadamente 27% dos participantes em cada grupo.
Ele é utilizado para ordenar as questões no relatório de desempenho, não como
critério de desempate dos participantes.

## Arquivos do código

- `main.py`: menus e interação com o usuário no contexto de olimpíadas de matemática;
- `sistema.py`: persistência, validação, correção, relatórios e histórico;
- `modelos.py`: classes `Prova`, `Questao`, `Participante` e `Resultado`;
- `dados/`: catálogo e pastas das provas.
