from typing import Literal
import dspy
from rich import print as rprint


# 1. Define the task and allowed outputs.
class MatchTransactionToStore(dspy.Signature):
    """
    Match a credit card transaction description to a store in our catalog.

    Example store catalog:
    - store_nordstrom: Nordstrom. Known name: NORDSTROM.
    - store_nordstrom_rack: Nordstrom Rack.
      Known names: NORDSTROM RACK, NORDSTROMRACK.
    - store_target: Target. Known name: TARGET.

    Rules:
    - Ignore capitalization, branch numbers, and channel labels like ONLINE.
    - Nordstrom and Nordstrom Rack are separate catalog entities.
    - A payment processor prefix alone does not identify the store.
    - Base your decision only on evidence in the transaction description.
    - Return unknown if the merchant is outside this catalog or the
      description provides insufficient evidence.
    """

    transaction_description: str = dspy.InputField(
        desc="The raw merchant description from a credit card transaction."
    )

    store_id: Literal[
        "store_nordstrom",
        "store_nordstrom_rack",
        "store_target",
        "unknown",
    ] = dspy.OutputField()

    evidence: str = dspy.OutputField(
        desc="Briefly explain the evidence supporting your decision in English."
    )


# 2. Use the language model already configured with dspy.configure().
matcher = dspy.Predict(MatchTransactionToStore)


# 3. Synthetic examples with expected labels.
test_cases = [
    ("NORDSTROM #0831", "store_nordstrom"),
    ("NORDSTROM ONLINE", "store_nordstrom"),
    ("NORDSTROMRACK.COM", "store_nordstrom_rack"),
    ("TARGET T-1234", "store_target"),
    ("PAYPAL *XYZSHOP", "unknown"),
]


# 4. Run predictions and check correctness.
correct = 0

for description, expected in test_cases:
    prediction = matcher(transaction_description=description)

    is_correct = prediction.store_id == expected
    correct += int(is_correct)

    rprint({
        "transaction": description,
        "predicted_store": prediction.store_id,
        "expected_store": expected,
        "correct": is_correct,
        "evidence": prediction.evidence,
    })
    print("-" * 60)

print(f"Accuracy on synthetic examples: {correct}/{len(test_cases)}")



prediction = matcher(
    transaction_description="NORDSTROM RACK #0218"
)

print("Matched store:", prediction.store_id)
print("Evidence:", prediction.evidence)

# Inspect the actual prompt and model response.
dspy.inspect_history(n=1)