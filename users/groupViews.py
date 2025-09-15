from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from users.groupserializers import AssignGroupSerializer, GroupSerializer, PermissionSerializer


User = get_user_model()


# 🔹 CRUD for Groups
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAdminUser]  # Only admins can manage groups


# 🔹 Assign Groups to a User
class AssignGroupsToUserView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AssignGroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group_names = serializer.validated_data.get("groups", [])
        groups = Group.objects.filter(name__in=group_names)

        if not groups.exists():
            return Response({"error": "No valid groups found"}, status=status.HTTP_400_BAD_REQUEST)

        user.groups.set(groups)  # replace user's groups
        return Response({"message": f"Groups assigned: {[g.name for g in groups]}"}, status=status.HTTP_200_OK)


# 🔹 Add/Remove Single Group from User (Optional)
class AddGroupToUserView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        group_name = request.data.get("group")
        if not group_name:
            return Response({"error": "Group name required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(pk=pk)
            group = Group.objects.get(name=group_name)
        except (User.DoesNotExist, Group.DoesNotExist):
            return Response({"error": "User or Group not found"}, status=status.HTTP_404_NOT_FOUND)

        user.groups.add(group)
        return Response({"message": f"Group '{group.name}' added to user '{user.username}'"})


class RemoveGroupFromUserView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        group_name = request.data.get("group")
        if not group_name:
            return Response({"error": "Group name required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(pk=pk)
            group = Group.objects.get(name=group_name)
        except (User.DoesNotExist, Group.DoesNotExist):
            return Response({"error": "User or Group not found"}, status=status.HTTP_404_NOT_FOUND)

        user.groups.remove(group)
        return Response({"message": f"Group '{group.name}' removed from user '{user.username}'"})

from rest_framework import viewsets
from django.contrib.auth.models import Permission

from rest_framework.permissions import IsAdminUser

class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only endpoint to list all permissions
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAdminUser]  # Only admin can see permissions
