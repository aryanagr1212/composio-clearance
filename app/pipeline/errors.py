"""Failures a developer should see in the UI, without a traceback."""


class GuideError(Exception):
    """A failure with a message that is safe to show on the page."""


class MissingCredentialsError(GuideError):
    """Live generation was asked for, and a required key is not configured."""


class ResearchError(GuideError):
    """Search or page fetch could not gather enough official material."""


class ExtractionError(GuideError):
    """The model did not return a guide we could validate."""
