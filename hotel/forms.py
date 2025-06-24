from django import forms
from django.core.exceptions import ValidationError
from .models import (
    Address, Client, Booking, Payment, ProductOrder, ServiceOrder,
    BuildingProducts, BuildingServices, Employee, Position, Room,
    Building, Accommodation
)


# === Общие стили для виджетов ===
DEFAULT_TEXT_INPUT = {'class': 'border rounded p-2 w-full'}
DEFAULT_SELECT = {'class': 'border rounded p-2 w-full'}
DEFAULT_NUMBER_INPUT = {'class': 'border rounded p-2 w-full'}
DEFAULT_DATE_INPUT = {'type': 'date', 'class': 'border rounded p-2 w-full'}
DEFAULT_CHECKBOX = {'class': 'form-checkbox'}
DEFAULT_TEXTAREA = {'class': 'border rounded p-2 w-full', 'rows': 4}


# === Клиенты ===
class ClientForm(forms.ModelForm):
    phone = forms.CharField(
        label='Телефон',
        widget=forms.TextInput(attrs={
            **DEFAULT_TEXT_INPUT,
            'data-mask': 'phone',
            'placeholder': '+7 (___) ___-__-__',
        })
    )
    passport_data = forms.CharField(
        label='Паспортные данные',
        widget=forms.TextInput(attrs={
            **DEFAULT_TEXT_INPUT,
            'data-mask': 'passport',
            'placeholder': '____ ______',
        })
    )

    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'middle_name', 'phone', 'email', 'passport_data']
        widgets = {
            'first_name': forms.TextInput(attrs=DEFAULT_TEXT_INPUT),
            'last_name': forms.TextInput(attrs=DEFAULT_TEXT_INPUT),
            'middle_name': forms.TextInput(attrs=DEFAULT_TEXT_INPUT),
            'email': forms.EmailInput(attrs={
                **DEFAULT_TEXT_INPUT,
                'placeholder': 'example@mail.ru',
            }),
        }


