from django.http import HttpResponse, JsonResponse

def index(req):
    user_data = req.token_payload
    return JsonResponse({'message': f'Bonjour {user_data["sub"]}'})
    # return index_view(req)
