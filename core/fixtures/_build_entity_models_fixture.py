"""
Genera core/fixtures/entity_models.json a partir de la definición estática
del frontend Angular. Ejecutar con:

    python core/fixtures/_build_entity_models_fixture.py
"""
import json
import os

TIMESTAMP = "2026-01-01T00:00:00Z"

DATA = [
    {
        "id": "default",
        "name": "Default",
        "plural_name": "Defaults",
        "views": [{"type": "dashboard", "route": "dashboard", "config": {}}],
    },
    {
        "id": "empleado",
        "name": "Empleado",
        "plural_name": "Empleados",
        "views": [
            {"type": "list", "route": "list", "config": {}},
            {"type": "form", "route": "list", "config": {}},
            {"type": "show", "route": "list", "config": {}},
            {"type": "update", "route": "list", "config": {}},
        ],
        "searchAttributes": [
            {"key": "nombre", "label": "Nombre", "type": "text"},
            {"key": "numero_empleado", "label": "Número de Empleado", "type": "number"},
            {"key": "nombre_adscripcion", "label": "Nombre de Adscripción", "type": "text"},
            {"key": "nombre_categoria", "label": "Nombre de categoría", "type": "text"},
        ],
    },
    {
        "id": "usuario",
        "name": "Usuario",
        "plural_name": "Usuarios",
        "views": [
            {"type": "list", "route": "list", "config": {"comments_tool": False}},
            {"type": "form", "route": "form", "config": {"comments_tool": False}},
            {"type": "show", "route": "show", "config": {"comments_tool": False}},
            {"type": "update", "route": "update", "config": {"comments_tool": False}},
        ],
        "searchAttributes": [
            {"key": "username", "label": "Usuario", "type": "text"},
            {"key": "email", "label": "Email", "type": "text"},
            {"key": "first_name", "label": "Nombre", "type": "text"},
            {"key": "last_name", "label": "Apellido", "type": "text"},
        ],
    },
    {
        "id": "stage",
        "name": "Etapa",
        "plural_name": "Etapas",
        "views": [
            {"type": "list", "route": "list", "config": {"comments_tool": False}},
            {"type": "form", "route": "form", "config": {"comments_tool": False}},
            {"type": "show", "route": "list", "config": {"comments_tool": False}},
            {"type": "update", "route": "list", "config": {"comments_tool": False}},
        ],
        "searchAttributes": [{"key": "name", "label": "Nombre de Etapa", "type": "text"}],
    },
    {
        "id": "brand",
        "name": "Marca",
        "plural_name": "Marcas",
        "model": "brand",
        "views": [
            {"type": "list", "route": "list", "config": {"comments_tool": False}},
            {"type": "form", "route": "list", "config": {"comments_tool": False}},
            {"type": "show", "route": "list", "config": {"comments_tool": False}},
            {"type": "update", "route": "list", "config": {"comments_tool": False}},
        ],
        "searchAttributes": [
            {"key": "code", "label": "Código", "type": "text"},
            {"key": "name", "label": "Nombre", "type": "text"},
        ],
    },
    {
        "id": "type",
        "name": "Tipo de Producto",
        "plural_name": "Tipos de Producto",
        "model": "type",
        "views": [
            {"type": "list", "route": "list", "config": {"comments_tool": False}},
            {"type": "form", "route": "form", "config": {"comments_tool": False}},
            {"type": "show", "route": "show", "config": {"comments_tool": False}},
            {"type": "update", "route": "update", "config": {"comments_tool": False}},
        ],
        "searchAttributes": [
            {"key": "code", "label": "Código", "type": "text"},
            {"key": "name", "label": "Nombre", "type": "text"},
        ],
    },
    {
        "id": "category",
        "name": "Categoría de Producto",
        "plural_name": "Categorías de Producto",
        "model": "category",
        "views": [
            {"type": "list", "route": "list", "config": {"comments_tool": False}},
            {"type": "form", "route": "form", "config": {"comments_tool": False}},
            {"type": "show", "route": "show", "config": {"comments_tool": False}},
            {"type": "update", "route": "update", "config": {"comments_tool": False}},
        ],
        "searchAttributes": [
            {"key": "code", "label": "Código", "type": "text"},
            {"key": "name", "label": "Nombre", "type": "text"},
        ],
    },
    {
        "id": "unit_of_measure",
        "name": "Unidad de Medida",
        "plural_name": "Unidades de Medida",
        "model": "unit_of_measure",
        "views": [
            {"type": "list", "route": "list", "config": {"comments_tool": False}},
            {"type": "form", "route": "form", "config": {"comments_tool": False}},
            {"type": "show", "route": "show", "config": {"comments_tool": False}},
            {"type": "update", "route": "update", "config": {"comments_tool": False}},
        ],
        "searchAttributes": [
            {"key": "name", "label": "Nombre", "type": "text"},
            {"key": "abbreviation", "label": "Abreviatura", "type": "text"},
        ],
    },
    {
        "id": "product",
        "name": "Producto",
        "plural_name": "Productos",
        "model": "product",
        "views": [
            {"type": "list", "route": "list", "config": {"card_view": True}},
            {"type": "form", "route": "form", "config": {}},
            {"type": "show", "route": "show", "config": {}},
            {"type": "update", "route": "update", "config": {}},
        ],
        "searchAttributes": [
            {"key": "name", "label": "Nombre", "type": "text"},
            {"key": "short_description", "label": "Descripción Corta", "type": "text"},
            {"key": "long_description", "label": "Descripción Larga", "type": "text"},
            {"key": "brand", "label": "Marca", "type": "text"},
            {"key": "category", "label": "Categoría", "type": "text"},
            {"key": "partner", "label": "Socio Comercial", "type": "text"},
        ],
    },
    {
        "id": "product_variation",
        "name": "Variación de Producto",
        "plural_name": "Variaciones de Producto",
        "model": "product_variation",
        "views": [
            {"type": "list", "route": "list", "config": {"card_view": True}},
            {"type": "form", "route": "form", "config": {"comments_tool": False}},
            {"type": "show", "route": "show", "config": {"comments_tool": False}},
            {"type": "update", "route": "update", "config": {"comments_tool": False}},
        ],
        "searchAttributes": [
            {"key": "name", "label": "Nombre", "type": "text"},
            {"key": "description", "label": "Descripción", "type": "text"},
        ],
    },
    {
        "id": "person_title",
        "name": "Título de Persona",
        "plural_name": "Títulos de Persona",
        "model": "person_title",
        "views": [
            {"type": "list", "route": "list", "config": {"comments_tool": False}},
            {"type": "form", "route": "form", "config": {"comments_tool": False}},
            {"type": "show", "route": "show", "config": {"comments_tool": False}},
            {"type": "update", "route": "update", "config": {"comments_tool": False}},
        ],
        "searchAttributes": [
            {"key": "code", "label": "Código", "type": "text"},
            {"key": "name", "label": "Nombre", "type": "text"},
            {"key": "abbreviation", "label": "Abreviatura", "type": "text"},
        ],
    },
    {
        "id": "department",
        "name": "Departamento",
        "plural_name": "Departamentos",
        "model": "department",
        "views": [
            {"type": "list", "route": "list", "config": {"comments_tool": False}},
            {"type": "form", "route": "form", "config": {"comments_tool": False}},
            {"type": "show", "route": "show", "config": {"comments_tool": False}},
            {"type": "update", "route": "update", "config": {"comments_tool": False}},
        ],
        "searchAttributes": [
            {"key": "code", "label": "Código", "type": "text"},
            {"key": "name", "label": "Nombre", "type": "text"},
            {"key": "description", "label": "Descripción", "type": "text"},
        ],
    },
    {
        "id": "company_sector",
        "name": "Sector Empresarial",
        "plural_name": "Sectores Empresariales",
        "model": "company_sector",
        "views": [
            {"type": "list", "route": "list", "config": {"comments_tool": False}},
            {"type": "form", "route": "form", "config": {"comments_tool": False}},
            {"type": "show", "route": "show", "config": {"comments_tool": False}},
            {"type": "update", "route": "update", "config": {"comments_tool": False}},
        ],
        "searchAttributes": [
            {"key": "code", "label": "Código", "type": "text"},
            {"key": "name", "label": "Nombre", "type": "text"},
            {"key": "description", "label": "Descripción", "type": "text"},
        ],
    },
    {
        "id": "employee",
        "name": "Empleado",
        "plural_name": "Empleados",
        "model": "employee",
        "views": [
            {"type": "list", "route": "list", "config": {"comments_tool": False}},
            {"type": "form", "route": "form", "config": {"comments_tool": False}},
            {"type": "show", "route": "show", "config": {"comments_tool": False}},
            {"type": "update", "route": "update", "config": {"comments_tool": False}},
        ],
        "searchAttributes": [
            {"key": "first_name", "label": "Nombre", "type": "text"},
            {"key": "last_name_father", "label": "Apellido Paterno", "type": "text"},
            {"key": "last_name_mother", "label": "Apellido Materno", "type": "text"},
            {"key": "email", "label": "Email", "type": "text"},
        ],
    },
    {
        "id": "company",
        "name": "Empresa",
        "plural_name": "Empresas",
        "model": "company",
        "views": [
            {"type": "list", "route": "list", "config": {"card_view": True}},
            {"type": "form", "route": "form", "config": {}},
            {"type": "show", "route": "show", "config": {}},
            {"type": "update", "route": "update", "config": {}},
        ],
        "searchAttributes": [
            {"key": "code", "label": "Código", "type": "text"},
            {"key": "name", "label": "Nombre", "type": "text"},
            {"key": "trade_name", "label": "Nombre Comercial", "type": "text"},
            {"key": "tax_id", "label": "RFC / Tax ID", "type": "text"},
            {"key": "email", "label": "Email", "type": "text"},
        ],
    },
    {
        "id": "company_address",
        "name": "Dirección de Empresa",
        "plural_name": "Direcciones de Empresa",
        "model": "company_address",
        "views": [
            {"type": "list", "route": "list", "config": {"comments_tool": False}},
            {"type": "form", "route": "form", "config": {"comments_tool": False}},
            {"type": "show", "route": "show", "config": {"comments_tool": False}},
            {"type": "update", "route": "update", "config": {"comments_tool": False}},
        ],
        "searchAttributes": [
            {
                "key": "kind",
                "label": "Tipo",
                "type": "select",
                "options": [
                    {"label": "Fiscal", "value": "FISCAL"},
                    {"label": "Sucursal", "value": "BRANCH"},
                    {"label": "Envío", "value": "SHIPPING"},
                    {"label": "Otro", "value": "OTHER"},
                ],
            },
            {"key": "name", "label": "Nombre", "type": "text"},
            {"key": "city", "label": "Ciudad", "type": "text"},
            {"key": "state", "label": "Estado", "type": "text"},
            {"key": "zip_code", "label": "Código Postal", "type": "text"},
        ],
    },
    {
        "id": "company_contact",
        "name": "Contacto de Empresa",
        "plural_name": "Contactos de Empresa",
        "model": "company_contact",
        "views": [
            {"type": "list", "route": "list", "config": {"comments_tool": False}},
            {"type": "form", "route": "form", "config": {"comments_tool": False}},
            {"type": "show", "route": "show", "config": {"comments_tool": False}},
            {"type": "update", "route": "update", "config": {"comments_tool": False}},
        ],
        "searchAttributes": [
            {"key": "name", "label": "Nombre", "type": "text"},
            {"key": "email", "label": "Email", "type": "text"},
            {"key": "phone", "label": "Teléfono", "type": "text"},
        ],
    },
    {
        "id": "company_bank_account",
        "name": "Cuenta Bancaria de Empresa",
        "plural_name": "Cuentas Bancarias de Empresa",
        "model": "company_bank_account",
        "views": [
            {"type": "list", "route": "list", "config": {"comments_tool": False}},
            {"type": "form", "route": "form", "config": {"comments_tool": False}},
            {"type": "show", "route": "show", "config": {"comments_tool": False}},
            {"type": "update", "route": "update", "config": {"comments_tool": False}},
        ],
        "searchAttributes": [
            {"key": "account_holder", "label": "Titular", "type": "text"},
            {"key": "clabe", "label": "CLABE", "type": "text"},
            {"key": "account_number", "label": "No. de Cuenta", "type": "text"},
        ],
    },
    {
        "id": "partner",
        "name": "Partner",
        "plural_name": "Partners",
        "model": "partner",
        "views": [
            {"type": "list", "route": "list", "config": {"card_view": True}},
            {"type": "form", "route": "form", "config": {}},
            {"type": "show", "route": "show", "config": {}},
            {"type": "update", "route": "update", "config": {}},
        ],
        "searchAttributes": [
            {"key": "commercial_name", "label": "Nombre", "type": "text"},
            {
                "key": "role",
                "label": "Rol",
                "type": "select",
                "options": [
                    {"label": "Cliente", "value": "CUSTOMER"},
                    {"label": "Proveedor", "value": "SUPPLIER"},
                    {"label": "Transportista", "value": "CARRIER"},
                    {"label": "Otro", "value": "OTHER"},
                ],
            },
            {
                "key": "sector",
                "label": "Sector",
                "type": "select",
                "options": [
                    {"label": "Privado", "value": "PRIVATE"},
                    {"label": "Público", "value": "PUBLIC"},
                ],
            },
            {"key": "company_sector", "label": "Sector Comercial", "type": "text"},
            {
                "key": "person_type",
                "label": "Tipo de Persona",
                "type": "select",
                "options": [
                    {"label": "Persona Moral", "value": "MORAL"},
                    {"label": "Persona Física", "value": "FISICA"},
                ],
            },
        ],
    },
    {
        "id": "sat_catalog",
        "name": "Catálogo SAT",
        "plural_name": "Catálogos SAT",
        "model": "sat_catalog",
        "views": [
            {"type": "list", "route": "list", "config": {"comments_tool": False}},
            {"type": "form", "route": "form", "config": {"comments_tool": False}},
            {"type": "show", "route": "show", "config": {"comments_tool": False}},
            {"type": "update", "route": "update", "config": {"comments_tool": False}},
        ],
        "searchAttributes": [
            {"key": "code", "label": "Código", "type": "text"},
            {
                "key": "catalog",
                "label": "Catálogo",
                "type": "select",
                "options": [
                    {"label": "Regimen Fiscal", "value": "c_RegimenFiscal"},
                    {"label": "DIOT Tipo Tercero", "value": "DIOT_TipoTercero"},
                    {"label": "DIOT Tipo Operación", "value": "DIOT_TipoOperacion"},
                    {"label": "Moneda", "value": "c_Moneda"},
                    {"label": "Forma de Pago", "value": "c_FormaPago"},
                    {"label": "Método de Pago", "value": "c_MetodoPago"},
                    {"label": "Periodicidad", "value": "c_Periodicidad"},
                ],
            },
            {"key": "description", "label": "Descripción", "type": "text"},
        ],
    },
    {
        "id": "bank",
        "name": "Banco",
        "plural_name": "Bancos",
        "model": "bank",
        "views": [
            {"type": "list", "route": "list", "config": {"comments_tool": False}},
            {"type": "form", "route": "form", "config": {"comments_tool": False}},
            {"type": "show", "route": "show", "config": {"comments_tool": False}},
            {"type": "update", "route": "update", "config": {"comments_tool": False}},
        ],
        "searchAttributes": [
            {"key": "code", "label": "Código", "type": "text"},
            {"key": "name", "label": "Nombre", "type": "text"},
            {"key": "short_name", "label": "Nombre Corto", "type": "text"},
            {"key": "legal_name", "label": "Razón Social", "type": "text"},
        ],
    },
    {
        "id": "job_position",
        "name": "Puesto de Trabajo",
        "plural_name": "Puestos de Trabajo",
        "model": "job_position",
        "views": [
            {"type": "list", "route": "list", "config": {"comments_tool": False}},
            {"type": "form", "route": "form", "config": {"comments_tool": False}},
            {"type": "show", "route": "show", "config": {"comments_tool": False}},
            {"type": "update", "route": "update", "config": {"comments_tool": False}},
        ],
        "searchAttributes": [
            {"key": "code", "label": "Código", "type": "text"},
            {"key": "name", "label": "Nombre", "type": "text"},
        ],
    },
    {
        "id": "partner_contact",
        "name": "Contacto de Partner",
        "plural_name": "Contactos de Partner",
        "model": "partner_contact",
        "views": [
            {"type": "list", "route": "list", "config": {"card_view": True}},
            {"type": "form", "route": "form", "config": {"comments_tool": False}},
            {"type": "show", "route": "show", "config": {"comments_tool": False}},
            {"type": "update", "route": "update", "config": {"comments_tool": False}},
        ],
        "searchAttributes": [
            {"key": "name", "label": "Nombre", "type": "text"},
            {"key": "email", "label": "Email", "type": "text"},
            {"key": "phone", "label": "Teléfono", "type": "text"},
        ],
    },
    {
        "id": "sat_catalog_prod_serv",
        "name": "Clave Producto/Servicio SAT",
        "plural_name": "Claves Productos/Servicios SAT",
        "model": "sat_catalog_prod_serv",
        "views": [{"type": "list", "route": "list", "config": {"comments_tool": False}}],
        "searchAttributes": [
            {"key": "clave", "label": "Clave", "type": "text"},
            {"key": "descripcion", "label": "Descripción", "type": "text"},
        ],
    },
    {
        "id": "sat_catalog_unit",
        "name": "Clave Unidad SAT",
        "plural_name": "Claves Unidades SAT",
        "model": "sat_catalog_unit",
        "views": [{"type": "list", "route": "list", "config": {"comments_tool": False}}],
        "searchAttributes": [
            {"key": "clave", "label": "Clave", "type": "text"},
            {"key": "name", "label": "Nombre", "type": "text"},
        ],
    },
    {
        "id": "quotation",
        "name": "Cotización",
        "plural_name": "Cotizaciones",
        "model": "quotation",
        "views": [
            {"type": "list", "route": "list", "config": {"comments_tool": False}},
            {"type": "form", "route": "form", "config": {"comments_tool": False}},
            {"type": "show", "route": "show", "config": {"comments_tool": True}},
            {"type": "update", "route": "update", "config": {"comments_tool": False}},
        ],
        "searchAttributes": [
            {"key": "code", "label": "Código", "type": "text"},
            {"key": "name", "label": "Nombre", "type": "text"},
        ],
    },
    {
        "id": "fast_sales_proposal",
        "name": "Propuesta de Venta Rápida",
        "plural_name": "Propuestas de Venta Rápida",
        "model": "fastsalesproposal",
        "views": [
            {"type": "list", "route": "list", "config": {"comments_tool": False}},
            {"type": "form", "route": "form", "config": {"comments_tool": False}},
            {"type": "show", "route": "show", "config": {"comments_tool": True}},
            {"type": "update", "route": "update", "config": {"comments_tool": False}},
        ],
        "searchAttributes": [
            {"key": "code", "label": "Código", "type": "text"},
            {"key": "name", "label": "Nombre", "type": "text"},
        ],
    },
    {
        "id": "fast_quotation",
        "name": "Cotización Rápida",
        "plural_name": "Cotizaciones Rápidas",
        "model": "fastquotation",
        "views": [
            {"type": "list", "route": "list", "config": {"comments_tool": False}},
            {"type": "form", "route": "form", "config": {"comments_tool": False}},
            {"type": "show", "route": "show", "config": {"comments_tool": True}},
            {"type": "update", "route": "update", "config": {"comments_tool": False}},
        ],
        "searchAttributes": [
            {"key": "code", "label": "Código", "type": "text"},
            {"key": "name", "label": "Nombre", "type": "text"},
        ],
        "secondary_actions": [
            {
                "id": "export",
                "icon": "request_page",
                "title": "Exportar",
                "description": "Cotización rápida.",
                "color": "primary",
                "views": ["show"],
            },
            {
                "id": "visualize",
                "icon": "preview",
                "title": "Visualizar",
                "description": "Vista externa.",
                "color": "primary",
                "views": ["show"],
            },
        ],
    },
    {
        "id": "service_category",
        "name": "Categoría de Servicio",
        "plural_name": "Categorías de Servicio",
        "model": "service_category",
        "views": [
            {"type": "list", "route": "list", "config": {"comments_tool": False}},
            {"type": "form", "route": "form", "config": {"comments_tool": False}},
            {"type": "show", "route": "show", "config": {"comments_tool": False}},
            {"type": "update", "route": "update", "config": {"comments_tool": False}},
        ],
        "searchAttributes": [
            {"key": "code", "label": "Código", "type": "text"},
            {"key": "name", "label": "Nombre", "type": "text"},
        ],
    },
    {
        "id": "external_note_template",
        "name": "Plantilla de Nota Externa",
        "plural_name": "Plantillas de Notas Externas",
        "model": "external_note_template",
        "views": [
            {"type": "list", "route": "list", "config": {"comments_tool": False}},
            {"type": "form", "route": "form", "config": {"comments_tool": False}},
            {"type": "show", "route": "show", "config": {"comments_tool": False}},
        ],
        "searchAttributes": [
            {"key": "code", "label": "Código", "type": "text"},
            {"key": "name", "label": "Nombre", "type": "text"},
        ],
    },
    {
        "id": "service",
        "name": "Servicio",
        "plural_name": "Servicios",
        "model": "service",
        "views": [
            {"type": "list", "route": "list", "config": {"card_view": True}},
            {"type": "form", "route": "form", "config": {}},
            {"type": "show", "route": "show", "config": {}},
            {"type": "update", "route": "update", "config": {}},
        ],
        "searchAttributes": [
            {"key": "name", "label": "Nombre", "type": "text"},
            {"key": "short_description", "label": "Descripción Corta", "type": "text"},
            {"key": "long_description", "label": "Descripción Larga", "type": "text"},
            {"key": "category", "label": "Categoría", "type": "text"},
        ],
    },
    {
        "id": "entity_model",
        "name": "Entity Model",
        "plural_name": "Entity Models",
        "model": "entity_model",
        "views": [
            {"type": "list", "route": "list", "config": {"comments_tool": False}},
            {"type": "form", "route": "form", "config": {"comments_tool": False}},
            {"type": "show", "route": "show", "config": {"comments_tool": False}},
            {"type": "update", "route": "update", "config": {"comments_tool": False}},
        ],
        "searchAttributes": [
            {"key": "code", "label": "Código", "type": "text"},
            {"key": "name", "label": "Nombre", "type": "text"},
            {"key": "plural_name", "label": "Nombre Plural", "type": "text"},
            {"key": "module", "label": "Módulo", "type": "text"},
            {"key": "model", "label": "Modelo", "type": "text"},
        ],
    },
]


