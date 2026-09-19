from math import isfinite
from pathlib import Path
from statistics import mean

from modelos import Questao
from sistema import CorretorProvas


PASTA_PROJETO = Path(__file__).resolve().parent
PASTA_DADOS = PASTA_PROJETO / "dados"
DISCIPLINA_PADRAO = "Matemática"


def ler_inteiro(mensagem: str, minimo: int = 1) -> int:
    while True:
        try:
            valor = int(input(mensagem).strip())
            if valor < minimo:
                raise ValueError
            return valor
        except ValueError:
            print(f"Digite um número inteiro maior ou igual a {minimo}.")


def ler_float(mensagem: str) -> float:
    while True:
        try:
            valor = float(input(mensagem).strip().replace(",", "."))
            if not isfinite(valor) or valor <= 0:
                raise ValueError
            return valor
        except ValueError:
            print("Digite um número maior que zero.")


def ler_sim_nao(mensagem: str) -> bool:
    while True:
        resposta = input(mensagem).strip().upper()
        if resposta in {"S", "SIM"}:
            return True
        if resposta in {"N", "NAO", "NÃO"}:
            return False
        print("Digite S para sim ou N para não.")


def ler_caminho(mensagem: str) -> Path:
    texto = input(mensagem).strip().strip('"').strip("'")
    caminho = Path(texto).expanduser()
    if not caminho.is_absolute():
        caminho = Path.cwd() / caminho
    if not caminho.is_file():
        raise ValueError(f"Arquivo não encontrado: {caminho}")
    return caminho


def cabecalho(corretor: CorretorProvas) -> None:
    if corretor.prova:
        print(
            f"\nOlimpíada/prova selecionada: {corretor.prova.identificador} - "
            f"{corretor.prova.nome}"
        )
    else:
        print("\nOlimpíada/prova selecionada: nenhuma")


def exigir_prova(corretor: CorretorProvas) -> bool:
    if corretor.prova:
        return True
    print("Selecione ou cadastre uma olimpíada/prova na opção 1 antes de continuar.")
    return False


def listar_provas(corretor: CorretorProvas) -> None:
    provas = corretor.listar_provas()
    if not provas:
        print("Nenhuma prova cadastrada.")
        return
    print("\nID       | Nome                     | Disciplina          | Categoria")
    print("-" * 79)
    for prova in provas:
        marca = "*" if corretor.prova and prova.identificador == corretor.prova.identificador else " "
        print(
            f"{marca}{prova.identificador:<8} | {prova.nome:<24} | "
            f"{prova.disciplina:<19} | {prova.categoria}"
        )


def cadastrar_prova(corretor: CorretorProvas) -> None:
    print("\nCADASTRAR OLIMPÍADA/PROVA")
    identificador = input("ID da olimpíada/prova (ex.: OBM2026): ")
    nome = input("Nome da olimpíada/prova: ")
    categoria = input("Nível/categoria da olimpíada: ")
    corretor.criar_prova(identificador, nome, DISCIPLINA_PADRAO, categoria)
    print("Olimpíada/prova cadastrada e selecionada.")


def selecionar_prova(corretor: CorretorProvas) -> None:
    listar_provas(corretor)
    if not corretor.listar_provas():
        return
    identificador = input("Informe o ID da olimpíada/prova: ")
    corretor.selecionar_prova(identificador)
    print("Olimpíada/prova selecionada. Os dados salvos foram carregados.")


def exibir_gabarito(corretor: CorretorProvas) -> None:
    if not exigir_prova(corretor):
        return
    if not corretor.prova.questoes:
        print("O gabarito ainda não foi cadastrado.")
        return
    print("\nQuestão | Resposta(s) | Peso | Dificuldade | Anulada")
    print("-" * 58)
    for questao in corretor.prova.questoes:
        respostas = "/".join(questao.respostas_aceitas)
        anulada = "SIM" if questao.anulada else "NÃO"
        print(
            f"{questao.numero:^7} | {respostas:^11} | {questao.peso:^4.2f} | "
            f"{questao.dificuldade:^11} | {anulada}"
        )


