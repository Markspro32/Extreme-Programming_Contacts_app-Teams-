from django.db import models


# Create your models here.

class Contact(models.Model):
    name = models.CharField(max_length=100)
    bookmarked = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def primary_email(self):
        """Get primary email or first email if no primary set"""
        primary = self.contact_methods.filter(method_type='email', is_primary=True).first()
        if primary:
            return primary.value
        # Fallback to first email
        email_method = self.contact_methods.filter(method_type='email').first()
        return email_method.value if email_method else None

    @property
    def primary_phone(self):
        """Get primary phone or first phone if no primary set"""
        primary = self.contact_methods.filter(method_type='phone', is_primary=True).first()
        if primary:
            return primary.value
        # Fallback to first phone
        phone_method = self.contact_methods.filter(method_type='phone').first()
        return phone_method.value if phone_method else None


class ContactMethod(models.Model):
    METHOD_TYPES = [
        ('phone', 'Phone'),
        ('email', 'Email'),
        ('social_media', 'Social Media'),
        ('address', 'Address'),
    ]

    contact = models.ForeignKey(Contact, related_name='contact_methods', on_delete=models.CASCADE)
    method_type = models.CharField(max_length=20, choices=METHOD_TYPES)
    label = models.CharField(max_length=50, blank=True, help_text="Optional label like 'Work', 'Home', 'Personal'")
    value = models.TextField(help_text="The contact detail value")
    is_primary = models.BooleanField(default=False, help_text="Mark as primary contact method")

    class Meta:
        ordering = ['method_type', '-is_primary', 'label']

    def __str__(self):
        label_part = f" ({self.label})" if self.label else ""
        primary_part = " (Primary)" if self.is_primary else ""
        return f"{self.contact.name} - {self.get_method_type_display()}{label_part}{primary_part}"

    def save(self, *args, **kwargs):
        # Ensure only one primary per method type per contact
        if self.is_primary:
            ContactMethod.objects.filter(
                contact=self.contact,
                method_type=self.method_type,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)
