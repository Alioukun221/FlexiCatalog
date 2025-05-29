from mongoengine import Document, EmailField

class NewsletterSubscriber(Document):
    email = EmailField(required=True, unique=True)
