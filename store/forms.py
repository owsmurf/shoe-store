from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'article', 'product_name', 'category', 'description',
            'manufacturer', 'supplier', 'price', 'unit',
            'quantity_in_stock', 'discount', 'photo'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'article': forms.TextInput(attrs={'placeholder': 'Артикул'}),
            'product_name': forms.TextInput(attrs={'placeholder': 'Наименование'}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'quantity_in_stock': forms.NumberInput(attrs={'min': '0'}),
            'discount': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '100'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError('Цена не может быть отрицательной.')
        return price

    def clean_quantity_in_stock(self):
        qty = self.cleaned_data.get('quantity_in_stock')
        if qty is not None and qty < 0:
            raise forms.ValidationError('Количество не может быть отрицательным.')
        return qty

    def clean_discount(self):
        discount = self.cleaned_data.get('discount')
        if discount is not None and (discount < 0 or discount > 100):
            raise forms.ValidationError('Скидка должна быть от 0 до 100.')
        return discount
