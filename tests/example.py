from __future__ import print_function

from hippiehug import Chain
from claimchain import State, LocalParams, View

import base64


def init_state(store, name):
    state = State()
    state.identity_info = "Hi, I'm " + name

    # Generate cryptographic keys
    params = LocalParams.generate()
    return commit_state_to_chain(store, params, state, head=None), params


def commit_state_to_chain(store, params, state, head):
    chain = Chain(store, root_hash=head)
    with params.as_default():
        # print ("------BEGIN commit")
        head = state.commit(chain)
        # print ("------FINISH commit", head)
    return head


def add_claim(state, params, claim, access_pk=None):
    key, value = claim
    state[key] = value
    if access_pk is not None:
        with params.as_default():
            state.grant_access(access_pk, [key])


def read_claim(store, params, head, claimkey):
    chain = Chain(store, root_hash=head)
    with params.as_default():
        view = View(chain)
        return view[claimkey]


def has_readable_claim(store, params, head, claimkey):
    try:
        read_claim(store, params, head, claimkey)
    except (KeyError, ValueError):
        return False
    return True


def get_pk(store, head, params):
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


def play_scenario1():
    store = MyStore()
    alice_head, alice_params = init_state(store, "Alice")
    bob_head, bob_params = init_state(store, "Bob")
    carol_head, carol_params = init_state(store, "Carol")
    print ("Alice reads her own PK:", get_pk(store, alice_head, alice_params))
    print ("Bob reads Alice's PK:", get_pk(store, alice_head, bob_params))
    print ("Alice reads Bob's PK:", get_pk(store, bob_head, alice_params))
    print ("Bob reads his own PK:", get_pk(store, bob_head, bob_params))
    alice_pk = get_pk(store, alice_head, alice_params)
    bob_pk = get_pk(store, bob_head, alice_params)
    carol_pk = get_pk(store, carol_head, alice_params)

    assert not has_readable_claim(store, alice_params, head=alice_head, claimkey="bob_hair")
    state = State()
    add_claim(state, alice_params, claim=("bob_hair", "black"), access_pk=bob_pk)
    alice_head = commit_state_to_chain(store, alice_params, state, head=alice_head)
    assert has_readable_claim(store, bob_params, head=alice_head, claimkey="bob_hair")

    add_claim(state, alice_params, claim=("bob_feet", "4"), access_pk=bob_pk)
    alice_head = commit_state_to_chain(store, alice_params, state, head=alice_head)
    assert has_readable_claim(store, bob_params, head=alice_head, claimkey="bob_feet")
    assert not has_readable_claim(store, carol_params, head=alice_head, claimkey="bob_feet")

    print ("Bob reads encrypted claim hair: {!r}".format(
           read_claim(store, bob_params, head=alice_head, claimkey="bob_hair")))
    print ("Bob reads encrypted claim feet: {!r}".format(
           read_claim(store, bob_params, head=alice_head, claimkey="bob_feet")))


if __name__ == "__main__":
    play_scenario1()

