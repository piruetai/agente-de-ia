import pandas as pd
import json
from dados import perfil, transacoes, historico, produtos

#Tratamentos
def brl(valor: float) -> str:
    """Formata número no padrão monetário brasileiro (R$ 1.234,56)."""
    return "R$ " + f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(valor: float) -> str:
    """Formata percentual com vírgula decimal (66,7%)."""
    return f"{valor:.1%}".replace(".", ",")


def meses_ate(prazo: str, data_ref: pd.Timestamp) -> int:
    """Meses entre a data de referência e o prazo no formato 'AAAA-MM'."""
    ano, mes = map(int, prazo.split("-"))
    return (ano - data_ref.year) * 12 + (mes - data_ref.month)


def linha_meta(meta: dict, perfil: dict, data_ref: pd.Timestamp) -> str:
    """Descreve uma meta. Só calcula progresso quando o valor atual está nos dados."""
    necessario = meta["valor_necessario"]
    meses = meses_ate(meta["prazo"], data_ref)
    texto = f"- {meta['meta']}: valor necessário {brl(necessario)} | prazo {meta['prazo']} ({meses} meses)"

    atual = perfil["reserva_emergencia_atual"] if "reserva" in meta["meta"].lower() else meta.get("valor_atual")
    if atual is None:
        return texto + " | valor acumulado NÃO informado nos dados"

    falta = max(necessario - atual, 0)
    aporte = f" | aporte mensal necessário ≈ {brl(falta / meses)}" if meses > 0 else ""
    return texto + f" | acumulado {brl(atual)} ({pct(atual / necessario)}) | faltam {brl(falta)}{aporte}"


#Contexto
def montar_contexto(perfil: dict, transacoes: pd.DataFrame, historico: pd.DataFrame, produtos: list) -> str:
    """Monta o contexto (base de conhecimento) enviado à Mia junto com o system prompt.
    Os totais e prazos são pré-calculados aqui para que o LLM não precise fazer contas."""
    data_ref = pd.to_datetime(transacoes["data"]).max()

    saidas = transacoes[transacoes["tipo"] == "saida"]
    entradas_total = transacoes.loc[transacoes["tipo"] == "entrada", "valor"].sum()
    saidas_total = saidas["valor"].sum()
    por_categoria = saidas.groupby("categoria")["valor"].sum().sort_values(ascending=False)
    gastos_categoria = "\n".join(
        f"- {cat}: {brl(val)} ({pct(val / saidas_total)} dos gastos)" for cat, val in por_categoria.items()
    )
    metas = "\n".join(linha_meta(m, perfil, data_ref) for m in perfil["metas"])

    return f"""
DATA DE REFERÊNCIA: {data_ref:%Y-%m-%d}

CLIENTE: {perfil['nome']}, {perfil['idade']} anos, {perfil['profissao']}
PERFIL: {perfil['perfil_investidor']} | ACEITA RISCO: {'sim' if perfil['aceita_risco'] else 'não'}
RENDA MENSAL: {brl(perfil['renda_mensal'])}
OBJETIVO PRINCIPAL: {perfil['objetivo_principal']}
PATRIMÔNIO: {brl(perfil['patrimonio_total'])} | RESERVA DE EMERGÊNCIA: {brl(perfil['reserva_emergencia_atual'])}

METAS:
{metas}

RESUMO DO PERÍODO DAS TRANSAÇÕES:
- Entradas: {brl(entradas_total)}
- Saídas: {brl(saidas_total)}
- Saldo: {brl(entradas_total - saidas_total)}

GASTOS POR CATEGORIA:
{gastos_categoria}

TRANSAÇÕES RECENTES:
{transacoes.to_string(index=False)}

ATENDIMENTOS ANTERIORES:
{historico.to_string(index=False)}

PRODUTOS DISPONÍVEIS:
{json.dumps(produtos, indent=2, ensure_ascii=False)}
"""

contexto = montar_contexto(perfil, transacoes, historico, produtos)