from __future__ import print_function

from claimchain import State
from hippiehug import Chain
from claimchain import LocalParams

import base64

def init_state(store, name):
    state = State()
    state.identity_info = "Hi, I'm " + name

    # Generate cryptographic keys
    params = LocalParams.generate()
    chain = Chain(store)
    with params.as_default():
        head = state.commit(chain)
    return head, params

def get_pk(store, head, params):
    from hippiehug import Chain
    from claimchain import View

    chain = Chain(store, root_hash=head)

    with params.as_default():
        view = View(chain)
        return view.params.dh.pk



class MyStore(dict):
    def __setitem__(self, key, value):
        print("store-set {}={}".format(base64.b64encode(key), value))
        super(MyStore, self).__setitem__(key, value)

    def __getitem__(self, key):
        val = super(MyStore, self).__getitem__(key)
        print("store-get {} -> {}".format(base64.b64encode(key), val))
        return val


if __name__ == "__main__":
    store = MyStore()
    alice_head, alice_params = init_state(store, "Alice")
    bob_head, bob_params = init_state(store, "Bob")
    print ("Alice reads her own PK:", get_pk(store, alice_head, alice_params))
    print ("Bob reads Alice's PK:", get_pk(store, alice_head, bob_params))
    print ("Alice reads Bob's PK:", get_pk(store, bob_head, alice_params))
    print ("Bob reads his own PK:", get_pk(store, bob_head, bob_params))
