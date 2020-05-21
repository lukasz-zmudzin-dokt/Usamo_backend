from rest_framework import views, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from account.permissions import IsStaffMember
from job.views import ErrorResponse, MessageResponse
from steps.serializers import *


class CreateRoot(generics.CreateAPIView):
    # permission_classes = (IsAuthenticated, IsStaffMember)
    permission_classes = (AllowAny,)
    serializer_class = RootSerializer
    queryset = Root.objects.all()


class CreateStep(generics.CreateAPIView):
    # permission_classes = (IsAuthenticated, IsStaffMember)
    permission_classes = (AllowAny,)
    serializer_class = StepSerializer
    queryset = Step.objects.all()


class CreateSubStep(generics.CreateAPIView):
    # permission_classes = (IsAuthenticated, IsStaffMember)
    permission_classes = (AllowAny,)
    serializer_class = SubStepSerializer
    queryset = SubStep.objects.all()

    def get_serializer_context(self):
        result = super().get_serializer_context()
        try:
            parent = Step.objects.get(id=self.kwargs['pk'])
            result['request'].data['parent'] = self.kwargs['pk']
        except Step.DoesNotExist:
            return ErrorResponse('Podany krok usamodzielnienia nie istnieje!', status.HTTP_404_NOT_FOUND)
        return result


class GetRoot(views.APIView):
    # permission_classes = (IsAuthenticated, IsStaffMember)
    permission_classes = (AllowAny,)

    def get(self, request):
        return Response(RootSerializer(instance=Root.objects.first()).data, status=status.HTTP_200_OK)


class GetStep(generics.RetrieveAPIView):
    # permission_classes = (IsAuthenticated, IsStaffMember)
    permission_classes = (AllowAny,)
    serializer_class = StepSerializer
    queryset = Step.objects.all()


class DestroyStep(generics.DestroyAPIView):
    # permission_classes = (IsAuthenticated, IsStaffMember)
    permission_classes = (AllowAny,)
    serializer_class = StepSerializer
    queryset = Step.objects.all()


class DestroySubStep(generics.DestroyAPIView):
    # permission_classes = (IsAuthenticated, IsStaffMember)
    permission_classes = (AllowAny,)
    serializer_class = SubStepSerializer
    queryset = SubStep.objects.all()


class SwitchSubSteps(views.APIView):
    # permission_classes = (IsAuthenticated, IsStaffMember)
    permission_classes = (AllowAny,)

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
        sub1 = parent.substeps.get(order=sub1)
        sub2 = parent.substeps.get(order=sub2)
        sub1.switch_places(sub2)
        return Response(StepSerializer(instance=parent).data, status=status.HTTP_200_OK)