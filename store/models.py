from django.db import models
from django.contrib.auth.models import AbstractUser


class Role(models.Model):
    """Роль пользователя в системе"""
    role_name = models.CharField(max_length=100, unique=True, verbose_name="Название роли")

    class Meta:
        db_table = "role"
        verbose_name = "Роль"
        verbose_name_plural = "Роли"

    def __str__(self):
        return self.role_name


class User(AbstractUser):
    """Пользователь системы"""
    patronymic = models.CharField(max_length=150, blank=True, default='', verbose_name="Отчество")
    role = models.ForeignKey(Role, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Роль")

    class Meta:
        db_table = "user"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def get_full_name_display(self):
        """ФИО: Фамилия Имя Отчество"""
        parts = [self.last_name, self.first_name, self.patronymic]
        return ' '.join(p for p in parts if p)


class Category(models.Model):
    """Категория товара"""
    category_name = models.CharField(max_length=200, unique=True, verbose_name="Категория")

    class Meta:
        db_table = "category"
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.category_name


class Manufacturer(models.Model):
    """Производитель"""
    manufacturer_name = models.CharField(max_length=200, unique=True, verbose_name="Производитель")

    class Meta:
        db_table = "manufacturer"
        verbose_name = "Производитель"
        verbose_name_plural = "Производители"

    def __str__(self):
        return self.manufacturer_name


class Supplier(models.Model):
    """Поставщик"""
    supplier_name = models.CharField(max_length=200, unique=True, verbose_name="Поставщик")

    class Meta:
        db_table = "supplier"
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"

    def __str__(self):
        return self.supplier_name


class Unit(models.Model):
    """Единица измерения"""
    unit_name = models.CharField(max_length=50, unique=True, verbose_name="Единица измерения")

    class Meta:
        db_table = "unit"
        verbose_name = "Единица измерения"
        verbose_name_plural = "Единицы измерения"

    def __str__(self):
        return self.unit_name


class Product(models.Model):
    """Товар"""
    article = models.CharField(max_length=50, unique=True, verbose_name="Артикул")
    product_name = models.CharField(max_length=300, verbose_name="Наименование")
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, verbose_name="Единица измерения")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name="Поставщик")
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT, verbose_name="Производитель")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name="Категория")
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Скидка (%)")
    quantity_in_stock = models.IntegerField(default=0, verbose_name="Количество на складе")
    description = models.TextField(blank=True, default='', verbose_name="Описание")
    photo = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Фото")

    class Meta:
        db_table = "product"
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return f"{self.article} - {self.product_name}"

    @property
    def discounted_price(self):
        """Цена с учётом скидки"""
        if self.discount and self.discount > 0:
            return round(float(self.price) * (1 - float(self.discount) / 100), 2)
        return float(self.price)


class PickupPoint(models.Model):
    """Пункт выдачи"""
    address = models.CharField(max_length=500, verbose_name="Адрес")

    class Meta:
        db_table = "pickup_point"
        verbose_name = "Пункт выдачи"
        verbose_name_plural = "Пункты выдачи"

    def __str__(self):
        return self.address


class Order(models.Model):
    """Заказ"""
    STATUS_CHOICES = [
        ('Новый', 'Новый'),
        ('Завершен', 'Завершен'),
    ]
    order_date = models.DateField(verbose_name="Дата заказа")
    delivery_date = models.DateField(null=True, blank=True, verbose_name="Дата доставки")
    pickup_point = models.ForeignKey(PickupPoint, on_delete=models.PROTECT, verbose_name="Пункт выдачи")
    client = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Клиент")
    pickup_code = models.IntegerField(verbose_name="Код получения")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Новый', verbose_name="Статус")

    class Meta:
        db_table = "order"
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ №{self.pk}"


class OrderItem(models.Model):
    """Позиция заказа"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Товар")
    quantity = models.IntegerField(verbose_name="Количество")

    class Meta:
        db_table = "order_item"
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"
