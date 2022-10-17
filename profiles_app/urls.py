from rest_framework.routers import DefaultRouter

from profiles_app import views

router = DefaultRouter()

router.register('login', views.UserLoginViewSet, basename='login')
router.register('logout', views.UserLogoutViewSet, basename='logout')
router.register('forgot-password', views.ForgotPasswordViewSet, basename='password')
router.register('reset-password', views.ResetPasswordViewSet, basename='reset-password')
router.register('logoutAll', views.UserLogoutAllDevicesViewSet, basename='logoutAll')
router.register('register', views.UserRegisterViewSet, basename='register')
router.register('users', views.UsersViewSet, basename='users')
router.register('token', views.TokenViewSet, basename='token_refresh')

urlpatterns = router.get_urls()
