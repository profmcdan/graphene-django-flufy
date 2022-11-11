import factory

from django.contrib.auth.models import User


class UserFactory(factory.django.DjangoModelFactory):
    # username = factory.Faker("user_name")
    username = "graphql"
    # first_name = factory.Faker("first_name")
    first_name = "Daniel"
    # last_name = factory.Faker("last_name")
    last_name = "Ale"
    # email = factory.Faker("email")
    email = "danielale9291@gmail.com"

    class Meta:
        model = User
        django_get_or_create = ("username",)
