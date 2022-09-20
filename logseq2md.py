#!/usr/bin/env python
"""A panflute filter to flatten LogSeq bulleted lists and remove block attributes.
"""

import panflute as pf
import sys


def prepare(doc):
    pass

def log(*a):
    print(*a, file=sys.stderr)

def get_list_depth(elt):
    depth = 0
    while elt is not None:
        if isinstance(elt, pf.BulletList):
            depth += 1
        elt = elt.parent
    return depth

def collapse_li(item):
    result = []
    # li's contain Plain's and BulletLists. Convert plains to paras, leave BulletLists and Headers alone.
    # BulletLists that are right after Headers should be collapsed too, though.
    prev_was_header = False
    for child in item.content:
        if isinstance(child, (pf.Para, pf.Header, pf.OrderedList, pf.RawBlock, pf.RawInline)):
            result.append(child)
        elif isinstance(child, pf.Plain):
            result.append(pf.Para(*child.content))
        elif isinstance(child, pf.BulletList):
            # NOTE: Change this to the commented version if you actually want bulleted lists.
            if True:#prev_was_header:
                result.extend([r for item in child.content for r in collapse_li(item)])
            else:
                result.append(child)
        else:
            log("Unknown ListItem child type:", type(child), str(child)[:50])
        prev_was_header = isinstance(child, pf.Header)
    return result


def flatten_bulletlists(elem, doc):
    stringified = pf.stringify(elem)

    # Remove the page tags.
    #if isinstance(elem.parent, pf.Doc) and elem.prev is None and '::' in stringified:
    #    return []
    depth = get_list_depth(elem)
    # Replace the top-level bulleted list with paragraphs.
    if isinstance(elem, pf.BulletList):
        if depth > 1:
            return
        log("Processing BulletList at depth", depth)
        new_children = []
        for child in elem.content:
            if isinstance(child, pf.ListItem):
                new_children.extend(collapse_li(child))
            else:
                new_children.append(child)
        return new_children

    # if isinstance(elem, pf.ListItem):
    #     print(' ' * get_list_depth(elem) + ' - ' + stringified[:10])

import re

tag_re = re.compile(r'\#([a-zA-Z-]+)')

assert tag_re.sub(r'\1', 'Every #writing-stage has') == "Every writing-stage has"

def split_by(seq, typ):
    '''Split seq into lists, each one ending with something that isinstance typ.
    
    >>> list(split_by([2, 4, 0.0, 4], float))
    [[2, 4, 0.0], [4]]
    '''
    cur = []
    for x in seq:
        cur.append(x)
        if isinstance(x, typ):
            yield cur
            cur = []
    yield cur


def remove_logseq_attrs(elem, doc):
    if not isinstance(elem, (pf.Para, pf.Plain)) or len(elem.content) < 1:
        return
    # Skip TODOs entirely
    first_str = pf.stringify(elem.content[0])
    if first_str in {"LATER", "NOW", "TODO", "DOING"}:
        return [pf.RawBlock('% ' + pf.stringify(elem).replace('\n', ' '), format='latex')]

    stringified = pf.stringify(elem)
    if "SKIP" in stringified:
        log("Removing SKIP", stringified[:20])
        return []

    any_change = False


    # Split out attributes. They're after SoftBreaks, so split the children by SoftBreak
    sections = list(split_by(elem.content, pf.SoftBreak))

    def should_skip_section(section):
        if len(section) == 0:
            return False
        first_text = getattr(section[0], 'text', '')
        return first_text.endswith("::") or first_text.startswith('%')
        

    new_sections = []
    for section in sections:
        if should_skip_section(section):
            log("Removing part", len(elem.content), len(stringified), stringified[:20])
            any_change = True
            new_sections.append([
                pf.RawInline('% ' + pf.stringify(pf.Plain(*section)).replace('\n', ' '), format='latex')])
        else:
            new_sections.append(section)

    if not any(new_sections):
        return []

    if not any_change:
        return elem

    return type(elem)(*[x for sec in new_sections for x in sec])

def untagify(elem, doc):
    if isinstance(elem, pf.Str) and tag_re.search(elem.text):
        def tag2str(match):
            return match.group(1).replace('-', ' ')
        return pf.Str(tag_re.sub(tag2str, elem.text))


def finalize(doc):
    pass


def main(doc=None):
    return pf.run_filters([remove_logseq_attrs, flatten_bulletlists, untagify],
                         prepare=prepare,
                         finalize=finalize,
                         doc=doc) 


if __name__ == '__main__':
    main()
