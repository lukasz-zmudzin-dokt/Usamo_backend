from datetime import date, timedelta
from unittest.mock import MagicMock
from django.core.files import File
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase
from cv.models import *
from job.models import *
from job.enums import Voivodeships
from account.models import *
from account.account_type import StaffGroupType
from account.account_status import AccountStatus


def create_test_offer_data(name="OFERTA TESTOWA", voivodeship="mazowieckie", expiration_date=date.today() + timedelta(days=10),
                           description="TEST TEST", category='IT', offer_type='Praca'):
    category, _ = JobOfferCategory.objects.get_or_create(name=category)
    offer_type, _ = JobOfferType.objects.get_or_create(name=offer_type)
    return {
        "offer_name": name,
        "category": category.name,
        "type": offer_type.name,
        "company_name": "TESTOWA FIRMA",
        "company_address": {
            "city": "Warszawa",
            "street": "Testowa",
            "street_number": "420",
            "postal_code": "69-420"
        },
        "voivodeship": voivodeship,
        "expiration_date": str(expiration_date),
        "description": description
    }

def create_test_offer_instance(name="OFERTA TESTOWA", voivodeship="mazowieckie", expiration_date=date(2020, 5, 5),
                               description="TEST TEST", category='IT', offer_type='Praca', employer=None,
                               confirmed=True):
    category, _ = JobOfferCategory.objects.get_or_create(name=category)
    offer_type, _ = JobOfferType.objects.get_or_create(name=offer_type)
    address = Address.objects.create(
        city="Warszawa",
            street="Testowa",
            street_number="420",
            postal_code="69-420"
    )
    return JobOffer.objects.create(
        offer_name=name,
        category=category,
        offer_type=offer_type,
        company_name="TESTOWA FIRMA",
        company_address=address,
        voivodeship=voivodeship,
        expiration_date=expiration_date,
        description=description,
        employer=employer,
        confirmed=confirmed
    )

def create_offer_edit_data():
    return {
        "offer_name": "EDYTOWANA OFERTA",
        "voivodeship": "lubelskie",
        "expiration_date": str(date(2021, 6, 6)),
        "description": "EDIT EDIT"
    }

def create_cv(user):
    mock_file = MagicMock(spec=File)
    mock_file.name = 'TestFileName'
    mock_file.read.return_value = "fake file contents"
    return CV.objects.create(cv_user=user, document=mock_file)


def create_job_application(cv_user, offer):
    cv = create_cv(cv_user)
    return JobOfferApplication.objects.create(cv=cv, job_offer=offer)



def create_user(username='testuser', verified=True):
    email = '%s@test.com' % username
    user = Account.objects.create_user(username=username, password='testuser', first_name='test',
                                       last_name='test', email=email)
    if verified:
        user.status=AccountStatus.VERIFIED.value
    return user


def create_employer(user, verified=True):
    address = Address.objects.create(
        city="Warszawa",
        street="Testowa",
        street_number="420",
        postal_code="69-420"
    )
    return EmployerAccount.objects.create(user=user, phone_number='+48123456789', company_name='TESTOWA FIRMA',
                                          company_address=address, nip='1234567890')


def create_staff(user, for_jobs=True):
    if for_jobs:
        group, _ = Group.objects.get_or_create(name=StaffGroupType.STAFF_JOBS.value)
        user.groups.add(group)
    return StaffAccount.objects.create(user=user)


def create_staff(user, for_jobs=True):
    if for_jobs:
        group, _ = Group.objects.get_or_create(name=StaffGroupType.STAFF_JOBS.value)
        user.groups.add(group)
    return StaffAccount.objects.create(user=user)


def create_default(user):
    address = Address.objects.create(
        city="Warszawa",
        street="Testowa",
        street_number="420",
        postal_code="69-420"
    )
    return DefaultAccount.objects.create(user=user, phone_number='+48123456789', facility_name='test facility',
                                         facility_address=address)


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
        staff = create_staff(self.user)
        self.assertEquals(JobOffer.objects.count(), 1)
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        offer_edit_data = create_offer_edit_data()
        response = self.client.put(self.url(self.offer.id), data=offer_edit_data)
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
        staff = create_staff(self.user)
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
        staff = create_staff(self.user)
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
        staff = create_staff(self.user)
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response = self.client.delete(self.url(self.offer.id))
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(JobOffer.objects.filter(removed=True).count(), 1)

    def test_offer_delete_bad_offer_id(self):
        staff = create_staff(self.user)
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
        cls.offer1 = create_test_offer_instance(confirmed=True)
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
        cls.url = '/job/job-offers/application/'
        cls.user = create_user()
        cls.offer = create_test_offer_instance()

    def test_offer_insterested_users_add_success(self):
        default_user = create_default(self.user)
        cv = create_cv(default_user)
        application_data = {'cv': cv.cv_id, 'job_offer': self.offer.id}
        self.assertEquals(self.offer.jobofferapplication_set.count(), 0)
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response = self.client.post(self.url, application_data, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(JobOffer.objects.count(), 1)
        updated_offer = JobOffer.objects.get()
        self.assertEquals(updated_offer.jobofferapplication_set.count(), 1)

    def test_offer_insterested_users_add_again_error(self):
        default_user = create_default(self.user)
        cv = create_cv(default_user)
        application_data = {'cv': cv.cv_id, 'job_offer': self.offer.id}
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response1 = self.client.post(self.url, application_data, format='json')
        self.assertEquals(response1.status_code, status.HTTP_201_CREATED)
        response2 = self.client.post(self.url, application_data, format='json')
        self.assertEquals(response2.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEquals(JobOffer.objects.count(), 1)
        updated_offer = JobOffer.objects.get()
        self.assertEquals(updated_offer.jobofferapplication_set.count(), 1)


class EmployerJobOfferInterestedUsersListTestCase(APITestCase):

    @classmethod
    def setUp(cls):
        cls.url = lambda self, id: '/job/employer/application_list/%s/' % id
        cls.employer_user = create_user(username='testemployer')
        cls.employer = create_employer(cls.employer_user)
        cls.user = create_user()
        cls.default_user = create_default(cls.user)
        cls.offer = create_test_offer_instance(employer=cls.employer)
        cls.application = create_job_application(cls.default_user, cls.offer)

    def test_employer_offer_insterested_users_list_success(self):
        self.client.force_authenticate(user=self.employer_user, token=self.employer_user.auth_token)
        response = self.client.get(self.url(self.offer.id))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.data), 1)
        self.assertEquals(response.data[0]['user_id'], str(self.user.id))

    def test_employer_offer_insterested_users_bad_offer(self):
        self.client.force_authenticate(user=self.employer_user, token=self.employer_user.auth_token)
        response = self.client.get(self.url(0))
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)


