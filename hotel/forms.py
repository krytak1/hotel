from django import forms
from .models import Address, Client, Booking, Payment, ProductOrder, ServiceOrder, BuildingProducts, BuildingServices, Employee, Position, Room, Review, Building

class ClientForm(forms.ModelForm):
    phone = forms.CharField(
        label='Телефон',
        widget=forms.TextInput(attrs={
            'data-mask': 'phone',
            'placeholder': '+7 (___) ___-__-__',
            'class': 'border rounded p-2 w-full'
        })
    )

    passport_data = forms.CharField(
        label='Паспортные данные',
        widget=forms.TextInput(attrs={
            'data-mask': 'passport',
            'placeholder': '____ ______',
            'class': 'border rounded p-2 w-full'
        })
    )

    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'middle_name', 'phone', 'email', 'passport_data']
        widgets = {
            'first_name':  forms.TextInput(attrs={'class': 'border rounded p-2 w-full'}),
            'last_name':   forms.TextInput(attrs={'class': 'border rounded p-2 w-full'}),
            'middle_name': forms.TextInput(attrs={'class': 'border rounded p-2 w-full'}),
            'email':       forms.EmailInput(attrs={'class': 'border rounded p-2 w-full', 'placeholder': 'example@mail.ru'}),
        }


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['client', 'room', 'checkin_date', 'checkout_date']
        widgets = {
            'client': forms.Select(attrs={'class': 'border rounded p-2 w-full'}),
            'room':   forms.Select(attrs={'class': 'border rounded p-2 w-full'}),
            'checkin_date':  forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'border rounded p-2 w-full',
                },
                format='%Y-%m-%d'
            ),
            'checkout_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'border rounded p-2 w-full',
                },
                format='%Y-%m-%d'
            ),
        }

    def clean(self):
        cd = super().clean()
        room = cd.get('room')
        ci   = cd.get('checkin_date')
        co   = cd.get('checkout_date')
        if room and ci and co:
            if ci >= co:
                raise ValidationError('Дата заезда должна быть раньше даты выезда')
            if not room.is_available(ci, co):
                raise ValidationError('Номер недоступен в эти даты')
        return cd

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['booking', 'amount', 'payment_date', 'payment_method', 'status']
        widgets = {
            'booking': forms.Select(attrs={
                'class': 'border rounded p-2 w-full'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'border rounded p-2 w-full',
                'step': '0.01',
            }),
            'payment_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'border rounded p-2 w-full',
                # можно добавить min/max если нужно: 'min': '2025-01-01', …
            }),
            'payment_method': forms.Select(attrs={
                'class': 'border rounded p-2 w-full'
            }),
            'status': forms.Select(attrs={
                'class': 'border rounded p-2 w-full'
            }),
        }

    def clean(self):
        cd = super().clean()
        booking = cd.get('booking')
        amount = cd.get('amount')
        if booking and amount and amount > booking.total_price:
            raise ValidationError('Сумма не может превышать стоимость брони')
        return cd

class ProductOrderForm(forms.ModelForm):
    class Meta:
        model = ProductOrder
        fields = ['product','quantity']
        widgets = {
            'product':  forms.Select(attrs={'class':'border rounded p-2 w-full'}),
            'quantity': forms.NumberInput(attrs={'class':'border rounded p-2 w-full'}),
        }


class ServiceOrderForm(forms.ModelForm):
    class Meta:
        model = ServiceOrder
        fields = ['service']
        widgets = {
            'service': forms.Select(attrs={'class':'border rounded p-2 w-full'}),
        }


class BuildingProductsForm(forms.ModelForm):
    class Meta:
        model = BuildingProducts
        fields = ['building','product','available']
        widgets = {
            'building': forms.Select(attrs={'class':'border rounded p-2 w-full'}),
            'product':  forms.Select(attrs={'class':'border rounded p-2 w-full'}),
            'available':forms.NumberInput(attrs={'class':'border rounded p-2 w-full'}),
        }

class BuildingServicesForm(forms.ModelForm):
    class Meta:
        model = BuildingServices
        fields = ['building','service','is_active']
        widgets = {
            'building': forms.Select(attrs={'class':'border rounded p-2 w-full'}),
            'service':  forms.Select(attrs={'class':'border rounded p-2 w-full'}),
            'is_active':forms.CheckboxInput(attrs={'class':'form-checkbox'}),
        }


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['first_name','last_name','middle_name','phone','building','positions']
        widgets = {
            'first_name':  forms.TextInput(attrs={'class':'border rounded p-2 w-full'}),
            'last_name':   forms.TextInput(attrs={'class':'border rounded p-2 w-full'}),
            'middle_name': forms.TextInput(attrs={'class':'border rounded p-2 w-full'}),
            'phone':       forms.TextInput(attrs={'class':'border rounded p-2 w-full','data-mask':'phone','placeholder':'+7 (___) ___-__-__'}),
            'building':    forms.Select(attrs={'class':'border rounded p-2 w-full'}),
            'positions':   forms.SelectMultiple(attrs={'class':'border rounded p-2 w-full'}),
        }


class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'border rounded p-2 w-full'}),
        }


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['building','room_number','room_type','status']
        widgets = {
            'building':    forms.Select(attrs={'class':'border rounded p-2 w-full'}),
            'room_number': forms.TextInput(attrs={'class':'border rounded p-2 w-full'}),
            'room_type':   forms.Select(attrs={'class':'border rounded p-2 w-full'}),
            'status':      forms.Select(attrs={'class':'border rounded p-2 w-full'}),
        }



# forms.py

class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [(i, '★' * i + '☆' * (5 - i)) for i in range(1, 6)]

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.Select(attrs={
            'class': 'border rounded p-2 w-full bg-white',
        }),
        label='Рейтинг'
    )

    class Meta:
        model = Review
        fields = ['client', 'booking', 'rating', 'review_text']
        widgets = {
            'client': forms.Select(attrs={'class': 'border rounded p-2 w-full'}),
            'booking': forms.Select(attrs={'class': 'border rounded p-2 w-full'}),
            'review_text': forms.Textarea(attrs={'class': 'border rounded p-2 w-full', 'rows': 4}),
        }


class BuildingForm(forms.ModelForm):
    class Meta:
        model = Building
        fields = ['name', 'description', 'capacity', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'border rounded p-2 w-full'}),
            'description': forms.Textarea(attrs={'class': 'border rounded p-2 w-full', 'rows': 4}),
            'capacity': forms.NumberInput(attrs={'class': 'border rounded p-2 w-full'}),
            'address': forms.Select(attrs={'class': 'border rounded p-2 w-full'}),
        }


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['city', 'street', 'house']