import csv
import re
import shutil
from datetime import datetime
from math import isfinite
from pathlib import Path

from modelos import Participante, Prova, Questao, Resultado


class CorretorProvas:
    ALTERNATIVAS_VALIDAS = {"A", "B", "C", "D", "E"}
    PADRAO_IDENTIFICADOR = re.compile(r"[A-Z0-9_-]+")

    def __init__(self, pasta_dados: Path) -> None:
        self.pasta_dados = pasta_dados
        self.pasta_provas = pasta_dados / "provas"
        self.arquivo_provas = pasta_dados / "provas.txt"
        self.pasta_provas.mkdir(parents=True, exist_ok=True)
        self._criar_catalogo_se_necessario()
        self.prova: Prova | None = None
        self.participantes: dict[str, Participante] = {}
        self.respostas: dict[str, list[str]] = {}
        self.resultados: list[Resultado] = []
        self.registros_validos = 0
        self.registros_invalidos = 0
        self.inconsistencias: list[str] = []

    def _criar_catalogo_se_necessario(self) -> None:
        if not self.arquivo_provas.exists():
            self.arquivo_provas.write_text(
                "id;nome;disciplina;categoria\n", encoding="utf-8"
            )

    def listar_provas(self) -> list[Prova]:
        provas: list[Prova] = []
        with self.arquivo_provas.open(encoding="utf-8") as arquivo:
            self._validar_cabecalho(
                arquivo,
                ["id", "nome", "disciplina", "categoria"],
                self.arquivo_provas,
            )
            for numero_linha, linha in enumerate(arquivo, start=2):
                if not linha.strip():
                    continue
                campos = [campo.strip() for campo in linha.split(";")]
                if len(campos) != 4 or not all(campos):
                    raise ValueError(
                        f"Linha {numero_linha} inválida em {self.arquivo_provas.name}."
                    )
                provas.append(Prova(*campos))
        return provas

    @classmethod
    def _validar_identificador(cls, identificador: str, tipo: str) -> None:
        if not cls.PADRAO_IDENTIFICADOR.fullmatch(identificador):
            raise ValueError(
                f"O ID {tipo} deve conter apenas letras, números, _ ou -."
            )

    @staticmethod
    def _validar_campos_texto(**campos: str) -> None:
        for nome_campo, valor in campos.items():
            if not valor.strip():
                raise ValueError(f"O campo {nome_campo} é obrigatório.")
            if any(separador in valor for separador in (";", "\n", "\r")):
                raise ValueError(
                    f"O campo {nome_campo} não pode conter ponto e vírgula ou quebra de linha."
                )

    @staticmethod
    def _validar_cabecalho(
        arquivo, esperado: list[str], caminho: Path
    ) -> None:
        primeira_linha = next(arquivo, "").strip()
        recebido = [campo.strip().lower() for campo in primeira_linha.split(";")]
        if recebido != esperado:
            raise ValueError(
                f"Cabeçalho inválido em {caminho.name}. Esperado: {';'.join(esperado)}."
            )

    def _invalidar_resultados(self) -> None:
        self.resultados.clear()
        if self.prova is None:
            return
        arquivo_resultados = self.pasta_atual / "resultados.csv"
        if arquivo_resultados.exists():
            arquivo_resultados.unlink()

    def criar_prova(
        self, identificador: str, nome: str, disciplina: str, categoria: str
    ) -> None:
        identificador = identificador.strip().upper()
        self._validar_identificador(identificador, "da olimpíada/prova")
        if any(prova.identificador == identificador for prova in self.listar_provas()):
            raise ValueError(f"Já existe uma prova com o ID {identificador}.")
        self._validar_campos_texto(
            nome=nome, disciplina=disciplina, categoria=categoria
        )

        pasta = self.pasta_provas / identificador
        if pasta.exists():
            raise ValueError(f"A pasta da prova {identificador} já existe.")
        pasta.mkdir(parents=True, exist_ok=False)
        (pasta / "gabarito.txt").write_text(
            "numero;respostas_aceitas;peso;dificuldade;anulada\n",
            encoding="utf-8",
        )
        (pasta / "participantes.txt").write_text(
            "id;nome;categoria\n", encoding="utf-8"
        )
        (pasta / "respostas.txt").write_text(
            "participante_id;respostas\n", encoding="utf-8"
        )
        (pasta / "historico.txt").write_text(
            "id;data_hora;registros_corrigidos;media\n", encoding="utf-8"
        )
        with self.arquivo_provas.open("a", encoding="utf-8") as arquivo:
            arquivo.write(
                f"{identificador};{nome.strip()};{disciplina.strip()};{categoria.strip()}\n"
            )
        self.selecionar_prova(identificador)

    def selecionar_prova(self, identificador: str) -> None:
        identificador = identificador.strip().upper()
        prova = next(
            (p for p in self.listar_provas() if p.identificador == identificador),
            None,
        )
        if prova is None:
            raise ValueError(f"Prova {identificador} não encontrada.")

        pasta = self.pasta_provas / prova.identificador
        if not pasta.is_dir():
            raise ValueError(
                f"A pasta de dados da prova {identificador} não foi encontrada."
            )

        self.prova = prova
        self.participantes.clear()
        self.respostas.clear()
        self.resultados.clear()
        self.registros_validos = 0
        self.registros_invalidos = 0
        self.inconsistencias.clear()

        if (pasta / "gabarito.txt").exists():
            self.importar_gabarito(pasta / "gabarito.txt", salvar=False)
        if (pasta / "participantes.txt").exists():
            self.importar_participantes(pasta / "participantes.txt", salvar=False)
        if (pasta / "respostas.txt").exists() and self.prova.questoes:
            self.importar_respostas(pasta / "respostas.txt", salvar=False)
        arquivo_inconsistencias = pasta / "inconsistencias.txt"
        if arquivo_inconsistencias.exists():
            self.inconsistencias = [
                linha.strip()
                for linha in arquivo_inconsistencias.read_text(
                    encoding="utf-8"
                ).splitlines()
                if linha.strip()
            ]
            self.registros_invalidos = len(self.inconsistencias)
        if self.respostas and self.prova.questoes:
            self.corrigir(registrar_historico=False)

    @property
    def pasta_atual(self) -> Path:
        if self.prova is None:
            raise ValueError("Selecione ou cadastre uma prova primeiro.")
        return self.pasta_provas / self.prova.identificador

    def importar_participantes(self, caminho: Path, salvar: bool = True) -> None:
        novos: dict[str, Participante] = {}
        with caminho.open(encoding="utf-8-sig") as arquivo:
            self._validar_cabecalho(
                arquivo, ["id", "nome", "categoria"], caminho
            )
            for numero_linha, linha in enumerate(arquivo, start=2):
                if not linha.strip():
                    continue
                campos = [campo.strip() for campo in linha.split(";")]
                if len(campos) != 3:
                    raise ValueError(f"Linha {numero_linha} inválida em {caminho.name}.")
                identificador, nome, categoria = campos
                identificador = identificador.upper()
                try:
                    self._validar_identificador(identificador, "do participante")
                    self._validar_campos_texto(nome=nome, categoria=categoria)
                except ValueError as erro:
                    raise ValueError(f"Linha {numero_linha}: {erro}") from erro
                if identificador in novos:
                    raise ValueError(f"ID duplicado: {identificador}.")
                novos[identificador] = Participante(identificador, nome, categoria)
        self.participantes = novos
        if salvar:
            self.salvar_participantes()

    def salvar_participantes(self) -> None:
        self._invalidar_resultados()
        caminho = self.pasta_atual / "participantes.txt"
        with caminho.open("w", encoding="utf-8", newline="") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";", lineterminator="\n")
            escritor.writerow(["id", "nome", "categoria"])
            for participante in self.participantes.values():
                escritor.writerow(
                    [participante.identificador, participante.nome, participante.categoria]
                )

    def cadastrar_participante(
        self, identificador: str, nome: str, categoria: str
    ) -> None:
        identificador = identificador.strip().upper()
        self._validar_identificador(identificador, "do participante")
        if identificador in self.participantes:
            raise ValueError("Este ID já está cadastrado.")
        self._validar_campos_texto(nome=nome, categoria=categoria)
        self.participantes[identificador] = Participante(
            identificador, nome.strip(), categoria.strip()
        )
        self.salvar_participantes()

    def importar_gabarito(self, caminho: Path, salvar: bool = True) -> None:
        if self.prova is None:
            raise ValueError("Selecione uma prova primeiro.")
        questoes: list[Questao] = []
        numeros: set[int] = set()
        with caminho.open(encoding="utf-8-sig") as arquivo:
            self._validar_cabecalho(
                arquivo,
                ["numero", "respostas_aceitas", "peso", "dificuldade", "anulada"],
                caminho,
            )
            for numero_linha, linha in enumerate(arquivo, start=2):
                if not linha.strip():
                    continue
                campos = [campo.strip() for campo in linha.split(";")]
                if len(campos) != 5:
                    raise ValueError(f"Linha {numero_linha} inválida em {caminho.name}.")
                numero_texto, respostas, peso_texto, dificuldade, anulada = campos
                try:
                    numero = int(numero_texto)
                    peso = float(peso_texto)
                except ValueError as erro:
                    raise ValueError(
                        f"Linha {numero_linha}: número ou peso inválido."
                    ) from erro
                if numero < 1:
                    raise ValueError(
                        f"Linha {numero_linha}: o número da questão deve ser positivo."
                    )
                if numero in numeros:
                    raise ValueError(f"Questão duplicada: {numero}.")
                numeros.add(numero)
                respostas_aceitas = [r.strip().upper() for r in respostas.split("|")]
                self._validar_questao(respostas_aceitas, peso, dificuldade)
                anulada_normalizada = anulada.upper()
                if anulada_normalizada not in {"SIM", "S", "NAO", "N", "NÃO"}:
                    raise ValueError(
                        f"Linha {numero_linha}: anulada deve ser SIM ou NAO."
                    )
                questoes.append(
                    Questao(
                        numero,
                        respostas_aceitas,
                        peso,
                        dificuldade.upper(),
                        anulada_normalizada in {"SIM", "S"},
                    )
                )
        if not questoes and salvar:
            raise ValueError("O arquivo de gabarito não possui questões.")
        self.prova.questoes = sorted(questoes, key=lambda questao: questao.numero)
        if salvar:
            self.salvar_gabarito()

    def _validar_questao(
        self, respostas_aceitas: list[str], peso: float, dificuldade: str
    ) -> None:
        if not respostas_aceitas or not set(respostas_aceitas).issubset(
            self.ALTERNATIVAS_VALIDAS
        ):
            raise ValueError("As respostas devem utilizar apenas A, B, C, D ou E.")
        if not isfinite(peso) or peso <= 0:
            raise ValueError("O peso deve ser maior que zero.")
        if dificuldade.upper() not in {"FACIL", "MEDIA", "DIFICIL"}:
            raise ValueError("A dificuldade deve ser FACIL, MEDIA ou DIFICIL.")

    def definir_gabarito(self, questoes: list[Questao]) -> None:
        if self.prova is None:
            raise ValueError("Selecione uma prova primeiro.")
        if not questoes:
            raise ValueError("O gabarito deve possuir pelo menos uma questão.")
        numeros: set[int] = set()
        for questao in questoes:
            if questao.numero < 1:
                raise ValueError("O número da questão deve ser positivo.")
            if questao.numero in numeros:
                raise ValueError(f"Questão duplicada: {questao.numero}.")
            numeros.add(questao.numero)
            self._validar_questao(
                questao.respostas_aceitas, questao.peso, questao.dificuldade
            )
        self.prova.questoes = sorted(questoes, key=lambda questao: questao.numero)
        self.salvar_gabarito()

    def salvar_gabarito(self) -> None:
        if self.prova is None:
            raise ValueError("Selecione uma prova primeiro.")
        self._invalidar_resultados()
        caminho = self.pasta_atual / "gabarito.txt"
        with caminho.open("w", encoding="utf-8", newline="") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";", lineterminator="\n")
            escritor.writerow(
                ["numero", "respostas_aceitas", "peso", "dificuldade", "anulada"]
            )
            for questao in self.prova.questoes:
                escritor.writerow(
                    [
                        questao.numero,
                        "|".join(questao.respostas_aceitas),
                        f"{questao.peso:.2f}",
                        questao.dificuldade,
                        "SIM" if questao.anulada else "NAO",
                    ]
                )

    def importar_respostas(self, caminho: Path, salvar: bool = True) -> list[str]:
        if self.prova is None or not self.prova.questoes:
            raise ValueError("Cadastre o gabarito antes de importar as respostas.")
        respostas_validas: dict[str, list[str]] = {}
        inconsistencias: list[str] = []
        with caminho.open(encoding="utf-8-sig") as arquivo:
            self._validar_cabecalho(
                arquivo, ["participante_id", "respostas"], caminho
            )
            for numero_linha, linha in enumerate(arquivo, start=2):
                if not linha.strip():
                    continue
                campos = [campo.strip() for campo in linha.split(";", maxsplit=1)]
                if len(campos) != 2:
                    inconsistencias.append(f"Linha {numero_linha}: formato inválido")
                    continue
                participante_id, texto_respostas = campos
                participante_id = participante_id.upper()
                respostas = [r.strip().upper() for r in texto_respostas.split(",")]
                erro = self._validar_respostas(
                    participante_id, respostas, respostas_validas
                )
                if erro:
                    inconsistencias.append(f"Linha {numero_linha}: {erro}")
                else:
                    respostas_validas[participante_id] = respostas
        self.respostas = respostas_validas
        self.inconsistencias = inconsistencias
        self.registros_validos = len(respostas_validas)
        self.registros_invalidos = len(inconsistencias)
        if salvar:
            self.salvar_respostas()
            self.salvar_inconsistencias()
        return inconsistencias

    def _validar_respostas(
        self,
        participante_id: str,
        respostas: list[str],
        respostas_existentes: dict[str, list[str]] | None = None,
    ) -> str | None:
        if respostas_existentes is None:
            respostas_existentes = self.respostas
        if participante_id not in self.participantes:
            return f"participante {participante_id} não cadastrado"
        if participante_id in respostas_existentes:
            return f"respostas duplicadas para {participante_id}"
        if self.prova is None or len(respostas) != len(self.prova.questoes):
            return "quantidade de respostas diferente da quantidade de questões"
        invalidas = [
            resposta
            for resposta in respostas
            if resposta not in self.ALTERNATIVAS_VALIDAS and resposta != "-"
        ]
        if invalidas:
            return f"alternativa inválida: {invalidas[0]}"
        return None

    def registrar_respostas(self, participante_id: str, respostas: list[str]) -> None:
        participante_id = participante_id.strip().upper()
        respostas = [resposta.strip().upper() for resposta in respostas]
        existentes = dict(self.respostas)
        existentes.pop(participante_id, None)
        erro = self._validar_respostas(participante_id, respostas, existentes)
        if erro:
            raise ValueError(erro)
        self.respostas[participante_id] = respostas
        self.registros_validos = len(self.respostas)
        self.resultados.clear()
        self.salvar_respostas()

    def salvar_respostas(self) -> None:
        self._invalidar_resultados()
        caminho = self.pasta_atual / "respostas.txt"
        with caminho.open("w", encoding="utf-8", newline="") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";", lineterminator="\n")
            escritor.writerow(["participante_id", "respostas"])
            for participante_id, respostas in self.respostas.items():
                escritor.writerow([participante_id, ",".join(respostas)])

    def salvar_inconsistencias(self) -> None:
        caminho = self.pasta_atual / "inconsistencias.txt"
        texto = "\n".join(self.inconsistencias)
        caminho.write_text(texto + ("\n" if texto else ""), encoding="utf-8")

    def corrigir(self, registrar_historico: bool = True) -> list[Resultado]:
        if self.prova is None or not self.prova.questoes:
            raise ValueError("Cadastre o gabarito antes de corrigir.")
        if not self.respostas:
            raise ValueError("Importe ou registre respostas antes de corrigir.")
        incompatibilidades: list[str] = []
        for participante_id, respostas in self.respostas.items():
            if participante_id not in self.participantes:
                incompatibilidades.append(
                    f"participante {participante_id} não cadastrado"
                )
            elif len(respostas) != len(self.prova.questoes):
                incompatibilidades.append(
                    f"{participante_id} possui {len(respostas)} respostas, "
                    f"mas o gabarito possui {len(self.prova.questoes)} questões"
                )
            else:
                invalidas = [
                    resposta
                    for resposta in respostas
                    if resposta not in self.ALTERNATIVAS_VALIDAS and resposta != "-"
                ]
                if invalidas:
                    incompatibilidades.append(
                        f"{participante_id} possui alternativa inválida: {invalidas[0]}"
                    )
        if incompatibilidades:
            detalhes = "; ".join(incompatibilidades[:3])
            if len(incompatibilidades) > 3:
                detalhes += f"; e mais {len(incompatibilidades) - 3} ocorrência(s)"
            raise ValueError(
                "As respostas não são compatíveis com os dados atuais: "
                f"{detalhes}. Reimporte ou corrija as respostas."
            )
        self.resultados.clear()
        for participante_id, respostas in self.respostas.items():
            participante = self.participantes[participante_id]
            pontuacao = 0.0
            acertos = 0
            erros = 0
            detalhes: list[str] = []
            for questao, resposta in zip(self.prova.questoes, respostas):
                correta = questao.esta_correta(resposta)
                situacao = "ANULADA" if questao.anulada else ("ACERTO" if correta else "ERRO")
                if correta:
                    pontuacao += questao.peso
                    acertos += 1
                else:
                    erros += 1
                detalhes.append(
                    f"Q{questao.numero}: resposta={resposta}, "
                    f"gabarito={'/'.join(questao.respostas_aceitas)}, "
                    f"situação={situacao}, peso={questao.peso:.2f}"
                )
            self.resultados.append(
                Resultado(participante, pontuacao, acertos, erros, detalhes)
            )
        self.resultados.sort(key=lambda resultado: resultado.pontuacao, reverse=True)
        self.exportar_resultados()
        if registrar_historico:
            self.registrar_historico()
        return self.resultados

    def exportar_resultados(self, caminho: Path | None = None) -> Path:
        if not self.resultados:
            raise ValueError("Execute a correção antes de exportar.")
        caminho = caminho or (self.pasta_atual / "resultados.csv")
        with caminho.open("w", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";")
            escritor.writerow(
                ["posicao", "id", "nome", "categoria", "pontuacao", "acertos", "erros"]
            )
            for posicao, resultado in enumerate(self.resultados, start=1):
                escritor.writerow(
                    [
                        posicao,
                        resultado.participante.identificador,
                        resultado.participante.nome,
                        resultado.participante.categoria,
                        f"{resultado.pontuacao:.2f}",
                        resultado.acertos,
                        resultado.erros,
                    ]
                )
        return caminho

    def registrar_historico(self) -> None:
        caminho = self.pasta_atual / "historico.txt"
        registros = self.ler_historico()
        identificador = f"CORR{len(registros) + 1:03d}"
        media = sum(resultado.pontuacao for resultado in self.resultados) / len(
            self.resultados
        )
        if not caminho.exists() or not caminho.read_text(encoding="utf-8").strip():
            caminho.write_text(
                "id;data_hora;registros_corrigidos;media\n", encoding="utf-8"
            )
        with caminho.open("a", encoding="utf-8") as arquivo:
            data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            arquivo.write(
                f"{identificador};{data};{len(self.resultados)};{media:.2f}\n"
            )

        pasta_historico = self.pasta_atual / "historico"
        pasta_historico.mkdir(exist_ok=True)
        shutil.copyfile(
            self.pasta_atual / "resultados.csv",
            pasta_historico / f"{identificador}_resultados.csv",
        )
        shutil.copyfile(
            self.pasta_atual / "gabarito.txt",
            pasta_historico / f"{identificador}_gabarito.txt",
        )

    def ler_historico(self) -> list[dict[str, str]]:
        caminho = self.pasta_atual / "historico.txt"
        if not caminho.exists():
            return []
        with caminho.open(encoding="utf-8") as arquivo:
            linhas = [linha.strip() for linha in arquivo if linha.strip()]
        if len(linhas) <= 1:
            return []
        registros: list[dict[str, str]] = []
        for linha in linhas[1:]:
            campos = linha.split(";")
            if len(campos) == 4:
                registros.append(
                    {
                        "id": campos[0],
                        "data_hora": campos[1],
                        "quantidade": campos[2],
                        "media": campos[3],
                    }
                )
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
        return next(
            (
                resultado
                for resultado in self.resultados
                if resultado.participante.identificador == participante_id
            ),
            None,
        )

    def estatisticas_questoes(self) -> list[tuple[int, float, float]]:
        if not self.resultados or self.prova is None:
            raise ValueError("Execute a correção antes de gerar estatísticas.")
        quantidade = len(self.resultados)
        tamanho_grupo = max(1, round(quantidade * 0.27))
        ids_superiores = {
            resultado.participante.identificador
            for resultado in self.resultados[:tamanho_grupo]
        }
        ids_inferiores = {
            resultado.participante.identificador
            for resultado in self.resultados[-tamanho_grupo:]
        }
        estatisticas: list[tuple[int, float, float]] = []
        for indice, questao in enumerate(self.prova.questoes):
            acertos = sum(
                questao.esta_correta(respostas[indice])
                for respostas in self.respostas.values()
            )
            taxa = acertos / quantidade
            superiores = sum(
                questao.esta_correta(self.respostas[identificador][indice])
                for identificador in ids_superiores
            ) / tamanho_grupo
            inferiores = sum(
                questao.esta_correta(self.respostas[identificador][indice])
                for identificador in ids_inferiores
            ) / tamanho_grupo
            estatisticas.append((questao.numero, taxa, superiores - inferiores))
        return estatisticas
