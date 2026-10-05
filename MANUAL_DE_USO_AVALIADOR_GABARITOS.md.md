# Manual de Uso 
## Avaliador de Gabaritos de Olimpíadas de Matemática

**Versão:** 1.0  
**Data:** 05/10/2026  
**Finalidade:** orientar o professor/usuário no cadastro de provas, gabaritos, participantes, respostas, correção, classificação, relatórios e histórico.

---

## 1. Visão geral

O Avaliador de Gabaritos de Olimpíadas de Matemática é um sistema em Python executado pelo terminal. Ele permite:

- cadastrar e selecionar olimpíadas/provas;
- cadastrar ou importar gabaritos;
- cadastrar ou importar participantes;
- registrar ou importar respostas;
- corrigir automaticamente as provas;
- usar pesos diferentes por questão;
- aceitar mais de uma alternativa correta;
- anular questões;
- gerar classificação;
- consultar a correção individual;
- gerar estatísticas por prova e por questão;
- exportar resultados em CSV;
- manter histórico das correções realizadas;
- reprocessar a correção quando o gabarito for alterado.

O sistema aceita alternativas **A, B, C, D e E**. Para representar uma questão **não respondida**, use o caractere **`-`**.

> **Regra principal:** antes de usar qualquer função de uma prova, é necessário cadastrá-la ou selecioná-la no menu **1. Olimpíadas, provas e questões**.

---

## 2. Como iniciar o sistema

### 2.1 Requisito

É necessário ter o **Python 3** instalado no computador.

O sistema não depende de bibliotecas externas.

### 2.2 Abrir

Abra um terminal na pasta do projeto e execute:

```bash
python main.py
```

Se no computador o comando `python` não funcionar, tente:

```bash
py main.py
```

Ao iniciar, será exibido o menu principal:

```text
=== AVALIADOR DE GABARITOS DE OLIMPÍADAS DE MATEMÁTICA ===
1. Olimpíadas, provas e questões
2. Participantes
3. Gabarito oficial
4. Respostas e correção
5. Resultados e classificação
6. Relatórios e estatísticas
7. Histórico e reprocessamento
0. Sair
```

### 2.3 Importante ao reabrir o programa

As provas e seus dados ficam salvos no computador. Porém, ao fechar e abrir o programa novamente, nenhuma prova começa selecionada.

Portanto, ao reabrir o sistema:

1. entre em **1. Olimpíadas, provas e questões**;
2. escolha **2. Listar/selecionar olimpíada/prova**;
3. informe o ID da prova desejada.

Depois disso, gabarito, participantes, respostas e resultados salvos daquela prova serão carregados.

---

## 3. Fluxo recomendado de uso

Para evitar erros, use sempre esta ordem:

1. **Cadastrar ou selecionar a prova**;
2. **Cadastrar/importar o gabarito**;
3. **Cadastrar/importar os participantes**;
4. **Registrar/importar as respostas**;
5. **Verificar inconsistências**, se houver;
6. **Executar a correção**;
7. **Consultar resultados e classificação**;
8. **Gerar relatórios/estatísticas**;
9. **Consultar o histórico**, quando necessário.

---

# 4. Provas e questões

No menu principal, escolha:

```text
1. Olimpíadas, provas e questões
```

O submenu possui:

```text
1. Cadastrar olimpíada/prova
2. Listar/selecionar olimpíada/prova
3. Gerenciar questões
4. Configurar pontuação e regras
0. Voltar
```

## 4.1 Cadastrar uma nova prova

Escolha **1. Cadastrar olimpíada/prova**.

O sistema solicitará:

- **ID da olimpíada/prova**;
- **Nome da olimpíada/prova**;
- **Nível/categoria**.

Exemplo:

```text
ID da olimpíada/prova: OBM2026
Nome da olimpíada/prova: Olimpíada de Matemática 2026
Nível/categoria: Nível 1
```

### Regras para o ID

O ID deve usar apenas:

- letras;
- números;
- `_`;
- `-`.

Exemplos válidos:

```text
OBM2026
PROVA_01
NIVEL-1
```

