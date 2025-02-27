from django.shortcuts import render, redirect
from django.shortcuts import (get_object_or_404, render, HttpResponseRedirect)
from django.http import HttpResponse
from django.contrib.auth import login, logout,authenticate
from django.contrib import messages
from .forms import LoginForm, UserRegistrationForm,AdminUserCreationForm,PasswordChangeForm
from .forms import PasswordChangeForm, generate_random_password,DeleteCredentialForm,NormalUserCredentialUpdateForm
from django.core.mail import send_mail
from .models import Userstable, Roles,UserRole
from .decorators import role_required
import os
import folium
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from django.conf import settings
import plotly.graph_objects as go
import plotly.io as pio
 
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                user = Userstable.objects.get(username=username)
                
                if user.password == password:  # (Consider hashing passwords)
                    # Fetch the user's role
                    user_role = UserRole.objects.get(user=user)
                    role_name = user_role.role.role_names  # Get the role name

                    # Store in session
                    request.session['user_id'] = user.id
                    request.session['user_role'] = role_name

                    # Redirect based on role
                    if role_name == "Admin":
                        return redirect('admin_dashboard')
                    elif role_name == "Government Engineer":
                        return redirect('govt_dashboard')
                    else:
                        return redirect('home')
                else:
                    messages.error(request, "Invalid credentials")
            except Userstable.DoesNotExist:
                messages.error(request, "User does not exist")
            except UserRole.DoesNotExist:
                messages.error(request, "User role not assigned")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form}) 

# User Logout View
def user_logout(request):
    request.session.flush()  # Clear session
    return redirect('login')

# Dashboard Views
@role_required(allowed_roles=['Admin'])
def admin_dashboard(request):
    if 'user_id' not in request.session:
        return redirect('login')  # Force login if not authenticated
    return render(request, 'admin_dashboard.html')

@role_required(allowed_roles=['Government Engineer'])
def govt_dashboard(request):
    if 'user_id' not in request.session:
        return redirect('login')  # Force login if not authenticated
    return render(request, 'govt_dashboard.html')

@role_required(allowed_roles=['Normal User', 'Entrepreneur', 'Researcher'])
def user_dashboard(request):
    if 'user_id' not in request.session:
        return redirect('login')  # Force login if not authenticated
    return render(request, 'user_dashboard.html')

def user_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            # messages.success(request, "Account created successfully!")
            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})

def creatRroles(request):
    roles = ['Normal User', 'Entrepreneur', 'Researcher', 'Government Engineer', 'Admin']
    for role in roles:
        Roles.objects.get_or_create(role_names=role)
    return HttpResponse("<h1>Roles created successfully<h1>")


# Admin-Only View to Create Admin & Govt. Engineers
@role_required(allowed_roles=['Admin'])
def admin_create_user(request):
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            form.save()

            messages.success(request, "Admin/Govt. Engineer account created! Credentials sent via email.")
            return redirect('admin_dashboard')
    else:
        form = AdminUserCreationForm()

    return render(request, 'admin_create_user.html', {'form': form})

def unauthorized_access(request):
    return render(request, 'unauthorized.html')  # Create unauthorized.html template

@role_required(allowed_roles=['Admin'])
def change_user_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            logged_in_user = request.session.get('user_id')  # Get logged-in admin's ID

            try:
                user = Userstable.objects.get(username=username)

                # Generate a random password
                new_password = generate_random_password()

                # Update password in plain text
                user.password = new_password
                user.save()

                # Send the new password via email (only if Admin/Gov Engineer)
                send_mail(
                    subject='Your Password Has Been Updated',
                    message=f'Your new password is: {new_password}',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[username],  # Using username as email
                    fail_silently=False,
                )

                # messages.success(request, f'Password updated and emailed to {username}')

                # If the admin changed their own password, force logout and ask them to re-login
                if user.id == logged_in_user:
                    messages.warning(request, "You changed your own password. Please log in again.")
                    request.session.flush()  # Clears the session
                    return redirect('login')

                messages.success(request, f"User {username}'s password has been changed successfully.")
                return redirect('admin_dashboard')

            except Userstable.DoesNotExist:
                messages.error(request, 'User not found.')

    else:
        form = PasswordChangeForm()

    return render(request, 'change_password.html', {'form': form})

