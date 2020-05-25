from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from drf_yasg.openapi import Schema
from drf_yasg.utils import swagger_auto_schema
from rest_framework import views, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from account.permissions import IsStaffMember
from steps.permissions import IsStaffStepsModerator
from job.views import ErrorResponse, MessageResponse
from steps.serializers import *


def sample_switch_substeps_body():
    return Schema(
        type='object',
        properties={
            "sub1": Schema(type='integer'),
            "sub2": Schema(type='integer')
        }
    )


def sample_move_substep_body():
    return Schema(
        type='object',
        properties={
            "sub": Schema(type='integer'),
            "new_position": Schema(type='integer')
        }
    )


class CreateRoot(generics.CreateAPIView):
    permission_classes = (IsStaffStepsModerator,)
    serializer_class = RootSerializer
    queryset = Root.objects.all()

    def post(self, request, *args, **kwargs):
        if Root.objects.count() > 0:
            return ErrorResponse('Może istnieć tylko jeden początek kroków usamodzielnienia', status.HTTP_400_BAD_REQUEST)
        else:
            return super().post(request=request, args=args, kwargs=kwargs)


class UpdateRoot(generics.UpdateAPIView):
    permission_classes = (IsStaffStepsModerator,)
    serializer_class = RootSerializer

    def get_object(self):
        return Root.objects.first()


class CreateStep(generics.CreateAPIView):
    permission_classes = (IsStaffStepsModerator,)
    serializer_class = StepSerializer
    queryset = Step.objects.all()


class CreateSubStep(generics.CreateAPIView):
    permission_classes = (IsStaffStepsModerator,)
    serializer_class = SubStepSerializer
    queryset = SubStep.objects.all()


class GetRoot(views.APIView):
    permission_classes = (AllowAny,)
    

    @swagger_auto_schema(
        responses={
            '200': RootSerializer,
            '404': '"error": Nie znaleziono początku kroków usamodzielnienia',
    },
        operation_description="Zwraca korzeń drzewa",
    )
    def get(self, request):
        user = request.user
        if isinstance(user, DefaultAccount):
            try:
                perspective = UserPerspective.objects.get(id=user.id)
                perspective.step = Root.objects.first()
                perspective.substep_order = 0
            except DefaultAccount.DoesNotExist:
                perspective = UserPerspective(user=user, step=Root.objects.first(), substep_order=0)
            perspective.save()
        if Root.objects.count() > 0:
            return Response(RootSerializer(instance=Root.objects.first()).data, status=status.HTTP_200_OK)
        else:
            return ErrorResponse('Nie znaleziono początku kroków usamodzielnienia', status.HTTP_404_NOT_FOUND)


