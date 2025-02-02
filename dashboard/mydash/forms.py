# forms.py
from django import forms
from .models import ResearchCenter, Continent, Region, ResearchArea

class SearchResearchCenterForm(forms.Form):
    search_query = forms.CharField(required=False, label="Search by Name", max_length=255)

class FilterResearchCenterForm(forms.Form):
    continent = forms.ModelChoiceField(queryset=Continent.objects.all(), required=False)
    region = forms.ModelChoiceField(queryset=Region.objects.all(), required=False)
    research_area = forms.ModelChoiceField(queryset=ResearchArea.objects.all(), required=False)
