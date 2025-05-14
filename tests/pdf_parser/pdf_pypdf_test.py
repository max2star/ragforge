from pypdf import PdfReader as pdf2_read
import logging
        
outlines = []
fnm = "./大模型训练原文/22298.pdf"
fnm = "./原文/D028386.pdf"
outlines_global = []
try:
    pdf = None
    with (pdf2_read(fnm if isinstance(fnm, str)
                    else BytesIO(fnm))) as pdf:
        pdf = pdf
        outlines = pdf.outline
        print("能够获取到的目录结构为 {}".format(pdf.outline))
        def dfs(arr, depth):
            for a in arr:
                if isinstance(a, dict):
                    outlines_global.append((a["/Title"], depth))
                    continue
                dfs(a, depth + 1)

        dfs(outlines, 0)
except Exception as e:
    logging.warning(f"Outlines exception: {e}")

if not outlines:
    logging.warning("Miss outlines")

print("目录结构 {}".format(outlines_global))
