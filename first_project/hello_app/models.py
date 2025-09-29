from django.db import models

# Create your models here.

class Users(models.Model):
    user_name = models.CharField(verbose_name='имя пользователя')
    email = models.CharField("почта")
    balance = models.IntegerField("баланс аккаунта")
    trade_link = models.TextField('ссылка для обмена')
    role = models.CharField("admin or user", default='user')
    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["user_name", "role"]
        indexes = [
            models.Index(fields=["user_name"])
        ]
    def str(self):
        return f"{self.user_name} {self.role}"
    
class Items(models.Model):
    name = models.CharField(verbose_name='название предмета')
    image_url = models.CharField("картинка предмета")
    rarity = models.TextField("редкость предмета")
    is_stattrack = models.TextField('stattrack or no', default= 'no')
    class Meta:
        verbose_name = "item"
        verbose_name_plural = "items"
        ordering = ["name", "image_url"]
        indexes = [
            models.Index(fields=["name"])
        ]
    def str(self):
        return f"{self.name} {self.image_url}"


class Cases(models.Model):
    name = models.CharField(verbose_name='название кейса')
    price = models.IntegerField("цена кейса")
    description = models.TextField("описание текста")
    class Meta:
        verbose_name = "case"
        verbose_name_plural = "cases"
        ordering = ["user_name", "role"]
        indexes = [
            models.Index(fields=["user_name"])
        ]
    def str(self):
        return f"{self.user_name} {self.role}"
