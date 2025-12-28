from ckeditor.widgets import CKEditorWidget
from django import forms
from django.forms import Select, TextInput, SelectMultiple, NumberInput, Textarea, PasswordInput
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from user_app.models import *
from user_app.sanitizer import (
    sanitize_text, sanitize_comment, sanitize_username,
    sanitize_email, sanitize_phone, sanitize_url, contains_xss
)
from django.utils.translation import gettext_lazy as _
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.contrib.auth.forms import AuthenticationForm
from captcha.fields import CaptchaField, CaptchaTextInput, CaptchaAnswerInput


class CreateUserForm(UserCreationForm):
    captcha = CaptchaField(widget=CaptchaTextInput())

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'chosen_role']


class LoginForm(AuthenticationForm):
    captcha = CaptchaField(
        widget=CaptchaTextInput(),
        error_messages={'invalid': 'Xato belgilar kiritildi!'})

    class Meta:
        model = User
        fields = ['username', 'password']

        widgets = {
            'username': TextInput(attrs={
                'class': 'form-control username',
            }),
            'password': PasswordInput(attrs={
                'class': 'form-control password',
            }),
        }


class UpdateUserForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'work', 'sc_degree']

        widgets = {
            'username': TextInput(attrs={
                'class': 'form-control username',
                'type': 'text',
            }),
            'phone': TextInput(attrs={
                'class': 'form-control phone',
                'type': 'text',
                'id': 'masked-input-phone',
            }),
            'email': TextInput(attrs={
                'class': 'form-control email',
                'type': 'email',
            }),
            'work': TextInput(attrs={
                'class': 'form-control work',
                'type': 'text',
            }),
            'sc_degree': Select(attrs={
                'class': 'form-control sc_degree',
                'data-live-search': "true",
                'data-style': "btn-white",
            }),
        }

    def __init__(self, *args, **kwargs):
        super(UpdateUserForm, self).__init__(*args, **kwargs)
        self.fields['sc_degree'].empty_label = _("Tanlang")

    def clean_username(self):
        username = self.cleaned_data.get('username', '')
        return sanitize_username(username)

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        return sanitize_email(email)

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        return sanitize_phone(phone)

    def clean_work(self):
        work = self.cleaned_data.get('work', '')
        return sanitize_text(work)


class ReviewerFileForm(forms.ModelForm):
    file = forms.FileField(
        label="Files",
        widget=forms.ClearableFileInput(attrs={"allow_multiple_selected": True, "name": "file"}), required=False
    )

    class Meta:
        model = ReviewerFile
        fields = ['file']


class AddReviewerForm(forms.ModelForm):
    class Meta:
        model = Reviewer
        fields = ['user', 'section']

        widgets = {
            'section': SelectMultiple(attrs={
                'class': 'multiple-select2 form-control',
                'multiple': 'multiple',
                'name': 'section',
            }),
        }


class CreateCountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ['name']

        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
        }

    def clean_name(self):
        return sanitize_text(self.cleaned_data.get('name', ''))


class CreateRegionForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = ['name']

        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
        }

    def clean_name(self):
        return sanitize_text(self.cleaned_data.get('name', ''))


class CreateGenderForm(forms.ModelForm):
    class Meta:
        model = Gender
        fields = ['name']

        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
        }

    def clean_name(self):
        return sanitize_text(self.cleaned_data.get('name', ''))


class CreateRoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'code_name', 'level']

        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
            'code_name': TextInput(attrs={
                'class': 'form-control',
            }),
            'level': TextInput(attrs={
                'class': 'form-control',
            }),
        }

    def clean_name(self):
        return sanitize_text(self.cleaned_data.get('name', ''))

    def clean_code_name(self):
        return sanitize_text(self.cleaned_data.get('code_name', ''))


class CreateScientificDegreeForm(forms.ModelForm):
    class Meta:
        model = ScientificDegree
        fields = ['name', 'level']

        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
            'level': TextInput(attrs={
                'class': 'form-control',
            }),
        }

    def clean_name(self):
        return sanitize_text(self.cleaned_data.get('name', ''))


class CreateMenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['name', 'url', 'url_name', 'icon_name', 'order', 'status', 'type', 'allowed_roles']

        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
            'url': TextInput(attrs={
                'class': 'form-control',
            }),
            'url_name': TextInput(attrs={
                'class': 'form-control',
            }),
            'icon_name': TextInput(attrs={
                'class': 'form-control',
            }),
            'order': NumberInput(attrs={
                'class': 'form-control',
            }),
            'type': NumberInput(attrs={
                'class': 'form-control',
            }),
            'allowed_roles': SelectMultiple(attrs={
                'class': 'multiple-select2 form-control',
                'multiple': 'multiple',
                'name': 'allowed_roles',
            }),
        }

    def clean_name(self):
        return sanitize_text(self.cleaned_data.get('name', ''))

    def clean_url(self):
        return sanitize_url(self.cleaned_data.get('url', ''))

    def clean_url_name(self):
        return sanitize_text(self.cleaned_data.get('url_name', ''))

    def clean_icon_name(self):
        return sanitize_text(self.cleaned_data.get('icon_name', ''))


class ReviewArticleForm(forms.ModelForm):
    class Meta:
        model = ReviewerArticle
        fields = ['comment']

        widgets = {
            'comment': Textarea(attrs={
                'class': 'form-control desc',
                'rows': '3',
                'name': 'comment',
                'id': 'id_comment',
            }),
        }

    def clean_comment(self):
        """Izohni XSS dan tozalash"""
        return sanitize_comment(self.cleaned_data.get('comment', ''))
