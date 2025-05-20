from django.urls import path
from . import views
from .views import GlobalSearchView

urlpatterns = [
    # --- Dashboard ---
    path('', views.DashboardView.as_view(), name='dashboard'),

    # --- Клиенты ---
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/add/', views.ClientCreateView.as_view(), name='client_add'),
    path('clients/<int:pk>/', views.ClientDetailView.as_view(), name='client_detail'),
    path('clients/<int:pk>/edit/', views.ClientUpdateView.as_view(), name='client_edit'),

    # --- Бронирования и проживание ---
    path('bookings/', views.BookingListView.as_view(), name='booking_list'),
    path('bookings/add/', views.BookingCreateView.as_view(), name='booking_add'),
    path('bookings/<int:pk>/', views.BookingDetailView.as_view(), name='booking_detail'),
    path('bookings/<int:pk>/edit/', views.BookingUpdateView.as_view(), name='booking_edit'),
    path('bookings/<int:pk>/cancel/', views.BookingCancelView.as_view(), name='booking_cancel'),
    path('bookings/<int:pk>/checkin/', views.CheckInView.as_view(), name='booking_checkin'),
    path('bookings/<int:pk>/checkout/', views.CheckOutView.as_view(), name='booking_checkout'),
    path('accommodations/', views.AccommodationListView.as_view(), name='accommodation_list'),
    path('accommodations/add/', views.AccommodationCreateView.as_view(), name='accommodation_add'),
    path('accommodations/<int:pk>/edit/', views.AccommodationUpdateView.as_view(), name='accommodation_edit'),
    path('accommodations/<int:pk>/delete/', views.AccommodationDeleteView.as_view(), name='accommodation_delete'),



    # --- Платежи ---
    path('payments/', views.PaymentListView.as_view(), name='payment_list'),
    path('payments/add/', views.PaymentCreateView.as_view(), name='payment_add'),

    # --- Сотрудники и должности ---
    path('staff/positions/', views.PositionListView.as_view(), name='position_list'),
    path('staff/positions/add/', views.PositionCreateView.as_view(), name='position_add'),
    path('staff/positions/<int:pk>/edit/', views.PositionUpdateView.as_view(), name='position_edit'),
    path('staff/positions/<int:pk>/delete/', views.PositionDeleteView.as_view(), name='position_delete'),

    path('staff/employees/', views.EmployeeListView.as_view(), name='employee_list'),
    path('staff/employees/add/', views.EmployeeCreateView.as_view(), name='employee_add'),
    path('staff/employees/<int:pk>/edit/', views.EmployeeUpdateView.as_view(), name='employee_edit'),
    path('staff/employees/<int:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee_delete'),
    path('staff/employees/export/', views.EmployeeExportView.as_view(), name='employee_export'),

    # --- Номера ---
    path('rooms/', views.RoomListView.as_view(), name='room_list'),
    path('rooms/add/', views.RoomCreateView.as_view(), name='room_create'),
    path('rooms/<int:pk>/edit/', views.RoomUpdateView.as_view(), name='room_update'),


    # --- Здания и адреса ---
    path('buildings/', views.BuildingListView.as_view(), name='building_list'),
    path('buildings/add/', views.BuildingCreateView.as_view(), name='building_add'),
    path('buildings/<int:pk>/edit/', views.BuildingUpdateView.as_view(), name='building_edit'),

    path('addresses/', views.AddressListView.as_view(), name='address_list'),
    path('addresses/add/', views.AddressCreateView.as_view(), name='address_add'),
    path('addresses/<int:pk>/edit/', views.AddressUpdateView.as_view(), name='address_edit'),

    # --- CRUD Товары ---
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/add/', views.ProductCreateView.as_view(), name='product_add'),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),

    # --- CRUD Услуги ---
    path('services/', views.ServiceListView.as_view(), name='service_list'),
    path('services/add/', views.ServiceCreateView.as_view(), name='service_add'),
    path('services/<int:pk>/edit/', views.ServiceUpdateView.as_view(), name='service_edit'),
    path('services/<int:pk>/delete/', views.ServiceDeleteView.as_view(), name='service_delete'),


    # --- Инвентарь: заказы товаров и услуг (отдельная витрина) ---
    path('inventory/orders/', views.InventoryOrderListView.as_view(), name='inventory_orders'),
    path('inventory/orders/add/', views.ProductOrderCreateView.as_view(), name='productorder_add'),
    path('inventory/orders/<int:pk>/edit/', views.ProductOrderUpdateView.as_view(), name='productorder_edit'),
    path('inventory/orders/<int:pk>/delete/', views.ProductOrderDeleteView.as_view(), name='productorder_delete'),

    path('inventory/service-orders/', views.ServiceOrderListView.as_view(), name='serviceorder_list'),
    path('inventory/service-orders/add/', views.ServiceOrderCreateView.as_view(), name='serviceorder_add'),
    path('inventory/service-orders/<int:pk>/edit/', views.ServiceOrderUpdateView.as_view(), name='serviceorder_edit'),
    path('inventory/service-orders/<int:pk>/delete/', views.ServiceOrderDeleteView.as_view(), name='serviceorder_delete'),

    # --- Общие ---
    path('inventory/', views.InventoryListView.as_view(), name='inventory_list'),

    path('search/', GlobalSearchView.as_view(), name='global_search'),



    path('clients/<int:pk>/delete/', views.ClientDeleteView.as_view(), name='client_delete'),
    path('buildings/<int:pk>/delete/', views.BuildingDeleteView.as_view(), name='building_delete'),
    path('addresses/<int:pk>/delete/', views.AddressDeleteView.as_view(), name='address_delete'),
    path('rooms/<int:pk>/delete/', views.RoomDeleteView.as_view(), name='room_delete'),

]
