from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """Registration form for CustomUser model."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username',)
