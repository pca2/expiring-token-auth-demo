from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class HelloView(APIView):
    permission_classes = [
        IsAuthenticated
    ]  # Only authenticated users can access this view

    def get(self, request):
        context = {"message": "Hello, World!"}
        return Response(context)
