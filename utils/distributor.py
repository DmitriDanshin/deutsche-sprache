from typing import Any


class Distributor:
    @classmethod
    def distribute(
            cls,
            verbformen_data,
            context_reverso_data,
            context_synonyms_data,
    ) -> dict[str, Any]:
        data = {
            "Word": verbformen_data["Word"],
            "PartOfSpeech": verbformen_data["PartOfSpeech"],
            "Forms": verbformen_data["Forms"],
            "EnglishTranslations": verbformen_data["English"],
            "RussianTranslations": context_reverso_data["Translations"],
            "Examples": context_reverso_data["Examples"],
            "Synonyms": context_synonyms_data["Synonyms"],
        }

        return data
