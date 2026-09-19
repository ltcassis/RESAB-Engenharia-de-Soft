from dataclasses import dataclass, field


@dataclass
class Questao:
    numero: int
    respostas_aceitas: list[str]
    peso: float = 1.0
    dificuldade: str = "MEDIA"
    anulada: bool = False

    def esta_correta(self, resposta: str) -> bool:
        return self.anulada or resposta.upper() in self.respostas_aceitas


@dataclass
class Prova:
    identificador: str
    nome: str
    disciplina: str
    categoria: str
    questoes: list[Questao] = field(default_factory=list)

    def pontuacao_maxima(self) -> float:
        return sum(questao.peso for questao in self.questoes)


@dataclass
class Participante:
    identificador: str
    nome: str
    categoria: str


@dataclass
class Resultado:
    participante: Participante
    pontuacao: float
    acertos: int
    erros: int
    detalhes: list[str]

