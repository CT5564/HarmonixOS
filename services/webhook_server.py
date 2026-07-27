# Webhook Server
#
# Receives Notion webhook events and routes
# them to the sync service.
#
# Runs as a background aiohttp server alongside
# the Discord bot.

import hmac
import hashlib
import json

import aiohttp
from aiohttp import web

from config import NOTION_WEBHOOK_SECRET
from services import sync_service
from services.log import get_log
import services.database as db

log = get_log(__name__)


# ============================================================
# SIGNATURE VERIFICATION
# ============================================================

def verify_signature(
    body: bytes,
    signature_header: str
) -> bool:
    """Verify the X-Notion-Signature header
    using HMAC-SHA256."""

    if not NOTION_WEBHOOK_SECRET:
        return True

    if not signature_header:
        return False

    expected = (
        "sha256="
        + hmac.new(
            NOTION_WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
    )

    return hmac.compare_digest(
        expected,
        signature_header
    )


# ============================================================
# WEBHOOK HANDLER
# ============================================================

async def handle_webhook(request):

    body = await request.read()

    # ========================================================
    # SIGNATURE CHECK
    # ========================================================

    signature = request.headers.get(
        "X-Notion-Signature",
        ""
    )

    if not verify_signature(body, signature):

        log.error("Invalid signature. Rejecting.")

        return web.json_response(
            {"error": "invalid signature"},
            status=401
        )

    # ========================================================
    # PARSE PAYLOAD
    # ========================================================

    try:

        payload = json.loads(body)

    except Exception:

        return web.json_response(
            {"error": "invalid json"},
            status=400
        )

    # ========================================================
    # HANDSHAKE — first POST from Notion
    # ========================================================

    if "verification_token" in payload:

        token = payload["verification_token"]

        log.info(f"Received handshake. Token: {token}")
        log.info(
            "Paste this token in Notion integration "
            "settings to verify."
        )

        return web.json_response(
            {"ok": True}
        )

    # ========================================================
    # EVENT ROUTING
    # ========================================================

    event_type = payload.get("type", "")
    entity = payload.get("entity", {})
    page_id = entity.get("id", "")
    entity_type = entity.get("type", "")

    log.info(f"Event: {event_type} → {entity_type} {page_id}")

    # Only handle page events in our tasks DB
    if entity_type != "page":
        return web.json_response({"ok": True})

    if event_type in (
        "page.created",
        "page.properties_updated",
        "page.content_updated",
    ):

        await sync_service.upsert_from_notion(
            page_id
        )

    elif event_type == "page.deleted":

        db.soft_delete_task_by_notion_id(
            page_id
        )

        log.info(f"Soft-deleted local task for page {page_id}")

    elif event_type == "page.undeleted":

        db.restore_task_by_notion_id(
            page_id
        )

        await sync_service.upsert_from_notion(
            page_id
        )

        log.info(f"Restored local task for page {page_id}")

    return web.json_response({"ok": True})


# ============================================================
# HEALTH CHECK
# ============================================================

async def handle_health(request):

    return web.json_response(
        {"status": "ok", "service": "harmonix"}
    )


# ============================================================
# SERVER SETUP
# ============================================================

def create_app():

    app = web.Application()

    app.router.add_post(
        "/webhook/notion",
        handle_webhook
    )

    app.router.add_get(
        "/webhook/health",
        handle_health
    )

    return app


async def start_server(port: int = 8080):
    """Start the webhook server. Called from
    main.py on bot ready."""

    app = create_app()

    runner = web.AppRunner(app)

    await runner.setup()

    site = web.TCPSite(
        runner, "0.0.0.0", port
    )

    await site.start()

    log.info(f"Server running on port {port}")

    return runner
