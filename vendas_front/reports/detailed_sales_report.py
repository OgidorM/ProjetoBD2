import csv
from datetime import date
from typing import Optional
from django.http import HttpResponse
from django.db import connections

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

    # Query using Stored Function
    with connections['admin'].cursor() as cursor:
        cursor.execute("SELECT * FROM fn_relatorio_vendas_csv(%s, %s)", [start, end])
        rows = cursor.fetchall()
        
        for row in rows:
            # Format date
            row_list = list(row)
            if row_list[1]:
                row_list[1] = row_list[1].isoformat()
            
            # Handle None values for prices
            row_list[8] = f"{row_list[8]:.2f}" if row_list[8] else "0.00"
            row_list[9] = f"{row_list[9]:.2f}" if row_list[9] else "0.00"
            
            writer.writerow(row_list)

    return response

    return response