def cadastrar_gabarito_manual(corretor: CorretorProvas) -> None:
    quantidade = ler_inteiro("Quantidade de questões: ")
    questoes: list[Questao] = []
    for numero in range(1, quantidade + 1):
        print(f"\nQuestão {numero}")
        while True:
            respostas = input("Resposta(s) correta(s), ex.: A ou A|B: ").upper().split("|")
            respostas = [resposta.strip() for resposta in respostas]
            if respostas and set(respostas).issubset(corretor.ALTERNATIVAS_VALIDAS):
                break
            print("Use somente A, B, C, D ou E.")
        peso = ler_float("Peso: ")
        while True:
            dificuldade = input("Dificuldade (FACIL/MEDIA/DIFICIL): ").strip().upper()
            if dificuldade in {"FACIL", "MEDIA", "DIFICIL"}:
                break
            print("Digite FACIL, MEDIA ou DIFICIL.")
        anulada = ler_sim_nao("Questão anulada? (S/N): ")
        questoes.append(Questao(numero, respostas, peso, dificuldade, anulada))
    corretor.definir_gabarito(questoes)
    print("Gabarito cadastrado e salvo.")


def cadastrar_ou_importar_gabarito(corretor: CorretorProvas) -> None:
    print("\n1. Cadastrar manualmente")
    print("2. Importar arquivo TXT")
    opcao = input("Escolha: ").strip()
    if opcao == "1":
        cadastrar_gabarito_manual(corretor)
    elif opcao == "2":
        caminho = ler_caminho("Caminho completo do gabarito TXT: ")
        corretor.importar_gabarito(caminho)
        print("Gabarito importado e salvo na prova selecionada.")
    else:
        print("Opção inválida.")


def alterar_gabarito(corretor: CorretorProvas) -> None:
    exibir_gabarito(corretor)
    if not corretor.prova or not corretor.prova.questoes:
        return
    numero = ler_inteiro("Número da questão que será alterada: ")
    questao = next((q for q in corretor.prova.questoes if q.numero == numero), None)
    if questao is None:
        print("Questão não encontrada.")
        return
    respostas = [
        resposta.strip().upper()
        for resposta in input("Nova(s) resposta(s), ex.: A|B: ").split("|")
    ]
    peso = ler_float("Novo peso: ")
    dificuldade = input("Dificuldade (FACIL/MEDIA/DIFICIL): ").strip().upper()
    anulada = ler_sim_nao("Anulada? (S/N): ")
    corretor._validar_questao(respostas, peso, dificuldade)
    questao.respostas_aceitas = respostas
    questao.peso = peso
    questao.dificuldade = dificuldade
    questao.anulada = anulada
    corretor.salvar_gabarito()
    corretor.resultados.clear()
    print("Gabarito alterado e salvo. Reprocesse a correção.")


def gerenciar_questoes(corretor: CorretorProvas) -> None:
    if not exigir_prova(corretor):
        return
    while True:
        print("\n--- GERENCIAR QUESTÕES ---")
        print("1. Listar questões")
        print("2. Adicionar questão")
        print("3. Alterar questão")
        print("4. Remover última questão")
        print("0. Voltar")
        opcao = input("Escolha: ").strip()
        if opcao == "1":
            exibir_gabarito(corretor)
        elif opcao == "2":
            numero = len(corretor.prova.questoes) + 1
            respostas = [
                resposta.strip().upper()
                for resposta in input("Resposta(s), ex.: A|B: ").split("|")
            ]
            peso = ler_float("Peso: ")
            dificuldade = input("Dificuldade (FACIL/MEDIA/DIFICIL): ").strip().upper()
            anulada = ler_sim_nao("Anulada? (S/N): ")
            corretor._validar_questao(respostas, peso, dificuldade)
            corretor.prova.questoes.append(
                Questao(numero, respostas, peso, dificuldade, anulada)
            )
            corretor.salvar_gabarito()
            corretor.resultados.clear()
            print("Questão adicionada e salva.")
        elif opcao == "3":
            alterar_gabarito(corretor)
        elif opcao == "4":
            if not corretor.prova.questoes:
                print("Não há questões para remover.")
            else:
                removida = corretor.prova.questoes.pop()
                corretor.salvar_gabarito()
                corretor.resultados.clear()
                print(f"Questão {removida.numero} removida.")
        elif opcao == "0":
            return
        else:
            print("Opção inválida.")


