from django.urls import path
from users.views import (
    ProfilView,
    CreerIndividuView,
    CreerOrganisationView,
    MonIndividuView,
    MonOrganisationView,
    CategorieListCreateView,
    CategorieDetailView,
    BadgeListCreateView,
    BadgeDetailView,
    RegisterUserView
)

from events.views import (
    EvenementListCreateView,
    EvenementDetailView,
    ParticiperEvenementView,
    MesParticipationsView,
    ParticipantsEvenementView,
    AccepterParticipationView,
    RefuserParticipationView,
    AnnulerParticipationView,
    TerminerEvenementView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [

    path(
        'api/login/',
        TokenObtainPairView.as_view(),
        name='login'
    ),

    path(
        'api/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),
    # Profil
    path(
        'profil/',
        ProfilView.as_view()
    ),
    
    path(
        'users/register/',
        RegisterUserView.as_view(),
        name='register'
    ),

    path(
        'profil/individu/',
        CreerIndividuView.as_view()
    ),

    path(
        'profil/individu/moi/',
        MonIndividuView.as_view()
    ),

    path(
        'profil/organisation/',
        CreerOrganisationView.as_view()
    ),

    path(
        'profil/organisation/moi/',
        MonOrganisationView.as_view()
    ),

    # Catégories
    path(
        'categories/',
        CategorieListCreateView.as_view()
    ),

    path(
        'categories/<int:pk>/',
        CategorieDetailView.as_view()
    ),

    # Badges
    path(
        'badges/',
        BadgeListCreateView.as_view()
    ),

    path(
        'badges/<int:pk>/',
        BadgeDetailView.as_view()
    ),

    # Événements
    path(
        'evenements/',
        EvenementListCreateView.as_view()
    ),

    path(
        'evenements/<int:pk>/',
        EvenementDetailView.as_view()
    ),

    path(
        'evenements/<int:pk>/participer/',
        ParticiperEvenementView.as_view()
    ),

    path(
        'evenements/<int:pk>/participants/',
        ParticipantsEvenementView.as_view()
    ),

    path(
        'evenements/<int:pk>/terminer/',
        TerminerEvenementView.as_view()
    ),

    # Participations
    path(
        'participations/miennes/',
        MesParticipationsView.as_view()
    ),

    path(
        'participations/<int:pk>/accepter/',
        AccepterParticipationView.as_view()
    ),

    path(
        'participations/<int:pk>/refuser/',
        RefuserParticipationView.as_view()
    ),

    path(
        'participations/<int:pk>/annuler/',
        AnnulerParticipationView.as_view()
    ),
]
