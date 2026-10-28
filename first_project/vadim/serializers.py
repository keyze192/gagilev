from rest_framework import serializers
from .models import (
    Users, Items, Cases, Contract, Upgrade, Chance,
    CaseOpening, UserInventory
)

def get_item_icon(name=''):
    n = (name or '').lower()
    if 'нож' in n or 'knife' in n: return 'fa-crosshairs'
    if 'перчатк' in n or 'glove' in n: return 'fa-hand-paper'
    if any(x in n for x in ['ak', 'awp', 'm4', 'deagle', 'usp', 'glock', 'famas', 'aug', 'ssg', 'scar']):
        return 'fa-gun'
    return 'fa-cube'

RARITY_NAMES = {
    'common': 'Обычный', 'rare': 'Редкий', 'epic': 'Эпический',
    'legendary': 'Легендарный', 'ancient': 'Древний',
}


class UsersSerializer(serializers.ModelSerializer):
    display_name = serializers.ReadOnlyField()
    class Meta:
        model = Users
        fields = ['id', 'user_name', 'email', 'balance', 'trade_link',
                  'is_admin', 'created_at', 'display_name']
        read_only_fields = ['created_at']

class ItemsSerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()
    rarity_class = serializers.SerializerMethodField()
    rarity_name = serializers.SerializerMethodField()

    class Meta:
        model = Items
        fields = ['id', 'name', 'rarity', 'price', 'is_stattrack',
                  'icon', 'rarity_class', 'rarity_name', 'image_url']

    def get_icon(self, obj): 
        return get_item_icon(obj.name)
    def get_rarity_class(self, obj): 
        return (obj.rarity or 'common').lower()
    def get_rarity_name(self, obj): 
        return RARITY_NAMES.get((obj.rarity or 'common').lower(), 'Обычный')


class CasesSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = Cases
        fields = ['id', 'name', 'price', 'description', 'image', 'image_url']
        extra_kwargs = {'image': {'required': False, 'allow_null': True}}
        
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

class CasesListSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = Cases
        fields = ['id', 'name', 'price', 'image_url']
        
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

class ChanceSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    item_details = ItemsSerializer(source='item', read_only=True) # <--- ВОТ ОНО, вложенный объект с ценой
    cases_name = serializers.CharField(source='cases.name', read_only=True)
    
    class Meta:
        model = Chance
        fields = ['id', 'chance', 'item', 'cases', 'item_name', 'item_details', 'cases_name']

class ContractSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.display_name', read_only=True)
    item_name = serializers.CharField(source='item.name', read_only=True)
    class Meta:
        model = Contract
        fields = ['id', 'name', 'amount', 'item', 'user', 'user_name', 'item_name']

class UpgradeSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.display_name', read_only=True)
    item_name = serializers.CharField(source='item.name', read_only=True)
    class Meta:
        model = Upgrade
        fields = ['id', 'amount', 'upgrade_item', 'item', 'user', 'user_name', 'item_name']

class CaseOpeningSerializer(serializers.ModelSerializer):
    user_name  = serializers.CharField(source='user.display_name', read_only=True)
    case_name  = serializers.CharField(source='case.name', read_only=True)
    item_name  = serializers.CharField(source='item.name', read_only=True)
    item_price = serializers.DecimalField(source='item.price', max_digits=10, decimal_places=2, read_only=True)
    rarity     = serializers.SerializerMethodField()
    time_ago   = serializers.SerializerMethodField()

    class Meta:
        model = CaseOpening
        fields = ['id', 'user', 'case', 'item', 'opened_at',
                  'user_name', 'case_name', 'item_name', 'item_price', 'rarity', 'time_ago']

    def get_rarity(self, obj): return (obj.item.rarity or 'common').lower()
    def get_time_ago(self, obj):
        from django.utils.timesince import timesince
        return timesince(obj.opened_at, depth=1) + ' назад'

class UserInventorySerializer(serializers.ModelSerializer):
    item_details = ItemsSerializer(source='item', read_only=True)
    class Meta:
        model = UserInventory
        fields = ['id', 'user', 'item', 'item_details', 'quantity', 'obtained_at']
        read_only_fields = ['obtained_at']

class UsersSelfUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['user_name', 'email', 'trade_link']