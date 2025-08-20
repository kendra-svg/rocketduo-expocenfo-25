from flask import Blueprint, jsonify, request
from service.scheduler_service import (
    init_scheduler,
    run_job_once,
    scheduler_status,
    CONFIG,
)

scheduler_bp = Blueprint("scheduler_api", __name__, url_prefix="/api/scheduler")


@scheduler_bp.get("/status")
def api_scheduler_status():
    return jsonify(scheduler_status()), 200


@scheduler_bp.post("/run-now")
def api_scheduler_run_now():
    res = run_job_once()
    status = 201 if res.get("id_documento") else (502 if res.get("error") else 200)
    return jsonify(res), status