class GetStep(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = StepSerializer
    queryset = Step.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            user = DefaultAccount.objects.get(user=request.user)
            step = Step.objects.get(id=self.kwargs['pk'])
            try:
                perspective = UserPerspective.objects.get(user=user)
                if perspective.step != step:
                    perspective.step = step
                    perspective.substep_order = 0
            except UserPerspective.DoesNotExist:
                perspective = UserPerspective(user=user, step=step, substep_order=0)
            perspective.save()
        except (DefaultAccount.DoesNotExist, ValidationError):
            pass
        return super().get(request, *args, **kwargs)


class GetStepList(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = StepSerializer
    queryset = Step.objects.all()


class UpdateStep(generics.UpdateAPIView):
    permission_classes = (IsStaffStepsModerator,)
    serializer_class = StepSerializer
    queryset = Step.objects.all()

    def put(self, request, *args, **kwargs):
        if str(request.data['parent']) == str(kwargs['pk']):
            return ErrorResponse('Krok nie może następować po sobie', status.HTTP_400_BAD_REQUEST)
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        if str(request.data['parent']) == str(kwargs['pk']):
            return ErrorResponse('Krok nie może następować po sobie', status.HTTP_400_BAD_REQUEST)
        return super().patch(request, *args, **kwargs)


class UpdateSubStep(generics.UpdateAPIView):
    permission_classes = (IsStaffStepsModerator,)
    serializer_class = SubStepSerializer
    queryset = SubStep.objects.all()


class DestroyStep(generics.DestroyAPIView):
    permission_classes = (IsStaffStepsModerator,)
    serializer_class = StepSerializer
    queryset = Step.objects.all()


class DestroySubStep(generics.DestroyAPIView):
    permission_classes = (IsStaffStepsModerator,)
    serializer_class = SubStepSerializer
    queryset = SubStep.objects.all()


class SwitchSubSteps(views.APIView):
    permission_classes = (IsStaffStepsModerator,)

    @swagger_auto_schema(
        request_body=sample_switch_substeps_body(),
        responses={
            '200': StepSerializer,
            '404': '"error": Nie znaleziono podanego kroku usamodzielnienia',
            '400': '"error": Nie podano, które podkroki mają być zamienione miejscami'
        },
        operation_description="Zamienia dwa podkroki miejscami na podstawie ich obecnych miejsc w kolejności."
                              " Id w url-u to id kroku",
    )
    def post(self, request, pk):
        try:
            parent = Step.objects.get(id=pk)
        except Step.DoesNotExist:
            return ErrorResponse('Nie znaleziono podanego kroku usamodzielnienia', status.HTTP_404_NOT_FOUND)
        try:
            sub1 = request.data['sub1']
            sub2 = request.data['sub2']
        except KeyError:
            return ErrorResponse('Nie podano, które podkroki mają być zamienione miejscami', status.HTTP_400_BAD_REQUEST)
        n_substeps = parent.substeps.count() - 1
        try:
            sub1 = parent.substeps.get(order=sub1)
        except SubStep.DoesNotExist:
            return ErrorResponse(f'Numer pierwszego podanego podkroku nie mieści się w zakresie 0-{n_substeps}',
                                 status.HTTP_400_BAD_REQUEST)
        try:
            sub2 = parent.substeps.get(order=sub2)
        except SubStep.DoesNotExist:
            return ErrorResponse(f'Numer drugiego podanego podkroku nie mieści się w zakresie 0-{n_substeps}',
                                 status.HTTP_400_BAD_REQUEST)
        sub1.switch_places(sub2)
        return Response(StepSerializer(instance=parent).data, status=status.HTTP_200_OK)


class MoveSubStep(views.APIView):
    permission_classes = (IsStaffStepsModerator,)

    @swagger_auto_schema(
        request_body=sample_move_substep_body(),
        responses={
            '200': StepSerializer,
            '404': '"error": Nie znaleziono podanego kroku usamodzielnienia',
            '400': '"error": Nie podano, jaki krok ma przejść na które miejsce'
        },
        operation_description="Przenosi podkrok (podany wg jego miesjca na liście) na inne miejsce na liście,"
                              " przesuwając wszystkie kroki będące na dalszych miejscach."
                              " Id w url-u to id kroku",
    )
    def post(self, request, pk):
        try:
            parent = Step.objects.get(id=pk)
        except Step.DoesNotExist:
            return ErrorResponse('Nie znaleziono podanego kroku usamodzielnienia', status.HTTP_404_NOT_FOUND)
        try:
            sub = request.data['sub']
            new_position = request.data['new_position']
        except KeyError:
            return ErrorResponse('Nie podano, jaki krok ma przejść na które miejsce', status.HTTP_400_BAD_REQUEST)
        sub = parent.substeps.get(order=sub)
        sub.move_to_spot(new_position)
        return Response(StepSerializer(instance=parent).data, status=status.HTTP_200_OK)


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_description="Zwraca ostatni krok, który oglądał użytkownik, wraz z numerem podkroku"
))
class GetUserPerspective(generics.RetrieveAPIView):
    serializer_class = UserPerspectiveSerializer

    def get_object(self):
        user = DefaultAccount.objects.get(user=self.request.user)
        try:
            perspective = UserPerspective.objects.get(user=user)
        except UserPerspective.DoesNotExist:
            perspective = UserPerspective.objects.create(user=user, step=Root.objects.first(), substep_order=0)
        return perspective


class IncrementUserPerspectiveSubStep(views.APIView):
    @swagger_auto_schema(
        responses={
            '200': '"message": Gratulacje, przechodzisz dalej!',
            '400': '"error": Nie zacząłeś_aś oglądać kroków usamodzielnienia / '
                   'Przekroczono liczbę podkroków'
        },
        operation_description="Zwiększa o jeden numer podkroku, który ostatnio oglądał użytkownik."
    )
    def post(self, request):
        user = DefaultAccount.objects.get(user=request.user)
        try:
            perspective = UserPerspective.objects.get(user=user)
        except UserPerspective.DoesNotExist:
            return ErrorResponse('Nie zacząłeś_aś oglądać kroków usamodzielnienia', status.HTTP_400_BAD_REQUEST)
        if perspective.step.substeps.count() <= perspective.substep_order + 1:
            return ErrorResponse('Przekroczono liczbę podkroków', status.HTTP_400_BAD_REQUEST)
        else:
            perspective.substep_order += 1
            perspective.save()
            return MessageResponse('Gratulacje, przechodzisz dalej!')
