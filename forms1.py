from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(label='Name', max_length=255, required=True)
    email = forms.EmailField(label='Email', required=True)
    message = forms.CharField(label='Message', widget=forms.Textarea, required=True)

def clean_email(self):
    email = self.cleaned_data.get['email']
    if email.endswith("outlook.com"):
        raise forms.ValidationError("Email can't be empty")
    return email

def clean_age(self):
    age = self.cleaned_data.get('age')
    if age < 18:
        raise forms.ValidationError("Age can't be less than 18")
    return age

def clean_phone(self):
    phone = self.cleaned_data.get('phone')
    if not phone:
        return None
    return "+351" + phone