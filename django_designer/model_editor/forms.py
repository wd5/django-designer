from django import forms
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.forms.models import modelformset_factory
from models import Model, Field, UniqueTogether


class NewModelForm(forms.ModelForm):
    class Meta:
        model = Model
        exclude = ('application',)
    
    def __init__(self, data, application):
        self.application = application
        super(NewModelForm, self).__init__(data)
    
    def save(self):
        obj = super(NewModelForm, self).save(commit=False)
        obj.application = self.application
        obj.save()
        return obj
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            try:
                Model.objects.get(application=self.application, name=name)#TODO: ci check ?
                raise forms.ValidationError('Model "%s" already exist' % name)
            except Model.DoesNotExist:
                pass
        return name

class EditModelForm(forms.ModelForm):
    class Meta:
        model = Model
        exclude = ('application','is_external')
    
    #TODO: name validation


class AutocompleteModelWidget(forms.HiddenInput):
    is_hidden = False
    def render(self, name, value, attrs=None):
        html = super(AutocompleteModelWidget, self).render(name, value, attrs)
        model_name = u''
        if value:
            try:
                model_name = Model.objects.get(pk=value)
            except Model.DoesNotExist:
                pass
        html += u'<input type="text" class="autocomplete" value="%s">' % escape(model_name)
        return mark_safe(html) 
    

class FieldForm(forms.ModelForm):
    class Meta:
        model = Field
        exclude = ('model',)
    relation = forms.ModelChoiceField(queryset=Model.objects.all(), required=False
                                    , widget=AutocompleteModelWidget)
    sort_order = forms.IntegerField(required=False
                                    , widget=forms.HiddenInput(attrs={'class':'sort_field'}))
    
    POPUP_FIELDS = ('max_length', 
                    'related_name', 'to_field',
                    'auto_now', 'auto_now_add', 
                    'max_digits', 'decimal_places', 
                    'verify_exists','upload_to',
                    'primary_key', 'db_index', 'editable', 
                    'verbose_name', 'default', 'help_text'
                    )
    
    GRID_FIELDS = ['name', 'type', 'relation', 'null', 'blank', 'unique', 'DELETE']
    
    def __init__(self, *args, **kwargs):
        super(FieldForm, self). __init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name in FieldForm.POPUP_FIELDS:
                field.label = name
        self.append_titles()
    
    def append_titles(self):
        for name, field in self.fields.items():
            if not field.widget.is_hidden:
                field.widget.attrs.update({'title': name})
    
    def grid_fields(self):
        return [self[f] for f in FieldForm.GRID_FIELDS]
    
    def popup_fields(self):
        return [self[f] for f in FieldForm.POPUP_FIELDS]


class BaseFieldFormSet(forms.models.BaseModelFormSet):
    def clean(self):
        if any(self.errors):
            return
        primary_keys = []
        for form in self.forms:
            if form.cleaned_data.get('primary_key'):
                primary_keys.append(form.cleaned_data['name'])
        if len(primary_keys) > 1:
            raise forms.ValidationError('Only one primary key allowed (curently: %s)' % ','.join(primary_keys))


ModelFieldFormSet = modelformset_factory(Field, extra=4, can_delete=True, 
                                         form=FieldForm, formset=BaseFieldFormSet)



class UniqueTogetherForm(forms.ModelForm):
    class Meta:
        model = UniqueTogether
        fields = ('fields',)
    fields = forms.ModelMultipleChoiceField(queryset=Field.objects.all(), label=''
                                            , widget=forms.CheckboxSelectMultiple())
    
    def __init__(self, data=None, model=None):
        assert model is not None
        self.model = model
        super(UniqueTogetherForm, self).__init__(data)
        self.fields['fields'].queryset = model.field_set
    
    def save(self, commit=True):
        self.instance.model = self.model
        return super(UniqueTogetherForm, self).save(commit) 
    
    def clean_fields(self):
        value = self.cleaned_data.get('fields')
        if not value:
            return value
        if len(value) < 2:
            raise forms.ValidationError("Select at least 2 fields")
        return value
    