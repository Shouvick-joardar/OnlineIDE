from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, JsonResponse
from .models import Submissions
from rest_framework.viewsets import ModelViewSet
from .serializers import SubmissionSerializer, UserSerializer
from rest_framework import permissions
from .utils import create_code_file, execute_file
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.response import Response
from knox.views import LoginView as KnoxLoginVIew
from django.contrib.auth import login
from django.contrib.auth.models import User


# Create your views here.

class LoginView(KnoxLoginVIew):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginView, self).post(request, format=None)


class SubmissionsViewSet(ModelViewSet):
    queryset = Submissions.objects.all()
    serializer_class = SubmissionSerializer

    def create(self, request, *args, **kwargs):
        request.data['status'] = 'P'
        file_name = create_code_file(request.data.get('code'), request.data.get('language'))
        output = execute_file(file_name, request.data.get('language'))
        request.data['output'] = output
        return super().create(request, args, kwargs)


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.all()

    def list(self, request, *args, **kwargs):
        return Response(UserSerializer(request.user).data, status=200)
