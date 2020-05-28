import uuid
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase
from account.account_type import StaffGroupType
from account.models import StaffAccount, Account
from blog.models import *


def create_test_blogpost_instance(id, category, tags, content, title, author):
    reservation = BlogPostReservation.objects.get(id=id)
    instance = BlogPost.objects.create(
        id=reservation,
        category=BlogPostCategory.objects.get_or_create(name=category)[0],
        content=content,
        title=title,
        author=author
    )
    instance.tags.set([BlogPostTag.objects.get_or_create(name=tag)[0] for tag in tags])
    return instance


def create_test_blogpost(category='category', tags=None, content='BASE64CONTENT', title='title'):
    reservation = BlogPostReservation.objects.create()
    if tags is None:
        tags = ['tag1', 'tag2']
    return {
        "id": reservation.id,
        "category": category,
        "tags": tags,
        "content": content,
        "title": title
    }


def create_test_category_set(n):
    categories = []
    for i in range(n):
        categories.append({"name": f"category{i}"})
    return categories


def create_test_category_instances_set(n):
    instances = []
    for i in range(n):
        instances.append(BlogPostCategory.objects.get_or_create(name=f'category{i}'))
    return instances


def create_user(username='testuser'):
    email = '%s@test.com' % username
    return Account.objects.create_user(username=username, password='testuser', first_name='test',
                                       last_name='test', email=email)

def create_staff(user, group = None):
    if group is not None and isinstance(group, StaffGroupType):
        g, created = Group.objects.get_or_create(name=group.value)
        user.groups.add(g)
    staff_user = StaffAccount.objects.create(user=user)
    return staff_user


class BlogPostCreateTestCase(APITestCase):

    @classmethod
    def setUp(cls):
        cls.url = '/blog/blogpost/'
        cls.user = create_user()

    def test_blogpost_create_not_staff(self):
        self.assertEquals(StaffAccount.objects.count(), 0)
        self.assertEquals(BlogPost.objects.count(), 0)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, create_test_blogpost(), format='json')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN, msg=response.data)
        self.assertEquals(BlogPost.objects.count(), 0)

    def test_blogpost_create_success(self):
        staff = create_staff(self.user, group=StaffGroupType.STAFF_BLOG_CREATOR)
        self.assertEquals(StaffAccount.objects.count(), 1)
        self.assertEquals(BlogPost.objects.count(), 0)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, create_test_blogpost(), format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED, msg=response.data)
        self.assertEquals(BlogPost.objects.count(), 1)
        blogpost = BlogPost.objects.get()
        self.assertEquals(blogpost.author.id, staff.id)

    def test_blogpost_create_bad_request(self):
        staff = create_staff(self.user, group=StaffGroupType.STAFF_BLOG_CREATOR)
        self.assertEquals(StaffAccount.objects.count(), 1)
        self.assertEquals(BlogPost.objects.count(), 0)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, create_test_blogpost(category=""), format='json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST, msg=response.data)
        self.assertEquals(BlogPost.objects.count(), 0)


class BlogPostGetTestCase(APITestCase):

    @classmethod
    def setUp(cls):
        cls.url = lambda self, id: '/blog/blogpost/%s/' % id
        cls.user = create_user()
        cls.staff = create_staff(cls.user, StaffGroupType.STAFF_BLOG_CREATOR)
        cls.blogpost = create_test_blogpost_instance(**create_test_blogpost(), author=cls.staff)

    def test_blogpost_get_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url(self.blogpost.pk), create_test_blogpost(), format='json')
        self.assertEquals(response.status_code, status.HTTP_200_OK, msg=response.data)
        self.assertEquals(response.data['content'], self.blogpost.content)

    def test_blogpost_get_bad_blogpost_id(self):
        self.client.force_authenticate(user=self.user)
        bad_uuid = '00000000-0000-0000-0000-000000000000'
        response = self.client.get(self.url(bad_uuid))
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)


