from django.core.management.base import BaseCommand
from django.core.files import File
from vadim.models import Cases, Items, Chance
import random
from decimal import Decimal

class Command(BaseCommand):
    help = 'Добавляет демонстрационные кейсы и предметы'

    def handle(self, *args, **options):
        self.stdout.write('Добавление демонстрационных данных...')
        
        cases_data = [
            {
                'name': 'Кейс "Револьвер"',
                'price': 85,
                'description': 'Кейс с оружием из обновления "Револьвер"',
                'rarity_distribution': {'common': 60, 'rare': 25, 'epic': 10, 'legendary': 4, 'ancient': 1}
            },
            {
                'name': 'Кейс "Спектр"',
                'price': 120,
                'description': 'Элегантный кейс с уникальными скинами',
                'rarity_distribution': {'common': 55, 'rare': 27, 'epic': 12, 'legendary': 5, 'ancient': 1}
            },
            {
                'name': 'Кейс "Гамма"',
                'price': 95,
                'description': 'Зеленый кейс с яркими скинами',
                'rarity_distribution': {'common': 58, 'rare': 26, 'epic': 11, 'legendary': 4, 'ancient': 1}
            },
            {
                'name': 'Кейс "Горизонт"',
                'price': 110,
                'description': 'Кейс с космической тематикой',
                'rarity_distribution': {'common': 56, 'rare': 27, 'epic': 12, 'legendary': 4, 'ancient': 1}
            },
            {
                'name': 'Кейс "Призма"',
                'price': 105,
                'description': 'Кейс с яркими и цветными скинами',
                'rarity_distribution': {'common': 57, 'rare': 26, 'epic': 12, 'legendary': 4, 'ancient': 1}
            },
            {
                'name': 'Кейс "Опасная зона"',
                'price': 90,
                'description': 'Кейс вдохновленный режимом Danger Zone',
                'rarity_distribution': {'common': 59, 'rare': 26, 'epic': 10, 'legendary': 4, 'ancient': 1}
            },
            {
                'name': 'Кейс "Сломанный коготь"',
                'price': 150,
                'description': 'Премиум кейс с эксклюзивными предметами',
                'rarity_distribution': {'common': 50, 'rare': 28, 'epic': 14, 'legendary': 6, 'ancient': 2}
            },
            {
                'name': 'Кейс "Фракция"',
                'price': 115,
                'description': 'Кейс с противостоянием фракций',
                'rarity_distribution': {'common': 56, 'rare': 27, 'epic': 12, 'legendary': 4, 'ancient': 1}
            },
        ]

        items_by_rarity = {
            'common': [
                {'name': 'MAG-7 | Теплый', 'price': Decimal('5.50')},
                {'name': 'MP9 | Зеленый пластик', 'price': Decimal('4.20')},
                {'name': 'Glock-18 | Оксид', 'price': Decimal('6.80')},
                {'name': 'USP-S | Лесные листья', 'price': Decimal('7.50')},
                {'name': 'Five-SeveN | Лесной', 'price': Decimal('5.90')},
                {'name': 'P250 | Металл', 'price': Decimal('6.20')},
                {'name': 'FAMAS | Цифровой', 'price': Decimal('8.30')},
                {'name': 'Galil AR | Камуфляж', 'price': Decimal('7.80')},
                {'name': 'SSG 08 | Абрикос', 'price': Decimal('9.10')},
                {'name': 'AUG | Колея', 'price': Decimal('8.90')},
            ],
            'rare': [
                {'name': 'AK-47 | Красная линия', 'price': Decimal('45.00')},
                {'name': 'M4A4 | Зенитка', 'price': Decimal('38.50')},
                {'name': 'AWP | Козырной туз', 'price': Decimal('52.00')},
                {'name': 'Desert Eagle | Кобальт', 'price': Decimal('35.80')},
                {'name': 'SSG 08 | Кровь в воде', 'price': Decimal('42.30')},
                {'name': 'P90 | Шелковый путь', 'price': Decimal('28.90')},
                {'name': 'MP7 | Импульс', 'price': Decimal('32.40')},
                {'name': 'UMP-45 | Преступник', 'price': Decimal('29.70')},
                {'name': 'MAC-10 | Ягненок', 'price': Decimal('31.20')},
                {'name': 'SG 553 | Пульсар', 'price': Decimal('44.50')},
            ],
            'epic': [
                {'name': 'AK-47 | Ламинат', 'price': Decimal('125.00')},
                {'name': 'M4A1-S | Золотая ветвь', 'price': Decimal('118.50')},
                {'name': 'AWP | Электрик Hive', 'price': Decimal('142.00')},
                {'name': 'Desert Eagle | Гипотермия', 'price': Decimal('98.80')},
                {'name': 'USP-S | Нейронная сеть', 'price': Decimal('88.30')},
                {'name': 'Glock-18 | Вода элементальная', 'price': Decimal('95.40')},
                {'name': 'P2000 | Империя', 'price': Decimal('82.90')},
                {'name': 'SSG 08 | Пара', 'price': Decimal('108.70')},
                {'name': 'FAMAS | Эйфория', 'price': Decimal('92.50')},
                {'name': 'Galil AR | Сахар', 'price': Decimal('85.60')},
            ],
            'legendary': [
                {'name': 'AK-47 | Гидропоника', 'price': Decimal('350.00')},
                {'name': 'M4A4 | Асiмов', 'price': Decimal('295.00')},
                {'name': 'AWP | Дракон Лор', 'price': Decimal('450.00')},
                {'name': 'Desert Eagle | Blaze', 'price': Decimal('280.00')},
                {'name': 'USP-S | Убийца', 'price': Decimal('225.00')},
                {'name': 'Glock-18 | Фадей', 'price': Decimal('210.00')},
                {'name': '★ Нож | Свежесть', 'price': Decimal('850.00')},
                {'name': '★ Нож | Ультрафиолет', 'price': Decimal('780.00')},
                {'name': '★ Нож | Сетка', 'price': Decimal('720.00')},
                {'name': '★ Перчатки | Убийца', 'price': Decimal('650.00')},
            ],
            'ancient': [
                {'name': 'AK-47 | Дикий лотос', 'price': Decimal('1250.00')},
                {'name': 'M4A4 | Харизма', 'price': Decimal('1100.00')},
                {'name': 'AWP | Медуза', 'price': Decimal('1850.00')},
                {'name': 'Desert Eagle | Изумруд', 'price': Decimal('950.00')},
                {'name': '★ Нож | Рубин', 'price': Decimal('2500.00')},
                {'name': '★ Нож | Сапфир', 'price': Decimal('2600.00')},
                {'name': '★ Нож | Черный жемчуг', 'price': Decimal('2800.00')},
                {'name': '★ Перчатки | Пандора', 'price': Decimal('1950.00')},
                {'name': '★ Перчатки | Изумруд', 'price': Decimal('2200.00')},
                {'name': '★ Нож | Лор', 'price': Decimal('3200.00')},
            ]
        }
        

        for case_data in cases_data:

            case = Cases.objects.create(
                name=case_data['name'],
                price=case_data['price'],
                description=case_data['description'],
                image=None  
            )
            
            self.stdout.write(f'Создан кейс: {case.name}')

            items_added = []

            for rarity, items_list in items_by_rarity.items():
  
                rarity_count = case_data['rarity_distribution'].get(rarity, 5)

                selected_items = random.sample(items_list, min(rarity_count, len(items_list)))
                
                for item_data in selected_items:

                    item, created = Items.objects.get_or_create(
                        name=item_data['name'],
                        defaults={
                            'rarity': rarity,
                            'price': item_data['price'],
                            'is_stattrack': random.choice([True, False]) if rarity in ['legendary', 'ancient'] else False
                        }
                    )
                    
                    if created:
                        self.stdout.write(f'  Создан предмет: {item.name}')
                    
                    chance_percentage = 0
                    if rarity == 'common':
                        chance_percentage = random.uniform(5, 12)
                    elif rarity == 'rare':
                        chance_percentage = random.uniform(3, 8)
                    elif rarity == 'epic':
                        chance_percentage = random.uniform(1.5, 4)
                    elif rarity == 'legendary':
                        chance_percentage = random.uniform(0.8, 2)
                    elif rarity == 'ancient':
                        chance_percentage = random.uniform(0.2, 0.8)
                    
                    Chance.objects.create(
                        chance=Decimal(str(round(chance_percentage, 2))),
                        item=item,
                        cases=case
                    )
                    
                    items_added.append(item.name)
            
            self.stdout.write(f'  Добавлено предметов: {len(items_added)}')
            self.stdout.write('-' * 50)
        
        self.stdout.write(self.style.SUCCESS('Демонстрационные данные успешно добавлены!'))
        self.stdout.write(self.style.SUCCESS(f'Создано кейсов: {len(cases_data)}'))
        self.stdout.write(self.style.SUCCESS(f'Создано предметов: {Items.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Создано шансов: {Chance.objects.count()}'))