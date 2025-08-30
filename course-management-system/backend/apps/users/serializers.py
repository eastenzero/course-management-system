from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, UserPreference


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'user_type', 'employee_id', 'student_id', 'department',
            'phone', 'avatar', 'is_active', 'date_joined',
            'password', 'password_confirm'
        ]
        read_only_fields = ['id', 'date_joined']

    def validate(self, attrs):
        """验证密码确认"""
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({'password_confirm': '两次输入的密码不一致'})
        return attrs

    def create(self, validated_data):
        """创建用户"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        """更新用户"""
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    """用户资料序列化器（不包含密码）"""

    display_id = serializers.ReadOnlyField()
    user_type_display = serializers.CharField(source='get_user_type_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'user_type', 'user_type_display', 'employee_id', 'student_id',
            'department', 'phone', 'avatar', 'is_active',
            'date_joined', 'display_id'
        ]
        read_only_fields = ['id', 'username', 'date_joined', 'user_type']


class LoginSerializer(serializers.Serializer):
    """登录序列化器"""

    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('用户名或密码错误')
            if not user.is_active:
                raise serializers.ValidationError('用户账户已被禁用')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('必须提供用户名和密码')

        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """修改密码序列化器"""

    old_password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()

    def validate_old_password(self, value):
        """验证旧密码"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('旧密码错误')
        return value

    def validate(self, attrs):
        """验证新密码确认"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': '两次输入的新密码不一致'})
        return attrs

    def save(self):
        """保存新密码"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class RegisterSerializer(serializers.Serializer):
    """注册序列化器（面向匿名注册端点）"""
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(validators=[validate_password])
    # 前端可能传 confirm_password 或 password_confirm，二者择一
    password_confirm = serializers.CharField(required=False)
    confirm_password = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        confirm = attrs.get('password_confirm') or attrs.get('confirm_password')
        if attrs.get('password') != confirm:
            raise serializers.ValidationError({'password_confirm': '两次输入的密码不一致'})
        return attrs

    def create(self, validated_data):
        # 默认注册为学生；自动生成 student_id
        from django.db.models.functions import Substr
        from django.db.models import Max
        username = validated_data['username']
        email = validated_data.get('email')
        password = validated_data['password']
        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')

        # 生成下一个 student_id: student000001 递增
        prefix = 'student'
        last_num = (
            User.objects.filter(student_id__startswith=prefix)
            .annotate(num=Substr('student_id', len(prefix) + 1))
            .aggregate(maxn=Max('num'))
            .get('maxn')
        )
        try:
            next_seq = int(last_num) + 1 if last_num else 1
        except (TypeError, ValueError):
            next_seq = 1
        student_id = f"{prefix}{next_seq:06d}"

        user = User(
            username=username,
            email=email or '',
            first_name=first_name,
            last_name=last_name,
            user_type='student',
            student_id=student_id,
            is_active=True,
        )
        user.set_password(password)
        user.save()
        return user


class UserPreferenceSerializer(serializers.ModelSerializer):
    """用户偏好设置序列化器"""

    class Meta:
        model = UserPreference
        fields = [
            'theme', 'language', 'page_size', 'date_format',
            'profile_visibility', 'show_email', 'show_phone',
            'auto_logout', 'session_timeout'
        ]

    def validate_page_size(self, value):
        """验证分页大小"""
        if not (5 <= value <= 100):
            raise serializers.ValidationError("分页大小必须在5-100之间")
        return value

    def validate_auto_logout(self, value):
        """验证自动登出时间"""
        if not (5 <= value <= 480):
            raise serializers.ValidationError("自动登出时间必须在5-480分钟之间")
        return value
