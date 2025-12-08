# pdfmodules/__init__.py

from pdfmodules.transformer import (
    PdfTagTransformerPhase1,
    Reference,
    Table,
    footprint,
    Table_delete,
    PdfAltTextSetter,
    Figure_inlineequation,
    formula_inside_figure_delete
)

__all__ = [
    'PdfTagTransformerPhase1',
    'Reference',
    'Table',
    'footprint',
    'Table_delete',
    'PdfAltTextSetter',
    'Figure_inlineequation',
    'formula_inside_figure_delete'
]