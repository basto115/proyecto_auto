from django import forms


class PedidoForm(forms.Form):
    cliente_id = forms.IntegerField(label='ID Cliente')
    productos = forms.CharField(widget=forms.HiddenInput())  # Este campo se llenará desde JS
    tipo_entrega = forms.ChoiceField(choices=[('retiro', 'Retiro en tienda'), ('envio', 'Envío a domicilio')])
    direccion_entrega = forms.CharField(max_length=255, required=False)
