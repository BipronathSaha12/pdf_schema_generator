import os
import tempfile
from datetime import datetime, timezone

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from backend.pdf_parser import parse_pdf
from backend.schema_generator import generate_schema
from backend.serializers import (
    SchemaEditSerializer,
    UserCreateSerializer,
    ValidateDataSerializer,
)
from backend.validator import (
    add_validation_rules,
    validate_data_against_schema,
    validate_schema,
)

UPLOAD_DIR = tempfile.mkdtemp(prefix="pdf_schema_")

fake_users_db: dict[str, str] = {}


def index(request):
    return render(request, "index.html")


@api_view(["POST"])
@parser_classes([MultiPartParser])
def generate_schema_endpoint(request):
    file = request.FILES.get("file")
    if not file:
        return Response(
            {"detail": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
        )

    if not file.name.lower().endswith(".pdf"):
        return Response(
            {"detail": "Only PDF files are supported"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if file.size > settings.UPLOAD_MAX_SIZE:
        return Response(
            {"detail": "File size exceeds 50MB limit"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    file_path = os.path.join(UPLOAD_DIR, file.name)
    try:
        with open(file_path, "wb") as f:
            for chunk in file.chunks():
                f.write(chunk)

        parsed = parse_pdf(file_path)
        schema = generate_schema(parsed)

        schema["properties"]["document_metadata"]["properties"]["extraction_date"][
            "const"
        ] = datetime.now(timezone.utc).isoformat()
        schema["properties"]["document_metadata"]["properties"]["page_count"][
            "const"
        ] = parsed["page_count"]

        schema = add_validation_rules(schema)
        validation = validate_schema(schema)

        return Response(
            {
                "schema": schema,
                "validation": validation,
                "document_info": {
                    "filename": file.name,
                    "pages": parsed["page_count"],
                    "fields_detected": len(parsed["key_value_pairs"]),
                    "tables_detected": len(parsed["tables"]),
                    "sections_detected": len(parsed["sections"]),
                },
            }
        )
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@api_view(["POST"])
def validate_schema_endpoint(request):
    serializer = SchemaEditSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    result = validate_schema(serializer.validated_data["schema_payload"])
    return Response(result)


@api_view(["POST"])
def validate_data_endpoint(request):
    serializer = ValidateDataSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    result = validate_data_against_schema(
        serializer.validated_data["data"],
        serializer.validated_data["schema_payload"],
    )
    return Response(result)


@api_view(["POST"])
def register(request):
    serializer = UserCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data["username"]
    password = serializer.validated_data["password"]

    if username in fake_users_db:
        return Response(
            {"detail": "Username already exists"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    fake_users_db[username] = make_password(password)
    token = str(AccessToken())
    return Response({"access_token": token, "token_type": "bearer"})


@api_view(["POST"])
def login(request):
    serializer = UserCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data["username"]
    password = serializer.validated_data["password"]

    stored_hash = fake_users_db.get(username)
    if not stored_hash or not check_password(password, stored_hash):
        return Response(
            {"detail": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    token = str(AccessToken())
    return Response({"access_token": token, "token_type": "bearer"})


@api_view(["GET"])
def health(request):
    return Response({"status": "healthy", "version": "1.0.0"})


EXAMPLE_INVOICE_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "invoice-schema",
    "title": "Invoice Schema",
    "description": "Schema for a standard business invoice document",
    "type": "object",
    "properties": {
        "document_metadata": {
            "type": "object",
            "properties": {
                "page_count": {"type": "integer", "minimum": 1},
                "extraction_date": {"type": "string", "format": "date-time"},
            },
            "required": ["page_count", "extraction_date"],
        },
        "invoice_header": {
            "type": "object",
            "properties": {
                "invoice_number": {
                    "type": "string",
                    "minLength": 1,
                    "description": "Unique invoice identifier",
                },
                "invoice_date": {
                    "type": "string",
                    "format": "date",
                    "description": "Date the invoice was issued",
                },
                "due_date": {
                    "type": "string",
                    "format": "date",
                    "description": "Payment due date",
                },
                "po_number": {
                    "type": ["string", "null"],
                    "description": "Purchase order number if applicable",
                },
            },
            "required": ["invoice_number", "invoice_date", "due_date"],
        },
        "vendor": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "address": {"type": "string"},
                "tax_id": {"type": ["string", "null"]},
                "contact": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "format": "email"},
                        "phone": {"type": "string"},
                    },
                },
            },
            "required": ["name"],
        },
        "bill_to": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "address": {"type": "string"},
                "tax_id": {"type": ["string", "null"]},
            },
            "required": ["name"],
        },
        "line_items": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {
                    "item_number": {"type": "integer", "minimum": 1},
                    "description": {"type": "string", "minLength": 1},
                    "quantity": {"type": "number", "minimum": 0},
                    "unit_price": {"type": "number", "minimum": 0},
                    "tax_rate": {"type": "number", "minimum": 0, "maximum": 100},
                    "amount": {"type": "number", "minimum": 0},
                },
                "required": ["description", "quantity", "unit_price", "amount"],
            },
            "description": "Individual line items on the invoice",
        },
        "totals": {
            "type": "object",
            "properties": {
                "subtotal": {
                    "type": "number",
                    "minimum": 0,
                    "description": "Sum of all line item amounts before tax",
                },
                "tax_amount": {
                    "type": "number",
                    "minimum": 0,
                    "description": "Total tax amount",
                },
                "discount": {
                    "type": "number",
                    "minimum": 0,
                    "description": "Total discount applied",
                },
                "grand_total": {
                    "type": "number",
                    "minimum": 0,
                    "description": "Final total: subtotal + tax - discount",
                },
                "currency": {
                    "type": "string",
                    "minLength": 3,
                    "maxLength": 3,
                    "description": "ISO 4217 currency code",
                },
            },
            "required": ["subtotal", "tax_amount", "grand_total", "currency"],
            "description": "Sum validation: subtotal + tax_amount - discount = grand_total",
        },
        "payment_terms": {
            "type": "object",
            "properties": {
                "method": {
                    "type": "string",
                    "enum": [
                        "bank_transfer",
                        "check",
                        "credit_card",
                        "cash",
                        "other",
                    ],
                },
                "bank_details": {
                    "type": "object",
                    "properties": {
                        "bank_name": {"type": "string"},
                        "account_number": {"type": "string"},
                        "routing_number": {"type": "string"},
                        "swift_code": {"type": ["string", "null"]},
                    },
                },
                "notes": {"type": ["string", "null"]},
            },
        },
    },
    "required": [
        "document_metadata",
        "invoice_header",
        "vendor",
        "bill_to",
        "line_items",
        "totals",
    ],
    "additionalProperties": False,
}


@api_view(["GET"])
def example_schema(request):
    return Response(EXAMPLE_INVOICE_SCHEMA)
