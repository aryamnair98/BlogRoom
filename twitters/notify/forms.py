from django import forms
from .models import NotificationLike

class NotificationForm(forms.ModelForm):
    class Meta:
        model = NotificationLike
        fields = ['notified', 'notifier', 'tweet'] 