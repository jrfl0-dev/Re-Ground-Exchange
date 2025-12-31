from django.db import models
from django.conf import settings

# conversation model shows who’s in the chat and when it started
class Conversation(models.Model):
    # keep track of every user in this conversation (most chats are just two people)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    # making it easy to tell which convo this is in the admin
    def __str__(self):
        return f"Conversation {self.id}"

# message model shows the actual text each person sends inside a convo
class Message(models.Model):
    # link message to whichever conversation thread it belongs to
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    # track which user actually sent this particular message
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)

    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        # show messages oldest-to-newest so the thread reads top to bottom
        ordering = ['created_at']

    def __str__(self):
        return f"Message {self.id} by {self.sender}"
