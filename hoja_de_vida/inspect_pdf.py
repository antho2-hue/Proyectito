from pypdf import PdfReader
p='test_cv_css.pdf'
reader=PdfReader(p)
print('pages', len(reader.pages))
for i,pg in enumerate(reader.pages, start=1):
    w=float(pg.mediabox.width); h=float(pg.mediabox.height)
    try:
        text=pg.extract_text() or ''
    except Exception as e:
        text='(extract error)'
    print(i, round(w,2), round(h,2), repr(text[:120]))
