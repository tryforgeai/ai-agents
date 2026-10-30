"""Phoenix integration: official OpenInference or ADK-native coexistence."""
import os
from urllib.parse import urlsplit

_provider = None
_configuration = None


def enable_phoenix(project_name, *, enabled=True, mode="openinference",
                   endpoint=None, batch=True):
    """Configure once per process and return a provider for force_flush().

    openinference: official phoenix.register(auto_instrument=True).
    native: export existing ADK spans via standard OTEL, retaining Web processors.
    Credentials are read by Phoenix exporters from PHOENIX_* environment variables.
    """
    global _provider, _configuration
    if not enabled:
        return None
    if mode not in {"openinference", "native"}:
        raise ValueError("mode must be openinference or native")
    if not project_name.strip():
        raise ValueError("project_name must not be empty")
    endpoint = endpoint or os.getenv("PHOENIX_COLLECTOR_ENDPOINT")
    if not endpoint:
        raise ValueError("set PHOENIX_COLLECTOR_ENDPOINT or pass endpoint explicitly")
    parsed = urlsplit(endpoint)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("endpoint must be an HTTP(S) URL")
    config = (project_name, mode, endpoint, batch)
    if _provider is not None:
        if config != _configuration:
            raise RuntimeError("tracing already configured differently; restart the process")
        return _provider

    if mode == "openinference":
        from phoenix.otel import register
        provider = register(project_name=project_name, endpoint=endpoint,
                            protocol="http/protobuf", batch=batch,
                            auto_instrument=True, verbose=False)
    else:
        import inspect
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
        from phoenix.otel import HTTPSpanExporter
        # A full traces endpoint makes the transport explicit in native mode.
        if not parsed.path.rstrip("/").endswith("/v1/traces"):
            raise ValueError("native mode requires the full HTTP endpoint ending /v1/traces")
        provider = trace.get_tracer_provider()
        if not isinstance(provider, TracerProvider):
            provider = TracerProvider(resource=Resource.create({"openinference.project.name": project_name}))
            trace.set_tracer_provider(provider)
        else:
            existing = provider.resource.attributes.get("openinference.project.name")
            if existing != project_name:
                raise RuntimeError("existing tracer provider has a different/missing project name; configure tracing before starting ADK Web")
        exporter = HTTPSpanExporter(endpoint=endpoint)
        processor_type = BatchSpanProcessor if batch else SimpleSpanProcessor
        processor = processor_type(exporter)
        # Phoenix providers default to replacing their default processor;
        # standard SDK providers append. Preserve other exporters in either case.
        options = {}
        if "replace_default_processor" in inspect.signature(provider.add_span_processor).parameters:
            options["replace_default_processor"] = False
        provider.add_span_processor(processor, **options)
    _provider, _configuration = provider, config
    return provider
