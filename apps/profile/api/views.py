from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.profile.api.permissions import ProfilePermission
from apps.profile.api.serializers import ProfileSerializer
from apps.profile.models import Profile


class ProfileApiView(APIView):
    permission_classes = [ProfilePermission]

    def get_object(self, pk):
        try:
            return Profile.objects.get(email=pk)
        except Profile.DoesNotExist:
            return None

    def patch(self, request, pk, *args, **kwargs):
        profile_instance = self.get_object(pk)
        self.check_object_permissions(self.request, profile_instance)

        if not profile_instance:
            return Response({"profile": ["Profile entry not found"]}, status=status.HTTP_404_NOT_FOUND)

        #Partial is for specified the patch is for specifique object
        serializer = ProfileSerializer(profile_instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"profile": {"valid": True, "email": pk}}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, email, *args, **kwargs):
        profile_instance = self.get_object(email)
        self.check_object_permissions(self.request, profile_instance)

        if not profile_instance:
            return Response({"profile": ["Profile entry not found"]}, status=status.HTTP_404_NOT_FOUND)

        #Partial is for specified the patch is for specifique object
        serializer = ProfileSerializer(profile_instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"profile": {"valid": True, "email": email}}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)