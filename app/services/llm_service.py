"""
LLM service layer using google/flan-t5-small for document question answering
"""

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Instruction-tuned for QA
# - Deterministic generation

model_name = "google/flan-t5-small"

# Load once 
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)


def answer_question(context, question):
    """
    Generate a natural language answer to a question using the document context.
    Args:
        context: Extracted text from the document.
        question: User's natural language question.

    Returns:
        Model-generated answer string.
    """
    prompt = f"""Answer the question based on the document below.

Document:
{context}

Question:
{question}

Answer:"""

    # Tokenize with truncation to fit model limits
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=512,  # Safe input limit
        )

    # Generate deterministically
    outputs = model.generate(
        **inputs,
        max_new_tokens=128,
        do_sample=False,  # Greedy decoding for consistency
    )

    # Decode and clean
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return answer.strip()