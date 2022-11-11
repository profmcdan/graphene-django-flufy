
---

# Graphene-Django-Flufy
![Travis (.org) branch](https://img.shields.io/travis/eamigo86/graphene-django-extras/master)
![Codecov](https://img.shields.io/codecov/c/github/eamigo86/graphene-django-extras)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/graphene-django-extras)
![PyPI](https://img.shields.io/pypi/v/graphene-django-extras?color=blue)
![PyPI - License](https://img.shields.io/pypi/l/graphene-django-extras)
![PyPI - Downloads](https://img.shields.io/pypi/dm/graphene-django-extras?style=flat)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)

This package builds on top of `Graphene-Django-Extra`  and it adds some extra functionalities to graphene-django to facilitate the graphql use without Relay:
  1. Allow pagination and filtering on Queries.
  2. Allow defining DjangoRestFramework serializers based on Mutations.
  3. Allow using Directives on Queries and Fragments.

**NOTE:** Subscription support still sits in moved to [graphene-django-subscriptions](https://github.com/eamigo86/graphene-django-subscriptions). It may be moved later

## Installation

For installing graphene-django-flufy, just run this command in your shell:

```
pip install graphene-django-flufy
```

## Documentation:

### Extra functionalities:
 **Fields:**
  1.  DjangoObjectField
  2.  DjangoFilterListField
  3.  DjangoFilterPaginateListField
  4.  DjangoListObjectField (*Recommended for Queries definition*)

 **Mutations:**
  1.  DjangoSerializerMutation (*Recommended for Mutations definition*)

 **Types:**
  1.  DjangoListObjectType  (*Recommended for Types definition*)
  2.  DjangoInputObjectType
  3.  DjangoSerializerType  (*Recommended for quick queries and mutations definitions*)

 **Paginations:**
  1.  LimitOffsetGraphqlPagination
  2.  PageGraphqlPagination


### Queries and Mutations examples:

This is a basic example of graphene-django-extras package use. You can configure global params
for DjangoListObjectType classes pagination definitions on settings.py like this:

```python
    GRAPHENE_DJANGO_FLUFY = {
        'DEFAULT_PAGINATION_CLASS': 'graphene_django_flufy.paginations.LimitOffsetGraphqlPagination',
        'DEFAULT_PAGE_SIZE': 20,
        'MAX_PAGE_SIZE': 50,
        'CACHE_ACTIVE': True,
        'CACHE_TIMEOUT': 300    # seconds
    }
```

#### 1- Types Definition:

```python
from django.contrib.auth.models import User
from graphene_django_flufy import DjangoListObjectType, DjangoSerializerType, DjangoObjectType
from graphene_django_flufy.paginations import LimitOffsetGraphqlPagination

from .serializers import UserSerializer


class UserType(DjangoObjectType):
    class Meta:
        model = User
        description = " Type definition for a single user "
        filter_fields = {
            "id": ("exact", ),
            "first_name": ("icontains", "iexact"),
            "last_name": ("icontains", "iexact"),
            "username": ("icontains", "iexact"),
            "email": ("icontains", "iexact"),
            "is_staff": ("exact", ),
        }


class UserListType(DjangoListObjectType):
    class Meta:
        description = " Type definition for user list "
        model = User
        pagination = LimitOffsetGraphqlPagination(default_limit=25, ordering="-username") # ordering can be: string, tuple or list


class UserModelType(DjangoSerializerType):
    """ With this type definition it't necessary a mutation definition for user's model """

    class Meta:
        description = " User model type definition "
        serializer_class = UserSerializer
        pagination = LimitOffsetGraphqlPagination(default_limit=25, ordering="-username") # ordering can be: string, tuple or list
        filter_fields = {
            "id": ("exact", ),
            "first_name": ("icontains", "iexact"),
            "last_name": ("icontains", "iexact"),
            "username": ("icontains", "iexact"),
            "email": ("icontains", "iexact"),
            "is_staff": ("exact", ),
        }
```

#### 2- You can to define InputTypes for use on mutations:

```python
from graphene_django_flufy import DjangoInputObjectType


class UserInput(DjangoInputObjectType):
    class Meta:
        description = " User InputType definition to use as input on an Arguments class on traditional Mutations "
        model = User
```

#### 3- You can define traditional mutations that use InputTypes or Mutations based on DRF serializers:

```python
import graphene
from graphene_django_flufy import DjangoSerializerMutation

from .serializers import UserSerializer
from .types import UserType
from .input_types import UserInputType


class UserSerializerMutation(DjangoSerializerMutation):
    """
        DjangoSerializerMutation auto implement Create, Delete and Update functions
    """
    class Meta:
        description = " DRF serializer based Mutation for Users "
        serializer_class = UserSerializer


class UserMutation(graphene.Mutation):
    """
         On traditional mutation classes definition you must implement the mutate function

    """

    user = graphene.Field(UserType, required=False)

    class Arguments:
        new_user = graphene.Argument(UserInput)

    class Meta:
        description = " Graphene traditional mutation for Users "

    @classmethod
    def mutate(cls, root, info, *args, **kwargs):
        ...
```

#### 4- Defining the Schema file:

```python
import graphene
from graphene_django_flufy import DjangoObjectField, DjangoListObjectField, DjangoFilterPaginateListField,
DjangoFilterListField, LimitOffsetGraphqlPagination
from .types import UserType, UserListType, UserModelType
from .mutations import UserMutation, UserSerializerMutation


class Queries(graphene.ObjectType):
    # Possible User list queries definitions
    users = DjangoListObjectField(UserListType, description='All Users query')
    users1 = DjangoFilterPaginateListField(UserType, pagination=LimitOffsetGraphqlPagination())
    users2 = DjangoFilterListField(UserType)
    users3 = DjangoListObjectField(UserListType, filterset_class=UserFilter, description='All Users query')

    # Defining a query for a single user
    # The DjangoObjectField have a ID type input field, that allow filter by id and is't necessary to define resolve function
    user = DjangoObjectField(UserType, description='Single User query')

    # Another way to define a query to single user
    user1 = UserListType.RetrieveField(description='User List with pagination and filtering')

    # Exist two ways to define single or list user queries with DjangoSerializerType
    user_retrieve1, user_list1 = UserModelType.QueryFields(
        description='Some description message for both queries',
        deprecation_reason='Some deprecation message for both queries'
    )
    user_retrieve2 = UserModelType.RetrieveField(
        description='Some description message for retrieve query',
        deprecation_reason='Some deprecation message for retrieve query'
    )
    user_list2 = UserModelType.ListField(
        description='Some description message for list query',
        deprecation_reason='Some deprecation message for list query'
    )

class Mutations(graphene.ObjectType):
    user_create = UserSerializerMutation.CreateField(deprecation_reason='Some one deprecation message')
    user_delete = UserSerializerMutation.DeleteField()
    user_update = UserSerializerMutation.UpdateField()

    # Exist two ways to define mutations with DjangoSerializerType
    user_create1, user_delete1, user_update1 = UserModelType.MutationFields(
        description='Some description message for create, delete and update mutations',
        deprecation_reason='Some deprecation message for create, delete and update mutations'
    )

    user_create2 = UserModelType.CreateField(description='Description message for create')
    user_delete2 = UserModelType.DeleteField(description='Description message for delete')
    user_update2 = UserModelType.UpdateField(description='Description message for update')

    traditional_user_mutation = UserMutation.Field()
```

#### 5- Directives settings:
For use Directives you must follow two simple steps:
1. You must add **'graphene_django_flufy.ExtraGraphQLDirectiveMiddleware'** to your GRAPHENE dict
config on your settings.py:

```python
# settings.py

GRAPHENE = {
    'SCHEMA_INDENT': 4,
    'MIDDLEWARE': [
        'graphene_django_flufy.ExtraGraphQLDirectiveMiddleware'
    ]
}
```

2. You must add the *directives* param with your custom directives to your schema definition. This module comes with
some common directives for you, these directives allow to you format strings, numbers, lists, and dates (optional), and
you can load like this:

```python
# schema.py
from graphene_django_flufy import all_directives

schema = graphene.Schema(
    query=RootQuery,
    mutation=RootMutation,
    directives=all_directives
)
```
**NOTE**: Date directive depends on *dateutil* module, so if you do not have installed it, this directive will not be
available. You can install *dateutil* module manually:
```
pip install python-dateutil
```
or like this:
```
pip install graphene_django_flufy[date]
```
That's all !!!


#### 6- Complete Directive list:

##### FOR NUMBERS:
1. **FloorGraphQLDirective**: Floors value. Supports both String and Float fields.
2. **CeilGraphQLDirective**: Ceils value. Supports both String and Float fields.

##### FOR LIST:
1. **ShuffleGraphQLDirective**: Shuffle the list in place.
2. **SampleGraphQLDirective**: Take a 'k' int argument and return a k length list of unique elements chosen from the
taken list

##### FOR DATE:
1. **DateGraphQLDirective**: Take a optional 'format' string argument and format the date from resolving the field by
dateutil module with the 'format' format. Default format is: 'DD MMM YYYY HH:mm:SS' equivalent to
'%d %b %Y %H:%M:%S' python format.

##### FOR STRING:
1. **DefaultGraphQLDirective**: Take a 'to' string argument. Default to given value if None or ""
2. **Base64GraphQLDirective**: Take a optional ("encode" or "decode") 'op' string argument(default='encode').
Encode or decode the string taken.
3. **NumberGraphQLDirective**: Take a 'as' string argument. String formatting like a specify Python number formatting.
4. **CurrencyGraphQLDirective**: Take a optional 'symbol' string argument(default="$").
Prepend the *symbol* argument to taken string and format it like a currency.
5. **LowercaseGraphQLDirective**: Lowercase the taken string.
6. **UppercaseGraphQLDirective**: Uppercase the taken string.
7. **CapitalizeGraphQLDirective**: Return the taken string with its first character capitalized and the rest lowered.
8. **CamelCaseGraphQLDirective**: CamelCase the taken string.
9. **SnakeCaseGraphQLDirective**: SnakeCase the taken string.
10. **KebabCaseGraphQLDirective**: SnakeCase the taken string.
11. **SwapCaseGraphQLDirective**: Return the taken string with uppercase characters converted to lowercase and vice
versa.
12. **StripGraphQLDirective**: Take a optional 'chars' string argument(default=" ").
Return the taken string with the leading and trailing characters removed. The 'chars' argument is not a prefix or
suffix; rather, all combinations of its values are stripped.
13. **TitleCaseGraphQLDirective**: Return the taken string title-cased, where words start with an uppercase character
and the remaining characters are lowercase.
14. **CenterGraphQLDirective**: Take a 'width' string argument and a optional 'fillchar' string argument(default=" ").
Return the taken string centered with the 'width' argument as new length. Padding is done using the specified
'fillchar' argument. The original string is returned if 'width' argument is less than or equal to taken string
length.
15. **ReplaceGraphQLDirective**: Take two strings arguments 'old' and 'new', and a optional integer argument
'count'.
Return the taken string with all occurrences of substring 'old' argument replaced by 'new' argument value.
If the optional argument 'count' is given, only the first 'count' occurrences are replaced.


#### 7- Queries's examples:
```js
{
  allUsers(username_Icontains:"john"){
    results(limit:5, offset:5){
      id
      username
      firstName
      lastName
    }
    totalCount
  }

  allUsers1(lastName_Iexact:"Doe", limit:5, offset:0){
    id
    username
    firstName
    lastName
  }

  allUsers2(firstName_Icontains: "J"){
    id
    username
    firstName
    lastName
  }

  user(id:2){
    id
    username
    firstName
  }

  user1(id:2){
    id
    username
    firstName
  }
}
```

#### 8- Mutations's examples:

```js
mutation{
  userCreate(newUser:{username:"test", password:"test*123"}){
    user{
      id
      username
      firstName
      lastName
    }
    ok
    errors{
      field
      messages
    }
  }

  userDelete(id:1){
    ok
    errors{
      field
      messages
    }
  }

  userUpdate(newUser:{id:1, username:"John"}){
    user{
      id
      username
    }
    ok
    errors{
      field
      messages
    }
  }
}
```

#### 9- Directives's examples:
Let's suppose that we have this query:
```js
query{
    allUsers{
        result{
            id
            firstName
            lastName
            dateJoined
            lastLogin
        }
    }
}
```
And return this data:
```js
{
  "data": {
    "allUsers": {
      "results": [
        {
            "id": "1",
            "firstName": "JOHN",
            "lastName": "",
            "dateJoined": "2017-06-20 09:40:30",
            "lastLogin": "2017-08-05 21:05:02"
        },
        {
            "id": "2",
            "firstName": "Golden",
            "lastName": "GATE",
            "dateJoined": "2017-01-02 20:36:45",
            "lastLogin": "2017-06-20 10:15:31"
        },
        {
            "id": "3",
            "firstName": "Nike",
            "lastName": "just do it!",
            "dateJoined": "2017-08-30 16:05:20",
            "lastLogin": "2017-12-05 09:23:09"
        }
      ]
    }
  }
}
```
As we see, some data it's missing or just not have the format that we like it, so let's go to format the output data
that we desired:
```js
query{
    allUsers{
        result{
            id
            firstName @capitalize
            lastName @default(to: "Doe") @title_case
            dateJoined @date(format: "DD MMM YYYY HH:mm:SS")
            lastLogin @date(format: "time ago")
        }
    }
}
```
And we get this output data:
```js
{
  "data": {
    "allUsers": {
      "results": [
        {
            "id": "1",
            "firstName": "John",
            "lastName": "Doe",
            "dateJoined": "20 Jun 2017 09:40:30",
            "lastLogin": "4 months, 12 days, 15 hours, 27 minutes and 58 seconds ago"
        },
        {
            "id": "2",
            "firstName": "Golden",
            "lastName": "Gate",
            "dateJoined": "02 Jan 2017 20:36:45",
            "lastLogin": "5 months, 28 days, 2 hours, 17 minutes and 53 seconds ago"
        },
        {
            "id": "3",
            "firstName": "Nike",
            "lastName": "Just Do It!",
            "dateJoined": "30 Aug 2017 16:05:20",
            "lastLogin": "13 days, 3 hours, 10 minutes and 31 seconds ago"
        }
      ]
    }
  }
}
```
As we see, the directives are an easy way to format output data on queries, and it's can be put together like a chain.

**List of possible date's tokens**:
"YYYY", "YY", "WW", "W", "DD", "DDDD", "d", "ddd", "dddd", "MM", "MMM", "MMMM", "HH", "hh", "mm", "ss", "A", "ZZ", "z".

You can use this shortcuts too:

1. "time ago"
2. "iso": "YYYY-MMM-DDTHH:mm:ss"
3. "js" or "javascript": "ddd MMM DD YYYY HH:mm:ss"


## Change Log:

#### v0.1.0:
    1. Update dependencies
    2. Upgrade graphene-django dependency to version > 3.
