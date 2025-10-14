"""
用户模块测试
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.users.models import UserPreference
from apps.users.serializers import UserSerializer, UserProfileSerializer, UserPreferenceSerializer

User = get_user_model()


class UserModelTestCase(TestCase):
    """用户模型测试"""

    def setUp(self):
        """设置测试数据"""
        pass

    def test_create_student_user(self):
        """测试创建学生用户"""
        user = User.objects.create_user(
            username='student1',
            email='student1@test.com',
            password='testpass123',
            user_type='student',
            student_id='S001',
            first_name='张',
            last_name='三',
            department='计算机学院'
        )

        self.assertEqual(user.username, 'student1')
        self.assertEqual(user.email, 'student1@test.com')
        self.assertEqual(user.user_type, 'student')
        self.assertEqual(user.student_id, 'S001')
        self.assertEqual(user.department, '计算机学院')
        self.assertTrue(user.check_password('testpass123'))

    def test_create_teacher_user(self):
        """测试创建教师用户"""
        user = User.objects.create_user(
            username='teacher1',
            email='teacher1@test.com',
            password='testpass123',
            user_type='teacher',
            employee_id='T001',
            first_name='李',
            last_name='老师',
            department='计算机学院'
        )

        self.assertEqual(user.username, 'teacher1')
        self.assertEqual(user.user_type, 'teacher')
        self.assertEqual(user.employee_id, 'T001')
        self.assertEqual(user.department, '计算机学院')

    def test_user_display_id_property(self):
        """测试用户显示ID属性"""
        # 测试学生用户
        student = User.objects.create_user(
            username='student1',
            user_type='student',
            student_id='S001'
        )
        self.assertEqual(student.display_id, 'S001')

        # 测试教师用户
        teacher = User.objects.create_user(
            username='teacher1',
            user_type='teacher',
            employee_id='T001'
        )
        self.assertEqual(teacher.display_id, 'T001')

    def test_user_str_method(self):
        """测试用户字符串表示"""
        user = User.objects.create_user(
            username='student1',
            user_type='student'
        )
        expected_str = "student1 - 学生"
        self.assertEqual(str(user), expected_str)


class UserPreferenceTestCase(TestCase):
    """用户偏好设置测试"""

    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )

    def test_create_user_preference(self):
        """测试创建用户偏好设置"""
        preference = UserPreference.objects.create(
            user=self.user,
            theme='dark',
            language='en-US',
            page_size=20,
            date_format='MM/DD/YYYY',
            profile_visibility='private',
            show_email=False,
            show_phone=True,
            auto_logout=60,
            session_timeout=False
        )

        self.assertEqual(preference.user, self.user)
        self.assertEqual(preference.theme, 'dark')
        self.assertEqual(preference.language, 'en-US')
        self.assertEqual(preference.page_size, 20)
        self.assertEqual(preference.date_format, 'MM/DD/YYYY')
        self.assertEqual(preference.profile_visibility, 'private')
        self.assertFalse(preference.show_email)
        self.assertTrue(preference.show_phone)
        self.assertEqual(preference.auto_logout, 60)
        self.assertFalse(preference.session_timeout)

    def test_user_preference_defaults(self):
        """测试用户偏好设置默认值"""
        preference = UserPreference.objects.create(user=self.user)

        self.assertEqual(preference.theme, 'light')
        self.assertEqual(preference.language, 'zh-CN')
        self.assertEqual(preference.page_size, 10)
        self.assertEqual(preference.date_format, 'YYYY-MM-DD')
        self.assertEqual(preference.profile_visibility, 'public')
        self.assertTrue(preference.show_email)
        self.assertFalse(preference.show_phone)
        self.assertEqual(preference.auto_logout, 30)
        self.assertTrue(preference.session_timeout)

    def test_user_preference_str_method(self):
        """测试用户偏好设置字符串表示"""
        preference = UserPreference.objects.create(user=self.user)
        expected_str = f"{self.user.username}的偏好设置"
        self.assertEqual(str(preference), expected_str)


class UserSerializerTestCase(TestCase):
    """用户序列化器测试"""

    def test_user_serializer_validation(self):
        """测试用户序列化器验证"""
        data = {
            'username': 'testuser',
            'email': 'test@test.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'user_type': 'student',
            'first_name': '张',
            'last_name': '三'
        }

        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_user_serializer_password_mismatch(self):
        """测试用户序列化器密码不匹配"""
        data = {
            'username': 'testuser',
            'email': 'test@test.com',
            'password': 'testpass123',
            'password_confirm': 'wrongpass',
            'user_type': 'student'
        }

        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password_confirm', serializer.errors)

    def test_user_preference_serializer(self):
        """测试用户偏好设置序列化器"""
        user = User.objects.create_user(username='testuser')
        preference = UserPreference.objects.create(
            user=user,
            theme='dark',
            page_size=25
        )

        serializer = UserPreferenceSerializer(preference)
        data = serializer.data

        self.assertEqual(data['theme'], 'dark')
        self.assertEqual(data['page_size'], 25)
        self.assertNotIn('user', data)  # user字段不应该在序列化数据中


class UserAPITestCase(APITestCase):
    """用户API测试"""

    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            user_type='student'
        )

        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='adminpass123',
            user_type='admin',
            is_staff=True
        )

    def test_user_registration(self):
        """测试用户注册"""
        url = reverse('users:auth_register')
        data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'first_name': '新',
            'last_name': '用户'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 验证用户已创建
        user_exists = User.objects.filter(username='newuser').exists()
        self.assertTrue(user_exists)

    def test_user_login(self):
        """测试用户登录"""
        url = reverse('users:auth_login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 验证响应包含token
        self.assertIn('data', response.data)
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])

    def test_get_user_profile_unauthorized(self):
        """测试未授权用户无法获取用户资料"""
        url = reverse('users:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_profile_authorized(self):
        """测试授权用户可以获取用户资料"""
        self.client.force_authenticate(user=self.user)

        url = reverse('users:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 验证响应数据
        self.assertIn('data', response.data)
        profile_data = response.data['data']
        self.assertEqual(profile_data['username'], 'testuser')
        self.assertEqual(profile_data['user_type'], 'student')

    def test_update_user_profile(self):
        """测试更新用户资料"""
        self.client.force_authenticate(user=self.user)

        url = reverse('users:profile')
        data = {
            'first_name': '更新',
            'last_name': '姓名',
            'phone': '13800138000',
            'department': '软件学院'
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 验证数据已更新
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, '更新')
        self.assertEqual(self.user.last_name, '姓名')
        self.assertEqual(self.user.phone, '13800138000')
        self.assertEqual(self.user.department, '软件学院')

    def test_get_user_preferences_unauthorized(self):
        """测试未授权用户无法获取偏好设置"""
        url = reverse('users:preferences')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_preferences_authorized(self):
        """测试授权用户可以获取偏好设置"""
        self.client.force_authenticate(user=self.user)

        # 创建偏好设置
        UserPreference.objects.create(
            user=self.user,
            theme='dark',
            page_size=25
        )

        url = reverse('users:preferences')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 验证响应数据
        self.assertIn('data', response.data)
        prefs_data = response.data['data']
        self.assertEqual(prefs_data['theme'], 'dark')
        self.assertEqual(prefs_data['page_size'], 25)

    def test_update_user_preferences(self):
        """测试更新用户偏好设置"""
        self.client.force_authenticate(user=self.user)

        url = reverse('users:preferences')
        data = {
            'theme': 'dark',
            'language': 'en-US',
            'page_size': 50,
            'show_email': False
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 验证偏好设置已创建/更新
        preference = UserPreference.objects.get(user=self.user)
        self.assertEqual(preference.theme, 'dark')
        self.assertEqual(preference.language, 'en-US')
        self.assertEqual(preference.page_size, 50)
        self.assertFalse(preference.show_email)

    def test_user_list_admin_only(self):
        """测试只有管理员可以获取用户列表"""
        # 普通用户无法访问
        self.client.force_authenticate(user=self.user)
        url = reverse('users:user_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 管理员可以访问
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
