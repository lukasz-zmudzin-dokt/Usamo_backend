import uuid
from django.db import models
from django.db.models import Max
from account.models import DefaultAccount


class BaseStep(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50)
    description = models.TextField(null=True)

    class Meta:
        abstract = True


class Step(BaseStep):
    parent = models.ForeignKey('self', related_name='children', null=True, on_delete=models.CASCADE)
    video = models.URLField(null=True)

    def delete(self, using=None, keep_parents=True):
        for child in self.children.all():
            child.parent = self.parent
            child.save()
        super().delete(using=using, keep_parents=keep_parents)

    def hard_delete(self, using=None, keep_parents=True):
        super().delete(using=using, keep_parents=keep_parents)

    def reorder(self):
        previous = -1
        for substep in self.substeps.all():
            substep.order = previous + 1
            substep.save()
            previous += 1


class Root(Step):
    parent = None

    def delete(self, using=None, keep_parents=True):
        for step in Step.objects.all():
            step.hard_delete()
        self.hard_delete()


class SubStep(BaseStep):
    parent = models.ForeignKey(Step, related_name='substeps', null=False, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    video = models.URLField(null=True)

    class Meta:
        ordering = ['order']

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.parent.substeps.filter(id=self.id).exists() and self.parent.substeps.count() > 0:
            self.order = self.parent.substeps.aggregate(Max('order'))['order__max'] + 1
        super().save(force_insert=force_insert, force_update=force_update, using=using,
                     update_fields=update_fields)

    def switch_places(self, other):
        self.order, other.order = other.order, self.order
        self.save()
        other.save()
        self.parent.reorder()

    def move_to_spot(self, new_order):
        for substep in self.parent.substeps.filter(order__gte=new_order):
            substep.order += 1
            substep.save()
        self.order = new_order
        self.save()
        self.parent.reorder()

    def delete(self, using=None, keep_parents=True):
        super().delete(using=using, keep_parents=keep_parents)
        self.parent.reorder()


class UserPerspective(models.Model):
    user = models.OneToOneField(DefaultAccount, primary_key=True, parent_link=True, on_delete=models.CASCADE)
    step = models.OneToOneField(Step, on_delete=models.CASCADE)
    substep_order = models.PositiveIntegerField(default=0)
