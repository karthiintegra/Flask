# pdfmodules/__init__.py

from pdfmodules.transformer_v1 import (
    PdfTagTransformerPhase1,
    Reference,
    Table,
    footprint,
    Table_delete,
    PdfAltTextSetter,
    # Figure_inlineequation,
    # formula_inside_figure_delete,
    # removing_figureTag_inside_P_tag_and_Formula,
)

__all__ = [
    'PdfTagTransformerPhase1',
    'Reference',
    'Table',
    'footprint',
    'Table_delete',
    'PdfAltTextSetter',
    # 'Figure_inlineequation',
    # 'formula_inside_figure_delete',
    # 'removing_figureTag_inside_P_tag_and_Formula',
]