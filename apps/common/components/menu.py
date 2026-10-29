# apps/common/components/menu.py
import logging
import math
from fnmatch import fnmatchcase
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Literal, Optional

from django.core.exceptions import ImproperlyConfigured
from django.urls import NoReverseMatch, reverse


logger = logging.getLogger(__name__)


# Variantes de insignia permitidas (spec FR-017): neutra, advertencia e
# informativa. Cada una tiene su estilo en static/project/css/sidebar.css.
BADGE_VARIANTS = ('light', 'warning', 'info')

# Tipos de opción del menú de usuario: enlace o formulario POST con CSRF.
USER_ITEM_KINDS = ('link', 'post')


# ── Estructuras declarativas ─────────────────────────────────────────────
#
# Cada app declara su menú en `apps/<app>/menu.py` con estas estructuras
# inmutables (data-model §1; contracts/menu-declaration.md).


@dataclass(frozen=True)
class Badge:
    """
    Insignia breve de una opción de menú.

    El texto (en español, no vacío) es obligatorio: el color nunca es el
    único medio para comunicar su significado.
    """
    text: str
    variant: str = 'light'


@dataclass(frozen=True)
class MenuSection:
    """
    Agrupación de opciones con título visible.

    Varias apps pueden aportar ítems a la misma sección, siempre que la
    declaren con el mismo `label` y `order`.
    """
    id: str
    label: str
    order: int = 100


@dataclass(frozen=True)
class MenuItem:
    """
    Opción del menú lateral.

    Es una **hoja** si tiene destino (`url_name` o `url`, excluyentes) y no
    tiene hijos, o un **contenedor** si tiene hijos y no tiene destino ni
    permisos propios: el contenedor es visible solo si algún hijo lo es.

    :param section: Solo en primer nivel; los hijos la heredan.
    :param url_name: `namespace:name`, resoluble con `reverse()` sin argumentos.
    :param url: URL externa absoluta `https://…`.
    :param icon: Nombre del parcial `templates/components/icons/<icon>.html`.
    :param permissions: Permisos `app_label.codename`; se exigen todos.
    :param visible_to_authenticated: Visible para todo usuario autenticado
        aunque no declare permisos.
    :param columns: Solo en contenedores; reparte los hijos en columnas.
    :param active_patterns: Patrones `namespace:name` (admiten comodines
        `fnmatch`) que marcan la opción como actual. Vacío equivale a
        `(url_name,)`.
    """
    id: str
    label: str
    section: Optional[str] = None
    url_name: Optional[str] = None
    url: Optional[str] = None
    icon: Optional[str] = None
    badge: Optional[Badge] = None
    permissions: tuple[str, ...] = ()
    visible_to_authenticated: bool = False
    order: int = 100
    children: tuple['MenuItem', ...] = ()
    columns: int = 1
    active_patterns: tuple[str, ...] = ()


@dataclass(frozen=True)
class UserMenuItem:
    """
    Opción del menú de usuario (área inferior del aside).

    `kind='post'` se renderiza como un formulario POST con CSRF (p. ej.,
    "Cerrar sesión"); `kind='link'`, como un enlace.
    """
    id: str
    label: str
    kind: Literal['link', 'post']
    url_name: str
    icon: Optional[str] = None
    permissions: tuple[str, ...] = ()
    visible_to_authenticated: bool = False
    order: int = 100
    divider_before: bool = False


# ── Registro ─────────────────────────────────────────────────────────────


class MenuRegistry:
    """
    Registro único del menú (Principio IV).

    Las apps registran sus declaraciones al arrancar; `CommonConfig.ready()`
    importa el módulo `menu` de cada app instalada.
    """

    def __init__(self):
        self._sections = {}
        self._items = {}
        self._user_items = {}

    def _register(self, store, obj, tipo):
        # Registrar el mismo objeto dos veces es inocuo; un id repetido con
        # otro contenido es un error de configuración.
        existente = store.get(obj.id)
        if existente is not None and existente != obj:
            raise ImproperlyConfigured(
                f'Menú: {tipo} "{obj.id}" ya está registrado con otro contenido.'
            )
        store[obj.id] = obj

    def register_section(self, section):
        self._register(self._sections, section, 'la sección')

    def register_item(self, item):
        """Registra un ítem de primer nivel; los hijos van en `children`."""
        self._register(self._items, item, 'el ítem')

    def register_user_item(self, item):
        self._register(self._user_items, item, 'la opción de usuario')

    def sections(self):
        return tuple(self._sections.values())

    def items(self):
        return tuple(self._items.values())

    def user_items(self):
        return tuple(self._user_items.values())

    @contextmanager
    def isolated(self):
        """Sustituye temporalmente el contenido del registro (uso en tests)."""
        guardado = (self._sections, self._items, self._user_items)
        self._sections, self._items, self._user_items = {}, {}, {}
        try:
            yield self
        finally:
            self._sections, self._items, self._user_items = guardado


