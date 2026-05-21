ROL_ADMINISTRADOR = 'Administrador'
ROL_RECEPCION = 'Recepcion'
ROL_TECNICO = 'Tecnico'
ROL_CONSULTA = 'Consulta'

ROLES_OPERATIVOS = [ROL_ADMINISTRADOR, ROL_RECEPCION, ROL_TECNICO, ROL_CONSULTA]

ROLES_POR_SECCION = {
    'panel': ROLES_OPERATIVOS,
    'clientes': [ROL_ADMINISTRADOR, ROL_RECEPCION, ROL_CONSULTA],
    'productos': [ROL_ADMINISTRADOR, ROL_RECEPCION, ROL_CONSULTA],
    'ventas': [ROL_ADMINISTRADOR, ROL_RECEPCION, ROL_CONSULTA],
    'garantias': [ROL_ADMINISTRADOR, ROL_RECEPCION, ROL_CONSULTA],
    'casos': [ROL_ADMINISTRADOR, ROL_RECEPCION, ROL_TECNICO, ROL_CONSULTA],
    'diagnosticos': [ROL_ADMINISTRADOR, ROL_TECNICO, ROL_CONSULTA],
    'evidencias': [ROL_ADMINISTRADOR, ROL_RECEPCION, ROL_TECNICO, ROL_CONSULTA],
    'estados': [ROL_ADMINISTRADOR],
    'historial': [ROL_ADMINISTRADOR, ROL_TECNICO, ROL_CONSULTA],
    'entregas': [ROL_ADMINISTRADOR, ROL_RECEPCION, ROL_CONSULTA],
}


def usuario_tiene_rol(usuario, roles_permitidos):
    if not usuario.is_authenticated:
        return False
    if usuario.is_superuser:
        return True
    return usuario.groups.filter(name__in=roles_permitidos).exists()


def usuario_puede_ver_seccion(usuario, seccion):
    roles_permitidos = ROLES_POR_SECCION.get(seccion, [ROL_ADMINISTRADOR])
    return usuario_tiene_rol(usuario, roles_permitidos)


def obtener_rol_visible(usuario):
    if not usuario.is_authenticated:
        return ''
    if usuario.is_superuser:
        return ROL_ADMINISTRADOR
    grupo = usuario.groups.filter(name__in=ROLES_OPERATIVOS).first()
    if grupo:
        return grupo.name
    return 'Sin rol asignado'
