from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.core.paginator import Paginator

from .forms import (ItemForm, ItemImageForm,ReviewForm,SearchFilterForm,UserInterestForm)
from .models import (Category, Item, ItemImage, Review, UserInterest,Transaction,)
from messaging.models import Conversation

def item_list(request):
    items = Item.objects.filter(status=Item.STATUS_AVAILABLE)
    categories = Category.objects.all()
    search_form = SearchFilterForm(request.GET or None)

    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        category = search_form.cleaned_data.get('category')
        min_price = search_form.cleaned_data.get('min_price')
        max_price = search_form.cleaned_data.get('max_price')

        if query:
            items = items.filter(Q(title__icontains=query) | Q(description__icontains=query))

        if category:
            items = items.filter(category=category)

        if min_price is not None:
            items = items.filter(price__gte=min_price)

        if max_price is not None:
            items = items.filter(price__lte=max_price)

    total_items = items.count()

    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'items': items,
        'categories': categories,
        'search_form': search_form,
        'page_obj': page_obj,
        'total_items': total_items,
    }
    return render(request, 'marketplace/item_list.html', context)

def item_detail(request, pk):
    item = get_object_or_404(
        Item.objects.select_related("category", "seller").prefetch_related("images"),
        pk=pk,
    )
    latest_transaction=(item.transactions.select_related('buyer','seller').order_by('-created_at').first())
    context = {
        'item': item,
        'latest_transaction':latest_transaction,
        'is_owner': request.user.is_authenticated and request.user == item.seller,
    }
    return render(request, 'marketplace/item_detail.html', context)
@login_required
def create_item(request):
    if request.method == 'POST':
        item_form = ItemForm(request.POST)
        image_form = ItemImageForm(request.POST, request.FILES)
        if item_form.is_valid() and image_form.is_valid():
            item = item_form.save(commit=False)
            item.seller = request.user
            item.status = Item.STATUS_AVAILABLE
            item.save()

            images= image_form.cleaned_data.get('images')
            if images:
                for img in images:
                    ItemImage.objects.create(item=item, image=img)            
            messages.success(request, 'Item created successfully.')
            return redirect(reverse('marketplace:item_detail', args=[item.id]))
    else:
        item_form = ItemForm()
        image_form = ItemImageForm()
    
    context = {
        'item_form': item_form,
        'image_form': image_form,
    }
    return render(request, 'marketplace/create_item.html', context)

@login_required
def edit_item(request,pk):
    item=get_object_or_404(Item,pk=pk,seller=request.user)
    if request.method=='POST':
        form=ItemForm(request.POST,instance=item)
        image_form=ItemImageForm(request.POST,request.FILES)
        if form.is_valid() and image_form.is_valid():
            item=form.save()
            
            # Handle image deletion
            delete_ids = request.POST.getlist('delete_images')
            if delete_ids:
                # Filter by item=item to ensure user owns the images they are deleting
                ItemImage.objects.filter(id__in=delete_ids, item=item).delete()

            images=image_form.cleaned_data.get('images')
            if images:
                for img in images:
                    ItemImage.objects.create(item=item,image=img)
            messages.success(request,'Item updated successfully.')
            return redirect("marketplace:item_detail",pk=item.pk)
    else:
        form=ItemForm(instance=item)
        image_form=ItemImageForm()
    return render(request,'marketplace/edit_item.html',{'form':form,'image_form':image_form,'item':item})

@login_required
def delete_item(request,pk):
    item=get_object_or_404(Item,pk=pk,seller=request.user)
    if request.method=='POST':
        item.delete()
        messages.success(request,'Item deleted successfully.')
        return redirect('marketplace:item_list')
    return render(request,'marketplace/delete_item.html',{'item':item})

@login_required
def my_items(request):
    items=Item.objects.filter(seller=request.user).select_related('category')
    return render(request,'marketplace/my_items.html',{'items':items})

@login_required
def initiate_transaction(request, item_id):
    item = get_object_or_404(Item, pk=item_id)

    if item.seller == request.user:
        messages.error(request, "You cannot buy your own item.")
        return redirect('marketplace:item_detail', pk=item.pk)

    if item.status != Item.STATUS_AVAILABLE:
        messages.error(request, "This item is not available for sale.")
        return redirect('marketplace:item_detail', pk=item.pk)

    # (Optional) prevent duplicate pending holds by the same buyer
    existing = Transaction.objects.filter(
        item=item,
        buyer=request.user,
        status=Transaction.STATUS_PENDING,
    ).first()
    if existing:
        messages.info(request, "You already have a pending reservation for this item.")
        return redirect('marketplace:item_detail', pk=item.pk)

    transaction = Transaction.objects.create(
        item=item,
        buyer=request.user,
        seller=item.seller,
        price=item.price,
        status=Transaction.STATUS_PENDING,
    )
    item.status = Item.STATUS_RESERVED
    item.save(update_fields=['status'])

    messages.success(request, "Reserved! We’ve held this item for you.")
    
    # Create or get conversation with seller
    convo = Conversation.objects.filter(participants=request.user).filter(participants=item.seller).first()
    if not convo:
        convo = Conversation.objects.create()
        convo.participants.add(request.user, item.seller)
        
    return redirect('messaging:detail', convo_id=convo.id)

