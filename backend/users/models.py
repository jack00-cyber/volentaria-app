from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class User(AbstractUser):

    class TypeCompte(models.TextChoices):
        INDIVIDU = 'individu', 'Individu'
        ORGANISATION = 'organisation', 'Organisation'

    type_compte = models.CharField(
        max_length=20,
        choices=TypeCompte.choices
    )

    telephone = models.CharField(
        max_length=20,
        blank=True
    )

    date_creation = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.username


class Categorie(models.Model):
    nom = models.CharField(
        max_length=50,
        unique=True
    )

    icone = models.CharField(
        max_length=50,
        blank=True
    )

    class Meta:
        ordering = ['nom']
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'

    def __str__(self):
        return self.nom


class Badge(models.Model):

    class TypeDeblocage(models.TextChoices):
        POINTS = 'points', 'Points cumulés'
        PARTICIPATIONS = 'participations', 'Nombre total de participations'
        PARTICIPATIONS_TYPE = (
            'participations_type',
            "Participations dans une catégorie"
        )
        MANUEL = 'manuel', 'Manuel (remis IRL)'

    nom = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    icone = models.ImageField(
        upload_to='badges/',
        blank=True,
        null=True
    )

    type_deblocage = models.CharField(
        max_length=30,
        choices=TypeDeblocage.choices,
        default=TypeDeblocage.POINTS
    )

    seuil = models.PositiveIntegerField(
        default=0
    )

    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='badges',
        help_text=(
            "Requis uniquement si le type de déblocage "
            "est participations_type."
        )
    )

    def clean(self):
        if self.type_deblocage == self.TypeDeblocage.MANUEL:
            raise ValidationError(
                "Les badges manuels ne sont pas disponibles pour le moment."
            )

        if (
            self.type_deblocage == self.TypeDeblocage.PARTICIPATIONS_TYPE
            and self.categorie_id is None
        ):
            raise ValidationError(
                "Une catégorie doit être choisie pour un badge "
                "de type participations_type."
            )

        if (
            self.type_deblocage != self.TypeDeblocage.PARTICIPATIONS_TYPE
            and self.categorie_id is not None
        ):
            raise ValidationError(
                "Une catégorie ne peut être utilisée que pour "
                "un badge de type participations_type."
            )

    def __str__(self):
        return self.nom


class Individu(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='individu'
    )

    prenom = models.CharField(
        max_length=100
    )

    nom = models.CharField(
        max_length=100
    )

    bio = models.TextField(
        blank=True
    )

    photo = models.ImageField(
        upload_to='individus/',
        blank=True,
        null=True
    )

    points = models.PositiveIntegerField(
        default=0
    )

    badges = models.ManyToManyField(
        Badge,
        through='IndividuBadge',
        related_name='individus'
    )

    ville = models.CharField(
        max_length=100,
        blank=True
    )

    preferences = models.ManyToManyField(
        Categorie,
        related_name='individus',
        blank=True
    )

    def ajouter_points(self, montant):
        if montant <= 0:
            return

        self.points += montant
        self.save(update_fields=['points'])

        self._verifier_badges_points()

    def _verifier_badges_points(self):
        deja_obtenus = self.badges.values_list(
            'id',
            flat=True
        )

        badges = Badge.objects.filter(
            type_deblocage=Badge.TypeDeblocage.POINTS,
            seuil__lte=self.points
        ).exclude(
            id__in=deja_obtenus
        )

        for badge in badges:
            IndividuBadge.objects.get_or_create(
                individu=self,
                badge=badge
            )

    def __str__(self):
        return f"{self.prenom} {self.nom}"


class IndividuBadge(models.Model):

    individu = models.ForeignKey(
        Individu,
        on_delete=models.CASCADE
    )

    badge = models.ForeignKey(
        Badge,
        on_delete=models.CASCADE
    )

    date_obtention = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['individu', 'badge'],
                name='unique_individu_badge'
            )
        ]

    def __str__(self):
        return f"{self.individu} — {self.badge}"


class Organisation(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='organisation'
    )

    nom = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    logo = models.ImageField(
        upload_to='organisations/',
        blank=True,
        null=True
    )

    site_web = models.URLField(
        blank=True
    )

    est_verifiee = models.BooleanField(
        default=False
    )

    ville = models.CharField(
        max_length=30
    )

    def __str__(self):
        return self.nom
