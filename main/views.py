from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetView, \
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.core.signing import BadSignature
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, CreateView, TemplateView, DeleteView
from rest_framework import status, mixins
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import RetrieveAPIView, CreateAPIView, GenericAPIView, ListAPIView, ListCreateAPIView
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import BbSerializer, BbDetailSerializer, CommentSerializer
from main.forms import ProfileEditForm, RegisterForm, SearchForm, BbForm, AIFormSet, UserCommentForm, \
    GuestCommentForm
from main.models import AdvUser, SubRubric, Bb, AdditionalImage, Comment
from main.utilities import signer


def index(request):
    bbs = Bb.objects.filter(is_active=True).select_related('rubric')[:10]
    context = {'bbs': bbs}
    return render(request, 'main/index.html', context)


def other_page(request, page):
    try:
        template = get_template(template_name='main/' + page + '.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))


class BbLoginView(LoginView):
    template_name = 'main/login.html'
    # альтернатива:
    # path('accounts/login', LoginView.as_view(template_name='main/login.html'), name='login')


class BbLogoutView(LogoutView):
    pass  # т.к. в settings.py LOGOUT_REDIRECT_URL = 'main:index'
    # альтернатива:
    # template_name = 'main/index.html'


@login_required
def profile(request):
    bbs = Bb.objects.filter(author=request.user.pk)
    context = {'bbs': bbs}
    return render(request, 'main/profile.html', context)


class ProfileEditView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = AdvUser
    template_name = 'main/profile_edit.html'
    form_class = ProfileEditForm
    success_url = reverse_lazy('main:profile')
    success_message = 'Данные пользователя изменены'

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class PasswordEditView(PasswordChangeView):
    template_name = 'main/password_edit.html'
    success_url = reverse_lazy('main:profile')
    success_message = 'Пароль пользователя изменён'


class RegisterView(CreateView):
    model = AdvUser
    template_name = 'main/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('main:register_done')


class RegisterDoneView(TemplateView):
    template_name = 'main/register_done.html'


def user_activate(request, sign):
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'main/activation_failed.html')
    user = get_object_or_404(AdvUser, username=username)
    if user.is_activated:
        template = 'main/activation_done_earlier.html'
    else:
        template = 'main/activation_done.html'
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template)


class ProfileDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = AdvUser
    template_name = 'main/profile_delete.html'
    success_url = reverse_lazy('main:index')
    success_message = 'Пользователь удалён'

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class ProfilePasswordResetView(PasswordResetView):
    template_name = 'main/password_reset.html'
    subject_template_name = 'email/reset_letter_subject.txt'
    email_template_name = 'email/reset_letter_body.txt'
    success_url = reverse_lazy('main:password_reset_done')


class ProfilePasswordResetDoneView(PasswordResetDoneView):
    template_name = 'main/password_reset_done.html'


class ProfilePasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'main/password_reset_confirm.html'
    post_reset_login = True
    success_url = reverse_lazy('main:password_reset_complete')


class ProfilePasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'main/password_reset_complete.html'


def rubric_bbs(request, pk):
    rubric = get_object_or_404(SubRubric, pk=pk)
    bbs = Bb.objects.filter(is_active=True, rubric=pk)

    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        bbs = bbs.filter(Q(title__icontains=keyword) | Q(content__icontains=keyword))  # ИЛИ
    else:
        keyword = ''
    form = SearchForm(initial={'keyword': keyword})

    paginator = Paginator(bbs, 2)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)

    context = {'bbs': page.object_list, 'rubric': rubric, 'page': page, 'form': form}
    return render(request, 'main/rubric_bbs.html', context)


def bb_detail(request, rubric_pk, pk):
    bb = get_object_or_404(Bb, pk=pk)
    initial = {'bb': bb.pk}
    if request.user.is_authenticated:
        initial['author'] = request.user
        form_class = UserCommentForm
    else:
        form_class = GuestCommentForm
    form = form_class(initial=initial)

    if request.method == 'POST':
        # print('requestPOST!!!!!!!!!!!1')
        # print(request.POST)
        # print('requestPOST!!!!!!!!!!!')
        c_form = form_class(request.POST)
        if c_form.is_valid():
            c_form.save()
            messages.add_message(request, messages.SUCCESS, 'Отзыв оставлен')
            return redirect(request.get_full_path_info())
        else:
            form = c_form
            messages.add_message(request, messages.WARNING, 'Отзыв не оставлен')

    try:
        next = bb.get_previous_by_created_at()
    except ObjectDoesNotExist:
        next = bb
    try:
        prev = bb.get_next_by_created_at()
    except ObjectDoesNotExist:
        prev = bb

    ais = AdditionalImage.objects.filter(bb=pk)
    comments = Comment.objects.filter(bb=pk, is_active=True)
    context = {'bb': bb, 'ais': ais, 'next': next, 'prev': prev, 'comments': comments, 'form': form,
               'user': request.user}
    return render(request, 'main/bb_detail.html', context)


