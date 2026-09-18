from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from users.models import User, Individu


class Evenement(models.Model):
    class TypeInscription(models.TextChoices):
        DIRECTE = 'directe', 'Inscription directe'
        DOSSIER = 'dossier', 'Sur dossier (validation requise)'

    class Statut(models.TextChoices):
        PUBLIE = 'publie', 'Publié'
        ANNULE = 'annule', 'Annulé'
        TERMINE = 'termine', 'Terminé'

    titre = models.CharField(max_length=200)
    description = models.TextField()
    organisateur_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    organisateur_object_id = models.PositiveIntegerField()
    organisateur = GenericForeignKey(
        'organisateur_content_type',
        'organisateur_object_id'
    )
    categories = models.ManyToManyField(
        'users.Categorie',
        related_name='evenements'
    )
    adresse = models.CharField(
        max_length=255
    )
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    capacite_max = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    type_inscription = models.CharField(
        max_length=20,
        choices=TypeInscription.choices,
        default=TypeInscription.DIRECTE
    )
    statut = models.CharField(
        max_length=20,
        choices=Statut.choices,
        default=Statut.PUBLIE
    )
    points_recompense = models.PositiveIntegerField(
        default=0
    )
    date_creation = models.DateTimeField(
        auto_now_add=True
    )
    def clean(self):
        if (
            self.date_fin
            and self.date_debut
            and self.date_fin <= self.date_debut
        ):
            raise ValidationError(
                "La date de fin doit être après la date de début."
            )

    @property
    def nombre_participants_confirmes(self):
        return self.participations.filter(
            statut__in=[
                Participation.Statut.ACCEPTE,
                Participation.Statut.TERMINE
            ]
        ).count()

    @property
    def est_complet(self):
        if self.capacite_max is None:
            return False

        return (
            self.nombre_participants_confirmes
            >= self.capacite_max
        )

    def __str__(self):
        return self.titre


class Participation(models.Model):
    class Statut(models.TextChoices):
        EN_ATTENTE = ( 'en_attente','En attente de validation')
        ACCEPTE = ('accepte','Accepté')
        REFUSE = ('refuse', 'Refusé')
        ANNULE = ( 'annule',  'Annulé par le participant'  )
        TERMINE = ( 'termine',  'Participation terminée'  )
        
    individu = models.ForeignKey(
        Individu,
        on_delete=models.CASCADE,
        related_name='participations'
    )
    evenement = models.ForeignKey(
        Evenement,
        on_delete=models.CASCADE,
        related_name='participations'
    )
    statut = models.CharField(
        max_length=20,
        choices=Statut.choices,
        default=Statut.EN_ATTENTE
    )
    message_candidature = models.TextField(
        blank=True
    )
    cv = models.FileField(
        upload_to='cv/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf']
            )
        ],
        help_text=(
            "CV en PDF, utilisé pour l'inscription "
            "sur dossier."
        )
    )
    date_inscription = models.DateTimeField(
        auto_now_add=True
    )
    date_traitement = models.DateTimeField(
        null=True,
        blank=True
    )
    points_attribues = models.BooleanField(
        default=False
    )
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['individu', 'evenement'],
                name='unique_individu_evenement'
            )
        ]

        ordering = ['-date_inscription']

    def clean(self):
        if (
            self.evenement_id
            and self.evenement.type_inscription
            == Evenement.TypeInscription.DOSSIER
        ):
            if (
                not self.message_candidature
                and not self.cv
            ):
                raise ValidationError(
                    "Une lettre de motivation ou un CV "
                    "(PDF) est requis pour une inscription "
                    "sur dossier."
                )

    def __str__(self):
        return (
            f"{self.individu} → "
            f"{self.evenement} "
            f"({self.statut})"
        )


