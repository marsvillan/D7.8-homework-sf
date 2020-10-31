from django.shortcuts import render, redirect
from django.template import loader
from django.http import HttpResponse
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.views.generic.base import TemplateView
from django.urls import reverse_lazy
from django.forms import formset_factory  
from django.http.response import HttpResponseRedirect
from p_library.models import Author, Book, Publisher, Friend, UserProfile
from p_library.forms import AuthorForm, BookForm
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.contrib.auth import logout

class LogoutIfNotStaffMixin(AccessMixin):
    """
    Миксин для проверки, входит ли пользователь в персонал
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            #logout(request)
            return self.handle_no_permission()
        return super(LogoutIfNotStaffMixin, self).dispatch(request, *args, **kwargs)

class ProfileView(TemplateView):
    template_name = 'userprofile.html'

class AuthorEdit(LoginRequiredMixin, CreateView):
    model = Author
    form_class = AuthorForm
    success_url = reverse_lazy('author_list')
    template_name = 'author_edit.html'


class AuthorList(ListView):
    model = Author
    template_name = 'authors_list.html'

class BookCreate(LoginRequiredMixin, CreateView):
    template_name = 'book_form.html'
    model = Book
    fields = ['ISBN', 'title', 'description', 'year_release',
            'author', 'publisher', 'friend', 'copy_count',
            'price', 'cover']

class BookUpdate(LoginRequiredMixin, LogoutIfNotStaffMixin, UpdateView):
    permission_required = 'is_staff'
    template_name = 'book_form.html'
    model = Book
    fields = ['ISBN', 'title', 'description', 'year_release',
            'author', 'publisher', 'friend', 'copy_count',
            'price', 'cover']

class BookDelete(LoginRequiredMixin, LogoutIfNotStaffMixin, DeleteView):
    permission_required = 'is_staff'
    template_name = 'book_confirm_delete.html'
    model = Book
    success_url = reverse_lazy('books')

class ProfileUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'profile_form.html'
    model = UserProfile
    fields = ['age', 'gender']

    success_url = reverse_lazy('userprofile')

    # этот метод нужен, что бы для UpdateView определить объект редактирования
    def get_object(self, queryset=None):
        return self.request.user.profile

    # когда данные проверены, то так же добавляем информацию по возрасту и полу в extra_data
    def form_valid(self, form):
        super(ProfileUpdate, self).form_valid(form)
        social = SocialAccount.objects.filter(provider='github', user=self.request.user).first()
        if social:
            social.extra_data['age'] = form.instance.age
            social.extra_data['gender'] = form.instance.gender
            social.save()
        return HttpResponseRedirect(self.get_success_url())


# Create your views here.
def books_list(request):
    books = Book.objects.all()
    return HttpResponse(books)

def index(request):
    template = loader.get_template('index.html')
    books = Book.objects.all()
    biblio_data = {
        "title": "мою библиотеку",
        "books": books,
        "range": [x for x in range(1, 100) if not x%3],
    }
    return HttpResponse(template.render(biblio_data, request))

@login_required
def book_increment(request):
    if request.method == 'POST':
        book_id = request.POST['id']
        if not book_id:
            return redirect('/')
        else:
            book = Book.objects.filter(id=book_id).first()
            if not book:
                return redirect('/')
            book.copy_count += 1
            book.save()
        return redirect('/')
    else:
        return redirect('/')

@login_required
def book_decrement(request):
    if request.method == 'POST':
        book_id = request.POST['id']
        if not book_id:
            return redirect('/')
        else:
            book = Book.objects.filter(id=book_id).first()
            if not book:
                return redirect('/')
            if book.copy_count < 1:
                book.copy_count = 0
            else:
                book.copy_count -= 1
            book.save()
        return redirect('/')
    else:
        return redirect('/')

def publisher(request):
    template = loader.get_template('publisher.html')
    publishers = Publisher.objects.all()
    for pub in publishers:
        pub.allbooks = ", ".join([x.title for x in Book.objects.filter(publisher=pub.id)])
    data = {
        "publishers": publishers,
    }
    return HttpResponse(template.render(data, request))

def friend(request):
    template = loader.get_template('friend.html')
    friends = Friend.objects.all()
    data = {
        "friends": friends,
    }
    return HttpResponse(template.render(data, request))

@login_required
def author_create_many(request):
    AuthorFormSet = formset_factory(AuthorForm, extra=2)  #  Первым делом, получим класс, который будет создавать наши формы. Обратите внимание на параметр `extra`, в данном случае он равен двум, это значит, что на странице с несколькими формами изначально будет появляться 2 формы создания авторов.
    if request.method == 'POST':  #  Наш обработчик будет обрабатывать и GET и POST запросы. POST запрос будет содержать в себе уже заполненные данные формы
        author_formset = AuthorFormSet(request.POST, request.FILES, prefix='authors')  #  Здесь мы заполняем формы формсета теми данными, которые пришли в запросе. Обратите внимание на параметр `prefix`. Мы можем иметь на странице не только несколько форм, но и разных формсетов, этот параметр позволяет их отличать в запросе.
        if author_formset.is_valid():  #  Проверяем, валидны ли данные формы
            for author_form in author_formset:
                author_form.save()  #  Сохраним каждую форму в формсете
            return HttpResponseRedirect(reverse_lazy('author_list'))  #  После чего, переадресуем браузер на список всех авторов.
    else:  #  Если обработчик получил GET запрос, значит в ответ нужно просто "нарисовать" формы.
        author_formset = AuthorFormSet(prefix='authors')  #  Инициализируем формсет и ниже передаём его в контекст шаблона.
    return render(request, 'manage_authors.html', {'author_formset': author_formset})

@login_required
def books_authors_create_many(request):
    AuthorFormSet = formset_factory(AuthorForm, extra=2)
    BookFormSet = formset_factory(BookForm, extra=2)
    if request.method == 'POST':
        author_formset = AuthorFormSet(request.POST, request.FILES, prefix='authors')
        book_formset = BookFormSet(request.POST, request.FILES, prefix='books')
        if author_formset.is_valid() and book_formset.is_valid():
            for author_form in author_formset:
                author_form.save()
            for book_form in book_formset:
                book_form.save()
            return HttpResponseRedirect(reverse_lazy('author_list'))
    else:
        author_formset = AuthorFormSet(prefix='authors')
        book_formset = BookFormSet(prefix='books')
    return render(
            request,
            'manage_books_authors.html',
            {
                'author_formset': author_formset,
                'book_formset': book_formset,
                }
            )
