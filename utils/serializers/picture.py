import io
import sys

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import serializers


class ProfilePictureValidator(serializers.Serializer):
    profile_picture = serializers.ImageField(required=True)

    def validate_profile_picture(self, image):
        if image.size > 2 * 1024 * 1024:
            raise serializers.ValidationError("Image file too large (> 2MB)")

        try:
            img = Image.open(image)
            img.verify()

            # Re-open image (verify() closes it)
            img = Image.open(image)
            if img.width > 1000 or img.height > 1000:
                raise serializers.ValidationError("Image too large. Max dimensions: 1000x1000px")

            # Resize to standard dimensions
            img = img.resize((300, 300))
            # Convert to JPEG/PNG if not already
            if img.format not in ('JPEG', 'PNG'):
                img = img.convert('RGB')

            # This uploads it to ram
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=80)
            output.seek(0)

            return InMemoryUploadedFile(
                output, 'ImageField',
                f"{image.name.split('.')[0]}.jpg",
                'image/jpeg', sys.getsizeof(output), None
            )

        except Exception as e:
            raise serializers.ValidationError(f"Invalid image file: {str(e)}")
