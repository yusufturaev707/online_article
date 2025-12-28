from django import forms
from django.forms import TextInput, Textarea, FileInput, Select
from article_app.models import *
from article_app.sanitizer import sanitize_title, sanitize_keywords, sanitize_abstract, sanitize_plain_text
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.utils.translation import gettext_lazy as _


class CreateArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['section', 'title', 'article_type', 'article_lang', 'country']

        widgets = {
            'country': Select(attrs={
                'class': 'form-control selectpicker forshadow',
                'data-size': "10",
                'data-live-search': "true",
                'data-style': "btn-white",
                'data-placeholder': "Tanlang",
                'data-parsley-required': "true",
            }),
            'article_type': Select(attrs={
                'class': 'form-control selectpicker forshadow',
                'data - size': "10",
                'data-live-search': "true",
                'data-style': "btn-white",
                'data - parsley - required': "true",
            }),
            'article_lang': Select(attrs={
                'class': 'form-control selectpicker forshadow',
                'data - size': "10",
                'data-live-search': "true",
                'data-style': "btn-white",
                'data - parsley - required': "true",
            }),
            'section': Select(attrs={
                'class': 'form-control selectpicker forshadow',
                'data - size': "10",
                'data-live-search': "true",
                'data-style': "btn-white",
                'data - parsley - required': "true",
            }),
            'title': Textarea(attrs={
                'class': 'form-control forshadow',
                'data - size': "10",
                'data - parsley - required': "true",
            }),
        }

    def __init__(self, *args, **kwargs):
        super(CreateArticleForm, self).__init__(*args, **kwargs)
        self.fields['country'].empty_label = _("Tanlang")
        self.fields['article_type'].empty_label = _("Tanlang")
        self.fields['article_lang'].empty_label = _("Tanlang")
        self.fields['section'].empty_label = _("Tanlang")

    def clean_title(self):
        """Sarlavhani XSS dan tozalash"""
        title = self.cleaned_data.get('title', '')
        return sanitize_title(title)


class CreateArticleFileForm(forms.ModelForm):
    class Meta:
        model = ArticleFile
        fields = ['file', 'article']
        labels = {
            'file': 'Writer',
        }
        help_texts = {
            'file': 'Word yuklang!',
        }
        error_messages = {
            'file': {
                'max_length': "This writer's name is too long.",
            },
        }

        widgets = {
            'file': FileInput(attrs={
                'class': 'form-control',
                'type': 'file',
                'name': 'file',
                'id': 'id_file',
                'accept': ".docx, .doc, .pdf",
                'data - parsley - required': "true",
            }),
        }


class UpdateArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'section', 'abstract', 'keywords', 'title_en', 'abstract_en', 'keywords_en',
                  'article_type', 'article_lang', 'country']

        widgets = {
            'section': Select(attrs={
                'class': 'form-control selectpicker',
                'data-live-search': "true",
                'data-style': "btn-white",
                'name': 'section',
                'id': 'id_section',
            }),
            'title': Textarea(attrs={
                'class': 'form-control title',
                'rows': '1',
                'name': 'title',
                'id': 'id_title',
            }),
            'title_en': Textarea(attrs={
                'class': 'form-control title_en',
                'rows': '1',
                'name': 'title-en',
                'id': 'id_title_en',
            }),
            'abstract': Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'Enter...',
                'name': 'abstract',
                'id': 'id_abstract',
            }),
            'abstract_en': Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'name': 'abstract_en',
                'id': 'id_abstract_en',
            }),
            'keywords': Textarea(attrs={
                'class': 'form-control',
                'name': 'keywords',
                'id': 'id_keywords',
                'rows': '3',
            }),
            'keywords_en': Textarea(attrs={
                'class': 'form-control',
                'name': 'keywords_en',
                'id': 'id_keywords_en',
                'rows': '3',
            }),
            'country': Select(attrs={
                'class': 'form-control selectpicker',
                'data-size': "10",
                'data-live-search': "true",
                'data-style': "btn-white",
                'data-placeholder': "Tanlang",
                'data-parsley-required': "true",
            }),
            'article_type': Select(attrs={
                'class': 'form-control selectpicker',
                'data - size': "10",
                'data-live-search': "true",
                'data-style': "btn-white",
            }),
            'article_lang': Select(attrs={
                'class': 'form-control selectpicker',
                'data - size': "10",
                'data-live-search': "true",
                'data-style': "btn-white",
            }),
        }

    def __init__(self, *args, **kwargs):
        super(UpdateArticleForm, self).__init__(*args, **kwargs)
        self.fields['section'].empty_label = _("Tanlang")
        self.fields['country'].empty_label = _("Tanlang")
        self.fields['article_type'].empty_label = _("Tanlang")
        self.fields['article_lang'].empty_label = _("Tanlang")

    def clean_title(self):
        """Sarlavhani XSS dan tozalash"""
        title = self.cleaned_data.get('title', '')
        return sanitize_title(title)

    def clean_title_en(self):
        """Inglizcha sarlavhani XSS dan tozalash"""
        title_en = self.cleaned_data.get('title_en', '')
        return sanitize_title(title_en)

    def clean_abstract(self):
        """Annotatsiyani XSS dan tozalash"""
        abstract = self.cleaned_data.get('abstract', '')
        return sanitize_abstract(abstract)

    def clean_abstract_en(self):
        """Inglizcha annotatsiyani XSS dan tozalash"""
        abstract_en = self.cleaned_data.get('abstract_en', '')
        return sanitize_abstract(abstract_en)

    def clean_keywords(self):
        """Kalit so'zlarni XSS dan tozalash"""
        keywords = self.cleaned_data.get('keywords', '')
        return sanitize_keywords(keywords)

    def clean_keywords_en(self):
        """Inglizcha kalit so'zlarni XSS dan tozalash"""
        keywords_en = self.cleaned_data.get('keywords_en', '')
        return sanitize_keywords(keywords_en)


