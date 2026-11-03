import json
from dataclasses import dataclass
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import main
from app.classification.labels import SOUNDBOARD_LABELS


FIXTURE_DIRECTORY = Path(__file__).resolve().parents[1] / "fixtures" / "regression"
MANIFEST_PATH = FIXTURE_DIRECTORY / "manifest.json"
MAX_TOP_K = 10


@dataclass(frozen=True)
class RegressionCase:
    id: str
    audio_path: Path
    expected_labels: dict[str, list[str]]
    top_k_per_category: int


def _load_cases() -> list[RegressionCase]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or not isinstance(manifest.get("cases"), list):
        raise ValueError(f"{MANIFEST_PATH} must contain a 'cases' array")

    cases = []
    seen_ids = set()
    for index, raw_case in enumerate(manifest["cases"]):
        location = f"{MANIFEST_PATH}: cases[{index}]"
        if not isinstance(raw_case, dict):
            raise ValueError(f"{location} must be an object")

        case_id = raw_case.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError(f"{location}.id must be a non-empty string")
        if case_id in seen_ids:
            raise ValueError(f"{location}.id duplicates {case_id!r}")
        seen_ids.add(case_id)

        audio = raw_case.get("audio")
        if not isinstance(audio, str) or not audio.strip():
            raise ValueError(f"{location}.audio must be a relative file path")
        audio_path = (FIXTURE_DIRECTORY / audio).resolve()
        if not audio_path.is_relative_to(FIXTURE_DIRECTORY.resolve()):
            raise ValueError(f"{location}.audio must stay inside {FIXTURE_DIRECTORY}")
        if not audio_path.is_file():
            raise ValueError(f"{location}.audio does not exist: {audio_path}")

        top_k = raw_case.get("top_k_per_category", 3)
        if isinstance(top_k, bool) or not isinstance(top_k, int) or not 1 <= top_k <= MAX_TOP_K:
            raise ValueError(f"{location}.top_k_per_category must be between 1 and {MAX_TOP_K}")

        expected_labels = raw_case.get("expected_labels")
        if not isinstance(expected_labels, dict) or not expected_labels:
            raise ValueError(f"{location}.expected_labels must be a non-empty category-to-labels object")
        for category, labels in expected_labels.items():
            if category not in SOUNDBOARD_LABELS:
                raise ValueError(f"{location} references unknown category {category!r}")
            if (
                not isinstance(labels, list)
                or not labels
                or any(not isinstance(label, str) or label not in SOUNDBOARD_LABELS[category] for label in labels)
            ):
                raise ValueError(f"{location} contains invalid labels for category {category!r}")
            if len(set(labels)) != len(labels):
                raise ValueError(f"{location} contains duplicate labels for category {category!r}")
            if len(labels) > top_k:
                raise ValueError(f"{location} expects more labels in {category!r} than top_k_per_category")

        cases.append(RegressionCase(case_id, audio_path, expected_labels, top_k))

    return cases


REGRESSION_CASES = _load_cases()
EMPTY_DATASET_SKIP = pytest.mark.skip(
    reason=f"No regression cases configured; add cases to {MANIFEST_PATH}",
)
PARAMETRIZED_CASES = [
    pytest.param(case, id=case.id)
    for case in REGRESSION_CASES
] or [pytest.param(None, id="empty-dataset", marks=EMPTY_DATASET_SKIP)]


@pytest.fixture(scope="module")
def labeler_client():
    original_overrides = main.app.dependency_overrides.copy()
    main.app.dependency_overrides[main._verify_token] = lambda: None
    try:
        with TestClient(main.app) as client:
            yield client
    finally:
        main.app.dependency_overrides.clear()
        main.app.dependency_overrides.update(original_overrides)


@pytest.mark.integration
@pytest.mark.parametrize("case", PARAMETRIZED_CASES)
def test_curated_audio_keeps_expected_labels(labeler_client, case: RegressionCase | None):
    if case is None:
        pytest.skip("No curated audio samples are configured")

    with case.audio_path.open("rb") as audio_file:
        response = labeler_client.post(
            "/label",
            params={"top_k": case.top_k_per_category},
            files={"file": (case.audio_path.name, audio_file)},
        )

    assert response.status_code == 200, (
        f"Case {case.id!r} could not be classified: {response.status_code} {response.text}"
    )
    categories = response.json().get("categories")
    assert isinstance(categories, dict), f"Case {case.id!r} response has no categories object"

    for category, expected_labels in case.expected_labels.items():
        assert category in categories, (
            f"Case {case.id!r}: expected category {category!r} is absent from the model output"
        )
        actual_labels = {
            prediction["label"]
            for prediction in categories[category].get("labels", [])
        }
        missing_labels = set(expected_labels) - actual_labels
        assert not missing_labels, (
            f"Case {case.id!r}, category {category!r}: labels {sorted(missing_labels)} "
            f"are absent from the top {case.top_k_per_category} predictions"
        )