@role_required(allowed_roles=['Admin'])
def delete_user(request):
    if request.method == 'POST':
        form = DeleteCredentialForm(request.POST)
        if form.is_valid():  # Ensure validation passes before proceeding
            username = form.cleaned_data['username']
            logged_in_user_id = request.session.get('user_id')  # Current admin's ID

            try:
                user = Userstable.objects.get(username=username)

                # Ensure admin cannot delete themselves
                if user.id == logged_in_user_id:
                    messages.error(request, "You cannot delete your own credential.")
                    return redirect('delete_user')

                # Delete user credentials
                user.delete()

                # Send email notification
                send_mail(
                    subject="Your Account Has Been Deleted",
                    message=f"Hello {username},\n\nYour account has been deleted by the Admin.\n\n",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[username],  # Assuming username is email
                    fail_silently=False,
                )

                messages.success(request, f"User {username} has been deleted successfully.")
                return redirect('admin_dashboard')

            except Userstable.DoesNotExist:
                messages.error(request, "User not found.")
        else:
            # If the form is not valid, Django will handle showing the errors
            messages.error(request, "Invalid form submission. Please check the details.")
    
    else:
        form = DeleteCredentialForm()

    return render(request, 'delete_credential.html', {'form': form})

@role_required(allowed_roles=['Normal User', 'Entrepreneur', 'Researcher'])
def update_credentials(request):
    if request.method == 'POST':
        form = NormalUserCredentialUpdateForm(request.POST)
        if form.is_valid():
            new_username = form.cleaned_data.get('new_username')
            new_password = form.cleaned_data.get('new_password')
            user = Userstable.objects.get(id=request.session['user_id'])

            user.username = new_username
            user.password = new_password
            user.save()
            messages.success(request, 'Your credentials have been successfully updated.')
            user_logout(request)
            return redirect('user_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = NormalUserCredentialUpdateForm()

    return render(request, 'update_credentials.html', {'form': form})

# def my_form_view(request):
#     if request.method == 'POST':
#         form = myform(request.POST)
#         if form.is_valid():
#             print('valid')
#     else:
#         form = myform()

#     return render(request, 'my_template.html', {'form': form})

# def registration_view(request):
#     if request.method == 'POST':
#         form = RegistrationForm(request.POST)
#         if form.is_valid():
#             data = form.cleaned_data
#             return render(request, 'details.html', {'data': data})
#     else:
#         form = RegistrationForm()
#     return render(request, 'registration_form.html', {'form': form})

# def create_view(request):
#     context={}

#     form=model_form(request.POST or None)
#     if form.is_valid():
#         return render(request, "message.html")
#         form.save()
#     context['form']=form
#     return render(request, "create_view.html", context)

# def list_view(request):

#     context ={}
#     context["dataset"] = my_model.objects.all()
#     return render(request, "list_view.html", context)


# def detail_view(request, id):
#     context ={}
#     context["data"] = my_model.objects.get(id = id)
#     return render(request, "detail_view.html", context)


# def update_view(request, id):

#     context ={}
#     obj = get_object_or_404(my_model, id = id)
#     form = model_form(request.POST or None, instance = obj)

#     if form.is_valid():
#         return render(request, "message.html")
#         form.save()
#         return HttpResponseRedirect("/myapp/"+id)

#     context["form"] = form
#     return render(request, "update_view.html", context)


# def delete_view(request, id):
#     context ={}
#     obj = get_object_or_404(my_model, id = id)

#     if request.method =="POST":
#         obj.delete()
#         return HttpResponseRedirect("/myapp/list")
#     return render(request, "delete_view.html", context)

def p_home(request):
    return render(request, "index_p.html")


def electricity_demand_plot_daily(request):

    dataset_path = os.path.join(settings.BASE_DIR, 'myapp', 'data', 'daily_testset.csv')

    if not os.path.exists(dataset_path):
        return render(request, 'electricity_demand.html', {'error': 'Dataset not found!'})

    df = pd.read_csv(dataset_path, parse_dates=['timestamp'])

    df_month = df[(df['timestamp'] >= '2024-01-01') & (df['timestamp'] <= '2024-01-31')]

    peak_day = df_month.loc[df_month['electricity_demand'].idxmax()]
    lowest_day = df_month.loc[df_month['electricity_demand'].idxmin()]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_month['timestamp'], y=df_month['electricity_demand'],
        mode='lines', name='Electricity Demand',
        line=dict(color='purple')
    ))

    fig.add_trace(go.Scatter(
        x=[peak_day['timestamp'], lowest_day['timestamp']],
        y=[peak_day['electricity_demand'], lowest_day['electricity_demand']],
        mode="markers",
        marker=dict(color='red', size=10, symbol='star'),
        name="Highlighted Points"
    ))

    fig.add_annotation(
        x=peak_day['timestamp'], y=peak_day['electricity_demand'],
        text=f"Peak: {peak_day['electricity_demand']:.2f}",
        showarrow=True, arrowhead=2, ax=30, ay=-40, bgcolor="yellow"
    )

    fig.add_annotation(
        x=lowest_day['timestamp'], y=lowest_day['electricity_demand'],
        text=f"Lowest: {lowest_day['electricity_demand']:.2f}",
        showarrow=True, arrowhead=2, ax=-30, ay=40, bgcolor="lightgreen"
    )

    fig.update_xaxes(
        dtick="D1", tickformat="%b %d", tickangle=45
    )

    graph_html = pio.to_html(fig, full_html=False)

    return render(request, 'electricity_demand_daily.html', {'plot_div': graph_html})


