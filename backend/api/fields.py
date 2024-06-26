import io
import base64
import uuid
from PIL import Image
from rest_framework import serializers
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError


class Base64ImageField(serializers.ImageField):
    """
    Кастомное поле для обработки загрузки изображений через данные, закодированные в base64.
    """
    def to_internal_value(self, data):
        """
        Конвертирует данные изображения, закодированные в base64, в файл изображения.

        Args:
            data (str): Данные изображения, закодированные в base64.

        Returns:
            SimpleUploadedFile: Декодированный файл изображения.

        Raises:
            ValidationError: Если данные не являются допустимыми данными изображения в base64.
        """
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
        """
        Получает расширение файла изображения.

        Args:
            decoded_file (bytes): Декодированные байты файла изображения.

        Returns:
            str: Расширение файла изображения.

        Raises:
            ValidationError: Если файл не является допустимым изображением.
        """
        try:
            image = Image.open(io.BytesIO(decoded_file))
        except:
            raise ValidationError('Загрузите валидное изображение')
        else:
            extension = image.format.lower()
        return 'jpg' if extension == 'jpeg' else extension
