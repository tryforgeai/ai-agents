#  -------------------------------------------------------------------------------------------------
#   Copyright (c) 2016-2026.  SupportVectors AI Lab
#   This code is part of the AI Lab Book companion repository.
#   It is released under the MIT License - see the LICENSE file at the repository root.
#
#   Copyright (c) 2016-2026 SupportVectors AI Lab.
#
#   Author: SupportVectors AI Training Team
#  -------------------------------------------------------------------------------------------------

"""
PRDA Backend Configuration

CompositeBackend setup: ephemeral agent state for scratch work, a LangGraph
store for everything under /memories/ (which is what makes PRDs survive
across threads and sessions).

Note (deepagents >= 0.7): backends are plain instances now. The old
0.2-era convention — passing a factory that received the runtime, with
StateBackend(runtime) / StoreBackend(runtime) — is gone. StoreBackend takes
a namespace factory instead, which scopes the persistent files (e.g. per
user); here one shared namespace is enough.
"""

from deepagents.backends import CompositeBackend, StateBackend, StoreBackend


def make_backend(store=None):
    """Create the CompositeBackend for the PRDA agent.

    Args:
        store: Optional BaseStore for /memories/. When None, StoreBackend
            resolves the store from the LangGraph execution context (the
            one passed to create_deep_agent(store=...)).

    Returns:
        CompositeBackend routing /memories/ to persistent storage and
        everything else to ephemeral agent state.
    """
    return CompositeBackend(
        default=StateBackend(),
        routes={
            "/memories/": StoreBackend(
                namespace=lambda rt: ("prda", "memories"),
                store=store,
            ),
        },
    )
