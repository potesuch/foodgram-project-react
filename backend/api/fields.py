import io
import base64
import uuid
from PIL import Image
from rest_framework import serializers
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            if ';base64,' in data:
                header, base64_data = data.split(';base64,')
                file_mime_type = header.replace('data:', '')
                try:
                    decoded_file = base64.b64decode(base64_data)
                except:
                    raise ValidationError('Загрузите валидное изображение')
                file_name = str(uuid.uuid4())
                file_extension = self.get_file_extension(decoded_file)
                complete_file_name = file_name + '.' + file_extension
                data = SimpleUploadedFile(
                    name=complete_file_name,
                    content=decoded_file,
                    content_type=file_mime_type
                )
                return super().to_internal_value(data)
        return ValidationError('Неверный формат файла')

    def get_file_extension(self, decoded_file):
        try:
            image = Image.open(io.BytesIO(decoded_file))
        except:
            raise ValidationError('Загрузите валидное изображение')
        else:
            extension = image.format.lower()
        return 'jpg' if extension == 'jpeg' else extension