Evite espaços, acentos e símbolos no ID.

## 4.2 Selecionar uma prova existente

Escolha:

```text
2. Listar/selecionar olimpíada/prova
```

O sistema exibirá as provas cadastradas. Digite o ID da prova desejada.

O ID não diferencia maiúsculas de minúsculas. Por exemplo, `obm2026` e `OBM2026` são tratados da mesma forma.

---

# 5. Gabarito oficial

No menu principal, escolha:

```text
3. Gabarito oficial
```

O sistema permite:

```text
1. Cadastrar/importar gabarito
2. Alterar questão
3. Exibir gabarito
0. Voltar
```

O gabarito pode ser cadastrado **manualmente** ou por **arquivo TXT**.

---

## 5.1 Cadastro manual do gabarito

Escolha:

```text
1. Cadastrar/importar gabarito
1. Manual
```

Informe a quantidade de questões e preencha cada questão.

Para cada questão serão solicitados:

- resposta correta;
- peso;
- dificuldade;
- informação se a questão está anulada.

### Resposta correta

Use apenas:

```text
A
B
C
D
E
```

Maiúsculas e minúsculas são aceitas, mas recomenda-se usar sempre maiúsculas.

### Mais de uma alternativa correta

Quando duas ou mais respostas forem aceitas, use **`|`** entre elas.

Exemplo:

```text
B|C
```

Isso significa que tanto **B** quanto **C** serão consideradas corretas.

### Peso

O peso deve ser um número maior que zero.

Exemplos:

```text
1
2
1.5
```

### Dificuldade

Use exatamente uma destas opções:

```text
FACIL
MEDIA
DIFICIL
```

A dificuldade é uma informação descritiva da questão. **Ela não altera a pontuação**. A pontuação é determinada pelo peso.

### Questão anulada

Responda:

```text
S
```

para questão anulada, ou:

```text
N
```

para questão normal.

Uma questão anulada é considerada correta para todos os participantes e concede o peso da questão.

---

# 6. Importação do gabarito por TXT

Para uso real, o formato mais seguro é o **gabarito completo** descrito abaixo.

## 6.1 Formato completo recomendado

O arquivo deve possuir exatamente este cabeçalho:

```text
numero;respostas_aceitas;peso;dificuldade;anulada
```

Exemplo completo:

```text
numero;respostas_aceitas;peso;dificuldade;anulada
1;A;1.0;FACIL;NAO
2;B|C;2.0;DIFICIL;NAO
3;E;1.5;MEDIA;SIM
4;D;1.0;MEDIA;NAO
```

### Significado das colunas

| Coluna | Como preencher |
|---|---|
| `numero` | Número da questão: `1`, `2`, `3`... |
| `respostas_aceitas` | `A`, `B`, `C`, `D`, `E` ou múltiplas como `B|C` |
| `peso` | Número maior que zero, como `1.0`, `2.0`, `1.5` |
| `dificuldade` | `FACIL`, `MEDIA` ou `DIFICIL` |
| `anulada` | `SIM` ou `NAO` |

### Muito importante

- As colunas são separadas por **ponto e vírgula `;`**.
- Para várias alternativas corretas, use **barra vertical `|`**, e não vírgula.
- Os números das questões não podem se repetir.
- As alternativas devem estar entre **A e E**.
- Para evitar problemas, não altere o nome das colunas do cabeçalho.

---

## 6.2 Gabarito TXT simples

Também é possível usar um arquivo mais simples:

```text
1- resposta: A
2- resposta: B
3- resposta: C
4- resposta: D
5- resposta: E
```

Também são reconhecidos formatos como:

```text
1;A
2;B
3;C
```

ou:

```text
1:A
2:B
3:C
```

ou apenas:

```text
A
B
C
D
E
```

Para mais de uma resposta correta no formato simples, prefira:

```text
2- resposta: B|C
```

### Atenção ao gabarito simples

Quando o formato simples é usado, o sistema assume automaticamente:

- **peso:** `1.0`;
- **dificuldade:** `MEDIA`;
- **anulada:** `NAO`.

