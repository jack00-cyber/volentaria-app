from rest_framework.permissions import BasePermission


class IsOwnerProfile(BasePermission):

    def has_object_permission(
        self,
        request,
        view,
        obj
    ):
        return obj.user == request.user
    
class IsOrganisateurEvenement(BasePermission):

    def has_object_permission(
        self,
        request,
        view,
        obj
    ):
        user = request.user

        if user.type_compte == user.TypeCompte.INDIVIDU:
            try:
                return obj.organisateur == user.individu
            except user.individu.RelatedObjectDoesNotExist:
                return False

        if user.type_compte == user.TypeCompte.ORGANISATION:
            try:
                return obj.organisateur == user.organisation
            except user.organisation.RelatedObjectDoesNotExist:
                return False

        return False    