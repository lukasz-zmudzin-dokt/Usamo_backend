from datetime import date

from rest_framework import status
from rest_framework.test import APITestCase
from job.models import *
from job.enums import Voivodeships
from account.models import Account, DefaultAccount, EmployerAccount


# Create your tests here.
def create_test_offer_data(name="OFERTA TESTOWA", voivodeship="mazowieckie", expiration_date=date(2020, 5, 5),
                           description="TEST TEST", category='IT', offer_type='Praca'):
    category, _ = JobOfferCategory.objects.get_or_create(name=category)
    offer_type, _ = JobOfferType.objects.get_or_create(name=offer_type)
    return {
        "offer_name": name,
        "category": category.name,
        "type": offer_type.name,
        "company_name": "TESTOWA FIRMA",
        "company_address": "TESTOWY ADRES",
        "voivodeship": voivodeship,
        "expiration_date": str(expiration_date),
        "description": description
    }

def create_test_offer_instance(name="OFERTA TESTOWA", voivodeship="mazowieckie", expiration_date=date(2020, 5, 5),
                           description="TEST TEST", category='IT', offer_type='Praca', employer=None):
    category, _ = JobOfferCategory.objects.get_or_create(name=category)
    offer_type, _ = JobOfferType.objects.get_or_create(name=offer_type)
    return JobOffer.objects.create(
        offer_name=name,
        category=category,
        offer_type=offer_type,
        company_name="TESTOWA FIRMA",
        company_address="TESTOWY ADRES",
        voivodeship=voivodeship,
        expiration_date=expiration_date,
        description=description,
        employer=employer
    )

def create_offer_edit_data():
    return {
        "offer_name": "EDYTOWANA OFERTA",
        "voivodeship": "lubelskie",
        "expiration_date": str(date(2021, 6, 6)),
        "description": "EDIT EDIT"
    }


def create_user(username='testuser'):
    email = '%s@test.com' % username
    return Account.objects.create_user(username=username, password='testuser', first_name='test',
                                       last_name='test', email=email)


def create_employer(user):
    return EmployerAccount.objects.create(user=user, phone_number='+48123456789', company_name='TESTOWA FIRMA',
                                          company_address='TESTOWY ADRES', nip='1234567890')


def create_default(user):
    return DefaultAccount.objects.create(user=user, phone_number='+48123456789', facility_name='test facility',
                                         facility_address='TESTOWY ADRES')