Por isso, para uma prova real com pesos, dificuldades ou questões anuladas, utilize o **formato completo**.

---

## 6.3 Como informar o caminho do arquivo

Se o arquivo estiver dentro da pasta `modelos_importacao`, pode ser informado assim:

```text
modelos_importacao/gabarito_modelo.txt
```

Também é possível informar o caminho completo, por exemplo:

```text
C:\Users\Professor\Documents\gabarito_olimpiada.txt
```

O arquivo pode ter qualquer nome, desde que o conteúdo siga um dos formatos aceitos.

---

# 7. Participantes

No menu principal, escolha:

```text
2. Participantes
```

As opções são:

```text
1. Importar TXT
2. Cadastrar manualmente
3. Listar inscritos
0. Voltar
```

---

## 7.1 Cadastrar participante manualmente

Escolha **2. Cadastrar manualmente**.

Informe:

```text
ID: A001
Nome: Ana Souza
Categoria/nível: Nível 1
```

### Regras do ID do participante

O ID deve ser único e utilizar apenas letras, números, `_` ou `-`.

Exemplos:

```text
A001
ALUNO_15
N1-023
```

---

## 7.2 Importar participantes por TXT

O arquivo deve ter exatamente este cabeçalho:

```text
id;nome;categoria
```

Exemplo:

```text
id;nome;categoria
A001;Ana Souza;Nível 1
A002;Bruno Lima;Nível 1
A003;Carla Santos;Nível 2
```

### Atenção

Ao importar um arquivo de participantes, o sistema passa a utilizar **a lista presente naquele arquivo** para a prova selecionada.

Portanto, se já houver participantes cadastrados e você importar um novo TXT, o arquivo deve conter **todos os participantes que deverão permanecer na prova**, e não apenas os novos.

Para adicionar somente uma pessoa sem substituir a lista, prefira **Cadastrar manualmente**.

---

# 8. Respostas dos participantes

No menu principal, escolha:

```text
4. Respostas e correção
```

As opções são:

```text
1. Registrar respostas manualmente
2. Importar respostas TXT
3. Exibir inconsistências
4. Executar correção
5. Exibir resumo
0. Voltar
```

Esta é a etapa em que é mais importante respeitar o formato correto.

---

# 9. Forma correta de escrever as respostas

## 9.1 Regra geral

Cada participante deve possuir **uma resposta para cada questão da prova, na mesma ordem do gabarito**.

Se a prova possui 5 questões, devem existir exatamente 5 respostas.

Exemplo correto:

```text
A,B,C,D,E
```

Exemplo incorreto para uma prova de 5 questões:

```text
A,B,C
```

O sistema rejeitará a entrada porque a quantidade de respostas é diferente da quantidade de questões.

## 9.2 Alternativas permitidas

Use apenas:

```text
A
B
C
D
E
-
```

O símbolo `-` significa **sem resposta**.

Exemplo:

```text
A,B,-,D,E
```

Nesse caso, a terceira questão foi deixada em branco.

### Não use

```text
F
X
0
?
```

Esses valores serão rejeitados.

---

# 10. Registrar respostas manualmente

Escolha:

```text
4. Respostas e correção
1. Registrar respostas manualmente
```

O sistema pedirá o ID do participante:

```text
ID do participante: A001
```

Depois, informe as respostas separadas por vírgulas:

```text
Respostas separadas por vírgula: A,B,C,D,E
```

### Exemplo com questão em branco

```text
A,B,-,D,E
```

### Observação

Se o mesmo participante já tiver respostas registradas, um novo registro manual para aquele ID atualiza as respostas dele.

---

# 11. Importar respostas de vários participantes por TXT

Este é o formato recomendado quando várias provas serão lançadas de uma vez.

O arquivo deve começar exatamente com:

```text
participante_id;respostas
```

Exemplo para uma prova de 5 questões:

```text
participante_id;respostas
A001;A,B,C,D,E
A002;B,B,C,D,A
A003;A,-,C,E,B
```

### Como o sistema interpreta

Para `A001`:

