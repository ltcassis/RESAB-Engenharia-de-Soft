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
            if valor >= minimo:
                return valor
        except ValueError:
            pass
        print(f"Digite um número inteiro maior ou igual a {minimo}.")


def ler_float(mensagem: str) -> float:
    while True:
        try:
            valor = float(input(mensagem).strip().replace(",", "."))
            if isfinite(valor) and valor > 0:
                return valor
        except ValueError:
            pass
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
    caminho = Path(input(mensagem).strip().strip('"').strip("'")).expanduser()

    if not caminho.is_absolute():
        opcoes = [Path.cwd() / caminho, PASTA_PROJETO / caminho]
        caminho = next((p for p in opcoes if p.is_file()), opcoes[0])

    if not caminho.is_file():
        raise ValueError(f"Arquivo não encontrado: {caminho}")

    return caminho.resolve()


def escolher(titulo: str, opcoes: list[tuple[str, str]]) -> str:
    print(f"\n--- {titulo} ---")
    for codigo, texto in opcoes:
        print(f"{codigo}. {texto}")
    return input("Escolha: ").strip()


def exigir_prova(corretor: CorretorProvas) -> bool:
    if corretor.prova:
        return True
    print("Selecione ou cadastre uma olimpíada/prova na opção 1 antes de continuar.")
    return False


def ler_questao(numero: int) -> Questao:
    print(f"\nQuestão {numero}")
    while True:
        respostas = [r.strip().upper() for r in input("Resposta(s), ex.: A ou A|B: ").split("|")]
        if respostas and set(respostas).issubset(CorretorProvas.ALTERNATIVAS_VALIDAS):
            break
        print("Use somente A, B, C, D ou E.")
    peso = ler_float("Peso: ")
    while True:
        dificuldade = input("Dificuldade (FACIL/MEDIA/DIFICIL): ").strip().upper()
        if dificuldade in CorretorProvas.DIFICULDADES:
            break
        print("Digite FACIL, MEDIA ou DIFICIL.")
    return Questao(numero, respostas, peso, dificuldade, ler_sim_nao("Questão anulada? (S/N): "))


# ---------- Provas e gabarito ----------


def listar_provas(corretor: CorretorProvas) -> None:
    provas = corretor.listar_provas()
    if not provas:
        print("Nenhuma prova cadastrada.")
        return
    print("\nID       | Nome                     | Disciplina          | Categoria")
    print("-" * 79)
    for prova in provas:
        marca = "*" if corretor.prova and prova.identificador == corretor.prova.identificador else " "
        print(f"{marca}{prova.identificador:<8} | {prova.nome:<24} | {prova.disciplina:<19} | {prova.categoria}")


def cadastrar_prova(corretor: CorretorProvas) -> None:
    corretor.criar_prova(
        input("ID da olimpíada/prova: "),
        input("Nome da olimpíada/prova: "),
        DISCIPLINA_PADRAO,
        input("Nível/categoria: "),
    )
    print("Olimpíada/prova cadastrada e selecionada.")


def selecionar_prova(corretor: CorretorProvas) -> None:
    listar_provas(corretor)
    if corretor.listar_provas():
        corretor.selecionar_prova(input("Informe o ID: "))
        print("Prova selecionada. Os dados salvos foram carregados.")


def exibir_gabarito(corretor: CorretorProvas) -> None:
    if not exigir_prova(corretor):
        return
    if not corretor.prova.questoes:
        print("O gabarito ainda não foi cadastrado.")
        return
    print("\nQuestão | Resposta(s) | Peso | Dificuldade | Anulada")
    print("-" * 58)
    for q in corretor.prova.questoes:
        print(f"{q.numero:^7} | {'/'.join(q.respostas_aceitas):^11} | {q.peso:^4.2f} | {q.dificuldade:^11} | {'SIM' if q.anulada else 'NÃO'}")


