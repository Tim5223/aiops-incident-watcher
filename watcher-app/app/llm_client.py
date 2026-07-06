import os

# Set this as an environment variable once you have your key from
# https://aistudio.google.com -> Get API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

_model = None


def _get_model():
    """Lazily initializes the Gemini client, only once, only if a key is set."""
    global _model
    if _model is None:
        import google.generativeai as genai

        genai.configure(api_key=GEMINI_API_KEY)
        _model = genai.GenerativeModel("gemini-2.5-flash")
    return _model


def get_diagnosis(alert_name: str, alert_details: str) -> str:
    """
    Given an alert's name and details, returns a diagnosis string.

    Uses Google's Gemini API (free tier) if GEMINI_API_KEY is set.
    Falls back to a mocked, keyword-based response if no key is configured,
    so the rest of the pipeline can still be built/tested without one.
    """
    if not GEMINI_API_KEY:
        return _mock_diagnosis(alert_name, alert_details)

    try:
        model = _get_model()
        prompt = (
            f"An infrastructure alert fired.\n"
            f"Alert name: {alert_name}\n"
            f"Details: {alert_details}\n\n"
            f"In 2-3 sentences, give the most likely cause and a suggested fix. "
            f"Be concise and specific."
        )
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        # If the API call fails for any reason (rate limit, network, bad key),
        # fall back to the mock rather than crashing the whole request.
        return f"[LLM call failed, using fallback] {_mock_diagnosis(alert_name, alert_details)} (error: {e})"


def _mock_diagnosis(alert_name: str, alert_details: str) -> str:
    """Fake diagnosis logic, used when no API key is configured."""
    alert_lower = alert_name.lower()

    if "crash" in alert_lower or "restart" in alert_lower:
        return (
            "MOCK DIAGNOSIS: Likely a pod crash-loop, possibly caused by a "
            "misconfiguration or an unhandled startup error. Suggested action: "
            "restart the pod and check its logs for the root exception."
        )
    elif "cpu" in alert_lower or "memory" in alert_lower:
        return (
            "MOCK DIAGNOSIS: Resource usage appears abnormally high. Suggested "
            "action: check for a runaway process or consider scaling up replicas."
        )
    else:
        return (
            f"MOCK DIAGNOSIS: Unrecognized alert type '{alert_name}'. "
            "Manual investigation recommended."
        )