- questão 1 = A;
- questão 2 = B;
- questão 3 = C;
- questão 4 = D;
- questão 5 = E.

### Regras essenciais

1. O ID deve existir na lista de participantes da prova.
2. Deve existir exatamente uma resposta por questão.
3. As respostas são separadas por **vírgula**.
4. Somente `A`, `B`, `C`, `D`, `E` e `-` são aceitos.
5. Um mesmo participante não deve aparecer duas vezes no mesmo arquivo.

### Atenção

Ao importar o arquivo no formato de **vários participantes**, ele passa a representar o conjunto de respostas importadas para aquela prova.

Portanto, para uma importação em lote, mantenha no arquivo todos os participantes cujas respostas deverão permanecer registradas.

---

# 12. Importar respostas de um único participante por TXT

Também é possível importar um arquivo que contenha somente as respostas de uma pessoa.

Exemplo:

```text
1- resposta: A
2- resposta: B
3- resposta: C
4- resposta: D
5- resposta: E
```

Ao detectar esse formato, o sistema perguntará:

```text
Se o TXT contém só as respostas de UM participante, informe o ID dele;
se o arquivo já contém os IDs, pressione Enter:
```

Digite, por exemplo:

```text
A001
```

Nesse formato, somente as respostas desse participante são atualizadas. As respostas já cadastradas para os demais participantes são preservadas.

### Numeração obrigatória

As linhas devem seguir a ordem das questões.

Correto:

```text
1- resposta: A
2- resposta: B
3- resposta: -
4- resposta: D
```

Não pule uma questão. Se ela estiver sem resposta, use `-`.

### Outra forma individual aceita

Também é possível usar uma única linha:

```text
A,B,C,D,E
```

Nesse caso, ao importar, informe o ID do participante quando solicitado.

---

# 13. Diferença entre gabarito e respostas

Esta diferença evita muitos erros:

### No gabarito

Para duas alternativas corretas, use:

```text
B|C
```

### Nas respostas do participante

Cada questão recebe apenas uma resposta. Exemplo:

```text
A,B,C,D,E
```

Não escreva `B|C` como resposta de um participante. `B|C` é uma regra do **gabarito**, indicando que B ou C serão aceitas.

---

# 14. Exibir inconsistências

Depois de importar respostas, utilize:

```text
4. Respostas e correção
3. Exibir inconsistências
```

Possíveis problemas identificados incluem:

- participante não cadastrado;
- participante duplicado no arquivo;
- quantidade de respostas diferente da quantidade de questões;
- alternativa inválida.

Corrija o TXT e importe novamente antes de executar a correção definitiva.

---

# 15. Executar a correção

Depois que gabarito, participantes e respostas estiverem corretos, escolha:

```text
4. Respostas e correção
4. Executar correção
```

O sistema irá:

1. validar as respostas;
2. comparar cada resposta com o gabarito;
3. aplicar o peso de cada questão;
4. considerar questões anuladas;
5. calcular acertos, erros e pontuação;
6. ordenar a classificação;
7. salvar os resultados em CSV;
8. registrar a correção no histórico.

---

# 16. Como a pontuação é calculada

Exemplo de gabarito:

```text
Questão 1: E, peso 1
Questão 2: B|C, peso 2
```

Respostas do participante:

```text
A,B
```

Resultado:

- Questão 1: `A` não corresponde a `E` → **erro** → 0 ponto;
- Questão 2: `B` está entre `B|C` → **acerto** → 2 pontos;
- Pontuação final: **2,00 pontos de 3,00 possíveis**.

### Questão anulada

Se uma questão estiver marcada como `SIM` no campo `anulada`, ela será considerada correta para todos e concederá seu peso.

---

# 17. Resultados e classificação

No menu principal, escolha:

```text
5. Resultados e classificação
```

## 17.1 Correção individual

Escolha:

```text
1. Correção individual
```

Informe o ID do participante.

O sistema exibirá, questão por questão:

- resposta dada;
- gabarito;
- situação: ACERTO, ERRO ou ANULADA;
- peso;
- pontuação total;
- quantidade de acertos e erros.

