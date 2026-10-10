"""Tests for adding visits and compiling them into candidates."""

from collections.abc import Callable
from datetime import UTC, datetime

import pytest

from caremerge_addon.errors import RecordNotFoundError
from caremerge_addon.pipeline.compiler import compile_source
from caremerge_addon.pipeline.context import PipelineContext
from caremerge_addon.pipeline.intake import add_visit
from caremerge_addon.settings import AddonSettings
from caremerge_addon.visits.fixture_inbox import FixtureVisitInbox
from caremerge_addon.visits.models import Visit
from caremerge_core.contracts import CompileInput, CompileOutput, Utterance
from caremerge_core.enums import EntityMatch, ReviewState, Role, SourceKind

VisitAdder = Callable[[int], list[str]]


def test_adding_a_visit_stores_a_minimized_source_once(ctx: PipelineContext) -> None:
    first = add_visit("visit-1", ctx)
    again = add_visit("visit-1", ctx)
    assert first.is_new and not again.is_new
    assert again.source == first.source
    source = first.source
    assert (source.kind, source.external_id) == (SourceKind.VISIT, "visit-1")
    assert (source.label, source.role) == ("Dr. Rivera", Role.FAMILY_PHYSICIAN)
    assert source.captured_at == datetime(2026, 10, 5, 14, 10, tzinfo=UTC)
    assert source.content_hash.startswith("sha256:")
    assert "title" not in source.model_dump()


def test_unknown_visits_raise_not_found(ctx: PipelineContext) -> None:
    with pytest.raises(RecordNotFoundError):
        add_visit("visit-9", ctx)


def test_compiled_candidates_wait_for_review(ctx: PipelineContext, add_visit_n: VisitAdder) -> None:
    created = add_visit_n(1)
    commits = {c.commit_id: c for c in ctx.repo.snapshot().commits}
    assert len(created) == 3
    assert {commits[i].review.state for i in created} == {ReviewState.CANDIDATE}
    assert {commits[i].source.role for i in created} == {Role.FAMILY_PHYSICIAN}


def test_later_visits_link_to_known_entities(ctx: PipelineContext, add_visit_n: VisitAdder) -> None:
    add_visit_n(1)
    hold_ids = add_visit_n(2)
    snapshot = ctx.repo.snapshot()
    names = snapshot.entity_names()
    hold = next(c for c in snapshot.commits if c.commit_id == hold_ids[1])
    assert names[hold.entity_id] == "Medication A"
    assert hold.signals.entity is EntityMatch.MATCHED
    assert hold.edges.branch == "procedure-2026-10-28"
    assert sorted(names.values()) == [
        "Medication A",
        "blood pressure",
        "follow-up visit",
        "procedure",
    ]


class _BadQuoteExtractor:
    """An extractor whose second candidate misquotes the source."""

    def compile(self, request: CompileInput) -> CompileOutput:
        good = request.source.utterances[0]
        return CompileOutput.model_validate(
            {
                "candidates": [
                    {
                        "kind": "procedure",
                        "subject_text": "procedure",
                        "entity": {"match": "new"},
                        "attributes": {"scheduled_for": "2026-10-28"},
                        "modality": "information",
                        "evidence": [{"utterance_id": good.id, "quote": good.text}],
                        "self_rating": "high",
                    },
                    {
                        "kind": "medication_instruction",
                        "subject_text": "Medication A",
                        "entity": {"match": "new"},
                        "attributes": {"action": "stop"},
                        "modality": "instruction",
                        "evidence": [{"utterance_id": good.id, "quote": "stop Medication A today"}],
                        "self_rating": "high",
                    },
                ]
            }
        )


def test_misquoted_candidates_are_rejected_not_stored(
    ctx: PipelineContext, settings: AddonSettings, inbox: FixtureVisitInbox
) -> None:
    bad_ctx = PipelineContext(settings, ctx.repo, inbox, _BadQuoteExtractor(), ctx.clock, ctx.ids)
    added = add_visit("visit-2", bad_ctx)
    report = compile_source(added.source, bad_ctx)
    assert (len(report.created), report.rejected) == (1, 1)
    assert [c.subject_text for c in ctx.repo.snapshot().commits] == ["procedure"]


def test_repeated_utterances_are_stored_once(ctx: PipelineContext, settings: AddonSettings) -> None:
    line = Utterance(id="r-u1", start_ms=0, text="Keep taking Medication A.")
    repeated = Visit(
        visit_id="repeat-1",
        title="Repeated segment",
        clinician="Dr. Rivera",
        role=Role.FAMILY_PHYSICIAN,
        started_at=datetime(2026, 10, 12, 15, 0, tzinfo=UTC),
        utterances=(line, Utterance(id="r-u2", start_ms=900, text="Yes."), line),
    )
    inbox = FixtureVisitInbox([repeated])
    repeat_ctx = PipelineContext(settings, ctx.repo, inbox, ctx.extraction, ctx.clock, ctx.ids)
    added = add_visit("repeat-1", repeat_ctx)
    assert [u.id for u in added.source.utterances] == ["r-u1", "r-u2"]
