from select import select
from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES =   (
    ('S','Stripe'),
    ('P','Paypal')
)

class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder':'Street No.'
    }))
    apartment_address = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'placeholder':'House No.'
    }))
    country = CountryField(blank_label='(select_country)').formfield(widget=CountrySelectWidget(
        attrs = {
            'class': 'custom-select d-block w-100'
        }
    ))
    zip = forms.CharField(widget=forms.TextInput(attrs = {
        'class':'form-control'
    }))
    same_shipping_address = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICES)

