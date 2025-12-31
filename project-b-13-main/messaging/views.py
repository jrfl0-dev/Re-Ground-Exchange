from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.contrib.auth import get_user_model
from django.urls import reverse

from .models import Conversation, Message
from .forms import NewConversationForm, MessageForm

User = get_user_model()

@login_required
def inbox(request):
    convos = request.user.conversations.all().order_by('-created_at')
    return render(request, 'messaging/inbox.html', {'convos': convos})

@login_required
def new_conversation(request):
    if request.method == 'POST':
        form = NewConversationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()

            try:
                other = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                django_messages.error(request, "No account with that email.")
                return redirect('messaging:new')
            
            # make sure they’re not trying to message themselves or if they don't already have a convo
            convo = Conversation.objects.filter(participants=request.user).filter(participants=other).first()
            if not convo:
                convo = Conversation.objects.create()
                convo.participants.add(request.user, other)
            return redirect('messaging:detail', convo_id=convo.id)
    else:
        # if it’s a GET request, just render an empty form for them to fill out
        form = NewConversationForm()
    return render(request, 'messaging/new.html', {'form': form})

@login_required
def conversation_detail(request, convo_id):
    # make sure the logged-in user is actually part of this conversation
    convo = get_object_or_404(Conversation, id=convo_id, participants=request.user)
    if request.method == 'POST':
        # user is submitting a new message to the thread
        form = MessageForm(request.POST)
        if form.is_valid():
            # create the actual message record tied to this convo and sender
            Message.objects.create(
                conversation=convo,
                sender=request.user,
                body=form.cleaned_data['body']
            )
            # refresh the page so the new message appears immediately
            return redirect(reverse('messaging:detail', args=[convo.id]))
    else:
        form = MessageForm()
    # mark unread messages from others as read
    convo.messages.filter(read=False).exclude(sender=request.user).update(read=True)
    messages_qs = convo.messages.select_related('sender')

    # render the chat view with convo info, message list, and the form to reply
    return render(request, 'messaging/detail.html', {'convo': convo, 'messages': messages_qs, 'form': form})

