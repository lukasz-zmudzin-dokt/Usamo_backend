from django.urls import path
from django.conf.urls import include, url
from .views import *


urlpatterns = [
    path('root/', CreateRoot.as_view()),
    path('root/update/', UpdateRoot.as_view()),
    path('step/', CreateStep.as_view()),
    path('substep/', CreateSubStep.as_view()),
    path('root', GetRoot.as_view()),
    path('step/<uuid:pk>', GetStep.as_view()),
    path('', GetStepList.as_view()),
    path('step/<uuid:pk>/update/', UpdateStep.as_view()),
    path('step/<uuid:pk>/delete/', DestroyStep.as_view()),
    path('substep/<uuid:pk>/delete/', DestroySubStep.as_view()),
    path('substep/<uuid:pk>/update/', UpdateSubStep.as_view()),
    path('step/<uuid:pk>/switch/', SwitchSubSteps.as_view()),
    path('step/<uuid:pk>/move/', MoveSubStep.as_view()),
    path('user-perspective', GetUserPerspective.as_view()),
    path('user-perspective/increment/', IncrementUserPerspectiveSubStep.as_view())
]