class AddAuthorForm(forms.ModelForm):
    class Meta:
        model = ExtraAuthor
        fields = ['article', 'fname', 'lname', 'mname', 'email', 'work', 'scientific_degree']

        widgets = {
            'fname': TextInput(attrs={
                'id': 'author_fname',
                'class': 'form-control forshadow',
                'type': 'text',
            }),
            'lname': TextInput(attrs={
                'id': 'author_lname',
                'class': 'form-control forshadow',
                'type': 'text',
                'data - parsley - required': "true",
            }),
            'mname': TextInput(attrs={
                'id': 'author_mname',
                'class': 'form-control forshadow',
                'type': 'text',
                'data - parsley - required': "true",
            }),
            'email': TextInput(attrs={
                'id': 'author_email',
                'class': 'form-control forshadow',
                'type': 'email',
                'data-parsley-type': "email",
                'placeholder': 'someone@example.com',
                'data - parsley - required': "true",
            }),
            'work': TextInput(attrs={
                'id': 'author_work',
                'class': 'form-control forshadow',
                'type': 'text',
                'data - parsley - required': "true",
            }),
            'scientific_degree': Select(attrs={
                'class': 'form-control forshadow',
                'data-live-search': "true",
                'data-style': "btn-white",
                'name': 'scientific_degree',
            }),

        }

    def __init__(self, *args, **kwargs):
        super(AddAuthorForm, self).__init__(*args, **kwargs)
        self.fields['scientific_degree'].empty_label = _("Tanlang")

    def clean_fname(self):
        return sanitize_plain_text(self.cleaned_data.get('fname', ''))

    def clean_lname(self):
        return sanitize_plain_text(self.cleaned_data.get('lname', ''))

    def clean_mname(self):
        return sanitize_plain_text(self.cleaned_data.get('mname', ''))

    def clean_work(self):
        return sanitize_plain_text(self.cleaned_data.get('work', ''))


class SendMessageForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['article', 'from_user', 'to_user', 'message']

        widgets = {
            'message': Textarea(attrs={
                'class': 'form-control forshadow',
                'placeholder': "...",
                'data - parsley - required': "true",
                'name': 'message',
            }),
        }

    def clean_message(self):
        return sanitize_plain_text(self.cleaned_data.get('message', ''))


class CreateSectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['name']

        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
                'data - parsley - required': "true",
            }),
        }


class CreateStageForm(forms.ModelForm):
    class Meta:
        model = Stage
        fields = ['name']

        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
        }


class CreateArticleTypeForm(forms.ModelForm):
    class Meta:
        model = ArticleType
        fields = ['name']

        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
        }


class CreateNotificationStatusForm(forms.ModelForm):
    class Meta:
        model = NotificationStatus
        fields = ['name']

        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
        }


class CreateArticleStatusForm(forms.ModelForm):
    class Meta:
        model = ArticleStatus
        fields = ['name', 'stage']

        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
            'stage': Select(attrs={
                'class': 'form-control',
                'data-live-search': "true",
                'data-style': "btn-white",
            }),
        }
