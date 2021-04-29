from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
import qrcode as qrcode
import random
from django.utils import timezone
import hashlib
from main.models.core import *


@login_required
def index(request):
    return HttpResponseRedirect(reverse('tablet:home'))


@login_required
def home(request):
    xuser = request.user.extuser

    rooms = Room.objects.all()

    context = {
        "user": xuser,
        "rooms": rooms
    }
    return render(request, 'tablet/home.html', context)


@login_required
def qr(request, area_id=None, target_date=None):
    # Generating a verification key
    now = timezone.localtime(timezone.now())
    random.seed(now)
    salt = random.randint(0, 128)
    salted_email = "%s%s" % (salt, request.user)
    verif_key = hashlib.sha1(salted_email.encode('utf-8')).hexdigest()

    # Remove all unused key from db
    #VerifyKey.objects.filter(user=None).delete()

    # Save new key
    #vk = VerifyKey.objects.create(verifykey=verif_key)
    #vk.save()

    #url = "http://" + request.get_host() + "/tablet/vd/" + str(verif_key) + "/"
    url = "http://" + request.get_host() + "/tablet?" + str(verif_key)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=6,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    response = HttpResponse(content_type='image/png')
    img.save(response, "PNG")
    print('request')
    return response


@login_required
def room(request, room_id=None, target_date=None):
    xuser = request.user.extuser
    room = Room.objects.get(pk=room_id)
    rooms = Room.objects.all()

    context = {
        "user": xuser,
        "rooms": rooms,
        "room": room
    }
    return render(request, 'tablet/room.html', context)
