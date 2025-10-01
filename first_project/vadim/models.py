from django.db import models

class Users(models.Model):
    user_name = models.CharField(verbose_name='имя пользователя', max_length=50)
    email = models.EmailField("почта", max_length=255)
    balance = models.IntegerField("баланс аккаунта", default=0)
    trade_link = models.TextField('ссылка для обмена')
    role = models.CharField("admin or user", max_length=20, default='user')
    
    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["user_name", "balance"]
        indexes = [
            models.Index(fields=["user_name"])
        ]
    
    def __str__(self):
        return f"{self.user_name} {self.role}"

class Items(models.Model):
    name = models.CharField(verbose_name='название предмета', max_length=255)
    rarity = models.CharField("редкость предмета", max_length=50)
    price = models.DecimalField("цена предмета", max_digits=10, decimal_places=2)  
    is_stattrack = models.BooleanField('stattrack or no', default=False)
    
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

class case_contents(models.Model):
    drop_chance = models.DecimalField("шанс выпадения", max_digits=5, decimal_places=2)  
    case = models.ForeignKey(Cases, verbose_name='кейс', on_delete=models.CASCADE)
    item = models.ForeignKey(Items, verbose_name='предмет', on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "case_content"
        verbose_name_plural = "case_contents"
        ordering = ["drop_chance"]
        indexes = [
            models.Index(fields=["drop_chance"])
        ]
    
    def __str__(self):
        return f"{self.drop_chance}%"