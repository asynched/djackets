from io import BytesIO
from PIL import Image
from uuid import uuid4
from django.contrib.auth.models import AbstractUser
from django.core.files import File
from django.contrib.admin import decorators
from django.db import models


def product_image_upload(instance, filename):
    id = uuid4()
    image_filename = f"{id}-{filename}"

    return image_filename


class CustomUser(AbstractUser):
    email = models.EmailField(max_length=255, unique=True)

    REQUIRED_FIELDS = ['username']

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/{self.slug}/'


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        related_name='products',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(
        upload_to=product_image_upload, blank=True, null=True)
    thumbnail = models.ImageField(
        upload_to=product_image_upload, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def absolute_url(self):
        return f'/{self.category.slug}/{self.slug}'

    @property
    def image_url(self):
        if self.image:
            return 'http://127.0.0.1:8000' + self.image.url

        return ''

    @property
    def thumbnail_url(self):
        if self.thumbnail:
            return 'http://127.0.0.1:8000' + self.image.url

        if self.image:
            self.thumbnail = self.make_thumbnail(self.image)
            self.save()

            return 'http://127.0.0.1:8000' + self.thumbnail.url

        return ''

    def make_thumbnail(self, image, size=(300, 200)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()

        img.save(thumb_io, 'JPEG', quality=85)

        thumbnail = File(thumb_io, name=image.name)

        return thumbnail
