from django.contrib import admin
from .models import Category, Vendor, Item, InventoryChangeLog, ItemsInStock, ReturnToVendor, PurchaseRecord, Department, Issuance, ReturnFromDepartment

# Admin configuration for Category
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)
    list_filter = ('created_at',)

admin.site.register(Category, CategoryAdmin)


# Admin configuration for Vendor
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_no', 'active_status', 'joined_date')
    search_fields = ('name', 'contact_no')
    list_filter = ('active_status', 'joined_date')
    ordering = ('name',)

admin.site.register(Vendor, VendorAdmin)


class ItemsInStockInline(admin.TabularInline):
    model = ItemsInStock
    extra = 1  # Number of empty forms to display


class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'unit_price', 'category', 'created_at')
    search_fields = ('name', 'sku')
    list_filter = ('category',)
    ordering = ('name',)
    inlines = [ItemsInStockInline]  # Adding inline model

admin.site.register(Item, ItemAdmin)


# Admin configuration for ItemsInStock
class ItemsInStockAdmin(admin.ModelAdmin):
    list_display = ('item', 'quantity', 'reorder_level', 'last_restocked')
    list_filter = ('reorder_level',)
    search_fields = ('item__name',)
    ordering = ('item',)

admin.site.register(ItemsInStock, ItemsInStockAdmin)


# Admin configuration for InventoryChangeLog
class InventoryChangeLogAdmin(admin.ModelAdmin):
    list_display = ('item', 'change_type', 'change_date', 'quantity_changed', 'remaining_quantity', 'user')
    list_filter = ('change_type', 'change_date')
    search_fields = ('item__name', 'user')
    ordering = ('-change_date',)

admin.site.register(InventoryChangeLog, InventoryChangeLogAdmin)


# Admin configuration for ReturnToVendor
class ReturnToVendorAdmin(admin.ModelAdmin):
    list_display = ('stock_item', 'vendor', 'return_date', 'quantity', 'reason')
    list_filter = ('return_date',)
    search_fields = ('stock_item__item__name', 'vendor__name')
    ordering = ('-return_date',)

admin.site.register(ReturnToVendor, ReturnToVendorAdmin)


# Admin configuration for PurchaseRecord
class PurchaseRecordAdmin(admin.ModelAdmin):
    list_display = ('stock_item', 'vendor', 'purchase_date', 'quantity', 'unit_price', 'total_cost', 'invoice_number')
    list_filter = ('purchase_date', 'vendor')
    search_fields = ('stock_item__item__name', 'invoice_number')
    ordering = ('-purchase_date',)

admin.site.register(PurchaseRecord, PurchaseRecordAdmin)


# Admin configuration for Department
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')
    search_fields = ('name',)
    ordering = ('name',)

admin.site.register(Department, DepartmentAdmin)


# Admin configuration for Issuance
class IssuanceAdmin(admin.ModelAdmin):
    list_display = ('stock_item', 'department', 'issue_date', 'quantity', 'recipient')
    list_filter = ('issue_date', 'department')
    search_fields = ('stock_item__item__name', 'department__name')
    ordering = ('-issue_date',)

admin.site.register(Issuance, IssuanceAdmin)


# Admin configuration for ReturnFromDepartment
class ReturnFromDepartmentAdmin(admin.ModelAdmin):
    list_display = ('stock_item', 'department', 'return_date', 'quantity', 'condition')
    list_filter = ('return_date', 'condition', 'department')
    search_fields = ('stock_item__item__name', 'department__name')
    ordering = ('-return_date',)

admin.site.register(ReturnFromDepartment, ReturnFromDepartmentAdmin)
