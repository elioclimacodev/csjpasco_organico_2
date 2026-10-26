from django import forms
from collections import defaultdict

class TreeModelChoiceField(forms.ModelChoiceField):
    """
    Campo de selección para modelos recursivos (árboles) en Django.
    Genera las opciones formateadas con sangría jerárquica y excluye
    automáticamente la instancia actual y sus descendientes en la edición.
    """
    def __init__(self, *args, **kwargs):
        self.indent_char = kwargs.pop('indent_char', '— ')
        self.indent_factor = kwargs.pop('indent_factor', 1)
        self.order_by = kwargs.pop('order_by', 'nombre')
        self.parent_field_name = kwargs.pop('parent_field', 'sede_superior')
        super().__init__(*args, **kwargs)

    def _get_tree_choices(self):
        """
        Genera la lista estructurada en árbol de tuplas (id, label).
        """
        instance = getattr(self, 'instance', None)
        instance_pk = instance.pk if (instance and instance.pk) else None

        # 1. Traer todos los objetos válidos ordenados
        queryset = self.queryset.order_by(self.order_by)
        all_nodes = list(queryset)

        # 2. Agrupar por nodo padre {padre_id: [hijos]}
        tree_map = defaultdict(list)
        roots = []

        for node in all_nodes:
            parent_id = getattr(node, f"{self.parent_field_name}_id")
            if parent_id is None:
                roots.append(node)
            else:
                tree_map[parent_id].append(node)

        # 3. Identificar la instancia actual y sus descendientes a excluir
        excluded_ids = set()
        if instance_pk:
            def mark_descendants(node_id):
                excluded_ids.add(node_id)
                for child in tree_map[node_id]:
                    mark_descendants(child.pk)
            
            if instance_pk in [n.pk for n in all_nodes] or any(getattr(n, f"{self.parent_field_name}_id") == instance_pk for n in all_nodes):
                mark_descendants(instance_pk)

        # 4. Construir la lista final mediante DFS (Recorrido en Profundidad)
        choices = []
        if self.empty_label:
            choices.append(('', self.empty_label))

        visited = set()

        def build_tree_choices(nodes, depth=0):
            for node in nodes:
                if node.pk in visited or node.pk in excluded_ids:
                    continue

                visited.add(node.pk)
                
                # Formatear el texto jerárquico
                indent = (self.indent_char * self.indent_factor) * depth
                label = f"{indent}{node}"
                
                choices.append((node.pk, label))
                
                if node.pk in tree_map:
                    build_tree_choices(tree_map[node.pk], depth + 1)

        build_tree_choices(roots, depth=0)
        return choices

    @property
    def choices(self):
        """
        Sobrescribe la propiedad choices para retornar nuestro árbol dinámico.
        """
        return self._get_tree_choices()

    @choices.setter
    def choices(self, value):
        """
        Permite que Django asigne valores internamente si lo requiere, 
        evitando el error de atributo de solo lectura.
        """
        pass

    def __deepcopy__(self, memo):
        result = super().__deepcopy__(memo)
        result.indent_char = self.indent_char
        result.indent_factor = self.indent_factor
        result.order_by = self.order_by
        result.parent_field_name = self.parent_field_name
        return result