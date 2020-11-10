from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import (
    LoginView, LogoutView, PasswordResetView,
    PasswordChangeView, PasswordResetConfirmView
)


class CustomRegisterView(RegisterView):
    pass


class CustomLoginView(LoginView):
    pass


class CustomLogoutView(LogoutView):
    pass


class CustomPasswordResetView(PasswordResetView):
    pass


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    pass


class CustomPasswordChangeView(PasswordChangeView):
    pass
