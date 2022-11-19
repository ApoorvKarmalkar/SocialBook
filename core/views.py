from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, LikePost, FollowersCount
from itertools import chain
import random

@login_required(login_url="core:signin")
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    user_following_list = []
    feed = []

    user_following = FollowersCount.objects.filter(follower=request.user.username)
    for users in user_following:
        user_following_list.append(users.user)

    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)

    feed_list = list(chain(*feed))

    all_users = User.objects.all()
    user_following_all = []
    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)
    new_suggestions_list = [x for x in list(all_users) if x not in list(user_following_all)]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [x for x in list(new_suggestions_list) if x not in list(current_user)]
    random.shuffle(final_suggestions_list)
    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)
    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))

    return render(request, "index.html", {"user_profile": user_profile, "posts": feed_list, "suggestions_username_profile_list": suggestions_username_profile_list[:4]})

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("password2")

        if password == confirm_password:
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email taken")
                return redirect("core:signup")
            elif User.objects.filter(username=username).exists():
                messages.error(request, "Username taken")
                return redirect("core:signup")
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                # login and redirect user after sign up
                user_login = authenticate(username=username, password=password)
                login(request, user_login)
                # create a profile object for the signed up user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect("core:settings")
        else:
            messages.error(request, "Password and confirm password do not match")
            return redirect("core:signup")

    return render(request, "signup.html")

def signin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            messages.error(request, "Invalid credentials")
            return redirect("core:signin")

    return render(request, "signin.html")

@login_required(login_url="core:signin")
def log_out(request):
    logout(request)
    return redirect("core:signin")

@login_required(login_url="core:signin")
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        if request.FILES.get("image") is None:
            user_profile.profileimg = user_profile.profileimg
        else:
            user_profile.profileimg = request.FILES.get("image")
        user_profile.bio = request.POST.get("bio")
        user_profile.location = request.POST.get("location")
        user_profile.save()
        return redirect("core:settings")
    return render(request, "setting.html", {"user_profile": user_profile})

@login_required(login_url="core:signin")
def upload(request):
    if request.method == "POST":
        user = request.user.username
        image = request.FILES.get("image_upload")
        caption = request.POST.get("caption")
        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()
    return redirect("core:index")

@login_required(login_url="core:signin")
def like_post(request):
    post_id = request.GET.get("post_id")
    username = request.user.username
    post = Post.objects.get(id=post_id)
    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter is None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes + 1
        post.save()
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes - 1
        post.save()
    return HttpResponse(post.no_of_likes)

@login_required(login_url="core:signin")
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_posts_length = len(user_posts)
    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = "Unfollow"
    else:
        button_text = "Follow"
    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))
    context = {
        "user_object": user_object,
        "user_profile": user_profile,
        "user_posts": user_posts,
        "user_posts_length": user_posts_length,
        "button_text": button_text,
        "user_followers": user_followers,
        "user_following": user_following
    }
    return render(request, "profile.html", context)

@login_required(login_url="core:signin")
def follow(request):
    if request.method == "POST":
        follower = request.POST.get("follower")
        user = request.POST.get("user")
        result = ""

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            result += "Follow"
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            result += "Unfollow"
        user_followers = len(FollowersCount.objects.filter(user=user))
        return JsonResponse({"buttonText": result, "userFollowers": user_followers})
        # return redirect("core:profile", pk=user)
    else:
        return redirect("core:index")

@login_required(login_url="core:signin")
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == "POST":
        username = request.POST.get("username")
        username_object = User.objects.filter(username__icontains=username)
        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)
        username_profile_list = list(chain(*username_profile_list))
    return render(request, "search.html", {"user_profile": user_profile, "username_profile_list": username_profile_list})

