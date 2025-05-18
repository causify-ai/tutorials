
# Bitcoin_API.md

This tutorial demonstrates the use of Hugging Face Transformers APIs for Named Entity Recognition (NER) and Zero-Shot Text Classification, applied to Bitcoin-related news content.

## 🔍 Named Entity Recognition (NER)

We use the pre-trained `dslim/bert-base-NER` model to extract named entities from the text. The pipeline returns tokens and their associated entity groups such as ORG, LOC, PERSON, etc.

```python
from transformers import pipeline
ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")
ner_pipeline("Bitcoin price surged after SEC approved the ETF proposal for Blackrock.")
```

## 🏷️ Zero-Shot Text Classification

We use `facebook/bart-large-mnli` to classify articles into predefined event types without needing to train a model.

```python
classifier_pipeline = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
labels = ["Regulatory", "Technological", "Market Manipulation", "Adoption News"]
classifier_pipeline("Blackrock's ETF was approved by the SEC.", labels)
```

## 💡 Notes

- No fine-tuning is needed.
- Both pipelines are pre-trained and accessible via Hugging Face Transformers.
- Text inputs are truncated to 512 tokens for performance and safety.
