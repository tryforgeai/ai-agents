# Progressive exercises

Each exercise builds on the previous one. Try the change in `adk web` or Streamlit and
confirm the behaviour in the Phoenix trace / session state.

## Level 1 — Read the graph

1. Open `src/newsletter/agent.py` and list every node of `NewsletterFlow` in execution order.
   Compare your list with the Phoenix trace of one run.
2. In `adk web`, run one newsletter request and open the **State** tab. For each key in the
   README's state table, find the agent that wrote it.

## Level 2 — Change behaviour with prompts and schemas

3. Add a `sentiment: Literal["positive", "neutral", "negative"]` field to `ValidatedArticle`
   in `schemas.py`. Update the validator prompt, then make the editorial agent mention the
   overall tone.
4. Give the analyst a `key_numbers: list[str]` field (figures quoted in the sources) and show
   them in the final newsletter.
5. Try three new phrasings that might confuse the intent classifier (e.g. questions *about*
   newsletters vs requests *for* one). If any mis-route, fix `INTENT_CLASSIFIER_INSTRUCTION`.

## Level 3 — New graph patterns

6. **New source.** Add a fifth collector (e.g. Hacker News search via a Python tool). Add it
   to the parallel tuple in `newsletter_collector`, give it an `output_key`, and feed it to
   the validator prompt.
7. **Second human gate.** Add a `RequestInput` step *before* the analyst that lets the human
   remove URLs from `validated_reports`. Tip: copy the ask/route pair from
   `human_review/agent.py`, and use a different `interrupt_id` prefix.
8. **Quality gate.** Add a `FunctionNode` after the validator that routes to a `"no_sources"`
   branch (a polite chat-style reply) when `validated_articles` is empty.

## Level 4 — Harden

9. Ask a question that mentions "news" but should stay on chat (e.g. "Which news APIs does
   this app use?"). Confirm it does not enter `NewsletterFlow`.
10. Run the full pipeline, approve the review, and check that `final_markdown_output` has a
    References section.
11. Swap `MODEL` / provider in `.env`. Does `output_schema` still work for the validator and
    analyst?
