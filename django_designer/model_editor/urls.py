from django.conf.urls.defaults import *

urlpatterns = patterns('model_editor.views',
    url(r'^(\d+)/$', 'model_list', name='application-models'),
    url(r'^new-model/(\d+)/$', 'new_model', name='new-model'),
    url(r'^edit-model/(\d+)/$', 'edit_model', name='edit-model'),
    url(r'^delete-model/(\d+)/$', 'delete_model', name='delete-model'),
    url(r'^model-code/(\d+)/$', 'get_models_code', name='model-code'),
    url(r'^app-code/(\d+)/$', 'get_app_models_code', name='app-models-code'),
    url(r'^unique-together-add/(\d+)/$', 'unique_together_add', name='unique-together-add'),
    url(r'^unique-together-remove/(\d+)/$', 'unique_together_remove', name='unique-together-remove'),
    
)
