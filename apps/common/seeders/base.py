# core/seeders/base.py
import logging
from typing import Callable, Type
from django.db import transaction, models
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


def seed_model(
    model: Type[models.Model],
    data: list[dict],
    *,
    natural_key: str = "id",
    update_existing: bool = True,
    batch_size: int = 1000,
) -> dict:
    """
    Inserta datos en un modelo Django de forma idempotente.
    MODIFICADO: Usa full_clean() y save() para garantizar que se 
    ejecuten todas las validaciones y normalizaciones del modelo.
    """
    stats = {"created": 0, "updated": 0, "skipped": 0}
    if not data:
        return stats

    keys = [d[natural_key] for d in data if natural_key in d]
    
    # Optimización: traemos todas las instancias existentes en una sola consulta
    existing_instances = {
        getattr(obj, natural_key): obj 
        for obj in model.objects.filter(**{f"{natural_key}__in": keys})
    }

    for item in data:
        pk = item.get(natural_key)
        
        if pk in existing_instances:
            if update_existing:
                instance = existing_instances[pk]
                fields = {k: v for k, v in item.items() if k != natural_key}
                
                for k, v in fields.items():
                    setattr(instance, k, v)
                
                # SOLUCIÓN PUNTO 5: Ejecutamos validaciones antes de guardar
                # Esto llamará a instance.clean() y validará unicidad.
                instance.full_clean()
                instance.save()
                stats["updated"] += 1
            else:
                stats["skipped"] += 1
        else:
            instance = model(**item)
            
            # SOLUCIÓN PUNTO 5: Ejecutamos validaciones antes de guardar
            instance.full_clean()
            instance.save()
            stats["created"] += 1

    return stats


def run_seeders(name: str, *seeders: Callable[[], dict]) -> dict:
    """
    Ejecuta una secuencia de seeders en orden, dentro de una transacción.
    """
    logger.info("Iniciando seeding '%s'", name)
    results = {}

    with transaction.atomic():
        for seeder in seeders:
            logger.info("  → %s ...", seeder.__name__)
            results[seeder.__name__] = seeder()
            logger.info("    %s", results[seeder.__name__])

    logger.info("Seeding '%s' finalizado: %s", name, results)
    return results