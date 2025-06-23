from django import forms
from django.core.exceptions import ValidationError
import re

class PedidoForm(forms.Form):
    cliente_id = forms.IntegerField(label='ID Cliente')
    productos = forms.CharField(widget=forms.HiddenInput())  # Este campo se llenará desde JS
    tipo_entrega = forms.ChoiceField(choices=[('retiro', 'Retiro en tienda'), ('envio', 'Envío a domicilio')])
    direccion_entrega = forms.CharField(max_length=255, required=False)



def validar_rut_chileno(rut):
    rut = rut.upper().replace("-", "").replace(".", "")
    aux = rut[:-1]
    dv = rut[-1]

    try:
        reversed_digits = list(map(int, reversed(aux)))
    except ValueError:
        raise ValidationError("RUT inválido.")

    factors = [2, 3, 4, 5, 6, 7] * 2
    s = sum(d * f for d, f in zip(reversed_digits, factors))
    res = 11 - (s % 11)
    if res == 11:
        dv_calc = '0'
    elif res == 10:
        dv_calc = 'K'
    else:
        dv_calc = str(res)

    if dv != dv_calc:
        raise ValidationError("RUT inválido.")

class CustomRegisterForm(forms.Form):
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    nombre = forms.CharField()
    apellido = forms.CharField()
    rut = forms.CharField()
    telefono = forms.CharField()
    is_b2b = forms.BooleanField(required=False)

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email.endswith('@gmail.com'):
            raise ValidationError("El correo debe ser de Gmail.")
        return email

    def clean_password1(self):
        password = self.cleaned_data['password1']
        if len(password) < 8 or not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password) or not re.search(r"\W", password):
            raise ValidationError("La contraseña debe tener al menos 8 caracteres, incluyendo letras, números y símbolos.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            raise ValidationError("Las contraseñas no coinciden.")
        validar_rut_chileno(cleaned_data.get('rut', ''))
        if not cleaned_data.get('telefono', '').isdigit() or len(cleaned_data.get('telefono', '')) < 8:
            raise ValidationError("El teléfono debe contener solo números y tener al menos 8 dígitos.")
