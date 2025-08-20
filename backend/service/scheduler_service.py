import os
import atexit
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from service.clothing_service import generar_alerta_y_guardar

# ======== Config por defecto (puede ser sobrescrita por ENV) ========
DEF_ENABLED = os.getenv("SCHED_ENABLED", "true").lower() == "true"
DEF_EVERY_MIN = int(os.getenv("SCHED_EVERY_MIN", "15"))
DEF_PERSONA = os.getenv("SCHED_PERSONA", "Gabriel")
DEF_PROMEDIO = float(os.getenv("SCHED_PROMEDIO", "25"))
DEF_MARGEN = float(os.getenv("SCHED_MARGEN", "3"))
DEF_INCLUIR_TEMP = os.getenv("SCHED_INCLUIR_TEMP", "true").lower() == "true"
DEF_LAT = float(os.getenv("SCHED_LAT", "9.9281"))
DEF_LON = float(os.getenv("SCHED_LON", "-84.0907"))

CONFIG: Dict[str, Any] = {
    "enabled": DEF_ENABLED,
    "every_min": DEF_EVERY_MIN,
    "persona": DEF_PERSONA,
    "promedio": DEF_PROMEDIO,
    "margen": DEF_MARGEN,
    "incluir_temp": DEF_INCLUIR_TEMP,
    "lat": DEF_LAT,
    "lon": DEF_LON,
}

SCHEDULER = BackgroundScheduler(timezone="UTC")
JOB_ID = "job_clothing_alert"


def run_job_once() -> Dict[str, Any]:
    """Ejecuta el job de alerta UNA vez con la config actual."""
    started = datetime.now(timezone.utc).isoformat()
    print(f"\n[SCHED] Ejecutando job a las {started} (UTC) persona={CONFIG['persona']}")
    res = generar_alerta_y_guardar(
        persona=CONFIG["persona"],
        promedio=CONFIG["promedio"],
        margen=CONFIG["margen"],
        incluir_temp=CONFIG["incluir_temp"],
        lat=CONFIG["lat"],
        lon=CONFIG["lon"],
    )
    if res.get("error"):
        print(f"[SCHED][ERROR] {res.get('error')}: {res.get('detalle')}")
    else:
        print(
            f"[SCHED][OK] estado={res.get('estado')} "
            f"id={res.get('id_documento')} categoria={res.get('categoria')} "
            f"url={res.get('url_audio')}"
        )
    return res


def _job_wrapper():
    """Wrapper interno para el scheduler."""
    try:
        run_job_once()
    except Exception as e:
        # No interrumpir el scheduler por excepciones no controladas
        print(f"[SCHED][FATAL] Excepción no controlada en job: {e}")


def init_scheduler(app_debug: bool, **overrides):
    """
    Inicializa/arranca el scheduler en background.
    - app_debug: si Flask corre en debug (para evitar doble arranque por reloader)
    - overrides: parámetros a pisar dinámicamente (opcional)
    """
    CONFIG.update({k: v for k, v in overrides.items() if v is not None})

    if not CONFIG["enabled"]:
        print("[SCHED] Deshabilitado (enabled=false)")
        return

    # Evitar doble arranque con el reloader (solo en proceso hijo real)
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true" and app_debug:
        print("[SCHED] Saltando arranque en proceso padre (reloader activo)")
        return

    trigger = IntervalTrigger(minutes=int(CONFIG["every_min"]))
    SCHEDULER.add_job(
        _job_wrapper,
        trigger=trigger,
        id=JOB_ID,
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=60,
    )
    if not SCHEDULER.running:
        SCHEDULER.start()
        atexit.register(lambda: SCHEDULER.shutdown(wait=False))

    print(f"[SCHED] Iniciado: cada {CONFIG['every_min']} min. Persona={CONFIG['persona']}")


def scheduler_status() -> Dict[str, Any]:
    """Devuelve estado del scheduler y próximos disparos."""
    jobs = []
    for j in SCHEDULER.get_jobs():
        jobs.append({
            "id": j.id,
            "next_run_time": j.next_run_time.isoformat() if j.next_run_time else None,
            "trigger": str(j.trigger),
        })
    return {
        "enabled": CONFIG["enabled"],
        "interval_minutes": CONFIG["every_min"],
        "persona": CONFIG["persona"],
        "jobs": jobs,
        "utc_now": datetime.now(timezone.utc).isoformat(),
    }
