from django.views.generic.base import TemplateView
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import UserInfoSerializer


@permission_classes((IsAuthenticated,))
class UserInfoView(APIView):

    serializer_class = UserInfoSerializer

    def get(self, request):
        return Response(
            self.serializer_class(request.user).data,
            status=status.HTTP_200_OK
        )
      
    def put(self, request):
        serializer = self.serializer_class(request.user, data=request.data)
        serializer.is_valid()
        serializer.save()
        return Response(
            self.serializer_class(request.user).data,
            status=status.HTTP_200_OK
        )


class SampleTemplateView(TemplateView):

    template_name = "sample.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context