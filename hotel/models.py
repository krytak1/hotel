from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Q


class Client(models.Model):
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    middle_name = models.CharField('Отчество', max_length=100)
    phone = models.CharField('Телефон', max_length=20, unique=True)
    email = models.EmailField('Email', max_length=100, unique=True)
    passport_data = models.CharField('Паспортные данные', max_length=50, unique=True)
    registration_date = models.DateField('Дата регистрации', default=timezone.now)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['-registration_date', 'last_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"

    def get_full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"


class RoomType(models.Model):
    name = models.CharField('Название типа', max_length=100)
    price_per_night = models.DecimalField('Стоимость за ночь', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Тип номера'
        verbose_name_plural = 'Типы номеров'

    def __str__(self):
        return f"{self.name} - {self.price_per_night} руб./ночь"


class Address(models.Model):
    city = models.CharField('Город', max_length=100)
    street = models.CharField('Улица', max_length=100)
    house = models.CharField('Номер дома', max_length=20)

    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Адреса'

    def __str__(self):
        return f"{self.city}, {self.street}, {self.house}"


class Position(models.Model):
    name = models.CharField('Название должности', max_length=100)

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField('Название товара', max_length=100)
    description = models.TextField('Описание')
    price = models.DecimalField('Стоимость', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return f"{self.name} - {self.price} руб."


class Service(models.Model):
    name = models.CharField('Название услуги', max_length=100)
    description = models.TextField('Описание')
    price = models.DecimalField('Стоимость', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'

    def __str__(self):
        return f"{self.name} - {self.price} руб."


class Building(models.Model):
    name = models.CharField('Название гостиницы', max_length=200)
    description = models.TextField('Описание здания')
    capacity = models.IntegerField('Количество мест')
    address = models.ForeignKey(Address, on_delete=models.CASCADE, verbose_name='Адрес', related_name='buildings')
    products = models.ManyToManyField(Product, through='BuildingProducts', verbose_name='Товары')
    services = models.ManyToManyField(Service, through='BuildingServices', verbose_name='Услуги')

    class Meta:
        verbose_name = 'Гостиница'
        verbose_name_plural = 'Гостиницы'

    def __str__(self):
        return self.name

    def get_available_rooms(self):
        return self.rooms.filter(status='Свободен')


class Room(models.Model):
    ROOM_STATUS_CHOICES = [
        ('Свободен', 'Свободен'),
        ('Занят', 'Занят'),
        ('На обслуживании', 'На обслуживании'),
        ('Требует уборки', 'Требует уборки'),
    ]
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, verbose_name='Тип номера', related_name='rooms')
    status = models.CharField('Статус номера', max_length=50, choices=ROOM_STATUS_CHOICES, default='Свободен')
    building = models.ForeignKey(Building, on_delete=models.CASCADE, verbose_name='Здание', related_name='rooms')
    room_number = models.CharField('Номер комнаты', max_length=20)

    class Meta:
        verbose_name = 'Номер'
        verbose_name_plural = 'Номера'
        unique_together = ['building', 'room_number']

    def __str__(self):
        return f"{self.room_number} - {self.room_type.name} ({self.status})"

    def is_available(self, checkin_date, checkout_date):
        conflicts = self.bookings.filter(
            status__in=['Подтвержден', 'Оплачен'],
            checkin_date__lt=checkout_date,
            checkout_date__gt=checkin_date
        )
        return not conflicts.exists() and self.status == 'Свободен'


class Booking(models.Model):
    BOOKING_STATUS_CHOICES = [
        ('Новый', 'Новый'),
        ('Подтвержден', 'Подтвержден'),
        ('Оплачен', 'Оплачен'),
        ('Отменен', 'Отменен'),
        ('Завершен', 'Завершен'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Клиент', related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name='Номер', related_name='bookings')
    checkin_date = models.DateField('Дата заезда')
    checkout_date = models.DateField('Дата выезда')
    total_price = models.DecimalField('Общая стоимость', max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField('Статус бронирования', max_length=50, choices=BOOKING_STATUS_CHOICES, default='Новый')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ['-created_at']

    def __str__(self):
        return f"Бронь #{self.pk} - {self.client} ({self.checkin_date} - {self.checkout_date})"

    def clean(self):
        if self.checkin_date >= self.checkout_date:
            raise ValidationError('Дата заезда должна быть раньше даты выезда')
        qs = Booking.objects.filter(
            room=self.room,
            status__in=['Подтвержден', 'Оплачен'],
            checkin_date__lt=self.checkout_date,
            checkout_date__gt=self.checkin_date
        )
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError('Номер недоступен в выбранные даты')

    def save(self, *args, **kwargs):
        delta = self.checkout_date - self.checkin_date
        days = delta.days
        self.total_price = self.room.room_type.price_per_night * days
        super().save(*args, **kwargs)


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('Наличные', 'Наличные'),
        ('Карта', 'Карта'),
        ('Онлайн', 'Онлайн'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('Оплачен', 'Оплачен'),
        ('Отменен', 'Отменен'),
        ('Возврат', 'Возврат'),
    ]
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, verbose_name='Бронирование', related_name='payments')
    amount = models.DecimalField('Сумма платежа', max_digits=10, decimal_places=2)
    payment_date = models.DateField('Дата платежа', default=timezone.now)
    payment_method = models.CharField('Метод оплаты', max_length=50, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField('Статус платежа', max_length=50, choices=PAYMENT_STATUS_CHOICES, default='Оплачен')

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-payment_date']

    def __str__(self):
        return f"Платеж {self.amount} руб. - {self.booking}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == 'Оплачен':
            self.booking.status = 'Оплачен'
            self.booking.save()


class Accommodation(models.Model):
    ACCOMMODATION_STATUS_CHOICES = [
        ('Проживает', 'Проживает'),
        ('Выехал', 'Выехал'),
    ]
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, verbose_name='Бронирование', related_name='accommodation')
    actual_checkin_date = models.DateField('Фактическая дата заезда')
    actual_checkout_date = models.DateField('Фактическая дата выезда', null=True, blank=True)
    status = models.CharField('Статус проживания', max_length=50, choices=ACCOMMODATION_STATUS_CHOICES, default='Проживает')

    class Meta:
        verbose_name = 'Проживание'
        verbose_name_plural = 'Проживания'

    def __str__(self):
        return f"Проживание для {self.booking.client} в номере {self.booking.room.room_number}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.booking.room.status = 'Занят'
            self.booking.room.save()
            self.booking.status = 'Завершен'
            self.booking.save()
        if self.status == 'Выехал' and self.actual_checkout_date:
            self.booking.room.status = 'Требует уборки'
            self.booking.room.save()


class Review(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Клиент', related_name='reviews')
    review_text = models.TextField('Текст отзыва')
    rating = models.IntegerField('Рейтинг', validators=[MinValueValidator(1), MaxValueValidator(5)])
    publication_date = models.DateField('Дата публикации', default=timezone.now)
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Бронирование', related_name='reviews')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-publication_date']

    def __str__(self):
        return f"Отзыв от {self.client} - {self.rating}/5"


class Employee(models.Model):
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    middle_name = models.CharField('Отчество', max_length=100)
    phone = models.CharField('Телефон', max_length=20, unique=True)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, verbose_name='Гостиница', related_name='employees')
    positions = models.ManyToManyField(Position, through='EmployeePositions', verbose_name='Должности', related_name='employees')

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"

    def get_full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"


class EmployeePositions(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='Сотрудник')
    position = models.ForeignKey(Position, on_delete=models.CASCADE, verbose_name='Должность')

    class Meta:
        verbose_name = 'Должность сотрудника'
        verbose_name_plural = 'Должности сотрудников'
        unique_together = ['employee', 'position']

    def __str__(self):
        return f"{self.employee} - {self.position}"


class ProductOrder(models.Model):
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE, verbose_name='Проживание', related_name='product_orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    order_date = models.DateField('Дата заказа', default=timezone.now)
    quantity = models.IntegerField('Количество', validators=[MinValueValidator(1)])
    total_price = models.DecimalField('Общая стоимость', max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        verbose_name = 'Заказ товара'
        verbose_name_plural = 'Заказы товаров'
        ordering = ['-order_date']

    def __str__(self):
        return f"Заказ {self.product.name} для {self.accommodation.booking.client.get_full_name()}"

    def save(self, *args, **kwargs):
        if self.total_price is None:
            self.total_price = self.product.price * self.quantity
        super().save(*args, **kwargs)
        try:
            hp = BuildingProducts.objects.get(product=self.product, building=self.accommodation.booking.room.building)
            if hp.available >= self.quantity:
                hp.available -= self.quantity
                hp.save()
        except BuildingProducts.DoesNotExist:
            pass


class ServiceOrder(models.Model):
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE, verbose_name='Проживание', related_name='service_orders')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name='Услуга')
    order_date = models.DateField('Дата заказа', default=timezone.now)
    total_price = models.DecimalField('Общая стоимость', max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        verbose_name = 'Заказ услуги'
        verbose_name_plural = 'Заказы услуг'
        ordering = ['-order_date']

    def __str__(self):
        return f"Заказ услуги {self.service.name} для {self.accommodation.booking.client.get_full_name()}"

    def save(self, *args, **kwargs):
        if self.total_price is None:
            self.total_price = self.service.price
        super().save(*args, **kwargs)


class BuildingProducts(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    building = models.ForeignKey(Building, on_delete=models.CASCADE, verbose_name='Гостиница')
    available = models.IntegerField('Доступное количество', validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = 'Товар в гостинице'
        verbose_name_plural = 'Товары в гостинице'
        unique_together = ['product', 'building']

    def __str__(self):
        return f"{self.product.name} в {self.building.name} - {self.available} шт."


class BuildingServices(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name='Услуга')
    building = models.ForeignKey(Building, on_delete=models.CASCADE, verbose_name='Гостиница')
    is_active = models.BooleanField('Активна', default=True)

    class Meta:
        verbose_name = 'Услуга в гостинице'
        verbose_name_plural = 'Услуги в гостинице'
        unique_together = ['service', 'building']

    def __str__(self):
        status = 'активна' if self.is_active else 'неактивна'
        return f"{self.service.name} в {self.building.name} — {status}"
