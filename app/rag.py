# rag.py
import os
import glob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import google.generativelanguage as genai
from typing import List
from .config import REFERENCE_FOLDER, TOP_K, GEMINI_MODEL

class RAGClient:
    def __init__(self, reference_folder=REFERENCE_FOLDER, top_k=TOP_K):
        self.reference_folder = reference_folder
        self.top_k = top_k
        self.docs = []
        self._load_references()
        self._build_vectorizer()
        api_key = os.environ.get("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)

    def _load_references(self):
        self.docs = []
        patterns = ["*.txt", "*.md"]
        for pat in patterns:
            for path in glob.glob(f"{self.reference_folder}/**/{pat}", recursive=True):
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                        txt = fh.read()
                        self.docs.append({"path": path, "text": txt})
                except Exception:
                    continue
        if not self.docs:
            self.docs = [{"path":"dummy","text":"ADGM Companies Regulations 2020: sample placeholder text."}]

    def _build_vectorizer(self):
        corpus = [d["text"] for d in self.docs]
        self.vectorizer = TfidfVectorizer(stop_words="english", max_features=20000)
        self.X = self.vectorizer.fit_transform(corpus)

    def retrieve(self, query, top_k=None):
        if top_k is None:
            top_k = self.top_k
        q_vec = self.vectorizer.transform([query])
        cosine_similarities = linear_kernel(q_vec, self.X).flatten()
        top_indices = cosine_similarities.argsort()[-top_k:][::-1]
        results = [self.docs[i] for i in top_indices]
        return results

    def query_with_context(self, question, local_context=None):
        retrieved = self.retrieve(question, top_k=self.top_k)
        combined_context = ""
        for r in retrieved:
            combined_context += f"\n--- Source: {r['path']} ---\n{r['text'][:2500]}\n"

        if local_context:
            combined_context = f"User Document Excerpt:\n{local_context[:2000]}\n\n" + combined_context

        # Build prompt
        system_prompt = (
            "You are an assistant specialized in ADGM corporate law. "
            "Use the provided ADGM references to cite applicable regulations and give a short recommendation."
        )
        user_prompt = f"{system_prompt}\n\nCONTEXT:\n{combined_context}\n\nQUESTION:\n{question}\n\nAnswer concisely; if you cite law include article numbers if available."

        try:
            response = genai.generate_text(model=GEMINI_MODEL, prompt=user_prompt, temperature=0.0, max_output_tokens=512)
            return response.text
        except Exception as e:
            return f"RAG LLM call failed: {e}. Retrieved contexts: {[r['path'] for r in retrieved]}"
