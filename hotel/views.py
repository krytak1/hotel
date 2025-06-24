from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.generic import (
    ListView, CreateView, UpdateView, DetailView, TemplateView, DeleteView
)
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Q, Sum
from django.db.models.functions import TruncDay

import csv
import datetime

from .models import (
    Client, Service, Product, Booking, Payment, Room, ProductOrder, ServiceOrder,
    Accommodation, BuildingProducts, BuildingServices, Building, Employee, Position, Address
)
from .forms import (
    BuildingForm, AccommodationForm, ClientForm, BookingForm, PaymentForm,
    ProductOrderForm, ServiceOrderForm, EmployeeForm, PositionForm,
    BuildingProductsForm, BuildingServicesForm, RoomForm, AddressForm
)


class ProtectedView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'


# === Клиенты ===
class ClientListView(ProtectedView, ListView):
    model = Client
    template_name = 'hotel/client_list.html'
    context_object_name = 'clients'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(passport_data__icontains=search_query)
            )
        return queryset


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
        context = super().get_context_data(**kwargs)
        context['bookings'] = Booking.objects.filter(client=self.object).order_by('-created_at')
        return context


class ClientDeleteView(ProtectedView, DeleteView):
    model = Client
    template_name = 'hotel/instant_delete.html'
    success_url = reverse_lazy('client_list')


# === Бронирования ===
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
        booking = get_object_or_404(Booking, pk=pk)
        booking.status = 'Отменен'
        booking.save()
        return redirect('booking_list')


class CheckInView(ProtectedView, View):
    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk, status='Подтвержден')
        Accommodation.objects.create(
            booking=booking,
            actual_checkin_date=timezone.now().date()
        )
        return redirect('booking_detail', pk=pk)


class CheckOutView(ProtectedView, View):
    def post(self, request, pk):
        accommodation = get_object_or_404(Accommodation, booking_id=pk)
        accommodation.actual_checkout_date = timezone.now().date()
        accommodation.status = 'Выехал'
        accommodation.save()
        return redirect('booking_detail', pk=pk)


