from rest_framework import serializers
from .models import *


class SubStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubStep
        fields = ['id', 'order', 'title', 'video', 'parent']
        extra_kwargs = {
            'order': {
                'read_only': True
            },
            'id': {
                'read_only': True
            },
            'parent': {
                'required': False
            },
            'video': {
                'required': False
            }
        }


class ChildStepSerializer(serializers.ModelSerializer):

    class Meta:
        model = Step
        fields = ['id', 'title']


class StepSerializer(serializers.ModelSerializer):
    video = serializers.URLField(required=False)
    substeps = SubStepSerializer(required=False, many=True)
    children = ChildStepSerializer(many=True, read_only=True)

    class Meta:
        model = Step
        fields = ['id', 'parent', 'title', 'description', 'video', 'children', 'substeps']
        extra_kwargs = {
            'id': {
                'read_only': True
            }
        }

    def create(self, validated_data):
        parent = validated_data.get('parent')
        title = validated_data.get('title')
        description = validated_data.get('description')
        video = validated_data.get('video')
        instance = Step.objects.create(parent=parent, title=title, description=description)
        if video:
            instance.video = video

        if 'substeps' in validated_data:
            substeps_data = validated_data.get('substeps')
            for data in substeps_data:
                substep = SubStep.objects.create(parent=instance, **data)
                substep.save()

        instance.save()
        return instance

    def update(self, instance, validated_data):
        if 'substeps' in validated_data:
            substeps_data = validated_data.pop('substeps')
            for substep in SubStep.objects.filter(parent=instance):
                substep.delete()
            for data in substeps_data:
                substep = SubStep.objects.create(parent=instance, **data)
                substep.save()
        return super().update(instance, validated_data)


class RootSerializer(serializers.ModelSerializer):
    children = ChildStepSerializer(many=True, read_only=True)

    class Meta:
        model = Root
        fields = ['id',  'title', 'description', 'children']
        extra_kwargs = {
            'id': {
                'read_only': True
            }
        }


class UserPerspectiveSerializer(serializers.ModelSerializer):
    step = StepSerializer(read_only=True)

    class Meta:
        model = UserPerspective
        fields = ['step', 'substep_order']
