from django import forms
from .models import Item, Category, Review, UserInterest

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['title', 'description', 'price', 'category', 'condition', 'location']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your item...'}),
            'title': forms.TextInput(attrs={'placeholder': 'What are you offering?'}),
            'location': forms.TextInput(attrs={'placeholder': 'General meetup location (e.g., New Dorms, Central Grounds)'}),
        }
        labels = {
            'condition': 'Item Condition',
        }

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class ItemImageForm(forms.Form):
    images = MultipleFileField(
        required=False,
        label='Upload Images'
    )

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Share your experience with this user...'}),
        }

class SearchFilterForm(forms.Form):
    query = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Search items...',
        'class': 'form-control'
    }))
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories"
    )
    min_price = forms.DecimalField(required=False, max_digits=10, decimal_places=2)
    max_price = forms.DecimalField(required=False, max_digits=10, decimal_places=2)
    condition = forms.ChoiceField(
        choices=[('', 'Any Condition')] + list(Item.CONDITION_CHOICES),
        required=False
    )

class UserInterestForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="I'm interested in:"
    )

    class Meta:
        model = UserInterest
        fields = []