from knox.views import LoginView as KnoxLoginView, LogoutView as KnoxLogoutView, LogoutAllView as KnoxLogoutAllView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from core.models import Comment

from .serializers import CommentSerializer, LoginSerializer

from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny

from collections import defaultdict
from django.contrib.auth import login
from django.contrib.contenttypes.models import ContentType
from rest_framework.views import APIView


class LoginView(KnoxLoginView):
    """Login con username/password → devuelve token Knox."""
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        response = super().post(request, format=None)

        account_data = {
            'id': user.pk,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }

        employee_data = None
        employee = getattr(user, 'employee', None)
        if employee:
            employee_data = {
                'id': employee.pk,
                'first_name': employee.first_name,
                'last_name_father': employee.last_name_father,
                'last_name_mother': employee.last_name_mother,
                'full_name': employee.full_name,
                'date_of_birth': employee.date_of_birth,
                'age': employee.age,
                'gender': employee.gender,
                'email': employee.email,
                'phone': employee.phone,
                'photo': request.build_absolute_uri(employee.photo.url) if employee.photo else None,
                'department': employee.department_id,
                'department_name': employee.department.name if employee.department else None,
                'job_position': employee.job_position_id,
                'job_position_name': employee.job_position.name if employee.job_position else None,
                'status': employee.status_id,
                'status_name': employee.status.name if employee.status else None,
            }

        response.data['account'] = account_data
        response.data['employee'] = employee_data
        response.data.pop('user', None)
        return response


class LogoutView(KnoxLogoutView):
    """Cierra la sesión actual (invalida el token usado)."""
    pass


class LogoutAllView(KnoxLogoutAllView):
    """Cierra todas las sesiones del usuario."""
    pass


class CommentView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # permite recibir files en multipart/form-data

    def get(self, request, *args, **kwargs):
        comments_qs = Comment.objects.filter(comment_type='comment')
        logs_qs = Comment.objects.filter(comment_type='log')

        data = {
            'comments': self._group_queryset(comments_qs, request),
            'logs': self._group_queryset(logs_qs, request),
        }
        return Response(data)

    def _group_queryset(self, qs, request):
        grouped = defaultdict(list)
        for comment in qs.order_by('created_at'):
            day = comment.created_at.day
            month = comment.created_at.month
            year = comment.created_at.year
            grouped[(day, month, year)].append(comment)

        sorted_keys = sorted(grouped.keys(), key=lambda x: (x[2], x[1], x[0]))  # year, month, day

        response = []
        for (day, month, year) in sorted_keys:
            comment_list = grouped[(day, month, year)]
            serialized = CommentSerializer(comment_list, many=True, context={'request': request})
            response.append({
                'date': {'day': day, 'month': month, 'year': year},
                'comments': serialized.data
            })
        return response

class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

class FilteredGroupedCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content_type_param = request.query_params.get('content_type')
        object_id_param = request.query_params.get('object_id')

        if not content_type_param or not object_id_param:
            return Response({'error': 'Se requiere content_type y object_id'}, status=400)

        try:
            content_type = ContentType.objects.get(model=content_type_param)
        except ContentType.DoesNotExist:
            return Response({'error': 'content_type inválido'}, status=400)

        comments_qs = Comment.objects.filter(
            content_type=content_type,
            object_id=object_id_param,
            comment_type='comment'
        ).order_by('created_at')

        logs_qs = Comment.objects.filter(
            content_type=content_type,
            object_id=object_id_param,
            comment_type='log'
        ).order_by('created_at')

        data = {
            'comments': self._group_queryset(comments_qs, request),
            'logs': self._group_queryset(logs_qs, request),
        }

        return Response(data)

    def _group_queryset(self, qs, request):
        grouped = defaultdict(list)
        for comment in qs.order_by('created_at'):
            day = comment.created_at.day
            month = comment.created_at.month
            year = comment.created_at.year
            grouped[(day, month, year)].append(comment)

        sorted_keys = sorted(grouped.keys(), key=lambda x: (x[2], x[1], x[0]))  # year, month, day

        response = []
        for (day, month, year) in sorted_keys:
            comment_list = grouped[(day, month, year)]
            serialized = CommentSerializer(comment_list, many=True, context={'request': request})
            response.append({
                'date': {'day': day, 'month': month, 'year': year},
                'comments': serialized.data
            })
        return response
    #END FILTERED GROUPED COMMENT VIEW