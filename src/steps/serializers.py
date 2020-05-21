from rest_framework import serializers
from .models import *


class SubStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubStep
        fields = ['id', 'order', 'title', 'parent']
        extra_kwargs = {
            'order': {
                'read_only': True
            },
            'id': {
                'read_only': True
            }
        }


class StepSerializer(serializers.ModelSerializer):
    video = serializers.URLField(required=False)
    parent_id = serializers.UUIDField(source='parent.id', write_only=True)
    substeps = SubStepSerializer(required=False, many=True)

    class Meta:
        model = Step
        fields = ['id', 'parent', 'parent_id', 'title', 'description', 'video', 'children', 'substeps']
        extra_kwargs = {
            'id': {
                'read_only': True
            },
            'children': {
                'many': True,
                'read_only': True
            }
        }

    def create(self, validated_data):
        print(validated_data)
        parent = validated_data.get('parent')
        title = validated_data.get('title')
        description = validated_data.get('description')
        video = validated_data.get('video')
        instance = Step.objects.create(parent_id=parent['id'], title=title, description=description)
        if video:
            instance.video = video

        if 'substeps' in validated_data:
            substeps_data = validated_data.get('substeps')
            for data in substeps_data:
                substep = SubStep.objects.create(parent=instance, **data)
                substep.save()

        instance.save()
        return instance


class RootSerializer(StepSerializer):
    parent = None