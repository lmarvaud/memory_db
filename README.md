# memory_db

[![Build Status](https://img.shields.io/travis/lmarvaud/memory_db)](https://travis-ci.org/lmarvaud/memory_db)
[![Coverage Status](https://img.shields.io/codecov/c/gh/lmarvaud/memory_db)](https://codecov.io/gh/lmarvaud/memory_db)
[![License](https://img.shields.io/github/license/lmarvaud/memory_db)](https://github.com/lmarvaud/memory_db/blob/master/LICENSE)
[![Repository](https://img.shields.io/badge/github-lmarvaud/memory_db-yellow?logo=github&logoColor=white)](https://github.com/lmarvaud/memory_db)

![Python versions](https://img.shields.io/badge/python_versions-3.6%20|%203.7%20|%203.8%20|%203.9-blue?logo=python)
![Django versions](https://img.shields.io/badge/django_versions-2.0%20|%202.1%20|%203.0%20|%203.1%20|%203.1-blue?logo=django)

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

## description

Memory DB is a Django like database manager using in-memory objects.

## disclamer

Unlike Django QuerySet, current version don't return new QuerySets when filtering on them.

```py
initial = Model.objects.all()
filtered_1 = initial.filter(...)
filtered_2 = initial.filter(...)  # don't do that
```

Otherwise `filtered_1` will also be filtered.

# Models

## Quick example

```py
from memory_db import MemoryManager, MemoryMeta, MemoryModel


class PersonManager(MemoryManager):
    def get_all(self):
        with open('persons.yml', mode='r', encoding='utf8') as stream:
            content = yaml.safe_load(stream)
            return [
                self.model.from_db(row)
                for row in content:
            ]


class Person(MemoryModel):
    objects = PersonManager()

    class Meta(MemoryMeta):
        fields = [
            models.CharField(name='first_name', max_length=30),
            models.CharField(name='last_name', max_length=30),
        ]
```

## Fields

The list of data fields is define in the field list of the Meta.

## Differences with django

Almoste all django differences could be considered as new features.

### Models fields

As you could see in above example, contrary to Django, the fields are directly populated in the fields of the Meta class of the model.

This might be an evolution to the future

### Manager database

In _memory_db_ project the manager take the role of the database, by returning the data in the `get_all` method.

### Model Relations

[ForeignKey], [ManyToManyField] and [OneToOneField] fields management is not implemented (yet).

[foreignkey]: https://docs.djangoproject.com/en/3.0/ref/models/fields/#django.db.models.ForeignKey
[manytomanyfield]: https://docs.djangoproject.com/en/3.0/ref/models/fields/#django.db.models.ManyToManyField
[onetoonefield]: https://docs.djangoproject.com/en/3.0/ref/models/fields/#django.db.models.OneToOneField

You may use `MemoryRelatedManager`:

```py
class Topping(MemoryModel):
    # ...
    pass


class PizzaManager(MemoryManager):
    def get_all(self) -> Iterable['Pizza']:
        """Create test models with relation."""
        margarita = Pizza()
        margarita.toppings.add(Topping(), Topping())
        return [margarita]


class Pizza(MemoryModel):
    objects = PizzaManager()

    toppings: 'MemoryRelatedManager[Topping]'

    def __init__(self):
        """Init the MemoryRelatedManager."""
        super().__init__()
        self.toppings = MemoryRelatedManager(Topping)
```

Note: all related elements are not store in the related `MemoryModel` manager.

### Model / data checks

You may want to check your data integrity according to you model. However data checks are not automatically added for each model managers.

You can create a check by calling the `check_data` of the `MemoryModel`.

**Example:**

```py
from django.core.checks.messages import CheckMessage
from django.core import checks


from memory_db import MemoryManager, MemoryModel


class PersonManager(MemoryManager):
    def get_all(self):
        pass

    def check_data(self):
        errors: List[CheckMessage]
        with open('persons.yml', mode='r', encoding='utf8') as stream:
            content = yaml.safe_load(stream)
            for row in content:
                errors += self.model.check_data(row)
        return error


class Person(MemoryModel):
    objects = PersonManager()


@checks.register
def check_persons()
    return Person.objects.check_data()
```

# QuerySet

## methods

[filter()]: #filter

### filter()

`filter(**kwargs)`

Filter the current queryset by only keeping the objects that match the given lookup parameters.

The lookup parameters (\*\*kwargs) should be in the format described in [Field lookups] below.

[exclude()]: #exclude

### exclude()

`exclude(**kwargs)`

Filter the current queryset by removing the objects that match the given lookup parameters.

The lookup parameters (\*\*kwargs) should be in the format described in [Field lookups] below.

This example excludes all entries whose pub_date is later than 2005-1-3 AND whose headline is “Hello”:

```py
Entry.objects.exclude(pub_date__gt=datetime.date(2005, 1, 3), headline='Hello')
```

This example excludes all entries whose pub_date is later than 2005-1-3 OR whose headline is “Hello”:

```py
Entry.objects.exclude(pub_date__gt=datetime.date(2005, 1, 3)).exclude(headline='Hello')
```

[annotate()]: #annotate

### annotate()

Not implemented yet

[order_by()]: #order_by

### order_by()

`order_by(*fields)`

By default, results returned by a _QuerySet_ depends on the `get_all` result of your `MemoryManager`. You can override this by using the order_by method.

[reverse()]: #reverse

### reverse()

`reverse()`

Work as [Django QuerySet reverse](https://docs.djangoproject.com/en/3.1/ref/models/querysets/#reverse)

[distinct()]: #distinct

### distinct()

Not implemented yet

[values()]: #values

### values()

`values(*fields)`

Work as [Django QuerySet values](https://docs.djangoproject.com/en/3.1/ref/models/querysets/#values)

```py
>>> Blog.objects.values('id', 'name')
<QuerySet [{'id': 1, 'name': 'Beatles Blog'}]>
```

Keyword arguments and non-positional arguments aren't implemented yet.

[values_list()]: #values_list

### values_list()

`values_list(*fields, flat=False)`

Work as [Django QuerySet values_list](https://docs.djangoproject.com/en/3.1/ref/models/querysets/#values-list)

```py
>>> Entry.objects.values_list('id', 'headline')
<QuerySet [(1, 'First entry'), ...]>

>>> Entry.objects.values_list('id').order_by('id')
<QuerySet[(1,), (2,), (3,), ...]>

>>> Entry.objects.values_list('id', flat=True).order_by('id')
<QuerySet [1, 2, 3, ...]>
```

Keyword argument `named: bool` is not implemented yet

[dates() / datetimes() / none()]: #dates

### dates() / datetimes() / none()

Not implemented yet

[all()]: #all

### all()

`all()`

Reset the iterator to the initial state

> **Disclamer**: this method different from the [Django all method](https://docs.djangoproject.com/en/3.1/ref/models/querysets/#all)

[union()]: #union

### union()

Not implemented yet

[get()]: #get

### get()

`get(**kwargs)`

Returns the object matching the given lookup parameters, which should be in the format described in [Field lookups]. You should use lookups that are guaranteed unique, such as the primary key or fields in a unique constraint. For example:

```py
Entry.objects.get(id=1)
Entry.objects.get(blog=blog, entry_number=1)
```

Work as [Django QuerySet get](https://docs.djangoproject.com/en/3.1/ref/models/querysets/#django.db.models.query.QuerySet.get)

[count()]: #count

### count()

`count()`

Work as [Django QuerySet count](https://docs.djangoproject.com/en/3.1/ref/models/querysets/#count)

```py
# Returns the total number of entries in the database.
Entry.objects.count()

# Returns the number of entries whose headline contains 'Lennon'
Entry.objects.filter(headline__contains='Lennon').count()
```

[iterator()]: #iterator

### iterator()

`iterator()`

Evaluates the QuerySet (by performing the query) and returns an iterator, as [Django QuerySet iterator()](https://docs.djangoproject.com/en/3.1/ref/models/querysets/#iterator) does.

[latest() / earliest()]: #latest

### latest() / earliest()

Not implemented yet

[first()]: #first

### first()

`first()`

Work as [Django QuerySet first()](https://docs.djangoproject.com/en/3.1/ref/models/querysets/#first)

```py
Article.objects.order_by('title', 'pub_date').first()
```

[last()]: #last

### last()

`last()`

Works like [first()](#first), but returns the last object in the queryset.

[exists()]: #exists

### exists()

`exists()`

Works as [Django QuerySet exists()](https://docs.djangoproject.com/en/3.1/ref/models/querysets/#exists)

[field lookups]: #field-lookups

## Field lookups

Field lookups are how you specify the meat of an SQL WHERE clause. They’re specified as keyword arguments to the QuerySet methods [filter()], [exclude()] and [get()].

For an introduction, see [models and database queries documentation](https://docs.djangoproject.com/en/3.1/topics/db/queries/#field-lookups-intro).

Built-in lookups are listed below :

### exact

Exact match. Use : `operator.eq`

Examples:

```py
Entry.objects.get(id__exact=14)
Entry.objects.get(id__exact=None)
```

### iexact

Case-insensitive exact match. Use : `icast_op(operator.eq)`

Example:

```py
Blog.objects.get(name__iexact='beatles blog')
Blog.objects.get(name__iexact=None)
```

### contains

Case-sensitive containment test. Use : `operator.contains`

Example:

```py
Entry.objects.get(headline__contains='Lennon')
```

### icontains

Case-insensitive containment test. Use : `icast_op(operator.contains)`

Example:

```py
Entry.objects.get(headline__icontains='Lennon')
```

### in

In a given iterable; often a list, tuple, or queryset. It’s not a common use case, but strings (being iterables) are accepted.

Use : `operator.contains`

Examples:

```py
Entry.objects.filter(id__in=[1, 3, 4])
Entry.objects.filter(headline__in='abc')
```

### gt

Greater than. Use : `operator.gt`

Example:

```py
Entry.objects.filter(id__gt=4)
```

### lte

Less than or equal to. Use : `operator.le`

### lt

Less than. Use : `operator.lt`

### gte

Greater than or equal to. Use : `operator.ge`

### startswith

Case-sensitive starts-with. Use : `str.startswith`

Example:

```py
Entry.objects.filter(headline__startswith='Lennon')
```

### istartswith

Use : `icast_op(str.startswith)`

Example:

```py
Entry.objects.filter(headline__istartswith='Lennon')
```

### endswith

Use : `str.endswith`

Example:

```py
Entry.objects.filter(headline__endswith='Lennon')
```

### iendswith

Use : `icast_op(str.endswith)`

Example:

```py
Entry.objects.filter(headline__iendswith='Lennon')
```

### isnull

Takes either True or False, which check if the value `is None` or `is not None`, respectively.

Example:

```py
Entry.objects.filter(pub_date__isnull=True)
```

## Aggregation

Not implemented yet
