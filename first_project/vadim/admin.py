from django.contrib import admin
from .models import (
    Users, Items, Cases, Contract, Upgrade, Chance,
    CaseOpening, UserInventory
)


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_name', 'email', 'balance', 'is_admin', 'steam_id', 'created_at')
    list_filter = ('is_admin', 'created_at')
    search_fields = ('user_name', 'email', 'steam_id', 'user__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)


@admin.register(Items)
class ItemsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'rarity', 'price', 'is_stattrack', 'image_url')
    list_filter = ('rarity', 'is_stattrack')
    search_fields = ('name',)
    ordering = ('rarity', 'name')


@admin.register(Cases)
class CasesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'description')
    search_fields = ('name', 'description')
    ordering = ('price',)


@admin.register(Chance)
class ChanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'cases', 'item', 'chance')
    list_filter = ('cases',)
    search_fields = ('item__name', 'cases__name')
    autocomplete_fields = ('item', 'cases')


@admin.register(CaseOpening)
class CaseOpeningAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'case', 'item', 'opened_at')
    list_filter = ('case', 'opened_at')
    search_fields = ('user__user_name', 'case__name', 'item__name')
    readonly_fields = ('opened_at',)
    ordering = ('-opened_at',)


@admin.register(UserInventory)
class UserInventoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'item', 'quantity', 'obtained_at')
    list_filter = ('obtained_at',)
    search_fields = ('user__user_name', 'item__name')
    autocomplete_fields = ('user', 'item')
    readonly_fields = ('obtained_at',)


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'amount', 'item', 'user')
    search_fields = ('name', 'user__user_name', 'item__name')


@admin.register(Upgrade)
class UpgradeAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'upgrade_item', 'item', 'user')
    search_fields = ('upgrade_item', 'user__user_name', 'item__name')