## 17.2 Classificação

Escolha:

```text
2. Classificação
```

O sistema perguntará:

```text
Categoria para filtrar ou Enter para todos:
```

- pressione **Enter** para listar todos;
- digite uma categoria, como `Nível 1`, para mostrar somente aquele grupo.

A classificação é ordenada pela pontuação, da maior para a menor.

## 17.3 Exportar CSV

Escolha:

```text
3. Exportar CSV
```

Pressione **Enter** para usar o arquivo padrão da prova.

O arquivo gerado possui campos como:

```text
posicao;id;nome;categoria;pontuacao;acertos;erros
```

Ele pode ser aberto no Excel ou em outro programa de planilhas.

---

# 18. Relatórios e estatísticas

No menu principal, escolha:

```text
6. Relatórios e estatísticas
```

## Relatório consolidado

Exibe a classificação e informações gerais da prova.

## Estatísticas da prova

Exibe:

- média de pontuação;
- pontuação máxima;
- aproveitamento médio em porcentagem.

## Desempenho por questão

Exibe:

- taxa de acerto de cada questão;
- índice de discriminação simplificado.

> Com poucos participantes, especialmente apenas um, o índice de discriminação pode aparecer como `0.00`. Isso não representa erro do sistema; não há grupos suficientes para uma comparação significativa.

---

# 19. Histórico e reprocessamento

No menu principal, escolha:

```text
7. Histórico e reprocessamento
```

## 19.1 Consultar correções

Cada correção executada gera um registro, por exemplo:

```text
CORR001
CORR002
CORR003
```

O histórico registra:

- data e hora;
- quantidade de participantes corrigidos;
- média;
- cópia dos resultados;
- cópia do gabarito utilizado naquela correção.

Isso permite verificar como a prova estava em uma correção anterior.

## 19.2 Reprocessar correção

Use esta função quando o gabarito sofrer uma alteração e as respostas já cadastradas continuarem compatíveis.

Exemplo:

- questão 2 era `B`;
- o professor percebe que `C` também deve ser aceita;
- altera o gabarito para `B|C`;
- entra em **Histórico e reprocessamento → Reprocessar correção**;
- confirma com `S`.

O sistema recalcula os resultados e cria uma nova entrada no histórico.

### Se a quantidade de questões mudar

Se forem adicionadas ou removidas questões depois que as respostas já foram importadas, as respostas antigas deixam de ter a mesma quantidade de itens.

Nesse caso, atualize/reimporte as respostas antes de corrigir novamente.

---

# 20. Onde os dados ficam salvos

Cada prova possui uma pasta própria em:

```text
dados/provas/ID_DA_PROVA/
```

Dentro dela podem existir:

```text
gabarito.txt
participantes.txt
respostas.txt
inconsistencias.txt
resultados.csv
historico.txt
historico/
```

### Recomendação

Não edite esses arquivos internos manualmente durante o uso normal do sistema.

Use os menus do Avaliador de Gabaritos de Olimpíadas de Matemática ou os arquivos TXT de importação. Isso reduz o risco de criar inconsistências.

---

# 21. Modelos prontos no projeto

A pasta:

```text
modelos_importacao/
```

contém arquivos de exemplo que podem ser copiados e adaptados:

```text
gabarito_modelo.txt
participantes_modelo.txt
respostas_modelo.txt
respostas_individuais_modelo.txt
respostas26_exemplo.txt
```

A forma mais segura de trabalhar é fazer uma cópia de um desses modelos, alterar os dados e importar o novo arquivo.

---

# 22. Erros comuns e como resolver

## “Selecione ou cadastre uma olimpíada/prova...”

Nenhuma prova está selecionada.

**Solução:**

```text
1. Olimpíadas, provas e questões
2. Listar/selecionar olimpíada/prova
```

Escolha o ID da prova.

---

## “Arquivo não encontrado”

O caminho digitado não corresponde ao local do arquivo.

**Solução:** confira o nome e a pasta. Se estiver em `modelos_importacao`, use, por exemplo:

```text
modelos_importacao/respostas_modelo.txt
```