def listar_participantes(corretor: CorretorProvas) -> None:
    if not corretor.participantes:
        print("Nenhum participante cadastrado.")
        return
    print("\nID       | Nome                     | Categoria")
    print("-" * 60)
    for participante in corretor.participantes.values():
        print(
            f"{participante.identificador:<8} | {participante.nome:<24} | "
            f"{participante.categoria}"
        )


def importar_participantes(corretor: CorretorProvas) -> None:
    caminho = ler_caminho("Caminho completo do arquivo de participantes: ")
    corretor.importar_participantes(caminho)
    print(f"{len(corretor.participantes)} participantes importados e salvos.")


def cadastrar_participante(corretor: CorretorProvas) -> None:
    identificador = input("ID do participante: ")
    nome = input("Nome: ")
    categoria = input("Categoria/nível: ")
    corretor.cadastrar_participante(identificador, nome, categoria)
    print("Participante cadastrado e salvo.")


def importar_respostas(corretor: CorretorProvas) -> None:
    caminho = ler_caminho("Caminho completo do arquivo de respostas: ")
    inconsistencias = corretor.importar_respostas(caminho)
    print(f"Registros válidos: {corretor.registros_validos}")
    print(f"Registros inválidos: {corretor.registros_invalidos}")
    if inconsistencias:
        print("\nRELATÓRIO DE INCONSISTÊNCIAS")
        for item in inconsistencias:
            print(f"- {item}")


def registrar_respostas_manual(corretor: CorretorProvas) -> None:
    participante_id = input("ID do participante: ")
    respostas = input("Respostas separadas por vírgula: ").split(",")
    corretor.registrar_respostas(participante_id, respostas)
    print("Respostas registradas e salvas.")


def executar_correcao(corretor: CorretorProvas) -> None:
    resultados = corretor.corrigir()
    print(f"Correção concluída: {len(resultados)} participantes corrigidos.")
    print(f"Resultados salvos em: {corretor.pasta_atual / 'resultados.csv'}")


def exibir_classificacao(corretor: CorretorProvas, pedir_filtro: bool = True) -> None:
    if not corretor.resultados:
        print("Execute a correção primeiro.")
        return
    categoria = ""
    if pedir_filtro:
        categoria = input(
            "Categoria/nível para filtrar ou Enter para mostrar todos: "
        ).strip().lower()
    resultados = [
        resultado
        for resultado in corretor.resultados
        if not categoria or resultado.participante.categoria.lower() == categoria
    ]
    if not resultados:
        print("Nenhum resultado encontrado para esse filtro.")
        return
    print("\nPosição | ID       | Nome                     | Pontos")
    print("-" * 62)
    for posicao, resultado in enumerate(resultados, start=1):
        print(
            f"{posicao:^7} | {resultado.participante.identificador:<8} | "
            f"{resultado.participante.nome:<24} | {resultado.pontuacao:>6.2f}"
        )


def consultar_resultado(corretor: CorretorProvas) -> None:
    participante_id = input("ID do participante: ")
    resultado = corretor.buscar_resultado(participante_id)
    if resultado is None:
        print("Resultado não encontrado. Execute a correção primeiro.")
        return
    print(f"\nParticipante: {resultado.participante.nome}")
    for detalhe in resultado.detalhes:
        print(detalhe)
    print(f"Pontuação: {resultado.pontuacao:.2f}")
    print(f"Acertos: {resultado.acertos} | Erros: {resultado.erros}")


def exportar_resultados(corretor: CorretorProvas) -> None:
    texto = input("Caminho do CSV ou Enter para usar a pasta da prova: ").strip().strip('"')
    caminho = Path(texto) if texto else None
    if caminho and not caminho.is_absolute():
        caminho = Path.cwd() / caminho
    salvo = corretor.exportar_resultados(caminho)
    print(f"Resultados exportados para: {salvo}")


