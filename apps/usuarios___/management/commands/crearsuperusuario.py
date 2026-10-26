import getpass

from django.contrib.auth import get_user_model
from django.core import exceptions
from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS
from django.utils.translation import gettext as _

from apps.personas.choices import EstadoCivil, Genero, TipoDocumento
from apps.personas.validators import PATRONES_DOCUMENTO


class Command(BaseCommand):
    help = "Crea un superusuario con el número de documento como nombre de usuario."

    def add_arguments(self, parser):
        parser.add_argument("--noinput", action="store_false", dest="interactive", help=("No pedir entrada de forma interactiva."))
        parser.add_argument("--database", default=DEFAULT_DB_ALIAS)
        parser.add_argument("--tipo-documento", choices=TipoDocumento.values)
        parser.add_argument("--numero-documento")
        parser.add_argument("--email")
        parser.add_argument("--password")
        parser.add_argument("--nombres")
        parser.add_argument("--apellido-paterno")
        parser.add_argument("--apellido-materno")
        parser.add_argument("--fecha-nacimiento")
        parser.add_argument("--genero", choices=[g for g in Genero.values if g])
        parser.add_argument("--estado-civil", choices=EstadoCivil.values)

    def handle(self, *args, **options):
        try:
            UserModel = get_user_model()
            database = options["database"]
            interactive = options["interactive"]

            def get_data():
                return {
                    "tipo_documento": options.get("tipo_documento"),
                    "numero_documento": options.get("numero_documento"),
                    "email": options.get("email"),
                    "password": options.get("password"),
                    "nombres": options.get("nombres"),
                    "apellido_paterno": options.get("apellido_paterno"),
                    "apellido_materno": options.get("apellido_materno"),
                    "fecha_nacimiento": options.get("fecha_nacimiento") or None,
                    "genero": options.get("genero") or None,
                    "estado_civil": options.get("estado_civil") or None,
                }

            data = get_data()

            if interactive:
                self.stdout.write(_("\nCreación de superusuario\n"))
                data["tipo_documento"] = self._prompt_tipo_documento(data["tipo_documento"])
                data["numero_documento"] = self._prompt(
                    "--- Número de documento (nombre de usuario)", data["numero_documento"]
                )
                data["email"] = self._prompt("--- Correo electrónico", data["email"])
                data["password"] = self._prompt_password(data["password"])
                data["nombres"] = self._prompt("--- Nombres", data["nombres"])
                data["apellido_paterno"] = self._prompt("--- Apellido paterno", data["apellido_paterno"])
                data["apellido_materno"] = self._prompt("--- Apellido materno", data["apellido_materno"])
                data["fecha_nacimiento"] = self._prompt(
                    "--- Fecha de nacimiento (AAAA-MM-DD, opcional)", data["fecha_nacimiento"]
                ) or None
                data["genero"] = self._prompt_choice(
                    "Género", Genero.choices, data["genero"]
                )
                data["estado_civil"] = self._prompt_choice(
                    "Estado civil", EstadoCivil.choices, data["estado_civil"]
                )

            missing = [k for k, v in data.items() if not v]
            if data["password"] is None or data["password"] == "":
                missing.append("password")
            if missing and not interactive:
                raise CommandError("Faltan valores obligatorios: %s" % ", ".join(missing))

            try:
                UserModel.objects.db_manager(database).create_superuser(**data)
            except exceptions.ValidationError as exc:
                raise CommandError("; ".join(str(msg) for msg in exc.messages))
            except Exception as exc:
                raise CommandError(str(exc))

            self.stdout.write(self.style.SUCCESS(
                _("Superusuario creado correctamente (nombre de usuario: %s).")
                % data["numero_documento"]
            ))
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Operación cancelada por el usuairo'))
            return

    def _prompt(self, label, default=None):
        prompt = "%s: " % label
        value = input(prompt).strip()
        if not value:
            if default:
                return default
            raise CommandError(_("%s es obligatorio." % label))
        return value

    def _prompt_password(self, default=None):
        while True:
            password = getpass.getpass("Contraseña: ").strip()
            if not password:
                if default:
                    return default
                self.stderr.write("La contraseña no puede estar vacía.")
                continue
            confirm = getpass.getpass("Confirme la contraseña: ").strip()
            if password != confirm:
                self.stderr.write("Las contraseñas no coinciden. Intente de nuevo.")
                continue
            return password

    def _prompt_tipo_documento(self, default=None):
        options = "".join(
            "  [%s] %s\n" % (v, label)
            for v, label in TipoDocumento.choices
        )
        value = default
        while not value:
            self.stdout.write("Tipo de documento:\n%s  >>> " % options)
            valor = input().strip().upper()
            if valor in PATRONES_DOCUMENTO:
                value = valor
            else:
                self.stderr.write("Opción no válida.")
        return value

    def _prompt_choice(self, label, choices, default=None):
        if default:
            return default
        options = "".join("  [%s] %s\n" % (value, name) for value, name in choices)
        while True:
            self.stdout.write("%s:\n%s  >>> " % (label, options))
            valor = input().strip().upper()
            if valor in dict(choices):
                return valor
            self.stderr.write("Opción no válida.")