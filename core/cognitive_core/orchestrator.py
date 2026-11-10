"""Cognitive orchestration: integrates identity, memory, emotion, personality, reasoning."""
from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from biological_systems.brain import service as brain_service
from biological_systems.brain.reasoning.adapters import ReasoningAdapter, get_default_adapter
from biological_systems.emotional_system import service as emo_service
from core.identity_core import service as identity_service
from mind.memories import service as memory_service
from mind.personality import service as pers_service
from security.auditing.audit import record_audit


async def run_cognitive_step(
    session: AsyncSession,
    identity_id: str,
    input_text: str,
    adapter: ReasoningAdapter | None = None,
    actor: str = "system",
) -> dict[str, Any]:
    adapter = adapter or get_default_adapter()

    identity = await identity_service.get_identity(session, identity_id)
    if identity is None:
        raise ValueError("identity not found")

    # retrieve relevant memories (recent episodic + semantic)
    memories = await memory_service.retrieve_memories(session, identity_id, limit=10)
    mem_snippets = [{"type": m.memory_type, "origin": m.origin_class, "content": m.content} for m in memories]

    wm = await brain_service.get_working_memory(session, identity_id)
    self_model = await brain_service.get_or_create_self_model(session, identity_id)
    emo_state = await emo_service.get_or_create_state(session, identity_id)
    pers = await pers_service.get_or_create_profile(session, identity_id)

    context = {
        "identity_id": identity_id,
        "identity_version": identity.version,
        "self_model": self_model.data,
        "emotion": emo_state.dimensions,
        "personality": {
            "stable": pers.stable_traits or {},
            "adaptable": pers.adaptable_tendencies or {},
        },
        "working_memory": wm,
        "memories": mem_snippets,
    }

    result = await adapter.generate(input_text, context=context)

    # record reflection (generated content is NOT promoted to memory automatically)
    reflection = await brain_service.record_reflection(
        session, identity_id, kind="cognitive_step",
        content={"input": input_text, "output": result.text, "provider": result.provider,
                 "confidence": result.confidence},
        actor=actor,
    )

    # update working memory with the step (temporary, not authoritative memory)
    await brain_service.push_working_memory(session, identity_id, {
        "input": input_text, "output": result.text, "provider": result.provider,
    }, actor=actor)

    await record_audit(session, actor=actor, action="cognition.step", target_type="identity",
                      target_id=identity_id, details={"provider": result.provider, "confidence": result.confidence})

    return {
        "identity_id": identity_id,
        "identity_version": identity.version,
        "output": result.text,
        "confidence": result.confidence,
        "provider": result.provider,
        "reflection_id": reflection.reflection_id,
        "memories_used": len(mem_snippets),
    }
