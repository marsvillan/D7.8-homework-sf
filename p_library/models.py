from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.
class Author(models.Model):
    full_name = models.TextField()
    birth_year = models.SmallIntegerField()
    country = models.CharField(max_length=2)
    def __str__(self):
        return self.full_name

class Publisher(models.Model):
    name = models.TextField()
    def __str__(self):
        return self.name

class Friend(models.Model):
    name = models.CharField(max_length=32)
    def __str__(self):
        return self.name

class Book(models.Model):
    ISBN = models.CharField(max_length=13)
    title = models.TextField()
    description = models.TextField()
    year_release = models.SmallIntegerField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name='books')
    friend = models.ForeignKey(Friend, on_delete=models.CASCADE, null=True, related_name='books', blank=True)
    copy_count = models.SmallIntegerField(default=1)
    price = models.DecimalField(max_digits=6,decimal_places=2)
    cover = models.ImageField(upload_to='covers/%Y/%m/%d', blank=True)
    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('books')    

class UserProfile(models.Model):
    GENDER = [
            (0, 'Неопределен'),
            (1, 'Мужской'),
            (2, 'Женский'),
    ]

    age = models.IntegerField(verbose_name="Возраст", default=0,
            validators = [MinValueValidator(0), MaxValueValidator(120)])
    gender = models.IntegerField(choices=GENDER, verbose_name="Пол", default=0)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    def __str__(self):
        return str(self.user)

# определяем функцию, которая будет вызываться при создании нового пользователя
# в этой функции мы создаем профиль пользователя с дефолтными значениями
def create_profile(sender, **kwargs):
    user = kwargs["instance"]
    if kwargs["created"]:
        user_profile = UserProfile(user=user)
        user_profile.save()

# тригер, который срабатывает, когда создается новый пользователь
post_save.connect(create_profile, sender=User)

