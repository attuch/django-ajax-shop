from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.sessions.models import Session
from django.db.models.signals import post_init, post_save
from datetime import datetime
import logging, re, urllib, os, shutil
from django.conf import settings
from settings import *
from PIL import Image

TAG_RE = re.compile('[^a-z0-9\-_\+\:\.]?', re.I)
TINY_SIZE = (80,80)    #thumb size (x,y)

class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.CharField(max_length=64, unique=True, null=True, blank=True)

    def __unicode__(self):
        return self.name

    @staticmethod
    def clean_tag(name):
        """Replace spaces with dashes, in case someone adds such a tag manually"""

        name = name.replace(' ', '-').encode('ascii', 'ignore')
        name = TAG_RE.sub('', name)
        clean = name.lower().strip()

        return clean

    def save(self, *args, **kwargs):
        """Cleans up any characters I don't want in a URL"""

        self.slug = Tag.clean_tag(self.name)
        super(Tag, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('tag', (self.cleaned,))

    @property
    def cleaned(self):
        """Returns the clean version of the tag"""

        return self.slug or Tag.clean_tag(self.name)

    class Meta:
        ordering = ["name"]
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __unicode__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField(max_length=600)
    tags = models.ManyToManyField(Tag, help_text=_('Tags that describe this product'), blank=True)
    image = models.ImageField(upload_to='e_commerce/')
    price = models.FloatField(max_length=300)
    number = models.IntegerField(max_length=50)
    date_disponibility = models.DateField()
    primo_piano = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        d = PROJECT_PATH + "/media/e_commerce/tiny"
        if not os.path.exists(d):
            logging.error("creo directory")
            os.makedirs(d)
        try:
            this = Product.objects.get(id=self.id)
            if this.image != self.image:
                this.image.delete()
                #logging.error("elimino directory")
                shutil.rmtree(d)
                #logging.error("creo directory")
                os.makedirs(d)
        except: pass
        super(Product, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.image.delete()
        super(Product, self).delete(*args, **kwargs)

    def thumb(self):
        d = PROJECT_PATH + "/media/e_commerce/tiny"
        if not os.path.exists(d):
            #logging.error("creo directory")
            os.makedirs(d)
        tinythumb = self.image.url.replace('\\','/').split('/')
	tinythumb[-1] = 'tiny/'+tinythumb[-1]
	tinythumb = '/'.join(tinythumb)
        tinythumbpath = PROJECT_PATH + tinythumb
        urlpath = PROJECT_PATH + self.image.url
	if not os.path.exists(tinythumbpath):
	    im = Image.open(urlpath)
	    im.thumbnail(TINY_SIZE,Image.ANTIALIAS)
	    im.save(tinythumbpath,"PNG")
	return """<a href="%s"><img src="%s" alt="thumbnail image" /></a>"""%(self.image.url,tinythumb)
    thumb.allow_tags = True

    class Meta:
        ordering = ["name"]
        verbose_name = 'Prodotto'
        verbose_name_plural = 'Prodotti'

    def __unicode__(self):
        return self.name

class CartObj(models.Model):
    product = models.ForeignKey(Product)
    session = models.ForeignKey(Session)
    num = models.IntegerField(max_length=30)
    data = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["data"]
        verbose_name = 'Prodotto Carrello'
        verbose_name_plural = 'Prodotti Carrelli'

    def __unicode__(self):
        return str(self.num) + " " + self.product.name + " " + self.session.session_key

class Cart(models.Model):
    session = models.ForeignKey(Session)
    product = models.ManyToManyField(CartObj, blank=True)
    payed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ["session"]
        verbose_name = 'Carrello'
        verbose_name_plural = 'Carrelli'

    def __unicode__(self):
        return self.session.session_key

    def save(self, *args, **kwargs):
        if self.payed:
            final = FinalCartPayed()
            purchase = PurchaseCart.objects.get(cart=self)
            out = ""
            for x in self.product.all():
                out += x.product.name + " X" + str(x.num) + "\n"
            final.descrizione = purchase.full_name + " " + purchase.address + " " + purchase.cap + " " + purchase.email + " " + purchase.phone + "\n" + purchase.tx + "\n" + out
            final.save()
        super(Cart, self).save(*args, **kwargs)

def post_save_final(sender, **kwargs):
    if kwargs['instance'].payed:
	logging.error("si pagato.. TODO Eliminare Carrello ormai da non usare piu, magari tramite la funzione di paypa, dopo aver salvato ;)")
    else:
	logging.error("non ancora pagato")
	

post_save.connect(post_save_final, sender=Cart)

class PurchaseCart(models.Model):
    cart = models.ForeignKey(Cart)
    tx = models.CharField(max_length=125, blank=True, null=True)
    full_name = models.CharField(max_length=125, blank=True, null=True)
    city = models.CharField(max_length=125, blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    cap = models.CharField(max_length=60, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=250, blank=True, null=True)

    def __unicode__(self):
        return str(self.id) + " " + "---" + " " + self.full_name + " " + "---" + " " + self.cart.session.session_key

class Discount(models.Model):
    discount = models.FloatField(max_length=100, help_text=_('This percentage to be applied to products or to tag'))
    product = models.ForeignKey(Product, blank=True, null=True)

    class Meta:
        ordering = ["discount"]
        verbose_name = 'Sconto'
        verbose_name_plural = 'Sconti'

    def __unicode__(self):
        return str(self.discount)

class FinalCartPayed(models.Model):
    descrizione = models.TextField(max_length="1000") # il resoconto di un acquisto terminato da parte di un utente, da fare una save() nel Cart al momento in cui payed = True
    data = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["data"]
        verbose_name = 'Descrizione Acquisto'
        verbose_name_plural = 'Descrizione Acquisti'

    def __unicode__(self):
        return str(self.descrizione)

