import uuid

from django.db import models
from django.db.models import Max


class BaseStep(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50)
    seen = models.BooleanField(default=False)

    class Meta:
        abstract = True


class Step(BaseStep):
    parent = models.ForeignKey('self', related_name='children', null=True, on_delete=models.CASCADE)
    description = models.TextField()
    video = models.URLField(null=True)

    def delete(self, using=None, keep_parents=True):
        for child in self.children.all():
            child.parent = self.parent
            child.save()
        super().delete(using=using, keep_parents=keep_parents)


class Root(Step):
    parent = None


class SubStep(BaseStep):
    parent = models.ForeignKey(Step, related_name='substeps', null=False, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, new=True):
        if new and self.parent.substeps.count() > 0:
            self.order = self.parent.substeps.aggregate(Max('order'))['order__max'] + 1
        super().save(force_insert=force_insert, force_update=force_update, using=using,
                     update_fields=update_fields)

    def switch_places(self, other):
        self.order, other.order = other.order, self.order
        self.save(new=False)
        other.save(new=False)

    def move_to_spot(self, new_order):
        max_order = self.parent.substeps.aggregate(Max('order'))['order__max']
        if new_order > max_order:
            new_order = max_order
        for substep in self.parent.substeps.filter(order__gte=new_order):
            substep.order += 1
            substep.save(new=False)
        self.order = new_order
        self.save(new=False)

