from attr import attrs, attrib, Factory
from defaultcontext import with_default_context
from petlib.cipher import Cipher
from petlib.ec import EcGroup


@with_default_context(use_empty_init=True)
@attrs
class PublicParams(object):
    ec_group = attrib(default=Factory(EcGroup))
    enc_cipher = attrib(default=Factory(lambda: Cipher("aes-128-gcm")))


@attrs
class Keypair(object):
    sk = attrib()
    pk = attrib()

    @staticmethod
    def generate(pp=None):
        pp = pp or PublicParams.get_default()

        G = pp.ec_group
        s = G.order().random()
        return Keypair(sk=s, pk=s * G.generator())


@with_default_context
@attrs
class LocalParams(object):
    vrf = attrib(default=None)
    sig = attrib(default=None)
    dh = attrib(default=None)

    @staticmethod
    def generate(pp=None):
        return LocalParams(
            vrf = Keypair.generate(pp),
            sig = Keypair.generate(pp),
            dh = Keypair.generate(pp)
        )