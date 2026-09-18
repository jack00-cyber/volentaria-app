from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Evenement, Participation


def individu_a_conflit(individu, evenement):
    return Participation.objects.filter(
        individu=individu,
        statut=Participation.Statut.ACCEPTE,
        evenement__date_debut__lt=evenement.date_fin,
        evenement__date_fin__gt=evenement.date_debut,
    ).exclude(
        evenement=evenement
    ).exists()


@transaction.atomic
def creer_participation(
    individu,
    evenement,
    message_candidature='',
    cv=None
):

    evenement = Evenement.objects.select_for_update().get(
        pk=evenement.pk
    )

    if evenement.statut != Evenement.Statut.PUBLIE:
        raise ValidationError(
            "Cet événement n'est plus disponible."
        )

    if timezone.now() >= evenement.date_debut:
        raise ValidationError(
            "L'inscription est fermée."
        )

    if Participation.objects.filter(
        individu=individu,
        evenement=evenement
    ).exists():
        raise ValidationError(
            "Vous avez déjà une participation pour cet événement."
        )

    if evenement.capacite_max is not None:

        nombre = evenement.participations.filter(
            statut=Participation.Statut.ACCEPTE
        ).count()

        if nombre >= evenement.capacite_max:
            raise ValidationError(
                "Cet événement est complet."
            )

    if evenement.type_inscription == (
        Evenement.TypeInscription.DIRECTE
    ):

        if individu_a_conflit(
            individu,
            evenement
        ):
            raise ValidationError(
                "Vous participez déjà à un autre événement "
                "sur ce créneau."
            )

        statut = Participation.Statut.ACCEPTE

    else:

        if not message_candidature and not cv:
            raise ValidationError(
                "Une lettre de motivation ou un CV est requis."
            )

        statut = Participation.Statut.EN_ATTENTE

    participation = Participation.objects.create(
        individu=individu,
        evenement=evenement,
        statut=statut,
        message_candidature=message_candidature,
        cv=cv
    )

    if statut == Participation.Statut.ACCEPTE:
        from users.services import verifier_badges_participations

    return participation

@transaction.atomic
def accepter_participation(
    participation
):

    participation = Participation.objects.select_for_update().select_related(
        'individu',
        'evenement'
    ).get(
        pk=participation.pk
    )

    evenement = Evenement.objects.select_for_update().get(
        pk=participation.evenement_id
    )

    if participation.statut != Participation.Statut.EN_ATTENTE:
        raise ValidationError(
            "Cette candidature n'est plus en attente."
        )

    if evenement.statut != Evenement.Statut.PUBLIE:
        raise ValidationError(
            "Cet événement n'est plus disponible."
        )

    if evenement.capacite_max is not None:

        nombre = evenement.participations.filter(
            statut=Participation.Statut.ACCEPTE
        ).count()

        if nombre >= evenement.capacite_max:
            raise ValidationError(
                "La capacité maximale est atteinte."
            )

    if individu_a_conflit(
        participation.individu,
        evenement
    ):
        raise ValidationError(
            "Cet individu participe déjà à un autre "
            "événement sur ce créneau."
        )

    participation.statut = Participation.Statut.ACCEPTE
    participation.date_traitement = timezone.now()

    participation.save(
        update_fields=[
            'statut',
            'date_traitement'
        ]
    )

    from users.services import verifier_badges_participations
    
    return participation

@transaction.atomic
def refuser_participation(
    participation
):

    participation.statut = Participation.Statut.REFUSE
    participation.date_traitement = timezone.now()

    participation.save(
        update_fields=[
            'statut',
            'date_traitement'
        ]
    )

    return participation

def annuler_participation(
    participation
):

    if participation.statut not in [
        Participation.Statut.EN_ATTENTE,
        Participation.Statut.ACCEPTE
    ]:
        raise ValidationError(
            "Cette participation ne peut plus être annulée."
        )

    participation.statut = Participation.Statut.ANNULE

    participation.save(
        update_fields=['statut']
    )

    return participation

@transaction.atomic
def terminer_evenement(evenement):

    evenement = Evenement.objects.select_for_update().get(
        pk=evenement.pk
    )

    if evenement.statut == Evenement.Statut.TERMINE:
        return evenement

    if evenement.statut == Evenement.Statut.ANNULE:
        raise ValidationError(
            "Un événement annulé ne peut pas être terminé."
        )

    maintenant = timezone.now()

    if maintenant < evenement.date_fin:
        raise ValidationError(
            "L'événement n'est pas encore terminé."
        )

    participations = Participation.objects.filter(
        evenement=evenement,
        statut=Participation.Statut.ACCEPTE
    ).select_related('individu')

    for participation in participations:

        participation.statut = Participation.Statut.TERMINE

        if not participation.points_attribues:

            participation.individu.ajouter_points(
                evenement.points_recompense
            )

            participation.points_attribues = True

        participation.save(
            update_fields=[
                'statut',
                'points_attribues'
            ]
        )

    evenement.statut = Evenement.Statut.TERMINE

    evenement.save(
        update_fields=['statut']
    )

    return evenement