@login_required
def complete_transaction(request,transaction_id):
    transaction=get_object_or_404(Transaction.objects.select_related('item'),pk=transaction_id)
        
    if request.user not in [transaction.buyer,transaction.seller]:
        messages.error(request,"You are not authorized to complete this transaction.")
        return redirect('marketplace:my_transactions')
    if request.method=='POST':
        transaction.status=Transaction.STATUS_COMPLETED
        transaction.item.status=Item.STATUS_SOLD
        transaction.item.save(update_fields=['status'])
        transaction.save(update_fields=['status'])
        messages.success(request,"Transaction completed successfully.")
        return redirect('marketplace:my_transactions')
    return render(request,'marketplace/complete_transaction.html',{'transaction':transaction})

@login_required
def cancel_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction.objects.select_related('item'), pk=transaction_id)

    if request.user != transaction.buyer:
        messages.error(request, "You are not authorized to cancel this transaction.")
        return redirect('marketplace:item_detail', pk=transaction.item.pk)

    if transaction.status != Transaction.STATUS_PENDING:
        messages.error(request, "Cannot cancel a transaction that is not pending.")
        return redirect('marketplace:item_detail', pk=transaction.item.pk)

    if request.method == 'POST':
        transaction.status = Transaction.STATUS_CANCELLED
        transaction.item.status = Item.STATUS_AVAILABLE
        transaction.item.save(update_fields=['status'])
        transaction.save(update_fields=['status'])
        messages.success(request, "Reservation cancelled. The item is now available again.")
        return redirect('marketplace:item_detail', pk=transaction.item.pk)
    
    # If GET, just redirect back to item detail (or show a confirmation page if desired, but button is enough)
    return redirect('marketplace:item_detail', pk=transaction.item.pk)

@login_required
def my_transactions(request):
    transactions=Transaction.objects.filter(
        Q(buyer=request.user) | Q(seller=request.user)
    ).select_related('item','buyer','seller')
    return render(request,'marketplace/my_transactions.html',{'transactions':transactions})

@login_required
def leave_review(request,transaction_id):
    transaction=get_object_or_404(Transaction.objects.select_related("buyer","seller"),pk=transaction_id)
    if transaction.status!=Transaction.STATUS_COMPLETED:
        messages.error(request,"You can only review completed transactions.")
        return redirect('marketplace:my_transactions')
    
    if request.user not in [transaction.buyer,transaction.seller]:
        messages.error(request,"You are not authorized to review this transaction.")
        return redirect('marketplace:my_transactions')
    
    if request.user==transaction.buyer:
        reviewee=transaction.seller
    else:
        reviewee=transaction.buyer
    if hasattr(transaction,'review'):
        messages.error(request,"You have already reviewed this transaction.")
        return redirect('marketplace:my_transactions')
    if request.method=='POST':
        form=ReviewForm(request.POST)
        if form.is_valid():
            review=form.save(commit=False)
            review.transaction=transaction
            review.reviewer=request.user
            review.reviewee=reviewee
            review.save()
            messages.success(request,"Review submitted successfully.")
            return redirect('marketplace:my_transactions')
    else:
        form=ReviewForm()
    return render(request,'marketplace/leave_review.html',{'form':form,'transaction':transaction,'reviewee':reviewee})

@login_required
def set_interests(request):
    existing_interests=UserInterest.objects.filter(user=request.user).select_related('category')
    initial_categories=[ui.category.pk for ui in existing_interests]

    if request.method=='POST':
        form=UserInterestForm(request.POST)
        if form.is_valid():
            categories=form.cleaned_data.get('categories')
            UserInterest.objects.filter(user=request.user).delete()
            if categories:
                for category in categories:
                    UserInterest.objects.create(user=request.user,category=category)
            messages.success(request,"Your interests have been updated.")
            return redirect('marketplace:item_list')
    else:
        form=UserInterestForm(initial={'categories':initial_categories})
    return render(request,'marketplace/set_interests.html',{'form':form})

@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'marketplace/category_list.html', {
        'categories': categories
    })




        

            

        