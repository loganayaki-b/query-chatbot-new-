# bot/views.py
import json, logging
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from .agents import agent_response


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@require_GET
def health(request):
    return JsonResponse({"status": "ok"})

@csrf_exempt
@require_POST
def create_message(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    if "text" not in data:
        return HttpResponseBadRequest("Missing field: text")

    user_text = data["text"]

    try:
        response = agent_response(user_text)
        return JsonResponse(response)
    except Exception as e:
        logger.error(f"[Views] Error: {str(e)}")
        return JsonResponse({"reply": f"Server Error: {str(e)}", "category": "ERROR"}, status=500)
