# Guia rápido para explicar o sistema

## Arquitetura

O projeto foi separado em três partes para manter responsabilidade única:

- `main.py`: interface de terminal, menus e entradas do usuário;
- `sistema.py`: regras de negócio, validações, importação, persistência, correção e relatórios;
- `modelos.py`: estruturas de dados com `dataclass`.

## Fluxo principal

1. Cadastra/seleciona uma prova.
2. Define ou importa o gabarito.
3. Cadastra/importa participantes.
4. Registra/importa respostas.
5. Valida os dados.
6. Corrige comparando cada resposta ao gabarito.
7. Ordena por pontuação e exporta o resultado.
8. Salva histórico para permitir consulta posterior.

## Importação TXT

O sistema aceita o formato estruturado com `;` e também um formato simples, como:

```text
1- resposta: A
2- resposta: B
3- resposta: E
```

Quando esse arquivo simples representa as respostas de um participante, o ID é informado no momento da importação. Isso evita adivinhar a quem pertencem as respostas.

## Validações importantes

- alternativas permitidas: A, B, C, D e E;
- `-` representa questão não respondida;
- quantidade de respostas deve ser igual à quantidade de questões;
- participante precisa existir;
- IDs não podem se repetir na importação;
- peso deve ser positivo;
- dificuldade deve ser `FACIL`, `MEDIA` ou `DIFICIL`;
- questões anuladas recebem a pontuação definida pelo peso.

## Bibliotecas usadas

Todas são da biblioteca padrão do Python:

- `csv`: leitura e escrita de arquivos separados por `;`;
- `re`: validação de IDs e interpretação dos TXT simples;
- `pathlib`: caminhos e arquivos de forma portátil;
- `datetime`: data/hora do histórico;
- `shutil`: copia o resultado e o gabarito para a pasta de histórico;
- `dataclasses`: modelos de dados simples e legíveis.

## provar que funciona

Executar:

```bash
python -m unittest discover -s testes -v
```

Os testes verificam o fluxo de correção, persistência, importações, alternativa E, histórico, estatísticas, CSV e rejeição de dados inválidos.
