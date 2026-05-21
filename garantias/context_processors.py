from .permisos import (
    ROL_ADMINISTRADOR,
    ROL_RECEPCION,
    ROL_TECNICO,
    obtener_rol_visible,
    usuario_puede_ver_seccion,
    usuario_tiene_rol,
)


def menu_por_roles(request):
    elementos_menu = [
        {'seccion': 'panel', 'nombre': 'Panel', 'url': 'dashboard'},
        {'seccion': 'clientes', 'nombre': 'Clientes', 'url': 'cliente_list'},
        {'seccion': 'productos', 'nombre': 'Productos', 'url': 'producto_list'},
        {'seccion': 'ventas', 'nombre': 'Ventas', 'url': 'venta_list'},
        {'seccion': 'garantias', 'nombre': 'Garantias', 'url': 'garantia_list'},
        {'seccion': 'casos', 'nombre': 'Casos tecnicos', 'url': 'caso_list'},
        {'seccion': 'diagnosticos', 'nombre': 'Diagnosticos', 'url': 'diagnostico_list'},
        {'seccion': 'evidencias', 'nombre': 'Fotos', 'url': 'evidencia_list'},
        {'seccion': 'estados', 'nombre': 'Estados', 'url': 'estado_list'},
        {'seccion': 'entregas', 'nombre': 'Entrega', 'url': 'entrega_list'},
    ]

    usuario = request.user
    return {
        'menu_principal': [
            elemento for elemento in elementos_menu if usuario_puede_ver_seccion(usuario, elemento['seccion'])
        ],
        'rol_usuario': obtener_rol_visible(usuario),
        'puede_crear_caso': usuario_tiene_rol(usuario, [ROL_ADMINISTRADOR, ROL_RECEPCION, ROL_TECNICO]),
        'puede_subir_evidencia': usuario_tiene_rol(usuario, [ROL_ADMINISTRADOR, ROL_RECEPCION, ROL_TECNICO]),
    }
