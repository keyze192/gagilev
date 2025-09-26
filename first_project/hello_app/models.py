from django.db import models

# Create your models here.

class Author(models.Model):
    name = models.CharField(verbose_name='имя автора', max_length=20)
    surname = models.CharField("Фамилия", max_length=25)
    birthday = models.DateField("Дата рождение")
    bio = models.TextField('Биография')
    desc = models.CharField("Умер или нет", default='No')
    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"
        ordering = ["surname", "name"]
        indexes = [
            models.Index(fields=["surname"])
        ]

        constraints = [
            models.UniqueConstraint(
                fields = ["surname", "bio"],
                condition = models.Q(desc = "Жив"),
                name = "unique_surname_bio"
            ),
            ]

    def str(self):
        return f"{self.surname} {self.name}"

class Publisher(models.Model):
    namr = models.CharField("Название", unique=True)

class Book(models.Model):
    title = models.CharField("Название", max_length=50)
    id_publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    id_author = models.ManyToManyField(Author)
