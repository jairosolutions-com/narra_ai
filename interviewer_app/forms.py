from django import forms
from .models import UserProfile


class IntakeForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "full_name",
            "maiden_name",
            "previous_name",
            "birthday",
            "birth_place",
            "grew_up_in",
        ]
