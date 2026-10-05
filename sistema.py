import csv
import re
import shutil
from datetime import datetime
from math import isfinite
from pathlib import Path

from modelos import Participante, Prova, Questao, Resultado


class CorretorProvas:
    """Regras, persistência e correção das provas."""

    ALTERNATIVAS_VALIDAS = set("ABCDE")
    DIFICULDADES = {"FACIL", "MEDIA", "DIFICIL"}
    PADRAO_IDENTIFICADOR = re.compile(r"[A-Z0-9_-]+")
    CABECALHOS = {
        "provas": ["id", "nome", "disciplina", "categoria"],
        "participantes": ["id", "nome", "categoria"],
        "gabarito": ["numero", "respostas_aceitas", "peso", "dificuldade", "anulada"],
        "respostas": ["participante_id", "respostas"],
    }

    def __init__(self, pasta_dados: Path) -> None:
        self.pasta_dados = Path(pasta_dados)
        self.pasta_provas = self.pasta_dados / "provas"
        self.arquivo_provas = self.pasta_dados / "provas.txt"
        self.pasta_provas.mkdir(parents=True, exist_ok=True)
        if not self.arquivo_provas.exists():
            self._gravar_csv(self.arquivo_provas, self.CABECALHOS["provas"], [])

        self.prova: Prova | None = None
        self.participantes: dict[str, Participante] = {}
        self.respostas: dict[str, list[str]] = {}
        self.resultados: list[Resultado] = []
        self.registros_validos = 0
        self.registros_invalidos = 0
        self.inconsistencias: list[str] = []

    # ---------- Utilidades de arquivo e validação ----------

    @staticmethod
    def _gravar_csv(caminho: Path, cabecalho: list[str], linhas) -> None:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        with caminho.open("w", encoding="utf-8", newline="") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";", lineterminator="\n")
            escritor.writerow(cabecalho)
            escritor.writerows(linhas)

    @classmethod
    def _ler_csv(cls, caminho: Path, tipo: str, colunas: int) -> list[list[str]]:
        with Path(caminho).open(encoding="utf-8-sig", newline="") as arquivo:
            leitor = csv.reader(arquivo, delimiter=";")
            cabecalho = [c.strip().lower() for c in next(leitor, [])]
            esperado = cls.CABECALHOS[tipo]
            if cabecalho != esperado:
                raise ValueError(
                    f"Cabeçalho inválido em {Path(caminho).name}. Esperado: {';'.join(esperado)}."
                )
            linhas = []
            for numero, campos in enumerate(leitor, start=2):
                if not campos or not any(c.strip() for c in campos):
                    continue
                campos = [c.strip() for c in campos]
                if len(campos) != colunas:
                    raise ValueError(f"Linha {numero} inválida em {Path(caminho).name}.")
                linhas.append(campos)
            return linhas

    @staticmethod
    def _linhas_texto(caminho: Path) -> list[str]:
        return [
            linha.strip()
            for linha in Path(caminho).read_text(encoding="utf-8-sig").splitlines()
            if linha.strip()
        ]

    @classmethod
    def _validar_identificador(cls, identificador: str, tipo: str) -> None:
        if not cls.PADRAO_IDENTIFICADOR.fullmatch(identificador):
            raise ValueError(f"O ID {tipo} deve conter apenas letras, números, _ ou -.")

    @staticmethod
    def _validar_campos_texto(**campos: str) -> None:
        for nome, valor in campos.items():
            if not valor.strip():
                raise ValueError(f"O campo {nome} é obrigatório.")
            if any(sep in valor for sep in (";", "\n", "\r")):
                raise ValueError(f"O campo {nome} não pode conter ';' ou quebra de linha.")

    def _invalidar_resultados(self) -> None:
        self.resultados.clear()
        if self.prova:
            arquivo = self.pasta_atual / "resultados.csv"
            if arquivo.exists():
                arquivo.unlink()

    @property
    def pasta_atual(self) -> Path:
        if not self.prova:
            raise ValueError("Selecione ou cadastre uma prova primeiro.")
        return self.pasta_provas / self.prova.identificador

    # ---------- Provas ----------

    def listar_provas(self) -> list[Prova]:
        provas = []
        for numero, campos in enumerate(
            self._ler_csv(self.arquivo_provas, "provas", 4), start=2
        ):
            if not all(campos):
                raise ValueError(f"Linha {numero} inválida em {self.arquivo_provas.name}.")
            provas.append(Prova(*campos))
        return provas

    def criar_prova(self, identificador: str, nome: str, disciplina: str, categoria: str) -> None:
        identificador = identificador.strip().upper()
        self._validar_identificador(identificador, "da olimpíada/prova")
        self._validar_campos_texto(nome=nome, disciplina=disciplina, categoria=categoria)
        if any(p.identificador == identificador for p in self.listar_provas()):
            raise ValueError(f"Já existe uma prova com o ID {identificador}.")

        pasta = self.pasta_provas / identificador
        if pasta.exists():
            raise ValueError(f"A pasta da prova {identificador} já existe.")
        pasta.mkdir(parents=True)
        self._gravar_csv(pasta / "gabarito.txt", self.CABECALHOS["gabarito"], [])
        self._gravar_csv(pasta / "participantes.txt", self.CABECALHOS["participantes"], [])
        self._gravar_csv(pasta / "respostas.txt", self.CABECALHOS["respostas"], [])
        self._gravar_csv(
            pasta / "historico.txt",
            ["id", "data_hora", "registros_corrigidos", "media"],
            [],
        )
        with self.arquivo_provas.open("a", encoding="utf-8", newline="") as arquivo:
            csv.writer(arquivo, delimiter=";", lineterminator="\n").writerow(
                [identificador, nome.strip(), disciplina.strip(), categoria.strip()]
            )
        self.selecionar_prova(identificador)

    def selecionar_prova(self, identificador: str) -> None:
        identificador = identificador.strip().upper()
        prova = next((p for p in self.listar_provas() if p.identificador == identificador), None)
        if not prova:
            raise ValueError(f"Prova {identificador} não encontrada.")
        if not (self.pasta_provas / identificador).is_dir():
            raise ValueError(f"A pasta de dados da prova {identificador} não foi encontrada.")

        self.prova = prova
        self.participantes.clear()
        self.respostas.clear()
        self.resultados.clear()
        self.inconsistencias.clear()
        self.registros_validos = self.registros_invalidos = 0

        pasta = self.pasta_atual
        if (pasta / "gabarito.txt").exists():
            self.importar_gabarito(pasta / "gabarito.txt", salvar=False)
        if (pasta / "participantes.txt").exists():
            self.importar_participantes(pasta / "participantes.txt", salvar=False)
        if self.prova.questoes and (pasta / "respostas.txt").exists():
            self.importar_respostas(pasta / "respostas.txt", salvar=False)
        if (pasta / "inconsistencias.txt").exists():
            self.inconsistencias = self._linhas_texto(pasta / "inconsistencias.txt")
            self.registros_invalidos = len(self.inconsistencias)
        if self.respostas:
            self.corrigir(registrar_historico=False)

    # ---------- Participantes ----------

    def importar_participantes(self, caminho: Path, salvar: bool = True) -> None:
        novos: dict[str, Participante] = {}
        for numero, (identificador, nome, categoria) in enumerate(
            self._ler_csv(caminho, "participantes", 3), start=2
        ):
            identificador = identificador.upper()
            try:
                self._validar_identificador(identificador, "do participante")
                self._validar_campos_texto(nome=nome, categoria=categoria)
            except ValueError as erro:
                raise ValueError(f"Linha {numero}: {erro}") from erro
            if identificador in novos:
                raise ValueError(f"ID duplicado: {identificador}.")
            novos[identificador] = Participante(identificador, nome, categoria)
        self.participantes = novos
        if salvar:
            self.salvar_participantes()

    def cadastrar_participante(self, identificador: str, nome: str, categoria: str) -> None:
        identificador = identificador.strip().upper()
        self._validar_identificador(identificador, "do participante")
        self._validar_campos_texto(nome=nome, categoria=categoria)
        if identificador in self.participantes:
            raise ValueError("Este ID já está cadastrado.")
        self.participantes[identificador] = Participante(
            identificador, nome.strip(), categoria.strip()
        )
        self.salvar_participantes()

    def salvar_participantes(self) -> None:
        self._invalidar_resultados()
        linhas = (
            (p.identificador, p.nome, p.categoria) for p in self.participantes.values()
        )
        self._gravar_csv(self.pasta_atual / "participantes.txt", self.CABECALHOS["participantes"], linhas)

    # ---------- Gabarito ----------

    def _validar_questao(self, respostas: list[str], peso: float, dificuldade: str) -> None:
        if not respostas or not set(respostas).issubset(self.ALTERNATIVAS_VALIDAS):
            raise ValueError("As respostas devem utilizar apenas A, B, C, D ou E.")
        if not isfinite(peso) or peso <= 0:
            raise ValueError("O peso deve ser maior que zero.")
        if dificuldade.upper() not in self.DIFICULDADES:
            raise ValueError("A dificuldade deve ser FACIL, MEDIA ou DIFICIL.")

    def _gabarito_simples(self, caminho: Path) -> list[Questao]:
        """Aceita, por exemplo: '1- resposta: A', '2;B', '3:C' ou uma letra por linha."""
        questoes = []
        padrao = re.compile(
            r"^(?:(\d+)\s*(?:[-:;])\s*(?:resposta\s*:?)?\s*)?([A-E](?:\s*[|/]\s*[A-E])*)$",
            re.I,
        )
        for posicao, linha in enumerate(self._linhas_texto(caminho), start=1):
            encontrado = padrao.fullmatch(linha)
            if not encontrado:
                raise ValueError(
                    f"Linha {posicao} inválida em {Path(caminho).name}. "
                    "Use o modelo completo ou linhas como '1- resposta: A'."
                )
            numero = int(encontrado.group(1) or posicao)
            respostas = re.split(r"\s*[|/]\s*", encontrado.group(2).upper())
            questoes.append(Questao(numero, respostas, 1.0, "MEDIA", False))
        return questoes

    def importar_gabarito(self, caminho: Path, salvar: bool = True) -> None:
        if not self.prova:
            raise ValueError("Selecione uma prova primeiro.")
        linhas = self._linhas_texto(caminho)
        if not linhas:
            if salvar:
                raise ValueError("O arquivo de gabarito está vazio.")
            self.prova.questoes = []
            return

        esperado = ";".join(self.CABECALHOS["gabarito"])
        if linhas[0].lower() == esperado:
            questoes = []
            for numero_linha, campos in enumerate(
                self._ler_csv(caminho, "gabarito", 5), start=2
            ):
                numero_txt, respostas_txt, peso_txt, dificuldade, anulada = campos
                try:
                    numero, peso = int(numero_txt), float(peso_txt.replace(",", "."))
                except ValueError as erro:
                    raise ValueError(f"Linha {numero_linha}: número ou peso inválido.") from erro
                respostas = [r.strip().upper() for r in respostas_txt.split("|")]
                self._validar_questao(respostas, peso, dificuldade)
                anulada = anulada.upper()
                if anulada not in {"SIM", "S", "NAO", "N", "NÃO"}:
                    raise ValueError(f"Linha {numero_linha}: anulada deve ser SIM ou NAO.")
                questoes.append(Questao(numero, respostas, peso, dificuldade.upper(), anulada in {"SIM", "S"}))
        else:
            # Um texto que parece ter cabeçalho, mas não é o correto, deve falhar claramente.
            if ";" in linhas[0] and not re.match(r"^\d", linhas[0]):
                raise ValueError(f"Cabeçalho inválido em {Path(caminho).name}. Esperado: {esperado}.")
            questoes = self._gabarito_simples(caminho)

        numeros = [q.numero for q in questoes]
        if not questoes and salvar:
            raise ValueError("O arquivo de gabarito não possui questões.")
        if any(n < 1 for n in numeros):
            raise ValueError("O número da questão deve ser positivo.")
        if len(set(numeros)) != len(numeros):
            raise ValueError("Há número de questão duplicado no gabarito.")
        self.prova.questoes = sorted(questoes, key=lambda q: q.numero)
        if salvar:
            self.salvar_gabarito()

    def definir_gabarito(self, questoes: list[Questao]) -> None:
        if not self.prova:
            raise ValueError("Selecione uma prova primeiro.")
        if not questoes:
            raise ValueError("O gabarito deve possuir pelo menos uma questão.")
        numeros = set()
        for questao in questoes:
            if questao.numero < 1 or questao.numero in numeros:
                raise ValueError(f"Questão inválida ou duplicada: {questao.numero}.")
            numeros.add(questao.numero)
            questao.respostas_aceitas = [r.upper() for r in questao.respostas_aceitas]
            self._validar_questao(questao.respostas_aceitas, questao.peso, questao.dificuldade)
        self.prova.questoes = sorted(questoes, key=lambda q: q.numero)
        self.salvar_gabarito()

    def salvar_gabarito(self) -> None:
        if not self.prova:
            raise ValueError("Selecione uma prova primeiro.")
        self._invalidar_resultados()
        linhas = (
            (q.numero, "|".join(q.respostas_aceitas), f"{q.peso:.2f}", q.dificuldade, "SIM" if q.anulada else "NAO")
            for q in self.prova.questoes
        )
        self._gravar_csv(self.pasta_atual / "gabarito.txt", self.CABECALHOS["gabarito"], linhas)

    # ---------- Respostas ----------

    def _validar_respostas(self, participante_id: str, respostas: list[str], existentes: dict[str, list[str]]) -> str | None:
        if participante_id not in self.participantes:
            return f"participante {participante_id} não cadastrado"
        if participante_id in existentes:
            return f"participante {participante_id} duplicado"
        if len(respostas) != len(self.prova.questoes):
            return "quantidade de respostas diferente da quantidade de questões"
        invalida = next((r for r in respostas if r not in self.ALTERNATIVAS_VALIDAS and r != "-"), None)
        return f"alternativa inválida: {invalida}" if invalida else None

    def _respostas_simples(self, caminho: Path) -> list[str]:
        linhas = self._linhas_texto(caminho)
        if len(linhas) == 1 and "," in linhas[0]:
            return [r.strip().upper() for r in linhas[0].split(",")]

        respostas = []
        padrao = re.compile(r"^(?:(\d+)\s*(?:[-:;])\s*(?:resposta\s*:?)?\s*)?([A-E-])$", re.I)
        for posicao, linha in enumerate(linhas, start=1):
            encontrado = padrao.fullmatch(linha)
            if not encontrado:
                raise ValueError(
                    f"Linha {posicao} inválida em {Path(caminho).name}. "
                    "Use A-E (ou -) e, opcionalmente, '1- resposta: A'."
                )
            numero = int(encontrado.group(1) or posicao)
            if numero != posicao:
                raise ValueError(f"Linha {posicao}: esperada a questão {posicao}, recebida {numero}.")
            respostas.append(encontrado.group(2).upper())
        return respostas

    def importar_respostas(self, caminho: Path, salvar: bool = True, participante_id: str | None = None) -> list[str]:
        if not self.prova or not self.prova.questoes:
            raise ValueError("Cadastre o gabarito antes de importar as respostas.")
        linhas = self._linhas_texto(caminho)
        if not linhas:
            raise ValueError("O arquivo de respostas está vazio.")

        validas: dict[str, list[str]] = {}
        inconsistencias: list[str] = []
        cabecalho = ";".join(self.CABECALHOS["respostas"])

        if linhas[0].lower() == cabecalho:
            for numero_linha, (pid, texto) in enumerate(self._ler_csv(caminho, "respostas", 2), start=2):
                pid = pid.upper()
                respostas = [r.strip().upper() for r in texto.split(",")]
                erro = self._validar_respostas(pid, respostas, validas)
                if erro:
                    inconsistencias.append(f"Linha {numero_linha}: {erro}")
                else:
                    validas[pid] = respostas
        else:
            pid = (participante_id or "").strip().upper()
            if not pid and len(self.participantes) == 1:
                pid = next(iter(self.participantes))
            if not pid:
                raise ValueError(
                    "Arquivo de respostas individuais detectado. Informe o ID do participante na importação."
                )
            # Arquivo individual atualiza só esse participante; não apaga os demais já importados.
            validas = dict(self.respostas)
            validas.pop(pid, None)
            respostas = self._respostas_simples(caminho)
            erro = self._validar_respostas(pid, respostas, validas)
            if erro:
                inconsistencias.append(f"{pid}: {erro}")
            else:
                validas[pid] = respostas

        self.respostas = validas
        self.inconsistencias = inconsistencias
        self.registros_validos = len(validas)
        self.registros_invalidos = len(inconsistencias)
        if salvar:
            self.salvar_respostas()
            self.salvar_inconsistencias()
        return inconsistencias

    def registrar_respostas(self, participante_id: str, respostas: list[str]) -> None:
        participante_id = participante_id.strip().upper()
        respostas = [r.strip().upper() for r in respostas]
        existentes = dict(self.respostas)
        existentes.pop(participante_id, None)  # permite atualizar as respostas do aluno
        erro = self._validar_respostas(participante_id, respostas, existentes)
        if erro:
            raise ValueError(erro)
        self.respostas[participante_id] = respostas
        self.registros_validos = len(self.respostas)
        self.salvar_respostas()

    def salvar_respostas(self) -> None:
        self._invalidar_resultados()
        linhas = ((pid, ",".join(respostas)) for pid, respostas in self.respostas.items())
        self._gravar_csv(self.pasta_atual / "respostas.txt", self.CABECALHOS["respostas"], linhas)

    def salvar_inconsistencias(self) -> None:
        texto = "\n".join(self.inconsistencias)
        (self.pasta_atual / "inconsistencias.txt").write_text(
            texto + ("\n" if texto else ""), encoding="utf-8"
        )

    # ---------- Correção, resultados e histórico ----------

    def corrigir(self, registrar_historico: bool = True) -> list[Resultado]:
        if not self.prova or not self.prova.questoes:
            raise ValueError("Cadastre o gabarito antes de corrigir.")
        if not self.respostas:
            raise ValueError("Importe ou registre respostas antes de corrigir.")

        incompatibilidades = []
        for pid, respostas in self.respostas.items():
            erro = self._validar_respostas(pid, respostas, {})
            if erro:
                incompatibilidades.append(f"{pid}: {erro}")
        if incompatibilidades:
            detalhes = "; ".join(incompatibilidades[:3])
            if len(incompatibilidades) > 3:
                detalhes += f"; e mais {len(incompatibilidades) - 3} ocorrência(s)"
            raise ValueError(f"As respostas não são compatíveis com os dados atuais: {detalhes}. Reimporte ou corrija as respostas.")

        self.resultados = []
        for pid, respostas in self.respostas.items():
            participante = self.participantes[pid]
            pontos = acertos = erros = 0
            detalhes = []
            for questao, resposta in zip(self.prova.questoes, respostas):
                correta = questao.esta_correta(resposta)
                situacao = "ANULADA" if questao.anulada else ("ACERTO" if correta else "ERRO")
                if correta:
                    pontos += questao.peso
                    acertos += 1
                else:
                    erros += 1
                detalhes.append(
                    f"Q{questao.numero}: resposta={resposta}, gabarito={'/'.join(questao.respostas_aceitas)}, "
                    f"situação={situacao}, peso={questao.peso:.2f}"
                )
            self.resultados.append(Resultado(participante, float(pontos), acertos, erros, detalhes))

        self.resultados.sort(key=lambda r: r.pontuacao, reverse=True)
        self.exportar_resultados()
        if registrar_historico:
            self.registrar_historico()
        return self.resultados

    def exportar_resultados(self, caminho: Path | None = None) -> Path:
        if not self.resultados:
            raise ValueError("Execute a correção antes de exportar.")
        caminho = Path(caminho) if caminho else self.pasta_atual / "resultados.csv"
        linhas = (
            (pos, r.participante.identificador, r.participante.nome, r.participante.categoria,
             f"{r.pontuacao:.2f}", r.acertos, r.erros)
            for pos, r in enumerate(self.resultados, 1)
        )
        self._gravar_csv(caminho, ["posicao", "id", "nome", "categoria", "pontuacao", "acertos", "erros"], linhas)
        return caminho

    def registrar_historico(self) -> None:
        historico = self.ler_historico()
        identificador = f"CORR{len(historico) + 1:03d}"
        media = sum(r.pontuacao for r in self.resultados) / len(self.resultados)
        caminho = self.pasta_atual / "historico.txt"
        if not caminho.exists() or not caminho.read_text(encoding="utf-8").strip():
            self._gravar_csv(caminho, ["id", "data_hora", "registros_corrigidos", "media"], [])
        with caminho.open("a", encoding="utf-8", newline="") as arquivo:
            csv.writer(arquivo, delimiter=";", lineterminator="\n").writerow(
                [identificador, datetime.now().strftime("%d/%m/%Y %H:%M:%S"), len(self.resultados), f"{media:.2f}"]
            )
        pasta = self.pasta_atual / "historico"
        pasta.mkdir(exist_ok=True)
        shutil.copyfile(self.pasta_atual / "resultados.csv", pasta / f"{identificador}_resultados.csv")
        shutil.copyfile(self.pasta_atual / "gabarito.txt", pasta / f"{identificador}_gabarito.txt")

    def ler_historico(self) -> list[dict[str, str]]:
        caminho = self.pasta_atual / "historico.txt"
        if not caminho.exists():
            return []
        linhas = self._linhas_texto(caminho)
        registros = []
        for linha in linhas[1:]:
            campos = linha.split(";")
            if len(campos) == 4:
                registros.append(dict(zip(("id", "data_hora", "quantidade", "media"), campos)))
        return registros

    def detalhes_historico(self, identificador: str) -> tuple[list[str], list[str]]:
        identificador = identificador.strip().upper()
        pasta = self.pasta_atual / "historico"
        resultados = pasta / f"{identificador}_resultados.csv"
        gabarito = pasta / f"{identificador}_gabarito.txt"
        if not resultados.exists() or not gabarito.exists():
            raise ValueError("Correção histórica não encontrada.")
        return (
            resultados.read_text(encoding="utf-8-sig").splitlines(),
            gabarito.read_text(encoding="utf-8-sig").splitlines(),
        )

    def buscar_resultado(self, participante_id: str) -> Resultado | None:
        participante_id = participante_id.strip().upper()
        return next((r for r in self.resultados if r.participante.identificador == participante_id), None)

    def estatisticas_questoes(self) -> list[tuple[int, float, float]]:
        if not self.resultados or not self.prova:
            raise ValueError("Execute a correção antes de gerar estatísticas.")
        quantidade = len(self.resultados)
        grupo = max(1, round(quantidade * 0.27))
        superiores = {r.participante.identificador for r in self.resultados[:grupo]}
        inferiores = {r.participante.identificador for r in self.resultados[-grupo:]}
        dados = []
        for indice, questao in enumerate(self.prova.questoes):
            acerto = lambda pid: questao.esta_correta(self.respostas[pid][indice])
            taxa = sum(acerto(pid) for pid in self.respostas) / quantidade
            discriminacao = (
                sum(acerto(pid) for pid in superiores) / grupo
                - sum(acerto(pid) for pid in inferiores) / grupo
            )
            dados.append((questao.numero, taxa, discriminacao))
        return dados
