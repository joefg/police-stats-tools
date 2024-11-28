"""
Templates for enforcing a house style on generated
plots.
"""

import plotly.graph_objects as go # type: ignore


def watermark(watermark_text: str):
    """
    Returns a Plotly layout template which adds a watermark
    to the plot.
    """
    watermarked_template = go.layout.Template()
    watermarked_template.layout.annotations = [
        {
            'name': watermark_text,
            'text': watermark_text,
            'textangle': -30,
            'opacity': 0.5,
            'font': {'color': "black", 'size': 100},
            'xref': "paper",
            'yref': "paper",
            'x': 0.5,
            'y': 0.5,
            'showarrow': False
        }
    ]
    return watermarked_template
