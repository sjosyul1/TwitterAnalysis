from django import forms


# HomeForm takes inputs ProductModel
class HomeForm(forms.Form):
    name = forms.CharField(max_length=50, label='Search Place for Reviews',
                              widget=forms.TextInput(attrs={'placeholder': 'Place Name'}))

    def clean(self):
        cleaned_data = super(HomeForm, self).clean()
        name = cleaned_data.get('name')

        if not name:
            raise forms.ValidationError('All Fields are Mandatory!')
