from rest_framework import serializers
from .models import (
    User,
    Categorie,
    Individu,
    Organisation,
    Badge,
    IndividuBadge,
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'telephone',
            'type_compte',
        ]

        read_only_fields = [
            'id',
            'type_compte',
        ]


class CategorieSerializer(serializers.ModelSerializer):

    class Meta:
        model = Categorie

        fields = [
            'id',
            'nom',
            'icone',
        ]

        read_only_fields = [
            'id',
        ]


class BadgeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Badge

        fields = [
            'id',
            'nom',
            'description',
            'icone',
            'type_deblocage',
            'seuil',
            'categorie',
        ]

        read_only_fields = [
            'id',
        ]

    def validate(self, attrs):
        type_deblocage = attrs.get(
            'type_deblocage',
            getattr(
                self.instance,
                'type_deblocage',
                None
            )
        )

        categorie = attrs.get(
            'categorie',
            getattr(
                self.instance,
                'categorie',
                None
            )
        )

        if (
            type_deblocage
            == Badge.TypeDeblocage.MANUEL
        ):
            raise serializers.ValidationError(
                "Les badges manuels ne sont pas "
                "disponibles pour le moment."
            )

        if (
            type_deblocage
            == Badge.TypeDeblocage.PARTICIPATIONS_TYPE
            and categorie is None
        ):
            raise serializers.ValidationError({
                'categorie': (
                    "Une catégorie est obligatoire "
                    "pour ce type de badge."
                )
            })

        if (
            type_deblocage
            != Badge.TypeDeblocage.PARTICIPATIONS_TYPE
            and categorie is not None
        ):
            raise serializers.ValidationError({
                'categorie': (
                    "La catégorie ne peut être utilisée "
                    "que pour participations_type."
                )
            })

        return attrs


class IndividuSerializer(serializers.ModelSerializer):
    user = UserSerializer(
        read_only=True
    )
    preferences = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Categorie.objects.all(),
        required=False
    )
    badges = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )
    class Meta:
        model = Individu
        fields = [
            'id',
            'user',
            'prenom',
            'nom',
            'bio',
            'photo',
            'ville',
            'points',
            'badges',
            'preferences',
        ]

        read_only_fields = [
            'id',
            'user',
            'points',
            'badges',
        ]


class OrganisationSerializer(serializers.ModelSerializer):
    user = UserSerializer(
        read_only=True
    )
    class Meta:
        model = Organisation
        fields = [
            'id',
            'user',
            'nom',
            'description',
            'logo',
            'site_web',
            'est_verifiee',
            'ville',
        ]

        read_only_fields = [
            'id',
            'user',
            'est_verifiee',
        ]

class IndividuCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Individu
        fields = [
            'prenom',
            'nom',
            'bio',
            'photo',
            'ville',
            'preferences',
        ]

    def validate(self, attrs):
        user = self.context['request'].user

        if user.type_compte != User.TypeCompte.INDIVIDU:
            raise serializers.ValidationError(
                "Ce compte n'est pas un compte individu."
            )

        if hasattr(user, 'individu'):
            raise serializers.ValidationError(
                "Un profil individu existe déjà pour ce compte."
            )

        return attrs

    def create(self, validated_data):
        return Individu.objects.create(
            user=self.context['request'].user,
            **validated_data
        )
        
class IndividuBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(
        read_only=True
    )
    class Meta:
        model = IndividuBadge
        fields = [
            'id',
            'badge',
            'date_obtention',
        ]

        read_only_fields = [
            'id',
            'badge',
            'date_obtention',
        ]
        
class IndividuCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Individu
        fields = [
            'prenom',
            'nom',
            'bio',
            'photo',
            'ville',
            'preferences',
        ]

    def validate(self, attrs):
        user = self.context['request'].user

        if user.type_compte != User.TypeCompte.INDIVIDU:
            raise serializers.ValidationError(
                "Ce compte n'est pas un compte individu."
            )

        if hasattr(user, 'individu'):
            raise serializers.ValidationError(
                "Un profil individu existe déjà pour ce compte."
            )

        return attrs

    def create(self, validated_data):
        return Individu.objects.create(
            user=self.context['request'].user,
            **validated_data
        )
        
class OrganisationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = [
            'nom',
            'description',
            'logo',
            'site_web',
            'ville',
        ]

    def validate(self, attrs):
        user = self.context['request'].user

        if user.type_compte != User.TypeCompte.ORGANISATION:
            raise serializers.ValidationError(
                "Ce compte n'est pas un compte organisation."
            )

        if hasattr(user, 'organisation'):
            raise serializers.ValidationError(
                "Un profil organisation existe déjà pour ce compte."
            )

        return attrs

    def create(self, validated_data):
        return Organisation.objects.create(
            user=self.context['request'].user,
            **validated_data
        )  
        
class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'type_compte',
            'telephone',
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        return user                      