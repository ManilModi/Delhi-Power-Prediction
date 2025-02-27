from django.urls import path
from . import views
from .views import electricity_demand_plot_daily, electricity_demand_plot_hourly, cluster_residential_areas, electricity_demand_plot

urlpatterns = [
path('', views.p_home, name='home'),
# path('list', views.list_view, name='list_view'),
# path('<id>',views.detail_view, name='detail_view'),
# path('<id>/update',views.update_view, name='update_view'),
# path('<id>/delete',views.delete_view, name='delete_view'),
path('electricity_demand_daily/', views.electricity_demand_plot_daily, name='electricity-demand_daily'),
path('electricity_demand_hourly/', views.electricity_demand_plot_hourly, name='electricity-demand_hourly'),
path('residential-clusters/', views.cluster_residential_areas, name='residential_clusters'),
path('electricity_demand_plot/', views.electricity_demand_plot, name='electricity_demand_plot'),
path('register/', views.user_register, name='user_registration'),
path('login/', views.user_login, name='login'),
path('logout/', views.user_logout, name='logout'),
path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
path('govt-dashboard/', views.govt_dashboard, name='govt_dashboard'),
path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
path('createroles/', views.creatRroles, name='create_roles'),
path('create-admin-user/', views.admin_create_user, name='admin_create_user'), 
path('unauthorized/', views.unauthorized_access, name='unauthorized_access'),
path('change-superuser-password/', views.change_user_password, name='change_password'),
path('delete-user/', views.delete_user, name='delete_user'),
path('update-credentials/', views.update_credentials, name='update_credentials'),
]