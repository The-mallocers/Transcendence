from django.http import HttpResponse
from django.shortcuts import render
from index.view.index_view import index_view
from utils.decorators.activity_checker import activity_checker
from utils.decorators.jwt_required import jwt_required

@jwt_required
@activity_checker
def index(req):
    return index_view(req)