@login_required
def profile_bb_detail(request, pk):
    bb = get_object_or_404(Bb, pk=pk)
    try:
        next = bb.get_previous_by_created_at()
    except ObjectDoesNotExist:
        next = bb
    try:
        prev = bb.get_next_by_created_at()
    except ObjectDoesNotExist:
        prev = bb

    comments = Comment.objects.filter(is_active=True, bb=pk)
    context = {'bb': bb, 'ais': AdditionalImage.objects.filter(bb=bb.pk), 'next': next, 'prev': prev,
               'comments': comments}
    return render(request, 'main/profile_bb_detail.html', context)


@login_required
def profile_bb_add(request):
    if request.method == 'POST':
        form = BbForm(request.POST, request.FILES)
        if form.is_valid():
            bb = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=bb)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Объявление добавлено')
                return HttpResponseRedirect(reverse('main:profile_bb_detail', kwargs={'pk': bb.pk}))
                # return redirect('main:profile')
        else:
            context = {'form': form}
            return render(request, 'main/profile_bb_add.html', context)
    else:
        form = BbForm(initial={'author': request.user.pk})
        formset = AIFormSet()
    context = {'form': form, 'formset': formset}
    return render(request, 'main/profile_bb_add.html', context)


@login_required
def profile_bb_edit(request, pk):
    bb = get_object_or_404(klass=Bb, pk=pk)
    if request.method == 'POST':
        form = BbForm(request.POST, request.FILES, instance=bb)
        if form.is_valid():
            bb = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=bb)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Объявление изменено')
                return HttpResponseRedirect(reverse('main:profile_bb_detail', kwargs={'pk': bb.pk}))

    else:
        form = BbForm(instance=bb)
        formset = AIFormSet(instance=bb)
    context = {'form': form, 'formset': formset}
    return render(request, 'main/profile_bb_edit.html', context)


@login_required
def profile_bb_delete(request, pk):
    bb = get_object_or_404(klass=Bb, pk=pk)
    if request.method == 'POST':
        bb.delete()
        messages.add_message(request, messages.SUCCESS, 'Объявление удалено')
        return HttpResponseRedirect(reverse('main:profile'))
    else:
        context = {'bb': bb}
    return render(request, 'main/profile_bb_delete.html', context)


@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    bb_pk = comment.bb.pk
    rubric_pk = comment.bb.rubric.pk
    if request.user.username == comment.author:
        comment.delete()
        messages.add_message(request, messages.SUCCESS, 'Комментарий удалён')
        return HttpResponseRedirect(reverse('main:bb_detail', kwargs={'pk': bb_pk, 'rubric_pk': rubric_pk}))


@login_required
@api_view(['GET'])
def bbs(request):
    if request.method == 'GET':
        bbs = Bb.objects.filter(is_active=True)[:10]
        serializer = BbSerializer(bbs, many=True)
        return Response(serializer.data)


class BbDetailView(RetrieveAPIView):
    queryset = Bb.objects.filter(is_active=True)
    serializer_class = BbDetailSerializer


# @permission_classes((IsAuthenticatedOrReadOnly,))
@api_view(['GET', 'POST'])
def comments(request, pk):
    if request.method == 'POST':
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        comments = Comment.objects.filter(is_active=True, bb=pk)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class CommentListCreate(ListCreateAPIView):
    serializer_class = CommentSerializer
    # permission_classes = (IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer, **kwargs):
        serializer.save(bb=Bb.objects.get(pk=self.kwargs['pk']))

    def get_queryset(self):
        bb_pk = Bb.objects.get(pk=self.kwargs['pk'])
        return Comment.objects.filter(bb=bb_pk)
