from django.core import serializers
from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import (
    User,
    Categorie,
    Individu,
    Organisation,
    Badge,
)
from .serializers import (
    UserSerializer,
    CategorieSerializer,
    IndividuSerializer,
    OrganisationSerializer,
    BadgeSerializer,
    IndividuCreateSerializer,
    OrganisationCreateSerializer,
    UserCreateSerializer,
)

class ProfilView(APIView):
    permission_classes = [
        IsAuthenticated
    ]
    def get(self, request):
        user = request.user
        data = {
            'user': UserSerializer(user).data,
            'profil': None
        }
        if user.type_compte == User.TypeCompte.INDIVIDU:
            try:
                data['profil'] = IndividuSerializer(
                    user.individu
                ).data
            except Individu.DoesNotExist:
                pass

        elif user.type_compte == User.TypeCompte.ORGANISATION:
            try:
                data['profil'] = OrganisationSerializer(
                    user.organisation
                ).data
            except Organisation.DoesNotExist:
                pass

        return Response(data)
    
class CreerIndividuView(generics.CreateAPIView):
    serializer_class = IndividuCreateSerializer
    permission_classes = [
        IsAuthenticated
    ]
    def perform_create(self, serializer):

        user = self.request.user

        if user.type_compte != User.TypeCompte.INDIVIDU:
            raise serializers.ValidationError(
                "Ce compte est une organisation."
            )

        if hasattr(user, 'individu'):
            raise serializers.ValidationError(
                "Le profil individu existe déjà."
            )

        serializer.save(user=user)  

class CreerOrganisationView(generics.CreateAPIView):
    serializer_class = OrganisationCreateSerializer
    permission_classes = [
        IsAuthenticated
    ]
    def perform_create(self, serializer):
        user = self.request.user
        if user.type_compte != User.TypeCompte.ORGANISATION:
            raise serializers.ValidationError(
                "Ce compte est un individu."
            )
        if hasattr(user, 'organisation'):
            raise serializers.ValidationError(
                "Le profil organisation existe déjà."
            )

        serializer.save(user=user)     
        
class MonIndividuView(generics.RetrieveUpdateAPIView):
    serializer_class = IndividuSerializer
    permission_classes = [
        IsAuthenticated
    ]
    def get_object(self):
        return self.request.user.individu             

class MonOrganisationView(generics.RetrieveUpdateAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [
        IsAuthenticated
    ]
    def get_object(self):
        return self.request.user.organisation    
    
class CategorieListCreateView(generics.ListCreateAPIView):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]

        return [IsAuthenticated()]  
    
class CategorieDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    
    def get_permissions(self):
        if self.request.method in [
            'PUT',
            'PATCH',
            'DELETE'
        ]:
            return [IsAdminUser()]

        return [IsAuthenticated()]      
    
class BadgeListCreateView(generics.ListCreateAPIView):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]

        return [IsAuthenticated()]    
    
class BadgeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer

    def get_permissions(self):
        if self.request.method in [
            'PUT',
            'PATCH',
            'DELETE'
        ]:
            return [IsAdminUser()]

        return [IsAuthenticated()]  
    
class RegisterUserView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]      