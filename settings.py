# Verbformen

VERBFORMEN_URL = "https://www.verbformen.ru/"
VERBFORMEN_WORD_CLASSES = (
    "vGrnd rCntr"
)
VERBFORMEN_WORD_VERB_CLASSES = (
    "vGrnd rCntr rClear"
)
VERBFORMEN_TRANSLATIONS_CLASSES = (
    "r1Zeile rU3px rO0px"
)
VERBFORMEN_NAV_CLASS = (
    "rKrml rKln rInf"
)
AMOUNT_OF_GRAMMATICAL_CASES = 4
NOUNS_WRAPPER_CLASS = (
    "vDkl"
)
NOUNS_TABLE_CLASS = (
    "vTbl"
)

VERBS_TABLE_CLASS = (
    "rAufZu"
)
VERBS_CELL_CLASS = (
    "rAufZu"
)

STRONG_DECLENSION_INDEX = 1
WEAK_DECLENSION_INDEX = 2
MIXED_DECLENSION_INDEX = 3

DECLENSION_TABLE_CLASS = (
    "vTbl"
)

# Context reverso

CONTEXT_REVERSO_URL = "https://context.reverso.net/перевод/немецкий-русский/{}"

# Synonyms reverso

SYNONYMS_REVERSO_URL = "https://synonyms.reverso.net/синонимы/de/Hund?filter=2"

# Logger
LOGGER_FORMAT = (
    '[%(asctime)s: %(name)s | %(levelname)s] %(message)s'
)

LOGGER_PATH = "logs/"

# Other

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/104.0.0.0 Safari/537.36"
)

# Mongo DB

CONNECTION_STRING = "mongodb://localhost:27017/"
