from django.urls import path
from django.conf.urls import include, url
from .views import *


urlpatterns = [
    path('root/', CreateRoot.as_view()),
    path('step/', CreateStep.as_view()),
    path('step/<uuid:pk>/substeps/', CreateSubStep.as_view()),
    path('root', GetRoot.as_view()),
    path('step/<uuid:pk>', GetStep.as_view()),
    path('step/<uuid:pk>/', DestroyStep.as_view()),
    path('substep/<uuid:pk>', DestroySubStep.as_view()),
    path('step/<uuid:pk>/switch/', SwitchSubSteps.as_view())
]
