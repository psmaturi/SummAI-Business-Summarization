# summarizer.py — Hybrid Extractive + Abstractive Summarizer
# Uses TextRank for extractive mode and T5-small for abstractive mode
# Supports length: short / medium / long

import re
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from transformers import T5ForConditionalGeneration, T5Tokenizer

print("🔥 Loaded HYBRID summarizer (extractive + abstractive)")

# =========================
#  Load T5 model once
# =========================
tokenizer = T5Tokenizer.from_pretrained("t5-small")
model = T5ForConditionalGeneration.from_pretrained("t5-small")


# =========================
#  Helpers for extractive
# =========================
def sentence_tokenize(text: str):
    """Split text into sentences."""
    text = text.replace("—", ". ").replace("–", ". ")
    text = re.sub(r"\s*\n\s*", " ", text)
    sentences = re.split(r'(?<=[.!?;])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def word_tokenize(text: str):
    text = re.sub(r"[^a-zA-Z0-9]", " ", text)
    return text.lower().split()


def sentence_vectors(sentences):
    """Convert each sentence to a simple bag-of-words vector."""
    vocab = set()
    for sent in sentences:
        vocab.update(word_tokenize(sent))

    vocab = list(vocab)
    if not vocab:
        return np.zeros((len(sentences), 1))

    vectors = []
    for sent in sentences:
        words = word_tokenize(sent)
        vec = np.zeros(len(vocab))
        for w in words:
            if w in vocab:
                vec[vocab.index(w)] += 1
        vectors.append(vec)

    return np.array(vectors)


def textrank_summary(text: str, length: str = "medium") -> str:
    """Extractive summary using TextRank with variable length."""
    sentences = sentence_tokenize(text)
    n = len(sentences)

    if n < 2:
        return text.strip()

    # Decide how many sentences to keep
    if length == "short":
        ratio = 0.2
    elif length == "long":
        ratio = 0.5
    else:  # medium
        ratio = 0.3

    keep = max(1, int(n * ratio))
    keep = min(keep, max(1, n - 1))  # don't keep all sentences

    vectors = sentence_vectors(sentences)
    sim_matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            if i != j:
                sim_matrix[i][j] = cosine_similarity(
                    vectors[i].reshape(1, -1),
                    vectors[j].reshape(1, -1)
                )

    # Simple PageRank
    scores = np.ones(n)
    for _ in range(20):
        scores = 0.85 * sim_matrix.dot(scores) + 0.15

    top_indices = scores.argsort()[-keep:]
    top_indices.sort()

    summary_sentences = [sentences[i] for i in top_indices]
    return " ".join(summary_sentences).strip()


# =========================
#  Abstractive (T5)
# =========================
def abstractive_summary(text: str, length: str = "medium") -> str:
    text = text.strip()
    if not text:
        return "No text provided."

    word_count = len(text.split())

    if length == "short":
        max_len, min_len = 40, 8
        prompt = "summarize in one short sentence: "
    elif length == "long":
        max_len, min_len = 150, 50
        prompt = "summarize in a detailed paragraph: "
    else:  # medium
        max_len, min_len = 80, 20
        prompt = "summarize in 1-2 concise sentences: "

    # If input is very small, still make it shorter
    if word_count < 60 and length == "medium":
        max_len, min_len = 40, 8
        prompt = "summarize concisely: "

    model_input = prompt + text

    inputs = tokenizer.encode(
        model_input,
        return_tensors="pt",
        max_length=512,
        truncation=True
    )

    summary_ids = model.generate(
        inputs,
        max_length=max_len,
        min_length=min_len,
        num_beams=4,
        length_penalty=2.0,
        early_stopping=True,
        no_repeat_ngram_size=3,
    )

    return tokenizer.decode(summary_ids[0], skip_special_tokens=True).strip()


# =========================
#  Main entry
# =========================
def summarize_text(text: str, mode: str = "extractive", length: str = "medium") -> str:
    """
    mode: "extractive" or "abstractive"
    length: "short", "medium", "long"
    """
    if not text or not text.strip():
        return "No text provided."

    if mode == "abstractive":
        return abstractive_summary(text, length)
    else:
        return textrank_summary(text, length)
