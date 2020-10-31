from django import forms
from p_library.models import Author, Book
from django.forms import formset_factory
from allauth.account import forms as aaforms
  
class AuthorForm(forms.ModelForm):
    full_name = forms.CharField(widget=forms.TextInput)
    class Meta:
        model = Author
        fields = '__all__'

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'

