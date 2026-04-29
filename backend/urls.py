from django.urls import path

from backend import views

urlpatterns = [
    path("", views.index, name="index"),
    path("api/generate-schema", views.generate_schema_endpoint, name="generate-schema"),
    path("generate-schema", views.generate_schema_endpoint, name="generate-schema-alt"),
    path("api/validate-schema", views.validate_schema_endpoint, name="validate-schema"),
    path("api/validate-data", views.validate_data_endpoint, name="validate-data"),
    path("api/auth/register", views.register, name="register"),
    path("api/auth/login", views.login, name="login"),
    path("api/health", views.health, name="health"),
    path("api/example-schema", views.example_schema, name="example-schema"),
]
