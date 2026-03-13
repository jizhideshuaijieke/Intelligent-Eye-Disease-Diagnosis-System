import logging

import requests
from fastapi import APIRouter

from core.config import settings
from models.template import DiseaseDate

router = APIRouter()
logger = logging.getLogger(__name__)

_REQUEST_TIMEOUT_SECONDS = 120
_DIABETIC_RETINOPATHY_KEY = "\u7cd6\u5c3f\u75c5\u6027\u89c6\u7f51\u819c\u75c5\u53d8"


def _post_json(url: str, payload: dict, name: str, index: int) -> dict:
    response = requests.post(url, json=payload, timeout=_REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()

    try:
        return response.json()
    except ValueError as exc:
        raise ValueError(f"invalid JSON from upstream for {name}#{index}") from exc


def _normalize_fundus_probabilities(content: dict) -> list[dict]:
    main_probabilities = dict(content.get("main_classification", {}).get("probabilities", {}))
    sub_probabilities = dict(content.get("sub_classification", {}).get("probabilities", {}))
    merged_probabilities = dict(main_probabilities)

    diabetic_probability = main_probabilities.get(_DIABETIC_RETINOPATHY_KEY)
    if diabetic_probability and diabetic_probability > 0.5 and sub_probabilities:
        merged_probabilities.pop(_DIABETIC_RETINOPATHY_KEY, None)
        total = sum(sub_probabilities.values()) or 1
        merged_probabilities.update(
            {
                key: round((value / total) * diabetic_probability, 3)
                for key, value in sub_probabilities.items()
            }
        )

    sorted_probabilities = sorted(
        merged_probabilities.items(),
        key=lambda item: item[1],
        reverse=True,
    )
    return [
        {"name": name, "probability": probability}
        for name, probability in sorted_probabilities
    ]


def _build_fundus_result(item: DiseaseDate) -> dict:
    content = _post_json(
        f"{settings.AI_MODEL_URL}/api/fundus_analysis",
        {"image": item.path},
        item.name,
        item.index,
    )

    probability_map = content.get("vessel_segmentation", {}).get("probability_map")
    enhanced_image = content.get("enhanced_image")
    if not probability_map or not enhanced_image:
        raise ValueError(f"missing fundus fields for {item.name}#{item.index}")

    return {
        "index": item.index,
        "name": item.name,
        "path": probability_map,
        "probabilities": _normalize_fundus_probabilities(content),
        "enhanced_image": enhanced_image,
    }


def _build_oct_result(item: DiseaseDate) -> dict:
    content = _post_json(
        f"{settings.AI_MODEL_URL}/api/oct_segmentation",
        {"image": item.path},
        item.name,
        item.index,
    )

    segmentation_result = content.get("segmentation_result")
    if not segmentation_result:
        raise ValueError(f"missing oct fields for {item.name}#{item.index}")

    return {
        "index": item.index,
        "name": item.name,
        "path": segmentation_result,
        "probabilities": [],
    }


@router.post("/aibo")
async def predict(request: list[DiseaseDate]) -> dict:
    data = []
    errors = []

    for item in request:
        try:
            if item.name in {"left-oct", "right-oct"}:
                data.append(_build_oct_result(item))
            else:
                data.append(_build_fundus_result(item))
        except requests.RequestException as exc:
            logger.exception("upstream AI request failed for %s#%s", item.name, item.index)
            errors.append(f"{item.name}#{item.index}: {exc}")
        except Exception as exc:
            logger.exception("AI analysis failed for %s#%s", item.name, item.index)
            errors.append(f"{item.name}#{item.index}: {exc}")

    if not data:
        return {
            "code": 0,
            "message": "AI analysis failed. Check the model service on port 5000.",
            "data": [],
            "errors": errors,
        }

    response = {
        "code": 1,
        "message": "success" if not errors else "partial success",
        "data": data,
    }
    if errors:
        response["errors"] = errors
    return response
