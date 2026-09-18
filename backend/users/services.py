from .models import (
    Badge,
    IndividuBadge,
)


def verifier_badges_participations(individu):

    from events.models import Participation

    deja_obtenus = set(
        individu.badges.values_list(
            'id',
            flat=True
        )
    )

    participations_terminees = Participation.objects.filter(
        individu=individu,
        statut=Participation.Statut.TERMINE
    )

    total = participations_terminees.count()

    badges_totaux = Badge.objects.filter(
        type_deblocage=Badge.TypeDeblocage.PARTICIPATIONS,
        seuil__lte=total
    ).exclude(
        id__in=deja_obtenus
    )

    for badge in badges_totaux:

        IndividuBadge.objects.get_or_create(
            individu=individu,
            badge=badge
        )

        deja_obtenus.add(
            badge.id
        )

    badges_categories = Badge.objects.filter(
        type_deblocage=Badge.TypeDeblocage.PARTICIPATIONS_TYPE
    ).exclude(
        id__in=deja_obtenus
    ).select_related(
        'categorie'
    )

    for badge in badges_categories:

        if badge.categorie_id is None:
            continue

        nombre = participations_terminees.filter(
            evenement__categories=badge.categorie
        ).count()

        if nombre >= badge.seuil:

            IndividuBadge.objects.get_or_create(
                individu=individu,
                badge=badge
            )