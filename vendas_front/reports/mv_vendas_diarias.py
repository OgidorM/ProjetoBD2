from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from typing import Iterable, Optional

from django.db import connection
from django.http import HttpResponse


@dataclass(frozen=True)
class VendasDiariasRow:
    data: date
    total_transacoes: int
    total_faturado: float


def fetch_mv_vendas_diarias(*, start: Optional[date] = None, end: Optional[date] = None) -> list[VendasDiariasRow]:
    """
    - start/end: intervalo inclusivo.
    - Retorna lista ordenada por data.

    """

    where_parts: list[str] = []
    params: list[date] = []

    if start is not None:
        where_parts.append("data >= %s")
        params.append(start)
    if end is not None:
        where_parts.append("data <= %s")
        params.append(end)

    where_sql = (" WHERE " + " AND ".join(where_parts)) if where_parts else ""

    sql = (
        "SELECT data, total_transacoes, total_faturado "
        "FROM mv_vendas_diarias"
        f"{where_sql} "
        "ORDER BY data"
    )

    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        rows = cursor.fetchall()

    result: list[VendasDiariasRow] = []
    for data_value, total_transacoes, total_faturado in rows:
        result.append(
            VendasDiariasRow(
                data=data_value,
                total_transacoes=int(total_transacoes),
                total_faturado=float(total_faturado) if total_faturado is not None else 0.0,
            )
        )

    return result


def build_mv_vendas_diarias_csv_response(
    *,
    rows: Iterable[VendasDiariasRow],
    filename: str = "mv_vendas_diarias.csv",
) -> HttpResponse:

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(["data", "total_transacoes", "total_faturado"])

    for r in rows:
        writer.writerow([r.data.isoformat(), r.total_transacoes, f"{r.total_faturado:.2f}"])

    return response
