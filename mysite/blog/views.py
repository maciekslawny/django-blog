from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm
from django.core.mail import send_mail

def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        #formularz wysłany
        form = EmailPostForm(request.POST)
        if form.is_valid():
            #weryfikacja pól formularza jest ok
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = "{} ({}) zachęca do przeczytania '{}'".format(cd['name'],cd['email'], post.title)
            message = 'Przeczytaj post "{}" na stronie {}\n\n Komentarz dodany przez {}: {}'.format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent})




class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

def post_list(request):
    posts = Post.published.all()
    object_list = Post.published.all()
    paginator = Paginator(object_list, 3) # 3 posty na każdej stronie
    page = request.GET.get('page')  # wskazuje numer bieżącej strony

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        #jeśli page nie jest liczbą całkowitą to pobierana jest pierwsza strona
        posts = paginator.page(1) 
    except EmptyPage:
        #jeśli page jest większa niż numer ostatniej strony to pobierana jest ostatnia
        posts = paginator.page(paginator.num_pages) 

    return render(request,
                    'blog/post/list.html',
                    {'posts': posts,
                     'page': page})



def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                                   status='published',
                                   publish__year=year,
                                   publish__month=month,
                                   publish__day=day)
    return render(request,
                    'blog/post/detail.html',
                    {'post': post})