def exibir_estatisticas(corretor: CorretorProvas) -> None:
    if not corretor.resultados:
        print("Execute a correção primeiro.")
        return
    media = mean(resultado.pontuacao for resultado in corretor.resultados)
    maxima = corretor.prova.pontuacao_maxima()
    print(f"Média: {media:.2f} de {maxima:.2f}")
    print(f"Aproveitamento médio: {(media / maxima) * 100:.1f}%")


def exibir_desempenho(corretor: CorretorProvas) -> None:
    print("\nQuestão | Taxa de acerto | Índice de discriminação")
    print("-" * 55)
    dados = sorted(corretor.estatisticas_questoes(), key=lambda item: item[2], reverse=True)
    for numero, taxa, indice in dados:
        print(f"{numero:^7} | {taxa * 100:>13.1f}% | {indice:>23.2f}")


def menu_provas(corretor: CorretorProvas) -> None:
    while True:
        print("\n--- OLIMPÍADAS, PROVAS E QUESTÕES ---")
        print("1. Cadastrar olimpíada/prova")
        print("2. Listar/selecionar olimpíada/prova")
        print("3. Gerenciar questões")
        print("4. Configurar pontuação e regras")
        print("0. Voltar")
        opcao = input("Escolha: ").strip()
        if opcao == "1":
            cadastrar_prova(corretor)
        elif opcao == "2":
            selecionar_prova(corretor)
        elif opcao == "3":
            gerenciar_questoes(corretor)
        elif opcao == "4":
            alterar_gabarito(corretor)
        elif opcao == "0":
            return
        else:
            print("Opção inválida.")


def menu_participantes(corretor: CorretorProvas) -> None:
    if not exigir_prova(corretor):
        return
    while True:
        print("\n--- PARTICIPANTES ---")
        print("1. Importar arquivo TXT")
        print("2. Cadastrar manualmente")
        print("3. Listar inscritos")
        print("0. Voltar")
        opcao = input("Escolha: ").strip()
        if opcao == "1":
            importar_participantes(corretor)
        elif opcao == "2":
            cadastrar_participante(corretor)
        elif opcao == "3":
            listar_participantes(corretor)
        elif opcao == "0":
            return
        else:
            print("Opção inválida.")


def menu_gabarito(corretor: CorretorProvas) -> None:
    if not exigir_prova(corretor):
        return
    while True:
        print("\n--- GABARITO OFICIAL ---")
        print("1. Cadastrar/importar gabarito")
        print("2. Alterar gabarito")
        print("3. Exibir gabarito")
        print("0. Voltar")
        opcao = input("Escolha: ").strip()
        if opcao == "1":
            cadastrar_ou_importar_gabarito(corretor)
        elif opcao == "2":
            alterar_gabarito(corretor)
        elif opcao == "3":
            exibir_gabarito(corretor)
        elif opcao == "0":
            return
        else:
            print("Opção inválida.")


def menu_respostas(corretor: CorretorProvas) -> None:
    if not exigir_prova(corretor):
        return
    while True:
        print("\n--- RESPOSTAS E CORREÇÃO ---")
        print("1. Registrar respostas manualmente")
        print("2. Importar respostas TXT")
        print("3. Validar/exibir inconsistências")
        print("4. Executar correção")
        print("5. Exibir resumo")
        print("0. Voltar")
        opcao = input("Escolha: ").strip()
        if opcao == "1":
            registrar_respostas_manual(corretor)
        elif opcao == "2":
            importar_respostas(corretor)
        elif opcao == "3":
            if corretor.inconsistencias:
                for item in corretor.inconsistencias:
                    print(f"- {item}")
            else:
                print("Nenhuma inconsistência registrada.")
        elif opcao == "4":
            executar_correcao(corretor)
        elif opcao == "5":
            print(f"Válidos: {corretor.registros_validos}")
            print(f"Inválidos: {corretor.registros_invalidos}")
            print(f"Corrigidos: {len(corretor.resultados)}")
        elif opcao == "0":
            return
        else:
            print("Opção inválida.")