def build():
    fixture = []
    em_pk = 0

    for entity in DATA:
        em_pk += 1

        # Agrupar secondary_actions por tipo de view
        actions_by_view: dict[str, list[dict]] = {}
        for order, act in enumerate(entity.get("secondary_actions", [])):
            payload = {
                "action_id": act["id"],
                "icon": act["icon"],
                "title": act["title"],
                "description": act.get("description", ""),
                "color": act.get("color", "primary"),
                "order": order,
            }
            for vtype in act.get("views", []):
                actions_by_view.setdefault(vtype, []).append(payload)

        views_payload = []
        for order, view in enumerate(entity.get("views", [])):
            cfg = view.get("config") or {}
            views_payload.append({
                "type": view["type"],
                "route": view["route"],
                "action_buttons_tool": "",
                "comments_tool": cfg.get("comments_tool", True),
                "card_view": cfg.get("card_view", False),
                "order": order,
                "secondary_actions": actions_by_view.get(view["type"], []),
            })

        search_attrs_payload = []
        for order, attr in enumerate(entity.get("searchAttributes", [])):
            search_attrs_payload.append({
                "key": attr["key"],
                "label": attr["label"],
                "type": attr.get("type", "text"),
                "options": attr.get("options", []),
                "order": order,
            })

        fixture.append({
            "model": "core.entitymodel",
            "pk": em_pk,
            "fields": {
                "code": entity["id"],
                "name": entity["name"],
                "plural_name": entity["plural_name"],
                "model": entity.get("model", ""),
                "module": entity.get("module", ""),
                "is_active": True,
                "views": views_payload,
                "search_attributes": search_attrs_payload,
                "created_at": TIMESTAMP,
                "updated_at": TIMESTAMP,
            },
        })

    out_path = os.path.join(os.path.dirname(__file__), "entity_models.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(fixture, fh, ensure_ascii=False, indent=2)
    print(f"Wrote {len(fixture)} objects to {out_path}")


if __name__ == "__main__":
    build()