class JobOfferCreateTestCase(APITestCase):

    @classmethod
    def setUp(cls):
        cls.url = '/job/job-offer/'
        cls.user = create_user()

    def test_offer_create_not_employer(self):
        self.assertEquals(EmployerAccount.objects.count(), 0)
        self.assertEquals(JobOffer.objects.count(), 0)
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response = self.client.post(self.url, create_test_offer_data(), format='json')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEquals(JobOffer.objects.count(), 0)

    def test_offer_create_success(self):
        employer = create_employer(self.user)
        self.assertEquals(EmployerAccount.objects.count(), 1)
        self.assertEquals(JobOffer.objects.count(), 0)
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response = self.client.post(self.url, create_test_offer_data(), format='json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(JobOffer.objects.count(), 1)
        offer = JobOffer.objects.get()
        self.assertEquals(offer.employer.id, employer.id)
        self.assertEquals(offer.interested_users.count(), 0)

    def test_offer_create_bad_request(self):
        employer = create_employer(self.user)
        self.assertEquals(EmployerAccount.objects.count(), 1)
        self.assertEquals(JobOffer.objects.count(), 0)
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response = self.client.post(self.url, create_test_offer_data(voivodeship='some_rubbish'), format='json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(JobOffer.objects.count(), 0)


class JobOfferGetTestCase(APITestCase):

    @classmethod
    def setUp(cls):
        cls.url = lambda self, id: '/job/job-offer/%s/' % id
        cls.user = create_user()
        cls.offer = create_test_offer_instance()

    def test_offer_get_success(self):
        self.assertEquals(JobOffer.objects.count(), 1)
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response = self.client.get(self.url(self.offer.id))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(JobOffer.objects.count(), 1)

    def test_offer_get_bad_offer_id(self):
        self.assertEquals(JobOffer.objects.count(), 1)
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response = self.client.get(self.url(0))
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)


class JobOfferEditTestCase(APITestCase):

    @classmethod
    def setUp(cls):
        cls.url = lambda self, id: '/job/job-offer/%s/' % id
        cls.user = create_user()
        cls.offer = create_test_offer_instance()

    def test_offer_edit_success(self):
        self.assertEquals(JobOffer.objects.count(), 1)
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        offer_edit_data = create_offer_edit_data()
        response = self.client.post(self.url(self.offer.id), data=offer_edit_data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(JobOffer.objects.count(), 1)
        edited_offer = JobOffer.objects.get()
        self.assertNotEquals(self.offer.offer_name, edited_offer.offer_name)
        self.assertEquals(edited_offer.offer_name, offer_edit_data['offer_name'])
        self.assertNotEquals(self.offer.voivodeship, edited_offer.voivodeship)
        self.assertEquals(edited_offer.voivodeship, offer_edit_data['voivodeship'])
        self.assertNotEquals(self.offer.expiration_date, edited_offer.expiration_date)
        self.assertEquals(str(edited_offer.expiration_date), offer_edit_data['expiration_date'])
        self.assertNotEquals(self.offer.description, edited_offer.description)
        self.assertEquals(edited_offer.description, offer_edit_data['description'])

    def test_offer_edit_bad_offer_id(self):
        self.assertEquals(JobOffer.objects.count(), 1)
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response = self.client.get(self.url(0))
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)


class JobOfferDeleteTestCase(APITestCase):

    @classmethod
    def setUp(cls):
        cls.url = lambda self, id: '/job/job-offer/%s/' % id
        cls.user = create_user()
        cls.offer = create_test_offer_instance()

    def test_offer_delete_success(self):
        self.assertEquals(JobOffer.objects.filter(removed=False).count(), 1)
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response = self.client.delete(self.url(self.offer.id))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(JobOffer.objects.filter(removed=False).count(), 0)
        self.assertEquals(JobOffer.objects.filter(removed=True).count(), 1)

    def test_offer_delete_already_removed(self):
        self.offer.removed = True
        self.offer.save()
        self.assertEquals(JobOffer.objects.filter(removed=True).count(), 1)
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response = self.client.delete(self.url(self.offer.id))
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(JobOffer.objects.filter(removed=True).count(), 1)

    def test_offer_delete_bad_offer_id(self):
        self.assertEquals(JobOffer.objects.filter(removed=False).count(), 1)
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response = self.client.delete(self.url(0))
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEquals(JobOffer.objects.filter(removed=False).count(), 1)


class JobOffersListTestCase(APITestCase):

    @classmethod
    def setUp(cls):
        cls.url = '/job/job-offers/'
        cls.user = create_user()
        cls.offer1 = create_test_offer_instance()
        cls.offer2 = create_test_offer_instance(name='Oferta 2', description='nowa oferta',
                                                                      voivodeship='lubelskie')

    def test_offer_list_success(self):
        self.assertEquals(JobOffer.objects.filter(removed=False).count(), 2)
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.data['results']), 2)

    def test_offer_list_without_removed(self):
        self.assertEquals(JobOffer.objects.count(), 2)
        self.offer1.removed = True
        self.offer1.save()
        self.assertEquals(JobOffer.objects.filter(removed=False).count(), 1)
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.data['results']), 1)
        self.assertEquals(response.data['results'][0]['id'], str(self.offer2.id))


