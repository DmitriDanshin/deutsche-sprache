from pathlib import Path

import pdfkit
from pdf.layout import template


def pdf_create(data):
    pdfkit.from_string(
        template.render(
            title=data['Word'].capitalize(),
            part_of_speech=data['PartOfSpeech'].lower(),
            russian_translations=", ".join(data['RussianTranslations']).capitalize(),
            english_translations=", ".join(data['EnglishTranslations']).capitalize(),
            synonyms=", ".join(data['Synonyms']),
            examples=data['Examples'],
            forms=data['Forms']
        ),
        str(Path(__file__).parent / "output/output.pdf")
    )
