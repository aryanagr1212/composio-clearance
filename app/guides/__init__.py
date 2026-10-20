"""Reviewed example guides. These render with no API keys."""

from app.guides.gmail import build as build_gmail
from app.guides.hubspot import build as build_hubspot
from app.guides.notion import build as build_notion
from app.guides.slack import build as build_slack
from app.schema import Guide


def load_curated() -> list[Guide]:
    return [build_gmail(), build_slack(), build_notion(), build_hubspot()]
