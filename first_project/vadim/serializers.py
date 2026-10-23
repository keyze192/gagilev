from rest_framework import serializers
from .models import (
    Users, Items, Cases, Contract, Upgrade, Chance,
    CaseOpening, UserInventory
)

class UsersSerializer(serializers.ModelSerializer):
    display_name = serializers.ReadOnlyField()
    is_steam_connected = serializers.ReadOnlyField()
    class Meta:
        model = Users
        fields = [
            'id', 'user', 'user_name', 'email', 'balance', 'trade_link',
            'is_admin', 'steam_id', 'steam_avatar', 'steam_profile_url',
            'steam_username', 'steam_realname', 'steam_country',
            'steam_created_at', 'last_login_steam', 'created_at',
            'display_name', 'is_steam_connected',
        ]
        read_only_fields = ['created_at', 'last_login_steam', 'steam_id']

class ItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Items
        fields = ['id', 'name', 'rarity', 'price', 'is_stattrack']

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
    cases_name = serializers.CharField(source='cases.name', read_only=True)
    class Meta:
        model = Chance
        fields = ['id', 'chance', 'item', 'cases', 'item_name', 'cases_name']

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
    user_name = serializers.CharField(source='user.display_name', read_only=True)
    case_name = serializers.CharField(source='case.name', read_only=True)
    item_name = serializers.CharField(source='item.name', read_only=True)
    item_price = serializers.DecimalField(source='item.price', max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = CaseOpening
        fields = ['id', 'user', 'case', 'item', 'opened_at', 'user_name', 'case_name', 'item_name', 'item_price']

class UserInventorySerializer(serializers.ModelSerializer):
    item_details = ItemsSerializer(source='item', read_only=True)
    class Meta:
        model = UserInventory
        fields = ['id', 'user', 'item', 'item_details', 'quantity', 'obtained_at']
        read_only_fields = ['obtained_at']