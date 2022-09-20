.PHONY: all

#LOGSEQ_MD=/Users/ka37/Library/Mobile\ Documents/iCloud~com~logseq~logseq/Documents/main/pages/Proposal\ 2022.md
#LOGSEQ_SUMMARY_MD=/Users/ka37/Library/Mobile\ Documents/iCloud~com~logseq~logseq/Documents/main/pages/Proposal\ 2022\ Project\ Summary.md

all: proposal.pdf ProjectSummary.pdf

# %.tex: %.md
# 	pandoc --natbib --bibliography proposal.bib --wrap=preserve \
# 	  --filter pandoc-crossref \
# 	  -f markdown+raw_tex+tex_math_dollars+citations -t latex \
# 	  "$<" -o "$@"

# summary.md: $(LOGSEQ_SUMMARY_MD) logseq2md.py
# 	cp $(LOGSEQ_SUMMARY_MD) summary-logseq.md
# 	pandoc -f markdown+raw_tex+tex_math_dollars+citations -t markdown+raw_tex+tex_math_dollars+citations \
# 		--filter ./logseq2md.py summary-logseq.md -o summary.md

# body.md: $(LOGSEQ_MD) logseq2md.py
# 	cp $(LOGSEQ_MD) body-logseq.md
# 	pandoc -f markdown+raw_tex+tex_math_dollars+citations -t markdown+raw_tex+tex_math_dollars+citations \
# 		--filter ./logseq2md.py \
# 		--wrap=preserve \
# 		body-logseq.md -o body.md

# body.docx: body.md
# 	pandoc -f markdown+raw_tex+tex_math_dollars+citations \
# 		--filter pandoc-crossref \
# 		--citeproc --bibliography proposal.yaml \
# 		body.md -o body.docx

body-tex.docx: body.tex
	pandoc --citeproc --bibliography proposal.yaml body.tex -o body-tex.docx

proposal.pdf: proposal.tex summary.tex body.tex
	! : | pdflatex -halt-on-error proposal | grep '^!.*' -A200 --color=always
	bibtex proposal
	! : | pdflatex -halt-on-error proposal | grep '^!.*' -A200 --color=always
	! : | pdflatex -halt-on-error proposal | grep '^!.*' -A200 --color=always

ProjectSummary.pdf: proposal.pdf
	qpdf "$<" --pages . 1 -- ProjectSummary.pdf
	qpdf "$<" --pages . 2-11 -- ProjectDescription.pdf
	qpdf "$<" --pages . 12-r1 -- ReferencesCited.pdf

# %-debug.html: %-logseq.md
# 	pandoc "$<" -F ~/code/github.com/sergiocorreia/panflute-filters/filters/debug.py -o "$@" --toc