---

## “alternativa inválida”

Existe uma resposta fora de A, B, C, D, E ou `-`.

**Exemplo incorreto:**

```text
A,F,C,D
```

**Solução:** corrija `F` para uma alternativa válida ou `-` se estiver em branco.

---

## “quantidade de respostas diferente da quantidade de questões”

O participante tem mais ou menos respostas do que a prova possui questões.

Se a prova possui 10 questões, devem existir exatamente 10 posições.

Use `-` para uma questão não respondida; não remova a posição.

---

## “participante ... não cadastrado”

O ID presente nas respostas não existe na lista de participantes.

**Solução:** cadastre ou importe o participante antes de importar as respostas.

---

## “participante ... duplicado”

O mesmo ID aparece duas vezes no arquivo de respostas em lote.

**Solução:** mantenha apenas uma linha para cada participante.

---

## “Cabeçalho inválido”

O nome das colunas foi alterado.

Use exatamente os cabeçalhos apresentados neste manual.

### Participantes

```text
id;nome;categoria
```

### Gabarito

```text
numero;respostas_aceitas;peso;dificuldade;anulada
```

### Respostas em lote

```text
participante_id;respostas
```

---

# 23. Tabela de referência rápida

| Situação | Forma correta |
|---|---|
| Alternativa correta única | `A` |
| Duas alternativas corretas no gabarito | `B|C` |
| Respostas manuais | `A,B,C,D,E` |
| Questão sem resposta | `-` |
| Dificuldade | `FACIL`, `MEDIA`, `DIFICIL` |
| Questão anulada | `SIM` ou `NAO` |
| Separador das colunas TXT | `;` |
| Separador entre respostas de um participante | `,` |
| Separador entre várias alternativas corretas | `|` |

---

# 24. Exemplo completo de uso

Suponha uma prova com 3 questões e dois participantes.

## Gabarito

Arquivo `gabarito.txt`:

```text
numero;respostas_aceitas;peso;dificuldade;anulada
1;A;1.0;FACIL;NAO
2;B|C;2.0;MEDIA;NAO
3;E;1.0;DIFICIL;NAO
```

## Participantes

Arquivo `participantes.txt`:

```text
id;nome;categoria
A001;Ana Souza;Nível 1
A002;Bruno Lima;Nível 1
```

## Respostas

Arquivo `respostas.txt`:

```text
participante_id;respostas
A001;A,B,E
A002;A,C,D
```

### Resultado esperado

**A001**

- Q1: A → correta → 1 ponto;
- Q2: B → correta porque B está em B|C → 2 pontos;
- Q3: E → correta → 1 ponto;
- total = **4 pontos**.

**A002**

- Q1: A → correta → 1 ponto;
- Q2: C → correta porque C está em B|C → 2 pontos;
- Q3: D → incorreta → 0 ponto;
- total = **3 pontos**.

Classificação:

```text
1º A001 - Ana Souza   4.00
2º A002 - Bruno Lima  3.00
```

---

# 25. Boas práticas para uso real

1. **Não altere os arquivos da pasta `dados` manualmente.**
2. Mantenha uma cópia dos TXT originais usados na importação.
3. Use IDs únicos e simples para participantes e provas.
4. Prefira o formato completo de gabarito em provas oficiais.
5. Use sempre `|` para indicar mais de uma alternativa correta no gabarito.
6. Use sempre vírgula para separar respostas de um participante.
7. Use `-` para questão não respondida; nunca elimine a posição da questão.
8. Antes de corrigir, consulte **Exibir inconsistências**.
9. Se alterar o gabarito, reexecute ou reprocesse a correção.
10. Se alterar a quantidade de questões, confira e reimporte as respostas.
11. Antes de uma importação em lote de participantes ou respostas, verifique se o arquivo contém todo o conjunto que deve permanecer cadastrado.

---

## Resumo em uma frase

**Gabarito:** `B|C` significa “B ou C são corretas”.  
**Respostas do aluno:** `A,B,C,D,E` significa “uma resposta para cada questão, na ordem da prova”.

