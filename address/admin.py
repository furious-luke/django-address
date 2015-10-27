from django.contrib import admin
from django import forms
# from django.contrib.admin import SimpleListFilter
from .models import *
from .kinds import KIND_KEY_TABLE


class BitFieldWidget(forms.CheckboxSelectMultiple):

    def render(self, name, value, attrs=None):
        value_list = []
        for bit, desc in self.choices:
            if value & bit:
                value_list.append(bit)
        return super(BitFieldWidget, self).render(name, value_list, attrs)

    def value_from_datadict(self, data, files, name):
        value_list = super(BitFieldWidget, self).value_from_datadict(data, files, name)
        value = 0
        for bit in value_list:
            value = value | int(bit)
        return value


class ComponentAdminForm(forms.ModelForm):

    class Meta:
        model = Component
        fields = '__all__'
        widgets = {
            'kind': BitFieldWidget(choices=KIND_KEY_TABLE.items()),
        }


# class UnidentifiedListFilter(SimpleListFilter):
#     title = 'unidentified'
#     parameter_name = 'unidentified'

#     def lookups(self, request, model_admin):
#         return (('unidentified', 'unidentified'),)

#     def queryset(self, request, queryset):
#         if self.value() == 'unidentified':
#             return queryset.filter(locality=None)

@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    form = ComponentAdminForm
    # search_fields = ('name', 'code')

# @admin.register(State)
# class StateAdmin(admin.ModelAdmin):
#     search_fields = ('name', 'code')

# @admin.register(Locality)
# class LocalityAdmin(admin.ModelAdmin):
#     search_fields = ('name', 'postal_code')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    filter_horizontal = ('components',)
    # search_fields = ('name',)
    # list_filter = (UnidentifiedListFilter,)
