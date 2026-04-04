from rest_framework.permissions import BasePermission




class IsAdmin(BasePermission):

    message = "Only admin can perform this action."


    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'ADMIN'
        )
    


class IsAnalystOrAbove(BasePermission):

    message = "Analysts and Admins only."

    def has_permission(self, request, view):
        return(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['ANALYST', 'ADMIN']
        )
    

class IsViewer(BasePermission):

    message = "Authentication required."


    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated 