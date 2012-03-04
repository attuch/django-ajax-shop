# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

from django.http import HttpResponseRedirect
from django.forms import ModelForm, Form
from models import *
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect, csrf_exempt
import os, decimal, urllib, sys, logging


@csrf_exempt
def purchased(request, cartid):
    tx = request.REQUEST['tx']
    amount = request.REQUEST['amt']
    #print(amount)
    if len(PurchaseCart.objects.filter(tx=tx)) == 0:
        #print("NON ANCORA PAGATO")
        try:
            result = Verify(tx)
            #print(result.success())
            if result.success(): # valid
                purchase = PurchaseCart.objects.get(cart=Cart.objects.get(id=cartid))
                purchase.tx = tx
                purchase.save()
                cart=Cart.objects.get(id=cartid)
                cart.payed=True
                cart.save()
                logging.error("INVIO DI VARIE MAIL E BASTA!!!!")
                to_template = 'Transazione %s avvenuta correttamente' % (tx)
            else:
                to_template = 'Riscontrati problemi nel corso della transazione %s' % (tx)
        except Exception, e:
            #print(e)
            to_template = 'Eccezione avvenuta nel corso della transazione %s, errore: %s' % (tx, e)
            pass
    else:
        to_template = "Transazione %s gia' avvenuta" % (tx)
        pass
    return render_to_response('purchased.html', locals(), RequestContext(request))

class Verify( object ):
    '''builds result, results, response'''
    def __init__( self, tx ):
        post = dict()
        post[ 'cmd' ] = '_notify-synch'
        post[ 'tx' ] = tx
        post[ 'at' ] = settings.PAYPAL_PDT_TOKEN
        self.response = urllib.urlopen( settings.PAYPAL_PDT_URL, urllib.urlencode(post)).read()
        lines = self.response.split( '\n' )
        self.result = lines[0].strip()
        self.results = dict()
        for line in lines[1:]: # skip first line
            linesplit = line.split( '=', 2 )
            if len( linesplit ) == 2:
                self.results[ linesplit[0].strip() ] = urllib.unquote(linesplit[1].strip())

    def success( self ):
        return self.result == 'SUCCESS' and self.results[ 'payment_status' ] == 'Completed'

