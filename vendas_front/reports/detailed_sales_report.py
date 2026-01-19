import csv
from datetime import date
from typing import Optional
from django.http import HttpResponse
from django.db import connection

def build_detailed_sales_csv_response(*, start: Optional[date] = None, end: Optional[date] = None) -> HttpResponse:
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    filename = "relatorio_vendas_detalhado.csv"
    if start:
        filename = f"vendas_{start}_{end or 'fim'}.csv"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    # Header
    writer.writerow([
        "Venda ID", "Data", "Cliente", "NIF", 
        "Tipo Item", "Descrição", "Sala/Cinema", 
        "Quantidade", "Preço Unit.", "Total Linha"
    ])

    # Query
    # We use raw SQL for performance and ease of creating a flat report from multiple joins
    # Note: We need to join Vendas -> VendaLinhas -> (Bilhetes -> Sessoes -> Filmes) OR (Produtos)
    
    where_clauses = []
    params = []
    
    if start:
        where_clauses.append("v.data >= %s")
        params.append(start)
    if end:
        where_clauses.append("v.data <= %s")
        params.append(end)
        
    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    sql = f"""
        SELECT 
            v.vendaid,
            v.data,
            c.nomecliente,
            c.nif,
            CASE 
                WHEN vl.bilheteid IS NOT NULL THEN 'Bilhete'
                ELSE 'Produto'
            END as tipo,
            CASE 
                WHEN vl.bilheteid IS NOT NULL THEN f.titulo
                ELSE p.nomeproduto
            END as descricao,
            CASE 
                WHEN vl.bilheteid IS NOT NULL THEN CONCAT(cine.nomecinema, ' - ', s.nomesala)
                ELSE '-'
            END as local,
            vl.quantidade,
            vl.precolinha,
            vl.total_linha_
        FROM vendas v
        JOIN vendalinhas vl ON v.vendaid = vl.vendaid
        LEFT JOIN clientes c ON v.clienteid = c.clienteid
        LEFT JOIN produtos p ON vl.produtoid = p.produtoid
        LEFT JOIN bilhetes b ON vl.bilheteid = b.bilheteid
        LEFT JOIN sessoes sess ON b.sessaoid = sess.sessaoid
        LEFT JOIN filmes f ON sess.filmeid = f.filmeid
        LEFT JOIN salas s ON sess.salaid = s.salaid
        LEFT JOIN cinemas cine ON s.cinemaid = cine.cinemaid
        {where_sql}
        ORDER BY v.data DESC, v.vendaid DESC
    """

    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        for row in rows:
            # Format date
            row_list = list(row)
            if row_list[1]: # data
                row_list[1] = row_list[1].isoformat()
            
            # Handle None values for prices
            row_list[8] = f"{row_list[8]:.2f}" if row_list[8] else "0.00"
            row_list[9] = f"{row_list[9]:.2f}" if row_list[9] else "0.00"
            
            writer.writerow(row_list)

    return response
