import os

# RAG settings
REFERENCE_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "references")
TOP_K = int(os.environ.get("RAG_TOP_K", 3))

# Gemini model name (change if necessary)
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "models/text-bison-1")

# ADGM metadata
ADGM_NAME = "Abu Dhabi Global Market"
