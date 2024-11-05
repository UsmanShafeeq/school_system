from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField


# Category for items in inventory
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']


# Vendor model with additional details
class Vendor(models.Model):
    name = models.CharField(max_length=255)
    contact_no = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    active_status = models.BooleanField(default=True)
    joined_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} - {self.contact_no}'

    class Meta:
        ordering = ['name']


# Manager for custom item queries with advanced capabilities
class ItemManager(models.Manager):
    def in_stock(self):
        return self.filter(stock__quantity__gt=0)

    def out_of_stock(self):
        return self.filter(stock__quantity=0)

    def search(self, query):
        return self.filter(models.Q(name__icontains=query) | models.Q(sku__icontains=query))


# Represents an item in the inventory
class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    sku = models.CharField(max_length=50, unique=True, help_text="Stock Keeping Unit")
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ItemManager()  # Assign the custom manager

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        unique_together = ['name', 'sku']


# Audit model for tracking changes in inventory items
class InventoryChangeLog(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='change_logs')
    change_type = models.CharField(max_length=50, choices=[('add', 'Added'), ('remove', 'Removed'), ('update', 'Updated')])
    change_date = models.DateTimeField(auto_now_add=True)
    quantity_changed = models.IntegerField()
    remaining_quantity = models.IntegerField()
    user = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.change_type} {self.quantity_changed} of {self.item.name} on {self.change_date}"

    class Meta:
        ordering = ['-change_date']
        verbose_name_plural = "Inventory Change Logs"


# Tracks items in stock with advanced features
class ItemsInStock(models.Model):
    item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name='stock')
    quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=5, help_text="Minimum quantity before reorder")
    last_restocked = models.DateField(blank=True, null=True)

    def check_reorder(self):
        return self.quantity <= self.reorder_level

    def __str__(self):
        return f'{self.item.name} - Stock'

    class Meta:
        verbose_name_plural = "Items in Stock"
        ordering = ['item__name']


# Record of items returned to the vendor
class ReturnToVendor(models.Model):
    stock_item = models.ForeignKey(ItemsInStock, on_delete=models.CASCADE, related_name='returns_to_vendor')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='returned_items')
    return_date = models.DateField(default=timezone.now)
    quantity = models.PositiveIntegerField()
    reason = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.stock_item.quantity >= self.quantity:
            self.stock_item.quantity -= self.quantity
            self.stock_item.save()
            InventoryChangeLog.objects.create(
                item=self.stock_item.item,
                change_type='remove',
                quantity_changed=self.quantity,
                remaining_quantity=self.stock_item.quantity
            )
            super().save(*args, **kwargs)
        else:
            raise ValidationError("Not enough stock to return")

    def __str__(self):
        return f"{self.quantity} of {self.stock_item.item.name} returned to {self.vendor.name}"

    class Meta:
        ordering = ['-return_date']
        verbose_name = "Return to Vendor"


# Record of purchases from vendors
class PurchaseRecord(models.Model):
    stock_item = models.ForeignKey(ItemsInStock, on_delete=models.CASCADE, related_name='purchases')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='purchases')
    purchase_date = models.DateField(default=timezone.now)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    invoice_number = models.CharField(max_length=255, unique=True)

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.unit_price
        self.stock_item.quantity += self.quantity
        self.stock_item.last_restocked = self.purchase_date
        InventoryChangeLog.objects.create(
            item=self.stock_item.item,
            change_type='add',
            quantity_changed=self.quantity,
            remaining_quantity=self.stock_item.quantity
        )
        with transaction.atomic():
            self.stock_item.save()
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} of {self.stock_item.item.name} from {self.vendor.name} on {self.purchase_date}"

    class Meta:
        ordering = ['-purchase_date']
        verbose_name_plural = "Purchase Records"


# Department model for tracking issuance and returns
class Department(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Departments"


# Record of items issued to departments
class Issuance(models.Model):
    stock_item = models.ForeignKey(ItemsInStock, on_delete=models.CASCADE, related_name='issuances')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='issuances')
    issue_date = models.DateField(default=timezone.now)
    quantity = models.PositiveIntegerField()
    recipient = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if self.quantity <= 0:
            raise ValidationError("Issuance quantity must be greater than zero.")
        if self.stock_item.quantity < self.quantity:
            raise ValidationError("Not enough stock to issue.")

        self.stock_item.quantity -= self.quantity
        InventoryChangeLog.objects.create(
            item=self.stock_item.item,
            change_type='remove',
            quantity_changed=self.quantity,
            remaining_quantity=self.stock_item.quantity
        )
        with transaction.atomic():
            self.stock_item.save()
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} of {self.stock_item.item.name} issued to {self.department.name}"

    class Meta:
        ordering = ['-issue_date']
        verbose_name = "Issuance Record"


# Record of items returned from departments
class ReturnFromDepartment(models.Model):
    stock_item = models.ForeignKey(ItemsInStock, on_delete=models.CASCADE, related_name='returns_from_department')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='returns')
    return_date = models.DateField(default=timezone.now)
    quantity = models.PositiveIntegerField()
    condition = models.CharField(max_length=50, choices=[('Good', 'Good'), ('Damaged', 'Damaged')], default='Good')

    def save(self, *args, **kwargs):
        if self.quantity <= 0:
            raise ValidationError("Return quantity must be greater than zero.")
        
        self.stock_item.quantity += self.quantity
        InventoryChangeLog.objects.create(
            item=self.stock_item.item,
            change_type='add',
            quantity_changed=self.quantity,
            remaining_quantity=self.stock_item.quantity
        )
        with transaction.atomic():
            self.stock_item.save()
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} of {self.stock_item.item.name} returned from {self.department.name}"

    class Meta:
        ordering = ['-return_date']
        verbose_name = "Return from Department"


@receiver(pre_save, sender=Item)
def check_item_sku(sender, instance, **kwargs):
    if Item.objects.filter(sku=instance.sku).exclude(id=instance.id).exists():
        raise ValidationError(f"SKU {instance.sku} already exists.")


# Implementing a search utility for improved search functionality
def search_inventory(query):
    items = Item.objects.search(query)
    return items
