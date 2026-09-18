from rest_framework import serializers
from users.models import Categorie
from .models import Evenement, Participation

class EvenementSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Categorie.objects.all()
    )

    organisateur = serializers.SerializerMethodField()

    nombre_participants_confirmes = serializers.IntegerField(
        read_only=True,
        source='nombre_participants_confirmes'
    )

    est_complet = serializers.BooleanField(
        read_only=True
    )

    class Meta:
        model = Evenement

        fields = [
            'id',
            'titre',
            'description',
            'organisateur',
            'categories',
            'adresse',
            'date_debut',
            'date_fin',
            'capacite_max',
            'type_inscription',
            'statut',
            'points_recompense',
            'nombre_participants_confirmes',
            'est_complet',
            'date_creation',
        ]

        read_only_fields = [
            'id',
            'organisateur',
            'statut',
            'nombre_participants_confirmes',
            'est_complet',
            'date_creation',
        ]

    def get_organisateur(self, obj):
        organisateur = obj.organisateur

        if organisateur is None:
            return None

        if isinstance(organisateur, type(
            getattr(
                organisateur,
                'individu',
                None
            )
        )):
            pass

        if hasattr(organisateur, 'prenom'):
            return {
                'type': 'individu',
                'id': organisateur.id,
                'nom': (
                    f"{organisateur.prenom} "
                    f"{organisateur.nom}"
                )
            }

        if hasattr(organisateur, 'nom'):
            return {
                'type': 'organisation',
                'id': organisateur.id,
                'nom': organisateur.nom
            }

        return None


class ParticipationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Participation

        fields = [
            'id',
            'individu',
            'evenement',
            'statut',
            'message_candidature',
            'cv',
            'date_inscription',
            'date_traitement',
            'points_attribues',
        ]

        read_only_fields = [
            'id',
            'individu',
            'statut',
            'date_inscription',
            'date_traitement',
            'points_attribues',
        ]

    def validate(self, attrs):
        evenement = self.context.get('evenement')

        if (
            evenement
            and evenement.type_inscription
            == Evenement.TypeInscription.DOSSIER
        ):
            message = attrs.get(
                'message_candidature',
                ''
            )

            cv = attrs.get('cv')

            if not message and not cv:
                raise serializers.ValidationError({
                    'message_candidature': (
                        "Une lettre de motivation ou "
                        "un CV est requis."
                    )
                })

        return attrs