def cadastrar_gabarito(corretor: CorretorProvas) -> None:
    opcao = input("1. Manual\n2. Importar TXT\nEscolha: ").strip()
    if opcao == "2":
        corretor.importar_gabarito(ler_caminho("Caminho do gabarito TXT: "))
        print("Gabarito importado e salvo.")
    elif opcao == "1":
        quantidade = ler_inteiro("Quantidade de questões: ")
        questoes = [ler_questao(i) for i in range(1, quantidade + 1)]
        corretor.definir_gabarito(questoes)
        print("Gabarito cadastrado e salvo.")
    else:
        print("Opção inválida.")


def alterar_questao(corretor: CorretorProvas) -> None:
    exibir_gabarito(corretor)
    if not corretor.prova or not corretor.prova.questoes:
        return
    numero = ler_inteiro("Número da questão: ")
    indice = next((i for i, q in enumerate(corretor.prova.questoes) if q.numero == numero), None)
    if indice is None:
        print("Questão não encontrada.")
        return
    nova = ler_questao(numero)
    corretor.prova.questoes[indice] = nova
    corretor.salvar_gabarito()
    print("Questão alterada e salva. Reprocesse a correção.")


def gerenciar_questoes(corretor: CorretorProvas) -> None:
    if not exigir_prova(corretor):
        return
    while True:
        opcao = escolher("GERENCIAR QUESTÕES", [
            ("1", "Listar questões"), ("2", "Adicionar questão"),
            ("3", "Alterar questão"), ("4", "Remover última questão"), ("0", "Voltar")])
        if opcao == "0":
            return
        if opcao == "1":
            exibir_gabarito(corretor)
        elif opcao == "2":
            q = ler_questao(len(corretor.prova.questoes) + 1)
            corretor.prova.questoes.append(q)
            corretor.salvar_gabarito()
            print("Questão adicionada e salva.")
        elif opcao == "3":
            alterar_questao(corretor)
        elif opcao == "4" and corretor.prova.questoes:
            q = corretor.prova.questoes.pop()
            corretor.salvar_gabarito()
            print(f"Questão {q.numero} removida.")
        elif opcao == "4":
            print("Não há questões para remover.")
        else:
            print("Opção inválida.")


# ---------- Participantes e respostas ----------


def listar_participantes(corretor: CorretorProvas) -> None:
    if not corretor.participantes:
        print("Nenhum participante cadastrado.")
        return
    print("\nID       | Nome                     | Categoria")
    print("-" * 60)
    for p in corretor.participantes.values():
        print(f"{p.identificador:<8} | {p.nome:<24} | {p.categoria}")


def importar_respostas(corretor: CorretorProvas) -> None:
    caminho = ler_caminho("Caminho do arquivo de respostas TXT: ")
    participante = input(
        "Se o TXT contém só as respostas de UM participante, informe o ID dele; "
        "se o arquivo já contém os IDs, pressione Enter: "
    ).strip() or None
    inconsistencias = corretor.importar_respostas(caminho, participante_id=participante)
    print(f"Registros válidos: {corretor.registros_validos}")
    print(f"Registros inválidos: {corretor.registros_invalidos}")
    for item in inconsistencias:
        print(f"- {item}")


def executar_correcao(corretor: CorretorProvas) -> None:
    resultados = corretor.corrigir()
    print(f"Correção concluída: {len(resultados)} participante(s).")
    print(f"Resultados: {corretor.pasta_atual / 'resultados.csv'}")


# ---------- Resultados e relatórios ----------


def exibir_classificacao(corretor: CorretorProvas, pedir_filtro: bool = True) -> None:
    if not corretor.resultados:
        print("Execute a correção primeiro.")
        return
    categoria = input("Categoria para filtrar ou Enter para todos: ").strip().lower() if pedir_filtro else ""
    resultados = [r for r in corretor.resultados if not categoria or r.participante.categoria.lower() == categoria]
    if not resultados:
        print("Nenhum resultado encontrado.")
        return
    print("\nPosição | ID       | Nome                     | Pontos")
    print("-" * 62)
    for posicao, r in enumerate(resultados, 1):
        print(f"{posicao:^7} | {r.participante.identificador:<8} | {r.participante.nome:<24} | {r.pontuacao:>6.2f}")


