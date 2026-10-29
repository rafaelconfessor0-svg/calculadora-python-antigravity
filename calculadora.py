#!/usr/bin/env python3
# ==============================================================================
# CALCULADORA CIENTÍFICA E MULTIFUNCIONAL EM PYTHON
# ==============================================================================
# Recursos:
# 1. Aritmética Completa (+, -, *, /, //, %, inverso, abs)
# 2. Potenciação e Radiciação (x^y, x², x³, √, ∛, raiz n-ésima)
# 3. Porcentagem e Finanças (%, acréscimo, desconto, variação %, juros simples e compostos)
# 4. Funções Científicas e Trigonometria (sin, cos, tan, arc, ln, log10, log_b, fat, exp)
# 5. Estatística Descritiva (média, mediana, moda, desvio padrão, variância, min/max/soma)
# 6. Conversor de Bases Numéricas (Decimal, Binário, Octal, Hexadecimal)
# 7. Avaliador de Expressões Livres (seguro via AST, ex: 3*(4+5) + sqrt(16) - 2^3)
# 8. Histórico de Cálculos e Memória (ANS, M+, M-, MR, MC)
# ==============================================================================

import ast
from datetime import datetime
import math
import operator
import os
import statistics
import sys
from typing import Any, Callable, List, Optional, Union

# ------------------------------------------------------------------------------
# Configurações Visuais e Cores ANSI
# ------------------------------------------------------------------------------
SUPPORTS_COLOR = sys.stdout.isatty() and os.name != 'nt' or 'ANSICON' in os.environ or 'WT_SESSION' in os.environ