registry = MenuRegistry()


# ── Estructuras resueltas por request ────────────────────────────────────
#
# Las produce `build_sidebar` y se entregan a las plantillas del aside
# (data-model §2). No contienen HTML.


@dataclass
class ResolvedItem:
    id: str
    label: str
    icon: Optional[str]
    badge: Optional[Badge]
    href: Optional[str]
    is_external: bool
    level: int
    children: list['ResolvedItem'] = field(default_factory=list)
    columns: list[list['ResolvedItem']] = field(default_factory=list)
    is_active: bool = False
    is_active_parent: bool = False
    # Patrones que marcan la hoja como actual; vacío en contenedores y
    # enlaces externos.
    active_patterns: tuple[str, ...] = ()


@dataclass
class ResolvedSection:
    # `id` y `label` son None para el grupo inicial sin título.
    id: Optional[str]
    label: Optional[str]
    items: list[ResolvedItem]


@dataclass
class ResolvedUserItem:
    id: str
    label: str
    icon: Optional[str]
    kind: str
    href: str
    divider_before: bool


@dataclass
class UserPanel:
    """
    Área de usuario del aside.

    `secondary` es el grupo principal del usuario; nunca el nombre de
    usuario, que es su número de documento (spec FR-021).
    """
    full_name: str
    secondary: Optional[str]
    initials: str
    items: list[ResolvedUserItem]


@dataclass
class Sidebar:
    sections: list[ResolvedSection]
    user: Optional[UserPanel] = None


# ── Construcción del árbol ───────────────────────────────────────────────


def _ordenar(declaraciones):
    """Orden estable entre hermanos y secciones: (order, label)."""
    return sorted(declaraciones, key=lambda d: (d.order, d.label))


def _es_visible(item, user):
    """
    Denegación por defecto (spec FR-006): una hoja es visible solo si se
    declara visible para todo autenticado o si el usuario tiene todos los
    permisos que declara.
    """
    if item.visible_to_authenticated:
        return True
    return bool(item.permissions) and user.has_perms(item.permissions)


def _repartir_en_columnas(children, columns):
    """
    Reparte los hijos en columnas llenando cada una de arriba hacia abajo
    (spec FR-015): k = ⌈n / c⌉ por columna y sin columnas vacías.
    """
    if not children:
        return []
    total = min(max(columns, 1), len(children))
    por_columna = math.ceil(len(children) / total)
    return [children[i:i + por_columna] for i in range(0, len(children), por_columna)]


def _resolver(item, user, level):
    """Devuelve el ítem resuelto, o None si no debe mostrarse."""
    if item.children:
        hijos = [
            resuelto
            for hijo in _ordenar(item.children)
            if (resuelto := _resolver(hijo, user, level + 1)) is not None
        ]
        # Un contenedor sin hijos visibles no se muestra (spec FR-007).
        if not hijos:
            return None
        return ResolvedItem(
            id=item.id, label=item.label, icon=item.icon, badge=item.badge,
            href=None, is_external=False, level=level,
            children=hijos, columns=_repartir_en_columnas(hijos, item.columns),
        )

    if not _es_visible(item, user):
        return None

    if item.url:
        href, is_external = item.url, True
    else:
        try:
            href, is_external = reverse(item.url_name), False
        except NoReverseMatch:
            # Una ruta no resoluble no debe romper la página (spec FR-009);
            # el system check la detecta antes de producción.
            logger.warning('Menú: no se pudo resolver %s', item.url_name)
            return None

    return ResolvedItem(
        id=item.id, label=item.label, icon=item.icon, badge=item.badge,
        href=href, is_external=is_external, level=level,
        active_patterns=item.active_patterns or ((item.url_name,) if item.url_name else ()),
    )


def _puntaje(view_name, patrones):
    """
    Puntaje de la mejor coincidencia de `view_name` con los patrones, o None.

    Precedencia (spec FR-020): la coincidencia exacta gana a un comodín y,
    entre comodines, gana el patrón más largo (el más específico).
    """
    puntajes = [
        (patron == view_name, len(patron))
        for patron in patrones
        if fnmatchcase(view_name, patron)
    ]
    return max(puntajes) if puntajes else None


