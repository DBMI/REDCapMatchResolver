SCORE=$(sh .\\.github\\pre-commit\\pylint_compute_score.sh)"/10.00"
anybadge -l pylint -v "$SCORE" --overwrite --file .\\.github\\badges\\pylint-badge.svg 2=red 4=orange 8=yellow 10=green
