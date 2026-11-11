"""Contract tests for future Python -> React offline synthetic impact messages."""

import json

import pytest

from openflight.camera.offline_impact_evidence import OfflineImpactEvidence
from openflight.camera.offline_impact_transport import serialize_offline_impact_evidence


def test_accepted_synthetic_evidence_serializes_with_capture_identity():
    evidence = OfflineImpactEvidence(
        "shot-42", "session-7", 2, True, 12., 5., "toe", "high",
        "synthetic geometry only",
    )
    payload = json.loads(json.dumps(serialize_offline_impact_evidence(evidence)))
    assert payload == {
        "schema_version": 1, "source": "offline_synthetic_analysis",
        "shot_id": "shot-42", "session_id": "session-7",
        "accepted": True, "reason": "synthetic geometry only",
        "physically_validated": False, "position_uncertainty_mm": None,
        "frame_index": 2, "x_mm": 12., "y_mm": 5.,
        "horizontal_region": "toe", "vertical_region": "high",
    }


def test_rejected_evidence_never_exposes_coordinates():
    evidence = OfflineImpactEvidence(
        "shot-42", "session-7", None, False, None, None, None, None,
        "ambiguous synthetic frame",
    )
    payload = serialize_offline_impact_evidence(evidence)
    assert payload["accepted"] is False
    for key in ("frame_index", "x_mm", "y_mm", "horizontal_region", "vertical_region"):
        assert key not in payload


@pytest.mark.parametrize("coordinate", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_accepted_coordinates_are_rejected(coordinate):
    evidence = OfflineImpactEvidence(
        "shot-42", "session-7", 2, True, coordinate, 5., "toe", "high",
        "synthetic geometry only",
    )
    with pytest.raises(ValueError, match="coordinates or regions invalid"):
        serialize_offline_impact_evidence(evidence)


def test_wrong_evidence_type_is_rejected():
    with pytest.raises(ValueError, match="typed impact evidence"):
        serialize_offline_impact_evidence(None)


def test_completed_handoff_publishes_only_to_explicit_recipient():
    from openflight.camera.offline_impact_handoff import OfflineImpactHandoff
    from openflight.camera.offline_impact_transport import publish_offline_impact_handoff

    # Temporal evidence is not used for serialization; it must be part of the
    # completed typed handoff, not a forged client dictionary.
    evidence = OfflineImpactEvidence(
        "shot-42", "session-7", 2, True, 12., 5., "toe", "high",
        "synthetic geometry only",
    )
    messages = []
    handoff = OfflineImpactHandoff(temporal=None, impact=evidence)
    payload = publish_offline_impact_handoff(
        handoff, lambda event, body, **kwargs: messages.append((event, body, kwargs)),
        recipient="client-1",
    )
    assert messages == [("offline_impact_evidence", payload, {"to": "client-1"})]


def test_publication_rejects_untyped_or_unaddressed_evidence():
    from openflight.camera.offline_impact_transport import publish_offline_impact_handoff

    with pytest.raises(ValueError, match="completed typed handoff"):
        publish_offline_impact_handoff({}, lambda *_args, **_kwargs: None, recipient="client")


@pytest.mark.parametrize("shot_id,session_id", [
    ("", "session"), ("shot", " "), (None, "session"),
    ("shot", None), ("x" * 257, "session"), ("shot", "x" * 257),
])
def test_offline_transport_rejects_invalid_capture_identity(shot_id, session_id):
    evidence = OfflineImpactEvidence(
        shot_id, session_id, 2, True, 12., 5., "toe", "high",
        "synthetic geometry only",
    )
    with pytest.raises(ValueError, match="shot/session identity"):
        serialize_offline_impact_evidence(evidence)


@pytest.mark.parametrize("reason", ["", " ", None, "x" * 2049])
def test_offline_transport_rejects_invalid_reason(reason):
    evidence = OfflineImpactEvidence(
        "shot", "session", None, False, None, None, None, None, reason,
    )
    with pytest.raises(ValueError, match="nonempty reason"):
        serialize_offline_impact_evidence(evidence)


def test_offline_transport_refuses_noncallable_emitter_without_sending():
    from openflight.camera.offline_impact_handoff import OfflineImpactHandoff
    from openflight.camera.offline_impact_transport import publish_offline_impact_handoff

    evidence = OfflineImpactEvidence(
        "shot", "session", None, False, None, None, None, None, "rejected",
    )
    with pytest.raises(ValueError, match="callable emitter"):
        publish_offline_impact_handoff(
            OfflineImpactHandoff(temporal=None, impact=evidence),
            None, recipient="client-1",
        )