class VoivodeshipEnumTestCase(APITestCase):

    @classmethod
    def setUp(cls):
        cls.url = '/job/enums/voivodeships/'
        cls.user = create_user()

    def test_offer_voivodeship_list_success(self):
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.data['voivodeships']), 16)
        self.assertEquals(sorted(response.data['voivodeships']), sorted(Voivodeships().getKeys()))

        
class OfferAdminConfirmTestCase(APITestCase):

    @classmethod
    def setUp(cls):
        cls.url = lambda self, id: '/job/admin/confirm/%s/' % id
        cls.user = create_user()
        cls.offer = create_test_offer_instance(confirmed=False)

    def test_offer_confirm_not_admin(self):
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response = self.client.post(self.url(self.offer.id), {'confirmed': True}, format='json')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_offer_confirm_success(self):
        staff = create_staff(self.user)
        self.assertEquals(JobOffer.objects.filter(removed=False, confirmed=False).count(), 1)
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response = self.client.post(self.url(self.offer.id), {'confirmed': True}, format='json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(JobOffer.objects.filter(removed=False, confirmed=False).count(), 0)


class OfferAdminUnconfirmedListTestCase(APITestCase):

    @classmethod
    def setUp(cls):
        cls.url = '/job/admin/job-offers/unconfirmed/'
        cls.user = create_user()
        cls.offer1 = create_test_offer_instance(name="TEST1", confirmed=False)
        cls.offer2 = create_test_offer_instance(name="TEST2", confirmed=False)

    def test_unconfirmed_offers_list_not_admin(self):
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_unconfirmed_offers_list_success(self):
        staff = create_staff(self.user)
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        self.assertEquals(JobOffer.objects.filter(removed=False).count(), 2)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results')
        self.assertNotEquals(results, None)
        self.assertEquals(len(results), 2)

        
class OfferTypesListTestCase(APITestCase):

    @classmethod
    def setUp(cls):
        cls.url = '/job/enums/types/'
        cls.user = create_user()

    def test_offer_type_list_success(self):
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(sorted(response.data['offer_types']), sorted(list(JobOfferType.objects.values_list('name', flat=True))))


class OfferTypeCreateTestCase(APITestCase):

    @classmethod
    def setUp(cls):
        cls.url = '/job/enums/type/'
        cls.user = create_user()
        cls.test_type_data = {'name': 'TESTTYPE'}

    def test_offer_type_add_not_admin(self):
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        count = JobOfferType.objects.count()
        response = self.client.post(self.url, self.test_type_data, format='json')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEquals(JobOfferType.objects.count(), count)


    def test_offer_type_add_success(self):
        staff = create_staff(self.user)
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        count = JobOfferType.objects.count()
        response = self.client.post(self.url, self.test_type_data, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(JobOfferType.objects.count(), count+1)
        self.assertTrue(JobOfferType.objects.filter(name='TESTTYPE').exists())


class OfferCategoriesListTestCase(APITestCase):

    @classmethod
    def setUp(cls):
        cls.url = '/job/enums/categories/'
        cls.user = create_user()

    def test_offer_category_list_success(self):
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(sorted(response.data['categories']), sorted(list(JobOfferCategory.objects.values_list('name', flat=True))))


class OfferCategoryCreateTestCase(APITestCase):

    @classmethod
    def setUp(cls):
        cls.url = '/job/enums/category/'
        cls.user = create_user()
        cls.test_category_data = {'name': 'TESTCATEGORY'}

    def test_offer_category_add_not_admin(self):
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        count = JobOfferCategory.objects.count()
        response = self.client.post(self.url, self.test_category_data, format='json')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEquals(JobOfferCategory.objects.count(), count)


    def test_offer_category_add_success(self):
        staff = create_staff(self.user)
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        count = JobOfferCategory.objects.count()
        response = self.client.post(self.url, self.test_category_data, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(JobOfferCategory.objects.count(), count+1)
        self.assertTrue(JobOfferCategory.objects.filter(name='TESTCATEGORY').exists())


