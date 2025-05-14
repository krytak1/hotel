from django.urls import path
from . import views
from .views import InventoryListView, GlobalSearchView

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/add/', views.ClientCreateView.as_view(), name='client_add'),
    path('clients/<int:pk>/', views.ClientDetailView.as_view(), name='client_detail'),
    path('clients/<int:pk>/edit/', views.ClientUpdateView.as_view(), name='client_edit'),
    path('bookings/', views.BookingListView.as_view(), name='booking_list'),
    path('bookings/add/', views.BookingCreateView.as_view(), name='booking_add'),
    path('bookings/<int:pk>/', views.BookingDetailView.as_view(), name='booking_detail'),
    path('bookings/<int:pk>/edit/', views.BookingUpdateView.as_view(), name='booking_edit'),
    path('bookings/<int:pk>/cancel/', views.BookingCancelView.as_view(), name='booking_cancel'),
    path('bookings/<int:pk>/checkin/', views.CheckInView.as_view(), name='booking_checkin'),
    path('bookings/<int:pk>/checkout/', views.CheckOutView.as_view(), name='booking_checkout'),
    path('payments/', views.PaymentListView.as_view(), name='payment_list'),
    path('payments/add/', views.PaymentCreateView.as_view(), name='payment_add'),
    path('accommodation/<int:pk>/orders/products/', views.ProductOrderCreateView.as_view(), name='product_order'),
    path('accommodation/<int:pk>/orders/services/', views.ServiceOrderCreateView.as_view(), name='service_order'),
    path('accommodation/<int:pk>/orders/', views.OrderListView.as_view(), name='order_list'),
    path('accommodation/', views.AccommodationListView.as_view(), name='accommodation_list'),

    # Товары и услуги: заказы, остатки
    path('inventory/orders/', views.InventoryOrderListView.as_view(), name='inventory_orders'),
    path('inventory/orders/add/', views.ProductOrderCreateView.as_view(), name='productorder_add'),
    path('inventory/orders/<int:pk>/edit/', views.ProductOrderUpdateView.as_view(), name='productorder_edit'),
    path('inventory/orders/<int:pk>/delete/', views.ProductOrderDeleteView.as_view(), name='productorder_delete'),

    path('inventory/service-orders/', views.InventoryOrderListView.as_view(), name='inventory_orders'),
    # та же страница
    path('inventory/service-orders/add/', views.ServiceOrderCreateView.as_view(), name='serviceorder_add'),
    path('inventory/service-orders/<int:pk>/edit/', views.ServiceOrderUpdateView.as_view(), name='serviceorder_edit'),
    path('inventory/service-orders/<int:pk>/delete/', views.ServiceOrderDeleteView.as_view(),
         name='serviceorder_delete'),

    # Position
    path('staff/positions/', views.PositionListView.as_view(), name='position_list'),
    path('staff/positions/add/', views.PositionCreateView.as_view(), name='position_add'),
    path('staff/positions/<int:pk>/edit/', views.PositionUpdateView.as_view(), name='position_edit'),
    path('staff/positions/<int:pk>/delete/', views.PositionDeleteView.as_view(), name='position_delete'),

    # Employee
    path('staff/employees/', views.EmployeeListView.as_view(), name='employee_list'),
    path('staff/employees/add/', views.EmployeeCreateView.as_view(), name='employee_add'),
    path('staff/employees/<int:pk>/edit/', views.EmployeeUpdateView.as_view(), name='employee_edit'),
    path('staff/employees/<int:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee_delete'),

    path('rooms/', views.RoomListView.as_view(), name='room_list'),
    path('rooms/add/', views.RoomCreateView.as_view(), name='room_create'),
    path('rooms/<int:pk>/edit/', views.RoomUpdateView.as_view(), name='room_update'),

    # Отзывы
    path('reviews/', views.ReviewListView.as_view(), name='review_list'),
    path('reviews/add/', views.ReviewCreateView.as_view(), name='review_create'),
    path('staff/employees/export/', views.EmployeeExportView.as_view(), name='employee_export'),


    path('inventory/', views.InventoryListView.as_view(), name='inventory_list'),
    path('reports/', views.ReportListView.as_view(), name='report_list'),
    path('reports/download/', views.download_report, name='report_download'),

    path('search/', GlobalSearchView.as_view(), name='global_search'),
    path('buildings/', views.BuildingListView.as_view(), name='building_list'),
    path('buildings/add/', views.BuildingCreateView.as_view(), name='building_add'),
    path('buildings/<int:pk>/edit/', views.BuildingUpdateView.as_view(), name='building_edit'),

    path('addresses/', views.AddressListView.as_view(), name='address_list'),
    path('addresses/add/', views.AddressCreateView.as_view(), name='address_add'),
    path('addresses/<int:pk>/edit/', views.AddressUpdateView.as_view(), name='address_edit'),


]