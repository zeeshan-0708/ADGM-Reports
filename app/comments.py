"""
comments.py

Adds Word comments inline into .docx files using low-level XML manipulation.

It:
- ensures a comments.xml part exists (or creates one)
- adds a <w:comment> entry with text/author
- inserts commentRangeStart/commentRangeEnd and commentReference run elements around a text run

NOTE: python-docx does not provide comment creation APIs; we edit the XML directly.
"""

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.opc.package import Part
from docx.oxml.shared import qn as _qn
import uuid

def _get_or_create_comments_part(doc):
    # get the package
    package = doc.part.package
    # find if comments part exists
    for rel in doc.part.rels:
        part = doc.part.rels[rel].target_part
        if part.content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml':
            return part

    # not found — create new comments part
    comments_xml = '<?xml version="1.0" encoding="UTF-8"?><w:comments xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"></w:comments>'
    new_part = package.part_factory.create_part(
        'application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml',
        comments_xml.encode('utf-8'),
        '/word/comments.xml'
    )
    # create rel from document part to the new comments part
    doc.part.relate_to(new_part, RT.COMMENTS)
    return new_part

def _get_next_comment_id(comments_part):
    root = comments_part._element
    max_id = -1
    for c in root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}comment'):
        cid = int(c.get(qn('w:id')))
        if cid > max_id:
            max_id = cid
    return max_id + 1

def _add_comment_to_comments_part(comments_part, comment_id, author, initials, text):
    root = comments_part._element
    # build <w:comment w:id="X" w:author="..." w:initials="...">
    comment = OxmlElement('w:comment')
    comment.set(qn('w:id'), str(comment_id))
    comment.set(qn('w:author'), author)
    comment.set(qn('w:initials'), initials)

    p = OxmlElement('w:p')
    r = OxmlElement('w:r')
    t = OxmlElement('w:t')
    t.text = text
    r.append(t)
    p.append(r)
    comment.append(p)
    root.append(comment)
    return comment

def add_comment_to_paragraph(doc: Document, paragraph, comment_text: str, author="Reviewer", initials="RV"):
    """
    Insert a Word comment anchored to the given paragraph's first run.
    """
    comments_part = _get_or_create_comments_part(doc)
    comment_id = _get_next_comment_id(comments_part)

    # Add comment XML entry
    _add_comment_to_comments_part(comments_part, comment_id, author, initials, comment_text)

    # Now add commentRangeStart before the run, commentRangeEnd after, and commentReference in the end run
    p = paragraph._p  # <w:p>
    # find first run
    runs = p.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r')
    if not runs:
        # If no runs, just append a run and attach comment to it
        run = OxmlElement('w:r')
        t = OxmlElement('w:t')
        t.text = paragraph.text if paragraph.text else ''
        run.append(t)
        p.append(run)
        runs = [run]

    first_run = runs[0]

    # commentRangeStart
    comment_start = OxmlElement('w:commentRangeStart')
    comment_start.set(qn('w:id'), str(comment_id))
    p.insert(p.index(first_run), comment_start)

    # commentRangeEnd -> append after the last run
    last_run = runs[-1]
    comment_end = OxmlElement('w:commentRangeEnd')
    comment_end.set(qn('w:id'), str(comment_id))
    p.insert(p.index(last_run)+1, comment_end)

    # commentReference -> insert as separate run at end
    cm_run = OxmlElement('w:r')
    cr = OxmlElement('w:commentReference')
    cr.set(qn('w:id'), str(comment_id))
    cm_run.append(cr)
    p.append(cm_run)

    return comment_id
