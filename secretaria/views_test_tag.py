from django.shortcuts import render
from .forms_test_tag import TagTestForm

def test_tag_form_view(request):
    form = TagTestForm()
    return render(request, 'secretaria/test_tag_form.html', {'form': form})