def _marcar_activo(sections, request):
    """
    Marca como actual una sola hoja según la página de la request y señala
    a sus ancestros (data-model §3 regla 6). Si persiste el empate, gana la
    primera hoja en el orden del menú.
    """
    resolver_match = getattr(request, 'resolver_match', None)
    if resolver_match is None:
        return

    mejor, mejor_puntaje, mejor_ruta = None, None, ()

    def recorrer(items, ancestros):
        nonlocal mejor, mejor_puntaje, mejor_ruta
        for item in items:
            if item.children:
                recorrer(item.children, ancestros + (item,))
                continue
            puntaje = _puntaje(resolver_match.view_name, item.active_patterns)
            # Comparación estricta: ante un empate se conserva la primera.
            if puntaje is not None and (mejor_puntaje is None or puntaje > mejor_puntaje):
                mejor, mejor_puntaje, mejor_ruta = item, puntaje, ancestros

    for seccion in sections:
        recorrer(seccion.items, ())

    if mejor is not None:
        mejor.is_active = True
        for ancestro in mejor_ruta:
            ancestro.is_active_parent = True


def _inicial(termino):
    """Primer carácter alfanumérico de un término, o '' si no tiene."""
    return next((caracter for caracter in termino if caracter.isalnum()), '')


def _iniciales(user):
    """
    Iniciales del avatar (research R10): primera letra del primer nombre y
    del apellido paterno; con un solo término, sus dos primeros caracteres
    alfanuméricos. Se conservan tildes y Ñ.
    """
    nombres = user.first_name.split()
    apellidos = user.last_name.split()

    if nombres and apellidos:
        iniciales = _inicial(nombres[0]) + _inicial(apellidos[0])
    else:
        # Un solo término: el nombre, el apellido o, en último caso, el
        # nombre de usuario (p. ej., un número de documento).
        termino = (nombres or apellidos or [user.get_username()])[0]
        iniciales = ''.join(caracter for caracter in termino if caracter.isalnum())[:2]

    return iniciales.upper()


def _resolver_opcion_de_usuario(opcion, user):
    """Devuelve la opción de usuario resuelta, o None si no debe mostrarse."""
    if not _es_visible(opcion, user):
        return None
    try:
        href = reverse(opcion.url_name)
    except NoReverseMatch:
        logger.warning('Menú: no se pudo resolver %s', opcion.url_name)
        return None
    return ResolvedUserItem(
        id=opcion.id, label=opcion.label, icon=opcion.icon, kind=opcion.kind,
        href=href, divider_before=opcion.divider_before,
    )


def _panel_de_usuario(user):
    return UserPanel(
        full_name=user.get_full_name() or user.get_username(),
        secondary=user.groups.order_by('name').values_list('name', flat=True).first(),
        initials=_iniciales(user),
        items=[
            resuelta
            for opcion in _ordenar(registry.user_items())
            if (resuelta := _resolver_opcion_de_usuario(opcion, user)) is not None
        ],
    )


def build_sidebar(user, request):
    """
    Construye el menú lateral filtrado para el usuario de la request.

    Solo decide qué se **muestra**: no autoriza ni desautoriza nada. Cada
    vista destino verifica su propia autorización (spec FR-008).

    :return: `Sidebar`, o None si el usuario no está autenticado.
    """
    if user is None or not user.is_authenticated:
        return None

    secciones = {seccion.id: seccion for seccion in registry.sections()}

    # Agrupa los ítems de primer nivel por sección; None es el grupo inicial
    # sin título.
    grupos = {}
    for item in _ordenar(registry.items()):
        if item.section is not None and item.section not in secciones:
            logger.warning('Menú: la sección %s del ítem %s no está registrada', item.section, item.id)
            continue
        resuelto = _resolver(item, user, level=1)
        if resuelto is not None:
            grupos.setdefault(item.section, []).append(resuelto)

    sections = []
    if None in grupos:
        sections.append(ResolvedSection(id=None, label=None, items=grupos[None]))
    for seccion in _ordenar(secciones.values()):
        # Una sección sin opciones visibles no se muestra (spec FR-007).
        if seccion.id in grupos:
            sections.append(ResolvedSection(id=seccion.id, label=seccion.label, items=grupos[seccion.id]))

    _marcar_activo(sections, request)

    return Sidebar(sections=sections, user=_panel_de_usuario(user))
