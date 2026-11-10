SYSTEM_PROMPT = """You are a concise financial assistant. Rules you must follow:

1. Answer in plain, readable sentences — never list raw transaction IDs or hash values.
2. Use merchant names, categories, dates and amounts to explain the answer.
3. Round amounts to 2 decimal places. Use ₹ symbol.
4. If asked for a summary or analysis, give totals by category and a brief insight.
5. Never invent transactions, amounts or dates not present in the context.
6. If the data is insufficient, say so clearly in one sentence.
7. Keep the response concise — 3 to 6 sentences maximum unless a breakdown is explicitly asked.
"""


def build_grounded_prompt(question: str, transactions: list[dict]) -> str:
    """
    Build the prompt sent to the LLM.
    Transactions are formatted as human-readable lines — no raw IDs exposed.
    """
    lines = []
    for i, tx in enumerate(transactions, start=1):
        merchant = tx.get("normalized_merchant") or tx.get("receiver") or "Unknown"
        date     = tx.get("date", "")
        amount   = tx.get("amount", 0)
        tx_type  = tx.get("transaction_type", "")
        category = tx.get("category", "")
        desc     = tx.get("description", "")

        lines.append(
            f"{i}. {merchant} | {date} | ₹{amount} | {tx_type} | {category}"
            + (f" | {desc}" if desc and desc.lower() != merchant.lower() else "")
        )

    context_block = "\n".join(lines) if lines else "No relevant transactions found."

    return (
        f"{SYSTEM_PROMPT}\n"
        f"Question: {question}\n\n"
        f"Transaction data ({len(transactions)} records):\n"
        f"{context_block}\n\n"
        "Answer the question using only the data above. Do not mention transaction IDs."
    )
