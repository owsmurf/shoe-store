import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.conf import settings
from PIL import Image

from .models import Product, Supplier, Order, OrderItem
from .forms import ProductForm


def get_user_role(user):
    """Определяет роль: guest / client / manager / admin"""
    if not user.is_authenticated:
        return 'guest'
    if user.role:
        name = user.role.role_name.lower()
        if 'админ' in name:
            return 'admin'
        elif 'менеджер' in name:
            return 'manager'
        elif 'клиент' in name:
            return 'client'
    return 'client'


def login_view(request):
    """Страница авторизации"""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        if not username or not password:
            messages.error(request, 'Заполните логин и пароль.')
        else:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('product_list')
            else:
                messages.error(request, 'Неверный логин или пароль.')
    return render(request, 'store/login.html')


def logout_view(request):
    """Выход из системы"""
    logout(request)
    return redirect('login')


def product_list(request):
    """Список товаров с фильтрацией/сортировкой/поиском"""
    user_role = get_user_role(request.user)
    products = Product.objects.select_related(
        'category', 'manufacturer', 'supplier', 'unit'
    ).all()

    suppliers = Supplier.objects.all().order_by('supplier_name')
    search_query = ''
    supplier_filter = ''
    sort_order = ''

    # Фильтрация/сортировка/поиск только для менеджера и админа
    if user_role in ('manager', 'admin'):
        search_query = request.GET.get('search', '').strip()
        supplier_filter = request.GET.get('supplier', '')
        sort_order = request.GET.get('sort', '')

        if search_query:
            products = products.filter(
                Q(product_name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(article__icontains=search_query) |
                Q(category__category_name__icontains=search_query) |
                Q(manufacturer__manufacturer_name__icontains=search_query) |
                Q(supplier__supplier_name__icontains=search_query)
            )

        if supplier_filter:
            products = products.filter(supplier__id=supplier_filter)

        if sort_order == 'asc':
            products = products.order_by('quantity_in_stock')
        elif sort_order == 'desc':
            products = products.order_by('-quantity_in_stock')

    context = {
        'products': products,
        'user_role': user_role,
        'search_query': search_query,
        'supplier_filter': supplier_filter,
        'sort_order': sort_order,
        'suppliers': suppliers,
    }
    return render(request, 'store/product_list.html', context)


@login_required
def product_add_edit(request, pk=None):
    """Добавление / редактирование товара (только админ)"""
    if get_user_role(request.user) != 'admin':
        messages.error(request, 'Доступ запрещён. Только администратор может редактировать товары.')
        return redirect('product_list')

    product = get_object_or_404(Product, pk=pk) if pk else None
    old_photo = product.photo if product else None

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            new_product = form.save()

            # Обработка изображения: ресайз 300x200, удаление старого
            if 'photo' in request.FILES and new_product.photo:
                # Удалить старое фото, если заменяем
                if old_photo and old_photo != new_product.photo:
                    old_path = os.path.join(settings.MEDIA_ROOT, str(old_photo))
                    if os.path.exists(old_path):
                        os.remove(old_path)
                # Ресайз
                img_path = new_product.photo.path
                img = Image.open(img_path)
                img = img.resize((300, 200), Image.LANCZOS)
                img.save(img_path)

            messages.success(request, 'Товар сохранён успешно.')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)

    # При добавлении скрываем артикул (будет autogen) — нет, артикул ручной по данным
    context = {
        'form': form,
        'product': product,
        'editing': pk is not None,
    }
    return render(request, 'store/product_form.html', context)


@login_required
def product_delete(request, pk):
    """Удаление товара (только админ)"""
    if get_user_role(request.user) != 'admin':
        messages.error(request, 'Доступ запрещён.')
        return redirect('product_list')

    product = get_object_or_404(Product, pk=pk)

    # Товар в заказе — удалить нельзя
    if OrderItem.objects.filter(product=product).exists():
        messages.error(request, f'Невозможно удалить товар «{product.product_name}» — он присутствует в заказе.')
        return redirect('product_list')

    if request.method == 'POST':
        # Удалить фото
        if product.photo:
            photo_path = product.photo.path
            if os.path.exists(photo_path):
                os.remove(photo_path)
        product.delete()
        messages.success(request, 'Товар удалён.')

    return redirect('product_list')


@login_required
def order_list(request):
    """Список заказов (менеджер и админ)"""
    user_role = get_user_role(request.user)
    if user_role not in ('manager', 'admin'):
        messages.error(request, 'Доступ запрещён.')
        return redirect('product_list')

    orders = Order.objects.select_related('client', 'pickup_point').prefetch_related('items__product').all().order_by('-order_date')
    context = {
        'orders': orders,
        'user_role': user_role,
    }
    return render(request, 'store/order_list.html', context)
