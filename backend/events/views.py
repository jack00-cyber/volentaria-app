from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from users.models import User, Individu, Organisation
from django.contrib.contenttypes.models import ContentType
from rest_framework.views import APIView
from .models import (
    Evenement,
    Participation
)
from .serializers import (
    EvenementSerializer,
    ParticipationSerializer
)
from .services import (
    creer_participation,
    accepter_participation,
    refuser_participation,
    annuler_participation,
    terminer_evenement,
)
from users.permissions import IsOrganisateurEvenement

class EvenementListCreateView(generics.ListCreateAPIView):

    queryset = Evenement.objects.all()
    serializer_class = EvenementSerializer
    permission_classes = [
        IsAuthenticated
    ]

    def perform_create(self, serializer):

        user = self.request.user

        if user.type_compte == User.TypeCompte.INDIVIDU:

            profil = get_object_or_404(
                Individu,
                user=user
            )

        elif user.type_compte == User.TypeCompte.ORGANISATION:

            profil = get_object_or_404(
                Organisation,
                user=user
            )

        else:
            raise ValidationError(
                "Type de compte invalide."
            )

        content_type = ContentType.objects.get_for_model(
            profil
        )

        serializer.save(
            organisateur_content_type=content_type,
            organisateur_object_id=profil.id
        )
        
class EvenementDetailView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Evenement.objects.all()
    serializer_class = EvenementSerializer
    permission_classes = [
        IsAuthenticated,
        IsOrganisateurEvenement
    ]        
    
class ParticiperEvenementView(generics.CreateAPIView):

    serializer_class = ParticipationSerializer
    permission_classes = [
        IsAuthenticated
    ]

    def create(self, request, *args, **kwargs):

        user = request.user

        if user.type_compte != User.TypeCompte.INDIVIDU:
            return Response(
                {
                    'detail': (
                        "Seuls les individus peuvent "
                        "participer à un événement."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        individu = get_object_or_404(
         Individu,
         user=user
        )

        evenement = get_object_or_404(
            Evenement,
            pk=kwargs['pk']
        )

        serializer = self.get_serializer(
            data=request.data,
            context={
                'request': request,
                'evenement': evenement
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:

            participation = creer_participation(
                individu=individu,
                evenement=evenement,
                message_candidature=serializer.validated_data.get(
                    'message_candidature',
                    ''
                ),
                cv=serializer.validated_data.get(
                    'cv'
                )
            )

        except ValidationError as e:

            return Response(
                {'detail': e.message},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            ParticipationSerializer(
                participation
            ).data,
            status=status.HTTP_201_CREATED
        )    
        
class MesParticipationsView(generics.ListAPIView):
    serializer_class = ParticipationSerializer
    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):

        if self.request.user.type_compte != (
            User.TypeCompte.INDIVIDU
        ):
            return Participation.objects.none()

        return Participation.objects.filter(
            individu__user=self.request.user
        ).select_related(
            'evenement'
        )        
        
class ParticipantsEvenementView(generics.ListAPIView):

    serializer_class = ParticipationSerializer
    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):

        evenement = get_object_or_404(
            Evenement,
            pk=self.kwargs['pk']
        )

        user = self.request.user

        if user.type_compte == User.TypeCompte.INDIVIDU:

            if evenement.organisateur != getattr(
                user,
                'individu',
                None
            ):
                return Participation.objects.none()

        elif user.type_compte == User.TypeCompte.ORGANISATION:

            if evenement.organisateur != getattr(
                user,
                'organisation',
                None
            ):
                return Participation.objects.none()

        else:
            return Participation.objects.none()

        return Participation.objects.filter(
            evenement=evenement
        ).select_related(
            'individu'
        )   
        
class AccepterParticipationView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request, pk):

        participation = get_object_or_404(
            Participation,
            pk=pk
        )

        evenement = participation.evenement

        if evenement.organisateur != (
            getattr(request.user, 'individu', None)
            or getattr(request.user, 'organisation', None)
        ):
            return Response(
                {'detail': 'Permission refusée.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:

            participation = accepter_participation(
                participation
            )

        except ValidationError as e:

            return Response(
                {'detail': e.message},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            ParticipationSerializer(
                participation
            ).data
        )    
        
class RefuserParticipationView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request, pk):

        participation = get_object_or_404(
            Participation,
            pk=pk
        )

        evenement = participation.evenement

        if evenement.organisateur != (
            getattr(request.user, 'individu', None)
            or getattr(request.user, 'organisation', None)
        ):
            return Response(
                {'detail': 'Permission refusée.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:

            participation = refuser_participation(
                participation
            )

        except ValidationError as e:

            return Response(
                {'detail': e.message},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            ParticipationSerializer(
                participation
            ).data
        )
        
class AnnulerParticipationView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request, pk):

        participation = get_object_or_404(
            Participation,
            pk=pk
        )

        if participation.individu.user != request.user:
            return Response(
                {'detail': 'Permission refusée.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:

            participation = annuler_participation(
                participation
            )

        except ValidationError as e:

            return Response(
                {'detail': e.message},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            ParticipationSerializer(
                participation
            ).data
        )
        
class TerminerEvenementView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request, pk):

        evenement = get_object_or_404(
            Evenement,
            pk=pk
        )

        organisateur = (
            getattr(request.user, 'individu', None)
            or getattr(request.user, 'organisation', None)
        )

        if evenement.organisateur != organisateur:
            return Response(
                {'detail': 'Permission refusée.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:

            evenement = terminer_evenement(
                evenement
            )

        except ValidationError as e:

            return Response(
                {'detail': e.message},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            EvenementSerializer(
                evenement
            ).data
        )                                 
