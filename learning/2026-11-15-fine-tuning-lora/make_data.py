"""Generate a small toy dataset: merchant note -> category JSON.

The task mimics W8's House Taxonomy: a "house rule" that is easy to learn from
examples but awkward to state in a prompt (e.g. coffee *shops* are dining, but
coffee *beans* from a supermarket are groceries).

Train and eval use DIFFERENT merchants, so the eval set is a real held-out test
(no leakage). Usage:  python make_data.py
"""

import json
import random
from pathlib import Path

random.seed(42)

SYSTEM = (
    "You classify a merchant note into exactly one category. "
    'Reply with JSON only: {"merchant": "...", "category": "..."}. '
    "Categories: groceries, dining, transport, utilities, entertainment, health."
)

# category -> list of (merchant, typical item) ; the house rules live in here
MERCHANTS = {
    "groceries": [
        ("Safeway", "milk and eggs"), ("Trader Joe's", "coffee beans"), ("Whole Foods", "vegetables"),
        ("99 Ranch", "rice and tofu"), ("Costco", "paper towels"), ("Mitsuwa", "miso and natto"),
        ("Sprouts", "fruit"), ("Lucky", "bread"), ("Aldi", "snacks"), ("Nijiya Market", "bento ingredients"),
    ],
    "dining": [
        ("Starbucks", "latte"), ("Blue Bottle", "pour-over coffee"), ("Chipotle", "burrito bowl"),
        ("Din Tai Fung", "xiaolongbao"), ("In-N-Out", "double-double"), ("Philz", "mint mojito coffee"),
        ("Ramen Nagi", "ramen"), ("Sweetgreen", "salad"), ("Panera", "soup"), ("Boba Guys", "milk tea"),
    ],
    "transport": [
        ("Uber", "ride to airport"), ("Lyft", "ride home"), ("Caltrain", "monthly pass"),
        ("Shell", "gas"), ("Chevron", "gas"), ("BART", "clipper reload"), ("ParkMobile", "parking"),
        ("FasTrak", "bridge toll"), ("Tesla Supercharger", "charging"), ("Amtrak", "train ticket"),
    ],
    "utilities": [
        ("PG&E", "electricity bill"), ("Comcast", "internet"), ("AT&T", "phone bill"),
        ("Verizon", "phone bill"), ("SJ Water", "water bill"), ("Recology", "garbage service"),
        ("Sonic", "fiber internet"), ("T-Mobile", "phone bill"), ("Silicon Valley Power", "electricity"),
        ("Republic Services", "trash pickup"),
    ],
    "entertainment": [
        ("Netflix", "subscription"), ("AMC", "movie tickets"), ("Spotify", "premium"),
        ("Steam", "video game"), ("Ticketmaster", "concert"), ("Disney+", "subscription"),
        ("Audible", "audiobook"), ("Cinemark", "movie"), ("Nintendo eShop", "game"), ("YouTube", "premium"),
    ],
    "health": [
        ("CVS", "prescription"), ("Walgreens", "cold medicine"), ("Kaiser", "copay"),
        ("One Medical", "visit"), ("24 Hour Fitness", "gym membership"), ("Dental Care", "cleaning"),
        ("LensCrafters", "glasses"), ("Rite Aid", "vitamins"), ("Planet Fitness", "membership"),
        ("Sutter Health", "lab test"),
    ],
}

TEMPLATES = [
    "{m} - {item} ${amt}",
    "paid {m} ${amt} for {item}",
    "{item} @ {m}, {amt} USD",
    "card charge: {m} {amt}",
    "{m}: {item}",
]


def example(merchant: str, item: str, category: str) -> dict:
    note = random.choice(TEMPLATES).format(m=merchant, item=item, amt=f"{random.uniform(3, 180):.2f}")
    answer = json.dumps({"merchant": merchant, "category": category})
    # TRL "conversational prompt-completion" format -> loss is computed on the completion only
    return {
        "prompt": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": note}],
        "completion": [{"role": "assistant", "content": answer}],
    }


def main() -> None:
    out = Path(__file__).parent / "data"
    out.mkdir(exist_ok=True)
    train, test = [], []
    for category, merchants in MERCHANTS.items():
        random.shuffle(merchants)
        held_out, seen = merchants[:2], merchants[2:]  # 2 merchants per category never seen in training
        for m, item in seen:
            train += [example(m, item, category) for _ in range(6)]
        for m, item in held_out:
            test += [example(m, item, category) for _ in range(5)]
    random.shuffle(train)
    random.shuffle(test)
    for name, rows in [("train", train), ("eval", test)]:
        with open(out / f"{name}.jsonl", "w") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"{name}: {len(rows)} rows -> {out / (name + '.jsonl')}")


if __name__ == "__main__":
    main()