def electricity_demand_plot_hourly(request):
    dataset_path = os.path.join(settings.BASE_DIR, 'myapp', 'data', '2023 dataset.csv')

    if not os.path.exists(dataset_path):
        return render(request, 'electricity_demand_hourly.html', {'error': 'Dataset not found!'})

    df = pd.read_csv(dataset_path, parse_dates=['timestamp'])

    df_day = df[(df['timestamp'] >= '2023-01-01') & (df['timestamp'] < '2023-01-02')]

    if df_day.empty:
        return render(request, 'electricity_demand_hourly.html', {'error': 'No data found for the selected day!'})

    peak_point = df_day.loc[df_day['electricity_demand'].idxmax()]
    lowest_point = df_day.loc[df_day['electricity_demand'].idxmin()]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_day['timestamp'], y=df_day['electricity_demand'],
        mode='lines+markers', name='Electricity Demand',
        line=dict(color='purple'),
        marker=dict(size=4)
    ))

    fig.add_trace(go.Scatter(
        x=[peak_point['timestamp'], lowest_point['timestamp']],
        y=[peak_point['electricity_demand'], lowest_point['electricity_demand']],
        mode="markers",
        marker=dict(color='red', size=10, symbol='circle'),
        name="Highlighted Points"
    ))

    fig.add_annotation(
        x=peak_point['timestamp'], y=peak_point['electricity_demand'],
        text=f"Peak: {peak_point['electricity_demand']:.2f}",
        showarrow=True, arrowhead=2, ax=30, ay=-40, bgcolor="yellow"
    )

    fig.add_annotation(
        x=lowest_point['timestamp'], y=lowest_point['electricity_demand'],
        text=f"Lowest: {lowest_point['electricity_demand']:.2f}",
        showarrow=True, arrowhead=2, ax=-30, ay=40, bgcolor="lightgreen"
    )

    fig.update_xaxes(
        tickformat="%H:%M",
        tickangle=45
    )

    fig.update_layout(
        title="Electricity Demand Over 24 Hours",
        xaxis_title="Time of Day",
        yaxis_title="Electricity Demand",
        template="plotly_white"
    )

    graph_html = pio.to_html(fig, full_html=False)

    return render(request, 'electricity_demand_hourly.html', {'plot_div': graph_html})



