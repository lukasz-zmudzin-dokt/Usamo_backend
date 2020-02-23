from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

from rest_framework import views
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response

from .models import JobOffer
from .serializers import JobOfferSerializer, JobOfferEditSerializer, JobOfferFiltersSerializer


# Create your views here.

class JobOfferGetView(generics.RetrieveAPIView):
    serializer_class = JobOfferSerializer
    queryset = JobOffer.objects.all()
    lookup_field = 'pk'


class JobOfferListView(generics.ListAPIView):
    serializer_class = JobOfferSerializer

    def get_queryset(self):
        serializer = JobOfferFiltersSerializer(data=self.request.data)
        if serializer.is_valid():
            job_offer_filters = serializer.create(serializer.validated_data)
            valid_filters = job_offer_filters.get_filters()

            out = JobOffer.objects.filter(removed=False, **valid_filters)
            return out
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class JobOfferCreateView(generics.CreateAPIView):
    serializer_class = JobOfferSerializer
    queryset = JobOffer.objects.all()


class JobOfferEditView(views.APIView):

    @permission_classes([IsAuthenticated])
    def post(self, request):
        serializer = JobOfferEditSerializer(data=request.data)
        if serializer.is_valid():
            job_offer_edit = serializer.create(serializer.validated_data)
            try:
                instance = JobOffer.objects.get(pk=job_offer_edit.offer_id)
                fields_to_update = job_offer_edit.update_dict()
                for field, value in fields_to_update.items():
                    setattr(instance, field, value)
                instance.save()
                return Response(status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response("Offer not found", status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @permission_classes([IsAuthenticated])
    def delete(self, request):
        offer_id = request.data.get('offer_id', None)
        if offer_id is not None:
            try:
                instance = JobOffer.objects.get(pk=offer_id)
                instance.removed = True
                instance.save()
                return Response(status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response("Offer not found", status.HTTP_404_NOT_FOUND)
        else:
            return Response("No offer_id in request", status.HTTP_400_BAD_REQUEST)


class JobOfferInterestedUsersView(views.APIView):

    @permission_classes([IsAuthenticated])
    def post(self, request, offer_id):
        try:
            instance = JobOffer.objects.get(pk=offer_id)
            instance.interested_users.add(request.user)
            instance.save()
            return Response(status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response("Offer not found", status.HTTP_404_NOT_FOUND)

    @permission_classes([IsAuthenticated])
    def get(self, request, offer_id):
        try:
            offer = JobOffer.objects.get(pk=offer_id)
            interested_users_count = offer.interested_users.count()
            return Response("Ofertą %s zainteresowane jest %d osób" % (offer_id, interested_users_count), status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response("Offer not found", status.HTTP_404_NOT_FOUND)



