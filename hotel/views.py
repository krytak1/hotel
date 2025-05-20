from django.http import HttpResponse
import csv

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, redirect


from django.db.models import Avg, Count
from django.utils import timezone
from django.views import View
from django.views.generic.edit import FormView
from django.views.generic import ListView, CreateView, UpdateView, DetailView, TemplateView, DeleteView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.urls import reverse_lazy
from django.db.models import Q
import datetime
from django.db.models import Sum

from .models import Client, Service, Product, Booking, Payment, Room, ProductOrder, ServiceOrder, Accommodation, BuildingProducts, BuildingServices, Building, Employee, Position, Address
  # и другие модели, если нужно
from .forms import BuildingForm, AccommodationForm, ClientForm, BookingForm, PaymentForm, ProductOrderForm, ServiceOrderForm, EmployeeForm, PositionForm, BuildingProductsForm, BuildingServicesForm, RoomForm, AddressForm


class ProtectedView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'


class ClientListView(ProtectedView, ListView):
    model = Client
    template_name = 'hotel/client_list.html'
    context_object_name = 'clients'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q) |
                Q(phone__icontains=q) |
                Q(email__icontains=q) |
                Q(passport_data__icontains=q)
            )
        return qs


class ClientCreateView(ProtectedView, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'hotel/client_form.html'
    success_url = reverse_lazy('client_list')


class ClientUpdateView(ProtectedView, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'hotel/client_form.html'
    success_url = reverse_lazy('client_list')


class ClientDetailView(ProtectedView, DetailView):
    model = Client
    template_name = 'hotel/client_detail.html'
    context_object_name = 'client'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        client = self.object
        ctx['bookings'] = Booking.objects.filter(client=client).order_by('-created_at')
        return ctx


class BookingListView(ProtectedView, ListView):
    model = Booking
    template_name = 'hotel/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 10

class BookingCreateView(ProtectedView, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'hotel/booking_form.html'
    success_url = reverse_lazy('booking_list')

class BookingUpdateView(ProtectedView, UpdateView):
    model = Booking
    form_class = BookingForm
    template_name = 'hotel/booking_form.html'
    success_url = reverse_lazy('booking_list')

class BookingDetailView(ProtectedView, DetailView):
    model = Booking
    template_name = 'hotel/booking_detail.html'
    context_object_name = 'booking'

class BookingCancelView(ProtectedView, View):
    def post(self, request, pk):
        b = get_object_or_404(Booking, pk=pk)
        b.status = 'Отменен'
        b.save()
        return redirect('booking_list')

class CheckInView(ProtectedView, View):
    def post(self, request, pk):
        b = get_object_or_404(Booking, pk=pk, status='Подтвержден')
        Accommodation.objects.create(
            booking=b,
            actual_checkin_date=timezone.now().date()
        )
        return redirect('booking_detail', pk=pk)

class CheckOutView(ProtectedView, View):
    def post(self, request, pk):
        a = get_object_or_404(Accommodation, booking_id=pk)
        a.actual_checkout_date = timezone.now().date()
        a.status = 'Выехал'
        a.save()
        return redirect('booking_detail', pk=pk)

class PaymentCreateView(ProtectedView, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'hotel/payment_form.html'
    success_url = reverse_lazy('payment_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление платежа'
        return context

class PaymentListView(ProtectedView, ListView):
    model = Payment
    template_name = 'hotel/payment_list.html'
    context_object_name = 'payments'

    def get_queryset(self):
        qs = super().get_queryset().select_related('booking', 'booking__client')

        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(booking__client__first_name__icontains=q) |
                Q(booking__client__last_name__icontains=q) |
                Q(payment_method__icontains=q) |
                Q(status__icontains=q)
            )
        return qs.order_by('-payment_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Платежи и отчёты'
        context['total_paid'] = self.get_queryset().aggregate(Sum('amount'))['amount__sum'] or 0
        # Исправленная строка для неоплаченных броней
        context['unpaid_bookings'] = Booking.objects.filter(payments__isnull=True)
        return context



class OrderListView(ProtectedView, ListView):
    template_name = 'hotel/order_list.html'
    context_object_name = 'accommodation'

    def get_queryset(self):
        return Accommodation.objects.select_related('booking__client').get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        accommodation = self.get_queryset()
        context['title'] = 'Заказы по проживанию'
        context['product_orders'] = ProductOrder.objects.filter(accommodation=accommodation)
        context['service_orders'] = ServiceOrder.objects.filter(accommodation=accommodation)
        return context


class AccommodationListView(ProtectedView, ListView):
    model = Accommodation
    template_name = 'hotel/accommodation_list.html'
    context_object_name = 'accommodations'

class InventoryListView(ProtectedView, TemplateView):
    template_name = 'hotel/inventory_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Для примера берём первую гостиницу.
        # В реальном приложении, конечно, нужно передавать ID от текущего пользователя/сессии
        building = Building.objects.first()
        context['products'] = BuildingProducts.objects.filter(building=building)
        context['services'] = BuildingServices.objects.filter(building=building)
        return context



class EmployeeListView(ProtectedView, ListView):
    model = Employee
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        pos = self.request.GET.get('position')
        if pos:
            qs = qs.filter(positions__id=pos)
        return qs

class EmployeeCreateView(ProtectedView, CreateView):
    model = Employee
    form_class = EmployeeForm
    success_url = reverse_lazy('employee_list')

class EmployeeUpdateView(ProtectedView, UpdateView):
    model = Employee
    form_class = EmployeeForm
    success_url = reverse_lazy('employee_list')

class EmployeeDeleteView(ProtectedView, DeleteView):
    model = Employee
    success_url = reverse_lazy('employee_list')

# CRUD для должностей
class PositionListView(ProtectedView, ListView):
    model = Position

class PositionCreateView(ProtectedView, CreateView):
    model = Position
    form_class = PositionForm
    success_url = reverse_lazy('position_list')

class PositionUpdateView(ProtectedView, UpdateView):
    model = Position
    form_class = PositionForm
    success_url = reverse_lazy('position_list')

class PositionDeleteView(ProtectedView, DeleteView):
    model = Position
    success_url = reverse_lazy('position_list')

# Экспорт сотрудников в CSV
@login_required
def export_employees_csv(request):
    qs = Employee.objects.select_related('building').prefetch_related('positions')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="employees.csv"'
    writer = csv.writer(response)
    writer.writerow(['ФИО', 'Телефон', 'Отель', 'Должности'])
    for emp in qs:
        writer.writerow([
            emp.get_full_name(),
            emp.phone,
            emp.building.name,
            ", ".join(p.name for p in emp.positions.all())
        ])
    return response




class AnalyticsDashboardView(ProtectedView, TemplateView):
    template_name = 'hotel/analytics.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = timezone.now().date()
        period_start = today - timezone.timedelta(days=30)

        # Загрузка номеров
        total_rooms = Room.objects.count()
        occupied = Booking.objects.filter(
            status__in=['Подтвержден','Оплачен'],
            checkin_date__lte=today, checkout_date__gt=today
        ).count()
        ctx['occupancy_rate'] = round(occupied / total_rooms * 100, 2) if total_rooms else 0

        # Финансы за месяц
        payments = Payment.objects.filter(payment_date__gte=period_start)
        ctx['monthly_revenue'] = payments.aggregate(total=Sum('amount'))['total'] or 0



        # Данные для графиков (например, доходы по дням)
        daily = payments.annotate(day=TruncDay('payment_date')).values('day') \
                        .annotate(sum=Sum('amount')).order_by('day')
        ctx['daily_payments'] = list(daily)
        return ctx



class ProductOrderListView(ProtectedView, ListView):
    model = ProductOrder
    template_name = 'hotel/productorder_list.html'
    context_object_name = 'product_orders'
    paginate_by = 10  # Указываем количество элементов на странице

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Пагинация
        paginator = Paginator(ProductOrder.objects.all(), 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context

class ProductOrderCreateView(ProtectedView, CreateView):
    model = ProductOrder
    form_class = ProductOrderForm
    template_name = 'hotel/productorder_form.html'
    success_url = reverse_lazy('productorder_list')


# --- Остатки товаров (BuildingProducts) ---
class BuildingProductsListView(ProtectedView, ListView):
    model = BuildingProducts
    template_name = 'hotel/buildingproducts_list.html'
    paginate_by = 20

class BuildingProductsUpdateView(ProtectedView, UpdateView):
    model = BuildingProducts
    form_class = BuildingProductsForm
    template_name = 'hotel/buildingproducts_form.html'
    success_url = reverse_lazy('buildingproducts_list')

# --- Доступность услуг (BuildingServices) ---
class BuildingServicesListView(ProtectedView, ListView):
    model = BuildingServices
    template_name = 'hotel/buildingservices_list.html'
    paginate_by = 20

class BuildingServicesUpdateView(ProtectedView, UpdateView):
    model = BuildingServices
    form_class = BuildingServicesForm
    template_name = 'hotel/buildingservices_form.html'
    success_url = reverse_lazy('buildingservices_list')

# --- Заказы услуг (ServiceOrder) ---
class ServiceOrderListView(ProtectedView, ListView):
    model = ServiceOrder
    template_name = 'hotel/serviceorder_list.html'
    paginate_by = 20

class ServiceOrderCreateView(ProtectedView, CreateView):
    model = ServiceOrder
    form_class = ServiceOrderForm
    template_name = 'hotel/serviceorder_form.html'
    success_url = reverse_lazy('serviceorder_list')

# --- Должности (Position) ---
class PositionListView(ProtectedView, ListView):
    model = Position
    template_name = 'hotel/position_list.html'
    paginate_by = 20

class PositionCreateView(ProtectedView, CreateView):
    model = Position
    form_class = PositionForm
    template_name = 'hotel/position_form.html'
    success_url = reverse_lazy('position_list')

class PositionUpdateView(ProtectedView, UpdateView):
    model = Position
    form_class = PositionForm
    template_name = 'hotel/position_form.html'
    success_url = reverse_lazy('position_list')

class PositionDeleteView(ProtectedView, DeleteView):
    model = Position
    template_name = 'hotel/position_confirm_delete.html'
    success_url = reverse_lazy('position_list')

# --- Сотрудники (Employee) ---
class EmployeeListView(ProtectedView, ListView):
    model = Employee
    template_name = 'hotel/employee_list.html'
    paginate_by = 20

class EmployeeCreateView(ProtectedView, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'hotel/employee_form.html'
    success_url = reverse_lazy('employee_list')

class EmployeeUpdateView(ProtectedView, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'hotel/employee_form.html'
    success_url = reverse_lazy('employee_list')

class EmployeeDeleteView(ProtectedView, DeleteView):
    model = Employee
    template_name = 'hotel/employee_confirm_delete.html'
    success_url = reverse_lazy('employee_list')



class DashboardView(ProtectedView, TemplateView):
    template_name = 'hotel/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = timezone.localdate()
        week_ago = today - datetime.timedelta(days=7)

        ctx['active_bookings_count'] = Booking.objects.filter(
            status__in=['Подтвержден', 'Оплачен']
        ).count()
        ctx['free_rooms_count'] = Room.objects.filter(status='Свободен').count()
        ctx['checked_in_today_count'] = Accommodation.objects.filter(
            actual_checkin_date=today
        ).count()
        ctx['weekly_revenue'] = Booking.objects.filter(
            status__in=['Оплачен', 'Завершен'],
            created_at__date__gte=week_ago
        ).aggregate(total=Sum('total_price'))['total'] or 0

        # Срез ближайших заселений (по дате заезда)
        ctx['upcoming_bookings'] = Booking.objects.filter(
            status='Подтвержден',
            checkin_date__gte=today
        ).order_by('checkin_date')[:5]


        return ctx

class RoomListView(ProtectedView, ListView):
    model = Room
    template_name = 'hotel/room_list.html'
    context_object_name = 'rooms'
    paginate_by = 20

class RoomCreateView(ProtectedView, CreateView):
    model = Room
    form_class = RoomForm
    template_name = 'hotel/room_form.html'
    success_url = reverse_lazy('room_list')

class RoomUpdateView(ProtectedView, UpdateView):
    model = Room
    form_class = RoomForm
    template_name = 'hotel/room_form.html'
    success_url = reverse_lazy('room_list')






class EmployeeExportView(ProtectedView, View):
    """
    Экспорт списка сотрудников в CSV.
    """
    def get(self, request, *args, **kwargs):
        # Подготовка HTTP-ответа с CSV
        response = HttpResponse(
            content_type='text/csv; charset=utf-8',
        )
        response['Content-Disposition'] = 'attachment; filename="employees.csv"'

        writer = csv.writer(response)
        # Заголовки столбцов
        writer.writerow(['ФИО', 'Телефон', 'Гостиница', 'Должности'])

        # Строки с данными
        for emp in Employee.objects.select_related('building').prefetch_related('positions').all():
            fio = f"{emp.last_name} {emp.first_name} {emp.middle_name}"
            positions = ', '.join(p.name for p in emp.positions.all())
            writer.writerow([fio, emp.phone, emp.building.name, positions])

        return response






class GlobalSearchView(ProtectedView, ListView):
    template_name = 'search_results.html'
    context_object_name = 'results'

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        return Client.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(middle_name__icontains=query)
        )



class BuildingListView(ListView):
    model = Building
    template_name = 'hotel/building_list.html'
    context_object_name = 'buildings'


class BuildingCreateView(CreateView):
    model = Building
    form_class = BuildingForm
    template_name = 'hotel/building_form.html'
    success_url = reverse_lazy('building_list')


class BuildingUpdateView(UpdateView):
    model = Building
    form_class = BuildingForm
    template_name = 'hotel/building_form.html'
    success_url = reverse_lazy('building_list')


class AddressListView(ListView):
    model = Address
    template_name = 'hotel/address_list.html'
    context_object_name = 'addresses'

class AddressCreateView(CreateView):
    model = Address
    form_class = AddressForm
    template_name = 'hotel/address_form.html'
    success_url = reverse_lazy('address_list')

class AddressUpdateView(UpdateView):
    model = Address
    form_class = AddressForm
    template_name = 'hotel/address_form.html'
    success_url = reverse_lazy('address_list')



class InventoryOrderListView(ProtectedView, TemplateView):
    template_name = 'hotel/inventory_orders.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        period_start = timezone.now().date() - datetime.timedelta(days=30)

        # Получаем заказы товаров за 30 дней
        raw_product_orders = ProductOrder.objects.filter(
            order_date__gte=period_start
        ).select_related('accommodation__booking__client', 'product', 'accommodation__booking__room__building')

        # Для каждого заказа заранее находим соответствующий запас
        product_orders = []
        for o in raw_product_orders:
            building = o.accommodation.booking.room.building
            try:
                stock = BuildingProducts.objects.get(product=o.product, building=building)
            except BuildingProducts.DoesNotExist:
                stock = None
            product_orders.append({
                'order': o,
                'stock': stock,
            })

        # Заказы услуг
        service_orders = ServiceOrder.objects.filter(
            order_date__gte=period_start
        ).select_related('accommodation__booking__client', 'service')

        # Статистика
        ctx.update({
            'product_orders': product_orders,
            'service_orders': service_orders,
            'total_product_orders': len(product_orders),
            'total_service_orders': service_orders.count(),
            'out_of_stock_count': BuildingProducts.objects.filter(available__lte=0).count(),
        })
        return ctx







class ProductOrderCreateView(ProtectedView, CreateView):
    model = ProductOrder
    form_class = ProductOrderForm
    template_name = 'hotel/productorder_form.html'
    success_url = reverse_lazy('inventory_orders')


class ProductOrderUpdateView(ProtectedView, UpdateView):
    model = ProductOrder
    form_class = ProductOrderForm
    template_name = 'hotel/productorder_form.html'
    def get_success_url(self):
        return reverse('inventory_orders')

class ProductOrderDeleteView(ProtectedView, DeleteView):
    model = ProductOrder
    template_name = 'hotel/productorder_confirm_delete.html'
    success_url = reverse_lazy('inventory_orders')

class ServiceOrderCreateView(ProtectedView, CreateView):
    model = ServiceOrder
    form_class = ServiceOrderForm
    template_name = 'hotel/serviceorder_form.html'
    success_url = reverse_lazy('inventory_orders')


class ServiceOrderUpdateView(ProtectedView, UpdateView):
    model = ServiceOrder
    form_class = ServiceOrderForm
    template_name = 'hotel/serviceorder_form.html'
    def get_success_url(self):
        return reverse('inventory_orders')

class ServiceOrderDeleteView(ProtectedView, DeleteView):
    model = ServiceOrder
    template_name = 'hotel/serviceorder_confirm_delete.html'
    success_url = reverse_lazy('inventory_orders')



# --- Products CRUD ---
class ProductListView(ProtectedView, ListView):
    model = Product
    template_name = 'hotel/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

class ProductCreateView(ProtectedView, CreateView):
    model = Product
    fields = ['name', 'description', 'price']
    template_name = 'hotel/product_form.html'
    success_url = reverse_lazy('product_list')

class ProductUpdateView(ProtectedView, UpdateView):
    model = Product
    fields = ['name', 'description', 'price']
    template_name = 'hotel/product_form.html'
    success_url = reverse_lazy('product_list')

class ProductDeleteView(ProtectedView, DeleteView):
    model = Product
    template_name = 'hotel/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')

# --- Services CRUD ---
class ServiceListView(ProtectedView, ListView):
    model = Service
    template_name = 'hotel/service_list.html'
    context_object_name = 'services'
    paginate_by = 10

class ServiceCreateView(ProtectedView, CreateView):
    model = Service
    fields = ['name', 'description', 'price']
    template_name = 'hotel/service_form.html'
    success_url = reverse_lazy('service_list')

class ServiceUpdateView(ProtectedView, UpdateView):
    model = Service
    fields = ['name', 'description', 'price']
    template_name = 'hotel/service_form.html'
    success_url = reverse_lazy('service_list')

class ServiceDeleteView(ProtectedView, DeleteView):
    model = Service
    template_name = 'hotel/service_confirm_delete.html'
    success_url = reverse_lazy('service_list')



class AccommodationListView(ProtectedView, ListView):
    model = Accommodation
    template_name = 'hotel/accommodations_list.html'
    context_object_name = 'accommodations'

class AccommodationCreateView(ProtectedView, CreateView):
    model = Accommodation
    form_class = AccommodationForm
    template_name = 'hotel/accommodation_form.html'
    success_url = reverse_lazy('accommodation_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view'] = self
        self.title = 'Добавить проживание'
        return context

class AccommodationUpdateView(ProtectedView, UpdateView):
    model = Accommodation
    form_class = AccommodationForm
    template_name = 'hotel/accommodation_form.html'
    success_url = reverse_lazy('accommodation_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view'] = self
        self.title = 'Редактировать проживание'
        return context

class AccommodationDeleteView(ProtectedView, DeleteView):
    model = Accommodation
    template_name = 'hotel/accommodation_confirm_delete.html'
    success_url = reverse_lazy('accommodation_list')


class ClientDeleteView(DeleteView):
    model = Client
    success_url = reverse_lazy('client_list')
    template_name = 'hotel/instant_delete.html'


class BuildingDeleteView(DeleteView):
    model = Building
    success_url = reverse_lazy('building_list')
    template_name = 'hotel/instant_delete.html'


class AddressDeleteView(DeleteView):
    model = Address
    success_url = reverse_lazy('address_list')
    template_name = 'hotel/instant_delete.html'


class RoomDeleteView(DeleteView):
    model = Room
    success_url = reverse_lazy('room_list')
    template_name = 'hotel/instant_delete.html'


class AccommodationDeleteView(DeleteView):
    model = Accommodation
    success_url = reverse_lazy('accommodation_list')
    template_name = 'hotel/instant_delete.html'