def cluster_residential_areas(request):

    data_path = os.path.join(settings.BASE_DIR, 'myapp', 'data')
    tdf = pd.read_csv(os.path.join(data_path, 'ResidentialAreas_Here_Final.csv'))
    rdf = pd.read_csv(os.path.join(data_path, 'ResidentialAreasNeighbourhood_Here_Final.csv'))

    X = np.array(rdf.drop(['lat', 'lon'], axis=1))

    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)

    optimal_clusters = 3
    kmeans = KMeans(n_clusters=optimal_clusters, init='k-means++', max_iter=1000, n_init=125, random_state=0)
    y_kmeans = kmeans.fit_predict(X_pca)
    rdf['cluster'] = y_kmeans

    cluster_colors = {0: 'red', 1: 'orange', 2: 'green'}

    this_map = folium.Map(prefer_canvas=True)
    mapping = {tuple(xy): name for name, xy in zip(tdf['name'], zip(tdf['lat'], tdf['lon']))}

    for _, row in rdf.iterrows():
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=2,
            weight=5,
            color=cluster_colors[row['cluster']],
            popup=mapping.get((row['lat'], row['lon']), "Unknown Location")
        ).add_to(this_map)

    this_map.fit_bounds(this_map.get_bounds())

    map_html = this_map._repr_html_()

    wcss = []
    for cluster_size in range(1, 15):
        kmeans_temp = KMeans(n_clusters=cluster_size, init='k-means++', max_iter=500, n_init=10, random_state=0)
        kmeans_temp.fit(X_pca)
        wcss.append(kmeans_temp.inertia_)

    plt.figure(figsize=(8, 5))
    plt.plot(range(1, 15), wcss, marker='o', linestyle='--')
    plt.title('Elbow Method')
    plt.xlabel('Number of Clusters')
    plt.ylabel('WCSS')
    plt.grid()

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_data = base64.b64encode(img.getvalue()).decode()

    return render(request, 'residential_clusters.html', {'map_html': map_html, 'plot_data': plot_data})


from datetime import datetime

def electricity_demand_plot(request):
    dataset_path = os.path.join(os.path.dirname(__file__), 'data', '2023 dataset.csv')

    if not os.path.exists(dataset_path):
        return render(request, 'electricity_demand.html', {'error': 'Dataset not found!'})

    df = pd.read_csv(dataset_path, parse_dates=['timestamp'])

    selected_date = request.GET.get('date', '2023-01-01')

    try:
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
    except ValueError:
        return render(request, 'electricity_demand.html', {'error': 'Invalid date format! Use YYYY-MM-DD.'})

    df_day = df[df['timestamp'].dt.date == selected_date]

    if df_day.empty:
        return render(request, 'electricity_demand.html', {'error': 'No data found for the selected date!'})

    peak_point = df_day.loc[df_day['electricity_demand'].idxmax()]
    lowest_point = df_day.loc[df_day['electricity_demand'].idxmin()]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_day['timestamp'], y=df_day['electricity_demand'],
        mode='lines+markers', name='Electricity Demand',
        line=dict(color='purple'),
        marker=dict(size=4)
    ))

    fig.add_trace(go.Scatter(
        x=[peak_point['timestamp'], lowest_point['timestamp']],
        y=[peak_point['electricity_demand'], lowest_point['electricity_demand']],
        mode="markers",
        marker=dict(color='red', size=10, symbol='circle'),
        name="Highlighted Points"
    ))

    fig.add_annotation(
        x=peak_point['timestamp'], y=peak_point['electricity_demand'],
        text=f"Peak: {peak_point['electricity_demand']:.2f}",
        showarrow=True, arrowhead=2, ax=30, ay=-40, bgcolor="yellow"
    )

    fig.add_annotation(
        x=lowest_point['timestamp'], y=lowest_point['electricity_demand'],
        text=f"Lowest: {lowest_point['electricity_demand']:.2f}",
        showarrow=True, arrowhead=2, ax=-30, ay=40, bgcolor="lightgreen"
    )

    fig.update_xaxes(
        tickformat="%H:%M",
        tickangle=45
    )

    fig.update_layout(
        title=f"Electricity Demand for {selected_date}",
        xaxis_title="Time of Day",
        yaxis_title="Electricity Demand",
        template="plotly_white"
    )

    graph_html = pio.to_html(fig, full_html=False)

    return render(request, 'electricity_demand.html', {'plot_div': graph_html, 'selected_date': selected_date})