# === Платежи ===
class PaymentListView(ProtectedView, ListView):
    model = Payment
    template_name = 'hotel/payment_list.html'
    context_object_name = 'payments'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('booking', 'booking__client')
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(booking__client__first_name__icontains=search_query) |
                Q(booking__client__last_name__icontains=search_query) |
                Q(payment_method__icontains=search_query) |
                Q(status__icontains=search_query)
            )
        return queryset.order_by('-payment_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Платежи и отчёты'
        context['total_paid'] = self.get_queryset().aggregate(Sum('amount'))['amount__sum'] or 0
        context['unpaid_bookings'] = Booking.objects.filter(payments__isnull=True)
        return context


class PaymentCreateView(ProtectedView, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'hotel/payment_form.html'
    success_url = reverse_lazy('payment_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление платежа'
        return context


# === Проживания ===
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
        context['title'] = 'Добавить проживание'
        return context


class AccommodationUpdateView(ProtectedView, UpdateView):
    model = Accommodation
    form_class = AccommodationForm
    template_name = 'hotel/accommodation_form.html'
    success_url = reverse_lazy('accommodation_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактировать проживание'
        return context


class AccommodationDeleteView(ProtectedView, DeleteView):
    model = Accommodation
    template_name = 'hotel/accommodation_confirm_delete.html'
    success_url = reverse_lazy('accommodation_list')


# === Номера ===
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


class RoomDeleteView(ProtectedView, DeleteView):
    model = Room
    template_name = 'hotel/instant_delete.html'
    success_url = reverse_lazy('room_list')


# === Товары ===
class ProductListView(ProtectedView, ListView):
    model = Product
    template_name = 'hotel/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        building = Building.objects.first()
        products_with_availability = []
        for product in context['products']:
            try:
                stock = BuildingProducts.objects.get(product=product, building=building)
                is_available = stock.is_available
            except BuildingProducts.DoesNotExist:
                stock = None
                is_available = False
            products_with_availability.append({
                'product': product,
                'stock': stock,
                'is_available': is_available
            })
        context['products'] = products_with_availability
        return context


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


# === Услуги ===
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


# === Заказы товаров ===
class ProductOrderListView(ProtectedView, ListView):
    model = ProductOrder
    template_name = 'hotel/productorder_list.html'
    context_object_name = 'product_orders'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(ProductOrder.objects.all(), 10)
        page_number = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)
        return context


class ProductOrderCreateView(ProtectedView, CreateView):
    model = ProductOrder
    form_class = ProductOrderForm
    template_name = 'hotel/productorder_form.html'
    success_url = reverse_lazy('inventory_orders')

    def form_valid(self, form):
        product = form.cleaned_data['product']
        building = Building.objects.first()
        try:
            stock = BuildingProducts.objects.get(product=product, building=building)
            if not stock.is_available:
                form.add_error('product', 'Этот товар недоступен для заказа.')
                return self.form_invalid(form)
        except BuildingProducts.DoesNotExist:
            form.add_error('product', 'Информация о наличии товара отсутствует.')
            return self.form_invalid(form)
        return super().form_valid(form)


class ProductOrderUpdateView(ProtectedView, UpdateView):
    model = ProductOrder
    form_class = ProductOrderForm
    template_name = 'hotel/productorder_form.html'
    success_url = reverse_lazy('inventory_orders')


class ProductOrderDeleteView(ProtectedView, DeleteView):
    model = ProductOrder
    template_name = 'hotel/product_confirm_delete.html'
    success_url = reverse_lazy('inventory_orders')


# === Заказы услуг ===
class ServiceOrderListView(ProtectedView, ListView):
    model = ServiceOrder
    template_name = 'hotel/serviceorder_list.html'
    paginate_by = 20


class ServiceOrderCreateView(ProtectedView, CreateView):
    model = ServiceOrder
    form_class = ServiceOrderForm
    template_name = 'hotel/serviceorder_form.html'
    success_url = reverse_lazy('inventory_orders')


class ServiceOrderUpdateView(ProtectedView, UpdateView):
    model = ServiceOrder
    form_class = ServiceOrderForm
    template_name = 'hotel/serviceorder_form.html'
    success_url = reverse_lazy('inventory_orders')


class ServiceOrderDeleteView(ProtectedView, DeleteView):
    model = ServiceOrder
    template_name = 'hotel/service_confirm_delete.html'
    success_url = reverse_lazy('inventory_orders')


# === Инвентарь ===
class InventoryListView(ProtectedView, TemplateView):
    template_name = 'hotel/inventory_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        building = Building.objects.first()
        context['products'] = BuildingProducts.objects.filter(building=building)
        context['services'] = BuildingServices.objects.filter(building=building)
        return context


class InventoryOrderListView(ProtectedView, ListView):
    template_name = 'hotel/inventory_orders.html'
    context_object_name = 'product_orders'

    def get_queryset(self):
        building = Building.objects.first()
        product_orders = ProductOrder.objects.select_related(
            'product', 'accommodation__booking__client', 'accommodation__booking__room__building'
        ).all()
        service_orders = ServiceOrder.objects.select_related(
            'service', 'accommodation__booking__client'
        ).all()
        combined_orders = []
        for order in product_orders:
            building = order.accommodation.booking.room.building
            try:
                stock = BuildingProducts.objects.get(product=order.product, building=building)
                is_available = stock.is_available
            except BuildingProducts.DoesNotExist:
                stock = None
                is_available = False
            combined_orders.append({
                'order': order,
                'stock': stock,
                'is_service': False,
                'is_available': is_available
            })
        for order in service_orders:
            combined_orders.append({
                'order': order,
                'stock': None,
                'is_service': True,
                'is_available': True
            })
        return combined_orders

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_orders'] = self.get_queryset()
        return context


# === Остатки товаров ===
class BuildingProductsListView(ProtectedView, ListView):
    model = BuildingProducts
    template_name = 'hotel/buildingproducts_list.html'
    paginate_by = 20


class BuildingProductsUpdateView(ProtectedView, UpdateView):
    model = BuildingProducts
    form_class = BuildingProductsForm
    template_name = 'hotel/buildingproducts_form.html'
    success_url = reverse_lazy('product_list')


# === Доступность услуг ===
class BuildingServicesListView(ProtectedView, ListView):
    model = BuildingServices
    template_name = 'hotel/buildingservices_list.html'
    paginate_by = 20


class BuildingServicesUpdateView(ProtectedView, UpdateView):
    model = BuildingServices
    form_class = BuildingServicesForm
    template_name = 'hotel/buildingservices_form.html'
    success_url = reverse_lazy('buildingservices_list')


# === Сотрудники ===
class EmployeeListView(ProtectedView, ListView):
    model = Employee
    template_name = 'hotel/employee_list.html'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        position_id = self.request.GET.get('position')
        if position_id:
            queryset = queryset.filter(positions__id=position_id)
        return queryset


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


class EmployeeExportView(ProtectedView, View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="employees.csv"'
        writer = csv.writer(response)
        writer.writerow(['ФИО', 'Телефон', 'Гостиница', 'Должности'])
        for emp in Employee.objects.select_related('building').prefetch_related('positions').all():
            fio = f"{emp.last_name} {emp.first_name} {emp.middle_name}"
            positions = ', '.join(p.name for p in emp.positions.all())
            writer.writerow([fio, emp.phone, emp.building.name, positions])
        return response


# === Должности ===
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


# === Гостиницы ===
class BuildingListView(ProtectedView, ListView):
    model = Building
    template_name = 'hotel/building_list.html'
    context_object_name = 'buildings'


class BuildingCreateView(ProtectedView, CreateView):
    model = Building
    form_class = BuildingForm
    template_name = 'hotel/building_form.html'
    success_url = reverse_lazy('building_list')


class BuildingUpdateView(ProtectedView, UpdateView):
    model = Building
    form_class = BuildingForm
    template_name = 'hotel/building_form.html'
    success_url = reverse_lazy('building_list')


class BuildingDeleteView(ProtectedView, DeleteView):
    model = Building
    template_name = 'hotel/instant_delete.html'
    success_url = reverse_lazy('building_list')


# === Адреса ===
class AddressListView(ProtectedView, ListView):
    model = Address
    template_name = 'hotel/address_list.html'
    context_object_name = 'addresses'


class AddressCreateView(ProtectedView, CreateView):
    model = Address
    form_class = AddressForm
    template_name = 'hotel/address_form.html'
    success_url = reverse_lazy('address_list')


class AddressUpdateView(ProtectedView, UpdateView):
    model = Address
    form_class = AddressForm
    template_name = 'hotel/address_form.html'
    success_url = reverse_lazy('address_list')


class AddressDeleteView(ProtectedView, DeleteView):
    model = Address
    template_name = 'hotel/instant_delete.html'
    success_url = reverse_lazy('address_list')


# === Аналитика ===
class AnalyticsDashboardView(ProtectedView, TemplateView):
    template_name = 'hotel/analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        period_start = today - timezone.timedelta(days=30)

        total_rooms = Room.objects.count()
        occupied = Booking.objects.filter(
            status__in=['Подтвержден', 'Оплачен'],
            checkin_date__lte=today,
            checkout_date__gt=today
        ).count()
        context['occupancy_rate'] = round(occupied / total_rooms * 100, 2) if total_rooms else 0

        payments = Payment.objects.filter(payment_date__gte=period_start)
        context['monthly_revenue'] = payments.aggregate(total=Sum('amount'))['total'] or 0

        daily = payments.annotate(day=TruncDay('payment_date')).values('day') \
            .annotate(sum=Sum('amount')).order_by('day')
        context['daily_payments'] = list(daily)
        return context


# === Панель управления ===
class DashboardView(ProtectedView, TemplateView):
    template_name = 'hotel/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        week_ago = today - datetime.timedelta(days=7)

        context['active_bookings_count'] = Booking.objects.filter(
            status__in=['Подтвержден', 'Оплачен']
        ).count()
        context['free_rooms_count'] = Room.objects.filter(status='Свободен').count()
        context['checked_in_today_count'] = Accommodation.objects.filter(
            actual_checkin_date=today
        ).count()
        context['weekly_revenue'] = Booking.objects.filter(
            status__in=['Оплачен', 'Завершен'],
            created_at__date__gte=week_ago
        ).aggregate(total=Sum('total_price'))['total'] or 0
        context['upcoming_bookings'] = Booking.objects.filter(
            status='Подтвержден',
            checkin_date__gte=today
        ).order_by('checkin_date')[:5]
        return context


# === Обновление доступности товаров ===
@require_POST
@login_required
def update_availability(request):
    product_id = request.POST.get('product_id')
    is_available = request.POST.get('is_available') == 'true'
    building = Building.objects.first()
    try:
        product = Product.objects.get(pk=product_id)
        stock, created = BuildingProducts.objects.get_or_create(product=product, building=building)
        stock.is_available = is_available
        stock.save()
        return JsonResponse({'status': 'success', 'is_available': is_available})
    except Product.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)

