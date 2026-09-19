import csv
import math
import tempfile
import unittest
from pathlib import Path

from modelos import Questao
from sistema import CorretorProvas


class CorretorProvasTestes(unittest.TestCase):
    def setUp(self) -> None:
        self.temporario = tempfile.TemporaryDirectory()
        self.pasta = Path(self.temporario.name)
        self.corretor = CorretorProvas(self.pasta)
        self.corretor.criar_prova(
            "OBM2026", "Olimpíada de Matemática", "Matemática", "Nível 1"
        )

    def tearDown(self) -> None:
        self.temporario.cleanup()

    def definir_gabarito_padrao(self) -> None:
        self.corretor.definir_gabarito(
            [
                Questao(1, ["A"], 1.0, "FACIL", False),
                Questao(2, ["B", "C"], 2.0, "MEDIA", False),
                Questao(3, ["D"], 1.5, "DIFICIL", True),
            ]
        )

    def test_criacao_e_persistencia_da_prova(self) -> None:
        prova = self.corretor.listar_provas()[0]
        self.assertEqual(prova.identificador, "OBM2026")
        self.assertEqual(prova.disciplina, "Matemática")
        self.assertTrue((self.pasta / "provas" / "OBM2026").is_dir())

        recarregado = CorretorProvas(self.pasta)
        recarregado.selecionar_prova("obm2026")
        self.assertEqual(recarregado.prova.nome, "Olimpíada de Matemática")

    def test_catalogo_invalido_nao_e_ignorado(self) -> None:
        arquivo = self.pasta / "provas.txt"
        arquivo.write_text(
            "id;nome;disciplina;categoria\nLINHA;INCOMPLETA\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "Linha 2 inválida"):
            self.corretor.listar_provas()

    def test_rejeita_ids_e_campos_invalidos(self) -> None:
        with self.assertRaises(ValueError):
            self.corretor.criar_prova("ID INVÁLIDO", "Outra", "Matemática", "Nível 2")
        with self.assertRaises(ValueError):
            self.corretor.criar_prova("OUTRA", "Nome;quebrado", "Matemática", "Nível 2")
        with self.assertRaises(ValueError):
            self.corretor.cadastrar_participante("A 01", "Ana", "Nível 1")

    def test_rejeita_gabarito_invalido(self) -> None:
        with self.assertRaises(ValueError):
            self.corretor.definir_gabarito([])
        with self.assertRaises(ValueError):
            self.corretor.definir_gabarito(
                [Questao(1, ["F"], 1.0, "FACIL", False)]
            )
        with self.assertRaises(ValueError):
            self.corretor.definir_gabarito(
                [Questao(1, ["A"], math.nan, "FACIL", False)]
            )
        with self.assertRaises(ValueError):
            self.corretor.definir_gabarito(
                [
                    Questao(1, ["A"], 1.0, "FACIL", False),
                    Questao(1, ["B"], 1.0, "MEDIA", False),
                ]
            )

    def test_importacao_rejeita_cabecalho_e_anulada_invalidos(self) -> None:
        caminho = self.pasta / "gabarito_invalido.txt"
        caminho.write_text("coluna;errada\n1;A\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Cabeçalho inválido"):
            self.corretor.importar_gabarito(caminho)

        caminho.write_text(
            "numero;respostas_aceitas;peso;dificuldade;anulada\n"
            "1;A;1.0;FACIL;TALVEZ\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "anulada deve ser SIM ou NAO"):
            self.corretor.importar_gabarito(caminho)

    def test_importacao_de_respostas_separa_validas_e_invalidas(self) -> None:
        self.definir_gabarito_padrao()
        self.corretor.cadastrar_participante("A001", "Ana", "Nível 1")
        self.corretor.cadastrar_participante("A002", "Bruno", "Nível 1")
        caminho = self.pasta / "respostas_teste.txt"
        caminho.write_text(
            "participante_id;respostas\n"
            "A001;A,C,E\n"
            "A001;A,B,D\n"
            "A002;A,X,D\n"
            "A999;A,B,D\n",
            encoding="utf-8",
        )

        inconsistencias = self.corretor.importar_respostas(caminho)

        self.assertEqual(self.corretor.registros_validos, 1)
        self.assertEqual(self.corretor.registros_invalidos, 3)
        self.assertEqual(set(self.corretor.respostas), {"A001"})
        self.assertEqual(len(inconsistencias), 3)

    def test_correcao_considera_peso_resposta_dupla_e_anulada(self) -> None:
        self.definir_gabarito_padrao()
        self.corretor.cadastrar_participante("A001", "Ana", "Nível 1")
        self.corretor.cadastrar_participante("A002", "Bruno", "Nível 1")
        self.corretor.registrar_respostas("A001", ["A", "C", "E"])
        self.corretor.registrar_respostas("A002", ["E", "B", "-"])

        resultados = self.corretor.corrigir()

        self.assertEqual(resultados[0].participante.identificador, "A001")
        self.assertEqual(resultados[0].pontuacao, 4.5)
        self.assertEqual(resultados[0].acertos, 3)
        self.assertEqual(resultados[0].erros, 0)
        self.assertEqual(resultados[1].pontuacao, 3.5)
        self.assertTrue((self.corretor.pasta_atual / "resultados.csv").exists())
        self.assertEqual(len(self.corretor.ler_historico()), 1)

    def test_impede_correcao_com_respostas_antigas_apos_mudar_questoes(self) -> None:
        self.definir_gabarito_padrao()
        self.corretor.cadastrar_participante("A001", "Ana", "Nível 1")
        self.corretor.registrar_respostas("A001", ["A", "B", "D"])
        self.corretor.prova.questoes.append(
            Questao(4, ["E"], 1.0, "MEDIA", False)
        )
        self.corretor.salvar_gabarito()

        with self.assertRaisesRegex(ValueError, "não são compatíveis"):
            self.corretor.corrigir()

    def test_impede_correcao_se_participante_nao_existe_mais(self) -> None:
        self.definir_gabarito_padrao()
        self.corretor.cadastrar_participante("A001", "Ana", "Nível 1")
        self.corretor.registrar_respostas("A001", ["A", "B", "D"])
        arquivo = self.pasta / "participantes_vazios.txt"
        arquivo.write_text("id;nome;categoria\n", encoding="utf-8")
        self.corretor.importar_participantes(arquivo)

        with self.assertRaisesRegex(ValueError, "não são compatíveis"):
            self.corretor.corrigir()

    def test_recarregamento_nao_cria_historico_extra(self) -> None:
        self.definir_gabarito_padrao()
        self.corretor.cadastrar_participante("A001", "Ana", "Nível 1")
        self.corretor.registrar_respostas("A001", ["A", "B", "D"])
        self.corretor.corrigir()
        self.assertEqual(len(self.corretor.ler_historico()), 1)

        recarregado = CorretorProvas(self.pasta)
        recarregado.selecionar_prova("OBM2026")
        self.assertEqual(len(recarregado.resultados), 1)
        self.assertEqual(len(recarregado.ler_historico()), 1)

    def test_recarregamento_preserva_relatorio_de_inconsistencias(self) -> None:
        self.definir_gabarito_padrao()
        self.corretor.cadastrar_participante("A001", "Ana", "Nível 1")
        arquivo = self.pasta / "respostas_com_erro.txt"
        arquivo.write_text(
            "participante_id;respostas\n"
            "A001;A,B,D\n"
            "A999;A,B,D\n",
            encoding="utf-8",
        )
        self.corretor.importar_respostas(arquivo)
        self.assertEqual(self.corretor.registros_invalidos, 1)

        recarregado = CorretorProvas(self.pasta)
        recarregado.selecionar_prova("OBM2026")
        self.assertEqual(recarregado.registros_invalidos, 1)
        self.assertEqual(len(recarregado.inconsistencias), 1)
        self.assertIn("A999", recarregado.inconsistencias[0])

    def test_csv_e_estatisticas_sao_gerados(self) -> None:
        self.definir_gabarito_padrao()
        self.corretor.cadastrar_participante("A001", "Ana", "Nível 1")
        self.corretor.cadastrar_participante("A002", "Bruno", "Nível 1")
        self.corretor.registrar_respostas("A001", ["A", "B", "D"])
        self.corretor.registrar_respostas("A002", ["E", "E", "D"])
        self.corretor.corrigir()

        estatisticas = self.corretor.estatisticas_questoes()
        self.assertEqual(len(estatisticas), 3)
        self.assertEqual(estatisticas[0][1], 0.5)

        caminho = self.pasta / "exportado.csv"
        self.corretor.exportar_resultados(caminho)
        with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
            linhas = list(csv.reader(arquivo, delimiter=";"))
        self.assertEqual(linhas[0][0], "posicao")
        self.assertEqual(len(linhas), 3)


if __name__ == "__main__":
    unittest.main()