def consultar_resultado(corretor: CorretorProvas) -> None:
    resultado = corretor.buscar_resultado(input("ID do participante: "))
    if not resultado:
        print("Participante não encontrado ou sem resultado nesta prova.")
        return
    print(f"\nParticipante: {resultado.participante.nome}")
    print(*resultado.detalhes, sep="\n")
    print(f"Pontuação: {resultado.pontuacao:.2f}")
    print(f"Acertos: {resultado.acertos} | Erros: {resultado.erros}")


def exibir_estatisticas(corretor: CorretorProvas) -> None:
    if not corretor.resultados:
        print("Execute a correção primeiro.")
        return
    media = mean(r.pontuacao for r in corretor.resultados)
    maxima = corretor.prova.pontuacao_maxima()
    print(f"Média: {media:.2f} de {maxima:.2f}")
    print(f"Aproveitamento médio: {(media / maxima) * 100:.1f}%")


def exibir_desempenho(corretor: CorretorProvas) -> None:
    print("\nQuestão | Taxa de acerto | Índice de discriminação")
    print("-" * 55)
    for numero, taxa, indice in sorted(corretor.estatisticas_questoes(), key=lambda x: x[2], reverse=True):
        print(f"{numero:^7} | {taxa * 100:>13.1f}% | {indice:>23.2f}")


# ---------- Menus ----------


def menu_provas(corretor: CorretorProvas) -> None:
    while True:
        op = escolher("OLIMPÍADAS, PROVAS E QUESTÕES", [
            ("1", "Cadastrar olimpíada/prova"), ("2", "Listar/selecionar olimpíada/prova"),
            ("3", "Gerenciar questões"), ("4", "Configurar pontuação e regras"), ("0", "Voltar")])
        if op == "0":
            return
        {"1": cadastrar_prova, "2": selecionar_prova, "3": gerenciar_questoes, "4": alterar_questao}.get(op, lambda _: print("Opção inválida."))(corretor)


def menu_participantes(corretor: CorretorProvas) -> None:
    if not exigir_prova(corretor):
        return
    while True:
        op = escolher("PARTICIPANTES", [("1", "Importar TXT"), ("2", "Cadastrar manualmente"), ("3", "Listar inscritos"), ("0", "Voltar")])
        if op == "0":
            return
        if op == "1":
            corretor.importar_participantes(ler_caminho("Caminho do arquivo de participantes: "))
            print(f"{len(corretor.participantes)} participante(s) importado(s).")
        elif op == "2":
            corretor.cadastrar_participante(input("ID: "), input("Nome: "), input("Categoria/nível: "))
            print("Participante cadastrado.")
        elif op == "3": listar_participantes(corretor)
        else: print("Opção inválida.")


def menu_gabarito(corretor: CorretorProvas) -> None:
    if not exigir_prova(corretor):
        return
    while True:
        op = escolher("GABARITO OFICIAL", [("1", "Cadastrar/importar gabarito"), ("2", "Alterar questão"), ("3", "Exibir gabarito"), ("0", "Voltar")])
        if op == "0":
            return
        {"1": cadastrar_gabarito, "2": alterar_questao, "3": exibir_gabarito}.get(op, lambda _: print("Opção inválida."))(corretor)


def menu_respostas(corretor: CorretorProvas) -> None:
    if not exigir_prova(corretor):
        return
    while True:
        op = escolher("RESPOSTAS E CORREÇÃO", [
            ("1", "Registrar respostas manualmente"), ("2", "Importar respostas TXT"),
            ("3", "Exibir inconsistências"), ("4", "Executar correção"), ("5", "Exibir resumo"), ("0", "Voltar")])
        if op == "0":
            return
        if op == "1":
            corretor.registrar_respostas(input("ID do participante: "), input("Respostas separadas por vírgula: ").split(","))
            print("Respostas registradas.")
        elif op == "2": importar_respostas(corretor)
        elif op == "3": print(*(corretor.inconsistencias or ["Nenhuma inconsistência registrada."]), sep="\n- ")
        elif op == "4": executar_correcao(corretor)
        elif op == "5": print(f"Válidos: {corretor.registros_validos}\nInválidos: {corretor.registros_invalidos}\nCorrigidos: {len(corretor.resultados)}")
        else: print("Opção inválida.")