class Style:
    if SUPPORTS_COLOR:
        RESET = "\033[0m"
        BOLD = "\033[1m"
        DIM = "\033[2m"
        CYAN = "\033[96m"
        BLUE = "\033[94m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        RED = "\033[91m"
        MAGENTA = "\033[95m"
    else:
        RESET = BOLD = DIM = CYAN = BLUE = GREEN = YELLOW = RED = MAGENTA = ""

def title_banner(text: str) -> str:
    line = "=" * 60
    return f"{Style.CYAN}{line}\n{text.center(60)}\n{line}{Style.RESET}"

def section_banner(text: str) -> str:
    line = "-" * 50
    return f"{Style.BLUE}\n{line}\n  {text}\n{line}{Style.RESET}"

def success(text: str) -> str:
    return f"{Style.GREEN}{Style.BOLD}✅ {text}{Style.RESET}"

def alert(text: str) -> str:
    return f"{Style.YELLOW}⚠️  {text}{Style.RESET}"

def error(text: str) -> str:
    return f"{Style.RED}❌ {text}{Style.RESET}"


# ------------------------------------------------------------------------------
# Estado Global da Sessão (Histórico, Memória, ANS e Modo Angular)
# ------------------------------------------------------------------------------
class CalculatorSession:
    def __init__(self):
        self.ans: float = 0.0
        self.memory: float = 0.0
        self.angle_mode: str = "deg"  # "deg" (Graus) ou "rad" (Radianos)
        self.history: List[dict] = []

    def save_result(self, operation: str, result: Union[float, int, str]) -> None:
        if isinstance(result, (int, float)):
            self.ans = float(result)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.history.append({
            "time": timestamp,
            "operation": operation,
            "result": result
        })
        if len(self.history) > 50:
            self.history.pop(0)

    def clear_history(self) -> None:
        self.history.clear()


session = CalculatorSession()


# ------------------------------------------------------------------------------
# Utilitários de Entrada e Formatação Numérica
# ------------------------------------------------------------------------------
def fmt(val: Any) -> str:
    """Formata números para exibição elegante, eliminando ruídos decimais."""
    if isinstance(val, (int, float)):
        if math.isnan(val):
            return "NaN"
        if math.isinf(val):
            return "Infinito" if val > 0 else "-Infinito"
        # Se for praticamente inteiro
        if abs(val - round(val)) < 1e-11:
            int_val = int(round(val))
            return f"{int_val}"
        # Arredonda ruído de representação flutuante
        rounded = round(val, 8)
        if rounded == int(rounded):
            return f"{int(rounded)}"
        # Remove zeros excedentes à direita
        txt = f"{val:.8f}".rstrip('0').rstrip('.')
        return txt
    return str(val)

def parse_number(prompt: str, allow_empty: bool = False, default: Optional[float] = None) -> float:
    """
    Lê um número do teclado com suporte a:
    - Vírgula ou ponto decimal (ex: 3,14 ou 3.14)
    - Constantes: 'pi', 'e', 'tau', 'phi'
    - 'ans' (resultado anterior)
    - 'mem' (memória)
    """
    while True:
        try:
            raw = input(f"{Style.BOLD}{prompt}{Style.RESET}").strip()
            if not raw:
                if allow_empty and default is not None:
                    return default
                print(alert("Entrada vazia. Por favor, digite um valor."))
                continue

            lower = raw.lower()
            if lower == 'ans':
                print(f"   ↳ [Usando ANS = {fmt(session.ans)}]")
                return session.ans
            elif lower == 'mem':
                print(f"   ↳ [Usando Memória = {fmt(session.memory)}]")
                return session.memory
            elif lower == 'pi':
                return math.pi
            elif lower == 'e':
                return math.e
            elif lower == 'tau':
                return math.tau
            elif lower == 'phi':
                return (1 + math.sqrt(5)) / 2

            # Trata vírgula como separador decimal
            cleaned = raw.replace(',', '.')
            return float(cleaned)

        except ValueError:
            print(error("Número inválido! Digite um valor numérico (ex: 10, 3.5, 3,14) ou 'ans', 'pi'."))
        except (KeyboardInterrupt, EOFError):
            print()
            raise


# ------------------------------------------------------------------------------
# 1. Operações Aritméticas Básicas e Avançadas
# ------------------------------------------------------------------------------
def somar(a: float, b: float) -> float:
    return a + b

def subtrair(a: float, b: float) -> float:
    return a - b

def multiplicar(a: float, b: float) -> float:
    return a * b

def dividir(a: float, b: float) -> float:
    if b == 0:
        raise ZeroDivisionError("Divisão por zero não é permitida.")
    return a / b

def divisao_inteira(a: float, b: float) -> int:
    if b == 0:
        raise ZeroDivisionError("Divisão por zero não é permitida.")
    return int(a // b)

def resto_divisao(a: float, b: float) -> float:
    if b == 0:
        raise ZeroDivisionError("Módulo por zero não é permitido.")
    return a % b

def inverso(a: float) -> float:
    if a == 0:
        raise ZeroDivisionError("Não existe inverso multiplicativo de zero (1/0).")
    return 1 / a

def valor_absoluto(a: float) -> float:
    return abs(a)


# ------------------------------------------------------------------------------
# 2. Potenciação e Radiciação
# ------------------------------------------------------------------------------
def potencia(base: float, expoente: float) -> float:
    if base == 0 and expoente < 0:
        raise ZeroDivisionError("Zero elevado a expoente negativo é indefinido.")
    # Evita raiz complexa por enquanto no modo real
    if base < 0 and int(expoente) != expoente:
        raise ValueError("Potência com base negativa e expoente fracionário gera número complexo.")
    return math.pow(base, expoente)

def raiz_quadrada(a: float) -> float:
    if a < 0:
        raise ValueError("Não existe raiz quadrada de número negativo nos números reais.")
    return math.sqrt(a)

def raiz_cubica(a: float) -> float:
    if a < 0:
        return -math.pow(-a, 1/3)
    return math.pow(a, 1/3)

def raiz_enesima(radicando: float, indice: float) -> float:
    if indice == 0:
        raise ZeroDivisionError("O índice da raiz não pode ser zero.")
    if radicando < 0:
        if int(indice) == indice and int(indice) % 2 != 0:
            return -math.pow(-radicando, 1 / indice)
        raise ValueError(f"Não existe raiz real de índice par ({indice}) para número negativo.")
    return math.pow(radicando, 1 / indice)


# ------------------------------------------------------------------------------
# 3. Porcentagem e Finanças
# ------------------------------------------------------------------------------
def porcentagem_de(pct: float, total: float) -> float:
    """Calcula pct% de total."""
    return (pct / 100.0) * total

def acrescimo_percentual(valor: float, pct: float) -> float:
    """Aumenta valor em pct%."""
    return valor + (valor * pct / 100.0)

def desconto_percentual(valor: float, pct: float) -> float:
    """Diminui valor em pct%."""
    return valor - (valor * pct / 100.0)

def variacao_percentual(inicial: float, final: float) -> float:
    """Calcula a variação percentual de inicial para final."""
    if inicial == 0:
        raise ZeroDivisionError("O valor inicial não pode ser zero para calcular a variação percentual.")
    return ((final - inicial) / abs(inicial)) * 100.0

def juros_simples(capital: float, taxa_pct: float, periodos: float) -> tuple[float, float]:
    """Retorna (Juros, Montante Final)."""
    juros = capital * (taxa_pct / 100.0) * periodos
    montante = capital + juros
    return juros, montante

def juros_compostos(capital: float, taxa_pct: float, periodos: float) -> tuple[float, float]:
    """Retorna (Rendimento, Montante Final)."""
    montante = capital * math.pow(1.0 + taxa_pct / 100.0, periodos)
    rendimento = montante - capital
    return rendimento, montante


# ------------------------------------------------------------------------------
# 4. Funções Científicas e Trigonometria
# ------------------------------------------------------------------------------
def fatorial(n: float) -> int:
    if int(n) != n or n < 0:
        raise ValueError("Fatorial só é definido para números inteiros não negativos (0, 1, 2, ...).")
    if n > 1500:
        raise ValueError("Número muito grande para cálculo de fatorial.")
    return math.factorial(int(n))

def to_radians(angle: float) -> float:
    return math.radians(angle) if session.angle_mode == "deg" else angle

def from_radians(angle: float) -> float:
    return math.degrees(angle) if session.angle_mode == "deg" else angle

def seno(x: float) -> float:
    val = math.sin(to_radians(x))
    return 0.0 if abs(val) < 1e-15 else val

def cosseno(x: float) -> float:
    val = math.cos(to_radians(x))
    return 0.0 if abs(val) < 1e-15 else val

def tangente(x: float) -> float:
    rad = to_radians(x)
    # Cos próximo de 0 => tangente indefinida
    if abs(math.cos(rad)) < 1e-14:
        raise ValueError("Tangente indefinida (assíntota vertical).")
    val = math.tan(rad)
    return 0.0 if abs(val) < 1e-15 else val

def arco_seno(x: float) -> float:
    if x < -1 or x > 1:
        raise ValueError("O domínio do arco-seno é de -1 a 1.")
    return from_radians(math.asin(x))

def arco_cosseno(x: float) -> float:
    if x < -1 or x > 1:
        raise ValueError("O domínio do arco-cosseno é de -1 a 1.")
    return from_radians(math.acos(x))

def arco_tangente(x: float) -> float:
    return from_radians(math.atan(x))

def log_natural(x: float) -> float:
    if x <= 0:
        raise ValueError("Logaritmo natural é definido apenas para x > 0.")
    return math.log(x)

def log_base10(x: float) -> float:
    if x <= 0:
        raise ValueError("Logaritmo na base 10 é definido apenas para x > 0.")
    return math.log10(x)

def log_base_b(x: float, base: float) -> float:
    if x <= 0:
        raise ValueError("O logaritmando deve ser maior que 0.")
    if base <= 0 or base == 1:
        raise ValueError("A base do logaritmo deve ser maior que 0 e diferente de 1.")
    return math.log(x, base)

def exponencial(x: float) -> float:
    return math.exp(x)


# ------------------------------------------------------------------------------
# 5. Avaliador Seguro de Expressões Livres (via AST)
# ------------------------------------------------------------------------------
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def safe_eval(expr_str: str) -> float:
    """Avalia seguramente expressões matemáticas com funções e constantes."""
    clean_expr = expr_str.replace('^', '**').replace(',', '.')
    parsed = ast.parse(clean_expr, mode='eval')

    constants = {
        'pi': math.pi,
        'e': math.e,
        'tau': math.tau,
        'phi': (1 + math.sqrt(5)) / 2,
        'ans': session.ans,
        'mem': session.memory,
    }

    functions = {
        'sqrt': math.sqrt,
        'cbrt': math.cbrt if hasattr(math, 'cbrt') else raiz_cubica,
        'abs': abs,
        'fact': fatorial,
        'factorial': fatorial,
        'sin': seno,
        'cos': cosseno,
        'tan': tangente,
        'asin': arco_seno,
        'acos': arco_cosseno,
        'atan': arco_tangente,
        'ln': log_natural,
        'log': log_natural,
        'log10': log_base10,
        'log2': math.log2,
        'exp': math.exp,
        'rad': math.radians,
        'deg': math.degrees,
    }

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Tipo de valor não suportado: {node.value}")
        elif isinstance(node, ast.Name):
            name = node.id.lower()
            if name in constants:
                return constants[name]
            raise ValueError(f"Constante ou variável desconhecida: '{node.id}'")
        elif isinstance(node, ast.UnaryOp):
            op = type(node.op)
            if op in SAFE_OPERATORS:
                return SAFE_OPERATORS[op](_eval(node.operand))
            raise ValueError(f"Operador unário não suportado: {op}")
        elif isinstance(node, ast.BinOp):
            op = type(node.op)
            if op in SAFE_OPERATORS:
                left = _eval(node.left)
                right = _eval(node.right)
                if op == ast.Div and right == 0:
                    raise ZeroDivisionError("Divisão por zero na expressão.")
                if op == ast.FloorDiv and right == 0:
                    raise ZeroDivisionError("Divisão inteira por zero.")
                if op == ast.Mod and right == 0:
                    raise ZeroDivisionError("Módulo por zero.")
                return SAFE_OPERATORS[op](left, right)
            raise ValueError(f"Operador binário não suportado: {op}")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id.lower()
                if func_name in functions:
                    args = [_eval(arg) for arg in node.args]
                    return functions[func_name](*args)
                raise ValueError(f"Função '{func_name}' não suportada")
            raise ValueError("Chamada de função inválida")
        else:
            raise ValueError(f"Elemento de sintaxe não permitido: {type(node).__name__}")

    return _eval(parsed)


# ------------------------------------------------------------------------------
# MENUS INTERATIVOS POR CATEGORIA
# ------------------------------------------------------------------------------

def menu_aritmetica():
    while True:
        print(section_banner("1. ARITMÉTICA BÁSICA E AVANÇADA"))
        print("  1 - Adição (+)")
        print("  2 - Subtração (-)")
        print("  3 - Multiplicação (*)")
        print("  4 - Divisão Real (/)")
        print("  5 - Divisão Inteira (//)")
        print("  6 - Resto da Divisão / Módulo (%)")
        print("  7 - Inverso Multiplicativo (1/x)")
        print("  8 - Valor Absoluto (|x|)")
        print("  0 - Voltar ao Menu Principal")

        op = input(f"\n{Style.BOLD}Escolha uma opção: {Style.RESET}").strip()
        if op == "0":
            break

        try:
            if op in ("1", "2", "3", "4", "5", "6"):
                n1 = parse_number("Digite o 1º número (ou 'ans'): ")
                n2 = parse_number("Digite o 2º número (ou 'ans'): ")

                if op == "1":
                    res = somar(n1, n2)
                    expr = f"{fmt(n1)} + {fmt(n2)}"
                elif op == "2":
                    res = subtrair(n1, n2)
                    expr = f"{fmt(n1)} - {fmt(n2)}"
                elif op == "3":
                    res = multiplicar(n1, n2)
                    expr = f"{fmt(n1)} * {fmt(n2)}"
                elif op == "4":
                    res = dividir(n1, n2)
                    expr = f"{fmt(n1)} / {fmt(n2)}"
                elif op == "5":
                    res = divisao_inteira(n1, n2)
                    expr = f"{fmt(n1)} // {fmt(n2)}"
                elif op == "6":
                    res = resto_divisao(n1, n2)
                    expr = f"{fmt(n1)} % {fmt(n2)}"

                session.save_result(expr, res)
                print(f"\n{success(f'{expr} = {fmt(res)}')}")

            elif op in ("7", "8"):
                n = parse_number("Digite o número (ou 'ans'): ")
                if op == "7":
                    res = inverso(n)
                    expr = f"1 / {fmt(n)}"
                else:
                    res = valor_absoluto(n)
                    expr = f"|{fmt(n)}|"

                session.save_result(expr, res)
                print(f"\n{success(f'{expr} = {fmt(res)}')}")
            else:
                print(alert("Opção inválida! Escolha entre 0 e 8."))

        except (ZeroDivisionError, ValueError) as err:
            print(f"\n{error(str(err))}")
        except (KeyboardInterrupt, EOFError):
            print("\nOperação cancelada.")
            break


def menu_potenciacao_radiciacao():
    while True:
        print(section_banner("2. POTENCIAÇÃO E RADICIAÇÃO"))
        print("  1 - Potência (x^y)")
        print("  2 - Quadrado (x²)")
        print("  3 - Cubo (x³)")
        print("  4 - Raiz Quadrada (√x)")
        print("  5 - Raiz Cúbica (∛x)")
        print("  6 - Raiz Enésima (índice n)")
        print("  0 - Voltar ao Menu Principal")

        op = input(f"\n{Style.BOLD}Escolha uma opção: {Style.RESET}").strip()
        if op == "0":
            break

        try:
            if op == "1":
                base = parse_number("Base (x): ")
                exp = parse_number("Expoente (y): ")
                res = potencia(base, exp)
                expr = f"{fmt(base)}^{fmt(exp)}"
            elif op == "2":
                base = parse_number("Número (x): ")
                res = potencia(base, 2)
                expr = f"{fmt(base)}²"
            elif op == "3":
                base = parse_number("Número (x): ")
                res = potencia(base, 3)
                expr = f"{fmt(base)}³"
            elif op == "4":
                num = parse_number("Número (x >= 0): ")
                res = raiz_quadrada(num)
                expr = f"√{fmt(num)}"
            elif op == "5":
                num = parse_number("Número (x): ")
                res = raiz_cubica(num)
                expr = f"∛{fmt(num)}"
            elif op == "6":
                radicando = parse_number("Radicando (número dentro da raiz): ")
                indice = parse_number("Índice da raiz (n): ")
                res = raiz_enesima(radicando, indice)
                expr = f"raiz_{fmt(indice)}({fmt(radicando)})"
            else:
                print(alert("Opção inválida!"))
                continue

            session.save_result(expr, res)
            print(f"\n{success(f'{expr} = {fmt(res)}')}")

        except (ZeroDivisionError, ValueError, OverflowError) as err:
            print(f"\n{error(str(err))}")
        except (KeyboardInterrupt, EOFError):
            print("\nOperação cancelada.")
            break


def menu_porcentagem_financas():
    while True:
        print(section_banner("3. PORCENTAGEM E FINANÇAS"))
        print("  1 - Calcular X% de Y")
        print("  2 - Acréscimo Percentual (Valor + X%)")
        print("  3 - Desconto Percentual (Valor - X%)")
        print("  4 - Variação Percentual entre 2 valores")
        print("  5 - Juros Simples (J = C * i * t)")
        print("  6 - Juros Compostos (M = C * (1 + i)^t)")
        print("  0 - Voltar ao Menu Principal")

        op = input(f"\n{Style.BOLD}Escolha uma opção: {Style.RESET}").strip()
        if op == "0":
            break

        try:
            if op == "1":
                pct = parse_number("Porcentagem (%): ")
                total = parse_number("Valor total: ")
                res = porcentagem_de(pct, total)
                expr = f"{fmt(pct)}% de {fmt(total)}"
                session.save_result(expr, res)
                print(f"\n{success(f'{expr} = {fmt(res)}')}")

            elif op == "2":
                val = parse_number("Valor original: ")
                pct = parse_number("Acréscimo (%): ")
                res = acrescimo_percentual(val, pct)
                expr = f"{fmt(val)} + {fmt(pct)}%"
                diff = res - val
                session.save_result(expr, res)
                print(f"\n{success(f'Novo valor: {fmt(res)} (Aumento de {fmt(diff)})')}")

            elif op == "3":
                val = parse_number("Valor original: ")
                pct = parse_number("Desconto (%): ")
                res = desconto_percentual(val, pct)
                expr = f"{fmt(val)} - {fmt(pct)}%"
                diff = val - res
                session.save_result(expr, res)
                print(f"\n{success(f'Novo valor: {fmt(res)} (Desconto de {fmt(diff)})')}")

            elif op == "4":
                ini = parse_number("Valor Inicial: ")
                fim = parse_number("Valor Final: ")
                res = variacao_percentual(ini, fim)
                expr = f"Variação de {fmt(ini)} para {fmt(fim)}"
                sinal = "+" if res > 0 else ""
                session.save_result(expr, res)
                print(f"\n{success(f'Variação: {sinal}{fmt(res)}%')}")

            elif op == "5":
                c = parse_number("Capital inicial (R$): ")
                i = parse_number("Taxa de juros por período (%): ")
                t = parse_number("Número de períodos (tempo): ")
                juros, montante = juros_simples(c, i, t)
                session.save_result(f"Juros Simples M({fmt(c)})", montante)
                print(f"\n{success('Cálculo Concluído:')}")
                print(f"   • Total em Juros: R$ {fmt(juros)}")
                print(f"   • Montante Final: R$ {fmt(montante)}")

            elif op == "6":
                c = parse_number("Capital inicial (R$): ")
                i = parse_number("Taxa de juros por período (%): ")
                t = parse_number("Número de períodos (tempo): ")
                rendimento, montante = juros_compostos(c, i, t)
                session.save_result(f"Juros Compostos M({fmt(c)})", montante)
                print(f"\n{success('Cálculo Concluído:')}")
                print(f"   • Total de Rendimentos: R$ {fmt(rendimento)}")
                print(f"   • Montante Final: R$ {fmt(montante)}")

            else:
                print(alert("Opção inválida!"))

        except (ZeroDivisionError, ValueError) as err:
            print(f"\n{error(str(err))}")
        except (KeyboardInterrupt, EOFError):
            print("\nOperação cancelada.")
            break


def menu_cientifica():
    while True:
        modo_txt = "Graus (DEG)" if session.angle_mode == "deg" else "Radianos (RAD)"
        print(section_banner(f"4. FUNÇÕES CIENTÍFICAS E TRIGONOMETRIA [{modo_txt}]"))
        print(f"  [M] Alternar Modo Angular (Atual: {Style.YELLOW}{session.angle_mode.upper()}{Style.RESET})")
        print("  1 - Fatorial (n!)")
        print("  2 - Seno (sin)")
        print("  3 - Cosseno (cos)")
        print("  4 - Tangente (tan)")
        print("  5 - Arco-Seno (asin)")
        print("  6 - Arco-Cosseno (acos)")
        print("  7 - Arco-Tangente (atan)")
        print("  8 - Logaritmo Natural (ln)")
        print("  9 - Logaritmo Base 10 (log10)")
        print("  10 - Logaritmo Base Personalizada (log_b)")
        print("  11 - Exponencial (e^x)")
        print("  12 - Exibir Constantes Matemáticas (pi, e, tau, phi)")
        print("  0 - Voltar ao Menu Principal")

        op = input(f"\n{Style.BOLD}Escolha uma opção: {Style.RESET}").strip()
        if op == "0":
            break

        if op.lower() == "m":
            session.angle_mode = "rad" if session.angle_mode == "deg" else "deg"
            print(f"\n{success(f'Modo angular alterado para: {session.angle_mode.upper()}')}")
            continue

        try:
            if op == "1":
                n = parse_number("Número inteiro não negativo (n): ")
                res = fatorial(n)
                expr = f"{fmt(n)}!"
            elif op == "2":
                ang = parse_number(f"Ângulo em {modo_txt}: ")
                res = seno(ang)
                expr = f"sin({fmt(ang)})"
            elif op == "3":
                ang = parse_number(f"Ângulo em {modo_txt}: ")
                res = cosseno(ang)
                expr = f"cos({fmt(ang)})"
            elif op == "4":
                ang = parse_number(f"Ângulo em {modo_txt}: ")
                res = tangente(ang)
                expr = f"tan({fmt(ang)})"
            elif op == "5":
                val = parse_number("Valor (-1 a 1): ")
                res = arco_seno(val)
                expr = f"asin({fmt(val)})"
            elif op == "6":
                val = parse_number("Valor (-1 a 1): ")
                res = arco_cosseno(val)
                expr = f"acos({fmt(val)})"
            elif op == "7":
                val = parse_number("Valor: ")
                res = arco_tangente(val)
                expr = f"atan({fmt(val)})"
            elif op == "8":
                val = parse_number("Valor (x > 0): ")
                res = log_natural(val)
                expr = f"ln({fmt(val)})"
            elif op == "9":
                val = parse_number("Valor (x > 0): ")
                res = log_base10(val)
                expr = f"log10({fmt(val)})"
            elif op == "10":
                val = parse_number("Valor (x > 0): ")
                base = parse_number("Base (b > 0 e b != 1): ")
                res = log_base_b(val, base)
                expr = f"log_{fmt(base)}({fmt(val)})"
            elif op == "11":
                val = parse_number("Expoente (x): ")
                res = exponencial(val)
                expr = f"e^({fmt(val)})"
            elif op == "12":
                print(f"\n{Style.CYAN}--- Principais Constantes ---{Style.RESET}")
                print(f"  • π (Pi):                {math.pi}")
                print(f"  • e (Número de Euler):   {math.e}")
                print(f"  • τ (Tau = 2*π):         {math.tau}")
                phi = (1 + math.sqrt(5)) / 2
                print(f"  • φ (Proporção Áurea):   {phi}")
                continue
            else:
                print(alert("Opção inválida!"))
                continue

            session.save_result(expr, res)
            unidade = f" ({modo_txt})" if op in ("5", "6", "7") else ""
            print(f"\n{success(f'{expr} = {fmt(res)}{unidade}')}")

        except (ZeroDivisionError, ValueError, OverflowError) as err:
            print(f"\n{error(str(err))}")
        except (KeyboardInterrupt, EOFError):
            print("\nOperação cancelada.")
            break


def menu_estatistica():
    print(section_banner("5. ESTATÍSTICA DESCRITIVA"))
    print("Digite os valores numéricos separados por espaço ou vírgula.")
    print("Exemplo: 12 15 20 22 15 30 18 ou 1.5, 2.3, 4.0")

    try:
        raw = input(f"\n{Style.BOLD}Conjunto de dados (ou 0 para cancelar): {Style.RESET}").strip()
        if raw == "0" or not raw:
            return

        # Normaliza vírgulas e separa
        tokens = raw.replace(',', ' ').split()
        valores = [float(t) for t in tokens]

        if not valores:
            print(alert("Nenhum valor válido foi inserido."))
            return

        n = len(valores)
        soma = sum(valores)
        media = statistics.mean(valores)
        mediana = statistics.median(valores)
        modas = statistics.multimode(valores)
        v_min = min(valores)
        v_max = max(valores)
        amplitude = v_max - v_min

        print(f"\n{Style.GREEN}{Style.BOLD}=== RESUMO ESTATÍSTICO (N = {n}) ==={Style.RESET}")
        print(f"  • Quantidade de amostras (N): {n}")
        print(f"  • Soma Total:                 {fmt(soma)}")
        print(f"  • Média Aritmética:           {fmt(media)}")
        print(f"  • Mediana:                    {fmt(mediana)}")

        if len(modas) == n:
            print("  • Moda:                       Não há moda (todos valores ocorrem igualmente)")
        else:
            modas_str = ", ".join(fmt(m) for m in modas)
            print(f"  • Moda(s):                    {modas_str}")

        print(f"  • Valor Mínimo:               {fmt(v_min)}")
        print(f"  • Valor Máximo:               {fmt(v_max)}")
        print(f"  • Amplitude (Máx - Mín):      {fmt(amplitude)}")

        if n >= 2:
            var_amostral = statistics.variance(valores)
            dp_amostral = statistics.stdev(valores)
            var_populacional = statistics.pvariance(valores)
            dp_populacional = statistics.pstdev(valores)
            print(f"  • Desvio Padrão Amostral (s): {fmt(dp_amostral)}")
            print(f"  • Variância Amostral (s²):    {fmt(var_amostral)}")
            print(f"  • Desvio Padrão Pop. (σ):     {fmt(dp_populacional)}")
            print(f"  • Variância Populacional (σ²):{fmt(var_populacional)}")
        else:
            print(alert("Para cálculo de desvio padrão e variância são necessários ao menos 2 valores."))

        session.save_result(f"Média(N={n})", media)

    except ValueError:
        print(error("Erro ao interpretar lista de números. Certifique-se de digitar apenas números válidos."))
    except (KeyboardInterrupt, EOFError):
        print("\nOperação cancelada.")


def menu_conversor_bases():
    while True:
        print(section_banner("6. CONVERSOR DE BASES NUMÉRICAS (PROGRAMADOR)"))
        print("  1 - Visão Geral (Converter Decimal para Bin, Oct, Hex)")
        print("  2 - Binário para Decimal")
        print("  3 - Hexadecimal para Decimal")
        print("  4 - Octal para Decimal")
        print("  0 - Voltar ao Menu Principal")

        op = input(f"\n{Style.BOLD}Escolha uma opção: {Style.RESET}").strip()
        if op == "0":
            break

        try:
            if op == "1":
                num = int(parse_number("Digite um número inteiro: "))
                bin_str = bin(num)
                oct_str = oct(num)
                hex_str = hex(num).upper().replace("X", "x")

                # Formata binário em blocos de 4 bits para leitura agradável
                raw_bin = bin(num)[2:] if num >= 0 else bin(num)[3:]
                padded = raw_bin.zfill((len(raw_bin) + 3) // 4 * 4)
                nibbles = " ".join([padded[i:i+4] for i in range(0, len(padded), 4)])
                if num < 0:
                    nibbles = f"-{nibbles}"

                print(f"\n{Style.GREEN}{Style.BOLD}=== CONVERSÃO DE {num} ==={Style.RESET}")
                print(f"  • Decimal:     {num}")
                print(f"  • Hexadecimal: {hex_str}")
                print(f"  • Octal:       {oct_str}")
                print(f"  • Binário:     {bin_str} (ou nibbles: {nibbles})")

            elif op == "2":
                b_str = input("Digite o número em Binário: ").strip()
                res = int(b_str, 2)
                session.save_result(f"bin2dec({b_str})", res)
                print(f"\n{success(f'Binário {b_str} = {res} em Decimal')}")

            elif op == "3":
                h_str = input("Digite o número em Hexadecimal (ex: 1A3F): ").strip()
                res = int(h_str, 16)
                session.save_result(f"hex2dec({h_str})", res)
                print(f"\n{success(f'Hexadecimal {h_str} = {res} em Decimal')}")

            elif op == "4":
                o_str = input("Digite o número em Octal: ").strip()
                res = int(o_str, 8)
                session.save_result(f"oct2dec({o_str})", res)
                print(f"\n{success(f'Octal {o_str} = {res} em Decimal')}")

            else:
                print(alert("Opção inválida!"))

        except ValueError as err:
            print(f"\n{error(f'Formato de número inválido para a base escolhida: {err}')}")
        except (KeyboardInterrupt, EOFError):
            print("\nOperação cancelada.")
            break


def menu_expressao_livre():
    print(section_banner("7. AVALIADOR DE EXPRESSÕES LIVRES"))
    print("Digite qualquer fórmula matemática completa.")
    print(f"Operadores: +, -, *, /, //, %, ^ (ou **)")
    print(f"Funções: sqrt, cbrt, sin, cos, tan, ln, log10, fact, abs, exp")
    print(f"Constantes e memória: pi, e, ans (atual: {fmt(session.ans)}), mem")
    print("Exemplos:")
    print("  • (15 + 5) * 3 - sqrt(64) + 2^4")
    print("  • sin(30) + cos(60)")
    print("  • fact(5) / (2 * pi)")
    print("  • ans * 2 + 10")
    print("Digite '0' ou pressione Enter em branco para voltar.")

    while True:
        try:
            expr = input(f"\n{Style.BOLD}Expressão > {Style.RESET}").strip()
            if expr == "0" or not expr:
                break

            res = safe_eval(expr)
            session.save_result(expr, res)
            print(f"{success(f'= {fmt(res)}')}")

        except (ZeroDivisionError, ValueError, OverflowError) as err:
            print(f"{error(str(err))}")
        except Exception as err:
            print(f"{error(f'Erro na expressão: {err}')}")


def menu_historico_memoria():
    while True:
        print(section_banner("8. HISTÓRICO E MEMÓRIA"))
        print(f"  • Memória Atual (M):  {Style.BOLD}{fmt(session.memory)}{Style.RESET}")
        print(f"  • Último Resultado (ANS): {Style.BOLD}{fmt(session.ans)}{Style.RESET}")
        print("-" * 50)
        print("  1 - Ver Histórico de Operações")
        print("  2 - Limpar Histórico")
        print("  3 - MS (Guardar valor na Memória)")
        print("  4 - M+ (Somar à Memória)")
        print("  5 - M- (Subtrair da Memória)")
        print("  6 - MC (Limpar Memória = 0)")
        print("  0 - Voltar ao Menu Principal")

        op = input(f"\n{Style.BOLD}Escolha uma opção: {Style.RESET}").strip()
        if op == "0":
            break

        if op == "1":
            if not session.history:
                print(alert("O histórico está vazio."))
            else:
                print(f"\n{Style.CYAN}{Style.BOLD}{'HORA':<10} {'CÁLCULO':<35} {'RESULTADO'}{Style.RESET}")
                print("-" * 60)
                for i, item in enumerate(session.history, 1):
                    print(f"{item['time']:<10} {item['operation']:<35} = {fmt(item['result'])}")

        elif op == "2":
            session.clear_history()
            print(f"\n{success('Histórico limpo com sucesso!')}")

        elif op == "3":
            val = parse_number("Valor a armazenar na memória (ou 'ans'): ")
            session.memory = val
            print(f"\n{success(f'Memória definida como: {fmt(session.memory)}')}")

        elif op == "4":
            val = parse_number("Valor a somar na memória: ")
            session.memory += val
            print(f"\n{success(f'Novo valor da Memória: {fmt(session.memory)}')}")

        elif op == "5":
            val = parse_number("Valor a subtrair da memória: ")
            session.memory -= val
            print(f"\n{success(f'Novo valor da Memória: {fmt(session.memory)}')}")

        elif op == "6":
            session.memory = 0.0
            print(f"\n{success('Memória zerada (MC)!')}")

        else:
            print(alert("Opção inválida!"))


# ------------------------------------------------------------------------------
# Menu Principal
# ------------------------------------------------------------------------------
def exibir_menu_principal():
    modo_ang = session.angle_mode.upper()
    print("\n" + title_banner("CALCULADORA CIENTÍFICA & MULTIFUNCIONAL"))
    print(f" {Style.DIM}Status: ANS = {fmt(session.ans)} | MEM = {fmt(session.memory)} | ÂNGULO = {modo_ang}{Style.RESET}")
    print("=" * 60)
    print(" [1] Aritmética Básica e Avançada (+, -, *, /, //, %, 1/x, |x|)")
    print(" [2] Potenciação e Raízes (x^y, x², x³, √, ∛, raiz n-ésima)")
    print(" [3] Porcentagem e Finanças (%, acréscimo, desconto, juros)")
    print(" [4] Funções Científicas e Trigonometria (sin, cos, log, fat)")
    print(" [5] Estatística Descritiva (média, mediana, moda, desvio)")
    print(" [6] Conversor de Bases Numéricas (Dec, Bin, Oct, Hex)")
    print(" [7] Avaliador de Expressão Livre (ex: 2*(5+3) - sqrt(16))")
    print(" [8] Histórico de Cálculos & Memória (ANS, M+, MR, MC)")
    print(" [0] Sair do Programa")
    print("=" * 60)


def main():
    while True:
        try:
            exibir_menu_principal()
            opcao = input(f"{Style.BOLD}Digite a opção desejada (0-8): {Style.RESET}").strip()

            if opcao == "0" or opcao.lower() in ("s", "sair", "exit", "quit", "q"):
                print(f"\n{Style.CYAN}Obrigado por usar a Calculadora Multifuncional! Até breve.{Style.RESET}\n")
                break
            elif opcao == "1":
                menu_aritmetica()
            elif opcao == "2":
                menu_potenciacao_radiciacao()
            elif opcao == "3":
                menu_porcentagem_financas()
            elif opcao == "4":
                menu_cientifica()
            elif opcao == "5":
                menu_estatistica()
            elif opcao == "6":
                menu_conversor_bases()
            elif opcao == "7":
                menu_expressao_livre()
            elif opcao == "8":
                menu_historico_memoria()
            else:
                print(f"\n{alert('Opção inválida! Escolha um número de 0 a 8.')}")

        except KeyboardInterrupt:
            print(f"\n\n{Style.YELLOW}Interrupção detectada. Encerrando calculadora com segurança...{Style.RESET}\n")
            break
        except Exception as e:
            print(f"\n{error(f'Ocorreu um erro inesperado: {e}')}")


if __name__ == "__main__":
    main()
