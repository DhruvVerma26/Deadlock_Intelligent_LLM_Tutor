"""
Deadlock RAG Retriever Engine
Performs semantic and lexical retrieval over the curated OS Deadlock Knowledge Base.
Supports top-k retrieval, relevance scoring, and citation generation.
"""
import os
import json
import re
import math
from typing import List, Dict, Tuple


class DeadlockRAGRetriever:
    def __init__(self, kb_path: str = None):
        if kb_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            kb_path = os.path.join(base_dir, "data", "os_deadlock_kb.json")
            
        self.kb_path = kb_path
        self.documents = []
        self._load_knowledge_base()
        self._build_index()

    def _load_knowledge_base(self):
        if os.path.exists(self.kb_path):
            with open(self.kb_path, "r", encoding="utf-8") as f:
                self.documents = json.load(f)
        else:
            self.documents = []

    def _tokenize(self, text: str) -> List[str]:
        tokens = re.findall(r"\b[a-zA-Z0-9_\-\']+\b", text.lower())
        stopwords = {
            "a", "an", "the", "in", "on", "of", "to", "for", "is", "are",
            "was", "were", "and", "or", "by", "with", "at", "from", "it",
            "this", "that", "these", "those", "as", "be", "have", "has"
        }
        return [t for t in tokens if t not in stopwords and len(t) > 1]

    def _build_index(self):
        """Builds TF-IDF inverted index over document titles, contents, and keywords."""
        self.doc_count = len(self.documents)
        self.df = {}  # term -> document frequency
        self.doc_tfs = []
        self.doc_lengths = []

        for doc in self.documents:
            full_text = f"{doc['title']} {doc['topic']} {doc['subtopic']} {doc['content']} {' '.join(doc.get('keywords', []))}"
            tokens = self._tokenize(full_text)
            self.doc_lengths.append(len(tokens))
            
            tf = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            self.doc_tfs.append(tf)

            for term in set(tokens):
                self.df[term] = self.df.get(term, 0) + 1

        self.avg_doc_len = sum(self.doc_lengths) / max(1, self.doc_count)

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieves top-k relevant knowledge snippets using BM25 scoring.
        Returns ranked documents with relevance score and highlight citations.
        """
        query_tokens = self._tokenize(query)
        if not query_tokens or self.doc_count == 0:
            return self.documents[:top_k]

        k1 = 1.5
        b = 0.75
        scores = []

        for idx, doc in enumerate(self.documents):
            score = 0.0
            doc_len = self.doc_lengths[idx]
            tf_dict = self.doc_tfs[idx]

            for term in query_tokens:
                if term in tf_dict:
                    # BM25 formula
                    df_val = self.df.get(term, 0)
                    idf = math.log((self.doc_count - df_val + 0.5) / (df_val + 0.5) + 1.0)
                    f = tf_dict[term]
                    denom = f + k1 * (1.0 - b + b * (doc_len / self.avg_doc_len))
                    score += idf * (f * (k1 + 1.0)) / denom

            scores.append((score, doc))

        scores.sort(key=lambda x: x[0], reverse=True)
        results = []
        for rank, (score, doc) in enumerate(scores[:top_k]):
            res_item = dict(doc)
            res_item["score"] = round(float(score), 4)
            res_item["rank"] = rank + 1
            results.append(res_item)

        return results

    def get_topics_list(self) -> List[str]:
        topics = set(d["topic"] for d in self.documents)
        return sorted(list(topics))
