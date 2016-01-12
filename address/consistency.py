import string


PUNC_TABLE = dict([(c, None) for c in string.punctuation])
KNOWN_TABLE = {
    'usa': 'us'
}


def get_consistency_from_parts(raw, components):
    ref_chunks = set()
    for com in components:
        ref_chunks |= set([x.lower() for x in com.long_name.split() + com.short_name.split() if x])
    all_chunks = [x.lower().translate(PUNC_TABLE) for x in raw.split()]
    all_chunks = set([KNOWN_TABLE.get(x, x) for x in all_chunks])
    return not bool(all_chunks - ref_chunks)


def get_consistency(inst):
    return get_consistency_from_parts(inst.raw, inst.get_components())