def menu_resultados(corretor: CorretorProvas) -> None:
    if not exigir_prova(corretor):
        return
    while True:
        print("\n--- RESULTADOS ---")
        print("1. Correção individual")
        print("2. Classificação")
        print("3. Exportar CSV")
        print("0. Voltar")
        opcao = input("Escolha: ").strip()
        if opcao == "1":
            consultar_resultado(corretor)
        elif opcao == "2":
            exibir_classificacao(corretor)
        elif opcao == "3":
            exportar_resultados(corretor)
        elif opcao == "0":
            return
        else:
            print("Opção inválida.")


def menu_relatorios(corretor: CorretorProvas) -> None:
    if not exigir_prova(corretor):
        return
    while True:
        print("\n--- RELATÓRIOS E ESTATÍSTICAS ---")
        print("1. Relatório consolidado")
        print("2. Estatísticas da prova")
        print("3. Desempenho por questão")
        print("0. Voltar")
        opcao = input("Escolha: ").strip()
        if opcao == "1":
            exibir_classificacao(corretor, pedir_filtro=False)
            exibir_estatisticas(corretor)
        elif opcao == "2":
            exibir_estatisticas(corretor)
        elif opcao == "3":
            exibir_desempenho(corretor)
        elif opcao == "0":
            return
        else:
            print("Opção inválida.")


def menu_historico(corretor: CorretorProvas) -> None:
    if not exigir_prova(corretor):
        return
    while True:
        print("\n--- HISTÓRICO E REPROCESSAMENTO ---")
        print("1. Consultar correções")
        print("2. Ver registros legíveis")
        print("3. Reprocessar correção")
        print("0. Voltar")
        opcao = input("Escolha: ").strip()
        if opcao == "1":
            historico = corretor.ler_historico()
            if not historico:
                print("Nenhuma correção registrada.")
            else:
                print("\nID      | Data/hora           | Corrigidos | Média")
                print("-" * 58)
                for registro in historico:
                    print(
                        f"{registro['id']:<7} | {registro['data_hora']:<19} | "
                        f"{registro['quantidade']:^9} | {registro['media']}"
                    )
                identificador = input(
                    "Informe um ID para ver detalhes ou Enter para voltar: "
                ).strip()
                if identificador:
                    resultados, gabarito = corretor.detalhes_historico(identificador)
                    print("\nRESULTADOS DA CORREÇÃO")
                    for linha in resultados:
                        print(linha)
                    print("\nGABARITO UTILIZADO")
                    for linha in gabarito:
                        print(linha)
        elif opcao == "2":
            print(f"Legíveis/válidos: {corretor.registros_validos}")
            print(f"Ilegíveis/inválidos: {corretor.registros_invalidos}")
        elif opcao == "3":
            print("\nGabarito e regras atuais:")
            exibir_gabarito(corretor)
            if ler_sim_nao("Confirmar reprocessamento? (S/N): "):
                executar_correcao(corretor)
            else:
                print("Reprocessamento cancelado.")
        elif opcao == "0":
            return
        else:
            print("Opção inválida.")


def menu() -> None:
    corretor = CorretorProvas(PASTA_DADOS)
    acoes = {
        "1": menu_provas,
        "2": menu_participantes,
        "3": menu_gabarito,
        "4": menu_respostas,
        "5": menu_resultados,
        "6": menu_relatorios,
        "7": menu_historico,
    }
    while True:
        cabecalho(corretor)
        print("\n=== AVALIADOR DE GABARITOS DE OLIMPÍADAS DE MATEMÁTICA ===")
        print("1. Olimpíadas, provas e questões")
        print("2. Participantes")
        print("3. Gabarito oficial")
        print("4. Respostas e correção")
        print("5. Resultados e classificação")
        print("6. Relatórios e estatísticas")
        print("7. Histórico e reprocessamento")
        print("0. Sair")
        opcao = input("Escolha uma opção: ").strip()
        if opcao == "0":
            print("Sistema encerrado.")
            break
        acao = acoes.get(opcao)
        if acao is None:
            print("Opção inválida.")
            continue
        try:
            acao(corretor)
        except (OSError, ValueError) as erro:
            print(f"Erro: {erro}")


if __name__ == "__main__":
    menu()
