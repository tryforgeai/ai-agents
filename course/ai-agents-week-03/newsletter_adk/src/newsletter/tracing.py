#  -------------------------------------------------------------------------------------------------
#   Copyright (c) 2016-2025.  SupportVectors AI Lab
#   This code is part of the training material and, therefore, part of the intellectual property.
#   It may not be reused or shared without the explicit, written permission of SupportVectors.
#
#   Use is limited to the duration and purpose of the training at SupportVectors.
#
#   Author: SupportVectors AI Training Team
#  -------------------------------------------------------------------------------------------------

"""
Phoenix / OpenTelemetry setup.

Coexistence rules (ADK Web Trace tab + Phoenix UI):
- Do NOT use ``auto_instrument=True`` — OpenInference disables ADK's native
  tracers, which blanks the ADK Web Trace tab.
- Keep Phoenix's default span processor when ADK later attaches its
  InMemoryExporter (``replace_default_processor=False``).
"""

from __future__ import annotations

_TRACING_STARTED = False


def setup_tracing() -> None:
    """Export ADK-native spans to Phoenix without blanking the ADK Web Trace tab."""
    global _TRACING_STARTED
    if _TRACING_STARTED:
        return

    from newsletter.settings import ENABLE_TRACING, PHOENIX_PROJECT_NAME

    if not ENABLE_TRACING:
        return

    import os

    from phoenix.otel import register

    # Prefer explicit env; default to Phoenix local collector (gRPC :4317).
    # HTTP alternative: http://127.0.0.1:6006/v1/traces + PHOENIX_PROTOCOL=http/protobuf
    endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://127.0.0.1:4317")
    protocol = os.getenv("PHOENIX_PROTOCOL", "grpc")  # or http/protobuf

    tracer_provider = register(
        project_name=PHOENIX_PROJECT_NAME,
        endpoint=endpoint,
        protocol=protocol,  # type: ignore[arg-type]
        # Critical: OpenInference auto_instrument disables ADK tracers → blank Trace tab.
        auto_instrument=False,
        batch=False,  # SimpleSpanProcessor — visible immediately in local Phoenix
        set_global_tracer_provider=True,
    )

    # ADK Web calls provider.add_span_processor(InMemoryExporter...). Phoenix's
    # TracerProvider removes its default OTLP processor unless we keep it.
    _original_add = tracer_provider.add_span_processor

    def _add_span_processor(*args, **kwargs):
        kwargs.setdefault("replace_default_processor", False)
        return _original_add(*args, **kwargs)

    tracer_provider.add_span_processor = _add_span_processor  # type: ignore[method-assign]
    _TRACING_STARTED = True
