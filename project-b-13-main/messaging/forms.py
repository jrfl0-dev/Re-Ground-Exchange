from django import forms

class NewConversationForm(forms.Form):
    email = forms.EmailField(label="Recipient email", widget=forms.EmailInput(attrs={
        "placeholder": "recipient@uva.edu",
        "class": "form-control",
    }))

class MessageForm(forms.Form):
    body = forms.CharField(
        widget=forms.Textarea(attrs={
            "rows": 3,
            "placeholder": "Type a message...",
            "class": "form-control",
        }),
        label="",
    )