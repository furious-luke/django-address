import re

from django.db.models import Case, When, Value, BooleanField, F
from django.contrib import admin
from django import forms
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
# from django.contrib.admin import SimpleListFilter

from .models import Address, Component
from .kinds import KIND_KEY_TABLE
from .forms import AddressWidget, AddressField


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
    list_display = ('__str__', 'formatted', 'inline_lookup', 'consistent')
    list_filter = ('consistent',)
    search_fields = ('raw',)
    # list_filter = (UnidentifiedListFilter,)

    class Media:
        js = AddressWidget().media['js']

    def changelist_view(self, request, extra_content=None):
        pk = None
        for key, val in request.POST.items():
            match = re.match(r'^address_(\d+)_submit', key)
            if match:
                pk = match.group(1)
                break
        if pk is not None:
            obj = get_object_or_404(Address, pk=pk)
            name = 'address_' + pk
            value = AddressWidget().value_from_datadict(request.POST, None, name)
            value['raw'] = obj.raw # keep old raw value
            addr = Address.to_python(value, instance=obj)
        return super(AddressAdmin, self).changelist_view(request, extra_content)

    # def get_queryset(self, request):
    #     qs = super(AddressAdmin, self).get_queryset(request)
    #     qs = qs.annotate(consistent=Case(
    #         When(raw=F('formatted'), then=Value(True)),
    #         default=Value(False),
    #         output_field=BooleanField(),
    #     ))
    #     return qs

    def inline_lookup(self, obj):
        name = 'address_' + str(obj.pk)
        widget = AddressWidget().render(name, None, {'style': 'height: 11px'})
        return '%s<button name="%s_submit" type="submit">Save</button>'%(widget, name)
    inline_lookup.allow_tags = True

    # def consistent(self, obj):
    #     return get_consistency(obj)
    #     # return obj.raw == obj.formatted
    # consistent.boolean = True
    # # consistent.admin_order_field = 'consistent'
