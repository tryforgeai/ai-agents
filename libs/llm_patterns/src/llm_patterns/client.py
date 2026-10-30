"""Week 01/02: raw text and schema-validated calls use separate clients."""
import os


class CompletionClient:
    def __init__(self, model, *, base_url=None, api_key=None, mode="json",
                 timeout=60, max_retries=2, raw_client=None):
        if not model or not model.strip():
            raise ValueError("model is required")
        if mode not in {"json", "tools"}:
            raise ValueError("mode must be json or tools")
        if timeout <= 0 or max_retries < 0:
            raise ValueError("timeout must be positive; max_retries must be nonnegative")
        self.model, self.mode, self.max_retries = model, mode, max_retries
        self._owned = raw_client is None
        if raw_client is None:
            from openai import OpenAI
            options = {"timeout": timeout, "max_retries": max_retries}
            if base_url:
                options["base_url"] = base_url
            if api_key:
                options["api_key"] = api_key
            raw_client = OpenAI(**options)
        self.raw = raw_client
        self._structured = None

    @classmethod
    def from_env(cls):
        return cls(os.environ["LLM_MODEL"], base_url=os.getenv("OPENAI_BASE_URL"),
                   api_key=os.getenv("OPENAI_API_KEY"),
                   mode=os.getenv("INSTRUCTOR_MODE", "json"))

    def complete(self, prompt=None, *, messages=None, response_model=None, **options):
        if (prompt is None) == (messages is None):
            raise ValueError("provide exactly one of prompt or messages")
        if {"model", "max_retries"} & options.keys():
            raise ValueError("configure model/max_retries on the client")
        messages = messages if messages is not None else [{"role": "user", "content": prompt}]
        if response_model is not None:
            if self._structured is None:
                import instructor
                # instructor may patch the underlying client's create method;
                # retain the original callable for raw requests before wrapping.
                self._raw_create = self.raw.chat.completions.create
                self._structured = instructor.from_openai(
                    self.raw, mode=instructor.Mode.JSON if self.mode == "json" else instructor.Mode.TOOLS)
            return self._structured.chat.completions.create(
                model=self.model, messages=messages, response_model=response_model,
                max_retries=self.max_retries, **options)
        create = getattr(self, "_raw_create", self.raw.chat.completions.create)
        response = create(model=self.model, messages=messages, **options)
        if not response.choices or response.choices[0].message.content is None:
            raise ValueError("model returned no text (possibly a tool call or refusal)")
        return response.choices[0].message.content

    def close(self):
        if self._owned:
            self.raw.close()
