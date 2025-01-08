from error.view.error_404 import error_404_view


# Create your views here.
def error_404(request, exception):
    return error_404_view(request)