class EmployerJobOffersListTestCase(APITestCase):

    @classmethod
    def setUp(cls):
        cls.url = '/job/employer/job-offers/'
        cls.user = create_user()
        cls.employer = create_employer(cls.user)
        cls.employer_offer1 = create_test_offer_instance(employer=cls.employer)
        cls.employer_offer2 = create_test_offer_instance(name='Oferta 2', description='nowa oferta - 2',
                                                         voivodeship='lubelskie', employer=cls.employer)
        cls.not_employer_offer = create_test_offer_instance(name='Oferta 3', description='nowa oferta - 3')

    def test_employer_offer_list_success(self):
        self.assertEquals(JobOffer.objects.filter(removed=False).count(), 3)
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.data['results']), 2)

    def test_employer_offer_list_without_removed(self):
        self.assertEquals(JobOffer.objects.count(), 3)
        self.employer_offer1.removed = True
        self.employer_offer1.save()
        self.assertEquals(JobOffer.objects.filter(removed=False).count(), 2)
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.data['results']), 1)
        self.assertEquals(response.data['results'][0]['id'], str(self.employer_offer2.id))

    def test_employer_offer_list_other_employer(self):
        self.assertEquals(JobOffer.objects.count(), 3)
        other_user = create_user("other_employer")
        other_employer = create_employer(other_user)
        self.client.force_authenticate(user=other_user, token=other_user.auth_token)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.data['results']), 0)


class JobOfferInterestedUsersAddTestCase(APITestCase):

    @classmethod
    def setUp(cls):
        cls.url = lambda self, id: '/job/offer-interested/%s/' % id
        cls.user = create_user()
        cls.offer = create_test_offer_instance()

    def test_offer_insterested_users_add_success(self):
        default_user = create_default(self.user)
        self.assertEquals(self.offer.interested_users.count(), 0)
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response = self.client.post(self.url(self.offer.id))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(JobOffer.objects.count(), 1)
        updated_offer = JobOffer.objects.get()
        self.assertEquals(updated_offer.interested_users.count(), 1)

    def test_offer_insterested_users_add_again_erorr(self):
        default_user = create_default(self.user)
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response1 = self.client.post(self.url(self.offer.id))
        self.assertEquals(response1.status_code, status.HTTP_200_OK)
        response2 = self.client.post(self.url(self.offer.id))
        self.assertEquals(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(JobOffer.objects.count(), 1)
        updated_offer = JobOffer.objects.get()
        self.assertEquals(updated_offer.interested_users.count(), 1)

    def test_offer_insterested_users_add_again_erorr(self):
        default_user = create_default(self.user)
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response1 = self.client.post(self.url(self.offer.id))
        self.assertEquals(response1.status_code, status.HTTP_200_OK)
        response2 = self.client.post(self.url(self.offer.id))
        self.assertEquals(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(JobOffer.objects.count(), 1)
        updated_offer = JobOffer.objects.get()
        self.assertEquals(updated_offer.interested_users.count(), 1)


    def test_offer_insterested_users_not_default_user(self):
        self.client.force_authenticate(
            user=self.user, token=self.user.auth_token)
        response1 = self.client.post(self.url(self.offer.id))
        self.assertEquals(response1.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEquals(JobOffer.objects.count(), 1)
        updated_offer = JobOffer.objects.get()
        self.assertEquals(updated_offer.interested_users.count(), 0)


class EmployerJobOfferInterestedUsersListTestCase(APITestCase):

    @classmethod
    def setUp(cls):
        cls.url = lambda self, id: '/job/employer/offer-interested/%s/' % id
        cls.employer_user = create_user(username='testemployer')
        cls.employer = create_employer(cls.employer_user)
        cls.user = create_user()
        cls.default_user = create_default(cls.user)
        cls.offer = create_test_offer_instance(employer=cls.employer)
        cls.offer.interested_users.add(cls.default_user)

    def test_employer_offer_insterested_users_list_success(self):
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response = self.client.get(self.url(self.offer.id))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.data), 1)
        self.assertEquals(response.data[0]['id'], str(self.user.id))

    def test_employer_offer_insterested_users_bad_offer(self):
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response = self.client.get(self.url(0))
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)


class VoivodeshipEnumTestCase(APITestCase):

    @classmethod
    def setUp(cls):
        cls.url = '/job/enums/voivodeships/'
        cls.user = create_user()

    def test_offer_insterested_users_add_success(self):
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.data['voivodeships']), 16)
        self.assertEquals(sorted(response.data['voivodeships']), sorted(Voivodeships().getKeys()))