def menu_resultados(corretor: CorretorProvas) -> None:
    if not exigir_prova(corretor):
        return
    while True:
        op = escolher("RESULTADOS", [("1", "Correção individual"), ("2", "Classificação"), ("3", "Exportar CSV"), ("0", "Voltar")])
        if op == "0":
            return
        if op == "1": consultar_resultado(corretor)
        elif op == "2": exibir_classificacao(corretor)
        elif op == "3":
            texto = input("Caminho do CSV ou Enter para usar a pasta da prova: ").strip().strip('"')
            salvo = corretor.exportar_resultados(Path(texto) if texto else None)
            print(f"Resultados exportados para: {salvo}")
        else: print("Opção inválida.")


def menu_relatorios(corretor: CorretorProvas) -> None:
    if not exigir_prova(corretor):
        return
    while True:
        op = escolher("RELATÓRIOS E ESTATÍSTICAS", [("1", "Relatório consolidado"), ("2", "Estatísticas da prova"), ("3", "Desempenho por questão"), ("0", "Voltar")])
        if op == "0":
            return
        if op == "1":
            exibir_classificacao(corretor, False)
            exibir_estatisticas(corretor)
        elif op == "2":
            exibir_estatisticas(corretor)
        elif op == "3":
            exibir_desempenho(corretor)
        else:
            print("Opção inválida.")


def menu_historico(corretor: CorretorProvas) -> None:
    if not exigir_prova(corretor):
        return
    while True:
        op = escolher("HISTÓRICO E REPROCESSAMENTO", [("1", "Consultar correções"), ("2", "Ver registros legíveis"), ("3", "Reprocessar correção"), ("0", "Voltar")])
        if op == "0":
            return
        if op == "1":
            historico = corretor.ler_historico()
            if not historico:
                print("Nenhuma correção registrada.")
                continue
            print("\nID      | Data/hora           | Corrigidos | Média")
            for r in historico:
                print(f"{r['id']:<7} | {r['data_hora']:<19} | {r['quantidade']:^9} | {r['media']}")
            codigo = input("ID para ver detalhes ou Enter para voltar: ").strip()
            if codigo:
                resultados, gabarito = corretor.detalhes_historico(codigo)
                print("\nRESULTADOS", *resultados, "\nGABARITO", *gabarito, sep="\n")
        elif op == "2":
            print(f"Legíveis/válidos: {corretor.registros_validos}")
            print(f"Ilegíveis/inválidos: {corretor.registros_invalidos}")
        elif op == "3":
            exibir_gabarito(corretor)
            if ler_sim_nao("Confirmar reprocessamento? (S/N): "):
                executar_correcao(corretor)
        else:
            print("Opção inválida.")


def menu() -> None:
    corretor = CorretorProvas(PASTA_DADOS)
    acoes = {"1": menu_provas, "2": menu_participantes, "3": menu_gabarito, "4": menu_respostas,
             "5": menu_resultados, "6": menu_relatorios, "7": menu_historico}
    while True:
        atual = f"{corretor.prova.identificador} - {corretor.prova.nome}" if corretor.prova else "nenhuma"
        print(f"\nProva selecionada: {atual}\n\n=== AVALIADOR DE GABARITOS DE OLIMPÍADAS DE MATEMÁTICA ===")
        print("1. Olimpíadas, provas e questões\n2. Participantes\n3. Gabarito oficial\n4. Respostas e correção")
        print("5. Resultados e classificação\n6. Relatórios e estatísticas\n7. Histórico e reprocessamento\n0. Sair")
        opcao = input("Escolha uma opção: ").strip()
        if opcao == "0":
            print("Sistema encerrado.")
            return
        acao = acoes.get(opcao)
        if not acao:
            print("Opção inválida.")
            continue

        while True:
            try:
                acao(corretor)
                break
            except (OSError, ValueError) as erro:
                print(f"Erro: {erro}")

if __name__ == "__main__":
    menu()