class BlogPostEditTestCase(APITestCase):

    @classmethod
    def setUp(cls):
        cls.url = lambda self, id: '/blog/blogpost/%s/' % id
        cls.user = create_user()
        cls.staff = create_staff(cls.user, StaffGroupType.STAFF_BLOG_CREATOR)
        cls.blogpost = create_test_blogpost_instance(**create_test_blogpost(), author=cls.staff)


    def test_blogpost_edit_not_staff(self):
        bad_user = create_user(username="baduser")
        self.client.force_authenticate(user=bad_user)
        response = self.client.put(self.url(self.blogpost.pk), create_test_blogpost(category='edited'), format='json')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN, msg=response.data)

    def test_blogpost_edit_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url(self.blogpost.pk), create_test_blogpost(category='edited'), format='json')
        self.assertEquals(response.status_code, status.HTTP_200_OK, msg=response.data)
        self.assertEquals(BlogPost.objects.count(), 1)
        blogpost = BlogPost.objects.get()
        self.assertEquals(blogpost.category.name, 'edited')


class BlogPostDeleteTestCase(APITestCase):

    @classmethod
    def setUp(cls):
        cls.url = lambda self, id: '/blog/blogpost/%s/' % id
        cls.user = create_user()
        cls.staff = create_staff(cls.user, StaffGroupType.STAFF_BLOG_CREATOR)
        cls.blogpost = create_test_blogpost_instance(**create_test_blogpost(), author=cls.staff)


    def test_blogpost_delete_not_staff(self):
        self.assertEquals(BlogPost.objects.count(), 1)
        bad_user = create_user(username="baduser")
        self.client.force_authenticate(user=bad_user)
        response = self.client.delete(self.url(self.blogpost.pk), create_test_blogpost(category='edited'), format='json')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN, msg=response.data)
        self.assertEquals(BlogPost.objects.count(), 1)

    def test_blogpost_delete_success(self):
        self.assertEquals(BlogPost.objects.count(), 1)
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url(self.blogpost.pk), create_test_blogpost(category='edited'), format='json')
        self.assertEquals(response.status_code, status.HTTP_200_OK, msg=response.data)
        self.assertEquals(BlogPost.objects.count(), 0)


class BlogPostCategoryGetTestCase(APITestCase):
    @classmethod
    def setUp(cls):
        cls.n = 10
        cls.url = '/blog/categories/'
        cls.categories = create_test_category_instances_set(cls.n)

    def test_blogpostcategory_get_success(self):
        self.assertEquals(BlogPostCategory.objects.count(), self.n)
        response = self.client.get(self.url, format='json')
        self.assertEquals(response.status_code, status.HTTP_200_OK, msg=response.data)
        self.assertEquals([c['name'] for c in response.data], [c['name'] for c in create_test_category_set(self.n)])


class BlogPostCategoryFilteringTestCase(APITestCase):
    @classmethod
    def setUp(cls):
        cls.url = '/blog/blogposts/'
        cls.user = create_user()
        cls.staff = create_staff(cls.user, StaffGroupType.STAFF_BLOG_CREATOR)
        cls.blogpost1 = create_test_blogpost_instance(**create_test_blogpost(category='category1'), author=cls.staff)
        cls.blogpost2 = create_test_blogpost_instance(**create_test_blogpost(category='category2'), author=cls.staff)

    def test_blogpost_filtering_success(self):
        self.assertTrue(BlogPostCategory.objects.filter(name='category1').exists())
        response = self.client.get(self.url, {'category': 'category1'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, status.HTTP_200_OK, msg=response.data)
        test_blogpost = create_test_blogpost(category='category1')
        self.assertTrue(all(blogpost['category'] for blogpost in response.data['results']), test_blogpost['category'])
        self.assertTrue(any(blogpost['tags'] for blogpost in response.data['results']), test_blogpost['tags'])

