from django.contrib.auth import authenticate

from rest_framework import serializers

from core.models import Comment, CommentAttachment
from django.contrib.contenttypes.models import ContentType

from entities.models.employees import Employee
from entities.serializers import EmployeeSerializer


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get('request'),
            username=attrs['username'],
            password=attrs['password'],
        )
        if not user or not user.is_active:
            raise serializers.ValidationError('Credenciales inválidas.')
        attrs['user'] = user
        return attrs


class CommentAttachmentSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    filename = serializers.CharField(source='file.name', read_only=True)

    class Meta:
        model = CommentAttachment
        fields = ('id', 'filename', 'url', 'uploaded_at')

    def get_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        if obj.file:
            return obj.file.url
        return None

class CommentSerializer(serializers.ModelSerializer):
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(), source='employee', write_only=True
    )
    employee = EmployeeSerializer(read_only=True)
    content_type = serializers.SlugRelatedField(
        slug_field='model',
        queryset=ContentType.objects.all()
    )
    object_id = serializers.IntegerField()
    related_object = serializers.SerializerMethodField()
    attachments = CommentAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = (
            'id',
            'employee',
            'employee_id',
            'event',
            'comment_type',
            'log_type',
            'content',
            'data',
            'content_type',
            'object_id',
            'related_object',
            'attachments',
            'created_at',
            'updated_at'
        )

    def get_related_object(self, obj):
        if obj.related_object:
            return str(obj.related_object)
        return None

    def create(self, validated_data):
        """
        Crea el comentario y guarda los archivos enviados en request.FILES.getlist('files').
        El front envía: files.forEach((f, idx) => formData.append('files', f, f.name));
        """
        request = self.context.get('request')
        # validated_data already contains 'employee' as instance because of PrimaryKeyRelatedField
        comment = Comment.objects.create(**validated_data)

        if request is not None:
            files = request.FILES.getlist('files')
            for f in files:
                CommentAttachment.objects.create(comment=comment, file=f)
        return comment