from django.conf import settings

def get_history(request):
    history = request.session.get("history", None)
    if not history:
        history = []
    return history

def update_history(request, code):
    if code in settings.EU_COUNTRY_KEYS:
        history = [code]
    else:
        history = get_history(request)
        if code in history:
            while history.pop() != code:
                pass
        history.append(code)
    request.session["history"] = history

