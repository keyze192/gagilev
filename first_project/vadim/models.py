from django.db import models

class Users(models.Model):
    user_name = models.CharField(verbose_name='имя пользователя', max_length=50, blank=True, null=True)
    email = models.EmailField("почта", max_length=255, blank=True, null=True)
    balance = models.IntegerField("баланс аккаунта", default=0)
    trade_link = models.TextField('ссылка для обмена', blank=True)
    is_admin = models.BooleanField("admin", default=False)
    steam_id = models.CharField("Steam ID", max_length=100, unique=True, blank=True, null=True)
    steam_avatar = models.URLField("аватар Steam", blank=True, null=True)
    steam_profile_url = models.URLField("профиль Steam", blank=True, null=True)
    
    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["user_name", "balance"]
        indexes = [
            models.Index(fields=["user_name"]),
            models.Index(fields=["steam_id"]),
        ]
    
    def __str__(self):
        return self.user_name or f"Steam User {self.steam_id}"

class Items(models.Model):
    name = models.CharField(verbose_name='название предмета', max_length=255)
    rarity = models.CharField("редкость предмета", max_length=50)
    price = models.DecimalField("цена предмета", max_digits=10, decimal_places=2)  
    is_stattrack = models.BooleanField('stattrack', default=False)
    
    class Meta:
        verbose_name = "item"
        verbose_name_plural = "items"
        ordering = ["name", "price"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["price"])
        ]
    
    def __str__(self):
        return f"{self.name} {self.price}"

class Cases(models.Model):
    name = models.CharField(verbose_name='название кейса', max_length=255)
    price = models.IntegerField("цена кейса")
    description = models.TextField("описание кейса")
    image = models.ImageField(
        "изображение кейса", 
        upload_to='cases/', 
        blank=True, 
        null=True
    )
    
    class Meta:
        verbose_name = "case"
        verbose_name_plural = "cases"
        ordering = ["price"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["price"])
        ]
    
    def __str__(self):
        return f"{self.name}"

class Contract(models.Model):
    name = models.CharField("название", max_length=255)
    amount = models.DecimalField("сумма апгрейда", max_digits=10, decimal_places=2)  
    item = models.ForeignKey(Items, verbose_name='предмет', on_delete=models.CASCADE)
    user = models.ForeignKey(Users, verbose_name='пользователь', on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "contract"
        verbose_name_plural = "contracts"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"])
        ]
    
    def __str__(self):
        return f"{self.name}"

class Upgrade(models.Model):
    amount = models.DecimalField("сумма апгрейда", max_digits=10, decimal_places=2)  
    upgrade_item = models.CharField("предмет для апгрейда", max_length=255)
    item = models.ForeignKey(Items, verbose_name='предметы', on_delete=models.CASCADE)
    user = models.ForeignKey(Users, verbose_name='пользователь', on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "upgrade"
        verbose_name_plural = "upgrades"
        ordering = ["amount"]
        indexes = [
            models.Index(fields=["amount"])
        ]
    
    def __str__(self):
        return f"{self.amount}"
    
class Chance(models.Model):
    chance = models.DecimalField("шанс выпадения", max_digits=10, decimal_places=2)  
    item = models.ForeignKey(Items, verbose_name='предметы', on_delete=models.CASCADE)
    cases = models.ForeignKey(Cases, verbose_name='кейс', on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "chance"
        verbose_name_plural = "chances"
        ordering = ["item"]
        indexes = [
            models.Index(fields=["item"])
        ]
    
    def __str__(self):
        return f"{self.item}"