# === Бронирования ===
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['client', 'room', 'checkin_date', 'checkout_date']
        widgets = {
            'client': forms.Select(attrs=DEFAULT_SELECT),
            'room': forms.Select(attrs=DEFAULT_SELECT),
            'checkin_date': forms.DateInput(
                attrs=DEFAULT_DATE_INPUT,
                format='%Y-%m-%d'
            ),
            'checkout_date': forms.DateInput(
                attrs=DEFAULT_DATE_INPUT,
                format='%Y-%m-%d'
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        room = cleaned_data.get('room')
        checkin_date = cleaned_data.get('checkin_date')
        checkout_date = cleaned_data.get('checkout_date')
        if room and checkin_date and checkout_date:
            if checkin_date >= checkout_date:
                raise ValidationError('Дата заезда должна быть раньше даты выезда.')
            if not room.is_available(checkin_date, checkout_date):
                raise ValidationError('Номер недоступен в указанные даты.')
        return cleaned_data


# === Платежи ===
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['booking', 'amount', 'payment_date', 'payment_method', 'status']
        widgets = {
            'booking': forms.Select(attrs=DEFAULT_SELECT),
            'amount': forms.NumberInput(attrs={
                **DEFAULT_NUMBER_INPUT,
                'step': '0.01',
            }),
            'payment_date': forms.DateInput(attrs=DEFAULT_DATE_INPUT),
            'payment_method': forms.Select(attrs=DEFAULT_SELECT),
            'status': forms.Select(attrs=DEFAULT_SELECT),
        }

    def clean(self):
        cleaned_data = super().clean()
        booking = cleaned_data.get('booking')
        amount = cleaned_data.get('amount')
        if booking and amount and amount > booking.total_price:
            raise ValidationError('Сумма не может превышать стоимость бронирования.')
        return cleaned_data


# === Проживания ===
class AccommodationForm(forms.ModelForm):
    class Meta:
        model = Accommodation
        fields = ['booking', 'actual_checkin_date', 'actual_checkout_date', 'status']
        widgets = {
            'booking': forms.Select(attrs=DEFAULT_SELECT),
            'actual_checkin_date': forms.DateInput(attrs=DEFAULT_DATE_INPUT),
            'actual_checkout_date': forms.DateInput(attrs=DEFAULT_DATE_INPUT),
            'status': forms.Select(attrs=DEFAULT_SELECT),
        }


# === Номера ===
class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['building', 'room_number', 'room_type', 'status']
        widgets = {
            'building': forms.Select(attrs=DEFAULT_SELECT),
            'room_number': forms.TextInput(attrs=DEFAULT_TEXT_INPUT),
            'room_type': forms.Select(attrs=DEFAULT_SELECT),
            'status': forms.Select(attrs=DEFAULT_SELECT),
        }


# === Товары и заказы ===
class ProductOrderForm(forms.ModelForm):
    class Meta:
        model = ProductOrder
        fields = ['accommodation', 'product', 'quantity']
        widgets = {
            'accommodation': forms.Select(attrs=DEFAULT_SELECT),
            'product': forms.Select(attrs=DEFAULT_SELECT),
            'quantity': forms.NumberInput(attrs=DEFAULT_NUMBER_INPUT),
        }


class BuildingProductsForm(forms.ModelForm):
    class Meta:
        model = BuildingProducts
        fields = ['building', 'product', 'is_available']
        widgets = {
            'building': forms.Select(attrs=DEFAULT_SELECT),
            'product': forms.Select(attrs=DEFAULT_SELECT),
            'is_available': forms.CheckboxInput(attrs=DEFAULT_CHECKBOX),
        }


# === Услуги и заказы ===
class ServiceOrderForm(forms.ModelForm):
    class Meta:
        model = ServiceOrder
        fields = ['accommodation', 'service']
        widgets = {
            'accommodation': forms.Select(attrs=DEFAULT_SELECT),
            'service': forms.Select(attrs=DEFAULT_SELECT),
        }


class BuildingServicesForm(forms.ModelForm):
    class Meta:
        model = BuildingServices
        fields = ['building', 'service', 'is_active']
        widgets = {
            'building': forms.Select(attrs=DEFAULT_SELECT),
            'service': forms.Select(attrs=DEFAULT_SELECT),
            'is_active': forms.CheckboxInput(attrs=DEFAULT_CHECKBOX),
        }


# === Сотрудники и должности ===
class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'middle_name', 'phone', 'building', 'positions']
        widgets = {
            'first_name': forms.TextInput(attrs=DEFAULT_TEXT_INPUT),
            'last_name': forms.TextInput(attrs=DEFAULT_TEXT_INPUT),
            'middle_name': forms.TextInput(attrs=DEFAULT_TEXT_INPUT),
            'phone': forms.TextInput(attrs={
                **DEFAULT_TEXT_INPUT,
                'data-mask': 'phone',
                'placeholder': '+7 (___) ___-__-__',
            }),
            'building': forms.Select(attrs=DEFAULT_SELECT),
            'positions': forms.SelectMultiple(attrs=DEFAULT_SELECT),
        }


class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs=DEFAULT_TEXT_INPUT),
        }


# === Здания и адреса ===
class BuildingForm(forms.ModelForm):
    class Meta:
        model = Building
        fields = ['name', 'description', 'capacity', 'address']
        labels = {
            'name': 'Название здания',
        }
        widgets = {
            'name': forms.TextInput(attrs=DEFAULT_TEXT_INPUT),
            'description': forms.Textarea(attrs=DEFAULT_TEXTAREA),
            'capacity': forms.NumberInput(attrs=DEFAULT_NUMBER_INPUT),
            'address': forms.Select(attrs=DEFAULT_SELECT),
        }


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['city', 'street', 'house']
        widgets = {
            'city': forms.TextInput(attrs=DEFAULT_TEXT_INPUT),
            'street': forms.TextInput(attrs=DEFAULT_TEXT_INPUT),
            'house': forms.TextInput(attrs=DEFAULT_TEXT_INPUT),
        }