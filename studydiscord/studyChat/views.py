from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Room, Topic, Message, User
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .forms import RoomForm, UserForm, MyUserCreationForm

# Create your views here.

# room =[
#   {'id': 1, 'name': "Learn Python"},
#   {'id': 2, 'name': "Learn C++"},
#   {'id': 3, 'name': "Learn DSA"},
# ]

# fetched data from the database...



def loginPage(request):

  page = 'login'
  if request.user.is_authenticated:
    return redirect('home')

  if request.method == "POST":
    email = request.POST.get('email').lower()
    password = request.POST.get('password')

    try:
      print("User exist")
      user = User.objects.get(email = email)
    except:
      messages.error(request, 'User does not exist')
    
    user = authenticate(request, email= email, password= password)

    if user is not None:
      # created session in the database.
      login(request, user)
      return redirect('home')
    else:
      messages.error(request, 'Username or password does not exist.')

  context = {'page': page}
  return render(request, 'login_register.html', context)


def LogoutPage(request):
  logout(request)
  return redirect('home') 
  # return render(request, 'login_register.html')

# register page
def registerPage(request):
  # print("is it working?") debugging the function
  form = MyUserCreationForm()
  print(form, "--1>")
  if request.method == "POST":
    form = MyUserCreationForm(request.POST)
    # print(form, "-->") debugging the function
    if form.is_valid():
      user = form.save(commit = False)
      user.username = user.username.lower()
      user.save()
      login(request, user)
      return redirect('home')
    else:
      messages.error(request, 'An, might be passsword too short!')
  return render(request, 'login_register.html', {'form': form})



def home(request):
  q = request.GET.get('q') if request.GET.get('q') != None else ''
  room = Room.objects.filter(
    Q(topic__name__icontains = q) |
    Q(name__icontains = q) |
    Q(description__icontains=  q)
      )
  topics = Topic.objects.all()[0:5]
  rom_count = room.count()
  room_messages = Message.objects.all().filter(Q(room__topic__name__icontains= q))
  # print(rom_count)
  context = {'room': room, 'topics': topics, 'rom_count': rom_count, 'room_messages': room_messages}
  return render(request, "home.html", context)


def Room_Details(request, pk):
  rooms = Room.objects.get(id=pk)
  # all child of the room
  # print(rooms.host, "#->@ checking..")
  # print(request.user, "@checking...")
  room_messages = rooms.message_set.all()
  participants = rooms.participants.all()
  # print(room_messages, "found/orNot")
  if request.method == "POST":
    message = Message.objects.create(
      user = request.user,
      room = rooms,
      body = request.POST.get('body'),
    )
    rooms.participants.add(request.user)
    return redirect('room', pk= rooms.id)
  context = {'rooms': rooms, 'room_messages': room_messages, 'participants': participants}

  return render(request, "room.html", context)

def userProfile(request, pk):
  user = User.objects.get(id=pk)
  room = user.room_set.all()
  room_messages = user.message_set.all()
  topics= Topic.objects.all()
  context = {'user': user, 'room': room, 'room_messages': room_messages, 'topics': topics}
  return render(request, 'profile.html', context)




# create (CRUD operation)
@login_required(login_url='login')

def createRoom(request):
  form = RoomForm()
  topics = Topic.objects.all()
  if request.method == 'POST':
    topic_name = request.POST.get('topic')
    topic, created = Topic.objects.get_or_create(name=topic_name)

    Room.objects.create(
      host = request.user,
      topic = topic,
      name = request.POST.get('name'),
      description = request.POST.get('description'),
    )
    return redirect('home')

  context = {'form': form, 'topics': topics}
  return render(request, 'room_form.html', context)




def updateRoom(request, pk):
  room = Room.objects.get(id=pk)
  form =  RoomForm(instance= room)
  topics = Topic.objects.all()
  if request.user != room.host:
    return HttpResponse("You are not allowed here")

  if request.method == 'POST':
    topic_name = request.POST.get('topic')
    topic, created = Topic.objects.get_or_create(name=topic_name)
    room.name = request.POST.get('name')
    room.topic = topic
    room.description = request.POST.get('description')
    room.save()
    return redirect('home')
    
  context = {'form': form, 'topics': topics, 'room': room}
  return render(request, 'room_form.html', context)


@login_required(login_url= 'login')
def deleteRoom(request, pk):
  room = Room.objects.get(id= pk)

  if request.user != room.host:
    return HttpResponse("you are not allowed here...")
  if request.method == "POST":
    room.delete()
    return redirect('home')
  return render(request, 'delete.html', {'obj':room})



@login_required(login_url= 'login')
def deleteMessages(request, pk):
  message = Message.objects.get(id= pk)

  if request.user != message.user:
    return HttpResponse("you are not allowed here...")
  
  if request.method == "POST":
    message.delete()
    return redirect('home')
  return render(request, 'delete.html', {'obj':message})


@login_required(login_url='login')
def updateUser(request):
  user = request.user
  form = UserForm(instance = user )
  if request.method == "POST":
    form = UserForm(request.POST, request.FILES,  instance= user)
    if form.is_valid():
      form.save()
      return redirect('profile', pk= user.id)
  # form = UserForm(instance= request.user)
  return render(request, 'update-user.html', {'form': form})


def topicsPage(request):
  q = request.GET.get('q') if request.GET.get('q') != None else ''
  topics = Topic.objects.filter(name__icontains=q)
  return render(request, 'topics.html', {'topics': topics})


def activityPage(request):
  room_messages = Message.objects.all()
  return render(request, 'activity.html', {'room_messages': room_messages})