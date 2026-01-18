from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from bd2ap1.models import Filmes


@dataclass(frozen=True)
class ImportResult:
    processed: int
    matched: int
    updated: int
    skipped_existing: int
    not_found: int
    missing_required: list[str] = field(default_factory=list)
    ambiguous_titles: list[str] = field(default_factory=list)
    titles_not_found: list[str] = field(default_factory=list)


class FilmeImportService:
    """Regras de negócio de importação relacionadas a Filmes.

    """

    def import_sinopses_from_csv(
        self,
        csv_path: str | Path,
        *,
        overwrite: bool = False,
        encoding: str = 'utf-8',
        max_report_items: int = 8,
    ) -> ImportResult:
        """Importa sinopses de um CSV e grava em bd2ap1.models.Filmes.sinopse.

        CSV esperado (header):
          - titulo (OBRIGATÓRIO)
          - sinopse (OBRIGATÓRIO)

        Matching:
          - por titulo

        Observação importante: se existir mais do que 1 filme com o mesmo título,
        esta rotina NÃO atualiza (para evitar pôr sinopse no filme errado).
        """
        path = Path(csv_path)

        processed = matched = updated = skipped_existing = not_found = 0
        missing_required: list[str] = []
        ambiguous_titles: list[str] = []
        titles_not_found: list[str] = []

        def _add_limited(lst: list[str], value: str):
            value = (value or '').strip()
            if not value:
                value = '(linha sem título)'
            if value in lst:
                return
            if len(lst) < max_report_items:
                lst.append(value)

        with path.open('r', encoding=encoding, newline='') as f:
            reader = csv.DictReader(f)

            fieldnames = [h.strip() for h in (reader.fieldnames or []) if h]
            required = {'titulo', 'sinopse'}
            if not reader.fieldnames:
                raise ValueError('CSV inválido: ficheiro vazio ou sem cabeçalho.')
            if not required.issubset(set(fieldnames)):
                raise ValueError('CSV inválido: cabeçalho deve ter as colunas: titulo, sinopse')

            for row in reader:
                processed += 1

                titulo = (row.get('titulo') or '').strip()
                synopsis = (row.get('sinopse') or '').strip()

                if not titulo or not synopsis:
                    not_found += 1
                    _add_limited(missing_required, titulo)
                    continue

                filme: Optional[Filmes] = None

                qs = Filmes.objects.filter(titulo__iexact=titulo)
                count = qs.count()
                if count == 1:
                    filme = qs.first()
                elif count > 1:
                    not_found += 1
                    _add_limited(ambiguous_titles, titulo)
                    continue
                else:
                    not_found += 1
                    _add_limited(titles_not_found, titulo)
                    continue

                matched += 1

                current = (filme.sinopse or '').strip()
                if current and not overwrite:
                    skipped_existing += 1
                    continue

                filme.sinopse = synopsis
                filme.save(update_fields=['sinopse'])
                updated += 1

        return ImportResult(
            processed=processed,
            matched=matched,
            updated=updated,
            skipped_existing=skipped_existing,
            not_found=not_found,
            missing_required=missing_required,
            ambiguous_titles=ambiguous_titles,
            titles_not_found=titles_not_found,
        )
