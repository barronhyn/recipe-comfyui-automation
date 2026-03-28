"""RunPod serverless entry point."""
import logging

import runpod

from .pipeline import run_from_api_input

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def handler(job: dict) -> dict:
    """RunPod calls this with job = {"id": ..., "input": {...}}."""
    job_input = job.get("input", {})
    log.info("RunPod job received: %s", job.get("id"))
    try:
        result = run_from_api_input(job_input)
        return result
    except Exception as exc:
        log.exception("Pipeline error: %s", exc)
        return {"error": str(exc)}


if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
