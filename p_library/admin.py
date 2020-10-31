from django.contrib import admin
from p_library.models import Book, Author, Publisher, Friend, UserProfile


# Register your models here.
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author',)
    fields = ('ISBN', 'title', 'description', 'year_release', 'author', 'publisher', 'price', 'friend', 'cover')

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    pass

@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    pass

@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    pass

@admin.register(UserProfile)
class FriendAdmin(admin.ModelAdmin):
    pass
