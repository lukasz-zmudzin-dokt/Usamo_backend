from rest_framework import serializers


class PolishModelSerializer(serializers.ModelSerializer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for field in self.fields:
            self.fields[field].error_messages = {
                'required': 'To pole jest wymagane',
                'blank': 'To pole nie może być puste'
            }