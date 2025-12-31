from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from marketplace.models import Transaction, Review
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


def landing(request):
    return render(request, 'landing.html')


@login_required
def dashboard(request):
    completed_count = Transaction.objects.filter(
        Q(buyer=request.user) | Q(seller=request.user),
        status=Transaction.STATUS_COMPLETED
    ).count()

    return render(request, 'dashboard.html', {
        'user': request.user,
        'completed_count': completed_count,
    })


@login_required
def profile(request):
    user = request.user

    if request.method == "POST":
        user.bio = request.POST.get("bio", user.bio)
        user.phone = request.POST.get("phone", user.phone)
        user.nickname = request.POST.get("nickname", user.nickname)

        if "profile_image" in request.FILES:
            user.profile_images = request.FILES["profile_image"]

        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("profile")

    return render(request, "profile.html", {"user": user})


@login_required
def user_profile(request, user_id):
    """
    Public, read-only profile for another user.
    Shows info + reviews they have received.
    """
    profile_user = get_object_or_404(CustomUser, pk=user_id)

    reviews_received = Review.objects.filter(
        reviewee=profile_user
    ).select_related("reviewer", "transaction", "transaction__item")

    avg_rating = reviews_received.aggregate(avg=Avg("rating"))["avg"]

    return render(request, "user_profile.html", {
        "profile_user": profile_user,
        "reviews_received": reviews_received,
        "avg_rating": avg_rating,
    })
