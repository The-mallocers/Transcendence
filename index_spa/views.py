# from django.shortcuts import render

# def indexspa(req):
#     return render(req, "index_spa/indexspa.html")

# views.py in your Django app
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET

@require_GET
def indexspa(request):
    # Example of rendering a template partial for SPA
    context = {
        'welcome_message': 'Welcome to our Single Page Application'
    }
    return HttpResponse(
        render_to_string('index_spa/indexspa.html', context)
    )

@require_GET
def partial(request, partial_id):
    NUMBER_OF_IDS = 3
    if (partial_id <= NUMBER_OF_IDS and partial_id > 0):
        return HttpResponse(
            render_to_string('index_spa/partial' + str(partial_id) + '.html')
        )

    
