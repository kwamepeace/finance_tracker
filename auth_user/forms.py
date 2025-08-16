from django import forms
from .models import CustomUser
from django.contrib.auth.forms import ReadOnlyPasswordHashField



class UserCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required fields,
    plus a repeated password.
    
    """
    password1 = forms.CharField(widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password", required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'date_of_birth', 'profile_photo']

    def clean_password2(self):
        """
        Check that the two password entries match.
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match.")
        return password2
    
    def save(self, commit=True):
        """
        Save the provided password in hashed format.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
    
class CustomUserChangeForm(forms.ModelForm):
    """
    A form for updating users. Includes all the fields on the user,
    but replaces the password field with a password change form.
    """
    password = ReadOnlyPasswordHashField()
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'date_of_birth', 'profile_photo']
    
    