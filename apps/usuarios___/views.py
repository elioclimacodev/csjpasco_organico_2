from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import ProtectedError, Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from apps.personas.choices import TipoDocumento
from .forms import PerfilForm, PersonaForm, RegistroUsuarioForm
from .models import Persona


def home(request):
    if request.user.is_authenticated:
        return redirect("perfil")
    return redirect("login")


def registro(request):
    if request.user.is_authenticated:
        return redirect("perfil")
    form = RegistroUsuarioForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(
            request,
            _("Cuenta creada correctamente. Bienvenido/a, %(nombre)s.")
            % {"nombre": user.persona.nombres},
        )
        return redirect("perfil")
    context = {
        'form': form,
        'title': 'Registro de usuarios',
        'container_size': 'narrow',
    }
    return render(request, "registration/signup.html", context)


@login_required
def perfil(request):
    form = PerfilForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Tu perfil se actualizó correctamente."))
        return redirect("perfil")
    context = {
        "form": form,
        "usuario": request.user,
        "tipo_documento": request.user.persona.tipo_documento,
        "numero_documento": request.user.persona.numero_documento,
    }
    return render(request, "usuarios/perfil.html", context)


class PersonaListView(PermissionRequiredMixin, ListView):
    model = Persona
    template_name = "usuarios/persona_list.html"
    context_object_name = "personas"
    permission_required = "usuarios.view_persona"
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset()
        busqueda = self.request.GET.get("q", "").strip()
        tipo = self.request.GET.get("tipo_documento", "").strip()
        if busqueda:
            queryset = queryset.filter(
                Q(numero_documento__icontains=busqueda)
                | Q(nombres__icontains=busqueda)
                | Q(apellido_paterno__icontains=busqueda)
                | Q(apellido_materno__icontains=busqueda)
                | Q(email__icontains=busqueda)
            )
        if tipo:
            queryset = queryset.filter(tipo_documento=tipo)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["busqueda"] = self.request.GET.get("q", "")
        context["filtro_tipo"] = self.request.GET.get("tipo_documento", "")
        context["tipo_opciones"] = TipoDocumento.choices
        return context


class PersonaDetailView(PermissionRequiredMixin, DetailView):
    model = Persona
    template_name = "usuarios/persona_detail.html"
    context_object_name = "persona"
    permission_required = "usuarios.view_persona"


class PersonaCreateView(PermissionRequiredMixin, CreateView):
    model = Persona
    form_class = PersonaForm
    template_name = "usuarios/persona_form.html"
    permission_required = "usuarios.add_persona"
    success_url = reverse_lazy("persona_lista")

    def form_valid(self, form):
        messages.success(self.request, _("Persona registrada correctamente."))
        return super().form_valid(form)


class PersonaUpdateView(PermissionRequiredMixin, UpdateView):
    model = Persona
    form_class = PersonaForm
    template_name = "usuarios/persona_form.html"
    permission_required = "usuarios.change_persona"
    success_url = reverse_lazy("persona_lista")

    def form_valid(self, form):
        messages.success(self.request, _("Persona actualizada correctamente."))
        return super().form_valid(form)


class PersonaDeleteView(PermissionRequiredMixin, DeleteView):
    model = Persona
    template_name = "usuarios/persona_confirm_delete.html"
    context_object_name = "persona"
    permission_required = "usuarios.delete_persona"
    success_url = reverse_lazy("persona_lista")

    def form_valid(self, form):
        persona = self.get_object()
        if persona.tiene_usuario:
            messages.error(
                self.request,
                _(
                    "No se puede eliminar porque la persona tiene cuenta de usuario. "
                    "Use el estado 'Activo' para desactivarla."
                ),
            )
            return redirect("persona_detalle", pk=persona.pk)
        try:
            respuesta = super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                _("No se puede eliminar la persona porque está referenciada por otros registros."),
            )
            return redirect("persona_detalle", pk=persona.pk)
        messages.success(self.request, _("Persona eliminada correctamente."))
        return respuesta