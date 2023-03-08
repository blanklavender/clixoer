from django.db import models

class hit_counters(models.Model):
    #id =  models.IntegerField(primary_key=True)
    visitednode_name = models.CharField(max_length=30)
    visitednode_id = models.CharField(max_length=30)
    created_date = models.DateField()
    preview_count = models.IntegerField(default = 0)
    visit_count = models.IntegerField(default = 0)
    download_count = models.IntegerField(default = 0)
    session_id = models.CharField(max_length=30)
    last_updated = models.DateField()
    language = models.CharField(max_length=30)
    share_count =  models.IntegerField(default = 0)
    print_count =  models.IntegerField(default = 0)
    feedback_count =  models.IntegerField(default = 0)
    help_count =  models.IntegerField(default = 0)
    class Meta:
        db_table = 'hit_counters'

