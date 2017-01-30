# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from apis.models import CustomUser
from apis.serializers import *
import json

def check_params(arr, keys):
    for key in keys:
        if not key in arr:
            return JSONResponse({'error': 'invalid parameters'}, status=status.HTTP_400_BAD_REQUEST)
    return None


def check_method_and_params(params, method, keys):
    if method == 'GET':
        return check_params(params.keys(), keys)
    if params is not None:
        return check_params(params.keys(), keys)
    return JSONResponse({'error': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)
        
def get_json_in_params(request):
    try:
        if request.body:
            return json.loads(request.body.replace("'", '"'))
    except:
        return None
    return None

def get_fields(model):
    field_names = [u'nick', u'age', u'first_name', u'last_name', u'email']
    return field_names

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)
        
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def user_list(request):
    """
    List all code users, or create a new snippet.
    """
    if not request.user.is_superuser:
        return JSONResponse({'error': 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)
    if request.method == 'GET':
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return JSONResponse(serializer.data)

    elif request.method == 'POST':
        params = get_json_in_params(request)
        res = check_method_and_params(params, 'POST', get_fields(CustomUser))
        if res is not None:
            return res
        serializer = UserSerializer(data=params)
        nickCount = CustomUser.objects.filter(nick=params['nick']).count()
        emailCount = CustomUser.objects.filter(email=params['email']).count()
        if nickCount > 0:
            return JSONResponse({'error': 'exist nick'}, status=status.HTTP_400_BAD_REQUEST)
        elif emailCount > 0:
            return JSONResponse({'error': 'exist email'}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse({'error': 'none'}, status=status.HTTP_201_CREATED)
        return JSONResponse({'error': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'DELETE', 'PUT', 'PATCH'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def user_detail(request, pk):
    """
    Retrieve, update or delete a snippet instance.
    """
    user = None
    try:
        user = CustomUser.objects.get(pk=pk)
    except CustomUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        if not request.user.is_superuser and request.user.id != int(pk):
            return JSONResponse({'error': 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    params = get_json_in_params(request)
    if request.method == 'PUT':
        res = check_method_and_params(params, 'PUT', get_fields(CustomUser))
        if res is not None:
            return res        
        if not request.user.is_superuser and request.user.id != int(pk):
            return JSONResponse({'error': 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'PATCH':
        if not request.user.is_superuser and request.user.id != int(pk):
            return JSONResponse({'error': 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not request.user.is_superuser:
            return JSONResponse({'error': 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
